# PHOENIX 15 — FINAL ENGINE V1
# 2026-09-07
# READ ONLY: Master / Frozen / Model
# Pipeline: Phoenix -> 60/40 -> TOP7 -> Spik -> Million Dollar Secret -> Cupong -> archive

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

VERSION = "1.0"
MAX_SPIKES = 3
TOP_N = 7


def _load_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_coupon(top7, spikes, budget, max_rows=50000):
    """Transparent V1 coupon allocator. Never changes Phoenix ranking.
    Uses spike candidates first, then distributes coverage by TOP7 strength.
    """
    races = list(top7["race_id"].drop_duplicates())
    spike_map = {}
    if not spikes.empty:
        for _, r in spikes.iterrows():
            if r.get("spikzon") in {"S4", "S2"}:
                spike_map[r["race_id"]] = r

    selected = []
    for race in races:
        g = top7[top7["race_id"] == race].sort_values("rank_6040")
        if race in spike_map:
            selected.append({"race_id": race, "selection": "SPIK", "numbers": [int(g.iloc[0]["number"])] if "number" in g.columns else [g.iloc[0]["horse_id"]]})
            continue
        # Coverage V1: TOP3 for strong races, TOP5 otherwise, TOP7 for flagged skräll-races.
        if "skrall_grade" in g.columns and (g["skrall_grade"] == "S4").any():
            n = 7
        else:
            spread = float(g["score_6040"].iloc[0] - g["score_6040"].iloc[min(1, len(g)-1)])
            n = 3 if spread >= 0.20 else 5
        n = min(n, len(g))
        nums = g.head(n)["number"].tolist() if "number" in g.columns else g.head(n)["horse_id"].tolist()
        selected.append({"race_id": race, "selection": f"TOP{n}", "numbers": nums})

    # If the raw product is too large, keep the plan rather than silently changing logic.
    combinations = 1
    for s in selected:
        combinations *= len(s["numbers"])
    return {"races": selected, "combinations": int(combinations), "max_rows": int(max_rows), "status": "V1_TRANSPARENT"}


def archive(result, out_dir, metadata=None):
    out = Path(out_dir)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = out / stamp
    run_dir.mkdir(parents=True, exist_ok=False)

    result["ranked"].to_csv(run_dir / "ranked_phoenix_6040.csv", index=False)
    result["top7"].to_csv(run_dir / "top7.csv", index=False)
    result["spikes"].to_csv(run_dir / "spikes.csv", index=False)
    result["skrall"].to_csv(run_dir / "million_dollar_secret.csv", index=False)
    pd.DataFrame(result["coupon"]["races"]).to_json(run_dir / "coupon_plan.json", orient="records", force_ascii=False, indent=2)

    manifest = {
        "engine": "PHOENIX15_FINAL_ENGINE_V1",
        "version": VERSION,
        "created": datetime.now().isoformat(),
        "read_only_components": ["Master", "Frozen", "Model"],
        "pipeline": ["Phoenix", "60/40", "TOP7", "Spikmotor", "Million Dollar Secret", "Kupongmotor", "Archive"],
        "budget": result["budget"],
        "coupon": {k: v for k, v in result["coupon"].items() if k != "races"},
        "metadata": metadata or {},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return run_dir


def run(core_df, engine_module, skrall_module, out_dir=None, metadata=None):
    """Run the final decision layer on an already prepared live dataframe."""
    base = engine_module.run(core_df)
    top7 = base["top7"].copy()

    # Million Dollar Secret is intentionally separate. It requires HD already supplied by the feature chain.
    if "hd_win_percent" in top7.columns:
        mds = skrall_module.million_dollar_secret(top7)
        top7["million_dollar_secret"] = False
        if not mds.empty:
            keys = [c for c in ["race_id", "horse_id"] if c in top7.columns and c in mds.columns]
            if keys:
                marked = set(map(tuple, mds[keys].itertuples(index=False, name=None)))
                top7["million_dollar_secret"] = [tuple(r) in marked for r in top7[keys].itertuples(index=False, name=None)]
    else:
        top7["million_dollar_secret"] = False

    base["top7"] = top7
    base["coupon"] = build_coupon(top7, base["spikes"], base["budget"])

    if out_dir:
        base["archive_dir"] = str(archive(base, out_dir, metadata))
    return base

"""Phoenix 15 — Phase 2 historical OOS backtest harness.

READ ONLY analysis layer. It never writes SQLite/model/features and never
uses post-race fields to build the input ranking.

Expected snapshot contract (CSV/JSON/Parquet):
- race_id
- race_datetime (or timestamp)
- start_number
- phoenix_rank
- phoenix_score / phoenix_probability (at least one)
- in_system (0/1)
- winner (0/1) OR result_position (1 for winner)
Optional:
- odds_rank / odds
- spike_signal
- round_id / meeting_id

The harness deliberately refuses to invent missing history. Missing required
columns/files are reported and the run exits without a fabricated result.

Usage from Colab:
    python phoenix15/PHOENIX15_PHASE2_BACKTEST.py --input <snapshot_dir> --output <output_dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from PHOENIX15_PROTECTION_LAYER_v1 import PhoenixProtectionLayerV1


REQUIRED = {"race_id", "start_number", "phoenix_rank", "in_system"}
WINNER_COLUMNS = ("winner", "result_position")
OPTIONAL = {"race_datetime", "timestamp", "phoenix_score", "phoenix_probability",
            "odds_rank", "odds", "spike_signal", "round_id", "meeting_id"}


def _read(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        if isinstance(obj, dict):
            for key in ("data", "rows", "records"):
                if isinstance(obj.get(key), list):
                    return pd.DataFrame(obj[key])
        raise ValueError(f"Unsupported JSON structure: {path}")
    raise ValueError(f"Unsupported snapshot file: {path}")


def load_snapshots(input_dir: Path) -> pd.DataFrame:
    files = sorted(p for p in input_dir.rglob("*")
                   if p.is_file() and p.suffix.lower() in {".csv", ".json", ".parquet", ".pq"})
    if not files:
        raise FileNotFoundError(f"No CSV/JSON/Parquet snapshots found under {input_dir}")
    frames = []
    for p in files:
        df = _read(p)
        df["__source_file"] = str(p.relative_to(input_dir))
        frames.append(df)
    return pd.concat(frames, ignore_index=True, sort=False)


def validate(df: pd.DataFrame) -> list[str]:
    errors = []
    missing = sorted(REQUIRED - set(df.columns))
    if missing:
        errors.append("Missing required columns: " + ", ".join(missing))
    if not any(c in df.columns for c in WINNER_COLUMNS):
        errors.append("Missing winner/result_position column")
    if "race_id" in df and "start_number" in df:
        dup = df.duplicated(["race_id", "start_number"]).sum()
        if dup:
            errors.append(f"Duplicate race_id/start_number rows: {dup}")
    if "phoenix_rank" in df:
        bad = (~pd.to_numeric(df["phoenix_rank"], errors="coerce").between(1, 7)).sum()
        if bad:
            errors.append(f"Phoenix rank outside 1..7: {bad}")
    if "in_system" in df:
        bad = (~pd.to_numeric(df["in_system"], errors="coerce").isin([0, 1])).sum()
        if bad:
            errors.append(f"in_system not binary: {bad}")
    if "race_datetime" in df:
        parsed = pd.to_datetime(df["race_datetime"], errors="coerce")
        if parsed.isna().any():
            errors.append("Invalid race_datetime values present")
    return errors


def winner_mask(df: pd.DataFrame) -> pd.Series:
    if "winner" in df.columns:
        return pd.to_numeric(df["winner"], errors="coerce").eq(1)
    return pd.to_numeric(df["result_position"], errors="coerce").eq(1)


def backtest(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    protection = PhoenixProtectionLayerV1(verbose=False)
    rows = []
    for race_id, race in df.groupby("race_id", sort=False):
        top7 = race[pd.to_numeric(race["phoenix_rank"], errors="coerce").between(1, 7)].copy()
        system = race[["start_number", "in_system"]].copy()
        market = None
        if {"start_number", "odds_rank"} <= set(race.columns):
            market = race[["start_number", "odds_rank"]].copy()
        spikes = None
        if {"start_number", "spike_signal"} <= set(race.columns):
            spikes = dict(zip(race["start_number"], race["spike_signal"].fillna("")))

        protected, decisions = protection.protect_system(
            top7, system, market_data=market, spike_signal=spikes
        )
        winners = race.loc[winner_mask(race), "start_number"].tolist()
        if len(winners) != 1:
            rows.append({
                "race_id": race_id, "status": "INVALID_WINNER_COUNT",
                "winner_count": len(winners), "source_file": race["__source_file"].iloc[0],
            })
            continue
        winner = winners[0]
        original_set = set(system.loc[system["in_system"].eq(1), "start_number"])
        protected_set = set(protected.loc[protected["in_system"].eq(1), "start_number"])
        protected_hit = winner in protected_set
        original_hit = winner in original_set
        rows.append({
            "race_id": race_id,
            "winner": winner,
            "original_hit": original_hit,
            "protected_hit": protected_hit,
            "recovered": (not original_hit) and protected_hit,
            "degradation": original_hit and not protected_hit,
            "original_size": len(original_set),
            "protected_size": len(protected_set),
            "protected_count": decisions["protection_summary"]["protected_count"],
            "dropped_count": decisions["protection_summary"]["dropped_count"],
            "rule_1_applied": any("Rule 1" in x for x in decisions["protection_rules_applied"]),
            "rule_2_applied": any("Rule 2" in x for x in decisions["protection_rules_applied"]),
            "rule_3_applied": any("Rule 3" in x for x in decisions["protection_rules_applied"]),
            "winner_phoenix_rank": int(race.loc[race["start_number"].eq(winner), "phoenix_rank"].iloc[0]),
            "source_file": race["__source_file"].iloc[0],
        })

    result = pd.DataFrame(rows)
    valid = result[result["status"].isna()] if "status" in result else result
    summary = {
        "races_total": int(len(result)),
        "races_valid": int(len(valid)),
        "original_hits": int(valid["original_hit"].sum()) if len(valid) else 0,
        "protected_hits": int(valid["protected_hit"].sum()) if len(valid) else 0,
        "recoveries": int(valid["recovered"].sum()) if len(valid) else 0,
        "degradations": int(valid["degradation"].sum()) if len(valid) else 0,
        "system_size_changed_cases": int((valid["original_size"] != valid["protected_size"]).sum()) if len(valid) else 0,
        "rule_1_applied": int(valid["rule_1_applied"].sum()) if len(valid) else 0,
        "rule_2_applied": int(valid["rule_2_applied"].sum()) if len(valid) else 0,
        "rule_3_applied": int(valid["rule_3_applied"].sum()) if len(valid) else 0,
        "no_fabricated_result": True,
    }
    return result, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    inp, out = Path(args.input), Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    df = load_snapshots(inp)
    errors = validate(df)
    if errors:
        (out / "PHASE2_VALIDATION_ERRORS.json").write_text(
            json.dumps({"errors": errors, "rows_loaded": len(df)}, indent=2),
            encoding="utf-8",
        )
        print("\n".join(errors))
        return 2

    results, summary = backtest(df)
    results.to_csv(out / "PHASE2_RACE_RESULTS.csv", index=False)
    (out / "PHASE2_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# PHOENIX 15 — LIVE DASHBOARD V1
# Produces clean PNG charts + an HTML report from the Intelligent Engine output.
# No model/master/frozen data is modified.

from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

VERSION = "1.0"


def _safe_name(value) -> str:
    return str(value).replace("/", "-").replace(" ", "_")


def render(result: dict, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    top7 = result["top7"].copy()
    spikes = result["spikes"].copy()
    skrall = result["skrall"].copy()
    budget = result["budget"]

    files = {}

    # 1. TOP7 — one clean figure
    if "horse_name" in top7.columns:
        labels = top7["horse_name"].astype(str)
    else:
        labels = top7["horse_id"].astype(str)
    top7_plot = top7.copy()
    top7_plot["label"] = labels
    top7_plot = top7_plot.sort_values("score_6040", ascending=True).tail(20)

    fig = plt.figure(figsize=(11, 7))
    plt.barh(top7_plot["label"], top7_plot["score_6040"])
    plt.xlabel("Phoenix 60/40 score")
    plt.ylabel("Horse")
    plt.title("PHOENIX 15 — TOP7 candidate pool")
    plt.tight_layout()
    path = out / "phoenix15_top7.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    files["top7"] = str(path)

    # 2. SPIK — separate figure
    if not spikes.empty:
        sp = spikes.copy()
        sp["label"] = (
            sp.get("horse_name", sp.get("horse_id", "" )).astype(str)
            + " — " + sp["spikzon"].astype(str)
        )
        sp = sp.sort_values("marginal", ascending=True)
        fig = plt.figure(figsize=(10, 6))
        plt.barh(sp["label"], sp["marginal"] * 100)
        plt.xlabel("Marginal P1–P2 (percentage points)")
        plt.ylabel("Horse")
        plt.title("PHOENIX 15 — Spike motor")
        plt.tight_layout()
        path = out / "phoenix15_spikes.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        files["spikes"] = str(path)

    # 3. SKRÄLL — separate figure
    if not skrall.empty:
        counts = skrall["skrall_grade"].value_counts().sort_index()
        fig = plt.figure(figsize=(8, 5))
        plt.bar(counts.index.astype(str), counts.values)
        plt.xlabel("Skräll grade")
        plt.ylabel("Antal TOP7-kandidater")
        plt.title("PHOENIX 15 — Skrällmotor")
        plt.tight_layout()
        path = out / "phoenix15_skrall.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        files["skrall"] = str(path)

    # 4. Lightweight HTML report
    def table_html(df: pd.DataFrame, cols: list[str], n: int = 100) -> str:
        cols = [c for c in cols if c in df.columns]
        return df[cols].head(n).to_html(index=False, classes="data", border=0)

    spike_cols = ["race_id", "number", "horse_name", "odds", "market_rank", "field_size", "marginal", "spikzon"]
    skrall_cols = ["race_id", "number", "horse_name", "market_rank", "phoenix_rank", "rank_6040", "skrall_grade", "skrall_status"]

    html = f"""<!doctype html>
<html lang='sv'>
<head>
<meta charset='utf-8'>
<title>Phoenix 15 Live Dashboard</title>
<style>
body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin:32px; line-height:1.45; }}
h1 {{ margin-bottom:4px; }}
.card {{ border:1px solid #ddd; border-radius:14px; padding:18px; margin:16px 0; }}
img {{ max-width:100%; border-radius:10px; }}
table {{ width:100%; border-collapse:collapse; }}
th,td {{ padding:7px 9px; border-bottom:1px solid #eee; text-align:left; }}
.small {{ color:#666; }}
</style>
</head>
<body>
<h1>PHOENIX 15 — Live Dashboard</h1>
<div class='small'>Engine V{VERSION} · 60/40 · TOP7 → Spike + Skräll → dynamic budget</div>
<div class='card'><h2>Budget</h2><pre>{budget}</pre></div>
<div class='card'><h2>TOP7</h2><img src='phoenix15_top7.png'></div>
<div class='card'><h2>Spikmotor</h2><img src='phoenix15_spikes.png'><h3>Detaljer</h3>{table_html(spikes, spike_cols)}</div>
<div class='card'><h2>Skrällmotor</h2><img src='phoenix15_skrall.png'><h3>Detaljer</h3>{table_html(skrall, skrall_cols)}</div>
</body>
</html>"""

    html_path = out / "phoenix15_live_dashboard.html"
    html_path.write_text(html, encoding="utf-8")
    files["html"] = str(html_path)
    return files

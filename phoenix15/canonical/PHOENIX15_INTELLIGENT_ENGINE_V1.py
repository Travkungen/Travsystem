# PHOENIX 15 — INTELLIGENT ENGINE V1
# Version: 1.0 — 2026-09-07
# Master / Frozen / Model: READ ONLY
#
# Architecture:
# ATG -> active starters -> current Vinnare odds -> Market rank
# -> Phoenix prediction -> exact 60/40 -> TOP7
# -> Spike motor + graded Skräll motor -> dynamic budget -> reduction
#
# IMPORTANT:
# - The 60/40 formula is the recovered OOS Cell 272 formula.
# - Live percentage scaling is an adapter only; it does not modify the model.
# - Million V2 is the only skräll rule marked VALIDATED here.
# - Other skräll grades and dynamic-budget selection are diagnostic/provisional
#   until separately OOS-validated.

from __future__ import annotations
from typing import Any
import pandas as pd

VERSION = "1.0"
PHOENIX_WEIGHT = 0.60
MARKET_WEIGHT = 0.40
TOP_N = 7

PCT_COLS = [
    "win_percent", "top3_percent", "last5_win_percent",
    "driver_win_percent", "driver_top3_percent",
    "trainer_win_percent", "trainer_top3_percent", "hd_win_percent",
]


def prepare_model_features(feature_df: pd.DataFrame) -> pd.DataFrame:
    """Live adapter: model training percentages are stored on a 0-100 scale."""
    x = feature_df.copy()
    for c in PCT_COLS:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce") * 100.0
    return x


def _minmax(s: pd.Series, reverse: bool = False) -> pd.Series:
    lo, hi = s.min(), s.max()
    den = hi - lo
    if den == 0:
        return pd.Series(0.0, index=s.index)
    return ((hi - s) if reverse else (s - lo)) / den


def build_6040(df: pd.DataFrame) -> pd.DataFrame:
    """Exact recovered OOS Cell 272: raw-value min-max, Phoenix 60 / Market 40."""
    x = df.copy()
    x["phoenix_norm"] = x.groupby("race_id")["phoenix_score"].transform(_minmax)
    x["market_norm"] = x.groupby("race_id")["odds"].transform(
        lambda s: _minmax(s, reverse=True)
    )
    x["score_6040"] = 0.60 * x["phoenix_norm"] + 0.40 * x["market_norm"]
    x["rank_6040"] = (
        x.groupby("race_id")["score_6040"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    x["phoenix_rank"] = (
        x.groupby("race_id")["phoenix_score"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    x["field_size"] = x.groupby("race_id")["race_id"].transform("count")
    return x


def build_top7(df: pd.DataFrame) -> pd.DataFrame:
    """TOP7 is the candidate pool. Reduction happens later."""
    x = df.sort_values(["race_id", "rank_6040"]).copy()
    return (
        x.groupby("race_id", group_keys=False)
        .head(TOP_N)
        .reset_index(drop=True)
    )


def spike_motor(df: pd.DataFrame) -> pd.DataFrame:
    """OOS-verified spike zones from TEST 32."""
    x = df.copy()
    p1 = x[x["rank_6040"] == 1][
        ["race_id", "score_6040", "market_rank", "field_size"]
    ].rename(columns={"score_6040": "p1_score"})
    p2 = x[x["rank_6040"] == 2][
        ["race_id", "score_6040"]
    ].rename(columns={"score_6040": "p2_score"})
    r = p1.merge(p2, on="race_id", how="left")
    r["marginal"] = r["p1_score"] - r["p2_score"]

    def zone(row: pd.Series) -> str:
        m, mr, fs = row["marginal"], row["market_rank"], row["field_size"]
        if mr <= 2 and m >= 0.40 and fs >= 9:
            return "S4"
        if mr <= 2 and 0.20 <= m < 0.30:
            return "S2"
        if mr <= 2 and 0.30 <= m < 0.40:
            return "S3"
        if mr <= 2 and 0.10 <= m < 0.20:
            return "S1"
        return "Ingen"

    r["spikzon"] = r.apply(zone, axis=1)
    p1horses = x[x["rank_6040"] == 1].copy()
    cols = [c for c in ["race_id", "number", "horse_name", "horse_id", "odds"] if c in p1horses]
    return p1horses[cols].merge(
        r[["race_id", "marginal", "spikzon", "field_size", "market_rank"]],
        on="race_id", how="left"
    )


def skrall_motor(top7: pd.DataFrame) -> pd.DataFrame:
    """Graded skräll diagnostics. Million V2 is validated; broader grades are provisional."""
    x = top7.copy()
    x["million_v2"] = (
        (x["rank_6040"] == 5)
        & (x["phoenix_rank"] == 3)
        & (x["market_rank"].between(4, 5))
    )
    x["skrall_grade"] = "S1"
    x.loc[
        (x["rank_6040"] <= 7)
        & (x["phoenix_rank"] <= 3)
        & (x["market_rank"].between(4, 7)),
        "skrall_grade",
    ] = "S2"
    x.loc[x["million_v2"], "skrall_grade"] = "S4"
    x["skrall_status"] = x["million_v2"].map(
        {True: "VALIDERAD MILLION V2", False: "DIAGNOSTISK — EJ LÅST"}
    )
    return x


def dynamic_budget(spikes: pd.DataFrame, race_count: int) -> dict[str, Any]:
    """Provisional budget policy. Must be OOS-validated before production lock."""
    s4 = int((spikes["spikzon"] == "S4").sum())
    s2 = int((spikes["spikzon"] == "S2").sum())
    s3 = int((spikes["spikzon"] == "S3").sum())
    if s4 >= 1 and s2 >= 2:
        selected_max = 3
    elif s4 >= 1 or s2 >= 2:
        selected_max = 2
    elif s2 == 1 or s3 >= 1:
        selected_max = 1
    else:
        selected_max = 0
    return {
        "status": "PROVISIONAL",
        "race_count": int(race_count),
        "s4": s4,
        "s2": s2,
        "s3": s3,
        "recommended_spik_max": min(selected_max, 3),
    }


def run(df: pd.DataFrame) -> dict[str, Any]:
    ranked = build_6040(df)
    top7 = build_top7(ranked)
    spikes = spike_motor(ranked)
    skrall = skrall_motor(top7)
    budget = dynamic_budget(spikes, ranked["race_id"].nunique())
    return {
        "ranked": ranked,
        "top7": top7,
        "spikes": spikes,
        "skrall": skrall,
        "budget": budget,
    }

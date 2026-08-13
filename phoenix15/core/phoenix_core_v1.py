"""Phoenix 15 Core V1.0
Reusable race-level Phoenix engine.
No database writes. Designed to work with any starter set containing
race id, horse id and phoenix score.
"""
from __future__ import annotations
import pandas as pd


def _level(gap: float) -> str:
    if pd.isna(gap):
        return "⚪ EJ KLASSAD"
    if gap < 5:
        return "🔴 NIVÅ 1"
    if gap < 10:
        return "🟡 NIVÅ 2"
    if gap < 20:
        return "🟢 NIVÅ 3"
    return "🟢🟢 NIVÅ 4"


def build_race_engine(starters: pd.DataFrame) -> pd.DataFrame:
    """Build reusable race-level ranking from any starter population.

    Required columns: race id, horse id, phoenix score.
    Accepted race-id aliases: atg_race_id, race_id.
    """
    df = starters.copy()
    race_col = next((c for c in ("atg_race_id", "race_id") if c in df.columns), None)
    if race_col is None:
        raise ValueError("Saknar race-id: atg_race_id eller race_id")
    for c in ("horse_id", "phoenix_score"):
        if c not in df.columns:
            raise ValueError(f"Saknar obligatorisk kolumn: {c}")

    df["phoenix_score"] = pd.to_numeric(df["phoenix_score"], errors="coerce")
    df = df.dropna(subset=[race_col, "horse_id", "phoenix_score"]).copy()
    df = df.sort_values([race_col, "phoenix_score"], ascending=[True, False])
    df["phoenix_rank"] = df.groupby(race_col).cumcount() + 1

    race = df.groupby(race_col, as_index=False).agg(
        top_score=("phoenix_score", "max"),
        field_size=("horse_id", "nunique"),
    )
    second = (
        df[df["phoenix_rank"] == 2][[race_col, "phoenix_score"]]
        .rename(columns={"phoenix_score": "second_score"})
    )
    top = df[df["phoenix_rank"] == 1][[race_col, "horse_id", "phoenix_score"]].rename(
        columns={"horse_id": "top_horse_id", "phoenix_score": "top_score"}
    )
    race = race.merge(second, on=race_col, how="left").merge(top, on=race_col, how="left", suffixes=("", "_top"))
    race["second_score"] = race["second_score"].fillna(0.0)
    race["gap"] = race["top_score"] - race["second_score"]
    race["phoenix_level"] = race["gap"].map(_level)

    out = df.merge(
        race[[race_col, "top_horse_id", "top_score", "second_score", "gap", "field_size", "phoenix_level"]],
        on=race_col,
        how="left",
    )
    out["phoenix_is_top"] = out["phoenix_rank"].eq(1)
    return out


def summarize_races(engine_df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per race, suitable for coupon analysis."""
    race_col = "atg_race_id" if "atg_race_id" in engine_df.columns else "race_id"
    cols = [race_col, "top_horse_id", "top_score", "second_score", "gap", "field_size", "phoenix_level"]
    return engine_df[cols].drop_duplicates(race_col).sort_values(race_col).reset_index(drop=True)

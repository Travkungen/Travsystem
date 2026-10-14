"""Phoenix 15 live ATG market layer.

Fetches current winner odds into a separate dataframe and ranks the market.
Does not change Phoenix features, predictions, the frozen model, or SQLite.
The verified ATG endpoint is /services/racinginfo/v1/api/games/vinnare_{race_id};
its raw odds are expressed in thousandths and converted by dividing by 1000.
"""
from __future__ import annotations

from typing import Any, Callable
import math
import time

import pandas as pd
import requests

ATG_BASE = "https://www.atg.se/services/racinginfo/v1/api"


def normalize_atg_odds(raw: Any) -> float | None:
    """Convert verified ATG raw winner odds to decimal odds; reject sentinels."""
    if raw is None:
        return None
    try:
        value = float(str(raw).replace(",", "."))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or value <= 0 or value in (9998, 9999):
        return None
    odds = value / 1000.0
    return odds if odds > 1.0 else None


def parse_race_market(race_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse one ATG vinnare game response into canonical market rows."""
    races = payload.get("races") or []
    matching = [race for race in races if str(race.get("id")) == str(race_id)]
    if not matching and len(races) == 1:
        matching = races
    if not matching:
        raise ValueError(f"ATG-svaret saknar lopp {race_id}")
    rows = []
    for start in matching[0].get("starts") or []:
        horse = start.get("horse") or {}
        raw = ((start.get("pools") or {}).get("vinnare") or {}).get("odds")
        rows.append({
            "race_id": str(race_id),
            "horse_id": horse.get("id"),
            "start_number": start.get("number"),
            "horse_name": horse.get("name"),
            "odds_raw": raw,
            "odds": normalize_atg_odds(raw),
            "scratched": bool(start.get("scratched", False)),
        })
    return rows


def fetch_market(
    race_ids: list[str],
    timeout: int = 20,
    get: Callable[..., Any] | None = None,
    pause_seconds: float = 0.0,
) -> pd.DataFrame:
    """Fetch each requested race; fail loudly rather than silently skipping it."""
    http_get = get or requests.get
    rows: list[dict[str, Any]] = []
    for race_id in race_ids:
        url = f"{ATG_BASE}/games/vinnare_{race_id}"
        response = http_get(url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"ATG-svar är inte ett objekt för {race_id}")
        race_rows = parse_race_market(str(race_id), payload)
        if not race_rows:
            raise ValueError(f"ATG gav inga starter för lopp {race_id}")
        rows.extend(race_rows)
        if pause_seconds:
            time.sleep(pause_seconds)

    columns = [
        "race_id", "horse_id", "start_number", "horse_name",
        "odds_raw", "odds", "scratched", "market_rank", "favorite"
    ]
    market = pd.DataFrame(rows)
    if market.empty:
        return pd.DataFrame(columns=columns)
    market["race_id"] = market["race_id"].astype(str)
    market["start_number"] = pd.to_numeric(market["start_number"], errors="coerce")
    market["odds"] = pd.to_numeric(market["odds"], errors="coerce")
    if market.duplicated(["race_id", "start_number"]).any():
        raise ValueError("Dubbletter i ATG-marknad på race_id + start_number")
    market["market_rank"] = market.groupby("race_id")["odds"].rank(
        method="min", ascending=True
    )
    market["favorite"] = market["market_rank"].eq(1)
    return market[columns]


def attach_market(phoenix_df: pd.DataFrame, market_df: pd.DataFrame) -> pd.DataFrame:
    """Attach odds and market rank by race/start number without altering Phoenix rank."""
    keys = ["race_id", "start_number"]
    for label, df in (("Phoenix", phoenix_df), ("marknad", market_df)):
        missing = [col for col in keys if col not in df.columns]
        if missing:
            raise ValueError(f"{label} saknar nyckelkolumner: {missing}")
    phoenix = phoenix_df.copy()
    market = market_df.copy()
    phoenix["race_id"] = phoenix["race_id"].astype(str)
    market["race_id"] = market["race_id"].astype(str)
    phoenix["start_number"] = pd.to_numeric(phoenix["start_number"], errors="coerce")
    market["start_number"] = pd.to_numeric(market["start_number"], errors="coerce")
    if phoenix.duplicated(keys).any() or market.duplicated(keys).any():
        raise ValueError("Dubbletter på race_id + start_number")
    result = phoenix.merge(
        market[keys + ["odds", "market_rank", "favorite", "horse_name"]],
        on=keys, how="left", validate="one_to_one", suffixes=("", "_market")
    )
    result["market_match"] = result["odds"].notna()
    return result


def validate_market(
    market_df: pd.DataFrame,
    expected_races: int,
    expected_starters: int,
) -> dict[str, Any]:
    """Validate race/starter coverage and at least one valid odds per race."""
    races = int(market_df["race_id"].nunique()) if "race_id" in market_df else 0
    rows = len(market_df)
    valid_odds = int(market_df["odds"].notna().sum()) if "odds" in market_df else 0
    races_with_odds = (
        int(market_df.loc[market_df["odds"].notna(), "race_id"].nunique())
        if {"race_id", "odds"}.issubset(market_df.columns) else 0
    )
    errors = []
    if rows != expected_starters:
        errors.append(f"starter rows {rows}, expected {expected_starters}")
    if races != expected_races:
        errors.append(f"races {races}, expected {expected_races}")
    if races_with_odds != expected_races:
        errors.append(f"valid odds found in {races_with_odds}/{expected_races} races")
    if market_df.duplicated(["race_id", "start_number"]).any():
        errors.append("duplicate race_id + start_number")
    return {
        "status": "OK" if not errors else "FAIL",
        "races": races,
        "starters": rows,
        "valid_odds": valid_odds,
        "missing_odds": rows - valid_odds,
        "errors": errors,
    }


def combine_ranks(
    ranked_df: pd.DataFrame,
    phoenix_weight: float = 0.35,
    market_weight: float = 0.65,
    phoenix_rank_col: str = "phoenix_mark",
) -> pd.DataFrame:
    """Blend within-race Phoenix and market rank strengths using 35/65 weights.

    Rank 1 is best for both inputs. Each rank is converted to a 0..1 strength
    within its race, where 1 is best and 0 is worst. Missing market ranks are
    assigned the worst market strength (0), never treated as favorites.
    The original Phoenix ranking and market rank are preserved.
    """
    if not math.isclose(phoenix_weight + market_weight, 1.0, abs_tol=1e-9):
        raise ValueError("Vikterna måste summera till 1.0")
    if phoenix_weight < 0 or market_weight < 0:
        raise ValueError("Vikterna får inte vara negativa")
    required = ["race_id", phoenix_rank_col, "market_rank"]
    missing = [c for c in required if c not in ranked_df.columns]
    if missing:
        raise ValueError(f"Saknar kolumner för kombinerad ranking: {missing}")

    result = ranked_df.copy()
    result["phoenix_rank_original"] = pd.to_numeric(result[phoenix_rank_col], errors="coerce")
    result["market_rank_original"] = pd.to_numeric(result["market_rank"], errors="coerce")
    if result["phoenix_rank_original"].isna().any():
        raise ValueError("Phoenix-rank saknas för en eller flera starter")

    group = result.groupby("race_id", sort=False)
    counts = group["race_id"].transform("size").astype(float)
    p = result["phoenix_rank_original"]
    m = result["market_rank_original"]
    denom = (counts - 1).clip(lower=1)
    result["phoenix_strength"] = 1.0 - (p - 1.0) / denom
    market_strength = 1.0 - (m - 1.0) / denom
    result["market_strength"] = market_strength.fillna(0.0).clip(0.0, 1.0)
    result["phoenix_strength"] = result["phoenix_strength"].clip(0.0, 1.0)
    result["combined_score"] = (
        phoenix_weight * result["phoenix_strength"]
        + market_weight * result["market_strength"]
    )
    result["combined_rank"] = (
        result.groupby("race_id", sort=False)["combined_score"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    result = result.sort_values(
        ["race_id", "combined_rank", "phoenix_rank_original", "start_number"],
        kind="stable"
    ).reset_index(drop=True)
    result.attrs["phoenix_weight"] = phoenix_weight
    result.attrs["market_weight"] = market_weight
    return result


def add_rescue_value_signals(
    ranked_df: pd.DataFrame,
    phoenix_rank_col: str = "phoenix_rank_original",
    top_n: int = 7,
) -> pd.DataFrame:
    """Add transparent, non-ranking-changing divergence flags.

    Rescue candidate: market ranks the horse in its Top N, but Phoenix does not.
    Value candidate: Phoenix ranks the horse in its Top N, but market does not.
    These are candidate flags, not a calibrated probability or a replacement for
    any separately maintained historical Rescue/Value engine.
    """
    required = ["race_id", phoenix_rank_col, "market_rank", "combined_rank"]
    missing = [col for col in required if col not in ranked_df.columns]
    if missing:
        raise ValueError(f"Saknar kolumner för Rescue/Value-signaler: {missing}")
    if top_n < 1:
        raise ValueError("top_n måste vara minst 1")

    result = ranked_df.copy()
    phoenix_rank = pd.to_numeric(result[phoenix_rank_col], errors="coerce")
    market_rank = pd.to_numeric(result["market_rank"], errors="coerce")
    result["rescue_candidate"] = market_rank.le(top_n) & phoenix_rank.gt(top_n)
    result["value_candidate"] = phoenix_rank.le(top_n) & market_rank.gt(top_n)
    result["rescue_value_reason"] = ""
    result.loc[result["rescue_candidate"], "rescue_value_reason"] = (
        "MARKNAD_RESCUE: marknad Top N, Phoenix utanför Top N"
    )
    result.loc[result["value_candidate"], "rescue_value_reason"] = (
        "PHOENIX_VALUE: Phoenix Top N, marknad utanför Top N"
    )
    return result

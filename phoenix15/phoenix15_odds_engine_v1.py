"""Phoenix 15 odds engine v1.

Production market-data producer for ATG Vinnare pools.
READ ONLY: fetches current ATG market data and returns canonical rows.
Does not modify Phoenix model features, Master, or historical database.
"""
from __future__ import annotations

from typing import Any
import requests
import pandas as pd


ATG_BASE = "https://horse-betting-info.prod.c1.atg.cloud/api-public/v0"


def fetch_vinnare_race(race_id: str, timeout: int = 20) -> dict[str, Any]:
    url = f"{ATG_BASE}/games/vinnare_{race_id}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise ValueError(f"ATG Vinnare-svar är inte dict för {race_id}")
    return data


def build_odds_rows(race_id: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    races = data.get("races") or []
    race = races[0] if races else {}
    rows = []
    for start in race.get("starts", []):
        raw = ((start.get("pools") or {}).get("vinnare") or {}).get("odds")
        if raw in (None, 0, 9998, 9999):
            odds = None
        else:
            odds = float(raw) / 100.0
        rows.append({
            "race_id": race_id,
            "start_id": start.get("id"),
            "start_number": start.get("number"),
            "odds": odds,
            "scratched": bool(start.get("scratched", False)),
        })
    return rows


def fetch_market(discovered: list[dict[str, Any]], timeout: int = 20) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in discovered:
        race_id = item.get("race_id")
        if not race_id:
            continue
        data = fetch_vinnare_race(race_id, timeout=timeout)
        rows.extend(build_odds_rows(race_id, data))

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=[
            "race_id", "start_id", "start_number", "odds",
            "scratched", "market_rank", "favorite"
        ])

    df["market_rank"] = df.groupby("race_id")["odds"].rank(
        method="min", ascending=True
    )
    df["favorite"] = df["market_rank"].eq(1)
    return df


__all__ = ["fetch_vinnare_race", "build_odds_rows", "fetch_market"]

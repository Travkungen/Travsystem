"""Phoenix 15 market-data layer.

Market data is deliberately separate from the 20 Phoenix model features.
Historical Phoenix archive data stored odds as `odds_sort` alongside
`race_id`, `horse_id` and `start_position`.
"""
from __future__ import annotations

from typing import Any, Iterable
import math
import pandas as pd


class PhoenixMarketData:
    VERSION = "1.0"

    @staticmethod
    def normalize_odds(value: Any) -> float | None:
        """Normalize odds to decimal odds.

        Historical `odds_sort` values such as 285 represent 2.85.
        9998/9999 are special/unavailable values and become missing.
        """
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        try:
            x = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None
        if x <= 0 or x >= 9998:
            return None
        if x >= 100:
            x /= 100.0
        return x if x > 1.0 else None

    @classmethod
    def normalize_market_rows(cls, rows: Iterable[dict]) -> pd.DataFrame:
        """Convert raw market rows to the canonical Phoenix market schema."""
        records = []
        for row in rows:
            raw_odds = row.get("odds")
            if raw_odds is None:
                raw_odds = row.get("odds_sort")
            if raw_odds is None:
                raw_odds = row.get("win_odds")
            records.append({
                "race_id": row.get("race_id"),
                "horse_id": row.get("horse_id"),
                "start_number": row.get("start_number", row.get("start_position")),
                "odds": cls.normalize_odds(raw_odds),
            })

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(columns=[
                "race_id", "horse_id", "start_number", "odds",
                "market_rank", "favorite"
            ])

        df["odds"] = pd.to_numeric(df["odds"], errors="coerce")
        df["market_rank"] = df.groupby("race_id")["odds"].rank(
            method="min", ascending=True
        )
        df["favorite"] = df["market_rank"].eq(1)
        return df

    @staticmethod
    def validate_market_data(market_df: pd.DataFrame, expected_starters: int | None = None) -> dict:
        required = [
            "race_id", "horse_id", "start_number", "odds",
            "market_rank", "favorite"
        ]
        missing = [c for c in required if c not in market_df.columns]
        duplicate_keys = 0
        if not missing and len(market_df):
            duplicate_keys = int(
                market_df.duplicated(["race_id", "horse_id"]).sum()
            )

        valid_odds = int(market_df["odds"].notna().sum()) if "odds" in market_df else 0
        races = int(market_df["race_id"].nunique()) if "race_id" in market_df else 0
        favorites = int(market_df["favorite"].sum()) if "favorite" in market_df else 0

        errors = []
        if missing:
            errors.append(f"missing_columns={missing}")
        if duplicate_keys:
            errors.append(f"duplicate_keys={duplicate_keys}")
        if expected_starters is not None and len(market_df) != expected_starters:
            errors.append(f"rows={len(market_df)} expected={expected_starters}")
        if races and favorites != races:
            errors.append(f"favorites={favorites} races={races}")

        return {
            "version": PhoenixMarketData.VERSION,
            "rows": len(market_df),
            "races": races,
            "valid_odds": valid_odds,
            "missing_odds": len(market_df) - valid_odds,
            "favorites": favorites,
            "duplicate_keys": duplicate_keys,
            "errors": errors,
            "status": "OK" if not errors else "FAIL",
        }

    @staticmethod
    def attach_market_data(startlist_df: pd.DataFrame, market_df: pd.DataFrame) -> pd.DataFrame:
        """Attach market fields without changing Phoenix model feature columns."""
        keys = ["race_id", "horse_id"]
        if not set(keys).issubset(startlist_df.columns):
            raise ValueError("Startlist saknar race_id/horse_id")
        if not set(keys).issubset(market_df.columns):
            raise ValueError("Marketdata saknar race_id/horse_id")

        cols = keys + ["odds", "market_rank", "favorite"]
        return startlist_df.merge(
            market_df[cols].drop_duplicates(keys),
            on=keys,
            how="left",
            validate="one_to_one",
        )


__all__ = ["PhoenixMarketData"]

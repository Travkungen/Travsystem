"""Phoenix 15 — Distance Rescue v1.0
READ ONLY rescue layer. Does not modify Phoenix/model rankings.

Purpose:
Identify a small number of horses outside Phoenix TOP7 with documented
strength at today's race distance. Designed as a final high-payout layer.

Expected input columns:
race_id, race_number, start_number, horse_name, phoenix_rank,
race_distance, starts, wins, top3, last5_starts, last5_wins, last5_top3
and optionally race_type/start_method.
"""

from __future__ import annotations
import pandas as pd
import numpy as np


class PhoenixDistanceRescueV1:
    VERSION = "1.0"

    def __init__(self, phoenix_min_rank: int = 8, phoenix_max_rank: int = 15):
        self.phoenix_min_rank = phoenix_min_rank
        self.phoenix_max_rank = phoenix_max_rank

    @staticmethod
    def _num(df, col, default=0.0):
        return pd.to_numeric(df[col], errors="coerce").fillna(default) if col in df else pd.Series(default, index=df.index)

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        out["phoenix_rank"] = self._num(out, "phoenix_rank", 99)
        out["race_distance"] = self._num(out, "race_distance", np.nan)

        # Historical distance evidence. The actual race-result distance
        # history is expected in precomputed columns when available.
        exact = self._num(out, "distance_exact_starts", 0)
        exact_wins = self._num(out, "distance_exact_wins", 0)
        exact_top3 = self._num(out, "distance_exact_top3", 0)
        near = self._num(out, "distance_near_starts", 0)
        near_wins = self._num(out, "distance_near_wins", 0)
        near_top3 = self._num(out, "distance_near_top3", 0)

        exact_win_pct = np.where(exact > 0, exact_wins / exact * 100, 0)
        exact_top3_pct = np.where(exact > 0, exact_top3 / exact * 100, 0)
        near_top3_pct = np.where(near > 0, near_top3 / near * 100, 0)

        # Exact distance is deliberately dominant.
        exact_score = np.minimum(exact, 5) / 5 * 25
        exact_score += np.minimum(exact_win_pct, 50) / 50 * 20
        exact_score += np.minimum(exact_top3_pct, 75) / 75 * 15

        near_score = np.minimum(near, 5) / 5 * 10
        near_score += np.minimum(near_top3_pct, 75) / 75 * 10
        near_score += np.minimum(near_wins, 2) / 2 * 5

        out["distance_rescue_score"] = np.round(exact_score + near_score, 2)

        # Only the final layer: outside Phoenix TOP7.
        eligible = out["phoenix_rank"].between(
            self.phoenix_min_rank, self.phoenix_max_rank, inclusive="both"
        )

        # Strong signal requires exact-distance evidence; watch can use
        # either exact or near-distance evidence.
        strong = eligible & (exact >= 1) & (out["distance_rescue_score"] >= 35)
        watch = eligible & (out["distance_rescue_score"] >= 20)

        out["distance_rescue_flag"] = np.select(
            [strong, watch], ["DISTANCE_RESCUE", "DISTANCE_WATCH"], default=""
        )

        out["distance_rescue_reason"] = np.select(
            [
                strong & (exact_wins >= 1),
                strong,
                watch & (exact >= 1),
                watch,
            ],
            [
                "vinnande historik på aktuell distans",
                "stark historik på aktuell distans",
                "dokumenterad historik på aktuell distans",
                "liknande distanshistorik",
            ],
            default="",
        )
        return out

    def top_candidates(self, df: pd.DataFrame, per_race: int = 4) -> pd.DataFrame:
        x = self.score(df)
        x = x[x["distance_rescue_flag"] != ""].copy()
        x = x.sort_values(
            ["race_id", "distance_rescue_score", "phoenix_rank"],
            ascending=[True, False, True],
        )
        return x.groupby("race_id", group_keys=False).head(per_race).reset_index(drop=True)


def apply_distance_rescue(df: pd.DataFrame) -> pd.DataFrame:
    return PhoenixDistanceRescueV1().score(df)

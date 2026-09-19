"""
Phoenix 15 — Historical Rescue Engine v1.0

Purpose:
    Separate READ ONLY rescue layer for horses whose historical/form profile
    deserves consideration despite a weak raw Phoenix rank.

Important:
    - Does NOT modify Phoenix score/rank.
    - Does NOT modify Frozen/Master/model/production.
    - Uses the existing PhoenixHorseHistory output.
    - Experimental candidate/rescue layer only.

Input columns expected:
    race_id, horse_id, starts, wins, win_percent, top3, top3_percent,
    last5_starts, last5_wins, last5_top3, last5_win_percent,
    last5_top3_percent

Output:
    historical_rescue_score
    historical_rescue_flag
    historical_rescue_reason
"""

import numpy as np
import pandas as pd


class PhoenixHistoricalRescueV1:
    VERSION = "1.0"

    def __init__(
        self,
        min_starts=3,
        strong_score=60.0,
        watch_score=45.0,
        weak_phoenix_rank=8,
        max_rescue_rank=15,
    ):
        self.min_starts = int(min_starts)
        self.strong_score = float(strong_score)
        self.watch_score = float(watch_score)
        self.weak_phoenix_rank = int(weak_phoenix_rank)
        self.max_rescue_rank = int(max_rescue_rank)

    @staticmethod
    def _num(df, col):
        if col not in df.columns:
            return pd.Series(0.0, index=df.index)
        return pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    def score(self, df):
        x = df.copy()

        starts = self._num(x, "starts")
        wins = self._num(x, "wins")
        top3 = self._num(x, "top3")
        last5_starts = self._num(x, "last5_starts")
        last5_wins = self._num(x, "last5_wins")
        last5_top3 = self._num(x, "last5_top3")

        career_win = self._num(x, "win_percent")
        career_top3 = self._num(x, "top3_percent")
        recent_win = self._num(x, "last5_win_percent")
        recent_top3 = self._num(x, "last5_top3_percent")

        # Evidence components are deliberately capped and transparent.
        # Recent form receives more weight than career history.
        recent_component = (
            0.45 * np.clip(recent_win * 100.0, 0, 100)
            + 0.55 * np.clip(recent_top3 * 100.0, 0, 100)
        )

        career_component = (
            0.40 * np.clip(career_win * 100.0, 0, 100)
            + 0.60 * np.clip(career_top3 * 100.0, 0, 100)
        )

        sample_factor = np.clip(starts / 10.0, 0.25, 1.0)

        # Consistency bonus: recent top-3 results with a usable sample.
        consistency = np.clip(
            (last5_top3 / np.maximum(last5_starts, 1)) * 15.0,
            0,
            15,
        )

        raw = (
            0.60 * recent_component
            + 0.40 * career_component
            + consistency
        )

        # Avoid overrating horses with almost no historical evidence.
        score = raw * (0.65 + 0.35 * sample_factor)

        x["historical_rescue_score"] = score.round(2)

        # Rescue is only relevant when Phoenix itself is outside its normal
        # candidate area. This never changes phoenix_rank.
        phoenix_rank = self._num(x, "phoenix_rank")
        weak_phoenix = (
            (phoenix_rank >= self.weak_phoenix_rank)
            & (phoenix_rank <= self.max_rescue_rank)
        )

        strong_recent = (
            (last5_starts >= 3)
            & (
                (recent_top3 >= 0.40)
                | (recent_win >= 0.20)
            )
        )

        useful_career = (
            (starts >= self.min_starts)
            & (
                (career_top3 >= 0.35)
                | (career_win >= 0.15)
            )
        )

        strong = weak_phoenix & (score >= self.strong_score) & (
            strong_recent | useful_career
        )

        watch = weak_phoenix & (score >= self.watch_score)

        x["historical_rescue_flag"] = np.select(
            [strong, watch],
            ["RESCUE", "WATCH"],
            default="NONE",
        )

        def reason(row):
            if row["historical_rescue_flag"] == "NONE":
                return ""
            reasons = []
            if row["last5_top3_percent"] >= 0.40:
                reasons.append("recent_top3")
            if row["last5_win_percent"] >= 0.20:
                reasons.append("recent_win")
            if row["top3_percent"] >= 0.35:
                reasons.append("career_top3")
            if row["win_percent"] >= 0.15:
                reasons.append("career_win")
            return "+".join(reasons) if reasons else "history_signal"

        x["historical_rescue_reason"] = x.apply(reason, axis=1)

        return x

    def build(self, history_df):
        required = [
            "race_id",
            "horse_id",
            "phoenix_rank",
        ]
        missing = [c for c in required if c not in history_df.columns]
        if missing:
            raise ValueError(f"Data saknar: {missing}")

        return self.score(history_df)

    def top_rescues(self, scored_df):
        cols = [
            c for c in [
                "race_id",
                "horse_id",
                "horse_name",
                "phoenix_rank",
                "market_rank",
                "historical_rescue_score",
                "historical_rescue_flag",
                "historical_rescue_reason",
            ]
            if c in scored_df.columns
        ]

        return (
            scored_df.loc[
                scored_df["historical_rescue_flag"].isin(["RESCUE", "WATCH"]),
                cols,
            ]
            .sort_values(
                ["race_id", "historical_rescue_score"],
                ascending=[True, False],
            )
            .reset_index(drop=True)
        )

"""Phoenix 15 performance metrics and benchmark persistence."""

from __future__ import annotations

import sqlite3
from typing import Any

import pandas as pd


class PhoenixPerformance:
    """Evaluate Phoenix predictions against final race results."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def load_evaluation_data(self) -> pd.DataFrame:
        with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
            return pd.read_sql_query(
                """
                SELECT
                    p.atg_race_id,
                    p.horse_id,
                    p.phoenix_score,
                    p.phoenix_probability,
                    r.placement_sort,
                    r.odds,
                    r.withdrawn,
                    r.result_status
                FROM phoenix15_predictions p
                JOIN phoenix15_results r
                  ON p.atg_race_id = r.atg_race_id
                 AND p.horse_id = r.horse_id
                WHERE r.result_status = 'FINAL'
                  AND r.withdrawn = 0
                """,
                conn,
            )

    def evaluate(self, results: pd.DataFrame | None = None) -> dict[str, Any]:
        df = self.load_evaluation_data() if results is None else results.copy()
        if df.empty:
            raise ValueError("No final, non-withdrawn results available")

        df["phoenix_rank"] = (
            df.groupby("atg_race_id")["phoenix_score"]
            .rank(method="min", ascending=False)
        )
        winners = df[df["placement_sort"] == 1].copy()
        races = int(df["atg_race_id"].nunique())

        avg_market_probability = (1.0 / df["odds"].replace(0, pd.NA)).mean()
        avg_phoenix_probability = df["phoenix_probability"].mean()

        return {
            "races": races,
            "starters": int(len(df)),
            "top1_hits": int((winners["phoenix_rank"] <= 1).sum()),
            "top3_hits": int((winners["phoenix_rank"] <= 3).sum()),
            "top5_hits": int((winners["phoenix_rank"] <= 5).sum()),
            "top10_hits": int((winners["phoenix_rank"] <= 10).sum()),
            "top1_pct": float((winners["phoenix_rank"] <= 1).mean() * 100),
            "top3_pct": float((winners["phoenix_rank"] <= 3).mean() * 100),
            "top5_pct": float((winners["phoenix_rank"] <= 5).mean() * 100),
            "top10_pct": float((winners["phoenix_rank"] <= 10).mean() * 100),
            "avg_winner_rank": float(winners["phoenix_rank"].mean()),
            "avg_winner_odds": float(winners["odds"].mean()),
            "median_winner_odds": float(winners["odds"].median()),
            "avg_phoenix_probability": float(avg_phoenix_probability),
            "avg_market_probability": float(avg_market_probability),
            "avg_phoenix_edge": float(
                (df["phoenix_probability"] - 1.0 / df["odds"]).mean()
            ),
        }

    def save_benchmark(
        self,
        race_date: str,
        track_name: str,
        report: dict[str, Any],
    ) -> bool:
        """Persist one benchmark per race date/track; never duplicate it."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS phoenix15_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_date TEXT NOT NULL,
                    track_name TEXT NOT NULL,
                    races INTEGER NOT NULL,
                    starters INTEGER NOT NULL,
                    top1_hits INTEGER,
                    top3_hits INTEGER,
                    top5_hits INTEGER,
                    top10_hits INTEGER,
                    top1_pct REAL,
                    top3_pct REAL,
                    top5_pct REAL,
                    top10_pct REAL,
                    avg_winner_rank REAL,
                    avg_winner_odds REAL,
                    median_winner_odds REAL,
                    avg_phoenix_probability REAL,
                    avg_market_probability REAL,
                    avg_phoenix_edge REAL,
                    created_at TEXT NOT NULL,
                    UNIQUE(race_date, track_name)
                )
                """
            )
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO phoenix15_performance (
                    race_date, track_name, races, starters,
                    top1_hits, top3_hits, top5_hits, top10_hits,
                    top1_pct, top3_pct, top5_pct, top10_pct,
                    avg_winner_rank, avg_winner_odds, median_winner_odds,
                    avg_phoenix_probability, avg_market_probability,
                    avg_phoenix_edge, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    race_date,
                    track_name,
                    report["races"],
                    report["starters"],
                    report["top1_hits"],
                    report["top3_hits"],
                    report["top5_hits"],
                    report["top10_hits"],
                    report["top1_pct"],
                    report["top3_pct"],
                    report["top5_pct"],
                    report["top10_pct"],
                    report["avg_winner_rank"],
                    report["avg_winner_odds"],
                    report["median_winner_odds"],
                    report["avg_phoenix_probability"],
                    report["avg_market_probability"],
                    report["avg_phoenix_edge"],
                ),
            )
            conn.commit()
            return cursor.rowcount == 1

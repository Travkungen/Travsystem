"""Safe, idempotent importer for Phoenix 15 race results.

The importer is intentionally independent of any ATG/network client. Callers
provide a pandas DataFrame containing validated result rows.
"""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from typing import Any

import pandas as pd


class PhoenixResultImporter:
    """Validate, preview and safely import Phoenix result rows."""

    REQUIRED_COLUMNS = {
        "atg_race_id",
        "horse_id",
        "horse_name",
        "placement",
        "placement_sort",
        "odds_sort",
        "odds",
        "race_time",
        "kilometer_time",
        "withdrawn",
        "result_status",
    }

    INSERT_COLUMNS = (
        "atg_race_id",
        "horse_id",
        "horse_name",
        "placement",
        "placement_sort",
        "odds_sort",
        "odds",
        "race_time",
        "kilometer_time",
        "withdrawn",
        "result_status",
        "imported_at",
    )

    def __init__(self, db_path: str):
        self.db_path = db_path

    def validate(self, results: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS - set(results.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        if results.empty:
            raise ValueError("Result data is empty")

        duplicates = results.groupby(["atg_race_id", "horse_id"]).size()
        duplicates = duplicates[duplicates > 1]
        if not duplicates.empty:
            raise ValueError(
                f"Duplicate incoming keys: {len(duplicates)}"
            )

    def preview(self, results: pd.DataFrame) -> dict[str, Any]:
        self.validate(results)

        with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
            existing = pd.read_sql_query(
                """
                SELECT atg_race_id, horse_id, placement, odds
                FROM phoenix15_results
                """,
                conn,
            )

        existing_keys = set(zip(existing.atg_race_id, existing.horse_id))
        incoming_keys = set(zip(results.atg_race_id, results.horse_id))
        new_keys = incoming_keys - existing_keys

        new_rows = results[
            results.apply(
                lambda row: (row.atg_race_id, row.horse_id) in new_keys,
                axis=1,
            )
        ].copy()

        already_rows = results[
            results.apply(
                lambda row: (row.atg_race_id, row.horse_id) in existing_keys,
                axis=1,
            )
        ].copy()

        merged = already_rows.merge(
            existing,
            on=["atg_race_id", "horse_id"],
            suffixes=("_incoming", "_existing"),
        )
        conflicts = merged[
            (merged["placement_incoming"].astype(str)
             != merged["placement_existing"].astype(str))
            | (merged["odds_incoming"].fillna(-1)
               != merged["odds_existing"].fillna(-1))
        ]

        return {
            "incoming": len(results),
            "incoming_races": results["atg_race_id"].nunique(),
            "new": len(new_rows),
            "already": len(already_rows),
            "conflicts": len(conflicts),
            "duplicates": 0,
            "new_rows": new_rows,
        }

    def import_results(self, results: pd.DataFrame) -> dict[str, Any]:
        """Import only genuinely new rows after a conflict-free preview.

        The database transaction is rolled back on any error. Existing rows
        are never updated by this importer.
        """
        preview = self.preview(results)
        if preview["conflicts"]:
            raise RuntimeError(
                f"Import stopped: {preview['conflicts']} conflicts detected"
            )

        new_rows = preview["new_rows"]
        if new_rows.empty:
            return {"status": "NO_NEW_DATA", "imported": 0, "verified": 0}

        imported_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for _, row in new_rows.iterrows():
            rows.append(
                (
                    row.atg_race_id,
                    row.horse_id,
                    row.horse_name,
                    row.placement,
                    row.placement_sort,
                    row.odds_sort,
                    row.odds,
                    row.race_time,
                    row.kilometer_time,
                    int(row.withdrawn),
                    row.result_status,
                    imported_at,
                )
            )

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.executemany(
                    """
                    INSERT INTO phoenix15_results (
                        atg_race_id, horse_id, horse_name, placement,
                        placement_sort, odds_sort, odds, race_time,
                        kilometer_time, withdrawn, result_status, imported_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" for _ in new_rows)
            keys = list(zip(new_rows.atg_race_id, new_rows.horse_id))
            # Verify each imported key exists; no reliance on row ordering.
            verified = 0
            for race_id, horse_id in keys:
                found = conn.execute(
                    """
                    SELECT COUNT(*) FROM phoenix15_results
                    WHERE atg_race_id = ? AND horse_id = ?
                    """,
                    (race_id, horse_id),
                ).fetchone()[0]
                verified += int(found == 1)

        if verified != len(new_rows):
            raise RuntimeError(
                f"Post-import verification failed: {verified}/{len(new_rows)}"
            )

        return {
            "status": "IMPORTED",
            "imported": len(new_rows),
            "verified": verified,
        }

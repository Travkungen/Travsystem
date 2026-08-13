import sqlite3

import pandas as pd

import numpy as np

class PhoenixHorseHistory:

    VERSION = "1.0"

    def __init__(self, conn):

        self.conn = conn

    @staticmethod
    def _num(series):

        return pd.to_numeric(series, errors="coerce")

    @staticmethod
    def _top3_from_placement(df):

        if "placement" not in df.columns:

            return pd.Series(False, index=df.index)

        p = pd.to_numeric(df["placement"], errors="coerce")

        return p.between(1, 3, inclusive="both")

    def horse_history(self, horse_id, before_date):

        sql = """

        SELECT *

        FROM horse_results

        WHERE horse_id = ?

        """

        h = pd.read_sql(

            sql,

            self.conn,

            params=[horse_id]

        )

        if h.empty:

            return self._empty()

        date_col = None

        for c in [

            "race_date",

            "date",

            "start_date"

        ]:

            if c in h.columns:

                date_col = c

                break

        if date_col is None:

            return self._empty()

        h["_date"] = pd.to_datetime(

            h[date_col],

            errors="coerce"

        )

        cutoff = pd.to_datetime(before_date)

        h = h[

            h["_date"].notna() &

            (h["_date"] < cutoff)

        ].copy()

        if h.empty:

            return self._empty()

        if "placement" in h.columns:

            h["_placement"] = pd.to_numeric(

                h["placement"],

                errors="coerce"

            )

        elif "placement_sort" in h.columns:

            h["_placement"] = pd.to_numeric(

                h["placement_sort"],

                errors="coerce"

            )

        else:

            h["_placement"] = np.nan

        starts = len(h)

        wins = int((h["_placement"] == 1).sum())

        top3 = int(

            h["_placement"].between(

                1, 3,

                inclusive="both"

            ).sum()

        )

        h = h.sort_values(

            "_date",

            ascending=False

        )

        last5 = h.head(5)

        last5_starts = len(last5)

        last5_wins = int(

            (last5["_placement"] == 1).sum()

        )

        last5_top3 = int(

            last5["_placement"].between(

                1, 3,

                inclusive="both"

            ).sum()

        )

        win_percent = (

            wins / starts

            if starts > 0 else 0.0

        )

        top3_percent = (

            top3 / starts

            if starts > 0 else 0.0

        )

        last5_win_percent = (

            last5_wins / last5_starts

            if last5_starts > 0 else 0.0

        )

        last5_top3_percent = (

            last5_top3 / last5_starts

            if last5_starts > 0 else 0.0

        )

        return {

            "starts": int(starts),

            "wins": int(wins),

            "win_percent": float(win_percent),

            "top3": int(top3),

            "top3_percent": float(top3_percent),

            "last5_starts": int(last5_starts),

            "last5_wins": int(last5_wins),

            "last5_top3": int(last5_top3),

            "last5_win_percent": float(last5_win_percent),

            "last5_top3_percent": float(last5_top3_percent)

        }

    def build(self, startlist):

        required = [

            "horse_id",

            "race_id"

        ]

        missing = [

            c for c in required

            if c not in startlist.columns

        ]

        if missing:

            raise ValueError(

                f"Startlist saknar: {missing}"

            )

        df = startlist.copy()

        date_col = None

        for c in [

            "race_date",

            "date",

            "start_date"

        ]:

            if c in df.columns:

                date_col = c

                break

        if date_col is None:

            raise ValueError(

                "Startlist saknar datumkolumn"

            )

        df[date_col] = pd.to_datetime(

            df[date_col],

            errors="coerce"

        )

        records = []

        for _, row in df.iterrows():

            horse_id = row["horse_id"]

            if pd.isna(horse_id):

                hist = self._empty()

            else:

                hist = self.horse_history(

                    horse_id,

                    row[date_col]

                )

            rec = {

                "race_id": row["race_id"],

                "horse_id": horse_id

            }

            if "horse_name" in df.columns:

                rec["horse_name"] = row["horse_name"]

            rec.update(hist)

            records.append(rec)

        return pd.DataFrame(records)

    @staticmethod
    def _empty():

        return {

            "starts": 0,

            "wins": 0,

            "win_percent": 0.0,

            "top3": 0,

            "top3_percent": 0.0,

            "last5_starts": 0,

            "last5_wins": 0,

            "last5_top3": 0,

            "last5_win_percent": 0.0,

            "last5_top3_percent": 0.0

        }

import pandas as pd

class Phoenix15PersonBridge:

    """

    Permanent Phoenix 15 person-history bridge.

    VERIFIED SOURCES

    ----------------

    Driver:

        driver_features_v2

    Horse-driver:

        horse_driver_features

    Trainer:

        trainer_features_v2

        (used only when trainer_id is actually present)

    The bridge is runtime-only:

        DB is READ ONLY.

        No tables are modified.

    """

    DRIVER_TABLE = "driver_features_v2"

    TRAINER_TABLE = "trainer_features_v2"

    HORSE_DRIVER_TABLE = "horse_driver_features"

    def __init__(self, conn):

        self.conn = conn

    def _driver_history(self):

        return pd.read_sql_query(

            f"""

            SELECT

                driver_id,

                starts,

                wins,

                win_percent,

                top3,

                top3_percent

            FROM {self.DRIVER_TABLE}

            """,

            self.conn

        )

    def _trainer_history(self):

        return pd.read_sql_query(

            f"""

            SELECT

                trainer_id,

                starts,

                wins,

                win_percent,

                top3,

                top3_percent

            FROM {self.TRAINER_TABLE}

            """,

            self.conn

        )

    def _horse_driver_history(self):

        return pd.read_sql_query(

            f"""

            SELECT

                horse_id,

                driver_id,

                hd_starts,

                hd_wins,

                hd_win_percent

            FROM {self.HORSE_DRIVER_TABLE}

            """,

            self.conn

        )

    def apply(self, features):

        df = features.copy()

        # --------------------------------------------------

        # DRIVER

        # --------------------------------------------------

        driver = self._driver_history()

        if "driver_id" in df.columns:

            driver = driver.drop_duplicates(

                "driver_id"

            ).set_index("driver_id")

            df["driver_starts"] = (

                df["driver_id"]

                .map(driver["starts"])

                .fillna(0)

            )

            df["driver_wins"] = (

                df["driver_id"]

                .map(driver["wins"])

                .fillna(0)

            )

            df["driver_win_percent"] = (

                df["driver_id"]

                .map(driver["win_percent"])

                .fillna(0)

                / 100.0

            )

            df["driver_top3_percent"] = (

                df["driver_id"]

                .map(driver["top3_percent"])

                .fillna(0)

                / 100.0

            )

        # --------------------------------------------------

        # TRAINER

        # --------------------------------------------------

        trainer = self._trainer_history()

        if "trainer_id" in df.columns:

            trainer = trainer.drop_duplicates(

                "trainer_id"

            ).set_index("trainer_id")

            df["trainer_starts"] = (

                df["trainer_id"]

                .map(trainer["starts"])

                .fillna(0)

            )

            df["trainer_wins"] = (

                df["trainer_id"]

                .map(trainer["wins"])

                .fillna(0)

            )

            df["trainer_win_percent"] = (

                df["trainer_id"]

                .map(trainer["win_percent"])

                .fillna(0)

                / 100.0

            )

            df["trainer_top3_percent"] = (

                df["trainer_id"]

                .map(trainer["top3_percent"])

                .fillna(0)

                / 100.0

            )

        # --------------------------------------------------

        # HORSE + DRIVER

        # --------------------------------------------------

        hd = self._horse_driver_history()

        if (

            "horse_id" in df.columns

            and "driver_id" in df.columns

        ):

            hd = hd.drop_duplicates(

                ["horse_id", "driver_id"]

            )

            hd_index = pd.MultiIndex.from_frame(

                hd[["horse_id", "driver_id"]]

            )

            hd_values = hd[

                [

                    "hd_starts",

                    "hd_wins",

                    "hd_win_percent"

                ]

            ].copy()

            hd_values.index = hd_index

            df_index = pd.MultiIndex.from_frame(

                df[["horse_id", "driver_id"]]

            )

            df["hd_starts"] = (

                pd.Series(

                    df_index.map(

                        hd_values["hd_starts"]

                    ),

                    index=df.index

                )

                .fillna(0)

            )

            df["hd_wins"] = (

                pd.Series(

                    df_index.map(

                        hd_values["hd_wins"]

                    ),

                    index=df.index

                )

                .fillna(0)

            )

            df["hd_win_percent"] = (

                pd.Series(

                    df_index.map(

                        hd_values["hd_win_percent"]

                    ),

                    index=df.index

                )

                .fillna(0)

                / 100.0

            )

        return df

import pandas as pd

import numpy as np

class PhoenixFeatureBuild:

    VERSION = "1.0"

    MODEL_FEATURES = [
        "starts", "wins", "win_percent", "top3", "top3_percent",
        "last5_starts", "last5_wins", "last5_top3", "last5_win_percent",
        "driver_starts", "driver_wins", "driver_win_percent", "driver_top3_percent",
        "trainer_starts", "trainer_wins", "trainer_win_percent", "trainer_top3_percent",
        "hd_starts", "hd_wins", "hd_win_percent",
    ]

    VERSION_COLUMNS = {
        "history_starts": "starts",
        "history_wins": "wins",
        "history_win_pct": "win_percent",
        "history_top3": "top3",
        "history_top3_pct": "top3_percent",
        "last5_starts": "last5_starts",
        "last5_wins": "last5_wins",
        "last5_top3": "last5_top3",
        "last5_win_percent": "last5_win_percent",
    }

    def build(self, startlist, horse_history=None):
        df = startlist.copy()

        if horse_history is not None:
            hist = horse_history.copy()
            keys = [c for c in ["race_id", "horse_id"] if c in df.columns and c in hist.columns]
            if keys == ["race_id", "horse_id"]:
                identified_mask = df["horse_id"].notna()
                df_identified = df[identified_mask].copy()
                df_unresolved = df[~identified_mask].copy()
                hist_identified = hist[hist["horse_id"].notna()].copy()
                hist_cols = [c for c in hist_identified.columns if c not in keys]
                if not hist_identified.empty:
                    df_identified = df_identified.merge(
                        hist_identified[keys + hist_cols], on=keys, how="left",
                        suffixes=("", "_hist"), validate="one_to_one"
                    )
                df = pd.concat([df_identified, df_unresolved], ignore_index=True)
                sort_cols = [c for c in ["race_id", "start_number"] if c in df.columns]
                if sort_cols:
                    df = df.sort_values(sort_cols, kind="stable").reset_index(drop=True)
            elif keys:
                hist_cols = [c for c in hist.columns if c not in keys]
                df = df.merge(hist[keys + hist_cols], on=keys, how="left", suffixes=("", "_hist"))

        for source, target in self.VERSION_COLUMNS.items():
            if target in df.columns:
                continue
            if source in df.columns:
                df[target] = df[source]

        for col in self.MODEL_FEATURES:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        if "wins" in df.columns and "starts" in df.columns:
            mask = df["starts"] > 0
            df.loc[mask & (df["win_percent"] == 0), "win_percent"] = (
                df.loc[mask & (df["win_percent"] == 0), "wins"] /
                df.loc[mask & (df["win_percent"] == 0), "starts"]
            )

        if "top3" in df.columns and "starts" in df.columns:
            mask = df["starts"] > 0
            df.loc[mask & (df["top3_percent"] == 0), "top3_percent"] = (
                df.loc[mask & (df["top3_percent"] == 0), "top3"] /
                df.loc[mask & (df["top3_percent"] == 0), "starts"]
            )

        percent_cols = [
            "win_percent", "top3_percent", "last5_win_percent",
            "driver_win_percent", "driver_top3_percent",
            "trainer_win_percent", "trainer_top3_percent", "hd_win_percent",
        ]
        for col in percent_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).clip(0.0, 1.0)

        return df

    def model_matrix(self, df):
        missing = [c for c in self.MODEL_FEATURES if c not in df.columns]
        if missing:
            raise RuntimeError(f"Saknade modellfeatures: {missing}")
        X = df[self.MODEL_FEATURES].copy()
        X = X.apply(pd.to_numeric, errors="coerce")
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0.0)
        return X

    def validate(self, df):
        missing = [c for c in self.MODEL_FEATURES if c not in df.columns]
        if missing:
            raise RuntimeError(f"Feature Build saknar: {missing}")
        X = self.model_matrix(df)
        return {
            "rows": len(df),
            "features": len(self.MODEL_FEATURES),
            "nan": int(X.isna().sum().sum()),
            "inf": int(np.isinf(X.to_numpy()).sum()),
            "missing": missing,
        }

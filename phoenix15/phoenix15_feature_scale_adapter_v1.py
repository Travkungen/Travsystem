import pandas as pd
import numpy as np


class PhoenixFeatureScaleAdapter:
    VERSION = "1.0"

    PERCENT_FEATURES = [
        "win_percent",
        "top3_percent",
        "last5_win_percent",
        "driver_win_percent",
        "driver_top3_percent",
        "trainer_win_percent",
        "trainer_top3_percent",
        "hd_win_percent",
    ]

    MODEL_PERCENT_SCALE = 100.0

    def transform(self, feature_df):
        df = feature_df.copy()
        for col in self.PERCENT_FEATURES:
            if col not in df.columns:
                raise RuntimeError(f"Saknad procentfeature: {col}")
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col] * self.MODEL_PERCENT_SCALE
        return df

    def validate(self, raw_df, scaled_df):
        errors = []
        for col in self.PERCENT_FEATURES:
            if col not in raw_df.columns:
                errors.append(f"{col}: saknas i rådata")
                continue
            if col not in scaled_df.columns:
                errors.append(f"{col}: saknas efter scaling")
                continue
            expected = pd.to_numeric(raw_df[col], errors="coerce") * 100.0
            actual = pd.to_numeric(scaled_df[col], errors="coerce")
            if not np.allclose(expected.fillna(0), actual.fillna(0)):
                errors.append(f"{col}: fel scaling")

        return {
            "version": self.VERSION,
            "rows": len(scaled_df),
            "percent_features": len(self.PERCENT_FEATURES),
            "errors": errors,
            "status": "OK" if not errors else "FAIL",
        }

"""PHOENIX 15 — LOCKED REAL SCORE → PROBABILITY → RANK ENGINE.

Production guardrail:
- Uses only _phoenix_raw_score as the ranking source.
- Builds probability with per-race softmax from that same score.
- Builds Phoenix rank from that same score.
- Never falls back to model_rank or existing win_probability.
- Does not use result/facit columns to construct predictions.
- Fails fast on degenerate/invalid score or probability output.

Master/model data remains READ ONLY; this module only creates prediction outputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SCORE_COL = "_phoenix_raw_score"
PROB_COL = "phoenix_probability"
RANK_COL = "phoenix_rank"


class PhoenixRealScoreLockError(RuntimeError):
    """Raised when the locked Phoenix score/rank contract is violated."""


def _softmax(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce").astype(float)
    if not np.isfinite(x).all():
        raise PhoenixRealScoreLockError(
            "Invalid raw model score encountered."
        )

    z = x - np.max(x)
    e = np.exp(z)
    total = e.sum()

    if not np.isfinite(total) or total <= 0:
        raise PhoenixRealScoreLockError(
            "Softmax normalization failed."
        )

    return pd.Series(e / total, index=values.index)


def build_locked_real_score_rank(
    source: pd.DataFrame,
    race_col: str | None = None,
) -> pd.DataFrame:
    """Create the locked Phoenix probability/rank output.

    The source must already contain the verified raw model score.
    No fallback source is permitted.
    """

    if not isinstance(source, pd.DataFrame):
        raise PhoenixRealScoreLockError("Source must be a pandas DataFrame.")

    df = source.copy(deep=True)

    if race_col is None:
        if "race_id" in df.columns:
            race_col = "race_id"
        elif "race_number" in df.columns:
            race_col = "race_number"
        else:
            raise PhoenixRealScoreLockError(
                "No race_id or race_number available."
            )

    if SCORE_COL not in df.columns:
        raise PhoenixRealScoreLockError(
            f"{SCORE_COL} is missing. "
            "No model_rank/win_probability fallback is allowed."
        )

    if "start_number" not in df.columns:
        raise PhoenixRealScoreLockError("start_number is missing.")

    raw = pd.to_numeric(df[SCORE_COL], errors="coerce")

    if raw.isna().any() or not np.isfinite(raw).all():
        raise PhoenixRealScoreLockError(
            "Raw model score contains NaN or non-finite values."
        )

    if raw.nunique() < 2:
        raise PhoenixRealScoreLockError(
            "Raw model score is degenerate."
        )

    df[PROB_COL] = (
        df.groupby(race_col, sort=False)[SCORE_COL]
        .transform(_softmax)
    )

    df[RANK_COL] = (
        df.groupby(race_col)[SCORE_COL]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    df = df.sort_values(
        [race_col, RANK_COL, "start_number"]
    ).reset_index(drop=True)

    prob_sums = df.groupby(race_col)[PROB_COL].sum()
    rank1 = df.groupby(race_col)[RANK_COL].apply(
        lambda x: int((x == 1).sum())
    )

    checks = {
        "score_valid": bool(np.isfinite(raw).all()),
        "score_non_degenerate": bool(raw.nunique() >= 2),
        "probability_valid": bool(
            np.isfinite(df[PROB_COL]).all()
        ),
        "probability_non_degenerate": bool(
            df[PROB_COL].nunique() >= 2
        ),
        "probability_normalized": bool(
            np.allclose(prob_sums.to_numpy(), 1.0, atol=1e-10)
        ),
        "exactly_one_rank1": bool((rank1 == 1).all()),
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise PhoenixRealScoreLockError(
            "PHOENIX LOCK FAIL: " + ", ".join(failed)
        )

    # Explicitly mark the contract so downstream code can verify it.
    df.attrs["phoenix_real_score_locked"] = True
    df.attrs["phoenix_score_source"] = SCORE_COL
    df.attrs["phoenix_probability_source"] = SCORE_COL
    df.attrs["phoenix_rank_source"] = SCORE_COL
    df.attrs["phoenix_master_read_only"] = True
    df.attrs["phoenix_no_result_leakage"] = True

    return df


def verify_locked_output(
    locked_df: pd.DataFrame,
    race_col: str | None = None,
) -> dict[str, object]:
    """Fail-fast verification for an already-built locked output."""

    if race_col is None:
        if "race_id" in locked_df.columns:
            race_col = "race_id"
        elif "race_number" in locked_df.columns:
            race_col = "race_number"
        else:
            raise PhoenixRealScoreLockError(
                "No race_id or race_number available."
            )

    required = {SCORE_COL, PROB_COL, RANK_COL, race_col}
    missing = required.difference(locked_df.columns)
    if missing:
        raise PhoenixRealScoreLockError(
            "Missing locked output columns: " + ", ".join(sorted(missing))
        )

    score = pd.to_numeric(locked_df[SCORE_COL], errors="coerce")
    prob = pd.to_numeric(locked_df[PROB_COL], errors="coerce")
    rank = pd.to_numeric(locked_df[RANK_COL], errors="coerce")

    if score.isna().any() or prob.isna().any() or rank.isna().any():
        raise PhoenixRealScoreLockError(
            "Locked output contains invalid numeric values."
        )

    if score.nunique() < 2:
        raise PhoenixRealScoreLockError(
            "Locked raw score is degenerate."
        )

    sums = locked_df.groupby(race_col)[PROB_COL].sum()
    rank1 = locked_df.groupby(race_col)[RANK_COL].apply(
        lambda x: int((x == 1).sum())
    )

    if not np.allclose(sums.to_numpy(), 1.0, atol=1e-10):
        raise PhoenixRealScoreLockError(
            "Probability is not normalized to 1.0 per race."
        )

    if not (rank1 == 1).all():
        raise PhoenixRealScoreLockError(
            "Expected exactly one Phoenix Rank 1 per race."
        )

    return {
        "locked": True,
        "rows": int(len(locked_df)),
        "races": int(locked_df[race_col].nunique()),
        "unique_raw_scores": int(score.nunique()),
        "unique_probabilities": int(prob.nunique()),
        "min_probability": float(prob.min()),
        "max_probability": float(prob.max()),
        "rank1_per_race": int((rank1 == 1).sum()),
    }

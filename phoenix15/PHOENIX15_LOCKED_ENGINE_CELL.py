# PHOENIX 15 — LOCKED REAL SCORE/RANK — COLAB INTEGRATION CELL
# Production cell: run AFTER the existing Phoenix model prediction cell.
# This cell imports the locked engine directly from GitHub, so it does not
# depend on a copied/old Colab version.
#
# Contract:
#   model output with _phoenix_raw_score
#       -> locked softmax probability per race
#       -> Phoenix rank from the SAME raw score
#       -> fail-fast verification
#
# Forbidden:
#   model_rank fallback
#   old/degenerate win_probability fallback
#   results/facit for prediction construction
#
# Master/model files are READ ONLY.

import sys
import importlib.util
from urllib.request import urlopen

LOCKED_URL = (
    "https://raw.githubusercontent.com/Travkungen/Travsystem/"
    "main/phoenix15/phoenix15_locked_real_score_rank_v1.py"
)

_LOCKED_LOCAL = "/content/phoenix15_locked_real_score_rank_v1.py"

with urlopen(LOCKED_URL, timeout=30) as _r:
    _code = _r.read().decode("utf-8")

with open(_LOCKED_LOCAL, "w", encoding="utf-8") as _f:
    _f.write(_code)

_spec = importlib.util.spec_from_file_location(
    "phoenix15_locked_real_score_rank_v1",
    _LOCKED_LOCAL,
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

build_locked_real_score_rank = _mod.build_locked_real_score_rank
verify_locked_output = _mod.verify_locked_output
PhoenixRealScoreLockError = _mod.PhoenixRealScoreLockError

# Locate the current prediction dataframe. ONLY dataframes containing the
# verified raw score are eligible. No fallback to model_rank/win_probability.
_candidates = []
for _name, _obj in list(globals().items()):
    if hasattr(_obj, "columns") and hasattr(_obj, "shape"):
        try:
            if "_phoenix_raw_score" in _obj.columns:
                _c = _obj.copy(deep=True)
                _c["_phoenix_source_name"] = _name
                _c["_phoenix_candidate_score"] = (
                    _c["_phoenix_raw_score"].nunique()
                )
                _c["_phoenix_candidate_rows"] = len(_c)
                _c["_phoenix_candidate_score"] = int(
                    _c["_phoenix_candidate_score"].iloc[0]
                )
                _c["_phoenix_candidate_rows"] = int(
                    _c["_phoenix_candidate_rows"].iloc[0]
                )
                _candidates.append((_name, _obj))
        except Exception:
            pass

if not _candidates:
    raise PhoenixRealScoreLockError(
        "LOCK FAIL: No dataframe with _phoenix_raw_score found. "
        "Prediction cannot continue."
    )

# Prefer the known live prediction object when available; otherwise require
# the best raw-score candidate. Never use model_rank or old probability.
_preferred = [
    "phoenix_predictions_real",
    "phoenix_predictions_fixed",
    "predictions",
    "scored_fixed",
]
_source_name, _source_df = next(
    (
        (n, o) for n, o in _candidates
        if n in _preferred
    ),
    _candidates[0],
)

if _source_df["_phoenix_raw_score"].nunique() < 2:
    raise PhoenixRealScoreLockError(
        "LOCK FAIL: raw model score is degenerate."
    )

phoenix_predictions_real = build_locked_real_score_rank(_source_df)
phoenix_rank_real = phoenix_predictions_real.copy(deep=True)

# Permanent verifier: all downstream rank/probability values must come from
# the same raw score and probabilities must sum to 1 within every race.
_lock_report = verify_locked_output(phoenix_rank_real)

# Remove helper columns from the source if they leaked into the output.
for _col in [
    "_phoenix_source_name",
    "_phoenix_candidate_score",
    "_phoenix_candidate_rows",
]:
    if _col in phoenix_rank_real.columns:
        phoenix_rank_real = phoenix_rank_real.drop(columns=[_col])

# Runtime aliases used by the Phoenix pipeline.
phoenix_predictions_fixed = phoenix_predictions_real.copy(deep=True)
ranking = phoenix_rank_real.copy(deep=True)
rank_df = phoenix_rank_real.copy(deep=True)

print("=" * 70)
print("PHOENIX 15 — LOCKED ENGINE INTEGRATED")
print("=" * 70)
print("Source:", _source_name)
print("Rows:", _lock_report["rows"])
print("Races:", _lock_report["races"])
print("Unique raw scores:", _lock_report["unique_raw_scores"])
print(
    "Probability range:",
    f'{_lock_report["min_probability"]:.8f}',
    "->",
    f'{_lock_report["max_probability"]:.8f}',
)
print("Rank 1 per race:", _lock_report["rank1_per_race"])
print("Score source: _phoenix_raw_score")
print("Probability: per-race softmax(raw score)")
print("Rank: same raw score")
print("model_rank fallback: FORBIDDEN")
print("old win_probability fallback: FORBIDDEN")
print("results/facit leakage: FORBIDDEN")
print("Master: READ ONLY")
print("=" * 70)
print("✅ LOCKED REAL SCORE/RANK ENGINE ACTIVE")
print("=" * 70)

# Make the contract explicit for later cells.
PHOENIX_LOCKED_ENGINE_ACTIVE = True
PHOENIX_LOCKED_SCORE_COLUMN = "_phoenix_raw_score"
PHOENIX_LOCKED_PROBABILITY_COLUMN = "phoenix_probability"
PHOENIX_LOCKED_RANK_COLUMN = "phoenix_rank"

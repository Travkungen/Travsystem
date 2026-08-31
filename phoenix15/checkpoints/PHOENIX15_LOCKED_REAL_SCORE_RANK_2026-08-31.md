# PHOENIX 15 — LOCKED REAL SCORE/RANK CHECKPOINT

Date: 2026-08-31

## Production decision

Phoenix 15 now uses the verified raw model score:

`_phoenix_raw_score`

The production prediction chain is:

**raw model score → race-normalized softmax probability → Phoenix rank**

Probability and rank are derived from the same raw score.

## Permanent guardrails

- `model_rank` is NOT a probability fallback.
- Existing/degenerate `win_probability` is NOT a probability fallback.
- Result/facit data must NOT be used to construct predictions.
- Raw score must be numeric, finite and non-degenerate.
- Probability must contain multiple unique values.
- Probability must sum to 1.0 within every race.
- Exactly one Phoenix Rank 1 must exist per race.
- The engine fails fast if any contract is violated.
- Master/model data remains READ ONLY.

## Verified live state

- Rows: 86
- Races: 8
- Unique raw scores: 13
- Unique probabilities: 62
- Probability range: 0.00000388 → 0.63269750
- Rank 1 per race: 8/8

## 2026-08-30 V85 facit check

- Phoenix #1: 2/8
- Top 3: 3/8
- Top 5: 7/8
- Top 7: 7/8

These results are a validation snapshot only. They are NOT used to create the score, probability or rank.

## Canonical implementation

`phoenix15/phoenix15_locked_real_score_rank_v1.py`

Runtime objects in Colab:

- `phoenix_predictions_real`
- `phoenix_rank_real`

The next development step is multi-day historical backtesting of this locked engine before changing any model features.

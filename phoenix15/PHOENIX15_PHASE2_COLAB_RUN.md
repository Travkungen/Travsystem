# Phase 2 — minimal Colab run

The historical backtest is intentionally one command after the repository and
Google Drive snapshot directory are mounted.

## 1. Mount/read the saved snapshots

Point INPUT_DIR at the existing Phoenix 15 historical snapshot directory.
Do not copy or mutate the frozen model/database.

## 2. Run

    python phoenix15/PHOENIX15_PHASE2_BACKTEST.py \
      --input "$INPUT_DIR" \
      --output "$OUTPUT_DIR"

## 3. Verify

Expected permanent outputs:

- PHASE2_SUMMARY.json
- PHASE2_RACE_RESULTS.csv

If validation fails:

- PHASE2_VALIDATION_ERRORS.json

No historical result is fabricated when the snapshot contract is incomplete.

## 4. Acceptance review

Review:

- protected_hits >= original_hits
- degradations
- recoveries
- Rule 1/2/3 counts
- system_size_changed_cases == 0
- valid race count
- source files used

Do not merge PR #14 based on synthetic tests or Phase 1 diagnostics.
Only real historical OOS results can satisfy Phase 2.

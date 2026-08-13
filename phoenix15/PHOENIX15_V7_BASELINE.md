# Phoenix 15 — V7 Baseline

**Status:** FROZEN BASELINE / READ ONLY
**Date:** 2026-08-13

## Verified baseline

- New Colab notebook is the active development workspace.
- Cell 3: Phoenix source discovery verified.
- Cell 4: Phoenix source verified; `phoenix_feature_engine_v3` / `ai_training_data_v9` contain race-level Phoenix scores.
- Cell 5: Phoenix Motor V1.0 operational and produces `phoenix_race`.
- Cell 6: Phoenix level system operational with four levels and colors.
- Cell 7: V85 live motor operational and produces `phoenix_live`.
- V7.2 Odds Baseline Audit completed.

## Odds truth

- Historical source: `horse_results.odds_sort`
- Normal odds scale: `odds_sort / 10`
- `0`, `9998`, `9999`, and missing values are special/missing values and must not be treated as normal odds.
- Database remains READ ONLY during model development.

## Important architecture rule

The GitHub repository is the permanent code/baseline home. Colab is the execution and testing environment. Do not use Colab runtime state as the permanent source of truth.

## Next build

Build the reusable Phoenix Core V1 engine from the verified baseline, then add:

1. Market/odds layer
2. Race confidence and level logic
3. V85 coupon analysis as a separate module on top of the same core
4. Live V85 output
5. Backtest/evaluation layer

## Safety rule

Do not modify the frozen database or historical source data. New engine code must be READ ONLY against the database.

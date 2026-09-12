# PHOENIX 15 — CURRENT VERIFIED STATE

## Checkpoint

**Date:** 2026-09-12
**Purpose:** Stable handoff / rediscovery point for Phoenix 15 live work.

## Source of truth

Repository: `Travkungen/Travsystem`

Canonical downstream foundation: Foundation Auto v1.3 + Intelligent Engine V1.
Version lock: `phoenix15/canonical/PHOENIX15_VERSION_LOCK_2026-09-07.md`

## Protected state

- Master: READ ONLY
- Frozen: READ ONLY
- Model: READ ONLY
- SQLite database: READ ONLY during live analysis
- No retraining or model modification from live analysis

## Live runtime

Drive root:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live`

Canonical database:
`/content/drive/MyDrive/PhoenixTrav/phoenix_trav.db`

Verified database size:
`278716416` bytes

## Database verification

Canonical DB exists and was successfully opened read-only.

Key row counts:

- `horse_results`: 284,429
- `driver_features_v2`: 3,267
- `trainer_features_v2`: 3,509
- `horse_driver_features`: 21,949
- `phoenix_feature_engine_v1`: 231,082
- `phoenix_feature_engine_v2`: 231,082
- `race_results_v2`: 283,955
- `ai_training_data_v2`: 45,652

Warehouse metadata:
`Warehouse 1.0 FROZEN` — `2026-08-02 14:08:29.675058`

## Frozen live model

Preferred/current frozen live model for the modern Foundation Auto v1.3 chain:
`phoenix15_baseline_v2_1.pkl`

Model SHA256:
`249fa76aaad93e6d8b7336d3a031adc42949770f1539e7f9abfa6869fd4cdf71`

Model size:
`303744` bytes

Feature count:
`20`

The 20 features are the exact Foundation Auto v1.3 feature contract:

`starts, wins, win_percent, top3, top3_percent, last5_starts, last5_wins, last5_top3, last5_win_percent, driver_starts, driver_wins, driver_win_percent, driver_top3_percent, trainer_starts, trainer_wins, trainer_win_percent, trainer_top3_percent, hd_starts, hd_wins, hd_win_percent`

Model evaluation metadata:

- accuracy: 0.9246653522880565
- roc_auc: 0.9399919730183537
- top1_rate: 0.6743916570104287
- top3_rate: 0.936268829663963
- top5_rate: 0.9837775202780996
- train: 2024-09-01 through 2026-06-20
- test: 2026-06-21 through 2026-07-25

Older `phoenix15_baseline_v1.pkl` exists but is a 24-feature model and must not be silently substituted for the modern 20-feature Foundation chain.

## Verified live chain

ATG → race/date guard → scratches → driver/trainer/HD bridge → HorseHistory → FeatureBuild → exact Frozen 20 → 0–100 percentage conversion → Frozen decision_function raw score → locked Phoenix probability/rank → Market rank on identical active starters → 50/50 → fixed Top7.

`50/50 = (phoenix_rank + market_rank) / 2.0`

Top7 is the fixed base before downstream decision motors.

## Downstream rules

Intelligent Engine V1:

- Phoenix 60%
- Market 40%
- raw-value min-max normalization per race
- TOP7 before downstream motors
- Million V2 is the only validated graded skräll rule
- broader graded skräll levels and dynamic budget remain provisional

Black is kept as a separate rescue/difficulty diagnostic layer and is not part of the locked Phoenix base ranking.

## Current live target

V85 Hagmyren — 2026-09-12

V85 races: 5–12
First V85 start: 15:00

Live build status at checkpoint creation:

- Database verified: YES
- Frozen model verified: YES
- Live build started: NO
- ATG current-card fetch: NOT YET RUN IN THIS CHECKPOINT

## Rediscovery rule

When continuing Phoenix 15, first read this checkpoint together with:

1. `phoenix15/canonical/PHOENIX15_VERSION_LOCK_2026-09-07.md`
2. `phoenix15/PHOENIX15_MASTER_STATUS.md`
3. `phoenix15/PHOENIX15_FOUNDATION_AUTO_v1_3_CONTRACT.py`

Then verify the live Drive paths before executing the current-card pipeline.

Do not overwrite Master/Frozen/Model or change formulas during live analysis.

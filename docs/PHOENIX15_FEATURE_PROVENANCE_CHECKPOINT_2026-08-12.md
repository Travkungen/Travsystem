# Phoenix 15 — Feature Provenance Checkpoint

**Date:** 2026-08-12
**Status:** READ ONLY / investigation checkpoint

## Purpose
Preserve the verified findings from the Phoenix 15 investigation into the original production source of driver, trainer and horse-driver (HD) features.

## Verified database tables

- `horse_results` — 284,429 rows; contains point-in-time race participation with `driver_id`, `trainer_id`, placement and race date.
- `race_results_v2` — 283,955 rows; race/horse/person result representation.
- `horse_driver_features` — 21,949 rows; columns: `horse_id`, `driver_id`, `hd_starts`, `hd_wins`, `hd_win_percent`.
- `horse_driver_history` — columns: `race_id`, `horse_id`, `driver_id`, `hd_starts`, `hd_wins`, `hd_win_percent`.
- `driver_features`, `driver_features_new`, `driver_features_v2` — driver aggregates.
- `trainer_features`, `trainer_features_v2` — trainer aggregates.
- `ai_training_data_v4` through `v9` — historical training-data generations.
- `phoenix_feature_engine_v1`, `_v2`, `_v3` — historical Phoenix feature-engine outputs.

## Important provenance finding

For driver/trainer statistics, the current `feature_engine.py`, `feature_provider.py`, `historical_feature_engine.py`, `driver_engine.py` and `trainer_engine.py` inspected in the Phoenix 15 bootstrap are **not sufficient evidence of the original production provider** for the historical values found in `ai_training_data_v9`.

The generic `historical_feature_engine.py` currently shown calculates only horse-level aggregates from `history_df`; it does not reproduce the verified v9 driver/trainer values.

The current Phoenix 15 `PhoenixFeatureBuild` expects these model features:

- `driver_starts`
- `driver_wins`
- `driver_win_percent`
- `driver_top3_percent`
- `trainer_starts`
- `trainer_wins`
- `trainer_win_percent`
- `trainer_top3_percent`
- `hd_starts`
- `hd_wins`
- `hd_win_percent`

Missing model features are currently zero-filled by the feature builder, so zero-filled values must **not** be mistaken for the original provider output.

## Critical verified example

For `race_id=789625`, `horse_id=717005`, race date `2013-04-25`:

- `horse_results` shows driver/trainer `89209 Johansson Hanz`.
- `ai_training_data_v9` contains `driver_starts=158`, `driver_wins=4`, `driver_win_pct=2.53`, `trainer_starts=246`, `trainer_wins=5`, `trainer_win_pct=2.03`.
- A naive point-in-time calculation performed against the currently inspected raw data returned zero, so it does **not** reproduce the v9 values.
- `ai_training_data_v7/v8` for the same row had driver/trainer values `2 / 0 / 0.0` and `5 / 0 / 0.0`, while v9 later contains `158 / 4 / 2.53` and `246 / 5 / 2.03`.
- `driver_features_new` and `driver_features_v2` contain for driver 89209: `158 starts`, `4 wins`, `2.53 win_percent`, `68 top3`, `43.04 top3_percent`.
- `trainer_features_v2` contains for trainer 89209: `246 starts`, `5 wins`, `2.03 win_percent`, `106 top3`, `43.09 top3_percent`.
- The older `driver_features` / `trainer_features` tables contain much smaller values and therefore are not the source matching v9 for this example.

## HD bridge finding

`horse_driver_features` is a real populated feature table with 21,949 rows. Example rows include `horse_id`, `driver_id`, `hd_starts`, `hd_wins`, `hd_win_percent`.

`person_bridge` does **not** exist in the inspected database.

`horse_driver_history` exists and is a candidate historical representation, but its inspected first row for horse 717005 showed `hd_starts=0`, `hd_wins=0`, `hd_win_percent=0.0`, so its production-generation logic still needs provenance verification before being used as the definitive source.

## Code provenance finding

A direct search under:

- `/content/drive/MyDrive/PhoenixTrav/bootstrap`
- `/content/drive/MyDrive/PhoenixTrav/phoenix_15_live`

for the production code behind the populated v2 driver/trainer feature tables did not locate the original producer in the inspected files.

## Frozen rule for next session

**DO NOT**:

1. overwrite the verified feature tables;
2. rebuild `driver_*`, `trainer_*` or `hd_*` features from an unverified approximation;
3. treat the current generic engines as the historical v9 provider;
4. alter the database while provenance investigation is ongoing.

**NEXT STEP:** locate the original production code/query/process that generated `driver_features_v2`, `trainer_features_v2` and the corresponding HD features, then reproduce a small set of known v9 rows exactly before integrating anything into Phoenix 15.

## Phoenix 15 architecture context

The verified Phoenix 15 chain remains conceptually:

`ATG → Discovery → Extended Startlist → HorseHistory → Feature Build → Model → Ranking`

The existing NULL-safe `PhoenixFeatureBuild` is preserved. Its `race_id + horse_id` merge protection prevents unresolved/NULL horse IDs from causing cartesian expansion and must remain unchanged unless a separately verified improvement is made.

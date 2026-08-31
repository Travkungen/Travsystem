# Phoenix 15 — V4 Repair Verified Checkpoint

Date: 2026-08-31

## Status

Phoenix 15 V4 duplication root cause has been isolated and repaired deterministically.

## Verified results

- Original V4: 45,652 rows
- Original unique race+horse keys: 45,316
- Duplicate keys: 336
- Duplicate rows: 672
- Extra rows: 336
- Duplicate groups differed only in trainer statistics.
- Trainer source trainer_features contained duplicate trainer_id values.
- Canonical trainer_features_v2 contains one row per trainer_id.
- Repaired V4: 45,316 rows
- Repaired unique race+horse keys: 45,316
- Repaired duplicates: 0
- Missing keys after repair: 0
- Phoenix V1 inference: 45,316 rows, 0 duplicates, 0 null probabilities
- Phoenix V1 rank: 45,316 rows, 4,855 races, rank 1 present exactly once per race, max rank 15
- Final chain check: PASS

## Safety

- Master was not modified.
- Original V4 was not modified.
- Repaired table saved separately as ai_training_data_v4_repaired.
- Verified checkpoint saved in Colab/Drive at:
  /content/drive/MyDrive/PhoenixTrav/phoenix_15_live/v4_repair_verified

## Important repair detail

For duplicate race+horse rows, the only differing fields were:

- trainer_starts
- trainer_wins
- trainer_win_percent
- trainer_top3_percent

The deterministic repair uses the canonical trainer statistics from trainer_features_v2, producing one row per race_id + horse_id.

## Next step

Continue Phoenix 15 development from the verified repaired chain. Do not alter the frozen Master baseline unless explicitly intended and separately verified.

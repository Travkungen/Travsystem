# Phoenix 15 — V4 Repair Verified Checkpoint

Date: 2026-08-31

V4 duplication was isolated to trainer statistics.

Verified:
- Original V4: 45,652 rows
- Unique race+horse: 45,316
- Duplicate keys: 336
- Extra rows: 336
- All 336 duplicate groups differed only in trainer statistics
- trainer_features had duplicate trainer_id values
- trainer_features_v2 has one canonical row per trainer_id
- Repaired V4: 45,316 rows
- Repaired unique race+horse: 45,316
- Repaired duplicates: 0
- Missing keys: 0
- V1 inference: 45,316 rows, 0 duplicate, 0 null probabilities
- V1 rank: 45,316 rows, 4,855 races, rank 1 exactly once per race, max rank 15
- Final chain check: PASS

Safety:
- Master unchanged
- Original V4 unchanged
- Repair stored separately as ai_training_data_v4_repaired
- Colab/Drive checkpoint: /content/drive/MyDrive/PhoenixTrav/phoenix_15_live/v4_repair_verified

Next:
Continue from the repaired chain toward the live Phoenix ranking/system-selection output. Do not modify the frozen Master baseline.

# Phoenix 15 — Verified Chain Checkpoint

Date: 2026-08-14

## Frozen verified chain

1. Existing Åby V85 startlist loaded: 89 starters / 8 races / 25 live columns.
2. `PhoenixHorseHistory` produces 89 history rows and the required 9 horse-history features.
3. `PhoenixFeatureBuild` produces 36 output columns and all 20 model features with no missing model features.
4. Existing `HistGradientBoostingClassifier` model is loaded from `phoenix15_baseline_v2_1.pkl`.
5. Root cause of the near-constant live probabilities was verified: training percentage features use 0–100 scale while live Feature Build outputs 0–1.
6. A read-only scale test converting the 8 percentage features to 0–100 produced meaningful model probabilities: 89 predictions, 86 unique probabilities, min 0.0000653, max 0.845771, std 0.21507.
7. `PhoenixFeatureScaleAdapter v1.0` was verified on all 89 Åby starters with status OK.
8. Existing Ranking Engine validated the scaled model output: 89 rows, 8 races, 0 duplicate keys, 0 rank errors.
9. Phoenix Top 7 was generated for every race: 8 x 7 = 56 horses.

## Model feature set — 20

### Horse history — 9
- starts
- wins
- win_percent
- top3
- top3_percent
- last5_starts
- last5_wins
- last5_top3
- last5_win_percent

### Driver — 4
- driver_starts
- driver_wins
- driver_win_percent
- driver_top3_percent

### Trainer — 4
- trainer_starts
- trainer_wins
- trainer_win_percent
- trainer_top3_percent

### Horse-driver — 3
- hd_starts
- hd_wins
- hd_win_percent

## Important constraints

- No database changes were made.
- No model retraining or model-file changes were made.
- The existing Feature Build remains the source feature layer.
- The scale adapter is a separate compatibility layer for the existing model's 0–100 training scale.
- Do not restart the Phoenix project from an old Colab checkpoint. Continue from this verified chain.
- Top 7 is the current Phoenix output standard. Reduction comes later.

## Åby V85 Top 7 — start numbers only

1: 11, 6, 2, 4, 14, 1, 5
2: 5, 3, 6, 7, 4, 2, 1
3: 2, 3, 12, 4, 11, 8, 9
4: 9, 1, 6, 10, 2, 12, 3
5: 6, 9, 8, 2, 10, 5, 12
6: 3, 1, 2, 5, 9, 8, 10
7: 8, 6, 5, 1, 7, 3, 9
8: 9, 10, 7, 4, 2, 11, 1

Note: these are the 8 displayed Åby race groups in the current session, renumbered 1–8 for the user's requested compact format. Original race numbers are 5–12.

## Next intended work

1. Import/save the actual Åby result/facit.
2. Compare Phoenix Top 7 against the winners and finishing positions.
3. Save the result into the Phoenix dataset.
4. Analyze misses before adding new features.
5. Build the future automatic chain around the verified components: import → history → features → scale adapter → model → ranking → Top 7.

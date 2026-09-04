# PHOENIX TRAV 15 — FINAL CHECKPOINT

Date: 2026-09-04
Status: FINAL CANDIDATE — CHECKPOINT COMPLETE
Repository: Travkungen/Travsystem

## Purpose
This document records the Phoenix Trav 15 state completed on 2026-09-04. It is the GitHub recovery/reference checkpoint and must not be interpreted as permission to modify the frozen Phoenix Master or Phoenix model.

## HARD SAFETY
- Phoenix Master: READ ONLY
- Phoenix model: READ ONLY
- Phoenix rank: READ ONLY
- No model retraining in live/product generation
- No unverified reduction engine activated
- Historical winner is used only as evaluation/facit, never as a live feature
- Existing frozen baselines must be preserved

## VERIFIED X105
Permanent Colab/Drive artifact:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/FINAL_PHOENIX15/PHOENIX15_X105_VERIFIED_FINAL.parquet`

Verified:
- Rows: 40,349
- Races: 4,210
- Rounds: 399
- Winners: 3,699
- Valid odds: 40,349

Original permanent verified X105 artifact also exists at:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/analysis_checkpoints/millionsecret_v2/MILLIONSECRETFORMEL_X105_VERIFIED.parquet`

## MILLIONSECRETFORMEL
Status: CANDIDATE — NOT MODEL-ACTIVE

Verified base:
- M1 + M3
- Race coverage: 82.30%
- OOS mean: 82.30%
- OOS min: 80.88%
- OOS max: 85.39%
- 4,210 races
- 399 rounds

Permanent Drive checkpoint:
`analysis_checkpoints/millionsecret_v2/MILLIONSECRETFORMEL_V2_CHECKPOINT.json`

## BEST VERIFIED RANK BASE — V18
Population: FULL X105
Method: `best_rank = min(Phoenix rank, Market rank)`
Selected level: N7

Historical result:
- Race coverage: 84.75%
- Complete-round survival: 10.28%
- 7 horses/race

Important: V18 is the best verified rank-based candidate found in this development phase. It is NOT a claim that a fixed 7-horse production coupon is the final budget reducer. The budget reduction engine remains unactivated.

## RADMOTOR TEST HISTORY
The following reduction/allocation variants were tested and rejected:
- V12 — winner survival: 63.62% / 70.34% / 76.73% / 79.94% at 100 / 400 / 2,000 / 4,000 SEK
- V13 — winner survival: 46.63% / 51.28% / 55.34% / 56.94%
- V15 — race coverage: 50.16% / 54.31% / 59.45% / 61.21%; round survival: 0 / 0.25 / 0.25 / 0.50%
- V16 — race coverage: 68.53%; complete-round survival: 2.51%
- V17 — M1+M3 rank base; race coverage plateaued around 67.7%; rejected
- V19 — race coverage: 50.16% / 54.31% / 59.45% / 61.21%; round survival: 0 / 0.25 / 0.25 / 0.50%

Conclusion: these heuristic/greedy reduction approaches are NOT production-active. Do not tune the Phoenix model to compensate for them.

## KEY VERIFIED HISTORICAL CURVES
Earlier verified rank concentration on the development population showed strong diminishing returns. One verified test reported approximately:
- Rank 1: 49.51%
- Rank 2: 68.43%
- Rank 3: 77.93%
- Rank 4: 80.82%
- Rank 5: 81.94%
- Rank 6: 82.27%
- Rank 7: 82.27%

A separate V18 full-X105 check produced:
- N1: 36.20% race / 0.00% round
- N2: 55.01% / 0.75%
- N3: 67.67% / 1.25%
- N4: 75.63% / 3.01%
- N5: 80.07% / 5.26%
- N6: 82.71% / 8.27%
- N7: 84.44% / 10.28%

A later comparison reported V18 race coverage as 84.75%; preserve the latest reported checkpoint value as the final comparison figure.

## LIVE PIPELINE / ODDS
Verified architecture:
ATG discovery -> startlist -> ATG odds/market -> locked Phoenix score/rank -> MillionSecretFormel overlay -> Game Engine -> candidate pool -> budget/rad output -> checkpoint.

Verified 2026-09-04 odds integration:
- Odds engine: `phoenix15/phoenix15_odds_engine_v1.py`
- Orchestrator updated for odds
- Direct ATG winner-game endpoint verified
- Full orchestrator test: 65 races / 634 starters; odds rows and valid odds were successfully produced
- Phoenix Master/model remained READ ONLY

Important Drive checkpoints from the day:
- `PHOENIX15_RUNTIME_CHECKPOINTS/checkpoint_20260904_083431`
- `PHOENIX15_RUNTIME_CHECKPOINTS/checkpoint_20260904_092635_AUTO_ODDS_FINAL`
- `PHOENIX15_RUNTIME_CHECKPOINTS/checkpoint_20260904_093844_ORCHESTRATOR_ODDS`

## CURRENT FINAL DRIVE PACKAGE
Directory:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/FINAL_PHOENIX15/`

Files:
- `PHOENIX15_FINAL_CONFIG.json`
- `PHOENIX15_FINAL_STATUS.json`
- `PHOENIX15_X105_VERIFIED_FINAL.parquet`
- `PHOENIX15_X105_FINAL_SNAPSHOT.json`
- `PHOENIX15_FINAL_MANIFEST.json`

The Colab final manifest verified all five files exist.

## RECOVERY / HISTORICAL DATABASE
Correct historical DB:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/recovery_checkpoints/PHOENIX15_COLAB_TRANSITION_20260810_211119/database/phoenix_trav.db`

Verified historical DB characteristics:
- 50 tables
- 284,429 horse_results rows
- 9,831 unique horses

Do NOT use the known empty/wrong database:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/phoenix15.db`

## IMPORTANT EXISTING PHOENIX 15 GITHUB ARTIFACTS
Existing GitHub Phoenix 15 files include:
- `phoenix15/PHOENIX15_COLAB_START.py`
- `phoenix15/PHOENIX15_LOCKED_ENGINE_CELL.py`
- `phoenix15/PHOENIX15_ATG_ODDS_COMBINED_CELL.py`
- `phoenix15/PHOENIX15_MARKET_DATA_CONTRACT.md`
- `phoenix15/PHOENIX15_MARKET_DATA_V1_FROZEN.md`
- `phoenix15/PHOENIX15_PLAYMOTOR_FINAL.py`
- `phoenix15/PHOENIX15_MASTER_STATUS.md`
- `phoenix15/PHOENIX15_COLAB_MINIMAL_WORKFLOW.md`
- `phoenix15/PHOENIX15_10H_PIPELINE.md`
- `phoenix15/PHOENIX15_FINAL_CHECKPOINT_2026-08-18.md`
- `phoenix15/PHOENIX15_PROTECTION_LAYER_CHECKPOINT_2026-08-27.md`
- `phoenix15/PHOENIX15_ATG_HORSE_API_CHECKPOINT_2026-08-14.md`

This 2026-09-04 checkpoint is the current development/recovery reference and should be read together with the older frozen checkpoints above.

## NEXT SESSION RULE
Do not rebuild today's work. Start from the final Drive package and this GitHub checkpoint. Any future reduction improvement must be separately validated and must not modify Phoenix Master/model without explicit authorization and clean unseen validation.

# PHOENIX 15 — MINIMAL COLAB WORKFLOW

## Goal
The Phoenix 15 live workflow must be reproducible with a small number of cells. Colab is runtime only; GitHub/Drive are the source of truth.

## Cell 1 — START
Run the existing `PHOENIX15_COLAB_START.py` startup. It mounts Drive, verifies the live environment, loads the existing Horse History, Feature Build, Model Engine and Ranking Engine, and confirms the 20-feature model contract.

## Cell 2 — LIVE ANALYSIS
Run the approved live chain:
1. discover/import today's race card into the live read-only analysis layer
2. build horse history/features
3. run the frozen Phoenix V3 model
4. produce Phoenix probabilities/ranks
5. merge market rank and odds
6. remove withdrawn/non-playable starters
7. classify SPIK/A/B/SKRÄLL/RESERV
8. calculate play profiles: SAFE/BALANS/OFFENSIV
9. call `PHOENIX15_PLAYMOTOR_FINAL.py` with `run_playmotor(race_info, profiles)`

Expected outputs: exact 32 / 96 / 192 rows and the corresponding coupon fields.

## Cell 3 — RESULT/FACIT
After the round, import the official results into the existing results/experience workflow. Compare:
- Phoenix rank vs winner
- market rank vs winner
- spik decisions
- A/B/SKRÄLL hits
- SAFE/BALANS/OFFENSIV 6/6, 5/6, etc.
- submitted coupon coverage
- payout/value when available

The result must be stored as experience/facit. Do not retrain or overwrite the frozen V3 model after one round.

## READ-ONLY RULE
The play layer must not write SQLite and must not write model files. Historical results are stored by the approved result/facit pipeline only.

## Important
The final play/reduction layer is a decision layer above the Phoenix model. It is not evidence that the reduction is statistically optimal yet. It must be validated over accumulated rounds before changing weights or model logic.

## Core principle
**Phoenix ranks. History teaches. Reduction allocates the budget. Results update the experience bank.**

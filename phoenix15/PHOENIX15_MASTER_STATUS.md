# PHOENIX 15 — MASTER STATUS

**Status:** ACTIVE / PLAY LAYER FROZEN FOR VALIDATION
**Last updated:** 2026-08-18

## Purpose
Phoenix 15 is a historical-learning and live-analysis system for Swedish trotting. V85/V86/V64 rounds are recurring experience data. The Phoenix model/ranking must not be rebuilt after every round.

## Source of truth
- GitHub repository: `Travkungen/Travsystem`
- Colab: runtime only; must be reproducible from GitHub/Drive
- Phoenix 15 live environment: `/content/drive/MyDrive/PhoenixTrav/phoenix_15_live`
- Database: `/content/drive/MyDrive/PhoenixTrav/phoenix_trav.db`

## VERIFIED / FROZEN
- Phoenix 14 is the frozen reference baseline.
- Phoenix 15 verified chain: startlist → Horse History → Feature Build → Scale Adapter → Model → Ranking → Top 7.
- 20 model features are currently verified.
- Training/live percentage-scale mismatch was identified; Scale Adapter v1 was verified read-only.
- Existing Ranking Engine produced valid ranks and Phoenix Top 7.
- Current Phoenix output standard is Top 7.
- Existing model files and database are NOT to be modified during analysis experiments.
- Phoenix V3 live probabilities were verified on 2026-08-18 and used read-only for the play layer.

## PLAY / REDUCTION LAYER — 2026-08-18
The play layer is now frozen for validation above the Phoenix V3 model.

Verified components:
- market rank + odds
- withdrawn/non-playable filtering
- SPIK / A / B / SKRÄLL / RESERV signals
- spike strength and maturity
- SAFE / BALANS / OFFENSIV profiles
- budget-controlled row generation
- final reusable reduction/play module
- exact 32 / 96 / 192 row outputs
- row diversification
- Phoenix probability + market + value + signal scoring

Reusable module:
`phoenix15/PHOENIX15_PLAYMOTOR_FINAL.py`

Minimal workflow:
`phoenix15/PHOENIX15_COLAB_MINIMAL_WORKFLOW.md`

Checkpoint:
`phoenix15/PHOENIX15_FINAL_CHECKPOINT_2026-08-18.md`

## IMPORTANT VALIDATION STATUS
The play/reduction architecture is frozen for testing, but statistical optimality is NOT yet proven. Do not change scoring weights or the Phoenix V3 model because of one V64/V85/V86 result. Accumulate official result/facit rounds first.

## HISTORICAL EVIDENCE ALREADY PRODUCED
- Large historical Phoenix analysis: 231,082 Phoenix rows; 198,625 matched starters; 45,428 matched races.
- Within Phoenix Top 7, winner distribution:
  - Rank 1: 46.45%
  - Rank 2: 22.90%
  - Rank 3: 12.94%
  - Rank 4: 7.77%
  - Rank 5: 5.29%
  - Rank 6: 2.81%
  - Rank 7: 1.84%
- Phoenix Top 3 captured 82.29% of winners that occurred inside Phoenix Top 7 in that experiment.
- Historical valid-odds winner analysis: 28,458 races.
- Spelodds rank winner distribution: ranks 1–3 = 89.41% of winners; ranks 4–6 = 8.65%; rank 7 = 0.89%; rank 8+ = 1.05%.
- Phoenix ranks 4–7 still contain meaningful winners and must not simply be discarded.

## CURRENT ARCHITECTURE GOAL
1. Automatic import of the current V85/V86/V64 races.
2. Automatic market/odds data ingestion.
3. Run all approved Phoenix engines.
4. Produce Phoenix Top 7 and probabilities.
5. Run signal/spike/play profile layer.
6. Produce SAFE / BALANS / OFFENSIV systems with exact budget targets.
7. Save the submitted system and its snapshot.
8. Import official results after the round.
9. Automatically compare predictions/ranks/market/value/reduction against the result.
10. Store the facit in the historical experience bank.
11. Use accumulated history to improve engines only after sufficient evidence.

## MINIMAL COLAB TARGET
A future clean Colab session should use only a small number of stable cells:
1. START — mount Drive and load verified modules.
2. LIVE ANALYSIS — current card → Phoenix V3 → market → signals → profiles → final play motor.
3. RESULT/FACIT — official result import → comparison → experience storage.

The detailed workflow is in `PHOENIX15_COLAB_MINIMAL_WORKFLOW.md`.

## IMPORTANT LESSONS / DO NOT REPEAT
- Do not mix `race_id` and `atg_race_id` without an explicit bridge.
- In `horse_results`, market rank is `odds_sort`; there is no `odds` column.
- Do not rely on a live Colab SQLite connection surviving runtime resets.
- Do not use stale DataFrames/variables from earlier cells.
- Handle NaN Phoenix scores explicitly before integer rank conversion.
- Do not modify the database or model while running read-only research.
- Do not redesign Phoenix because of a single round.
- Do not restart from an old Colab checkpoint when a verified GitHub baseline exists.

## WORKING PRINCIPLE
**Phoenix ranks. History teaches. Reduction allocates the budget. Results update the experience bank.**

A pause, Colab reset, or new conversation must never require rebuilding Phoenix from scratch.

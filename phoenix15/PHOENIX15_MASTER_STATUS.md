# PHOENIX 15 — MASTER STATUS

**Status:** ACTIVE / CONTINUE FROM VERIFIED BASELINE
**Last updated:** 2026-08-15

## Purpose
Phoenix 15 is a historical-learning and live-analysis system for Swedish trotting. V85/V86 rounds are used as recurring experience data. The Phoenix model/ranking must not be rebuilt after every round.

## Source of truth
- GitHub repository: `Travkungen/Travsystem`
- Colab: runtime only; must be reproducible from GitHub/Drive
- Phoenix 15 live environment: `/content/drive/MyDrive/PhoenixTrav/phoenix_15_live`
- Database: `/content/drive/MyDrive/PhoenixTrav/phoenix_trav.db`

## VERIFIED / FROZEN
- Phoenix 14 is the frozen reference baseline.
- Phoenix 15 verified chain: startlist → Horse History → Feature Build → Scale Adapter → Model → Ranking → Top 7.
- Verified on 89 starters / 8 races on 2026-08-14.
- 20 model features are currently verified.
- Training/live percentage-scale mismatch was identified; Scale Adapter v1 was verified read-only.
- Existing Ranking Engine produced valid ranks and Phoenix Top 7 for all 8 races.
- Current Phoenix output standard is Top 7.
- Existing model files and database are NOT to be modified during analysis experiments.

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
- Therefore Phoenix Top 3 captured 82.29% of winners that occurred inside Phoenix Top 7 in this experiment.
- Historical valid-odds winner analysis: 28,458 races.
- Spelodds rank winner distribution: ranks 1–3 = 89.41% of winners; ranks 4–6 = 8.65%; rank 7 = 0.89%; rank 8+ = 1.05%.
- Historical Phoenix Top 7 × spelodds analysis has been completed and shows that Phoenix ranks 4–7 still contain meaningful winners; they must not simply be discarded.
- Previous V85/V86 rounds are to be stored as experience/facit data, not used as justification for rebuilding the model after one round.

## CURRENT ARCHITECTURE GOAL
1. Automatic import of the current V85/V86 races.
2. Automatic market/odds data ingestion.
3. Run all approved Phoenix engines.
4. Produce Phoenix Top 7.
5. Run reduction using several system packages.
6. Save the submitted system and its snapshot.
7. Import official results after the round.
8. Automatically compare predictions/ranks/market/value/reduction against the result.
9. Store the facit in the historical experience bank.
10. Use accumulated history to improve engines only after sufficient evidence.

## NEXT DEVELOPMENT PRIORITY
### A. Stabilize the workflow before changing model logic
Create a simple reproducible Colab startup and analysis chain. Avoid ad-hoc cells that depend on stale runtime variables.

### B. Build the historical decision/analysis layer
Use the existing ~250k historical races to test:
- Phoenix Top 1/2/3/5/7
- Safe-2
- Safe-3
- Phoenix × spelodds rank
- Phoenix × market/streck
- value horses
- track/ban analysis
- distance/start method/start position
- horse/driver/trainer and horse-driver effects
- later: reduction packages

### C. Do NOT rebuild the Phoenix feature/model baseline yet
New features must be tested one at a time against the frozen/verified baseline and accepted/rejected based on historical evidence.

## IMPORTANT LESSONS / DO NOT REPEAT
- Do not mix `race_id` and `atg_race_id` without an explicit bridge.
- In `horse_results`, market rank is `odds_sort`; there is no `odds` column.
- Do not rely on a live Colab SQLite connection surviving runtime resets.
- Do not use stale DataFrames/variables from earlier cells.
- Handle NaN Phoenix scores explicitly before integer rank conversion.
- Do not modify the database or model while running read-only research.
- Do not redesign Phoenix because of a single V85/V86 result.
- Do not restart from an old Colab checkpoint when a verified GitHub baseline exists.

## CURRENT OPEN WORK
- Make the Colab startup/analysis workflow reliable and simple.
- Complete the automatic live-round import → analysis → system → result/facit chain.
- Complete track/ban analysis.
- Build and validate Safe-2/Safe-3.
- Build value analysis.
- Build reduction packages only after the above are historically validated.

## WORKING PRINCIPLE
**Phoenix ranks. History teaches. Reduction allocates the budget. Results update the experience bank.**

A pause, Colab reset, or new conversation must never require rebuilding Phoenix from scratch.

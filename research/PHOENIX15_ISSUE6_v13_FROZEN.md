# Phoenix 15 — ISSUE #6 v13 FROZEN CHECKPOINT

**Status:** FROZEN — READ ONLY research checkpoint  
**Date:** 2026-08-17

## v13 Marginal Contribution Walk-Forward
- DataFrame: `top7`
- Rows: 30,899
- Races: 4,855
- Winners: 4,055
- Five walk-forward blocks of 971 races each.

## Total marginal control
- Rule 1 only: 396 starters / 7 winners
- Rule 2 only: 811 starters / 8 winners
- Both rules: 3,764 starters / 13 winners

## Rule 1 only
- Mean reduction: 1.275%
- Min reduction: 0.907%
- Max reduction: 1.517%
- Mean winner loss: 0.173%
- Worst winner loss: 0.504%
- Mean efficiency: 6.401
- Block variation: 0.609 pp

## Rule 2 only
- Mean reduction: 2.620%
- Min reduction: 2.265%
- Max reduction: 3.160%
- Mean winner loss: 0.197%
- Worst winner loss: 0.260%
- Mean efficiency: 14.523
- Block variation: 0.894 pp

## v13 Research Assessment
**Best marginal candidate: Rule 2 only**

- 811 extra starters
- 8 extra winners
- Mean efficiency: 14.52
- Maximum winner loss: 0.260%
- Block variation: 0.894 pp
- Stable across all five blocks

## Combined candidate context
Previous v11 rolling multi-holdout identified `1+2` as the robust combined candidate:
- Mean reduction: 16.073%
- Min reduction: 15.338%
- Max reduction: 17.393%
- Mean winner loss: 0.686%
- Worst winner loss: 1.094%
- Mean efficiency: 47.52
- Block variation: 2.056 pp
- Max removed per race: 2

## Freeze Rule
This is a **research-only READ ONLY checkpoint**.

**No production table changed. No model changed. No production data changed.**

Next step: load Wednesday's V86 as a separate new dataset and evaluate Phoenix Top 7 plus the candidate reduction rules without modifying this frozen checkpoint.

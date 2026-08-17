# PHOENIX 15 — ISSUE #7 TOP7 MASTER CHECKPOINT

**Date:** 2026-08-17  
**Status:** VERIFIED / READ ONLY  
**Scope:** Historical TOP7 reconstruction and rank/tie forensics

## 1. Master TOP7 reference — LOCKED

The original historical TOP7 population has been identified and exactly reproduced from:

- **Master source:** `ai_training_data`
- **Rows:** 45,316
- **Races:** 4,855
- **Horses:** 9,655
- **Race+horse duplicates:** 0
- **TOP7 rows:** 30,899
- **Historical winners:** 4,172
- **Winners inside TOP7:** 4,109
- **TOP7 winner coverage:** 98.490%

`training_data` independently reproduces the same 30,899 TOP7 rows and 4,109 winners.

`ai_training_data_v6` also produces 30,899 TOP7 rows but only 4,055 winners inside TOP7, so it is **not** the master reference for exact historical TOP7 reproduction.

## 2. Why Phoenix Feature Engine v3 did not match

`phoenix_feature_engine_v3` contains:

- 40,349 rows
- 4,210 races
- 9,211 horses
- 606 race+horse duplicate rows
- 40,046 unique race+horse rows
- reconstructed TOP7: 27,282 rows

Therefore v3 is based on a smaller/different historical population than the original TOP7 master.

The historical original TOP7 must **not** be reconstructed from v3.

## 3. Original TOP7 ranking definition used for validation

For the current forensic reconstruction, rows are ordered within each race by:

1. `phoenix_score` descending
2. `horse_id` ascending as deterministic tie-breaker for the reconstruction

TOP7 is rank <= 7.

The exact original source population is already verified as 30,899 rows, so tie-handling remains a forensic item rather than a reason to modify the master source.

## 4. Tie / rank forensics — v3.7h

READ ONLY test results:

- **Race+score tie groups:** 4,132
- **Starters participating in score ties:** 12,992
- **Races with a tie at the TOP7 cutoff:** 1,294
- **Races with both rank 7 and rank 8 available in the comparison:** 3,727
- **Rank 7 vs rank 8 exact score ties:** 986
- **Minimum rank7-rank8 score gap:** 0.00
- **Median score gap:** 1.71
- **Maximum score gap:** 25.33

Conclusion: Phoenix score ties are common and tie handling is material to exact ranking reproduction. However, the **master TOP7 population itself is already verified from `ai_training_data`** and must remain READ ONLY.

## 5. Frozen rules from this checkpoint

- Do **not** modify `ai_training_data`.
- Do **not** modify the Phoenix 15 database.
- Do **not** modify the frozen Feature Engine as part of this forensic step.
- Do **not** use `phoenix_feature_engine_v3` as the historical TOP7 reference.
- Treat `ai_training_data` as `PHOENIX15_ORIGINAL_TOP7_MASTER`.
- Historical reference remains 4,855 races / 45,316 starters / 30,899 TOP7 rows / 4,109 TOP7 winners / 98.490% coverage.

## 6. Next development phase

The next phase is **not yet a production Feature Engine change**.

First perform a READ ONLY inventory of approximately 40 candidate features already available in the Phoenix data. Candidate groups include:

- Horse performance: starts, wins, win %, top3 %, last5 win %, last5 top3 %, form
- Driver: starts, wins, win %, top3 %
- Trainer: starts, wins, win %, top3 %
- Horse-driver history: starts, wins, win %
- Race context: field size, race average Phoenix, race best Phoenix, Phoenix gap/relative measures
- Start context: start position, distance, start method
- Phoenix ranking: Phoenix Score, race rank, gap to best, gap to average and related relative measures
- Later: verified gallop-related features, once their provenance is established

After the inventory, build a separate **Feature Combination Engine** that can test combinations of these candidate features without changing the master data or production pipeline.

The intended research workflow is:

`~40 candidate features → automated combinations → historical backtest → ranking metrics → shortlist → out-of-sample validation`

The engine must avoid leakage and must not optimize only against the same historical sample used for final evaluation.

## 7. Current status

**ISSUE #7:** TOP7 source identification = SOLVED  
**Original TOP7 master:** LOCKED  
**Tie/rank forensics:** COMPLETED  
**Feature inventory:** NEXT  
**Feature Combination Engine:** PLANNED  
**Production changes:** NONE

---

**Checkpoint principle:** preserve the verified master first; experiment separately; promote changes only after independent validation.

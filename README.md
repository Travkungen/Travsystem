# Phoenix Trav 15

## FINAL PRODUCT CHECKPOINT — 2026-08-18

Final product stage: **FINAL FAST PRODUCT ENGINE v6**. Product/rad generation is READ ONLY: no training, model write, or SQLite write.

### Verified final product
- Phoenix 3000: exactly 3,000 unique rows / 3,000 SEK
- Phoenix Core: 1,080 rows
- Smart value expansion
- Maximum 3 external candidates per leg
- Only verified start numbers
- Tangen Tom #9 protected by Phoenix Core
- Fast generation suitable for practical Colab use

### Phoenix pools
- V64-1: [3,5,7]
- V64-2: [1,2,6]
- V64-3: [9]
- V64-4: [1,2,5,7,8]
- V64-5: [1,2,3,4,6,7,8,9]
- V64-6: [1,7,8]

### Final fast product pools
- V64-1: [1,2,3,4,5,7]
- V64-2: [1,2,6,7,9,12]
- V64-3: [6,8,9,14]
- V64-4: [1,2,3,4,5,6,7,8]
- V64-5: [1,2,3,4,5,6,7,8,9,10]
- V64-6: [1,5,7,8,10,12]

### Product layers
- SAFE: 32 SEK
- BALANS: 96 SEK
- MAX/Core: 1,080 SEK raw Phoenix-space product
- PHOENIX 3000: exactly 3,000 unique rows / 3,000 SEK
- Shares: 100%=3,000 SEK; 50%=1,500; 25%=750; 10%=300

### Few-cell requirement
The complete Phoenix chain must be runnable from a few Google Colab cells after runtime restart, using reusable bootstrap/modules rather than large copied notebook cells. Required chain: bootstrap -> live/startlist load -> Phoenix scoring -> value/market -> spike/value profile -> SAFE/BALANS/OFFENSIV -> fast rad engine -> final 3,000-row/andel layer -> export rows/coupon/share basis -> post-race result import and evaluation.

### Hard constraints
- No training during live product generation
- No model write
- No SQLite write from product engines
- Preserve frozen Phoenix baselines
- Verify start numbers before row generation
- Never claim the full 3,000 rows unless they have actually been exported/read

Phoenix 15 historical architecture and READ ONLY verification remain the reference baseline. Google Drive PhoenixTrav live environment/backups remain the primary Colab-side recovery location.

## PHOENIX 15 — CLEAN INTELLIGENCE CHECKPOINT — 2026-08-18

This checkpoint records the important leakage-clean reconstruction and out-of-sample validation completed on 2026-08-18. It is a frozen reference baseline and must not be overwritten by later optimization.

### Leakage audit
- Original `training_data` audit showed an impossible signal: winner was highest Phoenix Score in **100.00%** of 4,159 checked races.
- Therefore the old Phoenix score was treated as contaminated and **not approved for production weighting**.
- Clean historical reconstruction was then built from `horse_results`, using only information available before the current start.
- Current placement/winner is used only as historical facit/label, never as a score input.

### Clean historical rebuild
- Raw `horse_results`: **284,429 starts** available.
- Clean reconstructed dataset: **170,757 starts / 60,466 races / 29,134 winners**.
- Clean Phoenix 1.1 historical ranking:
  - Top 1: **49.08%**
  - Top 3: **82.94%**
  - Top 5: **95.63%**
  - Top 7: **99.39%**
- Starter without previous history: **663**.
- Maximum previous starts: **205**.
- Clean score uses shifted historical horse features only plus start position; current placement is not used in the score.

### Walk-forward validation
- Chronological walk-forward / out-of-sample testing was performed.
- Aggregate across **59,466 test races** from the walk-forward run:
  - Top 1: **46.25%**
  - Top 3: **74.09%**
  - Top 5: **81.90%**
  - Top 7: **83.76%**
- The purpose of this run was validation, not permission to change production parameters after seeing future results.

### Final clean holdout
- Final holdout was the most recent **20%**, completely untouched during parameter selection.
- Holdout: **12,094 races / 56,708 starts** before completeness filtering.
- Integrity check found 8,994 complete races with exactly one winner; 3,080 had zero winners and 20 had >1 winner, so final accuracy is reported only on complete races.
- Final clean holdout: **8,994 complete races / 8,994 winners**.
- Final holdout results:
  - Top 1: **34.82%**
  - Top 3: **69.70%**
  - Top 5: **89.73%**
  - Top 7: **98.25%**
- This is the key frozen, leakage-clean, out-of-sample benchmark.

### Intelligence benchmark
- A preliminary internal Phoenix Intelligence rating was set to **78/100**, explicitly not 100/100.
- 100/100 is a goal, not a claim. It requires sustained leakage-free performance, stability across periods/loppstyper/banor, strong Top 1/3/7 ranking, and new unseen validation without post-hoc tuning.
- No model should be declared 100/100 merely because Top 7 is high.

### Today's V64 live-style test
- The first attempt used the wrong historical table for current starters; this was corrected without changing the model.
- Current startlist source identified as `phoenix15_live_starts`.
- The available current dataset showed **98 starters / 8 races**, dated **2026-08-08**, and produced eight Top-7 lists with frozen Clean Phoenix 1.1.
- These were recorded as the live-style test output, not as a result claim. The actual race facit must be imported separately before evaluating hits.
- Top-7 numbers produced:
  - Race 1: **8, 5, 10, 2, 12, 9, 7**
  - Race 2: **9, 4, 2, 1, 12, 6, 8**
  - Race 3: **8, 7, 10, 6, 5, 11, 9**
  - Race 4: **8, 2, 1, 15, 7, 10, 11**
  - Race 5: **1, 2, 9, 4, 8, 3, 6**
  - Race 6: **6, 7, 4, 3, 8, 11, 2**
  - Race 7: **9, 6, 4, 8, 10, 1, 7**
  - Race 8: **4, 7, 3, 10, 9, 2, 6**

### Next principle
- Do **not** change the frozen Clean Phoenix baseline before the current facit is available.
- Import the actual V64 result after the races and compare winner rank against the frozen Top-7 predictions.
- Then summarize Top 1 / Top 3 / Top 5 / Top 7 and use that as a real-world checkpoint.
- Future improvements should be evaluated on a new unseen holdout, never by tuning against already-used holdout results.
- Long-term objective: improve Phoenix Intelligence toward **100/100** without leakage, overfitting, or post-hoc optimization.

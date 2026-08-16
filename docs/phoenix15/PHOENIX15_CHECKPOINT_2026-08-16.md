# Phoenix 15 — Checkpoint 2026-08-16

## Status
Paused after READ ONLY diagnostics. **Important: the 8-race result set previously analysed in this checkpoint is the 2026-08-15 Åby card, not the current 2026-08-16 date.** The earlier wording incorrectly called it today's result. Treat that wording as corrected.

**No database changes. No Phoenix model changes. No Feature Engine changes.**

Database used in Colab:
`/content/drive/MyDrive/PhoenixTrav/phoenix_trav.db`

## Verified result/prediction coverage for the analysed card
- Phoenix 15 predictions: 98
- Phoenix 15 results: 98
- Matched starters: 98
- Races: 8
- Actual winners: 8
- Starters with valid Phoenix score: 91
- Starters without Phoenix score: 7
- No actual winner is missing a Phoenix score

## Phoenix performance on the analysed 8 races
- Top 1: 2/8 = 25.0%
- Top 3: 5/8 = 62.5%
- Top 5: 6/8 = 75.0%
- Top 7: 7/8 = 87.5%
- Top 10: 7/8 = 87.5%
- Winners outside Top 7: 1/8
- The outside-Top-7 winner was Fabulous Gent, Phoenix rank 11, score 16.435833, probability 0.133403, odds 5.31.

## The 7 missing Phoenix scores
1. 792193 — Jonases Lykka
2. 810983 — Tangen Merete
3. 777257 — Tangen Bork
4. 810900 — Grude Nils
5. 810985 — Skeie Loke
6. 816725 — Hallogubben
7. 816726 — Lannem Pär

All seven are missing these horse-level features:
- `horse_starts`
- `horse_wins`
- `horse_win_pct`
- `form_score`

Driver and trainer features are present for the affected starters.

## Horse-history diagnosis
The affected horse IDs exist in the `horses` table except that 777257 (Tangen Bork) has no matching horse-table name in the diagnostic join.

Six of the seven have rows in `horse_results`; one (777257 Tangen Bork) has no `horse_results` row.

For the six existing history rows, the following result fields are NULL:
- `placement`
- `placement_sort`
- `odds_sort`
- `kilometer_time`

The six rows found are all from `race_day_id = 616511`, dated 2026-07-27. Therefore the current working hypothesis is an incomplete horse-history import / result-data gap, not a Phoenix ranking problem.

## Important model conclusion
Do **not** rebuild or modify Phoenix Score, Feature Engine, ranking logic, or the database based on this diagnostic. The missing-score issue is isolated to horse-history inputs and must first be traced to the import/data source path.

The previous diagnostic also confirmed that Fabulous Gent has a valid Phoenix score and complete feature row, so its Top-7 miss is a genuine ranking/out-of-sample diagnostic case, separate from the seven missing-score starters.

## Next diagnostic to run when resumed
Run the READ ONLY diagnostic for `race_day_id = 616511`:
1. Inspect all `horse_results` rows for race day 616511.
2. Measure missingness of `placement`, `placement_sort`, `odds_sort`, and `kilometer_time` across that race day.
3. Compare the seven affected horses against the rest of the same race day.
4. Check whether the affected horses have valid history rows on other race days.
5. Only after this determine where the import gap originates.

Do not repair data yet. Do not write to SQLite. Do not change model/feature code.

## Resume point
Continue from the cell named:
`PHOENIX 15 — HORSE_RESULTS IMPORTGAP v3`

This checkpoint is intended to prevent repeating the diagnostics and to preserve the verified state before any fix is attempted.
# PHOENIX 15 — Known-good V85 run record

- Run date: 2026-10-17
- Game: V85
- Track folder: Gävle
- Status: full pipeline completed
- Races: 8
- Starters: 98
- History rows: 98
- Feature rows: 98
- Feature columns: 37
- Predictions: 98
- Ranked starters: 98
- Market check: OK; 93 valid odds, 5 missing odds, no errors
- Combined weighting: 35% Phoenix / 65% ATG market
- Distance Rescue: skipped because historical distance columns were unavailable
- Database writes: none
- Model changes: none
- Output CSVs saved in Drive:
  - `phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/startlist_v85.csv`
  - `phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/ranked_v85.csv`
  - `phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/market_df.csv`

## Combined Top 7 (35/65)

| Race | Ranked starters |
|---|---|
| V85-5 | 2, 3, 6, 4, 10, 1, 8 |
| V85-6 | 5, 10, 8, 2, 3, 7, 11 |
| V85-7 | 12, 6, 2, 1, 11, 3, 10 |
| V85-8 | 1, 7, 2, 6, 4, 8, 9 |
| V85-9 | 1, 4, 8, 2, 6, 9, 10 |
| V85-10 | 7, 5, 9, 4, 12, 3, 11 |
| V85-11 | 6, 7, 1, 3, 9, 4, 5 |
| V85-12 | 4, 9, 2, 3, 10, 1, 5 |

## Important limitation

This file records the successful run and its output. It is **not** the executable launcher source. The exact cell that produced this log must be copied from the Colab notebook and committed separately before it can be called a reproducible, frozen code version. Do not replace the existing `PHOENIX15_START_HERE.py` or V86 standard cell based only on this record.

## Reproducibility checklist

- [ ] Save the exact successful V85 cell source from Colab.
- [ ] Commit it under a new V85-specific path without overwriting the protected V86 entry point.
- [ ] Verify the new GitHub file can be fetched and run from a fresh Colab.
- [ ] Keep database and model read-only.

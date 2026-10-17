# Phoenix 15 — Recovery and safety record
Updated: 2026-10-17
Repository: `Travkungen/Travsystem`, branch `main`

## Priority: preserve the working system

The known-good V85 run from 2026-10-17 completed the full pipeline. Treat its outputs and the frozen Drive checkpoint as recovery references.

**Do not** overwrite the existing V86 start files, globally replace V86/V85 strings, retrain or overwrite model files, or write to the production SQLite database as part of recovery.

## Known-good run

- Game/date: V85, 2026-10-17, Gävle
- Races: 8
- Starters: 98
- History rows: 98
- Feature rows: 98
- Feature columns: 37
- Market check: 8 races / 98 starters; 93 valid odds, 5 missing odds, no errors
- Ranking blend: 35% Phoenix / 65% ATG market
- Database writes: none
- Model writes: none
- Distance Rescue: skipped because historical distance columns were unavailable

Combined Top 7, by race:
- V85-10: 7, 5, 9, 4, 12, 3, 11
- V85-11: 6, 7, 1, 3, 9, 4, 5
- V85-12: 4, 9, 2, 3, 10, 1, 5
- V85-5: 2, 3, 6, 4, 10, 1, 8
- V85-6: 5, 10, 8, 2, 3, 7, 11
- V85-7: 12, 6, 2, 1, 11, 3, 10
- V85-8: 1, 7, 2, 6, 4, 8, 9
- V85-9: 1, 4, 8, 2, 6, 9, 10

## Drive checkpoint and artifacts

Frozen checkpoint folder:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/frozen_runs/PHOENIX15_V85_2026-10-17_20261017_102044`

The checkpoint cell reported:
- 3 result files saved
- source cell saved as `launcher_cell.py`
- manifest with SHA-256 saved
- database unchanged
- model unchanged
- status: RESULTAT FRYST

Original database used by the successful run:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/recovery_checkpoints/PHOENIX15_COLAB_TRANSITION_20260810_211119/database/phoenix_trav.db`

Run outputs:
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/startlist_v85.csv`
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/ranked_v85.csv`
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/live_outputs/2026-10-17_V85_Gavle/market_df.csv`

## GitHub files and their purpose

- `phoenix15/checkpoints/PHOENIX15_V85_KNOWN_GOOD_2026-10-17.md`: run record and result summary; **not executable source**.
- `phoenix15/colab/PHOENIX15_V85_START_HERE.py`: launcher that validates the frozen Drive source against its manifest and runs it.
- `phoenix15/colab/PUBLISH_FROZEN_V85_TO_GITHUB.py`: optional Colab publisher to copy the exact frozen source from Drive into GitHub.
- `phoenix15/colab/PHOENIX15_V86_START_STANDARD.py`: existing V86 entrypoint; leave unchanged.
- `phoenix15/colab/PHOENIX15_START_HERE.py`: existing standard start file; leave unchanged.

## Important limitation / next integrity step

The exact successful source is currently confirmed in the private Drive checkpoint as `launcher_cell.py`, but has **not yet been confirmed as committed verbatim** to the repository. The GitHub V85 launcher and publisher are committed helpers; they do not substitute for the missing exact source.

To complete source preservation, either:
1. In the Colab session that can access the Drive checkpoint, run `phoenix15/colab/PUBLISH_FROZEN_V85_TO_GITHUB.py` with a Colab Secret named `GITHUB_TOKEN` that has Contents write access; or
2. Download/share `launcher_cell.py` itself so it can be committed directly.

After publishing, verify that `phoenix15/colab/PHOENIX15_V85_START_STANDARD.py` exists and compare its SHA-256 with the Drive manifest. Do not call the source secured until this check passes.

## Recovery rules

1. Preserve the frozen Drive folder unchanged.
2. Keep result CSVs and manifest with the launcher source.
3. Never put GitHub tokens or other secrets in this repository.
4. Use a separate V85 file; do not replace V86 files.
5. Run future tests in read-only mode first. Verify race count, starter count, odds validation, and output path before considering a run successful.

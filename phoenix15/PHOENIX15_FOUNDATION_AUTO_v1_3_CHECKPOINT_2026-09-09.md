# Phoenix 15 — Foundation Auto v1.3 Checkpoint

Date: 2026-09-09
Game: V86
Status: VERIFIED PASS

## Verified foundation
- 8/8 V86 races
- 81 active starters after scratch guard
- Locked Phoenix engine verified
- Frozen raw score range: -9.1 to 1.5167
- Locked output: 81 rows, 8 races, 8 rank-1
- Unique raw scores: 75
- Unique probabilities: 81
- Market: 81 verified odds
- 50/50 Phoenix + Market merge verified
- Fixed Top7: 56 rows (7 per race)

## Safety
- Master: READ ONLY
- Frozen model: READ ONLY
- SQLite: READ ONLY
- No model write
- No Master write
- Top7 is a fixed base and must never be reduced
- Future intelligence layers may only add candidates outside the fixed Top7

## Drive checkpoint
`PhoenixTrav/phoenix_15_live/checkpoints/FOUNDATION_AUTO_v1_3/`

Files:
- `foundation_auto_v1_3_live.csv` — 81 rows
- `foundation_auto_v1_3_top7.csv` — 56 rows
- `foundation_auto_v1_3_checkpoint.json`

## Purpose
This GitHub file records the verified definition and state of the Foundation Auto v1.3 checkpoint. The live CSV/JSON data remains stored in Google Drive; GitHub stores the canonical checkpoint documentation.

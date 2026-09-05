# Phoenix 15 — V85 Checkpoint 2026-09-05

## Status
SAFE CHECKPOINT — COLAB RECOVERY READY

## Round
- Date: 2026-09-05
- Game: V85
- Track: Jägersro
- Races: 8
- Starters: 99
- Valid live odds: 93
- Missing/invalid odds: 6

## Verified pipeline
Startlist → Horse History → Person Bridge → Feature Engine → Frozen Model → Locked Phoenix → Live Odds → Market Rank → MillionSecret → System decision.

- Master: READ ONLY
- Frozen Model: READ ONLY
- Locked Phoenix: verified
- Person Bridge: verified
- 20 Frozen Model features: verified and varying
- Feature pipeline status: VERIFIED LIVE PIPELINE

## Saved systems
- 100 KR profile: 120 rows = 60 KR
- 400 KR profile: 720 rows = 360 KR
- 2000 KR profile: 3,600 rows = 1,800 KR
- 4000 KR profile: 7,200 rows = 3,600 KR

The systems are stored as Parquet in the Google Drive checkpoint.

## Google Drive master checkpoint
`/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/analysis_checkpoints/v85_live/FULL_CHECKPOINT_20260905_122605`

The checkpoint contains the startlist, history, features, scored output, locked Phoenix output, odds, market data, MillionSecret data, race decisions, final value data, all four systems, race map, verified feature pipeline and MANIFEST.

## Recovery rule
Do not rebuild Phoenix Master or Frozen Model. Restore this V85 checkpoint from Drive and continue from the saved state.

## Important
This GitHub file is the durable textual checkpoint/index. The binary Parquet artifacts remain on Google Drive at the path above.

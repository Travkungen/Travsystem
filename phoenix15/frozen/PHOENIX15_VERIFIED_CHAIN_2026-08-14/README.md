# Phoenix 15 — Verified Chain Freeze

Date: 2026-08-14

This document freezes the verified Phoenix 15 chain up to the Feature Engine boundary. It is a reference baseline and must not be modified as part of Feature Engine v2 development.

## Verified baseline — Åby V85

- 89 starters
- 8 races
- Person Bridge: VERIFIED
- Driver data: 89/89 nonzero
- Trainer data: 86/89 nonzero
- Feature schema: VERIFIED
- 25 live columns
- 0 race+horse duplicates
- Model Engine: VERIFIED
- Model: HistGradientBoostingClassifier
- Model features: 20
- Training medians: present
- Ranking Engine: READ ONLY / VERIFIED

## Model features

1. starts
2. wins
3. win_percent
4. top3
5. top3_percent
6. last5_starts
7. last5_wins
8. last5_top3
9. last5_win_percent
10. driver_starts
11. driver_wins
12. driver_win_percent
13. driver_top3_percent
14. trainer_starts
15. trainer_wins
16. trainer_win_percent
17. trainer_top3_percent
18. hd_starts
19. hd_wins
20. hd_win_percent

## Boundary for new development

Everything before the Feature Engine boundary is treated as frozen/verified.

The unresolved issue is the Horse History -> Feature Build transition: the 9 horse-history features are produced by Horse History but did not reach the live feature dataframe. The existing Feature Engine, Model Engine, Ranking Engine and database must not be changed as part of this freeze.

## Development rule

Build Feature Engine v2 separately. Do not overwrite this directory. The verified chain remains the reference baseline.

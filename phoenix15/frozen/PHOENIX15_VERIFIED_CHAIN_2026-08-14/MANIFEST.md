# Phoenix 15 — Frozen Baseline Manifest

Commit: 3018316509420d67284bc903ddbc3ed37d299635
Repository: Travkungen/Travsystem

## Status

FROZEN REFERENCE BASELINE

## Verified chain

ATG -> Discovery -> Startlist -> Person Bridge -> Feature-input boundary

## Åby V85 verification

| Check | Result |
|---|---|
| Starters | 89 |
| Races | 8 |
| Driver starts | 89/89 nonzero |
| Trainer starts | 86/89 nonzero |
| Trainer wins | 86/89 nonzero |
| Trainer win percent | 86/89 nonzero |
| Trainer top3 percent | 86/89 nonzero |
| Horse-driver starts | 50/89 nonzero |
| Horse-driver wins | 26/89 nonzero |
| Horse-driver win percent | 26/89 nonzero |
| Live columns | 25 |
| Race+horse duplicates | 0 |
| Feature schema | VERIFIED |
| Model Engine | VERIFIED |
| Model type | HistGradientBoostingClassifier |
| Model features | 20 |
| Train medians | YES |
| Ranking Engine | READ ONLY / VERIFIED |

## Frozen modules / components

The following component identities were verified in the working Colab and are protected conceptually by this manifest:

- phoenix15_automation_orchestrator_v2.py
- phoenix15_horse_history_v1.py
- phoenix15_feature_build_v1.py
- phoenix15_model_engine_v1.py
- phoenix15_race_ranking_v1.py
- phoenix15_baseline_v2_1.pkl

The source copies should be added to this frozen directory from the verified Colab/Drive environment when available. This manifest does not claim that GitHub already contains byte-for-byte copies of those source files.

## Known unresolved item

Horse History -> Feature Build does not currently transfer the 9 horse-history features into the live feature dataframe. This is the only development target identified at the freeze point.

## Protection rule

Do not modify this frozen directory when developing Feature Engine v2. Create a separate development path and preserve this baseline unchanged.

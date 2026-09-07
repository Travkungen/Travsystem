# PHOENIX 15 — INTELLIGENT ENGINE V1

**Version:** 1.0  
**Date:** 2026-09-07  
**Status:** VERIFIED FOUNDATION / PARTLY PROVISIONAL

## Safety

- Master is READ ONLY.
- Frozen model is READ ONLY.
- Model file is READ ONLY.
- The engine is a downstream decision layer only.
- Existing v1/v2 automation files are not overwritten.

## Canonical pipeline

`ATG -> active starters -> current Vinnare odds -> Market rank -> Phoenix prediction -> exact 60/40 -> TOP7 -> Spike motor + graded Skräll motor -> dynamic budget -> reduction -> final V64/V85 row`

A parallel live report is generated from TOP7 and explains why a horse is interesting.

## 1. Live model-scale adapter

The verified live feature builder currently emits percentage features on a 0–1 scale while the frozen model was trained on 0–100. The canonical adapter therefore multiplies these percentage fields by 100 immediately before prediction.

Affected fields:

- win_percent
- top3_percent
- last5_win_percent
- driver_win_percent
- driver_top3_percent
- trainer_win_percent
- trainer_top3_percent
- hd_win_percent

This is an adapter. It does **not** modify the model or training data.

## 2. Phoenix / Market 60/40

The exact recovered OOS formula is raw-value min-max normalization per race:

`phoenix_norm = (phoenix_score - min) / (max - min)`

`market_norm = (max_odds - odds) / (max_odds - min_odds)`

`score_6040 = 0.60 * phoenix_norm + 0.40 * market_norm`

Rank descending by `score_6040`.

This is **not** percentile rank and **not** inverse-rank weighting.

## 3. TOP7

TOP7 is the candidate pool. It is generated **before** spike, skräll, budget and reduction decisions.

Exactly seven candidates are retained per active race when seven or more active starters exist.

## 4. Spike motor — OOS verified

The current verified zones are based on five OOS blocks.

### S4

- Market rank 1–2
- P1–P2 marginal >= 0.40
- field >= 9
- historical OOS: 84.67% winner coverage
- OOS1–OOS5: 89.47%, 86.21%, 85.71%, 87.10%, 77.78%

### S2

- Market rank 1–2
- marginal 0.20–0.30
- historical OOS: 65.69%

### S3

- Market rank 1–2
- marginal 0.30–0.40
- historical OOS: 57.31%

### S1

- Market rank 1–2
- marginal 0.10–0.20
- historical OOS: 53.48%

These labels are quality zones, not probabilities.

## 5. Graded Skräll motor

The skräll motor is intentionally graded rather than binary.

### VALIDATED

**Million V2:**

- 60/40 rank = 5
- Phoenix rank = 3
- Market rank = 4–5

This is marked `VALIDERAD MILLION V2`.

### PROVISIONAL / DIAGNOSTIC

Broader TOP7 skräll grades may flag horses when:

- 60/40 rank <= 7
- Phoenix rank <= 3
- Market rank 4–7

These broader grades are **not locked** until OOS-tested separately.

The live report must always distinguish `VALIDERAD` from `DIAGNOSTISK — EJ LÅST`.

## 6. Dynamic budget

The number of spiks must not be fixed at two or three.

The engine may recommend 0–3 maximum spiks depending on the quality of the current race set. The current budget policy is explicitly **PROVISIONAL** and must be OOS-validated before production lock.

The budget layer must also consider the skräll distribution and TOP7 depth before final row generation.

## 7. Future game support

The architecture is game-agnostic. Game type and race IDs must come from the live ATG game object. Do not infer V64/V85 from generic database `race_day_id`.

## 8. Live presentation

The dashboard produces:

- TOP7 ranking graphic
- Spike graphic
- Skräll graphic
- HTML report with explanations/status

The report is separate from the final betting row.

## 9. Versioning rule

Never overwrite an existing engine to change a formula. Create a new version and preserve the old one. A formula becomes canonical only after explicit verification and checkpointing.

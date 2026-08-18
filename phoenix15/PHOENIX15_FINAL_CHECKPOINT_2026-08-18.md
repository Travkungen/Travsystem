# PHOENIX 15 — FINAL PLAY/REDUCTION CHECKPOINT

**Date:** 2026-08-18
**Status:** PLAY LAYER FROZEN FOR VALIDATION

## Verified today
- Frozen Phoenix V3 model used read-only.
- Real V3 probabilities verified.
- Market rank and odds included.
- Withdrawn/non-playable starters excluded from play layer.
- Signal classes: SPIK / A / B / SKRÄLL / RESERV.
- Play profile layer: SAFE / BALANS / OFFENSIV.
- Spike maturity/strength layer verified.
- Final reusable reduction/play module added: `PHOENIX15_PLAYMOTOR_FINAL.py`.
- Exact budget outputs verified for 32, 96 and 192 rows.
- No model training/write.
- No SQLite write from the play layer.

## Current design
### SAFE
Conservative candidate fields and exactly 32 selected rows.

### BALANS
Broader candidate fields and exactly 96 selected rows.

### OFFENSIV
Broader candidate fields, value/skräll exposure and exactly 192 selected rows.

## Final play engine scoring inputs
- Phoenix probability
- Market rank
- Odds/value
- Signal class
- Skräll value
- Row diversification

## Important validation status
The architecture is frozen for testing, but statistical optimality is NOT yet proven. The engine must be evaluated against accumulated official results before changing scoring weights or the Phoenix V3 model.

## Reproducibility
Use `PHOENIX15_COLAB_START.py` for startup and the minimal workflow in `PHOENIX15_COLAB_MINIMAL_WORKFLOW.md`. Colab runtime state must never be treated as the permanent source of truth.

## Next required learning loop
1. Run today's V64.
2. Import official results after the round.
3. Save prediction + coupon snapshot.
4. Compare Phoenix ranks, market ranks, spikes, A/B/SKRÄLL and coupon hits.
5. Store the round as facit/experience.
6. Accumulate evidence over multiple rounds.
7. Only then consider weight changes.

**Principle:** Phoenix ranks. History teaches. Reduction allocates the budget. Results update the experience bank.

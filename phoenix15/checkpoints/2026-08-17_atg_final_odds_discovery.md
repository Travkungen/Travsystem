# Phoenix 15 — ATG finalOdds discovery (2026-08-17)

## CRITICAL VERIFIED DISCOVERY
The current ATG extended race payload contains the current market odds at:

`starts[*].result.finalOdds`

This was verified against real Färjestad V64 extended data and matched by:
- `race_id`
- `start.number`
- `start.horse.name`
- `start.result.finalOdds`

Examples verified:
- V1: 1 Electra A'lir = 4.05; 2 Nueva = 3.27; 4 Million Moni = 4.74
- V6: 1 Ideal Kronos = 1.65; 2 Alastair = 45.76; 3 Game Stop = 16.16; 6 Panne de Mi B.T.B. = 17.67

A recursive scan found 743 odds-related fields across the fetched races. The correct current-race market field is `starts[*].result.finalOdds`, NOT historical horse-result odds such as `horse.results.records[*].odds`, and NOT `lastFiveStarts.averageOdds`.

`finalOdds == 0.0` must be treated as missing/invalid for ranking purposes, not as a genuine market price.

## ARCHITECTURE RULE
Do not change Phoenix 15 ranking/features yet. Add odds as a separate market layer:

ATG extended -> Phoenix features/ranking -> market finalOdds -> Odds Rank -> Phoenix vs Odds comparison -> Spikmotor/Reduktionsmotor.

The purpose is to test whether odds add information to Phoenix Top 7 and improve spike/reduction decisions.

## IMPORTANT
This discovery must be reused permanently. Do NOT spend time rediscovering the odds field. Future live workflows should extract `starts[*].result.finalOdds` directly from the same extended payload already used by Phoenix.

MASTER/database remains READ ONLY.

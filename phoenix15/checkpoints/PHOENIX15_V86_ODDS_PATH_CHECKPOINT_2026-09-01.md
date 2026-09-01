# PHOENIX 15 — ODDS PATH CHECKPOINT
## 2026-09-01

The ATG V86 odds path is now VERIFIED against the live V86 card for 2026-09-02.

### Correct endpoint
https://www.atg.se/services/racinginfo/v1/api/games/vinnare_{race_id}

Example:
https://www.atg.se/services/racinginfo/v1/api/games/vinnare_2026-09-02_5_6

### Correct field
races[*].starts[*].pools.vinnare.odds

### Conversion
odds_raw / 1000 = decimal odds.

### Verified live result
- 8 V86 races
- 80 starters
- 80/80 odds rows
- horse_id and race_id match the existing V86 data

### Architecture
Phoenix ranking remains separate and unchanged.

Pipeline:
ATG V86 -> existing Phoenix features/prediction/ranking -> separate ATG winner odds -> market rank/favorite -> Phoenix Top 7 vs odds analysis.

### Important
Do NOT restart discovery of the odds endpoint.
Do NOT modify Master/database/model.
Use phoenix15/colab/PHOENIX15_V86_ODDS_CELL.py as the reusable Colab odds cell.

Note: an older checkpoint documented starts[*].result.finalOdds in an extended race payload. The current verified live market route for the V86 odds layer is the games/vinnare_{race_id} endpoint above. These are separate data paths; the Phoenix ranking is not changed.

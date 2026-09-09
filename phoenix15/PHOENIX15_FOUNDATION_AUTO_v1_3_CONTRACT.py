# PHOENIX 15 — FOUNDATION AUTO v1.3
# Verified live: 2026-09-09
# READ ONLY / FAIL FAST

VERSION = "1.3"
GAME_RACES = {"V64": 6, "V85": 8, "V86": 8}

MODEL_FEATURES = [
    "starts", "wins", "win_percent", "top3", "top3_percent",
    "last5_starts", "last5_wins", "last5_top3", "last5_win_percent",
    "driver_starts", "driver_wins", "driver_win_percent",
    "driver_top3_percent", "trainer_starts", "trainer_wins",
    "trainer_win_percent", "trainer_top3_percent",
    "hd_starts", "hd_wins", "hd_win_percent"
]

# VERIFIED FOUNDATION CONTRACT
# ATG -> race/date guard -> scratches -> driver/trainer/HD bridge
# -> HorseHistory -> FeatureBuild -> exact Frozen 20 -> 0-100 percentage conversion
# -> Frozen decision_function raw score -> locked Phoenix probability/rank
# -> Market rank on identical active starters -> 50/50 -> fixed Top7.
#
# LIVE PASS 2026-09-09:
# Active: 81
# Races: 8
# Frozen raw: -9.6365 .. -4.1286
# Unique raw scores: 64
# Unique probabilities: 78
# Locked Rank1: 8/8 races
# Foundation Top7: 56 rows
#
# 50/50 = (phoenix_rank + market_rank) / 2.0
# Top7 is the fixed FAST BASE and is never reduced by Foundation.
#
# Master: READ ONLY
# Frozen: READ ONLY
# SQLite: READ ONLY

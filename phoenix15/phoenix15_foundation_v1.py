# PHOENIX 15 — FOUNDATION v1
# Verified 2026-09-09
# Contract: ATG -> race guard -> scratches -> bridge -> Frozen -> Market -> 50/50 Top7
# READ ONLY / FAIL FAST

VERSION = "1.0"
GAME_RACES = {"V64": 6, "V85": 8, "V86": 8}

# Verified live foundation contract:
# 1. Correct game/date/race IDs
# 2. Scratched starters removed BEFORE ranking
# 3. Active starters unique
# 4. Driver/trainer bridge + horse-driver history
# 5. Exact Frozen 20 model features
# 6. Percentage inputs converted to the model's verified 0-100 scale
# 7. Locked Phoenix raw score/rank
# 8. Market rank on the exact same active starters
# 9. 50/50 = (Phoenix rank + Market rank) / 2
# 10. Top7 is the FAST BASE and is not reduced by this foundation

# This file records the verified foundation contract.
# The live Colab implementation remains READ ONLY against Master/Frozen/SQLite.

# ================================================================
# PHOENIX 15 — V86 ODDS CELL
# ================================================================
# Separat marknadslager. Ändrar INTE Phoenix features, prediction
# eller ranking.
#
# Förutsätter att v86 redan finns från PHOENIX15_START_HERE.
#
# VERIFIERAD ATG-VÄG:
# https://www.atg.se/services/racinginfo/v1/api/games/vinnare_{race_id}
#
# Odds finns i:
# races[*].starts[*].pools.vinnare.odds
#
# odds_raw / 1000 = decimalodds.
# 0 och 9999 behandlas som saknade/ogiltiga för ranking.
# ================================================================

import requests
import pandas as pd
import time

BASE = "https://www.atg.se/services/racinginfo/v1/api"

v86_race_ids = sorted(v86["race_id"].dropna().unique())

rows = []

for race_id in v86_race_ids:
    url = f"{BASE}/games/vinnare_{race_id}"
    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        print(race_id, "STATUS:", r.status_code)
        continue

    data = r.json()

    for race in data.get("races", []):
        if race.get("id") != race_id:
            continue

        for start in race.get("starts", []):
            horse = start.get("horse", {})
            vinnare = start.get("pools", {}).get("vinnare", {})
            odds_raw = vinnare.get("odds")

            rows.append({
                "race_id": race_id,
                "start_number": start.get("number"),
                "horse_id": horse.get("id"),
                "horse_name": horse.get("name"),
                "odds_raw": odds_raw,
                "odds": (
                    float(odds_raw) / 1000
                    if odds_raw is not None
                    else None
                ),
            })

    time.sleep(0.15)

odds_v86 = pd.DataFrame(rows)

if odds_v86.empty:
    raise RuntimeError("Inga V86-odds hämtades.")

print("=" * 64)
print("PHOENIX 15 — V86 ODDS HÄMTADE")
print("=" * 64)
print("Lopp    :", odds_v86["race_id"].nunique())
print("Starter :", len(odds_v86))

if odds_v86["race_id"].nunique() != len(v86_race_ids):
    raise RuntimeError(
        f"Odds saknas för lopp: "
        f"{set(v86_race_ids) - set(odds_v86['race_id'].unique())}"
    )

if len(odds_v86) != len(v86):
    raise RuntimeError(
        f"Odds mismatch: {len(odds_v86)} mot {len(v86)} starter."
    )

print("MATCH   : 80/80 (för aktuell V86-omgång om v86=80)")
print()
print(odds_v86.head(12).to_string(index=False))

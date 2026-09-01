# ================================================================
# PHOENIX 15 — V86 STARTCELL STANDARD
# ================================================================
# Framtida Colab-startcell.
# Kör hela kedjan: ATG -> V86 -> startlista -> history ->
# features -> prediction -> Phoenix rank -> Top 7.
#
# READ ONLY mot historik-DB och modell.
# Ingen DB-skrivning. Ingen modelländring.
#
# Förutsätter att Phoenix15-filerna ligger under ROOT.
# Datum kan ändras längst ned.
# ================================================================

from pathlib import Path
import sqlite3
import sys
import pandas as pd

ROOT = Path("/content/drive/MyDrive/PhoenixTrav/phoenix_15_live")
AUTO = ROOT / "race_automation"
DB = ROOT / "recovery_checkpoints/PHOENIX15_COLAB_TRANSITION_20260810_211119/database/phoenix_trav.db"
MODEL = ROOT / "models/phoenix15_baseline_v2_1.pkl"

TARGET_DATE = "2026-09-02"   # <-- ändra endast detta datum

for p in [AUTO, DB, MODEL]:
    if not p.exists():
        raise FileNotFoundError(f"Saknas: {p}")

sys.path.insert(0, str(AUTO))

from phoenix15_atg_loader_v1 import PhoenixATGLoader
from phoenix15_race_discovery_v1 import PhoenixRaceDiscovery
from phoenix15_automation_orchestrator_v2 import PhoenixAutomationOrchestratorV2

print("=" * 64)
print("PHOENIX 15 — V86 START")
print("=" * 64)
print("DATUM:", TARGET_DATE)
print("DB   :", DB)

# ------------------------------------------------
# 1. Öppna verifierad historik-DB
# ------------------------------------------------
conn = sqlite3.connect(str(DB))

# Kontrollera att DB verkligen är användbar.
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)["name"].tolist()

if not tables:
    conn.close()
    raise RuntimeError("DB saknar tabeller.")

print("DB tables:", len(tables))

# ------------------------------------------------
# 2. Ladda dagens ATG-data
# ------------------------------------------------
loader = PhoenixATGLoader()
today_data = loader.load(TARGET_DATE)

print("ATG tracks:", len(today_data.get("tracks", [])))
print("ATG games :", len(today_data.get("games", [])))

# ------------------------------------------------
# 3. Discovery
# ------------------------------------------------
discovery = PhoenixRaceDiscovery()
discovered = discovery.discover_from_today_data(today_data)

print("DISCOVERY:", len(discovered))

# ------------------------------------------------
# 4. Orchestrator med ÖPPEN DB-connection
# ------------------------------------------------
orch = PhoenixAutomationOrchestratorV2(
    auto_dir=AUTO,
    model_path=MODEL,
    conn=conn
)

orch.load_engines()

for name in ["discovery", "startlist", "history", "features",
             "model", "ranking", "top5"]:
    if getattr(orch, name, None) is None:
        conn.close()
        raise RuntimeError(f"Engine saknas: {name}")

# ------------------------------------------------
# 5. Startlista
# ------------------------------------------------
startlist = orch.build_startlist(today_data, discovered)

if startlist.empty:
    conn.close()
    raise RuntimeError("Ingen startlista kunde byggas.")

print("STARTLIST:", len(startlist))

# ------------------------------------------------
# 6. Isolera V86 via ATG:s faktiska V86-game
# ------------------------------------------------
v86_games = [
    g for g in today_data.get("games", [])
    if isinstance(g, dict) and g.get("id", "").startswith("V86_")
]

if not v86_games:
    conn.close()
    raise RuntimeError("V86-game hittades inte.")

v86_game = v86_games[0]
v86_ids = set(v86_game.get("races", []))

startlist_v86 = startlist[
    startlist["race_id"].astype(str).isin(v86_ids)
].copy()

startlist_v86 = startlist_v86.sort_values(
    ["race_id", "start_number"]
).reset_index(drop=True)

print("V86 LOPP:", startlist_v86["race_id"].nunique())
print("V86 STARTER:", len(startlist_v86))

if startlist_v86["race_id"].nunique() != 8:
    conn.close()
    raise RuntimeError(
        f"Förväntade 8 V86-lopp, fick "
        f"{startlist_v86['race_id'].nunique()}"
    )

# ------------------------------------------------
# 7. Hästhistorik
# ------------------------------------------------
history_v86 = orch.history.build(startlist_v86)

if len(history_v86) != len(startlist_v86):
    conn.close()
    raise RuntimeError(
        f"History mismatch: {len(history_v86)} mot "
        f"{len(startlist_v86)} starter."
    )

print("HISTORY:", len(history_v86))

# ------------------------------------------------
# 8. Features
# ------------------------------------------------
features_v86 = orch.build_features(
    startlist_v86,
    history_v86
)

if len(features_v86) != len(startlist_v86):
    conn.close()
    raise RuntimeError("Features har fel antal rader.")

print("FEATURES:", len(features_v86))
print("FEATURE COLUMNS:", len(features_v86.columns))

# ------------------------------------------------
# 9. Prediction
# ------------------------------------------------
prediction_v86 = orch.predict(features_v86)

if len(prediction_v86) != len(features_v86):
    conn.close()
    raise RuntimeError("Prediction har fel antal rader.")

print("PREDICTION:", len(prediction_v86))

# ------------------------------------------------
# 10. Phoenix rank
# ------------------------------------------------
ranked_v86 = orch.rank(
    prediction_v86
)

if len(ranked_v86) != len(startlist_v86):
    conn.close()
    raise RuntimeError("Rank har fel antal rader.")

print("RANK:", len(ranked_v86))

# ------------------------------------------------
# 11. Slutkontroll
# ------------------------------------------------
race_count = ranked_v86["race_id"].nunique()

print()
print("=" * 64)
print("PHOENIX 15 — V86 KLAR")
print("=" * 64)
print("Lopp   :", race_count)
print("Starter:", len(ranked_v86))

print()
print("=== TOP 7 ===")

top7 = {}

for race_id, g in ranked_v86.groupby("race_id", sort=False):
    g = g.sort_values("phoenix_rank")
    race_no = int(g["race_number"].iloc[0])
    nums = g.head(7)["start_number"].astype(int).tolist()
    top7[race_no] = nums
    print(f"V86-{race_no}: " + " ".join(map(str, nums)))

if len(top7) != 8:
    conn.close()
    raise RuntimeError("Top 7 saknas för något V86-lopp.")

print()
print("INGEN DB-SKRIVNING")
print("INGEN MODELLÄNDRING")
print("=" * 64)

# Behåll connection öppen om nästa cell vill använda orch/ranked_v86.
# Stäng den inte här.

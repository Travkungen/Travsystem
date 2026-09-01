# ================================================================
# PHOENIX 15 — START HERE
# ================================================================
# Standard framtida startcell.
#
# Användning:
#   DATE_MODE = "today"     -> dagens lopp
#   DATE_MODE = "tomorrow"  -> morgondagens lopp
#   DATE_MODE = "date"      -> ange TARGET_DATE
#
# Denna cell hämtar senaste standardkoden från GitHub och kör
# Phoenix 15 V86-startkedjan.
#
# Ingen DB-skrivning. Ingen modelländring.
# ================================================================

from pathlib import Path
import urllib.request
import runpy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

REPO_RAW = "https://raw.githubusercontent.com/Travkungen/travsystem/main/phoenix15/colab/PHOENIX15_V86_START_STANDARD.py"

DATE_MODE = "today"       # "today", "tomorrow" eller "date"
TARGET_DATE = None        # används bara när DATE_MODE == "date"

tz = ZoneInfo("Europe/Stockholm")
now = datetime.now(tz)

if DATE_MODE == "today":
    TARGET_DATE = now.strftime("%Y-%m-%d")
elif DATE_MODE == "tomorrow":
    TARGET_DATE = (now + timedelta(days=1)).strftime("%Y-%m-%d")
elif DATE_MODE == "date":
    if not TARGET_DATE:
        raise RuntimeError("Ange TARGET_DATE när DATE_MODE='date'.")
else:
    raise RuntimeError("DATE_MODE måste vara today, tomorrow eller date.")

print("=" * 64)
print("PHOENIX 15 — START HERE")
print("=" * 64)
print("DATE:", TARGET_DATE)
print("HÄMTAR STANDARDKOD FRÅN GITHUB...")

code = urllib.request.urlopen(REPO_RAW, timeout=30).read().decode("utf-8")

# Ersätt datumet i standardcellen utan att ändra filen på GitHub.
code = code.replace(
    'TARGET_DATE = "2026-09-02"   # <-- ändra endast detta datum',
    f'TARGET_DATE = "{TARGET_DATE}"'
)

exec(compile(code, REPO_RAW, "exec"))

print()
print("=" * 64)
print("PHOENIX 15 — START HERE KLAR")
print("=" * 64)

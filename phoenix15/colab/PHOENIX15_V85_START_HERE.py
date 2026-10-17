# ================================================================
# PHOENIX 15 — V85 START HERE (FROZEN LAUNCHER)
# ================================================================
# Runs the exact V85 cell saved from the successful 2026-10-17 run.
# This is a NEW V85 entry point. It does NOT replace the V86 launcher.
#
# Required Drive file:
# PhoenixTrav/phoenix_15_live/frozen_runs/
# PHOENIX15_V85_2026-10-17_20261017_102044/launcher_cell.py
#
# Database and model remain governed by the frozen cell's own settings.
# This wrapper does not write to the database, model, or GitHub.
# ================================================================

from pathlib import Path
import hashlib
import json
import runpy

try:
    from google.colab import drive
except ImportError as e:
    raise RuntimeError(
        "Öppna filen i Google Colab och kör den där."
    ) from e

drive.mount("/content/drive")

CHECKPOINT = Path(
    "/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/"
    "frozen_runs/PHOENIX15_V85_2026-10-17_20261017_102044"
)
CELL = CHECKPOINT / "launcher_cell.py"
MANIFEST = CHECKPOINT / "MANIFEST.json"

if not CELL.is_file():
    raise FileNotFoundError(
        "Den frysta V85-startcellen saknas: " + str(CELL)
    )
if not MANIFEST.is_file():
    raise FileNotFoundError(
        "MANIFEST.json saknas; kör inte en okontrollerad cell."
    )

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
expected = manifest.get("launcher_cell", {}).get("sha256")
actual = hashlib.sha256(CELL.read_bytes()).hexdigest()

if not expected:
    raise RuntimeError(
        "Manifestet innehåller ingen kontrollsumma för launcher_cell.py."
    )
if actual != expected:
    raise RuntimeError(
        "KONTROLLSUMMA FEL — startcellen kan ha ändrats. Avbryter."
    )

print("=" * 64)
print("PHOENIX 15 — V85 FROZEN LAUNCHER")
print("=" * 64)
print("Cell:", CELL)
print("SHA-256 verifierad:", actual)
print("Startar den sparade V85-cellen...")
print("Obs: körningen använder exakt koden i den frysta Drive-kopian.")
runpy.run_path(str(CELL), run_name="__main__")

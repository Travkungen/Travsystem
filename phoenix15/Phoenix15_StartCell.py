"""
PHOENIX 15 — STARTCELL
Permanent entry point for the Phoenix 15 pipeline.

Purpose:
- Verify the Phoenix 15 environment before execution.
- Load the frozen baseline model.
- Keep the pipeline entry point stable across new race days.
- New race-day data should be processed through the same pipeline,
  while completed race days are retained for later result analysis.

IMPORTANT:
- Do not modify the frozen baseline model from this start cell.
- Do not silently switch database paths or model versions.
- The Google Colab runtime should mount Google Drive before this cell.
"""

from pathlib import Path
import pickle
import pandas as pd

PHOENIX_ROOT = Path("/content/drive/MyDrive/PhoenixTrav/phoenix_15_live")
DB_PATH = Path("/content/drive/MyDrive/PhoenixTrav/phoenix_trav.db")
MODEL_PATH = PHOENIX_ROOT / "models" / "phoenix15_baseline_v1.pkl"

print("=" * 60)
print("PHOENIX 15 — STARTCELL")
print("=" * 60)
print("Phoenix root:", PHOENIX_ROOT)
print("Database:", DB_PATH)
print("Model:", MODEL_PATH)

# Environment checks
if not PHOENIX_ROOT.exists():
    raise RuntimeError(f"Phoenix 15-miljön saknas: {PHOENIX_ROOT}")

if not DB_PATH.exists():
    raise RuntimeError(f"Phoenix-databasen saknas: {DB_PATH}")

if not MODEL_PATH.exists():
    raise RuntimeError(f"Frozen Phoenix 15-modell saknas: {MODEL_PATH}")

# Load frozen baseline package without changing it.
with open(MODEL_PATH, "rb") as f:
    phoenix15_package = pickle.load(f)

phoenix15_model = phoenix15_package["model"]
phoenix15_features = phoenix15_package["features"]

print("MODEL: OK")
print("MODEL TYPE:", type(phoenix15_model).__name__)
print("FEATURES:", len(phoenix15_features))
print("TARGET:", phoenix15_package.get("target"))
print("TRAINING ROWS:", phoenix15_package.get("training_rows"))
print("TEST ROWS:", phoenix15_package.get("test_rows"))
print("DATE COLUMN:", phoenix15_package.get("date_column"))
print("=" * 60)
print("PHOENIX 15 — STARTCELL VERIFIED")
print("Next step: run the Phoenix 15 pipeline for the selected race day.")
print("=" * 60)

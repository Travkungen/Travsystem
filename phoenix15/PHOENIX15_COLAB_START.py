# PHOENIX 15 — COLAB STARTUP
# Purpose: deterministic startup for a NEW Google Colab session.
# Does not modify database or model files.

from pathlib import Path
import sys
import importlib.util

try:
    from google.colab import drive
    drive.mount('/content/drive', force_remount=False)
except Exception:
    print('Google Drive mount skipped (not running in Colab or already mounted).')

ROOT = Path('/content/drive/MyDrive/PhoenixTrav/phoenix_15_live')
RACE_AUTOMATION = ROOT / 'race_automation'
MODELS = ROOT / 'models'
CHECKPOINTS = ROOT / 'checkpoints'

print('=' * 60)
print('PHOENIX 15 — STARTUP')
print('=' * 60)
print('ROOT:', ROOT)
print('ROOT OK:', ROOT.exists())

required_modules = {
    'phoenix15_automation_orchestrator_v2.py': 'Phoenix automation orchestrator',
    'phoenix15_horse_history_v1.py': 'Horse History',
    'phoenix15_feature_build_v1.py': 'Feature Build',
    'phoenix15_model_engine_v1.py': 'Model Engine',
    'phoenix15_race_ranking_v1.py': 'Ranking Engine',
}

for filename, label in required_modules.items():
    path = RACE_AUTOMATION / filename
    print(('OK   ' if path.exists() else 'MISS '), label, '->', path)

model_path = MODELS / 'phoenix15_baseline_v2_1.pkl'
print('MODEL:', model_path)
print('MODEL OK:', model_path.exists())

# Load modules without requiring them to be installed as a package.
def load_module(name, path):
    if not path.exists():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module

history_mod = load_module(
    'phoenix15_horse_history_v1',
    RACE_AUTOMATION / 'phoenix15_horse_history_v1.py'
)
feature_mod = load_module(
    'phoenix15_feature_build_v1',
    RACE_AUTOMATION / 'phoenix15_feature_build_v1.py'
)
model_mod = load_module(
    'phoenix15_model_engine_v1',
    RACE_AUTOMATION / 'phoenix15_model_engine_v1.py'
)
ranking_mod = load_module(
    'phoenix15_race_ranking_v1',
    RACE_AUTOMATION / 'phoenix15_race_ranking_v1.py'
)

PhoenixHorseHistory = history_mod.PhoenixHorseHistory
PhoenixFeatureBuild = feature_mod.PhoenixFeatureBuild
PhoenixModelEngine = model_mod.PhoenixModelEngine
PhoenixRaceRanking = ranking_mod.PhoenixRaceRanking

print('HISTORY:', PhoenixHorseHistory.__name__)
print('FEATURE:', PhoenixFeatureBuild.__name__)
print('MODEL ENGINE:', PhoenixModelEngine.__name__)
print('RANKING:', PhoenixRaceRanking.__name__)

# Verified model feature contract.
MODEL_FEATURES = [
    'starts', 'wins', 'win_percent', 'top3', 'top3_percent',
    'last5_starts', 'last5_wins', 'last5_top3', 'last5_win_percent',
    'driver_starts', 'driver_wins', 'driver_win_percent',
    'driver_top3_percent', 'trainer_starts', 'trainer_wins',
    'trainer_win_percent', 'trainer_top3_percent',
    'hd_starts', 'hd_wins', 'hd_win_percent'
]

print('MODEL FEATURES:', len(MODEL_FEATURES))
print('=' * 60)
print('CHECKPOINT — STARTMILJÖ KLAR')
print('NÄSTA: RESULTATIMPORT / OMGÅNGSANALYS')
print('INGEN DB-ÄNDRING')
print('INGEN MODELLÄNDRING')
print('=' * 60)

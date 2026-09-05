from pathlib import Path
import importlib.util

ROOT = Path('/content/drive/MyDrive/PhoenixTrav/phoenix_15_live')
RESULT_ENGINE = ROOT / 'race_automation' / 'phoenix15_result_auto_finish_v1.py'


def load_result_engine():
    spec = importlib.util.spec_from_file_location('phoenix15_result_auto_finish_v1', RESULT_ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phoenix_result_auto_integration(date, game, prediction_df, result_df):
    engine = load_result_engine()
    return engine.phoenix_finish_full_round(date=date, game=game, prediction_df=prediction_df, result_df=result_df)

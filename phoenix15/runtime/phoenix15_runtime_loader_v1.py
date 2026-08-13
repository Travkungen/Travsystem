from pathlib import Path
import importlib.util

BOOTSTRAP = Path(
    "/content/drive/MyDrive/PhoenixTrav/"
    "bootstrap/phoenix_bootstrap.py"
)

MODULES = {
    "person_bridge": Path(
        "/content/drive/MyDrive/PhoenixTrav/"
        "phoenix_15_live/race_automation/"
        "phoenix15_person_bridge_v1.py"
    ),
    "horse_history": Path(
        "/content/drive/MyDrive/PhoenixTrav/"
        "phoenix_15_live/race_automation/"
        "phoenix15_horse_history_v1.py"
    ),
    "startlist": Path(
        "/content/drive/MyDrive/PhoenixTrav/"
        "phoenix_15_live/race_automation/"
        "phoenix15_race_startlist_v1.py"
    ),
    "feature_build": Path(
        "/content/drive/MyDrive/PhoenixTrav/"
        "phoenix_15_live/race_automation/"
        "phoenix15_feature_build_v1.py"
    ),
}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Kunde inte ladda: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def boot():
    if not BOOTSTRAP.exists():
        raise FileNotFoundError(BOOTSTRAP)

    bootstrap = _load(
        BOOTSTRAP,
        "phoenix15_central_bootstrap"
    )

    phoenix = bootstrap.boot()

    loaded = {
        name: _load(path, f"phoenix15_{name}")
        for name, path in MODULES.items()
        if path.exists()
    }

    return {
        "phoenix": phoenix,
        "conn": phoenix.conn,
        "modules": loaded,
    }

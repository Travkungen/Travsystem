# PHOENIX 15 — LIVE V64 RUNNER v1
# Verified 2026-08-17, Färjestad V64
# ATG Loader -> today_data -> Färjestad -> Extended races
# MASTER/database remains READ ONLY.

from importlib.util import spec_from_file_location, module_from_spec

AUTO = "/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/race_automation"


def _load(path, name):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_v64_farjestad():
    loader = _load(
        AUTO + "/phoenix15_atg_loader_v1.py",
        "phoenix15_atg_loader"
    ).PhoenixATGLoader()

    adapter = _load(
        AUTO + "/phoenix15_atg_extended_adapter_v2.py",
        "phoenix15_atg_extended"
    ).PhoenixATGExtendedAdapter()

    today_data = loader.load_today()

    tracks = today_data.get("tracks", [])
    farjestad = [
        t for t in tracks
        if "färjestad" in str(t.get("name", "")).lower()
        or "farjestad" in str(t.get("name", "")).lower()
    ]

    if not farjestad:
        raise RuntimeError("Färjestad hittades inte i today_data")

    races = farjestad[0].get("races", [])
    race_ids = [r["id"] for r in races if r.get("id")]

    extended = {
        race_id: adapter.fetch_extended(race_id)
        for race_id in race_ids
    }

    return today_data, farjestad[0], extended

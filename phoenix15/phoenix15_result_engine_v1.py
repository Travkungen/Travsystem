"""Phoenix 15 V64 result engine v1.1."""
from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pandas as pd

VERSION = "1.1"
GAME = "V64"


def _load_module(path: str, name: str):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Kunde inte ladda modul: {path}")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_v64_results(auto_dir: str):
    """Fetch only the current day's V64 through the existing Phoenix ATG chain."""
    auto = Path(auto_dir)
    loader_mod = _load_module(str(auto / "phoenix15_atg_loader_v1.py"), "phoenix15_v64_loader")
    adapter_mod = _load_module(str(auto / "phoenix15_atg_extended_adapter_v2.py"), "phoenix15_v64_adapter")
    loader = loader_mod.PhoenixATGLoader()
    adapter = adapter_mod.PhoenixATGExtendedAdapter()
    today_data = loader.load_today()

    rows = []
    for track in today_data.get("tracks", []):
        for race in track.get("races", []):
            race_id = race.get("id")
            if not race_id:
                continue
            raw = adapter.fetch_extended(race_id)
            # Only races explicitly identified as V64 are accepted.
            game_text = " ".join(str(raw.get(k, "")) for k in ("game", "gameName", "pool", "product", "type"))
            race_text = " ".join(str(race.get(k, "")) for k in ("game", "gameName", "pool", "product", "type"))
            if "v64" not in (game_text + " " + race_text).lower():
                continue
            for start in raw.get("starts", []):
                result = start.get("result") or {}
                horse = start.get("horse") or {}
                rows.append({
                    "date": race_id[:10],
                    "track": track.get("name", "Okänd bana"),
                    "game": GAME,
                    "race_id": race_id,
                    "number": start.get("number"),
                    "horse": horse.get("name"),
                    "placement": result.get("place"),
                    "finish_order": result.get("finishOrder"),
                    "status": start.get("status"),
                })

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("Ingen V64 hittades i dagens ATG-data")
    df["winner"] = df["placement"].eq(1)
    return today_data, df


def archive_v64_results(df: pd.DataFrame, results_dir: str):
    results = Path(results_dir)
    results.mkdir(parents=True, exist_ok=True)
    date_str = str(df["date"].dropna().iloc[0])
    csv_path = results / f"V64_RESULTAT_{date_str}.csv"
    json_path = results / f"V64_RESULTAT_{date_str}.json"
    if csv_path.exists() or json_path.exists():
        raise FileExistsError(f"V64-resultat finns redan för {date_str}; inget skrivs över.")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, ensure_ascii=False, indent=2, default=str)
    return csv_path, json_path

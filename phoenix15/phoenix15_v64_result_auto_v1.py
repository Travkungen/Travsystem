"""Phoenix 15 automatic V64 result importer."""
from __future__ import annotations
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pandas as pd

VERSION = "1.0"
GAME = "V64"

def _load(path, name):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Kunde inte ladda modul: {path}")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def fetch_v64_results(auto_dir: str):
    auto = Path(auto_dir)
    loader = _load(str(auto / "phoenix15_atg_loader_v1.py"), "phoenix15_v64_loader_auto").PhoenixATGLoader()
    adapter = _load(str(auto / "phoenix15_atg_extended_adapter_v2.py"), "phoenix15_v64_adapter_auto").PhoenixATGExtendedAdapter()
    today_data = loader.load_today()
    games = today_data.get("games", {}).get("V64", [])
    if not games:
        raise RuntimeError("Ingen V64 finns i dagens ATG-data")
    first_game_id = str(games[0].get("id", ""))
    if not first_game_id.startswith("V64_"):
        raise RuntimeError(f"Oväntat V64-id: {first_game_id}")
    first_race_id = first_game_id[4:]
    parts = first_race_id.rsplit("_", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        raise RuntimeError(f"Kunde inte tolka V64 race-id: {first_race_id}")
    race_prefix = parts[0]
    first_race_no = int(parts[1])
    race_ids = [f"{race_prefix}_{first_race_no + i}" for i in range(6)]
    rows = []
    for v64_no, race_id in enumerate(race_ids, 1):
        raw = adapter.fetch_extended(race_id)
        for start in raw.get("starts", []):
            result = start.get("result") or {}
            horse = start.get("horse") or {}
            rows.append({"date": str(today_data.get("date", race_id[:10])), "game": GAME, "v64": v64_no, "race_id": race_id, "number": start.get("number"), "horse": horse.get("name"), "placement": result.get("place"), "finish_order": result.get("finishOrder"), "status": start.get("status")})
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("V64 hittades men inga resultatstarter hämtades")
    df["winner"] = df["placement"].eq(1)
    return today_data, df

def archive_v64_results(df: pd.DataFrame, results_dir: str):
    results = Path(results_dir)
    results.mkdir(parents=True, exist_ok=True)
    date_str = str(df["date"].dropna().iloc[0])
    csv_path = results / f"V64_RESULTAT_{date_str}.csv"
    json_path = results / f"V64_RESULTAT_{date_str}.json"
    if csv_path.exists() or json_path.exists():
        return csv_path, json_path, False
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, ensure_ascii=False, indent=2, default=str)
    return csv_path, json_path, True

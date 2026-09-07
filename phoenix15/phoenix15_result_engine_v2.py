"""Phoenix 15 generic result engine for V64/V85/V86."""
from __future__ import annotations
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pandas as pd

VERSION = "2.0"
SUPPORTED_GAMES = {"V64": 6, "V85": 8, "V86": 8}

def _load(path, name):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Kunde inte ladda modul: {path}")
    mod = module_from_spec(spec); spec.loader.exec_module(mod); return mod

def _race_ids(today_data, game):
    games = today_data.get("games", {}).get(game, [])
    if not games: raise RuntimeError(f"Ingen {game} finns i dagens ATG-data")
    first = str(games[0].get("id", ""))
    prefix = f"{game}_"
    if not first.startswith(prefix): raise RuntimeError(f"Oväntat {game}-id: {first}")
    first_race = first[len(prefix):]
    p = first_race.rsplit("_", 1)
    if len(p) != 2 or not p[1].isdigit(): raise RuntimeError(f"Kunde inte tolka {game}-id: {first_race}")
    base, no = p[0], int(p[1])
    return [f"{base}_{no+i}" for i in range(SUPPORTED_GAMES[game])]

def fetch_game(auto_dir: str, game: str):
    game = str(game).upper()
    if game not in SUPPORTED_GAMES: raise ValueError(f"Stöder: {', '.join(SUPPORTED_GAMES)}")
    auto = Path(auto_dir)
    loader = _load(str(auto/"phoenix15_atg_loader_v1.py"), f"phoenix15_loader_{game}").PhoenixATGLoader()
    adapter = _load(str(auto/"phoenix15_atg_extended_adapter_v2.py"), f"phoenix15_adapter_{game}").PhoenixATGExtendedAdapter()
    today_data = loader.load_today()
    rows=[]
    for no, race_id in enumerate(_race_ids(today_data, game), 1):
        raw = adapter.fetch_extended(race_id)
        for start in raw.get("starts", []):
            result = start.get("result") or {}; horse = start.get("horse") or {}
            rows.append({"date": str(today_data.get("date", race_id[:10])), "track": None,
                         "game": game, "game_race": no, "race_id": race_id,
                         "number": start.get("number"), "horse": horse.get("name"),
                         "placement": result.get("place"), "finish_order": result.get("finishOrder"),
                         "status": start.get("status")})
    df=pd.DataFrame(rows)
    if df.empty: raise RuntimeError(f"{game} hittades men inga starter hämtades")
    df["winner"]=df["placement"].eq(1)
    return today_data, df

def fetch_all(auto_dir: str, games=("V64","V85","V86")):
    out={}
    for game in games:
        try: out[game]=fetch_game(auto_dir, game)
        except RuntimeError as e:
            if "Ingen" in str(e): out[game]=(None,pd.DataFrame())
            else: raise
    return out

def archive_game(df: pd.DataFrame, results_dir: str):
    if df.empty: raise ValueError("Tom resultatdata")
    results=Path(results_dir); results.mkdir(parents=True, exist_ok=True)
    date=str(df["date"].dropna().iloc[0]); game=str(df["game"].iloc[0])
    csv=results/f"{game}_RESULTAT_{date}.csv"; js=results/f"{game}_RESULTAT_{date}.json"
    if csv.exists() or js.exists(): return csv,js,False
    df.to_csv(csv,index=False,encoding="utf-8-sig")
    with js.open("w",encoding="utf-8") as f: json.dump(df.to_dict("records"),f,ensure_ascii=False,indent=2,default=str)
    return csv,js,True

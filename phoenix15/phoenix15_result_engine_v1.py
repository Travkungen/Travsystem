"""Phoenix 15 result engine v1.

Purpose:
    Fetch the current day's ATG race results through the existing Phoenix
    loader + extended adapter and archive the complete daily result set.

Rules:
    - Does not modify Master, Frozen, model, or SQLite.
    - Uses the existing Phoenix ATG loader/extended adapter.
    - Archives CSV + JSON with date-based filenames.
"""

from __future__ import annotations

import json
import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd

VERSION = "1.0"


def _load_module(path: str, name: str):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Kunde inte ladda modul: {path}")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_results(auto_dir: str):
    """Fetch all current-day race results via Phoenix's existing ATG chain."""
    auto = Path(auto_dir)

    loader_mod = _load_module(
        str(auto / "phoenix15_atg_loader_v1.py"),
        "phoenix15_result_loader",
    )
    adapter_mod = _load_module(
        str(auto / "phoenix15_atg_extended_adapter_v2.py"),
        "phoenix15_result_adapter",
    )

    loader = loader_mod.PhoenixATGLoader()
    adapter = adapter_mod.PhoenixATGExtendedAdapter()
    today_data = loader.load_today()

    rows = []

    for track in today_data.get("tracks", []):
        track_name = track.get("name", "Okänd bana")

        for race in track.get("races", []):
            race_id = race.get("id")
            if not race_id:
                continue

            raw = adapter.fetch_extended(race_id)

            for start in raw.get("starts", []):
                result = start.get("result") or {}
                horse = start.get("horse") or {}

                rows.append({
                    "date": race_id[:10] if len(race_id) >= 10 else None,
                    "track": track_name,
                    "race_id": race_id,
                    "number": start.get("number"),
                    "horse": horse.get("name"),
                    "placement": result.get("place"),
                    "finish_order": result.get("finishOrder"),
                    "status": start.get("status"),
                })

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("ATG-resultat gav inga starter")

    df["winner"] = df["placement"].eq(1)
    return today_data, df


def archive_results(df: pd.DataFrame, results_dir: str):
    """Archive daily results without overwriting an existing file."""
    results = Path(results_dir)
    results.mkdir(parents=True, exist_ok=True)

    date_str = str(df["date"].dropna().iloc[0])
    csv_path = results / f"ATG_RESULTAT_{date_str}.csv"
    json_path = results / f"ATG_RESULTAT_{date_str}.json"

    if csv_path.exists() or json_path.exists():
        raise FileExistsError(
            f"Resultatarkiv finns redan för {date_str}; ingen fil skrivs över."
        )

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            df.to_dict("records"),
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    return csv_path, json_path

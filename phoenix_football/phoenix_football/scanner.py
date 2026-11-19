from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

REQUIRED = {
    "event_id", "sport", "league", "commence_time", "home_team", "away_team",
    "bookmaker", "market", "selection", "line", "odds", "captured_at",
}


def read_odds(path: str | Path) -> list[dict[str, Any]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV saknar kolumner: {', '.join(sorted(missing))}")
        rows = []
        for row_number, row in enumerate(reader, start=2):
            try:
                odds = float(row["odds"])
            except (TypeError, ValueError):
                raise ValueError(f"Ogiltigt odds på CSV-rad {row_number}")
            if odds <= 1:
                raise ValueError(f"Odds måste vara större än 1 (rad {row_number})")
            row["odds"] = odds
            row["line"] = (row.get("line") or "").strip()
            for key in REQUIRED - {"odds"}:
                row[key] = (row.get(key) or "").strip()
            rows.append(row)
    return rows


def scan(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Each bookmaker's complete outcome set is normalized to remove overround.
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["event_id"], row["market"], row["line"], row["bookmaker"])
        groups[key].append(row)

    fair_by_selection: dict[tuple, list[float]] = defaultdict(list)
    overround_by_group: dict[tuple, float] = {}
    for key, outcomes in groups.items():
        # Duplicate selections within a book/market/line are ambiguous; skip group.
        selections = [r["selection"] for r in outcomes]
        if len(selections) < 2 or len(set(selections)) != len(selections):
            continue
        implied = [1.0 / r["odds"] for r in outcomes]
        total = sum(implied)
        if total <= 0:
            continue
        overround_by_group[key] = total - 1.0
        for row, probability in zip(outcomes, implied):
            fair_key = (row["event_id"], row["market"], row["line"], row["selection"])
            fair_by_selection[fair_key].append(probability / total)

    best: dict[tuple, dict[str, Any]] = {}
    for row in rows:
        key = (row["event_id"], row["market"], row["line"], row["selection"])
        if key not in best or row["odds"] > best[key]["best_odds"]:
            best[key] = {
                "event_id": row["event_id"], "sport": row["sport"],
                "league": row["league"], "commence_time": row["commence_time"],
                "home_team": row["home_team"], "away_team": row["away_team"],
                "market": row["market"], "selection": row["selection"],
                "line": row["line"], "best_odds": row["odds"],
                "best_bookmaker": row["bookmaker"], "captured_at": row["captured_at"],
            }

    output = []
    for key, item in best.items():
        probabilities = fair_by_selection.get(key, [])
        fair_probability = mean(probabilities) if probabilities else None
        fair_odds = 1.0 / fair_probability if fair_probability else None
        price_edge = ((item["best_odds"] / fair_odds) - 1.0) * 100 if fair_odds else None
        item.update({
            "market_fair_probability": round(fair_probability, 6) if fair_probability is not None else "",
            "market_fair_odds": round(fair_odds, 3) if fair_odds is not None else "",
            "price_edge_vs_consensus_pct": round(price_edge, 2) if price_edge is not None else "",
            "model_probability": "",
            "expected_value_pct": "",
            "classification": "PRICE_COMPARISON_ONLY" if fair_probability is not None else "INSUFFICIENT_MARKET_DATA",
        })
        output.append(item)

    output.sort(
        key=lambda r: r["price_edge_vs_consensus_pct"]
        if isinstance(r["price_edge_vs_consensus_pct"], (int, float)) else -999,
        reverse=True,
    )
    return output


def write_report(rows: list[dict[str, Any]], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Football multi-market odds scanner")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("scan", help="Scan an odds CSV and rank best prices")
    command.add_argument("--input", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = read_odds(args.input)
    report = scan(rows)
    write_report(report, args.output)
    print(f"PHOENIX FOOTBALL SCAN COMPLETE")
    print(f"Odds rows: {len(rows)} | selections: {len(report)}")
    print(f"Report: {args.output}")
    print("NOTE: price edge vs consensus is not proof of positive EV.")


if __name__ == "__main__":
    main()

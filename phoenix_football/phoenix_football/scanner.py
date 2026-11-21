from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phoenix_football.odds_api import FEATURED_MARKETS, TheOddsAPI, normalize_event

REQUIRED = {
    "event_id", "sport", "league", "commence_time", "home_team", "away_team",
    "bookmaker", "market", "selection", "line", "odds", "captured_at",
}


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"Ogiltig tidsstämpel: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
            if not math.isfinite(odds) or odds <= 1:
                raise ValueError(f"Odds måste vara ett ändligt tal större än 1 (rad {row_number})")
            row["odds"] = odds
            row["line"] = (row.get("line") or "").strip()
            for key in REQUIRED - {"odds"}:
                row[key] = (row.get(key) or "").strip()
            for key in ("event_id", "sport", "commence_time", "home_team", "away_team",
                        "bookmaker", "market", "selection", "captured_at"):
                if not row[key]:
                    raise ValueError(f"Tomt obligatoriskt fält '{key}' på CSV-rad {row_number}")
            _timestamp(row["commence_time"])
            _timestamp(row["captured_at"])
            rows.append(row)
    return rows


def _latest_bookmaker_snapshots(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the latest snapshot and collapse duplicate selection rows."""
    snapshots: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["event_id"], row["market"], row["line"], row["bookmaker"])
        snapshots[key].append(row)

    latest_rows: list[dict[str, Any]] = []
    for snapshot_rows in snapshots.values():
        latest_time = max(_timestamp(row["captured_at"]) for row in snapshot_rows)
        deduplicated: dict[str, dict[str, Any]] = {}
        for row in snapshot_rows:
            if _timestamp(row["captured_at"]) != latest_time:
                continue
            previous = deduplicated.get(row["selection"])
            # Duplicate provider rows are collapsed conservatively to one quote.
            if previous is None or row["odds"] > previous["odds"]:
                deduplicated[row["selection"]] = row
        latest_rows.extend(deduplicated.values())
    return latest_rows


def _is_complete_outcome_set(market: str, outcomes: list[dict[str, Any]]) -> bool:
    """Only calculate market consensus when the bookmaker supplied every expected outcome."""
    selections = {str(row["selection"]).strip().casefold() for row in outcomes}
    if market == "h2h":
        first = outcomes[0]
        expected = {
            str(first["home_team"]).strip().casefold(),
            str(first["away_team"]).strip().casefold(),
            "draw",
        }
        return len(expected) == 3 and selections == expected
    if market == "totals":
        return selections == {"over", "under"}
    if market == "spreads":
        # A spread is complete only when both sides of the same line are present.
        return len(outcomes) == 2 and len(selections) == 2
    # Unknown markets are not assumed complete: their outcome space varies by market.
    return False


def scan(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_rows = _latest_bookmaker_snapshots(rows)

    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in current_rows:
        key = (row["event_id"], row["market"], row["line"], row["bookmaker"])
        groups[key].append(row)

    fair_by_selection: dict[tuple, list[float]] = defaultdict(list)
    books_by_market: dict[tuple, set[str]] = defaultdict(set)
    for market_key, outcomes in groups.items():
        if not _is_complete_outcome_set(market_key[1], outcomes):
            continue
        implied = [1.0 / r["odds"] for r in outcomes]
        total = sum(implied)
        if total <= 0:
            continue
        for row, probability in zip(outcomes, implied):
            fair_key = (*market_key[:3], row["selection"])
            fair_by_selection[fair_key].append(probability / total)
            books_by_market[market_key[:3]].add(row["bookmaker"])

    best: dict[tuple, dict[str, Any]] = {}
    for row in current_rows:
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
        market_key = key[:3]
        probabilities = fair_by_selection.get(key, [])
        bookmaker_count = len(books_by_market.get(market_key, set()))
        fair_probability = (
            sum(probabilities) / len(probabilities)
            if probabilities and bookmaker_count >= 2 else None
        )
        fair_odds = 1.0 / fair_probability if fair_probability else None
        price_edge = ((item["best_odds"] / fair_odds) - 1.0) * 100 if fair_odds else None
        item.update({
            "complete_bookmakers": bookmaker_count,
            "market_fair_probability": round(fair_probability, 6) if fair_probability is not None else "",
            "market_fair_odds": round(fair_odds, 3) if fair_odds else "",
            "price_edge_vs_consensus_pct": round(price_edge, 2) if price_edge is not None else "",
            "model_probability": "",
            "expected_value_pct": "",
            "classification": "PRICE_COMPARISON_ONLY" if fair_probability is not None else "INSUFFICIENT_MARKET_DATA",
        })
        output.append(item)

    safety_order = sorted(
        (r for r in output if isinstance(r["market_fair_probability"], (int, float))),
        key=lambda r: r["market_fair_probability"],
        reverse=True,
    )
    for rank, item in enumerate(safety_order, start=1):
        item["safety_rank"] = rank
    for item in output:
        item.setdefault("safety_rank", "")

    value_order = sorted(
        (r for r in output if isinstance(r["price_edge_vs_consensus_pct"], (int, float))),
        key=lambda r: r["price_edge_vs_consensus_pct"],
        reverse=True,
    )
    for rank, item in enumerate(value_order, start=1):
        item["value_rank"] = rank
    for item in output:
        item.setdefault("value_rank", "")

    output.sort(
        key=lambda r: r["value_rank"] if isinstance(r["value_rank"], int) else 10**9
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


def fetch_daily(output_path: str, raw_path: str, include_extra_markets: bool = False) -> tuple[int, int, dict[str, str]]:
    api = TheOddsAPI()
    events_by_id: dict[str, dict[str, Any]] = {}
    now = datetime.now(timezone.utc)

    sports = api.soccer_sports()
    for sport in sports:
        sport_key = sport["key"]
        events = api.events_with_featured_odds(sport_key)
        for event in events:
            start = _timestamp(event["commence_time"])
            if start <= now:
                continue  # pre-match only; never mix in-play prices into the daily prematch report

            event_id = str(event.get("id", ""))
            combined = events_by_id.setdefault(event_id, dict(event))
            if include_extra_markets and event_id:
                market_map = api.event_market_keys(sport_key, event_id)
                extra = sorted({
                    market for markets in market_map.values() for market in markets
                    if market and market not in FEATURED_MARKETS
                })
                if extra:
                    detail = api.event_odds(sport_key, event_id, extra)
                    if detail:
                        # Preserve fixture metadata even if the detail response omits it.
                        combined.update({k: v for k, v in detail.items() if k != "bookmakers"})
                        by_book = {
                            b.get("key"): b for b in combined.get("bookmakers", [])
                        }
                        for bookmaker in detail.get("bookmakers", []):
                            book_key = bookmaker.get("key")
                            target = by_book.setdefault(book_key, dict(bookmaker))
                            if target is not bookmaker:
                                markets_by_key = {
                                    m.get("key"): m for m in target.get("markets", [])
                                }
                                for market in bookmaker.get("markets", []):
                                    markets_by_key[market.get("key")] = market
                                target["markets"] = list(markets_by_key.values())
                        combined["bookmakers"] = list(by_book.values())

    captured_at = datetime.now(timezone.utc).isoformat()
    normalized: list[dict[str, Any]] = []
    for event in events_by_id.values():
        normalized.extend(normalize_event(event, captured_at))

    coverage: dict[str, int] = defaultdict(int)
    for row in normalized:
        coverage[row["market"]] += 1

    raw_file = Path(raw_path)
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(json.dumps({
        "captured_at": captured_at,
        "sports": [s.get("key") for s in sports],
        "events": list(events_by_id.values()),
        "api_usage": api.last_usage,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(normalized, output_path)
    return len(events_by_id), len(normalized), dict(coverage)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Football multi-market odds scanner")
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("scan", help="Scan an odds CSV and rank best prices")
    command.add_argument("--input", required=True)
    command.add_argument("--output", required=True)

    fetch = sub.add_parser("fetch", help="Fetch current prematch soccer odds from The Odds API")
    fetch.add_argument("--output", default="reports/daily_odds.csv")
    fetch.add_argument("--raw", default="data/raw/latest_odds.json")
    fetch.add_argument("--include-extra-markets", action="store_true",
                       help="Discover and fetch non-featured markets per event; can use additional API quota")

    args = parser.parse_args()
    if args.command == "scan":
        rows = read_odds(args.input)
        report = scan(rows)
        write_report(report, args.output)
        print("PHOENIX FOOTBALL SCAN COMPLETE")
        print(f"Odds rows: {len(rows)} | selections: {len(report)}")
        print(f"Report: {args.output}")
        print("NOTE: price edge vs consensus is not proof of positive EV.")
    else:
        event_count, row_count, coverage = fetch_daily(args.output, args.raw, args.include_extra_markets)
        print("PHOENIX FOOTBALL DAILY FETCH COMPLETE")
        print(f"Events fetched: {event_count} | odds rows: {row_count}")
        print(f"Markets found: {', '.join(sorted(coverage)) if coverage else 'none'}")
        print(f"Raw snapshot: {args.raw}")
        print(f"Daily odds: {args.output}")
        print("Extra markets enabled:", args.include_extra_markets)


if __name__ == "__main__":
    main()

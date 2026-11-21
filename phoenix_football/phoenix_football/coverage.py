from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from phoenix_football.scanner import _timestamp, read_odds

EXPECTED_MARKETS = ("h2h", "totals", "spreads", "alternate_totals", "team_totals",
                    "draw_no_bet", "btts", "double_chance", "corners", "cards",
                    "shots", "shots_on_target", "player_shots", "player_goals")


def build_coverage(rows: list[dict[str, Any]], now: datetime | None = None,
                   stale_after_hours: float = 6.0) -> list[dict[str, Any]]:
    """Summarize only observed provider data; expected market names are never fabricated."""
    if stale_after_hours <= 0:
        raise ValueError("stale_after_hours måste vara större än noll")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["sport"], row["league"], row["market"], row["bookmaker"])
        groups[key].append(row)

    report = []
    for (sport, league, market, bookmaker), items in sorted(groups.items()):
        events = {item["event_id"] for item in items}
        latest = max(_timestamp(item["captured_at"]) for item in items)
        kickoff_times = [_timestamp(item["commence_time"]) for item in items]
        pre_match_events = sum(kickoff > current for kickoff in kickoff_times)
        report.append({
            "sport": sport,
            "league": league,
            "market": market,
            "bookmaker": bookmaker,
            "events": len(events),
            "selections": len(items),
            "latest_capture_utc": latest.isoformat(),
            "age_hours": round(max(0.0, (current - latest).total_seconds() / 3600), 2),
            "stale": (current - latest) > timedelta(hours=stale_after_hours),
            "upcoming_event_rows": pre_match_events,
        })
    return report


def write_coverage(rows: list[dict[str, Any]], output: str | Path) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["sport", "league", "market", "bookmaker", "events", "selections",
              "latest_capture_utc", "age_hours", "stale", "upcoming_event_rows"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phoenix Football market coverage report")
    parser.add_argument("--input", default="reports/daily_odds.csv")
    parser.add_argument("--output", default="reports/market_coverage.csv")
    parser.add_argument("--stale-after-hours", type=float, default=6.0)
    args = parser.parse_args()
    rows = read_odds(args.input)
    report = build_coverage(rows, stale_after_hours=args.stale_after_hours)
    write_coverage(report, args.output)
    print("PHOENIX FOOTBALL COVERAGE COMPLETE")
    print(f"Observed combinations: {len(report)} | input rows: {len(rows)}")
    print(f"Report: {args.output}")
    print("Only markets present in the source data are reported; no missing market is inferred.")


if __name__ == "__main__":
    main()

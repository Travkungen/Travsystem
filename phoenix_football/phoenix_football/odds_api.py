from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE_URL = "https://api.the-odds-api.com/v4"
DEFAULT_REGIONS = "eu,uk"
FEATURED_MARKETS = ("h2h", "totals")


class OddsAPIError(RuntimeError):
    pass


class TheOddsAPI:
    """Small stdlib-only adapter for The Odds API v4."""

    def __init__(self, api_key: str | None = None, regions: str = DEFAULT_REGIONS, timeout: int = 25):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise OddsAPIError("ODDS_API_KEY saknas. Lägg nyckeln som miljövariabel; dela den inte i Git eller chatten.")
        self.regions = regions
        self.timeout = timeout
        self.last_usage: dict[str, str] = {}

    def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        query = dict(params or {})
        query["apiKey"] = self.api_key
        url = f"{BASE_URL}{path}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "PhoenixFootball/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                for header in ("x-requests-remaining", "x-requests-used", "x-requests-last"):
                    if response.headers.get(header) is not None:
                        self.last_usage[header] = response.headers[header]
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise OddsAPIError(f"The Odds API HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OddsAPIError(f"Kunde inte nå The Odds API: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise OddsAPIError("Oddsleverantören returnerade ogiltig JSON.") from exc

    def soccer_sports(self) -> list[dict[str, Any]]:
        sports = self._get("/sports", {"all": "false"})
        return [s for s in sports if str(s.get("key", "")).startswith("soccer_") and s.get("active")]

    def events_with_featured_odds(self, sport_key: str) -> list[dict[str, Any]]:
        return self._get(
            f"/sports/{urllib.parse.quote(sport_key, safe='')}/odds",
            {"regions": self.regions, "markets": ",".join(FEATURED_MARKETS), "oddsFormat": "decimal", "dateFormat": "iso"},
        )

    def event_market_keys(self, sport_key: str, event_id: str) -> dict[str, list[str]]:
        data = self._get(
            f"/sports/{urllib.parse.quote(sport_key, safe='')}/events/{urllib.parse.quote(event_id, safe='')}/markets",
            {"regions": self.regions, "dateFormat": "iso"},
        )
        return {
            bookmaker.get("key", ""): [m.get("key", "") for m in bookmaker.get("markets", []) if m.get("key")]
            for bookmaker in data.get("bookmakers", [])
        }

    def event_odds(self, sport_key: str, event_id: str, markets: list[str]) -> dict[str, Any]:
        if not markets:
            return {}
        return self._get(
            f"/sports/{urllib.parse.quote(sport_key, safe='')}/events/{urllib.parse.quote(event_id, safe='')}/odds",
            {"regions": self.regions, "markets": ",".join(sorted(set(markets))), "oddsFormat": "decimal", "dateFormat": "iso"},
        )


def normalize_event(event: dict[str, Any], captured_at: str | None = None) -> list[dict[str, Any]]:
    """Flatten one Odds API event response to the Phoenix CSV contract."""
    captured = captured_at or datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for bookmaker in event.get("bookmakers", []):
        bookmaker_name = bookmaker.get("title") or bookmaker.get("key") or "unknown"
        for market in bookmaker.get("markets", []):
            market_key = market.get("key", "unknown")
            updated = market.get("last_update") or captured
            for outcome in market.get("outcomes", []):
                selection = outcome.get("name", "")
                description = outcome.get("description")
                if description:
                    selection = f"{description} - {selection}"
                rows.append({
                    "event_id": event.get("id", ""),
                    "sport": event.get("sport_key", "soccer"),
                    "league": event.get("sport_title", ""),
                    "commence_time": event.get("commence_time", ""),
                    "home_team": event.get("home_team", ""),
                    "away_team": event.get("away_team", ""),
                    "bookmaker": bookmaker_name,
                    "market": market_key,
                    "selection": selection,
                    "line": str(outcome.get("point", "")) if outcome.get("point") is not None else "",
                    "odds": float(outcome["price"]),
                    "captured_at": updated,
                })
    return rows

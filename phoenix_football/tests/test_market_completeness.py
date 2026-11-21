import unittest

from phoenix_football.scanner import scan


def make_row(bookmaker, selection, odds):
    return {
        "event_id": "match-1",
        "sport": "soccer_epl",
        "league": "Premier League",
        "commence_time": "2026-12-01T19:00:00Z",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "bookmaker": bookmaker,
        "market": "h2h",
        "selection": selection,
        "line": "",
        "odds": odds,
        "captured_at": "2026-11-21T17:00:00Z",
    }


class MarketCompletenessTests(unittest.TestCase):
    def test_incomplete_1x2_without_draw_is_not_used_for_consensus(self):
        rows = [
            make_row("Book A", "Arsenal", 2.0),
            make_row("Book A", "Chelsea", 4.0),
        ]
        report = scan(rows)
        self.assertTrue(report)
        self.assertTrue(all(item["market_fair_probability"] == "" for item in report))
        self.assertTrue(all(item["classification"] == "INSUFFICIENT_MARKET_DATA" for item in report))

    def test_complete_1x2_outcome_set_can_contribute_to_consensus(self):
        rows = [
            make_row("Book A", "Arsenal", 2.0),
            make_row("Book A", "Draw", 3.5),
            make_row("Book A", "Chelsea", 4.0),
            make_row("Book B", "Arsenal", 2.1),
            make_row("Book B", "Draw", 3.4),
            make_row("Book B", "Chelsea", 3.9),
        ]
        report = scan(rows)
        self.assertTrue(report)
        self.assertTrue(all(item["market_fair_probability"] != "" for item in report))
        self.assertTrue(all(item["complete_bookmakers"] == 2 for item in report))


if __name__ == "__main__":
    unittest.main()

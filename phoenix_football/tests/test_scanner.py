import unittest

from phoenix_football.odds_api import normalize_event
from phoenix_football.scanner import scan


class OddsAdapterTests(unittest.TestCase):
    def test_normalize_event_flattens_markets_and_keeps_lines(self):
        event = {
            "id": "evt-1", "sport_key": "soccer_epl", "sport_title": "EPL",
            "commence_time": "2026-11-20T18:00:00Z", "home_team": "A", "away_team": "B",
            "bookmakers": [{
                "key": "book", "title": "Bookmaker",
                "markets": [{
                    "key": "totals", "last_update": "2026-11-19T10:00:00Z",
                    "outcomes": [
                        {"name": "Over", "price": 1.91, "point": 2.5},
                        {"name": "Under", "price": 1.95, "point": 2.5},
                    ],
                }],
            }],
        }
        rows = normalize_event(event, "2026-11-19T10:01:00Z")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["event_id"], "evt-1")
        self.assertEqual(rows[0]["market"], "totals")
        self.assertEqual(rows[0]["line"], "2.5")
        self.assertEqual(rows[0]["captured_at"], "2026-11-19T10:00:00Z")


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"event_id":"e1","sport":"soccer","league":"L","commence_time":"2026-11-20T18:00:00+01:00","home_team":"A","away_team":"B","bookmaker":"X","market":"h2h","selection":"Home","line":"","odds":2.1,"captured_at":"2026-11-19T10:00:00+01:00"},
            {"event_id":"e1","sport":"soccer","league":"L","commence_time":"2026-11-20T18:00:00+01:00","home_team":"A","away_team":"B","bookmaker":"X","market":"h2h","selection":"Draw","line":"","odds":3.2,"captured_at":"2026-11-19T10:00:00+01:00"},
            {"event_id":"e1","sport":"soccer","league":"L","commence_time":"2026-11-20T18:00:00+01:00","home_team":"A","away_team":"B","bookmaker":"X","market":"h2h","selection":"Away","line":"","odds":3.5,"captured_at":"2026-11-19T10:00:00+01:00"},
        ]

    def test_best_odds_and_market_probability(self):
        result = scan(self.rows)
        self.assertEqual(len(result), 3)
        home = next(r for r in result if r["selection"] == "Home")
        self.assertAlmostEqual(home["best_odds"], 2.1)
        self.assertEqual(home["market_fair_probability"], "")
        self.assertEqual(home["classification"], "INSUFFICIENT_MARKET_DATA")
        self.assertEqual(home["expected_value_pct"], "")

    def test_market_without_complete_outcomes_is_not_valued(self):
        result = scan(self.rows[:1])
        self.assertEqual(result[0]["classification"], "INSUFFICIENT_MARKET_DATA")
        self.assertEqual(result[0]["market_fair_probability"], "")

    def test_stale_high_price_cannot_win_best_price(self):
        old = []
        for row in self.rows:
            copy = dict(row)
            copy["captured_at"] = "2026-11-18T10:00:00+01:00"
            copy["odds"] = 9.0 if copy["selection"] == "Home" else copy["odds"]
            old.append(copy)
        result = scan(old + self.rows)
        home = next(r for r in result if r["selection"] == "Home")
        self.assertEqual(home["best_odds"], 2.1)
        self.assertEqual(home["captured_at"], "2026-11-19T10:00:00+01:00")

    def test_latest_snapshot_is_used_for_market_consensus(self):
        older = []
        for row in self.rows:
            copy = dict(row)
            copy["captured_at"] = "2026-11-18T10:00:00+01:00"
            copy["odds"] = 1.5
            older.append(copy)
        second_book = []
        for row in self.rows:
            copy = dict(row)
            copy["bookmaker"] = "Y"
            copy["odds"] = row["odds"] * 1.02
            second_book.append(copy)
        result = scan(older + self.rows + second_book)
        home = next(r for r in result if r["selection"] == "Home")
        expected = (1 / 2.1) / ((1 / 2.1) + (1 / 3.2) + (1 / 3.5))
        self.assertAlmostEqual(home["market_fair_probability"], round(expected, 6))
        self.assertEqual(home["complete_bookmakers"], 2)

    def test_duplicate_selection_rows_are_collapsed(self):
        duplicate = dict(self.rows[0])
        duplicate["odds"] = 2.2
        result = scan(self.rows + [duplicate])
        home = next(r for r in result if r["selection"] == "Home")
        self.assertEqual(home["best_odds"], 2.2)
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()

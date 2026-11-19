import unittest

from phoenix_football.scanner import scan


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
        self.assertTrue(home["market_fair_probability"])
        self.assertEqual(home["classification"], "PRICE_COMPARISON_ONLY")
        self.assertEqual(home["expected_value_pct"], "")

    def test_market_without_complete_outcomes_is_not_valued(self):
        result = scan(self.rows[:1])
        self.assertEqual(result[0]["classification"], "INSUFFICIENT_MARKET_DATA")
        self.assertEqual(result[0]["market_fair_probability"], "")


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime, timezone

from phoenix_football.coverage import build_coverage


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"sport": "soccer_epl", "league": "Premier League", "market": "h2h",
             "bookmaker": "Book A", "event_id": "e1", "selection": "Home",
             "captured_at": "2026-11-19T10:00:00Z", "commence_time": "2026-11-20T18:00:00Z"},
            {"sport": "soccer_epl", "league": "Premier League", "market": "h2h",
             "bookmaker": "Book A", "event_id": "e1", "selection": "Draw",
             "captured_at": "2026-11-19T10:00:00Z", "commence_time": "2026-11-20T18:00:00Z"},
            {"sport": "soccer_epl", "league": "Premier League", "market": "totals",
             "bookmaker": "Book B", "event_id": "e2", "selection": "Over",
             "captured_at": "2026-11-19T01:00:00Z", "commence_time": "2026-11-20T18:00:00Z"},
        ]

    def test_groups_observed_market_and_bookmaker_coverage(self):
        now = datetime(2026, 11, 19, 11, tzinfo=timezone.utc)
        report = build_coverage(self.rows, now=now, stale_after_hours=6)
        self.assertEqual(len(report), 2)
        home_market = next(r for r in report if r["market"] == "h2h")
        self.assertEqual(home_market["events"], 1)
        self.assertEqual(home_market["selections"], 2)
        self.assertEqual(home_market["bookmaker"], "Book A")
        self.assertFalse(home_market["stale"])
        totals = next(r for r in report if r["market"] == "totals")
        self.assertTrue(totals["stale"])

    def test_rejects_non_positive_stale_threshold(self):
        with self.assertRaisesRegex(ValueError, "större än noll"):
            build_coverage(self.rows, stale_after_hours=0)


if __name__ == "__main__":
    unittest.main()

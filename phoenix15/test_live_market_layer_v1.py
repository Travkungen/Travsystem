"""Unit tests for the read-only Phoenix 15 live market layer."""
import unittest

import pandas as pd

from phoenix15.phoenix15_live_market_layer_v1 import (
    attach_market,
    normalize_atg_odds,
    parse_race_market,
    validate_market,
)


class Response:
    def __init__(self, payload):
        self._payload = payload
    def raise_for_status(self):
        return None
    def json(self):
        return self._payload


class MarketLayerTests(unittest.TestCase):
    def test_normalize_atg_odds(self):
        self.assertEqual(normalize_atg_odds(4050), 4.05)
        self.assertIsNone(normalize_atg_odds(0))
        self.assertIsNone(normalize_atg_odds(9999))
        self.assertIsNone(normalize_atg_odds("not odds"))

    def test_parse_race_market_uses_matching_race(self):
        payload = {"races": [
            {"id": "other", "starts": []},
            {"id": "r1", "starts": [
                {"number": 2, "horse": {"id": "h2", "name": "Horse 2"},
                 "pools": {"vinnare": {"odds": 4500}}},
                {"number": 1, "horse": {"id": "h1", "name": "Horse 1"},
                 "pools": {"vinnare": {"odds": 2000}}},
            ]},
        ]}
        rows = parse_race_market("r1", payload)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["odds"], 4.5)
        self.assertEqual(rows[1]["odds"], 2.0)

    def test_attach_preserves_phoenix_rank_and_matches_race_start(self):
        phoenix = pd.DataFrame([
            {"race_id": "r1", "start_number": 1, "phoenix_rank": 2},
            {"race_id": "r1", "start_number": 2, "phoenix_rank": 1},
        ])
        market = pd.DataFrame([
            {"race_id": "r1", "start_number": 1, "odds": 2.0,
             "market_rank": 1, "favorite": True, "horse_name": "A"},
            {"race_id": "r1", "start_number": 2, "odds": 4.5,
             "market_rank": 2, "favorite": False, "horse_name": "B"},
        ])
        result = attach_market(phoenix, market).sort_values("start_number")
        self.assertEqual(result["phoenix_rank"].tolist(), [2, 1])
        self.assertEqual(result["market_rank"].tolist(), [1, 2])
        self.assertTrue(result["market_match"].all())

    def test_validate_requires_expected_coverage(self):
        market = pd.DataFrame([
            {"race_id": "r1", "start_number": 1, "odds": 2.0},
            {"race_id": "r1", "start_number": 2, "odds": None},
            {"race_id": "r2", "start_number": 1, "odds": 3.0},
        ])
        result = validate_market(market, expected_races=2, expected_starters=3)
        self.assertEqual(result["status"], "OK")
        failed = validate_market(market.iloc[:2], expected_races=2, expected_starters=3)
        self.assertEqual(failed["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()

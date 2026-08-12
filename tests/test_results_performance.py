import pandas as pd

from phoenix.results.result_import import PhoenixResultImporter
from phoenix.performance.performance import PhoenixPerformance


def test_result_importer_rejects_duplicate_keys(tmp_path):
    importer = PhoenixResultImporter(str(tmp_path / "test.db"))
    rows = pd.DataFrame(
        [
            {
                "atg_race_id": "race-1",
                "horse_id": 1,
                "horse_name": "A",
                "placement": "1",
                "placement_sort": 1,
                "odds_sort": 2.0,
                "odds": 2.0,
                "race_time": "",
                "kilometer_time": "",
                "withdrawn": 0,
                "result_status": "FINAL",
            },
            {
                "atg_race_id": "race-1",
                "horse_id": 1,
                "horse_name": "A",
                "placement": "1",
                "placement_sort": 1,
                "odds_sort": 2.0,
                "odds": 2.0,
                "race_time": "",
                "kilometer_time": "",
                "withdrawn": 0,
                "result_status": "FINAL",
            },
        ]
    )

    try:
        importer.validate(rows)
    except ValueError as exc:
        assert "Duplicate incoming keys" in str(exc)
    else:
        raise AssertionError("Duplicate result keys must be rejected")


def test_performance_metrics_match_known_case(tmp_path):
    performance = PhoenixPerformance(str(tmp_path / "unused.db"))
    data = pd.DataFrame(
        [
            {"atg_race_id": "r1", "horse_id": 1, "phoenix_score": 10.0, "phoenix_probability": 0.50, "placement_sort": 1, "odds": 2.0, "withdrawn": 0, "result_status": "FINAL"},
            {"atg_race_id": "r1", "horse_id": 2, "phoenix_score": 5.0, "phoenix_probability": 0.30, "placement_sort": 2, "odds": 4.0, "withdrawn": 0, "result_status": "FINAL"},
            {"atg_race_id": "r2", "horse_id": 3, "phoenix_score": 9.0, "phoenix_probability": 0.40, "placement_sort": 2, "odds": 3.0, "withdrawn": 0, "result_status": "FINAL"},
            {"atg_race_id": "r2", "horse_id": 4, "phoenix_score": 8.0, "phoenix_probability": 0.35, "placement_sort": 1, "odds": 5.0, "withdrawn": 0, "result_status": "FINAL"},
        ]
    )

    report = performance.evaluate(data)

    assert report["races"] == 2
    assert report["starters"] == 4
    assert report["top1_hits"] == 1
    assert report["top3_hits"] == 2
    assert report["top5_hits"] == 2

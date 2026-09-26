# Phoenix 15 — Phase 2 Backtest Harness

This is a separate READ ONLY analysis layer. It does not modify the frozen Phoenix V1 model, feature engine, or SQLite/database.

## What is automated

- recursively loads stored CSV/JSON/Parquet snapshots;
- validates race_id + start_number uniqueness;
- requires Phoenix rank, original system selection, and actual winner/result;
- applies the existing PhoenixProtectionLayerV1;
- compares original vs protected system per race;
- records recovery and degradation cases;
- records Rule 1/2/3 application;
- verifies system size before/after;
- writes permanent CSV/JSON reports;
- refuses to fabricate a historical result when required data is missing.

## Colab

python phoenix15/PHOENIX15_PHASE2_BACKTEST.py --input /path/to/saved/phoenix15_snapshots --output /path/to/phase2_report

The input must contain the real historical snapshots. The script does not generate substitute races.

## Required historical fields

race_id, start_number, phoenix_rank, in_system, plus either winner=1 or result_position=1.

Optional fields: phoenix_score, phoenix_probability, odds, odds_rank, spike_signal, race_datetime, round_id, meeting_id.

## Current limitation

The GitHub repository does not contain the Google Drive/Colab historical snapshot files needed for a real Phase 2 run. Therefore this commit creates the executable backtest path but intentionally does not claim historical performance until the real snapshots are supplied.

PR #14 remains unmerged until the real OOS backtest passes its acceptance criteria.
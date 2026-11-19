# Phoenix Football Odds Scanner

A separate football project inside Travsystem. It does not import, modify, or depend on Phoenix Trav runtime code.

## First milestone: usable odds scanner

The first runnable version accepts odds exported or copied into a CSV and:

- handles any market name as data (1X2, goals, corners, cards, shots, player props, etc.);
- finds the best available price per event / market / selection / line;
- calculates bookmaker overround and normalized implied probabilities when a bookmaker has a complete outcome set;
- builds a market-consensus reference from bookmaker probabilities;
- ranks price differences against that consensus;
- exports a compact CSV report.

**Important:** a better price than the market consensus is not proof of positive expected value. A Phoenix model probability is required before a bet can be labelled +EV. The scanner must never invent probabilities for corners, cards, or player markets.

## Quick start

Python 3.10+; no third-party packages required.

```bash
cd phoenix_football
python -m phoenix_football scan --input data/odds_sample.csv --output reports/scan.csv
```

If running from the repository root:

```bash
python -m phoenix_football scan --input phoenix_football/data/odds_sample.csv --output phoenix_football/reports/scan.csv
```

## CSV format

Required columns:

`event_id,sport,league,commence_time,home_team,away_team,bookmaker,market,selection,line,odds,captured_at`

- `event_id`: stable event identifier from the source.
- `market`: provider market key or a consistent label.
- `selection`: outcome, e.g. Home / Draw / Away, Over / Under, Yes / No, or player name.
- `line`: optional market line (e.g. 2.5 goals, 9.5 corners); leave blank for no line.
- `odds`: decimal odds greater than 1.
- `captured_at`: ISO-8601 timestamp with timezone recommended.

Do not mix different lines or markets. For player props, selection must identify the player and outcome clearly.

## Data-source plan

1. CSV/manual import is the first reliable input path.
2. Add a live odds provider adapter after an API provider and account plan are confirmed.
3. Provider coverage varies: soccer 1X2 and totals are more common than corners, cards and player props. The app must report unavailable markets rather than pretending they were scanned.
4. Keep API keys in environment variables or a local .env file that is never committed.

## Interpretation

- `best_odds`: highest price found among imported bookmakers.
- `market_fair_probability`: average no-vig probability across bookmakers with a complete outcome set.
- `market_fair_odds`: reciprocal of the market fair probability.
- `price_edge_vs_consensus_pct`: best odds relative to consensus fair odds. This is a price-shopping indicator, not model EV.
- `model_probability` and `expected_value_pct` remain blank until an independently validated Phoenix probability is provided for that exact market and selection.

## Safety / integrity rules

- No auto-betting.
- No fabricated market coverage or model probabilities.
- Preserve source bookmaker, market, line, event and capture timestamp.
- Do not use closing odds or post-kickoff odds as if they were available earlier.
- Paper-trading and out-of-sample validation are required before any profitability claim.

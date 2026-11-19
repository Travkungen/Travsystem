# Phoenix Football Odds Scanner

A separate football project inside Travsystem. It does not import, modify, or depend on Phoenix Trav runtime code.

## Current capabilities

- The Odds API v4 adapter for active soccer leagues.
- Pre-match odds fetch for all active soccer sport keys returned by the provider.
- Default featured markets: 1X2 (h2h) and totals.
- Optional discovery and retrieval of additional event markets, when the provider/bookmaker exposes them.
- CSV normalization, best-price comparison and no-vig market consensus.
- Timestamped raw JSON snapshots and daily CSV reports.
- No automatic bet placement and no fabricated model probabilities.

## Quick start

Python 3.10+; no third-party packages required.

Set your API key as an environment variable. Never commit the key or paste it into GitHub files.

```bash
export ODDS_API_KEY="your-key"
cd phoenix_football
```

Fetch prematch odds for active soccer leagues:

```bash
python -m phoenix_football.scanner fetch
```

Discover and fetch additional event markets (may consume extra API quota):

```bash
python -m phoenix_football.scanner fetch --include-extra-markets
```

Run the scanner on an imported CSV:

```bash
python -m phoenix_football.scanner scan --input data/odds_sample.csv --output reports/scan.csv
```

The fetch command writes:
- `data/raw/latest_odds.json`: timestamped raw provider response and API usage metadata.
- `reports/daily_odds.csv`: normalized odds rows.

## Market coverage

The provider's main odds endpoint returns featured markets such as h2h and totals. Additional markets are discovered per event and queried through the event-odds endpoint. Coverage is not universal: corners, cards and soccer player props depend on league, bookmaker, region and subscription plan. The report must show what was actually returned.

The Odds API documents soccer player props for selected major leagues with coverage currently limited to US bookmakers. Do not assume those props will be present from European bookmakers. Additional event markets may also require extra API requests. See:
- https://the-odds-api.com/liveapi/guides/v4/
- https://the-odds-api.com/sports-odds-data/betting-markets.html

## CSV format

Required columns:

`event_id,sport,league,commence_time,home_team,away_team,bookmaker,market,selection,line,odds,captured_at`

- `event_id`: stable event identifier from the source.
- `market`: provider market key or a consistent label.
- `selection`: outcome, e.g. Home / Draw / Away, Over / Under, Yes / No, or player name.
- `line`: optional market line (e.g. 2.5 goals, 9.5 corners); leave blank for no line.
- `odds`: decimal odds greater than 1.
- `captured_at`: ISO-8601 timestamp with timezone recommended.

## Interpretation

- `best_odds`: highest price found among imported bookmakers.
- `market_fair_probability`: average no-vig probability across bookmaker snapshots with complete outcome sets.
- `market_fair_odds`: reciprocal of the market fair probability.
- `price_edge_vs_consensus_pct`: best odds relative to consensus fair odds. This is a price-shopping indicator, not model EV.
- `model_probability` and `expected_value_pct` remain blank until an independently validated Phoenix probability exists for that exact market, selection and line.

## Integrity rules

- No auto-betting.
- No fabricated market coverage or model probabilities.
- Preserve source bookmaker, market, line, event and capture timestamp.
- Exclude in-play events from the pre-match fetch.
- Never use closing odds or post-kickoff odds as if they were available earlier.
- Paper-trading and out-of-sample validation are required before any profitability claim.

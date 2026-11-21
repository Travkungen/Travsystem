# Codex handoff — Phoenix Football Odds Scanner

Work only inside `phoenix_football/`. Do not edit Phoenix Trav, Phoenix15, frozen baselines, notebooks, or the repository root README.

## User outcome
Deliver a usable daily football odds scanner quickly. It should scan every football event and every market actually available from the connected odds provider, including 1X2, goals, corners, cards, shots and player props when the provider/account plan exposes them. Never claim coverage for markets the provider does not return.

## Current starter
- A standard-library CSV scanner exists in `phoenix_football/phoenix_football/scanner.py`.
- Sample input: `data/odds_sample.csv`.
- Tests: `tests/test_scanner.py`.
- It finds best prices and computes no-vig market consensus only when a bookmaker supplies a complete outcome set.
- It deliberately does not label price-shopping differences as positive EV.

## Immediate tasks
1. Run the current tests and fix any defects without changing the data contract.
2. Add a provider adapter behind a clean interface. First inspect current provider documentation and select a provider that offers broad soccer coverage. Do not assume all player props/corners/cards are available.
3. Keep API credentials out of Git. Read them from environment variables (for example `ODDS_API_KEY`) and provide an `.env.example` containing only placeholders.
4. Implement a single command that fetches today's soccer fixtures and available odds, normalizes them to the existing CSV schema, stores timestamped raw snapshots, and emits a ranked daily report.
5. Add market-coverage reporting by sport/league/market/bookmaker so missing coverage is visible.
6. Add Phoenix model probability joins only where a validated model exists for the exact market/selection. Current Phoenix V2 is a 1X2 model; do not apply it to corners, cards, or player props.
7. Calculate EV only as `model_probability * decimal_odds - 1`, and only when the model probability is independently validated and corresponds to the exact market/line/selection. Otherwise leave EV blank and classify as market price comparison only.
8. Add paper-trading logs, stake limits and performance reporting; no automatic bet placement.
9. Provide one easy entry point (CLI first; small local web UI only if it is genuinely faster to use) and clear setup instructions.

## Acceptance criteria
- One command runs the daily scan.
- One CSV or HTML report shows best available price, bookmaker, event start, market, selection, line, timestamp, data coverage, and whether EV is genuinely model-backed.
- Duplicate events and stale/post-kickoff prices are detected or excluded.
- Missing markets are reported, never silently fabricated.
- Unit tests cover overround removal, best-price selection, incomplete outcomes, duplicate rows, invalid odds and stale timestamps.
- No credentials, bankroll secrets, or user-specific data are committed.
- Do not claim profitability until a timestamp-correct out-of-sample paper-trading sample supports it.

## Important project boundary
Phoenix Football is a separate project from Phoenix Trav. Preserve the existing Trav system exactly as it is.

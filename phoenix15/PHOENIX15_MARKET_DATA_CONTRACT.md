# Phoenix 15 — Market Data Contract

## Purpose

Odds and market information are mandatory omgångsdata but are **not** part of the current 20 Phoenix model features.

## Canonical fields

- `race_id`
- `horse_id`
- `start_number`
- `odds` — decimal winner odds
- `market_rank` — lowest valid odds = rank 1
- `favorite` — true for market rank 1

## Historical source compatibility

The Phoenix archive contains `odds_sort` with the same race/horse/start keys. Values such as `285` are interpreted as `2.85`; `9998`/`9999` are special/unavailable values and are not valid odds.

## Hard validation

A production omgång run must not silently continue with incomplete market data. Validate:

- expected starter count
- unique `race_id + horse_id`
- valid odds count
- one market favorite per race when odds are available

## Architecture

`ATG raw/game/startlist source`

→ `PhoenixMarketData`

→ `odds + market_rank + favorite`

→ parallel with Phoenix Feature Build

→ `Phoenix model`

→ `Top 7`

→ `Spikmatta/GAP`

Market data must remain separate from model features until a later, explicit backtest proves that odds improve the model.

## Current status

The historical odds structure is verified. The current Phoenix 15 live startlist path does not yet carry odds. The next implementation step is to connect the current ATG source to `PhoenixMarketData` and require market-data validation before producing the final omgång output.

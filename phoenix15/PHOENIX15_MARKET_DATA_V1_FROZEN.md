# PHOENIX 15 — MARKET DATA V1 — FROZEN

**Status:** READ ONLY

## V85 checkpoint — 2026-08-22

- V85 races: 8
- Starters: 90
- Valid odds: 85
- Missing odds: 5
- Phoenix model features changed: NO
- Status: FROZEN

## Verified ATG market path

The working market source is the ATG new betting system game endpoint:

`/api-public/v0/games/{game_id}`

For V85 the game id is:

`V85_2026-08-22_23_5`

The response contains race-level `starts` and current odds under:

`races[*].starts[*].pools.vinnare.odds`

The related pool endpoint is also verified:

`/api-public/v0/pools/{vinnare_pool_id}`

Example:

`/api-public/v0/games/vinnare_2026-08-22_23_1`

`/api-public/v0/pools/vinnare_2026-08-22_23_1`

## Important lessons

Do NOT use:

- `/api-public/v0/games/vinnare/{id}`
- `/api-public/v0/betting/...`
- `/api-public/v0/markets/...`
- `/api-public/v0/races/{race_id}/odds`
- `/api-public/v0/races/{race_id}/markets`
- `/api-public/v0/races/{race_id}/betting`
- `/api-public/v0/races/{race_id}/pools`

Those tested paths returned 404.

The race extended endpoint remains valid for startlists:

`/api-public/v0/races/{race_id}/extended`

It returned HTTP 200 and 10 starters for V85-1 during this checkpoint.

## Frozen rule

This checkpoint is READ ONLY. Do not modify Phoenix model features or the Master baseline when extending the market/odds pipeline.

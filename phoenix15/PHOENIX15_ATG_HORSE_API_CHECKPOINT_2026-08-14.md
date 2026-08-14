# PHOENIX 15 — ATG HORSE API CHECKPOINT

**Date:** 2026-08-14  
**Status:** VERIFIED / READ ONLY  
**Database:** NOT CHANGED  
**Model:** NOT CHANGED

## Verified ATG Horse API route

Production Horse API base:

`https://horse-betting-info.prod.c1.atg.cloud/api-public/v0`

The frontend JavaScript was inspected and confirmed to construct Horse API race routes under `/v0/races`.

## Verified real race ID

Real Phoenix 15 race ID from `race_mapping`:

`2026-08-08_33_5`

This is the frontend-compatible ATG race ID format:

`YYYY-MM-DD_trackId_raceNumber`

## Smoke-test results

Using the real race ID `2026-08-08_33_5`:

- `/races/2026-08-08_33_5/extended` → **HTTP 200**
- `/races/2026-08-08_33_5/start` → **HTTP 200**
- `/races/2026-08-08_33_5/tips-comments` → **HTTP 200**
- `/races/2026-08-08_33_5/comments` → **HTTP 200**

## Data verified

`extended` returned race-level and start-level data including race ID, date, race number, distance, start method, track, status, starts, horse IDs/names, trainer IDs/names, statistics, money, equipment and related entities.

`start` returned detailed start/horse information for the race.

`tips-comments` returned ATG comments and tips for the starts.

`comments` returned an empty JSON object for this race, but the route itself responded successfully with HTTP 200.

## Historical vs live race IDs

`race_mapping` contains older historical rows using numeric ATG race IDs such as `1297573`, while the current Phoenix 15 live import uses frontend-style IDs such as `2026-08-08_33_5`.

Do **not** merge or rewrite these ID systems as part of this checkpoint. Further mapping work must remain READ ONLY until explicitly approved.

## Odds status

**Odds are NOT YET VERIFIED.**

The successful Horse API responses above do not by themselves establish that current betting odds are available. A separate READ ONLY odds-field/API inspection is required before Phoenix 15 treats odds as a verified data source.

## Safety / change boundary

This checkpoint records discovery and smoke-test verification only.

- No SQLite tables changed.
- No race_mapping rows changed.
- No Feature Engine changes.
- No AI/model changes.
- No production data writes.

## Next intended READ ONLY step

Inspect the real `extended` and/or `start` JSON for explicit odds/betting fields and determine the correct ATG odds source before modifying any Phoenix 15 data pipeline.

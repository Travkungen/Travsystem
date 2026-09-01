# PHOENIX 15 — ATG ODDS → COMBINED RANK CELL
# Permanent Colab cell for Travkungen/Travsystem
#
# PURPOSE
# - Reuse the verified ATG odds dataframe already produced in Colab.
# - NEVER change the original Phoenix ranking.
# - Add market_rank + combined_score + phoenix_odds_rank as a separate layer.
# - Produce deterministic Top 7 for all V86 races.
#
# EXPECTED INPUTS
#   phoenix_df : DataFrame containing race_number, start_number, horse_name,
#                phoenix_rank (or equivalent Phoenix ranking).
#   odds_df    : DataFrame containing race_id, start_number, horse_name,
#                odds (the already verified ATG odds output).
#
# If the notebook already uses different variable names, set PHOENIX_DF and
# ODDS_DF below before running this cell.
#
# IMPORTANT:
# Original Phoenix ranking is copied to phoenix_rank_original and is never
# overwritten. Odds are an external decision layer only.

import pandas as pd
import numpy as np

# ---- INPUT VARIABLE DISCOVERY ----
def _pick_df(names):
    for name in names:
        obj = globals().get(name)
        if isinstance(obj, pd.DataFrame) and not obj.empty:
            return obj
    return None

PHOENIX_DF = _pick_df([
    "phoenix_df", "phoenix_rank_df", "phoenix_ranking",
    "phoenix_ranked", "ranked_df", "df_ranked"
])

ODDS_DF = _pick_df([
    "odds_df", "odds_v86", "market_df", "v86_odds",
    "df_odds"
])

if PHOENIX_DF is None:
    raise RuntimeError(
        "Hittar inte Phoenix-rankingens DataFrame. "
        "Sätt PHOENIX_DF = din Phoenix-ranking."
    )

if ODDS_DF is None:
    raise RuntimeError(
        "Hittar inte odds-DataFrame. "
        "Sätt ODDS_DF = den verifierade ATG-odds-tabellen."
    )

phoenix = PHOENIX_DF.copy()
odds = ODDS_DF.copy()

# ---- COLUMN HELPERS ----
def _find_col(df, candidates, label):
    for c in candidates:
        if c in df.columns:
            return c
    raise RuntimeError(
        f"Saknar {label}. Förväntade någon av: {candidates}. "
        f"Finns: {list(df.columns)}"
    )

p_race = _find_col(
    phoenix,
    ["race_id", "race_number", "race", "lopp"],
    "race-kolumn i Phoenix-data"
)
p_start = _find_col(
    phoenix,
    ["start_number", "startnr", "start_no", "number", "hästnummer"],
    "startnummer i Phoenix-data"
)
p_rank = _find_col(
    phoenix,
    ["phoenix_rank", "rank", "Phoenix_rank"],
    "Phoenix-rank"
)

o_race = _find_col(
    odds,
    ["race_id", "race_number", "race", "lopp"],
    "race-kolumn i odds-data"
)
o_start = _find_col(
    odds,
    ["start_number", "startnr", "start_no", "number", "hästnummer"],
    "startnummer i odds-data"
)
o_odds = _find_col(
    odds,
    ["odds", "odds_raw", "win_odds"],
    "odds-kolumn"
)

# ---- PRESERVE ORIGINAL PHOENIX ----
phoenix["phoenix_rank_original"] = pd.to_numeric(
    phoenix[p_rank], errors="coerce"
)
phoenix["phoenix_rank"] = phoenix["phoenix_rank_original"]

# ---- PREPARE ODDS LAYER ----
market = odds[[o_race, o_start, o_odds]].copy()
market.columns = ["_race", "_start", "odds"]
market["odds"] = pd.to_numeric(market["odds"], errors="coerce")

# The successful ATG output may contain 0 / 9999 / NaN for unavailable odds.
# Those values are treated as missing market odds, NOT as real favorites.
market.loc[market["odds"] <= 0, "odds"] = np.nan
market.loc[market["odds"] >= 9998, "odds"] = np.nan

market = market.drop_duplicates(["_race", "_start"], keep="last")

# ---- MERGE WITHOUT TOUCHING PHOENIX FEATURES/RANK ----
combined = phoenix.copy()
combined["_race_key"] = combined[p_race].astype(str)
combined["_start_key"] = pd.to_numeric(
    combined[p_start], errors="coerce"
)

market["_race_key"] = market["_race"].astype(str)
market["_start_key"] = pd.to_numeric(
    market["_start"], errors="coerce"
)

combined = combined.merge(
    market[["_race_key", "_start_key", "odds"]],
    on=["_race_key", "_start_key"],
    how="left",
    validate="one_to_one"
)

# ---- MARKET RANK ----
combined["market_rank"] = combined.groupby("_race_key")["odds"].rank(
    method="min", ascending=True
)

# ---- COMBINED SCORE ----
# Equal-weight average of Phoenix rank and market rank.
# Missing market odds: Phoenix remains the only available signal.
combined["combined_score"] = (
    combined["phoenix_rank_original"] + combined["market_rank"]
) / 2.0

combined.loc[
    combined["market_rank"].isna(),
    "combined_score"
] = combined.loc[
    combined["market_rank"].isna(),
    "phoenix_rank_original"
]

# ---- FINAL SEPARATE RANK ----
combined["phoenix_odds_rank"] = combined.groupby("_race_key")[
    "combined_score"
].rank(method="min", ascending=True)

# Stable tie-breakers: combined score -> Phoenix rank -> start number
combined = combined.sort_values(
    ["_race_key", "combined_score",
     "phoenix_rank_original", "_start_key"],
    ascending=[True, True, True, True]
).reset_index(drop=True)

combined["rank_change"] = (
    combined["phoenix_rank_original"] - combined["phoenix_odds_rank"]
)

# ---- TOP 7 PER RACE ----
phoenix_odds_top7 = (
    combined.sort_values(
        ["_race_key", "phoenix_odds_rank",
         "combined_score", "_start_key"]
    )
    .groupby("_race_key", sort=False, group_keys=False)
    .head(7)
    .copy()
)

# ---- DISPLAY CLEAN OUTPUT ----
display_cols = [
    p_race, p_start,
    "horse_name" if "horse_name" in combined.columns else p_start,
    "phoenix_rank_original",
    "market_rank",
    "odds",
    "combined_score",
    "phoenix_odds_rank",
    "rank_change",
]

display_cols = list(dict.fromkeys(
    c for c in display_cols if c in phoenix_odds_top7.columns
))

print("=" * 90)
print("PHOENIX 15 — ATG ODDS + PHOENIX")
print("Original Phoenix-ranking: BEVARAD")
print("New ranking: phoenix_odds_rank")
print("=" * 90)

display(phoenix_odds_top7[display_cols])

print("\n" + "=" * 90)
print("PHOENIX 15 — KOMBINERAD TOP 7")
print("=" * 90)

for race_key, g in phoenix_odds_top7.groupby("_race_key", sort=False):
    nums = g[p_start].astype(int).tolist()
    print(f"Lopp {race_key}: " + " - ".join(map(str, nums)))

print("\nKontroller:")
print("Phoenix originalkolumn bevarad:", "phoenix_rank_original" in combined.columns)
print("Rader:", len(combined))
print("Lopp:", combined["_race_key"].nunique())
print("Top 7-rader:", len(phoenix_odds_top7))
print("Odds träffade:", int(combined["odds"].notna().sum()))
print("ATG-odds saknas:", int(combined["odds"].isna().sum()))

# Public notebook variables for later cells
PHOENIX15_COMBINED = combined.drop(
    columns=["_race_key", "_start_key"], errors="ignore"
).copy()

PHOENIX15_ODDS_TOP7 = phoenix_odds_top7.drop(
    columns=["_race_key", "_start_key"], errors="ignore"
).copy()

print("\nPHOENIX 15 — ODDSLAGER KLART")
print("Original Phoenix-ranking är orörd.")

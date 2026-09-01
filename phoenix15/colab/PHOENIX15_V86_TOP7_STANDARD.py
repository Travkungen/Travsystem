# PHOENIX 15 — V86 TOP 7 STANDARD
# Colab-standard cell: paste into notebook and run after ranked_v86 exists.
# No DB writes. No model changes.

print("=" * 64)
print("PHOENIX 15 — V86 TOP 7 STANDARD")
print("=" * 64)

df = ranked_v86.copy()

required = ["race_id", "race_number", "start_number"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise RuntimeError("Saknade kolumner: " + str(missing))

rank_col = "phoenix_rank" if "phoenix_rank" in df.columns else "model_rank"
if rank_col not in df.columns:
    raise RuntimeError("Ingen Phoenix/model-rank hittades")

df = df.sort_values(["race_id", rank_col])

top7 = {}

print("\n=== PHOENIX TOP 7 ===\n")

for race_id, g in df.groupby("race_id", sort=False):
    g = g.sort_values(rank_col)
    race_no = int(g["race_number"].iloc[0])
    numbers = g.head(7)["start_number"].astype(int).tolist()
    top7[race_no] = numbers
    print(f"V86-{race_no}: " + " ".join(map(str, numbers)))

if len(top7) != 8:
    raise RuntimeError(f"Förväntade 8 V86-lopp, fick {len(top7)}")

print("\n=== RANK-KONTROLL ===")

if "phoenix_rank" in df.columns and "model_rank" in df.columns:
    all_same = True
    for race_id, g in df.groupby("race_id", sort=False):
        phoenix = g.sort_values("phoenix_rank").head(7)["start_number"].astype(int).tolist()
        model = g.sort_values("model_rank").head(7)["start_number"].astype(int).tolist()
        same = phoenix == model
        all_same = all_same and same
        race_no = int(g["race_number"].iloc[0])
        print(f"V86-{race_no}: " + ("SAMMA" if same else "SKILLNAD"))
    print("\nPhoenix Top 7 = Model Top 7:", "JA" if all_same else "NEJ")

print("\n" + "=" * 64)
print("PHOENIX 15 — TOP 7 KLAR")
print("=" * 64)
for race_no in sorted(top7):
    print(f"V86-{race_no}: " + " ".join(map(str, top7[race_no])))
print("INGEN DB-SKRIVNING")
print("INGEN MODELLÄNDRING")

# PHOENIX 15 — PLAYMOTOR FINAL
# Purpose: reusable read-only play layer above the frozen Phoenix V3 model.
# Inputs expected in the Colab runtime:
#   race_info, profiles, pandas as pd
# This module does NOT train, modify model files, or write SQLite.

from itertools import product
import math

BUDGETS = {"SAFE": 32, "BALANS": 96, "OFFENSIV": 192}


def build_candidate_fields(race_info, profiles):
    fields = {}
    for mode in ["SAFE", "BALANS", "OFFENSIV"]:
        fields[mode] = {}
        for leg in sorted(race_info):
            g = race_info[leg]["data"].copy()
            p = profiles[leg]
            g = g.sort_values("phoenix_probability", ascending=False)

            if mode == "SAFE":
                n = 1 if p["strength"] >= 75 else 2 if p["strength"] >= 55 else 3
            elif mode == "BALANS":
                n = 1 if p["strength"] >= 75 else 3 if p["strength"] >= 55 else 4
            else:
                n = 1 if p["strength"] >= 75 else 4 if p["strength"] >= 55 else 5

            selected = g[g["signal"].isin(["SPIK", "A", "B", "SKRÄLL"])].head(n).copy()

            if mode != "SAFE":
                skrall = g[g["signal"] == "SKRÄLL"]
                if not skrall.empty:
                    sn = int(skrall.iloc[0]["start_number"])
                    nums = selected["start_number"].astype(int).tolist()
                    if sn not in nums:
                        selected = __import__("pandas").concat([selected, skrall.iloc[[0]]], ignore_index=True)

            fields[mode][leg] = selected.drop_duplicates("start_number")
    return fields


def _score_row(row, fields, legs):
    total = 0.0
    value_score = 0.0
    signals = []

    for i, leg in enumerate(legs):
        number = int(row[i])
        g = fields[leg]
        hit = g[g["start_number"].astype(int) == number]
        if hit.empty:
            continue
        r = hit.iloc[0]
        p = max(float(r["phoenix_probability"]), 0.000001)
        market = float(r["market_rank"])
        odds = float(r["odds"])
        signal = str(r["signal"])
        signals.append(signal)

        total += math.log(p) * 100
        total += max(0.0, 10.0 - market) * 1.5
        if signal == "SPIK":
            total += 8.0
        elif signal == "A":
            total += 4.0
        elif signal == "SKRÄLL":
            total += 2.5

        if odds > 0:
            fair_value = p * odds
            if fair_value > 1.0:
                value_score += min(fair_value, 3.0) * 4.0

    skrallar = signals.count("SKRÄLL")
    if skrallar == 1:
        total += 5.0
    elif skrallar >= 2:
        total += 2.0

    return total + value_score


def build_final_rows(candidate_fields, mode):
    fields = candidate_fields[mode]
    legs = sorted(fields)
    number_lists = [fields[leg]["start_number"].astype(int).tolist() for leg in legs]
    candidates = list(product(*number_lists))

    scored = [{"row": row, "score": _score_row(row, fields, legs)} for row in candidates]
    scored.sort(key=lambda x: x["score"], reverse=True)

    wanted = BUDGETS[mode]
    selected = []

    for item in scored:
        row = item["row"]
        if not selected:
            selected.append(item)
            continue

        max_similarity = max(
            sum(row[i] == old["row"][i] for i in range(len(row)))
            for old in selected
        )
        limit = 5 if mode == "SAFE" else 4
        if max_similarity <= limit:
            selected.append(item)
        if len(selected) >= wanted:
            break

    if len(selected) < wanted:
        used = {tuple(x["row"]) for x in selected}
        for item in scored:
            key = tuple(item["row"])
            if key not in used:
                selected.append(item)
                used.add(key)
            if len(selected) >= wanted:
                break

    return selected


def run_playmotor(race_info, profiles):
    fields = build_candidate_fields(race_info, profiles)
    final_rows = {mode: build_final_rows(fields, mode) for mode in BUDGETS}
    return fields, final_rows


def print_summary(fields, final_rows):
    print("=" * 60)
    print("PHOENIX 15 — PLAYMOTOR FINAL")
    print("=" * 60)
    for mode in BUDGETS:
        rows = final_rows[mode]
        print(f"{mode}: {len(rows)} rader / {len(rows)} kr")
        for i, leg in enumerate(sorted(fields[mode])):
            nums = sorted({int(x["row"][i]) for x in rows})
            print(f"V64-{leg}: {','.join(map(str, nums))}")
        print()
    print("READ ONLY")

"""
Phoenix 15 — Point 9 Diagnostic Case: V86 2026-08-12 Protection Layer Test

This is a SIMULATED diagnostic test based on the historical system-miss patterns.
It is not a historical backtest and must not be interpreted as proof of no degradation.
"""

import pandas as pd
from PHOENIX15_PROTECTION_LAYER_v1 import PhoenixProtectionLayerV1


def simulate_v86_2026_08_12():
    """Run two diagnostic cases using simulated Top-7/market inputs."""
    print("\n" + "=" * 80)
    print("PHOENIX 15 — POINT 9 DIAGNOSTIC TEST: V86 2026-08-12")
    print("SIMULATED CASES — NOT A HISTORICAL BACKTEST")
    print("=" * 80)

    # ===== LEG 3: V86-3 =====
    print("\n" + "-" * 80)
    print("LEG 3 (V86-3): Winner 6 (Phoenix rank 5) — historical miss pattern")
    print("-" * 80)

    top7_leg3 = pd.DataFrame({
        "start_number": [2, 5, 6, 8, 11, 12, 14],
        "phoenix_rank": [1, 2, 3, 4, 5, 6, 7],
        "phoenix_score": [25.5, 21.3, 19.8, 18.2, 17.5, 16.1, 15.0],
        "phoenix_probability": [0.45, 0.38, 0.34, 0.30, 0.28, 0.24, 0.21],
    })
    system_leg3 = pd.DataFrame({
        "start_number": [2, 5, 6, 8, 11, 12, 14],
        "in_system": [1, 1, 0, 0, 0, 0, 0],
    })
    market_leg3 = pd.DataFrame({
        "start_number": [2, 5, 6, 8, 11, 12, 14],
        "odds_rank": [2, 3, 1, 5, 7, 4, 6],
        "odds_value": [3.2, 4.5, 2.8, 6.1, 8.3, 5.2, 7.1],
    })
    protection = PhoenixProtectionLayerV1(verbose=True)
    protected_leg3, decisions_leg3 = protection.protect_system(top7_leg3, system_leg3, market_data=market_leg3)
    eval_leg3 = protection.evaluate_on_facit(protected_leg3, 6, "V86-3")
    print(f"\nResult: {'HIT' if eval_leg3['hit'] else 'MISS'} (diagnostic expectation: MISS)")
    print(f"Protected system: {eval_leg3['system']}")
    print(f"Protection decisions: {decisions_leg3['protected_candidates']}")

    # ===== LEG 7: V86-7 CRITICAL CASE =====
    print("\n" + "-" * 80)
    print("LEG 7 (V86-7): Winner 4 (Phoenix rank 3) — CRITICAL CASE")
    print("-" * 80)

    # Historical diagnostic fact: start 4 is Phoenix rank 3.
    top7_leg7 = pd.DataFrame({
        "start_number": [1, 4, 5, 7, 8, 12, 15],
        "phoenix_rank": [1, 3, 2, 4, 5, 6, 7],
        "phoenix_score": [26.1, 24.8, 23.5, 22.0, 20.5, 18.3, 17.1],
        "phoenix_probability": [0.48, 0.45, 0.41, 0.38, 0.35, 0.29, 0.26],
    })
    system_leg7 = pd.DataFrame({
        "start_number": [1, 4, 5, 7, 8, 12, 15],
        "in_system": [0, 0, 1, 1, 0, 1, 0],
    })
    market_leg7 = pd.DataFrame({
        "start_number": [1, 4, 5, 7, 8, 12, 15],
        "odds_rank": [3, 2, 4, 1, 6, 5, 7],
        "odds_value": [4.2, 3.8, 5.1, 2.1, 7.3, 6.2, 8.5],
    })
    protection2 = PhoenixProtectionLayerV1(verbose=True)
    protected_leg7, decisions_leg7 = protection2.protect_system(top7_leg7, system_leg7, market_data=market_leg7)
    eval_leg7 = protection2.evaluate_on_facit(protected_leg7, 4, "V86-7")
    print(f"\nResult: {'HIT' if eval_leg7['hit'] else 'MISS'} (diagnostic expectation: HIT)")
    print(f"Protected system: {eval_leg7['system']}")
    print(f"Protection decisions: {decisions_leg7['protected_candidates']}")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY — NOT A HISTORICAL BACKTEST")
    print("=" * 80)
    print(f"V86-3: {'HIT' if eval_leg3['hit'] else 'MISS'} (expected MISS in this diagnostic)")
    print(f"V86-7: {'HIT' if eval_leg7['hit'] else 'MISS'} (expected HIT; critical rank-3 recovery)")
    print("System size is preserved in both diagnostic cases.")
    print("Historical no-degradation claim remains UNVALIDATED until Phase 2.")


if __name__ == "__main__":
    simulate_v86_2026_08_12()

"""
Phoenix 15 — System Selection / Protection Layer v1

Purpose:
--------
Protect strong Phoenix Top 7 candidates from aggressive system reduction.
Keep Phoenix ranking unchanged. Improve system construction by restoring
candidates that create obvious risk when removed.

Principle:
----------
Phoenix ranks. Reduction removes candidates. Protection restores candidates
that reduction logic would otherwise drop despite strong Phoenix signals.

Design:
-------
1. Accept Phoenix Top 7 ranking (read-only)
2. Accept system selection (reduction output)
3. Analyze gaps between Top 7 and selected system
4. Apply protection rules based on:
   - Phoenix rank (1-3 = high protection, 4-7 = selective)
   - Market odds rank (good odds = protection candidate)
   - Spike/skräll signal strength
   - Co-ranking consistency (if rank 1-2 strong but rank 4-7 weak, protect better odds)
5. Output protected system (same candidate count)
6. Return protection decisions for audit/learning

Important constraints:
-----------------------
- This is a DECISION LAYER above Phoenix ranking
- Phoenix model/features are READ ONLY
- No database writes
- No model retraining
- Output must maintain exact system size (do not grow it)
- Every protection decision must be logged for evaluation
"""

import pandas as pd
import json
from typing import Dict, List, Tuple, Optional


class PhoenixProtectionLayerV1:
    """
    Read-only decision layer for system protection.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize protection layer.

        Parameters
        ----------
        verbose : bool
            Enable detailed logging of protection decisions.
        """
        self.verbose = verbose
        self.protection_log = []

    def protect_system(
        self,
        phoenix_top7: pd.DataFrame,
        selected_system: pd.DataFrame,
        market_data: Optional[pd.DataFrame] = None,
        spike_signal: Optional[Dict[int, str]] = None,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Apply protection logic to system selection.

        Parameters
        ----------
        phoenix_top7 : pd.DataFrame
            Phoenix Top 7 ranking with columns:
            - start_number (int)
            - phoenix_rank (int, 1-7)
            - phoenix_score (float)
            - phoenix_probability (float)

        selected_system : pd.DataFrame
            System selected by reduction logic with columns:
            - start_number (int)
            - in_system (bool or 1/0)

        market_data : pd.DataFrame, optional
            Market odds data with columns:
            - start_number (int)
            - odds_rank (int, market rank 1-N)
            - odds_value (float, e.g., 2.5)

        spike_signal : Dict[int, str], optional
            Spike classification per start_number.
            Values: 'SPIK', 'A', 'B', 'SKRÄLL', 'RESERV'

        Returns
        -------
        protected_system : pd.DataFrame
            System after protection logic.
            Same shape and size as selected_system.

        decisions : Dict
            Protection decisions log with keys:
            - 'protected_candidates': List of (start_number, reason)
            - 'dropped_candidates': List of (start_number, reason)
            - 'gaps': Dict of gaps between Top 7 and system
            - 'protection_rules_applied': List[str]
        """
        self.protection_log = []
        decisions = {
            "protected_candidates": [],
            "dropped_candidates": [],
            "gaps": {},
            "protection_rules_applied": [],
            "protection_summary": {},
        }

        # Prepare working data
        top7_set = set(phoenix_top7["start_number"].values)
        system_set = set(selected_system[selected_system["in_system"] == 1]["start_number"].values)
        gap_candidates = sorted(top7_set - system_set)

        if self.verbose:
            print(f"Phoenix Top 7: {sorted(top7_set)}")
            print(f"System: {sorted(system_set)}")
            print(f"Gap (Top 7 not in system): {gap_candidates}")

        decisions["gaps"]["top7"] = sorted(top7_set)
        decisions["gaps"]["system"] = sorted(system_set)
        decisions["gaps"]["gap_candidates"] = gap_candidates

        # Build lookup tables
        top7_by_start = {row["start_number"]: row for _, row in phoenix_top7.iterrows()}
        market_by_start = {}
        if market_data is not None:
            for _, row in market_data.iterrows():
                market_by_start[row["start_number"]] = row

        spike_by_start = spike_signal or {}

        # PROTECTION RULE 1: Protect Phoenix rank 1-3 (high protection)
        for start_num in gap_candidates:
            if start_num in top7_by_start:
                rank = top7_by_start[start_num]["phoenix_rank"]
                if rank <= 3:
                    reason = f"PROTECT_TOP3: Phoenix rank {rank}"
                    decisions["protected_candidates"].append((start_num, reason))
                    decisions["protection_rules_applied"].append(f"Rule 1 (Top 3): {start_num}")
                    if self.verbose:
                        print(f"  >> PROTECT {start_num}: {reason}")

        # PROTECTION RULE 2: Protect Phoenix rank 4-7 with good market odds (1-3)
        for start_num in gap_candidates:
            if start_num in top7_by_start and start_num not in [x[0] for x in decisions["protected_candidates"]]:
                rank = top7_by_start[start_num]["phoenix_rank"]
                market_rank = market_by_start.get(start_num, {}).get("odds_rank", 999)

                if rank >= 4 and market_rank <= 3:
                    reason = f"PROTECT_VALUE: Phoenix rank {rank}, market rank {market_rank}"
                    decisions["protected_candidates"].append((start_num, reason))
                    decisions["protection_rules_applied"].append(f"Rule 2 (Value): {start_num}")
                    if self.verbose:
                        print(f"  >> PROTECT {start_num}: {reason}")

        # PROTECTION RULE 3: Protect spike signal (SPIK)
        for start_num in gap_candidates:
            if start_num in top7_by_start and start_num not in [x[0] for x in decisions["protected_candidates"]]:
                signal = spike_by_start.get(start_num, "").upper()
                if signal == "SPIK":
                    rank = top7_by_start[start_num]["phoenix_rank"]
                    reason = f"PROTECT_SPIK: Phoenix rank {rank}, spike signal SPIK"
                    decisions["protected_candidates"].append((start_num, reason))
                    decisions["protection_rules_applied"].append(f"Rule 3 (SPIK): {start_num}")
                    if self.verbose:
                        print(f"  >> PROTECT {start_num}: {reason}")

        # Create protected system
        protected_system = selected_system.copy()
        protected_candidates = [x[0] for x in decisions["protected_candidates"]]

        # To maintain system size, we need to swap: add protected candidates, remove lowest-confidence non-protected
        if protected_candidates:
            # Find candidates to drop (lowest Phoenix confidence outside Top 3)
            candidates_to_drop = []
            for start_num in system_set:
                if start_num in top7_by_start:
                    rank = top7_by_start[start_num]["phoenix_rank"]
                    if rank >= 4:  # Can drop rank 4-7
                        candidates_to_drop.append((start_num, rank))

            candidates_to_drop.sort(key=lambda x: -x[1])  # Sort by rank descending (worst first)

            # Swap protected candidates with lowest-confidence system candidates
            num_to_swap = min(len(protected_candidates), len(candidates_to_drop))
            for i in range(num_to_swap):
                start_to_remove = candidates_to_drop[i][0]
                start_to_add = protected_candidates[i]

                protected_system.loc[
                    protected_system["start_number"] == start_to_remove, "in_system"
                ] = 0
                protected_system.loc[protected_system["start_number"] == start_to_add, "in_system"] = 1

                decisions["dropped_candidates"].append(
                    (start_to_remove, f"Dropped to restore protected {start_to_add}")
                )

                if self.verbose:
                    print(
                        f"  >> SWAP: remove {start_to_remove} (rank {candidates_to_drop[i][1]}) "
                        f">> add {start_to_add}"
                    )

        # Summary
        decisions["protection_summary"]["protected_count"] = len(decisions["protected_candidates"])
        decisions["protection_summary"]["dropped_count"] = len(decisions["dropped_candidates"])
        decisions["protection_summary"]["system_size_maintained"] = (
            selected_system["in_system"].sum() == protected_system["in_system"].sum()
        )

        return protected_system, decisions

    def evaluate_on_facit(
        self, protected_system: pd.DataFrame, winner_start_number: int, race_label: str = ""
    ) -> Dict:
        """
        Evaluate protection layer decision against actual result.

        Parameters
        ----------
        protected_system : pd.DataFrame
            Protected system from protect_system()
        winner_start_number : int
            Actual race winner start number
        race_label : str
            Optional label for logging (e.g., "V86-3")

        Returns
        -------
        evaluation : Dict
            Evaluation result with keys:
            - 'race': race_label
            - 'winner': winner_start_number
            - 'hit': bool (True if winner in protected system)
            - 'system': sorted list of system start numbers
        """
        system_set = set(protected_system[protected_system["in_system"] == 1]["start_number"].values)
        hit = winner_start_number in system_set

        evaluation = {
            "race": race_label,
            "winner": winner_start_number,
            "hit": hit,
            "system": sorted(system_set),
        }

        if self.verbose:
            status = "HIT" if hit else "MISS"
            print(f"{race_label}: {status} (winner {winner_start_number}, system {sorted(system_set)})")

        return evaluation


def test_protection_layer_on_v86_2026_08_12():
    """
    Test the protection layer on V86 2026-08-12 diagnostic case.

    This is a demonstration/testing function.
    In actual use, call PhoenixProtectionLayerV1.protect_system()
    with real Phoenix Top 7 and system data.
    """
    print("\n" + "=" * 70)
    print("PHOENIX 15 — PROTECTION LAYER v1 TEST ON V86 2026-08-12")
    print("=" * 70)

    protection = PhoenixProtectionLayerV1(verbose=True)

    # Example: V86-3 system miss
    # Winner: 6 (Phoenix rank 5)
    # System: [2, 5] (both rank 4-7)
    # Candidates in gap: [6] (rank 5)
    # Rule 2 (Value) should protect rank 5 if market odds are good

    print("\nV86-3 diagnostic case:")
    print("Winner: 6 (Phoenix rank 5)")
    print("Original system: [2, 5]")
    print("Expected: Protection layer should restore 6 if market odds support it")

    print("\n" + "=" * 70)
    print("Protection layer is ready for integration.")
    print("Next step: Load real Phoenix Top 7, market data, and spike signals")
    print("from V86 2026-08-12 and run full evaluation.")
    print("=" * 70)


if __name__ == "__main__":
    test_protection_layer_on_v86_2026_08_12()

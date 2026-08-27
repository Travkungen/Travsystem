"""Tests for the read-only Phase 2 harness.

These tests use synthetic rows only to validate mechanics; they are NOT
historical performance claims.
"""
import pandas as pd
import pytest

from PHOENIX15_PROTECTION_LAYER_v1 import PhoenixProtectionLayerV1


def race(top7, system, winner, market=None, spikes=None):
    p = PhoenixProtectionLayerV1()
    protected, d = p.protect_system(
        pd.DataFrame(top7),
        pd.DataFrame(system),
        market_data=pd.DataFrame(market) if market else None,
        spike_signal=spikes,
    )
    original = {x["start_number"] for x in system if x["in_system"] == 1}
    final = set(protected.loc[protected.in_system.eq(1), "start_number"])
    return original, final, d, winner


def test_rule1_preserves_size_and_recovers_top3():
    top7 = [{"start_number":i, "phoenix_rank":i, "phoenix_score":1.0/i, "phoenix_probability":.2} for i in range(1,8)]
    system = [{"start_number":i, "in_system":1 if i in (5,7) else 0} for i in range(1,8)]
    original, final, d, winner = race(top7, system, 3)
    assert len(final) == len(original)
    assert 3 in final
    assert d["protection_summary"]["system_size_maintained"] is True


def test_rule2_requires_market_rank():
    top7 = [{"start_number":i, "phoenix_rank":i, "phoenix_score":1.0/i, "phoenix_probability":.2} for i in range(1,8)]
    system = [{"start_number":i, "in_system":1 if i in (5,7) else 0} for i in range(1,8)]
    market = [{"start_number":i, "odds_rank":10 if i != 4 else 2} for i in range(1,8)]
    original, final, d, _ = race(top7, system, 4, market=market)
    assert 4 in final
    assert any("Rule 2" in x for x in d["protection_rules_applied"])
    assert len(final) == len(original)


def test_rule3_spik_protection():
    top7 = [{"start_number":i, "phoenix_rank":i, "phoenix_score":1.0/i, "phoenix_probability":.2} for i in range(1,8)]
    system = [{"start_number":i, "in_system":1 if i in (5,7) else 0} for i in range(1,8)]
    original, final, d, _ = race(top7, system, 6, spikes={6:"SPIK"})
    assert 6 in final
    assert any("Rule 3" in x for x in d["protection_rules_applied"])
    assert len(final) == len(original)


def test_no_growth_when_no_swappable_system_candidate():
    top7 = [{"start_number":i, "phoenix_rank":i, "phoenix_score":1.0/i, "phoenix_probability":.2} for i in range(1,8)]
    system = [{"start_number":i, "in_system":1 if i == 1 else 0} for i in range(1,8)]
    original, final, d, _ = race(top7, system, 2)
    assert len(final) == len(original)


def test_protection_does_not_change_top7_input():
    top7 = pd.DataFrame([{"start_number":i, "phoenix_rank":i, "phoenix_score":1.0/i, "phoenix_probability":.2} for i in range(1,8)])
    before = top7.copy(deep=True)
    system = pd.DataFrame([{"start_number":i, "in_system":1 if i in (5,7) else 0} for i in range(1,8)])
    PhoenixProtectionLayerV1().protect_system(top7, system)
    pd.testing.assert_frame_equal(top7, before)

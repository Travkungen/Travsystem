"""Mechanical tests for Phase 2 harness; synthetic only, never historical claims."""
import pandas as pd
from PHOENIX15_PROTECTION_LAYER_v1 import PhoenixProtectionLayerV1

def make_ranked():
    return pd.DataFrame([{"start_number":i,"phoenix_rank":i,"phoenix_score":1/i,"phoenix_probability":.2} for i in range(1,8)])

def make_system(nums):
    return pd.DataFrame([{"start_number":i,"in_system":int(i in nums)} for i in range(1,8)])

def test_rule1_preserves_size_and_recovers_top3():
    p=PhoenixProtectionLayerV1()
    top=make_ranked(); system=make_system([5,7])
    out,d=p.protect_system(top,system)
    assert int(out.in_system.sum())==2
    assert 3 in set(out.loc[out.in_system.eq(1),"start_number"])
    assert d["protection_summary"]["system_size_maintained"]

def test_rule2_uses_market_rank():
    p=PhoenixProtectionLayerV1()
    top=make_ranked(); system=make_system([5,7])
    market=pd.DataFrame([{"start_number":i,"odds_rank":2 if i==4 else 9} for i in range(1,8)])
    out,d=p.protect_system(top,system,market_data=market)
    assert 4 in set(out.loc[out.in_system.eq(1),"start_number"])
    assert any("Rule 2" in x for x in d["protection_rules_applied"])
    assert int(out.in_system.sum())==2

def test_rule3_spik_protection():
    p=PhoenixProtectionLayerV1()
    top=make_ranked(); system=make_system([5,7])
    out,d=p.protect_system(top,system,spike_signal={6:"SPIK"})
    assert 6 in set(out.loc[out.in_system.eq(1),"start_number"])
    assert any("Rule 3" in x for x in d["protection_rules_applied"])
    assert int(out.in_system.sum())==2

def test_multiple_protected_candidates_preserve_size():
    p=PhoenixProtectionLayerV1()
    top=make_ranked(); system=make_system([6,7])
    market=pd.DataFrame([{"start_number":i,"odds_rank":1 if i in (3,4) else 9} for i in range(1,8)])
    out,d=p.protect_system(top,system,market_data=market,spike_signal={5:"SPIK"})
    selected=set(out.loc[out.in_system.eq(1),"start_number"])
    assert len(selected)==2
    assert int(out.in_system.sum())==2
    assert d["protection_summary"]["system_size_maintained"]

def test_no_swappable_candidate_does_not_grow():
    p=PhoenixProtectionLayerV1()
    out,d=p.protect_system(make_ranked(),make_system([1]))
    assert int(out.in_system.sum())==1

def test_same_input_frame_is_unchanged():
    p=PhoenixProtectionLayerV1(); top=make_ranked(); before=top.copy(deep=True)
    p.protect_system(top,make_system([5,7]),spike_signal={3:"SPIK"})
    pd.testing.assert_frame_equal(top,before)

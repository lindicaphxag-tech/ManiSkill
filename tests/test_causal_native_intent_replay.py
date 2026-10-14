import numpy as np
import pytest
from research.causal_native_intent_replay import intent_replay_translation

def impl(current=None,held=None,gate=True):
    current=np.asarray(current if current is not None else [.2,0,0,0,0,0])
    held=np.asarray(held if held is not None else [[.4,0,0,0,0,0],[.4,0,0,0,0,0]])
    return intent_replay_translation(
        current,held,source_low=[-1]*3,source_high=[1]*3,
        target_low=[-1]*3,target_high=[1]*3,alignment_gate=gate)

def test_aligned_causal_intent_is_actual_new_bounded_command():
    u,d=impl()
    assert np.isclose(u[0],.6) and d["actual_command_changed"]
    assert d["replay_mode"]=="aligned_projection"
    assert np.linalg.norm(u[3:])==0

def test_anti_aligned_public_action_is_fail_closed():
    u,d=impl(held=[[-.4,0,0,0,0,0],[-.4,0,0,0,0,0]])
    assert np.isclose(u[0],.2) and not d["actual_command_changed"]
    assert d["replay_mode"]=="direction_mismatch_abstain"

def test_unconditional_control_changes_anti_aligned_motion():
    u,d=impl(held=[[-.4,0,0,0,0,0],[-.4,0,0,0,0,0]],gate=False)
    assert np.isclose(u[0],-.2) and d["actual_command_changed"]

def test_preserves_nonzero_native_euler_command():
    u,d=impl(current=[.5,0,0,.1,-.2,.3],held=[[.4,0,0,0,0,0],[.4,0,0,0,0,0]])
    assert np.array_equal(np.asarray(u[3:]),[.1,-.2,.3])
    assert d["rotational_command_unchanged"]

def test_native_translation_saturation_never_violates_bounds():
    u,d=impl(current=[.95,0,0,0,0,0],held=[[1,0,0,0,0,0],[1,0,0,0,0,0]])
    assert u[0]==1.0 and d["actual_command_changed"]

def test_unequal_physical_scales_respected():
    x,d=intent_replay_translation(
        [.25,0,0,0,0,0],[[.5,0,0,0,0,0],[.5,0,0,0,0,0]],
        source_low=[-.02]*3,source_high=[.02]*3,
        target_low=[-.05]*3,target_high=[.05]*3)
    assert np.isclose(x[0],.45)

def test_zero_and_invalid_native_states_do_not_fabricate_action():
    x,d=impl(current=[0]*6,held=[[0]*6,[0]*6])
    assert not d["actual_command_changed"]
    with pytest.raises(ValueError):impl(held=[[1e9]*6,[1e9]*6])
    with pytest.raises(ValueError):impl(current=[0,0,0,2,0,0])

def test_random_2000_commands_never_mutate_rotation_or_exceed_bounds():
    rng=np.random.default_rng(20261014)
    for _ in range(2000):
        u=rng.uniform(-.95,.95,size=6)
        u[3:]*=.25
        held=rng.uniform(-1,1,(2,6))
        a,_=impl(current=u,held=held,gate=bool(rng.integers(2)))
        assert np.all(np.abs(a[:3])<=1+1e-8)
        assert np.allclose(a[3:],u[3:],rtol=0,atol=0)

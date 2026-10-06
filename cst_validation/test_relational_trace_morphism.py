import numpy as np

from relational_trace_morphism import (
    AffineStateBinding,
    compile_relational_sequence_morphism,
    shared_state_binding,
    verify_sequence,
)
from trace_semantics import joint_position_trace_ir


def test_target_relative_to_absolute_finds_hidden_state_adapter():
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=4,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0]),
        physical_high=np.array([2.0]),
        sim_steps=4,
        interpolate=True,
    )
    binding = shared_state_binding(1)
    cert = compile_relational_sequence_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-1.0]),
        context_high=np.array([1.0]),
        source_hidden_low=np.array([-1.0]),
        source_hidden_high=np.array([1.0]),
    )
    assert cert.algebraically_exact
    assert cert.bounded_on_region
    # q*_s = z_s + 0.1 u_s; absolute target action has physical half-range 2.
    np.testing.assert_allclose(cert.P, [[0.05]], atol=1e-10)
    np.testing.assert_allclose(cert.K, [[0.5]], atol=1e-10)
    np.testing.assert_allclose(cert.Q, [[0.0]], atol=1e-10)
    np.testing.assert_allclose(cert.R, [[1.0]], atol=1e-10)
    np.testing.assert_allclose(cert.r, [0.0], atol=1e-10)


def test_compiled_relation_preserves_long_action_sequence_by_induction():
    rng = np.random.default_rng(20261006)
    d = 2
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=-np.full(d, 0.1),
        physical_high=np.full(d, 0.1),
        sim_steps=5,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=-np.full(d, 2.0),
        physical_high=np.full(d, 2.0),
        sim_steps=5,
        interpolate=True,
    )
    binding = shared_state_binding(d)
    cert = compile_relational_sequence_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=-np.full(d, 0.5),
        context_high=np.full(d, 0.5),
        source_hidden_low=-np.full(d, 0.5),
        source_hidden_high=np.full(d, 0.5),
    )
    assert cert.algebraically_exact
    actions = rng.uniform(-0.5, 0.5, size=(100, d))
    contexts = rng.uniform(-0.5, 0.5, size=(100, d))
    witness = verify_sequence(
        cert,
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        source_actions=actions,
        contexts=contexts,
        source_hidden_initial=np.array([0.1, -0.2]),
    )
    assert witness["max_trace_residual"] < 1e-9
    assert witness["max_goal_residual"] < 1e-9
    assert witness["max_hidden_relation_residual"] < 1e-9


def test_interpolation_mismatch_has_no_sequence_morphism():
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=4,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0]),
        physical_high=np.array([2.0]),
        sim_steps=4,
        interpolate=False,
    )
    binding = shared_state_binding(1)
    cert = compile_relational_sequence_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5]),
        context_high=np.array([0.5]),
        source_hidden_low=np.array([-0.5]),
        source_hidden_high=np.array([0.5]),
    )
    assert not cert.algebraically_exact
    assert not cert.bounded_on_region


def test_exact_sequence_semantics_can_fail_target_action_region_bounds():
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-1.0]),
        physical_high=np.array([1.0]),
        sim_steps=2,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
        sim_steps=2,
        interpolate=True,
    )
    binding = shared_state_binding(1)
    cert = compile_relational_sequence_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-1.0]),
        context_high=np.array([1.0]),
        source_hidden_low=np.array([-1.0]),
        source_hidden_high=np.array([1.0]),
    )
    assert cert.algebraically_exact
    assert not cert.bounded_on_region
    assert cert.target_action_region_low[0] < -1.0
    assert cert.target_action_region_high[0] > 1.0


def test_hidden_relation_can_use_a_different_internal_encoding():
    # Source target memory z stores q*. Target memory stores 2*q*, while both
    # expose the same physical trace/goal. A numeric hidden-equality checker
    # would reject this despite perfect semantic correspondence.
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=1,
        interpolate=False,
    )
    base = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0]),
        physical_high=np.array([2.0]),
        sim_steps=1,
        interpolate=False,
    )
    from trace_semantics import StatefulTraceIR

    target = StatefulTraceIR(
        T_u=base.T_u,
        T_x=base.T_x,
        T_z=np.zeros_like(base.T_z),
        t=base.t,
        G_u=base.G_u,
        G_x=base.G_x,
        G_z=np.zeros_like(base.G_z),
        g=base.g,
        H_u=2.0 * base.H_u,
        H_x=2.0 * base.H_x,
        H_z=np.zeros_like(base.H_z),
        h=2.0 * base.h,
        native_low=base.native_low,
        native_high=base.native_high,
        trace_steps=base.trace_steps,
        name="absolute_with_doubled_internal_reference",
    )
    binding = shared_state_binding(1)
    cert = compile_relational_sequence_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5]),
        context_high=np.array([0.5]),
        source_hidden_low=np.array([-0.5]),
        source_hidden_high=np.array([0.5]),
    )
    assert cert.algebraically_exact
    assert cert.bounded_on_region
    np.testing.assert_allclose(cert.R, [[2.0]], atol=1e-10)

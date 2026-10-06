import numpy as np

from contextual_trace_morphism import (
    AffineContextBinding,
    compile_contextual_trace_morphism,
    shared_current_qpos_binding,
)
from trace_semantics import joint_position_trace_ir


def test_delta_current_to_absolute_compiles_state_conditioned_formula():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
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
    binding = shared_current_qpos_binding(1)
    cert = compile_contextual_trace_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-1.0]),
        context_high=np.array([1.0]),
    )
    assert cert.algebraically_exact
    assert cert.bounded_on_region
    # q* = x + 0.2 u_s and target native u_t = q*/2.
    np.testing.assert_allclose(cert.P, [[0.1]], atol=1e-12)
    np.testing.assert_allclose(cert.Q, [[0.5]], atol=1e-12)
    np.testing.assert_allclose(cert.q, [0.0], atol=1e-12)
    np.testing.assert_allclose(cert.target_region_low, [-0.6], atol=1e-12)
    np.testing.assert_allclose(cert.target_region_high, [0.6], atol=1e-12)


def test_context_region_can_break_global_target_bounds_without_breaking_semantics():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
        sim_steps=3,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0]),
        physical_high=np.array([2.0]),
        sim_steps=3,
        interpolate=True,
    )
    binding = shared_current_qpos_binding(1)
    cert = compile_contextual_trace_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-2.0]),
        context_high=np.array([2.0]),
    )
    assert cert.algebraically_exact
    assert not cert.bounded_on_region
    np.testing.assert_allclose(cert.target_region_low, [-1.1], atol=1e-12)
    np.testing.assert_allclose(cert.target_region_high, [1.1], atol=1e-12)


def test_interpolation_mismatch_has_no_exact_contextual_morphism():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2]),
        physical_high=np.array([0.2]),
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
    binding = shared_current_qpos_binding(1)
    cert = compile_contextual_trace_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5]),
        context_high=np.array([0.5]),
    )
    assert not cert.algebraically_exact
    assert not cert.bounded_on_region
    assert cert.action_map_residual > 0 or cert.context_map_residual > 0


def test_target_relative_delta_exposes_stored_target_in_shared_context():
    source = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=2,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0]),
        physical_high=np.array([2.0]),
        sim_steps=2,
        interpolate=True,
    )
    # c = [current_qpos, source_stored_target].
    source_binding = AffineContextBinding(
        X_c=np.array([[1.0, 0.0]]),
        x_0=np.zeros(1),
        Z_c=np.array([[0.0, 1.0]]),
        z_0=np.zeros(1),
    )
    target_binding = AffineContextBinding(
        X_c=np.array([[1.0, 0.0]]),
        x_0=np.zeros(1),
        Z_c=np.zeros((1, 2)),
        z_0=np.zeros(1),
    )
    cert = compile_contextual_trace_morphism(
        source=source,
        target=target,
        source_binding=source_binding,
        target_binding=target_binding,
        context_low=np.array([-0.5, -0.5]),
        context_high=np.array([0.5, 0.5]),
    )
    assert cert.algebraically_exact
    assert cert.bounded_on_region
    # Source physical goal is stored_target + 0.1 u_s. Target native absolute
    # action divides by its physical half-range 2.0.
    np.testing.assert_allclose(cert.P, [[0.05]], atol=1e-12)
    np.testing.assert_allclose(cert.Q, [[0.0, 0.5]], atol=1e-12)


def test_compiled_region_formula_matches_1000_random_action_context_pairs():
    rng = np.random.default_rng(20261006)
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2, -0.4]),
        physical_high=np.array([0.2, 0.4]),
        sim_steps=5,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0, -2.0]),
        physical_high=np.array([2.0, 2.0]),
        sim_steps=5,
        interpolate=True,
    )
    binding = shared_current_qpos_binding(2)
    cert = compile_contextual_trace_morphism(
        source=source,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5, -0.5]),
        context_high=np.array([0.5, 0.5]),
    )
    assert cert.bounded_on_region

    for _ in range(1000):
        u = rng.uniform(-1.0, 1.0, size=2)
        x = rng.uniform(-0.5, 0.5, size=2)
        ut = cert.transport(u, x)
        st, sg, sn = source.evaluate(u, x, np.zeros(2))
        tt, tg, tn = target.evaluate(ut, x, np.zeros(2))
        np.testing.assert_allclose(tt, st, atol=1e-9)
        np.testing.assert_allclose(tg, sg, atol=1e-9)
        np.testing.assert_allclose(tn, sn, atol=1e-9)

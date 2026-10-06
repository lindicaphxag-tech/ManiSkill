import numpy as np

from global_trace_morphism import (
    compile_global_trace_morphism,
    verify_global_morphism_sample,
)
from trace_semantics import joint_position_trace_ir


def test_compiles_exact_delta_current_to_absolute_morphism_for_whole_box():
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
    x = np.array([0.4])
    cert = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
    )
    assert cert.algebraically_exact
    assert cert.bounded_for_source_box
    assert cert.unique_if_exact
    # physical q* = 0.4 + 0.2 u_s; target native u_t = q*/2.
    np.testing.assert_allclose(cert.P, [[0.1]], atol=1e-12)
    np.testing.assert_allclose(cert.q, [0.2], atol=1e-12)
    np.testing.assert_allclose(cert.target_box_low, [0.1], atol=1e-12)
    np.testing.assert_allclose(cert.target_box_high, [0.3], atol=1e-12)


def test_random_actions_obey_compiled_identity_without_runtime_solver():
    rng = np.random.default_rng(20261006)
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2, -0.1]),
        physical_high=np.array([0.2, 0.1]),
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
    x = np.array([0.3, -0.4])
    cert = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=x,
        source_hidden=np.zeros(2),
        target_state=x,
        target_hidden=np.zeros(2),
    )
    assert cert.bounded_for_source_box
    for _ in range(500):
        u = rng.uniform(-1.0, 1.0, size=2)
        residual = verify_global_morphism_sample(
            cert,
            source=source,
            target=target,
            source_action=u,
            source_state=x,
            source_hidden=np.zeros(2),
            target_state=x,
            target_hidden=np.zeros(2),
        )
        assert residual < 1e-9


def test_interpolation_mismatch_is_structurally_not_exact():
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
    x = np.array([0.4])
    cert = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
    )
    assert not cert.algebraically_exact
    assert not cert.bounded_for_source_box
    assert cert.semantic_map_residual > 0.0


def test_exact_algebra_can_fail_global_native_box_certificate():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-1.0]),
        physical_high=np.array([1.0]),
        sim_steps=2,
        interpolate=False,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=2,
        interpolate=False,
    )
    x = np.array([0.0])
    cert = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
    )
    assert cert.algebraically_exact
    assert not cert.bounded_for_source_box
    assert cert.target_box_low[0] < -1.0
    assert cert.target_box_high[0] > 1.0


def test_context_offset_is_part_of_the_certificate():
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
    cert_a = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=np.array([0.1]),
        source_hidden=np.zeros(1),
        target_state=np.array([0.1]),
        target_hidden=np.zeros(1),
    )
    cert_b = compile_global_trace_morphism(
        source=source,
        target=target,
        source_state=np.array([0.7]),
        source_hidden=np.zeros(1),
        target_state=np.array([0.7]),
        target_hidden=np.zeros(1),
    )
    np.testing.assert_allclose(cert_a.P, cert_b.P, atol=1e-12)
    assert not np.allclose(cert_a.q, cert_b.q)

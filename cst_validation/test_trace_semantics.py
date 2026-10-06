import numpy as np

from trace_semantics import (
    TraceEquivalenceKind,
    compile_trace_transport,
    joint_position_trace_ir,
)


def test_same_interpolation_delta_current_to_absolute_is_exact_trace():
    source = joint_position_trace_ir(
        mode="delta_current",
        physical_low=np.array([-0.2, -0.2]),
        physical_high=np.array([0.2, 0.2]),
        sim_steps=4,
        interpolate=True,
    )
    target = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-2.0, -2.0]),
        physical_high=np.array([2.0, 2.0]),
        sim_steps=4,
        interpolate=True,
    )
    x = np.array([0.4, -0.3])
    cert = compile_trace_transport(
        source=source,
        target=target,
        source_action=np.array([0.5, -0.25]),
        source_state=x,
        source_hidden=np.zeros(2),
        target_state=x,
        target_hidden=np.zeros(2),
    )
    assert cert.kind is TraceEquivalenceKind.EXACT_TRACE
    assert cert.bounded_representable
    np.testing.assert_allclose(cert.target_action, [0.25, -0.175], atol=1e-10)
    np.testing.assert_allclose(cert.target_trace, cert.source_trace, atol=1e-10)
    np.testing.assert_allclose(cert.target_goal, cert.source_goal, atol=1e-10)


def test_equal_endpoint_can_still_be_trace_inequivalent():
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
    # Ignore trace while solving to prove an endpoint-equivalent target exists.
    goal_only = compile_trace_transport(
        source=source,
        target=target,
        source_action=np.array([0.5]),
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
        trace_weight=0.0,
    )
    assert goal_only.kind is TraceEquivalenceKind.GOAL_ONLY
    np.testing.assert_allclose(goal_only.source_goal, [0.5], atol=1e-12)
    np.testing.assert_allclose(goal_only.target_goal, [0.5], atol=1e-12)
    assert goal_only.max_substep_trace_error > 0.25

    # Asking for the full semantics cannot eliminate that structural mismatch
    # with one held target command.
    full = compile_trace_transport(
        source=source,
        target=target,
        source_action=np.array([0.5]),
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
    )
    assert full.kind is not TraceEquivalenceKind.EXACT_TRACE
    assert full.trace_residual_norm > 0.0


def test_delta_target_reference_is_explicit_controller_memory():
    controller = joint_position_trace_ir(
        mode="delta_target",
        physical_low=np.array([-0.1]),
        physical_high=np.array([0.1]),
        sim_steps=2,
        interpolate=False,
    )
    trace, goal, next_hidden = controller.evaluate(
        np.array([0.5]),
        np.array([0.2]),
        np.array([0.8]),
    )
    np.testing.assert_allclose(goal, [0.85], atol=1e-12)
    np.testing.assert_allclose(next_hidden, [0.85], atol=1e-12)
    np.testing.assert_allclose(trace, [0.85, 0.85], atol=1e-12)


def test_native_bounds_can_make_semantically_exact_map_unavailable():
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
    cert = compile_trace_transport(
        source=source,
        target=target,
        source_action=np.array([1.0]),
        source_state=np.array([0.5]),
        source_hidden=np.zeros(1),
        target_state=np.array([0.5]),
        target_hidden=np.zeros(1),
    )
    assert cert.kind is TraceEquivalenceKind.BOUNDED_APPROXIMATION
    assert not cert.bounded_representable
    assert cert.goal_residual_norm > 1.3
    assert cert.native_margin[0] >= -1e-9


def test_zero_delta_makes_interpolate_and_hold_degenerate_equivalent():
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
    # normalized source zero -> physical delta zero because symmetric bounds.
    cert = compile_trace_transport(
        source=source,
        target=target,
        source_action=np.array([0.0]),
        source_state=x,
        source_hidden=np.zeros(1),
        target_state=x,
        target_hidden=np.zeros(1),
    )
    assert cert.kind is TraceEquivalenceKind.EXACT_TRACE
    np.testing.assert_allclose(cert.source_trace, [0.4] * 4, atol=1e-12)


def test_random_exact_family_preserves_all_substep_targets():
    rng = np.random.default_rng(20261006)
    for _ in range(200):
        d = 3
        x = rng.uniform(-0.4, 0.4, size=d)
        action = rng.uniform(-0.5, 0.5, size=d)
        source = joint_position_trace_ir(
            mode="delta_current",
            physical_low=-np.full(d, 0.2),
            physical_high=np.full(d, 0.2),
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
        cert = compile_trace_transport(
            source=source,
            target=target,
            source_action=action,
            source_state=x,
            source_hidden=np.zeros(d),
            target_state=x,
            target_hidden=np.zeros(d),
        )
        assert cert.kind is TraceEquivalenceKind.EXACT_TRACE
        np.testing.assert_allclose(cert.target_trace, cert.source_trace, atol=1e-9)


def test_trace_certificate_does_not_claim_plant_equivalence():
    # API-level regression: certificate fields are controller-semantic
    # observables only. There is intentionally no task-success/safety flag.
    source = joint_position_trace_ir(
        mode="absolute",
        physical_low=np.array([-1.0]),
        physical_high=np.array([1.0]),
        sim_steps=1,
        interpolate=False,
    )
    cert = compile_trace_transport(
        source=source,
        target=source,
        source_action=np.array([0.2]),
        source_state=np.array([0.0]),
        source_hidden=np.array([0.0]),
        target_state=np.array([0.0]),
        target_hidden=np.array([0.0]),
    )
    assert cert.kind is TraceEquivalenceKind.EXACT_TRACE
    assert not hasattr(cert, "safe")
    assert not hasattr(cert, "task_success")

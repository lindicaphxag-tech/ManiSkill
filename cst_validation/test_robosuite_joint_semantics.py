import numpy as np

from contextual_trace_morphism import (
    compile_contextual_trace_morphism,
    shared_current_qpos_binding,
)
from robosuite_joint_semantics import (
    certify_robosuite_delta_affine_region,
    compile_robosuite_delta_goal_partition,
    robosuite_joint_position_ir,
)


def test_default_robosuite_delta_scaling_is_recovered():
    ir = robosuite_joint_position_ir(
        input_type="delta",
        d=1,
        input_min=-1,
        input_max=1,
        output_min=-0.05,
        output_max=0.05,
    )
    trace, goal, nxt = ir.evaluate(
        np.array([0.5]), np.array([0.4]), np.array([0.0])
    )
    np.testing.assert_allclose(goal, [0.425], atol=1e-12)
    np.testing.assert_allclose(trace, goal, atol=1e-12)
    np.testing.assert_allclose(nxt, goal, atol=1e-12)


def test_clipping_inactive_region_is_certified_analytically():
    region = certify_robosuite_delta_affine_region(
        d=1,
        state_low=np.array([-0.5]),
        state_high=np.array([0.5]),
        qpos_limits=np.array([[-1.0], [1.0]]),
    )
    assert region.clip_inactive
    np.testing.assert_allclose(region.unclipped_goal_low, [-0.55], atol=1e-12)
    np.testing.assert_allclose(region.unclipped_goal_high, [0.55], atol=1e-12)


def test_region_crossing_qpos_limit_is_refused_as_single_affine_region():
    region = certify_robosuite_delta_affine_region(
        d=1,
        state_low=np.array([0.96]),
        state_high=np.array([1.0]),
        qpos_limits=np.array([[-1.0], [1.0]]),
    )
    assert not region.clip_inactive
    assert region.unclipped_goal_high[0] > 1.0
    assert "split or refuse" in region.reason


def test_robosuite_delta_to_absolute_contextual_morphism():
    source_region = certify_robosuite_delta_affine_region(
        d=1,
        state_low=np.array([-0.5]),
        state_high=np.array([0.5]),
        qpos_limits=np.array([[-1.0], [1.0]]),
    )
    assert source_region.clip_inactive
    target = robosuite_joint_position_ir(
        input_type="absolute",
        d=1,
        native_absolute_low=np.array([-1.0]),
        native_absolute_high=np.array([1.0]),
    )
    binding = shared_current_qpos_binding(1)
    cert = compile_contextual_trace_morphism(
        source=source_region.ir,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5]),
        context_high=np.array([0.5]),
    )
    assert cert.algebraically_exact
    assert cert.bounded_on_region
    # absolute target action = current qpos + 0.05 * native delta action
    np.testing.assert_allclose(cert.P, [[0.05]], atol=1e-12)
    np.testing.assert_allclose(cert.Q, [[1.0]], atol=1e-12)
    np.testing.assert_allclose(cert.q, [0.0], atol=1e-12)


def test_cross_stack_formula_matches_1000_random_unclipped_cases():
    rng = np.random.default_rng(270)
    source_region = certify_robosuite_delta_affine_region(
        d=2,
        state_low=np.array([-0.5, -0.5]),
        state_high=np.array([0.5, 0.5]),
        qpos_limits=np.array([[-1.0, -1.0], [1.0, 1.0]]),
    )
    target = robosuite_joint_position_ir(
        input_type="absolute",
        d=2,
        native_absolute_low=np.array([-1.0, -1.0]),
        native_absolute_high=np.array([1.0, 1.0]),
    )
    binding = shared_current_qpos_binding(2)
    cert = compile_contextual_trace_morphism(
        source=source_region.ir,
        target=target,
        source_binding=binding,
        target_binding=binding,
        context_low=np.array([-0.5, -0.5]),
        context_high=np.array([0.5, 0.5]),
    )
    assert cert.bounded_on_region
    for _ in range(1000):
        u = rng.uniform(-1, 1, size=2)
        x = rng.uniform(-0.5, 0.5, size=2)
        ut = cert.transport(u, x)
        _, sg, _ = source_region.ir.evaluate(u, x, np.zeros(2))
        _, tg, _ = target.evaluate(ut, x, np.zeros(2))
        np.testing.assert_allclose(tg, sg, atol=1e-12)



def test_piecewise_partition_covers_saturated_robosuite_region():
    limits = np.array([[-1.0], [1.0]])
    partition = compile_robosuite_delta_goal_partition(
        d=1,
        state_low=np.array([0.9]),
        state_high=np.array([1.0]),
        qpos_limits=limits,
    )
    assert len(partition.cells) >= 2

    rng = np.random.default_rng(271)
    for _ in range(1000):
        u = rng.uniform(-1.0, 1.0, size=1)
        x = rng.uniform(0.9, 1.0, size=1)
        compiled = partition.evaluate(np.concatenate([u, x]))
        expected = np.clip(x + 0.05 * u, limits[0], limits[1])
        np.testing.assert_allclose(compiled, expected, atol=1e-9)

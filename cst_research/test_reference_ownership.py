import numpy as np

from reference_ownership import (
    certify_target_reference_ownership,
    target_relative_goal,
)


def test_same_visible_action_can_require_two_different_target_relative_actions():
    q = np.array([0.2, -0.1, 0.5])
    d = np.array([0.04, -0.02, 0.01])
    r_a = np.array([0.2, -0.1, 0.5])
    r_b = np.array([0.35, -0.05, 0.45])

    cert = certify_target_reference_ownership(
        current_qpos=q,
        source_delta=d,
        target_state_a=r_a,
        target_state_b=r_b,
    )

    assert cert.gap_norm > 0
    assert cert.minimax_memoryless_residual_lower_bound > 0
    assert not np.allclose(cert.stateful_action_a, cert.stateful_action_b)

    np.testing.assert_allclose(
        target_relative_goal(r_a, cert.stateful_action_a),
        cert.source_goal,
    )
    np.testing.assert_allclose(
        target_relative_goal(r_b, cert.stateful_action_b),
        cert.source_goal,
    )


def test_memoryless_adapter_has_nonzero_two_history_lower_bound():
    rng = np.random.default_rng(20261008)

    for _ in range(500):
        q = rng.normal(size=7)
        d = rng.normal(scale=0.05, size=7)
        r_a = rng.normal(size=7)
        r_b = rng.normal(size=7)
        cert = certify_target_reference_ownership(
            current_qpos=q,
            source_delta=d,
            target_state_a=r_a,
            target_state_b=r_b,
        )

        # Any one memoryless action v shared by both histories induces goals
        # separated by exactly the hidden target-state gap.  Test many arbitrary
        # shared actions and verify the minimax residual lower bound.
        for _ in range(5):
            v = rng.normal(scale=0.1, size=7)
            residual_a = np.linalg.norm(target_relative_goal(r_a, v) - cert.source_goal)
            residual_b = np.linalg.norm(target_relative_goal(r_b, v) - cert.source_goal)
            assert max(residual_a, residual_b) + 1e-12 >= (
                cert.minimax_memoryless_residual_lower_bound
            )


def test_bound_is_tight_at_midpoint_goal_for_unconstrained_action():
    q = np.array([0.0, 0.0])
    d = np.array([0.1, -0.2])
    r_a = np.array([0.4, -0.1])
    r_b = np.array([-0.2, 0.3])

    cert = certify_target_reference_ownership(
        current_qpos=q,
        source_delta=d,
        target_state_a=r_a,
        target_state_b=r_b,
    )

    # Choose a shared action so the two target goals straddle the desired goal
    # symmetrically.  This realizes the ||r_a-r_b||/2 minimax lower bound.
    v = cert.source_goal - 0.5 * (r_a + r_b)
    residual_a = np.linalg.norm(target_relative_goal(r_a, v) - cert.source_goal)
    residual_b = np.linalg.norm(target_relative_goal(r_b, v) - cert.source_goal)

    np.testing.assert_allclose(residual_a, cert.minimax_memoryless_residual_lower_bound)
    np.testing.assert_allclose(residual_b, cert.minimax_memoryless_residual_lower_bound)


def test_no_hidden_history_gap_means_memoryless_obstruction_disappears():
    q = np.array([0.3])
    d = np.array([0.02])
    r = np.array([0.31])

    cert = certify_target_reference_ownership(
        current_qpos=q,
        source_delta=d,
        target_state_a=r,
        target_state_b=r,
    )

    assert cert.gap_norm == 0
    assert cert.minimax_memoryless_residual_lower_bound == 0
    np.testing.assert_allclose(cert.stateful_action_a, cert.stateful_action_b)

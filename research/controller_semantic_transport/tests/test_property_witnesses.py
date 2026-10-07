import numpy as np

from cst import ControllerState, JointPositionChart, transport_joint_position_action


def _chart(mode, lower, upper, normalized):
    return JointPositionChart(
        mode=mode,
        lower=np.asarray(lower, dtype=float),
        upper=np.asarray(upper, dtype=float),
        normalized=normalized,
    )


def test_randomized_exact_family_transport_preserves_physical_goal():
    rng = np.random.default_rng(20261006)
    modes = ("absolute", "delta_current", "delta_target")

    checked = 0
    for _ in range(5000):
        dof = int(rng.integers(1, 8))
        current = rng.uniform(-0.5, 0.5, size=dof)
        prior_target = current + rng.uniform(-0.1, 0.1, size=dof)
        goal = current + rng.uniform(-0.15, 0.15, size=dof)

        source_mode = modes[int(rng.integers(0, len(modes)))]
        target_mode = modes[int(rng.integers(0, len(modes)))]
        source_normalized = bool(rng.integers(0, 2))
        target_normalized = bool(rng.integers(0, 2))

        source = _chart(
            source_mode,
            [-2.0] * dof if source_mode == "absolute" else [-0.5] * dof,
            [2.0] * dof if source_mode == "absolute" else [0.5] * dof,
            source_normalized,
        )
        target = _chart(
            target_mode,
            [-2.0] * dof if target_mode == "absolute" else [-0.5] * dof,
            [2.0] * dof if target_mode == "absolute" else [0.5] * dof,
            target_normalized,
        )

        source_state = ControllerState(
            current_qpos=current,
            target_qpos=prior_target if source_mode == "delta_target" else None,
        )
        target_state = ControllerState(
            current_qpos=current,
            target_qpos=prior_target if target_mode == "delta_target" else None,
        )

        if source_mode == "absolute":
            payload = goal
        elif source_mode == "delta_current":
            payload = goal - current
        else:
            payload = goal - prior_target

        if source.normalized:
            source_action = (
                payload - 0.5 * (source.upper + source.lower)
            ) / (0.5 * (source.upper - source.lower))
        else:
            source_action = payload

        cert = transport_joint_position_action(
            source_chart=source,
            source_state=source_state,
            source_action=source_action,
            target_chart=target,
            target_state=target_state,
        )

        assert cert.accepted, cert.reason
        np.testing.assert_allclose(cert.source_goal, goal, atol=1e-10)
        np.testing.assert_allclose(cert.reconstructed_goal, goal, atol=1e-10)
        assert cert.semantic_residual <= 1e-10
        checked += 1

    assert checked == 5000

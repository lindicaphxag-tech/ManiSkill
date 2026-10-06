import numpy as np

from cst.core import JointControllerContext, JointGoalChart
from cst.sequence_transport import compile_joint_sequence_transport


def _latched(bound=0.2):
    return JointGoalChart(
        "relative_latched",
        normalized=False,
        lower=-bound,
        upper=bound,
    )


def _target_delta(bound=0.2):
    return JointGoalChart(
        "delta_target",
        normalized=False,
        lower=-bound,
        upper=bound,
    )


def test_lerobot_style_latched_chunk_compiles_exactly_to_delta_target():
    source = _latched()
    target = _target_delta()
    latch = np.array([0.4, -0.2])
    target0 = np.array([0.38, -0.18])
    relative = np.array(
        [
            [0.05, -0.02],
            [0.08, 0.01],
            [0.02, 0.03],
        ]
    )
    result = compile_joint_sequence_transport(
        source_chart=source,
        target_chart=target,
        source_actions=relative,
        source_initial_context=JointControllerContext(q_latched=latch),
        target_initial_context=JointControllerContext(q_target=target0),
    )
    assert result.status == "exact"

    goals = latch + relative
    np.testing.assert_allclose(result.semantic_goals, goals, atol=1e-12)
    expected = np.vstack(
        [
            goals[0] - target0,
            goals[1] - goals[0],
            goals[2] - goals[1],
        ]
    )
    np.testing.assert_allclose(result.target_actions, expected, atol=1e-12)


def test_copying_latched_relative_tensor_into_delta_target_is_semantically_wrong():
    latch = np.array([0.4])
    relative = np.array([[0.05], [0.08], [0.02]])
    desired = latch + relative[:, 0]

    # Naively feeding the same numbers into an accumulating delta-target
    # controller changes the reference after every step.
    q_target = latch.copy()
    naive_goals = []
    chart = _target_delta()
    for action in relative:
        q_target = chart.decode(
            action,
            JointControllerContext(q_target=q_target),
        )
        naive_goals.append(float(q_target[0]))

    assert not np.allclose(naive_goals, desired)


def test_delta_target_chunk_compiles_to_one_fixed_latch_when_all_goals_fit():
    source = _target_delta(bound=0.3)
    target = _latched(bound=0.4)
    source_actions = np.array([[0.05], [0.02], [-0.04]])
    q0 = np.array([0.2])
    latch = np.array([0.18])
    result = compile_joint_sequence_transport(
        source_chart=source,
        target_chart=target,
        source_actions=source_actions,
        source_initial_context=JointControllerContext(q_target=q0),
        target_initial_context=JointControllerContext(q_latched=latch),
    )
    assert result.status == "exact"
    np.testing.assert_allclose(
        result.target_actions[:, 0],
        [0.07, 0.09, 0.05],
        atol=1e-12,
    )


def test_latched_to_delta_target_returns_first_unrepresentable_step():
    source = _latched(bound=1.0)
    target = _target_delta(bound=0.1)
    relative = np.array([[0.05], [0.40], [0.41]])
    result = compile_joint_sequence_transport(
        source_chart=source,
        target_chart=target,
        source_actions=relative,
        source_initial_context=JointControllerContext(q_latched=np.array([0.0])),
        target_initial_context=JointControllerContext(q_target=np.array([0.0])),
    )
    assert result.status == "nonrepresentable"
    assert result.failure_step == 1
    assert result.target_saturation.tolist() == [True]


def test_delta_current_sequence_refuses_without_exogenous_state_trace():
    source = JointGoalChart(
        "delta_current",
        normalized=False,
        lower=-0.2,
        upper=0.2,
    )
    target = JointGoalChart("absolute")
    result = compile_joint_sequence_transport(
        source_chart=source,
        target_chart=target,
        source_actions=np.array([[0.01], [0.02]]),
        source_initial_context=JointControllerContext(),
        target_initial_context=JointControllerContext(),
    )
    assert result.status == "ambiguous"
    assert result.required_source_state == ("source.q_current_trace",)


def test_random_latched_to_target_delta_preserves_goals_when_representable():
    rng = np.random.default_rng(20261006)
    source = _latched(bound=0.15)
    target = _target_delta(bound=0.3)
    for _ in range(500):
        horizon = int(rng.integers(2, 12))
        dim = int(rng.integers(1, 8))
        latch = rng.normal(size=dim)
        # Smooth relative trajectory ensures adjacent differences fit target.
        relative = np.cumsum(
            rng.uniform(-0.03, 0.03, size=(horizon, dim)),
            axis=0,
        )
        relative = np.clip(relative, -0.14, 0.14)
        target0 = latch + rng.uniform(-0.03, 0.03, size=dim)
        result = compile_joint_sequence_transport(
            source_chart=source,
            target_chart=target,
            source_actions=relative,
            source_initial_context=JointControllerContext(q_latched=latch),
            target_initial_context=JointControllerContext(q_target=target0),
        )
        assert result.status == "exact"
        np.testing.assert_allclose(
            result.semantic_goals,
            latch + relative,
            atol=1e-10,
            rtol=0.0,
        )


def test_all_reference_machine_pairs_preserve_physical_goal_trace():
    rng = np.random.default_rng(20261007)
    modes = ("absolute", "delta_current", "delta_target", "relative_latched")

    def chart(mode):
        if mode == "absolute":
            return JointGoalChart(mode, normalized=False)
        return JointGoalChart(
            mode,
            normalized=False,
            lower=-10.0,
            upper=10.0,
        )

    def native_for(mode, goals, current, target0, latch):
        if mode == "absolute":
            return goals.copy()
        if mode == "delta_current":
            return goals - current
        if mode == "relative_latched":
            return goals - latch
        if mode == "delta_target":
            previous = np.vstack([target0, goals[:-1]])
            return goals - previous
        raise AssertionError(mode)

    def initial_context(mode, target0, latch):
        if mode == "delta_target":
            return JointControllerContext(q_target=target0)
        if mode == "relative_latched":
            return JointControllerContext(q_latched=latch)
        return JointControllerContext()

    for source_mode in modes:
        for target_mode in modes:
            for _ in range(40):
                horizon = int(rng.integers(2, 9))
                dim = int(rng.integers(1, 7))
                goals = rng.normal(scale=0.4, size=(horizon, dim))
                source_current = rng.normal(scale=0.3, size=(horizon, dim))
                target_current = rng.normal(scale=0.3, size=(horizon, dim))
                source_target0 = rng.normal(scale=0.3, size=dim)
                target_target0 = rng.normal(scale=0.3, size=dim)
                source_latch = rng.normal(scale=0.3, size=dim)
                target_latch = rng.normal(scale=0.3, size=dim)

                source_actions = native_for(
                    source_mode,
                    goals,
                    source_current,
                    source_target0,
                    source_latch,
                )
                result = compile_joint_sequence_transport(
                    source_chart=chart(source_mode),
                    target_chart=chart(target_mode),
                    source_actions=source_actions,
                    source_initial_context=initial_context(
                        source_mode, source_target0, source_latch
                    ),
                    target_initial_context=initial_context(
                        target_mode, target_target0, target_latch
                    ),
                    source_q_current_trace=(
                        source_current if source_mode == "delta_current" else None
                    ),
                    target_q_current_trace=(
                        target_current if target_mode == "delta_current" else None
                    ),
                )
                assert result.status == "exact", (
                    source_mode,
                    target_mode,
                    result.reason,
                )
                np.testing.assert_allclose(
                    result.semantic_goals,
                    goals,
                    atol=1e-10,
                    rtol=0.0,
                )
                expected_target = native_for(
                    target_mode,
                    goals,
                    target_current,
                    target_target0,
                    target_latch,
                )
                np.testing.assert_allclose(
                    result.target_actions,
                    expected_target,
                    atol=1e-10,
                    rtol=0.0,
                )

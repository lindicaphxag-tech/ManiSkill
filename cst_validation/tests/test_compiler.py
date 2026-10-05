import numpy as np

from cst.compiler import compile_exact_joint_transport
from cst.core import JointControllerContext, JointGoalChart


def test_absolute_to_delta_current_exact_when_goal_in_one_step_image():
    source = JointGoalChart(
        "absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    target = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    result = compile_exact_joint_transport(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.24, -0.32]),
        source_context=JointControllerContext(),
        target_context=JointControllerContext(
            q_current=np.array([0.20, -0.30])
        ),
    )
    assert result.status == "exact"
    np.testing.assert_allclose(result.target_action, [0.4, -0.2], atol=1e-12)
    np.testing.assert_allclose(
        result.decoded_target_goal,
        [0.24, -0.32],
        atol=1e-12,
    )
    assert result.semantic_residual <= 1e-12


def test_source_hidden_reference_returns_constructive_ambiguity_witness():
    source = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    target = JointGoalChart(
        "absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    result = compile_exact_joint_transport(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.25, -0.5]),
        source_context=JointControllerContext(),
        target_context=JointControllerContext(),
    )
    assert result.status == "ambiguous"
    assert result.missing_source_state == ("q_current",)
    assert result.witness_goal_a is not None
    assert result.witness_goal_b is not None
    assert not np.allclose(result.witness_goal_a, result.witness_goal_b)


def test_target_hidden_reference_is_reported_before_guessing_an_action():
    source = JointGoalChart(
        "absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    target = JointGoalChart(
        "delta_target",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    result = compile_exact_joint_transport(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.2]),
        source_context=JointControllerContext(),
        target_context=JointControllerContext(),
    )
    assert result.status == "ambiguous"
    assert result.missing_source_state == ("target.q_target",)


def test_unique_but_unreachable_goal_returns_coordinate_witness():
    source = JointGoalChart(
        "absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    target = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    result = compile_exact_joint_transport(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.35, -0.31]),
        source_context=JointControllerContext(),
        target_context=JointControllerContext(
            q_current=np.array([0.0, -0.30])
        ),
    )
    assert result.status == "nonrepresentable"
    assert result.violating_coordinates == (0,)
    assert abs(result.required_native_action[0]) > 1.0
    assert abs(result.required_native_action[1]) <= 1.0


def test_compiler_is_sound_and_complete_for_random_box_joint_charts():
    rng = np.random.default_rng(20261006)
    source = JointGoalChart(
        "absolute",
        normalized=False,
        lower=None,
        upper=None,
    )
    target = JointGoalChart(
        "delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )

    for _ in range(1000):
        current = rng.uniform(-2.0, 2.0, size=7)
        displacement = rng.uniform(-0.2, 0.2, size=7)
        goal = current + displacement
        result = compile_exact_joint_transport(
            source_chart=source,
            target_chart=target,
            source_action=goal,
            source_context=JointControllerContext(),
            target_context=JointControllerContext(q_current=current),
        )

        mathematically_representable = bool(
            np.all(displacement >= -0.1 - 1e-10)
            and np.all(displacement <= 0.1 + 1e-10)
        )
        assert (result.status == "exact") == mathematically_representable
        if result.status == "exact":
            np.testing.assert_allclose(
                result.decoded_target_goal,
                goal,
                atol=1e-10,
                rtol=0.0,
            )
        else:
            expected = tuple(
                int(i)
                for i in np.flatnonzero(
                    np.abs(displacement / 0.1) > 1.0 + 1e-10
                )
            )
            assert result.violating_coordinates == expected

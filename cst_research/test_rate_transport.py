import numpy as np

from rate_transport import (
    RateDeployability,
    compile_zoh_rate_transport,
)
from reference_semantics import ReferenceKind, ReferenceSemantics


def sem(kind):
    return ReferenceSemantics(kind=kind, relative_mask=np.array([True]))


def test_absolute_zoh_rate_refinement_is_exact_and_precomputable():
    actions = np.array([[1.0], [2.0], [3.0]])
    states = np.zeros_like(actions)
    cert = compile_zoh_rate_transport(
        actions,
        sem(ReferenceKind.ABSOLUTE),
        sem(ReferenceKind.ABSOLUTE),
        source_rate_hz=20,
        target_rate_hz=100,
        source_current_states=states,
    )
    assert cert.deployability is RateDeployability.PRECOMPUTABLE
    assert cert.integer_ratio == 5
    assert cert.max_boundary_goal_error == 0.0
    np.testing.assert_allclose(
        cert.refined_goals[:, 0],
        [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3],
    )


def test_previous_command_naive_repeat_multiplies_delta_but_compiler_does_not():
    actions = np.array([[1.0], [2.0]])
    states = np.zeros_like(actions)
    cert = compile_zoh_rate_transport(
        actions,
        sem(ReferenceKind.PREVIOUS_COMMAND),
        sem(ReferenceKind.PREVIOUS_COMMAND),
        source_rate_hz=20,
        target_rate_hz=100,
        source_current_states=states,
        source_initial_previous_command=np.array([10.0]),
        target_initial_previous_command=np.array([10.0]),
    )
    assert cert.deployability is RateDeployability.PRECOMPUTABLE
    assert cert.max_boundary_goal_error == 0.0
    assert cert.naive_repeat_boundary_error is not None
    assert cert.naive_repeat_boundary_error >= 8.0
    # Correct target deltas are [1,0,0,0,0,2,0,0,0,0], not repeated [1,...,2,...].
    np.testing.assert_allclose(
        cert.target_actions[:, 0],
        [1,0,0,0,0,2,0,0,0,0],
    )


def test_current_state_target_requires_target_rate_step_hook():
    actions = np.array([[1.0], [2.0]])
    source_states = np.array([[10.0], [11.0]])
    cert = compile_zoh_rate_transport(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.CURRENT_STATE),
        source_rate_hz=20,
        target_rate_hz=100,
        source_current_states=source_states,
        source_chunk_anchor=np.array([10.0]),
    )
    assert cert.deployability is RateDeployability.REQUIRES_STEP_HOOK
    assert cert.target_actions is None
    assert cert.max_boundary_goal_error is None


def test_current_state_step_hook_reencodes_each_substep_goal():
    actions = np.array([[1.0], [2.0]])
    source_states = np.array([[10.0], [11.0]])
    # Source chunk anchor => physical goals 11 and 12.
    target_states = np.array(
        [[10.0], [10.5], [10.9], [11.0], [11.0],
         [11.0], [11.4], [11.8], [12.0], [12.0]]
    )
    cert = compile_zoh_rate_transport(
        actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.CURRENT_STATE),
        source_rate_hz=20,
        target_rate_hz=100,
        source_current_states=source_states,
        source_chunk_anchor=np.array([10.0]),
        target_current_states=target_states,
    )
    assert cert.deployability is RateDeployability.REQUIRES_STEP_HOOK
    assert cert.max_boundary_goal_error == 0.0
    np.testing.assert_allclose(
        cert.target_actions[:5, 0],
        11.0 - target_states[:5, 0],
    )
    np.testing.assert_allclose(
        cert.target_actions[5:, 0],
        12.0 - target_states[5:, 0],
    )


def test_chunk_anchor_to_previous_command_at_higher_rate_is_exact():
    source_actions = np.array([[1.0], [2.0], [3.0]])
    source_states = np.array([[10.0], [10.0], [10.0]])
    cert = compile_zoh_rate_transport(
        source_actions,
        sem(ReferenceKind.CHUNK_ANCHOR),
        sem(ReferenceKind.PREVIOUS_COMMAND),
        source_rate_hz=10,
        target_rate_hz=40,
        source_current_states=source_states,
        source_chunk_anchor=np.array([10.0]),
        target_initial_previous_command=np.array([10.0]),
    )
    assert cert.max_boundary_goal_error == 0.0
    np.testing.assert_allclose(cert.source_boundary_goals[:,0], [11,12,13])
    # Each new held goal is entered once; extra controller ticks are zero deltas.
    np.testing.assert_allclose(
        cert.target_actions[:,0],
        [1,0,0,0,1,0,0,0,1,0,0,0],
    )


def test_noninteger_rate_ratio_is_explicitly_out_of_scope():
    try:
        compile_zoh_rate_transport(
            np.array([[1.0]]),
            sem(ReferenceKind.ABSOLUTE),
            sem(ReferenceKind.ABSOLUTE),
            source_rate_hz=30,
            target_rate_hz=100,
            source_current_states=np.zeros((1,1)),
        )
    except ValueError as exc:
        assert "integer" in str(exc)
    else:
        raise AssertionError("noninteger ratio was silently accepted")

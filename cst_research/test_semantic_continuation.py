import numpy as np
import pytest

from reference_semantics import ReferenceKind, ReferenceSemantics
from semantic_continuation import (
    RuntimeSignal,
    SemanticActionContinuation,
)


def sem(kind, mask=(True, True)):
    return ReferenceSemantics(kind=kind, relative_mask=np.array(mask, dtype=bool))


def test_lerobot_3312_chunk_anchor_becomes_explicit_query_capture():
    # A LeRobot-style relative chunk: every offset is relative to state at
    # chunk generation time, even though the physical state moves later.
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0, 0.1], [2.0, 0.2], [3.0, 0.3]]),
        source_semantics=sem(ReferenceKind.CHUNK_ANCHOR, (True, False)),
        target_semantics=sem(ReferenceKind.ABSOLUTE, (True, False)),
        source_chunk_anchor=np.array([10.0, 0.0]),
    )
    plan = cont.dependency_plan()
    assert plan.query_captures == ("source_chunk_anchor",)
    assert plan.step_signals == ()
    assert plan.fully_precomputable

    actions = cont.precompute()
    np.testing.assert_allclose(
        actions,
        [[11.0, 0.1], [12.0, 0.2], [13.0, 0.3]],
    )


def test_moving_state_cannot_corrupt_precomputed_chunk_anchor():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0], [2.0], [3.0]]),
        source_semantics=sem(ReferenceKind.CHUNK_ANCHOR, (True,)),
        target_semantics=sem(ReferenceKind.ABSOLUTE, (True,)),
        source_chunk_anchor=np.array([10.0]),
    )
    expected = cont.precompute()[:, 0]
    moving_states = np.array([10.0, 20.0, 30.0])
    stale_cache_style = np.array([1.0, 2.0, 3.0]) + moving_states

    np.testing.assert_allclose(expected, [11.0, 12.0, 13.0])
    assert np.max(np.abs(stale_cache_style - expected)) == 20.0


def test_maniskill_delta_current_target_declares_step_state_slot():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0], [2.0]]),
        source_semantics=sem(ReferenceKind.CHUNK_ANCHOR, (True,)),
        target_semantics=sem(ReferenceKind.CURRENT_STATE, (True,)),
        source_chunk_anchor=np.array([10.0]),
    )
    plan = cont.dependency_plan()
    assert plan.step_signals == (RuntimeSignal.TARGET_CURRENT_STATE,)
    assert not plan.fully_precomputable

    first = cont.step(target_current_state=np.array([10.5]))
    second = cont.step(target_current_state=np.array([11.4]))
    np.testing.assert_allclose(first.target_native_action, [0.5])
    np.testing.assert_allclose(second.target_native_action, [0.6])
    np.testing.assert_allclose([first.physical_goal, second.physical_goal], [[11.0], [12.0]])


def test_robosuite_desired_goal_target_declares_controller_owned_slot():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0], [2.0]]),
        source_semantics=sem(ReferenceKind.ABSOLUTE, (True,)),
        target_semantics=sem(ReferenceKind.CONTROLLER_TARGET, (True,)),
    )
    plan = cont.dependency_plan()
    assert plan.step_signals == (RuntimeSignal.TARGET_CONTROLLER_TARGET,)

    with pytest.raises(ValueError, match="target_controller_target"):
        cont.step()

    out = cont.step(target_controller_target=np.array([0.25]))
    np.testing.assert_allclose(out.target_native_action, [0.75])


def test_previous_command_only_needs_initial_query_capture_then_self_updates():
    cont = SemanticActionContinuation(
        source_actions=np.array([[11.0], [12.0], [13.0]]),
        source_semantics=sem(ReferenceKind.ABSOLUTE, (True,)),
        target_semantics=sem(ReferenceKind.PREVIOUS_COMMAND, (True,)),
        target_previous_command=np.array([10.0]),
    )
    plan = cont.dependency_plan()
    assert plan.query_captures == ("target_initial_previous_command",)
    assert plan.step_signals == ()
    np.testing.assert_allclose(cont.precompute()[:, 0], [1.0, 1.0, 1.0])


def test_reference_dependency_is_eliminated_when_mask_has_no_relative_dims():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0, 2.0]]),
        source_semantics=sem(ReferenceKind.CURRENT_STATE, (False, False)),
        target_semantics=sem(ReferenceKind.CONTROLLER_TARGET, (False, False)),
    )
    plan = cont.dependency_plan()
    assert plan.query_captures == ()
    assert plan.step_signals == ()
    np.testing.assert_allclose(cont.precompute(), [[1.0, 2.0]])


def test_missing_query_capture_fails_before_execution():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0]]),
        source_semantics=sem(ReferenceKind.CHUNK_ANCHOR, (True,)),
        target_semantics=sem(ReferenceKind.ABSOLUTE, (True,)),
    )
    with pytest.raises(ValueError, match="source_chunk_anchor"):
        cont.step()


def test_source_current_state_is_distinct_from_target_current_state():
    cont = SemanticActionContinuation(
        source_actions=np.array([[1.0]]),
        source_semantics=sem(ReferenceKind.CURRENT_STATE, (True,)),
        target_semantics=sem(ReferenceKind.CURRENT_STATE, (True,)),
    )
    assert cont.dependency_plan().step_signals == (
        RuntimeSignal.SOURCE_CURRENT_STATE,
        RuntimeSignal.TARGET_CURRENT_STATE,
    )
    out = cont.step(
        source_current_state=np.array([10.0]),
        target_current_state=np.array([9.5]),
    )
    np.testing.assert_allclose(out.physical_goal, [11.0])
    np.testing.assert_allclose(out.target_native_action, [1.5])

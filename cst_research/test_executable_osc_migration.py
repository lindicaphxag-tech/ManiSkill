from types import SimpleNamespace
import numpy as np

from executable_osc_migration import (
    MigrationOutcome,
    OSCMigrationRollbackError,
    compile_and_apply_osc_posture_handshake,
    digest_mjcf,
)


class StubOSC:
    def __init__(self, *, input_type, initial_joint):
        self.input_type = input_type
        self.initial_joint = np.asarray(initial_joint, dtype=float)
        self.kp = np.ones(6) * 150.0
        self.kd = np.ones(6) * 24.49
        self.joint_pos = np.array([0.1, 0.2, 0.3, -0.2, -0.1, 0.5, 0.7])
        self.joint_vel = np.zeros(7)
        self.goal_pos = np.array([0.1, 0.2, 0.3]) if input_type == "delta" else np.array([0.9, 0.8, 0.7])
        self.goal_ori = np.eye(3) if input_type == "delta" else np.diag([-1., -1., 1.])
        self._goal_update_mode = "achieved"
        self.impedance_mode = "fixed"
        self.input_ref_frame = "base"
        self.interpolator_pos = None
        self.interpolator_ori = None

    def update_initial_joints(self, initial):
        self.initial_joint = np.asarray(initial, dtype=float).copy()
        # Match real OSC.update_initial_joints -> reset_goal side effect.
        self.goal_pos = np.array([4.0, 5.0, 6.0])
        self.goal_ori = np.eye(3)
        self._goal_update_mode = "achieved"


def _pair():
    a = StubOSC(input_type="delta", initial_joint=[0.1] * 7)
    b = StubOSC(input_type="absolute", initial_joint=[0.3] * 7)
    return a, b


def _run(src, dst, *, model_src=None, model_dst=None):
    x = digest_mjcf("<mujoco model='Panda'/>") if model_src is None else model_src
    y = x if model_dst is None else model_dst
    return compile_and_apply_osc_posture_handshake(
        src, dst, source_mjcf_sha256=x, target_mjcf_sha256=y
    )


def test_transfers_nullspace_memory_and_emits_nontrivial_witness():
    src, dst = _pair()
    c = _run(src, dst)
    assert c.outcome is MigrationOutcome.APPLIED
    assert c.maximum_reference_residual == 0
    assert c.target_reference_before == (0.3,) * 7
    assert c.target_reference_after == (0.1,) * 7
    np.testing.assert_array_equal(dst.initial_joint, src.initial_joint)
    np.testing.assert_array_equal(dst.goal_pos, src.goal_pos)
    np.testing.assert_array_equal(dst.goal_ori, src.goal_ori)


def test_rejects_different_physics_model_before_mutating_target():
    src, dst = _pair()
    original = dst.initial_joint.copy()
    c = _run(src, dst, model_dst=digest_mjcf("<other/>"))
    assert c.outcome is MigrationOutcome.REFUSED
    assert "MJCF" in c.reason
    np.testing.assert_array_equal(dst.initial_joint, original)


def test_rejects_mismatched_controller_gains():
    src, dst = _pair()
    dst.kp[-1] *= 1.1
    c = _run(src, dst)
    assert c.outcome is MigrationOutcome.REFUSED
    assert "kp" in c.reason


def test_rejects_mismatched_physical_joint_state():
    src, dst = _pair()
    dst.joint_pos[2] += 0.03
    c = _run(src, dst)
    assert c.outcome is MigrationOutcome.REFUSED
    assert "joint_pos" in c.reason


def test_rejects_desired_mode_hidden_goal_memory():
    src, dst = _pair()
    dst._goal_update_mode = "desired"
    c = _run(src, dst)
    assert c.outcome is MigrationOutcome.REFUSED
    assert "desired" in c.reason


def test_rejects_unsupported_interpolator_state():
    src, dst = _pair()
    dst.interpolator_ori = object()
    assert _run(src, dst).outcome is MigrationOutcome.REFUSED


def test_rejects_joint_dimension_changes():
    src, dst = _pair()
    dst.initial_joint = np.zeros(6)
    assert _run(src, dst).outcome is MigrationOutcome.REFUSED


def test_rejects_wrong_action_chart_or_controller_semantics():
    src, dst = _pair()
    dst.input_type = "delta"
    assert _run(src, dst).outcome is MigrationOutcome.REFUSED
    dst.input_type = "absolute"
    dst.input_ref_frame = "world"
    assert _run(src, dst).outcome is MigrationOutcome.REFUSED


def test_invalid_and_nonfinite_contracts_are_refused():
    src, dst = _pair()
    dst.kd[0] = float("nan")
    assert _run(src, dst).outcome is MigrationOutcome.REFUSED


def test_partially_written_bad_state_rolls_back_exactly():
    src, dst = _pair()

    class CorruptOnce(StubOSC):
        calls = 0

        def update_initial_joints(self, initial):
            self.calls += 1
            if self.calls == 1:
                self.initial_joint = np.asarray(initial, dtype=float) + 0.01
            else:
                super().update_initial_joints(initial)

    bad = CorruptOnce(input_type="absolute", initial_joint=dst.initial_joint)
    original = bad.initial_joint.copy()
    original_goal = bad.goal_pos.copy()
    original_ori = bad.goal_ori.copy()
    cert = _run(src, bad)
    assert cert.outcome is MigrationOutcome.REFUSED
    assert "rolled back" in cert.reason
    assert bad.calls == 2
    np.testing.assert_array_equal(bad.initial_joint, original)
    np.testing.assert_array_equal(bad.goal_pos, original_goal)
    np.testing.assert_array_equal(bad.goal_ori, original_ori)


def test_partially_applied_controller_exception_still_rolls_back():
    src, dst = _pair()

    class PartialWriteException(StubOSC):
        calls = 0

        def update_initial_joints(self, initial):
            self.calls += 1
            super().update_initial_joints(initial)
            if self.calls == 1:
                raise RuntimeError("device write partially applied")

    bad = PartialWriteException(input_type="absolute", initial_joint=dst.initial_joint)
    original = bad.initial_joint.copy()
    cert = _run(src, bad)
    assert cert.outcome is MigrationOutcome.REFUSED
    np.testing.assert_array_equal(bad.initial_joint, original)


def test_failed_rollback_raises_and_prevents_false_refusal_certificate():
    import pytest
    src, dst = _pair()

    class NeverRetainsRequestedReference(StubOSC):
        def update_initial_joints(self, initial):
            self.initial_joint = np.asarray(initial, dtype=float) + 0.1

    bad = NeverRetainsRequestedReference(input_type="absolute", initial_joint=dst.initial_joint)
    with pytest.raises(OSCMigrationRollbackError, match="quarantined"):
        _run(src, bad)


def test_reject_invalid_digest_without_touching_controller():
    src, dst = _pair()
    original = dst.initial_joint.copy()
    cert = _run(src, dst, model_src="g"*64)
    assert cert.outcome is MigrationOutcome.REFUSED
    np.testing.assert_array_equal(dst.initial_joint, original)



def test_no_mutation_if_required_source_goal_memory_missing():
    src, dst = _pair()
    before=(dst.initial_joint.copy(),dst.goal_pos.copy(),dst.goal_ori.copy())
    src.goal_ori = None
    cert=_run(src,dst)
    assert cert.outcome is MigrationOutcome.REFUSED
    np.testing.assert_array_equal(dst.initial_joint,before[0])
    np.testing.assert_array_equal(dst.goal_pos,before[1])
    np.testing.assert_array_equal(dst.goal_ori,before[2])

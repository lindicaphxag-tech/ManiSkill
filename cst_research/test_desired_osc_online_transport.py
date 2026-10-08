import numpy as np
from scipy.spatial.transform import Rotation

from desired_osc_online_transport import (
    OnlineTransportStatus,
    compile_live_desired_osc_action,
)


class DesiredStubOSC:
    input_type = "delta"
    _goal_update_mode = "desired"
    impedance_mode = "fixed"
    use_ori = True
    interpolator_pos = None
    interpolator_ori = None
    input_min = np.full(6, -1.0)
    input_max = np.full(6, 1.0)
    output_min = np.array([-0.05] * 3 + [-0.5] * 3)
    output_max = -output_min

    def __init__(self):
        self.goal_pos = np.array([0.2, -0.3, 0.15])
        self.goal_ori = Rotation.from_rotvec([0.12, 0.2, 0.04]).as_matrix()


def test_desired_goal_compiles_from_previous_target_not_achieved_pose():
    c = DesiredStubOSC()
    action = np.array([0.4, -0.2, 0.1, 0.2, 0.1, -0.3])
    result = compile_live_desired_osc_action(c, action)
    assert result.status is OnlineTransportStatus.EXECUTABLE_WITH_STEP_HOOK
    np.testing.assert_allclose(result.absolute_action[:3], [0.22, -0.31, 0.155])
    # The online compiler itself does not mutate state.
    np.testing.assert_allclose(c.goal_pos, [0.2, -0.3, 0.15])
    from scipy.spatial.transform import Rotation
    next_ori = Rotation.from_rotvec(result.absolute_action[3:]).as_matrix()
    expected = Rotation.from_rotvec([0.1, 0.05, -0.15]).as_matrix() @ c.goal_ori
    np.testing.assert_allclose(next_ori, expected, atol=1e-12)


def test_missing_goal_memory_fails_closed():
    c = DesiredStubOSC()
    c.goal_pos = None
    r = compile_live_desired_osc_action(c, np.zeros(6))
    assert r.status is OnlineTransportStatus.REFUSE_MISSING_RUNTIME_STATE
    assert r.absolute_action is None


def test_declared_limit_violations_refuse_without_clipping():
    c = DesiredStubOSC()
    r = compile_live_desired_osc_action(c, [1.5, 0, 0, 0, 0, 0])
    assert r.status is OnlineTransportStatus.REFUSE_MISSING_RUNTIME_STATE
    assert "clipping" in r.reason


def test_non_desired_or_non_fixed_mode_is_not_guessed():
    c = DesiredStubOSC()
    c._goal_update_mode = "achieved"
    assert compile_live_desired_osc_action(c, np.zeros(6)).absolute_action is None
    c._goal_update_mode = "desired"
    c.impedance_mode = "variable"
    assert compile_live_desired_osc_action(c, np.zeros(6)).absolute_action is None


def test_rolling_memory_produces_distinct_second_action():
    c = DesiredStubOSC()
    a = np.array([0.5, 0, 0, 0, 0.4, 0])
    first = compile_live_desired_osc_action(c, a)
    c.goal_pos = first.absolute_action[:3].copy()
    c.goal_ori = Rotation.from_rotvec(first.absolute_action[3:]).as_matrix()
    second = compile_live_desired_osc_action(c, a)
    assert second.status is OnlineTransportStatus.EXECUTABLE_WITH_STEP_HOOK
    assert second.absolute_action[0] > first.absolute_action[0]
    assert not np.allclose(second.absolute_action[3:], first.absolute_action[3:])

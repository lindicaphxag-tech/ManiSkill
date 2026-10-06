from types import SimpleNamespace
from unittest.mock import patch

from mani_skill.agents.controllers.pd_ee_pose import PDEEPosController


def make_controller(*, warn_on_ik_failure: bool):
    controller = object.__new__(PDEEPosController)
    controller.config = SimpleNamespace(warn_on_ik_failure=warn_on_ik_failure)
    controller.ik_failure_count = 0
    return controller


def test_ik_failure_counter_increments_without_warning_by_default():
    controller = make_controller(warn_on_ik_failure=False)

    with patch("mani_skill.agents.controllers.pd_ee_pose.logger.warning") as warning:
        controller._record_ik_failure()
        controller._record_ik_failure()

    assert controller.ik_failure_count == 2
    warning.assert_not_called()


def test_ik_failure_warning_is_rate_limited():
    controller = make_controller(warn_on_ik_failure=True)

    with patch("mani_skill.agents.controllers.pd_ee_pose.logger.warning") as warning:
        for _ in range(100):
            controller._record_ik_failure()

    assert controller.ik_failure_count == 100
    assert warning.call_count == 2
    assert "failure count: 1" in warning.call_args_list[0].args[0]
    assert "failure count: 100" in warning.call_args_list[1].args[0]

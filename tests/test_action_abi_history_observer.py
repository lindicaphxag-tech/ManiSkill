"""CPU-only executable contract and adversarial counterexamples for action-history ABI."""
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from research.action_abi_history_observer import (
    ActionHistoryObserver, TargetPose,
)


def observer():
    return ActionHistoryObserver(-0.1, 0.1, -np.pi / 2)


def pose(x=0.0):
    return TargetPose.from_arrays([x, 0, 0], [0, 0, 0, 1])


class ActionHistoryObserverTests(unittest.TestCase):
    def test_reconstruct_acknowledged_position_and_orientation(self):
        o = observer()
        o.reset(pose(0.5))
        a = o.prepare([1, 0, -1, 0, 0, 0.4])
        with self.assertRaises(RuntimeError):
            _ = o.pose
        o.acknowledge(a.ticket, applied=True)
        np.testing.assert_allclose(o.pose.position, [0.6, 0, -0.1], atol=1e-12)
        expected = Rotation.from_euler("XYZ", [0, 0, -0.2*np.pi])
        actual = Rotation.from_quat(o.pose.quaternion_xyzw)
        np.testing.assert_allclose((actual * expected.inv()).as_rotvec(), [0, 0, 0], atol=1e-12)
        b = o.prepare([-1, 0, 1, 0, 0, 0])
        o.acknowledge(b.ticket, applied=True)
        np.testing.assert_allclose(o.pose.position, [0.5, 0, 0], atol=1e-12)

    def test_reset_restores_new_episode_target_and_invalidates_old_ack(self):
        o = observer()
        o.reset(pose())
        old = o.prepare([1, 0, 0, 0, 0, 0]).ticket
        o.reset(pose(0.7))
        a = o.prepare([-1, 0, 0, 0, 0, 0])
        self.assertNotEqual(old, a.ticket)
        with self.assertRaises(RuntimeError):
            o.acknowledge(old, applied=True)
        with self.assertRaises(RuntimeError):
            _ = o.pose
        o.reset(pose(0.3))
        self.assertAlmostEqual(o.pose.position[0], 0.3)

    def test_known_rejection_keeps_previous_target(self):
        o = observer()
        o.reset(pose(0.3))
        req = o.prepare([1, 1, 1, 0, 0, 0])
        o.acknowledge(req.ticket, applied=False)
        self.assertEqual(o.pose, pose(0.3))

    def test_uncertain_delivery_requires_resynchronization(self):
        o = observer()
        o.reset(pose())
        req = o.prepare([0, 1, 0, 0, 0, 0])
        o.acknowledge(req.ticket, applied=None)
        with self.assertRaises(RuntimeError):
            o.prepare([0, 1, 0, 0, 0, 0])
        o.reset(pose(0.9))
        self.assertAlmostEqual(o.pose.position[0], 0.9)

    def test_no_silent_clipping_and_no_hidden_interface_assumption(self):
        o = observer()
        o.reset(pose())
        for action in ([1.5, 0, 0, 0, 0, 0],
                       [0, 0, 0, 1, 1, 1],
                       [float("nan"), 0, 0, 0, 0, 0]):
            with self.subTest(action=action), self.assertRaises(ValueError):
                o.prepare(action)
        for config in ({"frame": "body_translation:body_aligned_body_rotation"},
                       {"use_target": False}, {"normalize_action": False}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                ActionHistoryObserver(-0.1, 0.1, -1.0, **config)

    def test_same_observation_different_hidden_target_needs_different_command(self):
        # Achieved position (the policy sees) and physical goal are identical;
        # previous-command targets differ. One memory-blind delta cannot serve both.
        achieved_x, physical_goal_x = 0.0, 0.04
        prior_target_x = [0.0, 0.07]
        required_physical_delta = [physical_goal_x - p for p in prior_target_x]
        norm = [d / 0.1 for d in required_physical_delta]
        self.assertNotAlmostEqual(norm[0], norm[1])
        self.assertTrue(all(-1 <= u <= 1 for u in norm))
        self.assertEqual(achieved_x, 0.0)

    def test_root_aligned_rotation_composes_on_left(self):
        o = observer()
        q0 = Rotation.from_euler("XYZ", [0.4, -0.2, 0.1]).as_quat()
        o.reset(TargetPose.from_arrays([0, 0, 0], q0))
        ticket = o.prepare([0, 0, 0, 0.3, -0.2, 0.1])
        o.acknowledge(ticket.ticket, applied=True)
        expected = (Rotation.from_euler("XYZ", np.array([0.3, -0.2, 0.1]) * (-np.pi/2))
                    * Rotation.from_quat(q0))
        delta = Rotation.from_quat(o.pose.quaternion_xyzw) * expected.inv()
        np.testing.assert_allclose(delta.as_rotvec(), [0, 0, 0], atol=1e-12)


if __name__ == "__main__":
    unittest.main()

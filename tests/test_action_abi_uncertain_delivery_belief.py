"""Finite-belief target ABI falsification and branch-safe refusal tests."""
import unittest

import numpy as np

from research.action_abi_history_observer import TargetPose
from research.action_abi_uncertain_delivery_belief import (
    UncertainDeliveryBelief, positional_diameter,
)


def pose(x, y=0):
    return TargetPose.from_arrays([x, y, 0], [0, 0, 0, 1])


def belief(max_hypotheses=16):
    return UncertainDeliveryBelief(-0.1, 0.1, -np.pi / 2,
                                   max_hypotheses=max_hypotheses)


class UncertainDeliveryBeliefTests(unittest.TestCase):
    def test_unique_acknowledged_target_exact_native_inverse(self):
        b = belief()
        b.reset(pose(0))
        cert = b.certify_common_exact_action(pose(0.04))
        self.assertTrue(cert.authorized)
        self.assertEqual(cert.possible_targets, 1)
        self.assertAlmostEqual(cert.native_action[0], 0.4)
        token = b.prepare(cert.native_action)
        with self.assertRaises(RuntimeError):
            b.certify_common_exact_action(pose(0.04))
        b.acknowledge(token, applied=True)
        self.assertAlmostEqual(b.hypotheses[0].position[0], 0.04, places=12)

    def test_unknown_delivery_creates_noncollapsible_two_state_belief(self):
        b=belief()
        b.reset(pose(0))
        token=b.prepare([1,0,0,0,0,0])
        b.acknowledge(token, applied=None)
        self.assertEqual(len(b.hypotheses), 2)
        self.assertAlmostEqual(positional_diameter(b.hypotheses), 0.1)
        # Same observed achieved EE pose and intended desired pose, but
        # native inverses differ because prior commanded targets differ.
        cert=b.certify_common_exact_action(pose(0.04))
        self.assertFalse(cert.authorized)
        self.assertEqual(cert.reason,"AMBIGUOUS_PREVIOUS_TARGET")
        self.assertAlmostEqual(cert.maximum_native_spread, 1.0, places=12)
        # Re-applying the same action to all states cannot reduce the
        # unknown translation offset (root-frame delta has no contraction).
        t=b.prepare([0,0,0,0,0,0])
        b.acknowledge(t,applied=True)
        self.assertAlmostEqual(positional_diameter(b.hypotheses),0.1,places=12)

    def test_false_ack_preserves_reset_state(self):
        b=belief()
        b.reset(pose(0))
        t=b.prepare([1,0,0,0,0,0])
        b.acknowledge(t,applied=False)
        self.assertEqual(len(b.hypotheses),1)
        self.assertEqual(b.hypotheses[0],pose(0))

    def test_explicit_target_readback_can_resynchronize(self):
        b=belief()
        b.reset(pose(0))
        t=b.prepare([1,0,0,0,0,0])
        b.acknowledge(t,applied=None)
        self.assertFalse(b.certify_common_exact_action(pose(0.04)).authorized)
        b.require_external_resync(pose(0.1))
        c=b.certify_common_exact_action(pose(0.04))
        self.assertTrue(c.authorized)
        self.assertAlmostEqual(c.native_action[0],-0.6)

    def test_branch_budget_overrun_fails_closed_without_pruning(self):
        b=belief(2)
        b.reset(pose(0))
        t=b.prepare([1,0,0,0,0,0])
        b.acknowledge(t,applied=None)
        self.assertEqual(len(b.hypotheses),2)
        t=b.prepare([0.5,0,0,0,0,0])
        with self.assertRaisesRegex(RuntimeError,"budget"):
            b.acknowledge(t,applied=None)
        with self.assertRaises(RuntimeError):
            b.certify_common_exact_action(pose(0))

    def test_stale_ack_invalidates_all_hypotheses(self):
        b=belief()
        b.reset(pose(0))
        t=b.prepare([1,0,0,0,0,0])
        with self.assertRaisesRegex(RuntimeError,"Stale"):
            b.acknowledge((t[0],t[1]+99),applied=True)
        with self.assertRaises(RuntimeError):
            b.prepare([0,0,0,0,0,0])

    def test_single_state_unrepresentable_exact_goal_rejected(self):
        b=belief()
        b.reset(pose(0))
        c=b.certify_common_exact_action(pose(0.3))
        self.assertFalse(c.authorized)
        self.assertEqual(c.reason, "UNREPRESENTABLE_FOR_A_HYPOTHESIS")

    def test_nonfinite_action_and_pending_guard(self):
        b=belief()
        b.reset(pose(0))
        with self.assertRaises(ValueError):
            b.prepare([np.nan,0,0,0,0,0])
        t=b.prepare([0,0,0,0,0,0])
        with self.assertRaises(RuntimeError):
            b.prepare([0,0,0,0,0,0])
        b.acknowledge(t,applied=True)


if __name__=="__main__":
    unittest.main()

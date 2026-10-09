"""Adversarial tests for real four-history readback invalidation."""
import unittest
from research.action_abi_history_observer import TargetPose
from research.action_abi_uncertain_delivery_belief import UncertainDeliveryBelief
from research.readback_belief_consistency import (
    snapshot, authorize_dispatch, refresh_after_private_read,
)


def pose(x=0.0):
    return TargetPose.from_arrays([x,0,0],[0,0,0,1])


def four_histories():
    b=UncertainDeliveryBelief(-.1,.1,-.1,max_hypotheses=16)
    b.reset(pose(0))
    for action in ([.2,0,0,0,0,0],[-.4,0,0,0,0,0]):
        token=b.prepare(action)
        b.acknowledge(token,applied=None)
    assert len(b.hypotheses)==4
    return b


class AuthoritativeReadbackEpochRegressions(unittest.TestCase):
    def test_two_unknown_executions_create_four_real_memory_hypotheses(self):
        b=four_histories()
        h=snapshot(b)
        self.assertEqual(h.number_hypotheses,4)
        self.assertEqual(authorize_dispatch(b,h).kind,"HYPOTHESIS_SET")
        self.assertEqual(b.epoch,1)

    def test_authoritative_target_invalidates_old_local_branch(self):
        b=four_histories()
        cached=snapshot(b)
        old_cached_maybe_multiple=cached.number_hypotheses>1
        new=refresh_after_private_read(b,pose(0.03))
        self.assertTrue(old_cached_maybe_multiple)
        self.assertEqual(len(b.hypotheses),1)
        self.assertEqual(new.kind,"SINGLE_MEMORY")
        self.assertEqual(new.version.epoch,cached.epoch+1)
        # The bug in the original comparator: it followed the stale old
        # boolean despite the NEW singleton target state.
        refused=authorize_dispatch(b,cached)
        self.assertEqual(refused.kind,"REJECT")
        self.assertIn("STALE_BELIEF_VIEW",refused.explanation)

    def test_command_submission_stales_previous_read_version(self):
        b=four_histories()
        h=snapshot(b)
        t=b.prepare([0,0,0,0,0,0])
        with self.assertRaisesRegex(RuntimeError,"pending"):
            snapshot(b)
        b.acknowledge(t,applied=True)
        self.assertEqual(authorize_dispatch(b,h).kind,"REJECT")
        self.assertEqual(authorize_dispatch(b,snapshot(b)).kind,"HYPOTHESIS_SET")

    def test_second_target_read_invalidates_prior_singleton(self):
        b=four_histories()
        a=refresh_after_private_read(b,pose(.015))
        self.assertEqual(a.kind,"SINGLE_MEMORY")
        c=refresh_after_private_read(b,pose(.025))
        self.assertEqual(c.kind,"SINGLE_MEMORY")
        self.assertEqual(authorize_dispatch(b,a.version).kind,"REJECT")

    def test_bad_provenance_shape_and_pending_fail_closed(self):
        b=four_histories()
        with self.assertRaises(TypeError):
            snapshot(object())
        with self.assertRaises(TypeError):
            authorize_dispatch(b,None)
        t=b.prepare([0,0,0,0,0,0])
        with self.assertRaises(RuntimeError):
            authorize_dispatch(b,snapshot(b) if False else None)
        b.acknowledge(t,applied=None)

    def test_no_offline_float_threshold_tuning_changes_controller_semantics(self):
        b=four_histories()
        a=snapshot(b)
        self.assertEqual(a.number_hypotheses,4)
        out=refresh_after_private_read(b,pose(0.03))
        # All future dispatches must use singleton typed target.
        self.assertNotEqual(a,out.version)
        self.assertEqual(out.version.number_hypotheses,1)
        self.assertEqual(authorize_dispatch(b,out.version).kind,"SINGLE_MEMORY")


if __name__=="__main__":
    unittest.main()

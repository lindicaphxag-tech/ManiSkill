"""Prospective algorithmic unit tests, not claims of physics task success.
Includes a constructive case where a bounded nonzero intervention makes two
overlapping passive response sets separable; and a mandatory zero-gain no-go.
"""
import unittest
from research.robust_native_ack_active_probe import (
    NativeHistory as H,KnownNativeProbe as P,ResponseContract as C,
    min_segments,choose_native_probe,authorize_after_physical_probe)

Q=(0.,0.,0.,1.)
BASE=[
    H("exec",(.05,0.,0.),Q),
    H("held",(.10,0.,0.),Q)]
P0=P("native_zero",(0.,0.,0.,0.,0.,0.),(0.,0.,0.))
PN=P("normalized_nonzero",(0.,.4,0.,0.,0.,0.),(0.,.04,0.))

def model(a=.5,b=1.,eps=.002,current=True,frame=True):
    return C(a,b,eps,.002,current,frame)

def choose(h=BASE,m=None,probes=(P0,PN),max_motion=.05):
    return choose_native_probe(
        (0.,0.,0.),h,probes,model() if m is None else m,
        max_native_target_perturbation_m=max_motion,
        workspace_lower_xyz=(-.2,-.2,-.2),
        workspace_upper_xyz=(.2,.2,.2))

class TrueNativeAckActiveProbeRobustTests(unittest.TestCase):
    def test_3d_line_segment_geometry(self):
        self.assertAlmostEqual(min_segments((0,0,0),(.05,0,0),
                                            (0,.02,0),(.05,.02,0)),.02)
        self.assertAlmostEqual(min_segments((0,0,0),(.1,0,0),
                                            (.05,0,0),(.2,0,0)),0.)
        self.assertAlmostEqual(min_segments((0,0,0),(0,0,0),
                                            (.02,0,0),(.02,0,0)),.02)
    def test_zero_native_response_gain_is_proof_of_no_uniform_identifiability(self):
        r=choose(m=model(a=0))
        self.assertEqual(r.mode,"QUERY_CONTROLLER_TARGET")
        self.assertEqual(r.reason,"ZERO_GAIN_ADMISSIBLE_NO_UNIFORM_IDENTIFIABILITY")
        self.assertEqual(r.additional_physical_native_steps_if_executed,0)
    def test_unvalidated_current_regime_must_not_send_exploratory_robot_action(self):
        r=choose(m=model(current=False))
        self.assertEqual(r.mode,"QUERY_CONTROLLER_TARGET")
        self.assertEqual(r.public_samples_charged_if_executed,0)
    def test_unknown_native_target_chart_must_query(self):
        r=choose(m=model(frame=False))
        self.assertEqual(r.mode,"QUERY_CONTROLLER_TARGET")
    def test_nonzero_actuation_adds_response_direction_information(self):
        # With zero probe, collinear target histories produce response sets
        # touching at x=.05, so no reliable separation at α∈[.5,1].
        none=choose(probes=(P0,))
        self.assertEqual(none.mode,"QUERY_CONTROLLER_TARGET")
        intervention=choose()
        self.assertEqual(intervention.mode,"APPLY_KNOWN_PROBE_AND_OBSERVE")
        self.assertEqual(intervention.probe.label,"normalized_nonzero")
        self.assertGreater(intervention.worst_pairwise_response_set_gap_m,.006)
        self.assertEqual(intervention.public_samples_charged_if_executed,2)
        self.assertEqual(intervention.additional_physical_native_steps_if_executed,1)
    def test_real_observed_response_still_required(self):
        d=choose()
        # The known-delivered nonzero action changes the two targets to
        # (.05,.04) and (.10,.04). α=.75 for the first.
        y=(.0375,.03,0.)
        c=authorize_after_physical_probe(d,(0.,0.,0.),y,
            known_delivered_native_probe_ACK=True,response=model())
        self.assertEqual(c.mode,"CONDITIONAL_FULL_HISTORY_IDENTIFICATION")
        self.assertEqual(c.selected_history_id,"exec")
        self.assertEqual(c.authoritative_native_target_getters_charged_if_fallback,0)
        self.assertTrue(c.not_a_deterministic_robot_safety_guarantee)
    def test_probe_uncertain_delivery_fails_closed_even_with_perfect_XYZ(self):
        c=authorize_after_physical_probe(choose(),(0.,0.,0.),
           (.0375,.03,0.),known_delivered_native_probe_ACK=False,response=model())
        self.assertEqual(c.mode,"QUERY_CONTROLLER_TARGET")
        self.assertEqual(c.authoritative_native_target_getters_charged_if_fallback,1)
    def test_no_model_fit_falls_back_to_counted_native_target_getter(self):
        c=authorize_after_physical_probe(choose(),(0.,0.,0.),
           (.5,.5,.5),known_delivered_native_probe_ACK=True,response=model())
        self.assertEqual(c.mode,"QUERY_CONTROLLER_TARGET")
    def test_same_xyz_different_so3_is_never_identified_by_xyz_only(self):
        histories=[
            H("rot0",(.05,0.,0.),Q),
            H("rotpi",(.05,0.,0.),(0.,0.,1.,0.))]
        r=choose(h=histories)
        self.assertEqual(r.mode,"QUERY_CONTROLLER_TARGET")
    def test_native_motion_and_workspace_cost_limit(self):
        r=choose(probes=(PN,),max_motion=.005)
        self.assertEqual(r.mode,"QUERY_CONTROLLER_TARGET")
    def test_out_of_model_response_regime_may_still_confidently_fool_observer(self):
        # No deterministic model/safety guarantee: after an unobserved
        # physical regime change, achieved public XYZ can look like the WRONG
        # known-target candidate even after a nonzero probe.
        rec=choose()
        after=(.075,.03,0.)  # matches "held" despite "exec" actually true
        out=authorize_after_physical_probe(rec,(0.,0.,0.),after,
            known_delivered_native_probe_ACK=True,response=model())
        self.assertEqual(out.mode,"CONDITIONAL_FULL_HISTORY_IDENTIFICATION")
        self.assertEqual(out.selected_history_id,"held")
    def test_bad_quaternion_and_duplicate_history_provenance_fail_closed(self):
        for histories in ([H("a",(.05,0.,0.),(0.,0.,0.,2.)),BASE[1]],
                         [BASE[0],H("exec",(.1,0.,0.),Q)]):
            with self.assertRaises(ValueError):
                choose(h=histories)

if __name__=="__main__":
    unittest.main()

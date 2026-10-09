"""Adversarial correctness tests. NOT real-robot task efficacy experiments."""
import unittest
from math import pi
from research.regime_conditional_authority import (
    Probe, ResponseTube, PublicMotion, RegimeConditionalAuthority,
)

ID=(0.,0.,0.,1.)
QZ180=(0.,0.,1.,0.)

def probe(*,verified=True,known=True,effort=.2):
    return Probe("known_native_0",(.1,0.,0.,0.,0.,0.),
                 verified,known,effort,2)

def tubes(
    position_shift=False, rotation_separated=True,
    cross_regime_overlap=False, more_than_one_regime=False,
):
    regs=["nominal","shift"] if more_than_one_regime else ["nominal"]
    out=[]
    for regime in regs:
        for h in ("h0","h1"):
            xyz=(0.,0.,0.) if not position_shift else (
                (0.,0.,0.) if h=="h0" else (1.,0.,0.))
            if cross_regime_overlap:
                # Unobserved response regime can exchange the public physical
                # responses of the two hidden target histories.
                xyz=(0.,0.,0.) if ((h=="h0")==(regime=="nominal")) else (1.,0.,0.)
            q=ID if h=="h0" or not rotation_separated else QZ180
            if cross_regime_overlap:q=ID
            out.append(ResponseTube("known_native_0",h,regime,xyz,q,.02,.1))
    return tuple(out)

def build(*,cross=False,position=False,rotation=True,regimes=False,
          calibrated=True,chart=True,history=True,probes=None,model_tubes=None,
          max_norm=1.0):
    return RegimeConditionalAuthority(
        ("h0","h1"),("nominal","shift") if regimes else ("nominal",),
        tuple(probes if probes is not None else (probe(),)),
        tuple(model_tubes if model_tubes is not None else
              tubes(position_shift=position,rotation_separated=rotation,
                    cross_regime_overlap=cross,more_than_one_regime=regimes)),
        registered_contract_verified=chart,history_complete_and_fresh=history,
        independent_calibration_witness_available=calibrated,
        max_native_probe_norm=max_norm,
    )

def obs(*,q=ID,pos=(0.,0.,0.),confirmed=True,actual=2,step=4,probe_id="known_native_0"):
    return PublicMotion(probe_id,pos,q,confirmed,step,actual)

class TestRegimeConditionalAuthority(unittest.TestCase):
    def test_real_so3_public_witness_can_disambiguate_without_private_target(self):
        engine=build()
        p=engine.choose_probe()
        self.assertEqual(p.decision,"EXECUTE_KNOWN_DELIVERED_PROBE")
        decision=engine.authorize_from_real_public_motion(p,obs(),current_step=4)
        self.assertEqual((decision.action,decision.selected_history_id,decision.authoritative_private_reads_required),
                         ("AUTHORIZE_EMPIRICAL","h0",0))
        self.assertFalse(decision.empirical_model_validity_guaranteed)
        self.assertFalse(decision.hardware_safety_guaranteed)

    def test_wrong_orientation_selects_other_complete_history(self):
        engine=build()
        p=engine.choose_probe()
        d=engine.authorize_from_real_public_motion(p,obs(q=QZ180),current_step=4)
        self.assertEqual((d.selected_history_id,d.action),("h1","AUTHORIZE_EMPIRICAL"))

    def test_identical_xyz_and_quat_cannot_authorize(self):
        engine=build(rotation=False)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_response_regime_shift_makes_histories_indistinguishable(self):
        engine=build(cross=True,rotation=False,regimes=True)
        p=engine.choose_probe()
        self.assertEqual(p.decision,"READ_AUTHORITATIVE")
        self.assertLessEqual(p.conservative_min_sep_ratio,1.0)

    def test_model_unsupported_after_physical_response_fails_closed(self):
        engine=build()
        plan=engine.choose_probe()
        r=engine.authorize_from_real_public_motion(plan,obs(pos=(2.,0.,0.)),current_step=4)
        self.assertEqual((r.action,r.reason,r.authoritative_private_reads_required),
                         ("READ","MODEL_UNSUPPORTED",1))

    def test_no_independent_calibration_is_untrusted(self):
        engine=build(calibrated=False)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_stale_observation_must_not_select_history(self):
        engine=build()
        p=engine.choose_probe()
        d=engine.authorize_from_real_public_motion(p,obs(),current_step=5)
        self.assertEqual((d.action,d.reason),("READ","STALE_PHYSICAL_PUBLIC_EVIDENCE"))

    def test_delivery_ambiguity_of_probe_cannot_authorize(self):
        engine=build()
        p=engine.choose_probe()
        d=engine.authorize_from_real_public_motion(p,obs(confirmed=False),current_step=4)
        self.assertEqual(d.reason,"ACTUAL_PUBLIC_PROBE_DELIVERY_NOT_CONFIRMED")

    def test_extra_public_probe_sample_cost_is_not_silently_zero(self):
        engine=build()
        p=engine.choose_probe()
        self.assertEqual(p.predicted_sensor_sample_events,2)
        d=engine.authorize_from_real_public_motion(p,obs(actual=1),current_step=4)
        self.assertEqual((d.action,d.reason,d.actual_sensor_sample_events),
                         ("READ","INCOMPLETE_ACTUAL_PUBLIC_SENSOR_TRANSCRIPT",1))

    def test_unverified_native_action_chart_never_actuates(self):
        engine=build(probes=[probe(verified=False)])
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_unbounded_native_proposal_never_actuates(self):
        engine=build(probes=[probe(effort=10.)],max_norm=1.)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_unconfirmed_native_probe_delivery_never_actuates(self):
        engine=build(probes=[probe(known=False)])
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_missing_response_regime_does_not_optimistically_impute(self):
        model=tubes(more_than_one_regime=True)[:-1]
        engine=build(regimes=True,model_tubes=model)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_no_controller_provenance_refuses(self):
        engine=build(chart=False)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_incomplete_hypothesis_set_refuses(self):
        engine=build(history=False)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_quaternion_double_cover_not_spurious_discriminability(self):
        model=(
            ResponseTube("known_native_0","h0","nominal",(0.,0.,0.),ID,.02,.1),
            ResponseTube("known_native_0","h1","nominal",(0.,0.,0.),tuple(-v for v in ID),.02,.1),
        )
        engine=build(model_tubes=model)
        self.assertEqual(engine.choose_probe().decision,"READ_AUTHORITATIVE")

    def test_invalid_prediction_radius_and_duplicate_regime_fail(self):
        with self.assertRaises(ValueError):
            ResponseTube("p","h","r",(0.,0.,0.),ID,-1.,.1)
        with self.assertRaises(ValueError):
            build(model_tubes=tuple(tubes())+tuple(tubes()))

    def test_public_observation_must_be_finite_and_valid(self):
        with self.assertRaises(ValueError):
            obs(pos=(float("nan"),0.,0.))
        with self.assertRaises(ValueError):
            obs(q=(0.,0.,0.,0.))

    def test_wrong_probe_identity_cannot_authorize(self):
        engine=build()
        p=engine.choose_probe()
        d=engine.authorize_from_real_public_motion(p,obs(probe_id="different_action"),current_step=4)
        self.assertEqual((d.action,d.reason),("READ","ACTUAL_PUBLIC_PROBE_DELIVERY_NOT_CONFIRMED"))

if __name__=="__main__":
    unittest.main()

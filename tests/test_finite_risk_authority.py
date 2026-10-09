"""Adversarial checks: never certify trivial query-all or selected risky method."""
import unittest
from dataclasses import replace
from research.finite_risk_authority import (
  upper_cp,lower_cp,native_public_score,LabelledCalibration,
  calibrate_authority,authorize_online,required_zero_error_authorizations
)

def make(task,seed,score=.8,good=True,original=True):
    truth=("held/held","held/applied","applied/held","applied/applied")[seed%4]
    return LabelledCalibration(task,seed,score,original,good,truth)

class TestNativeLatentRiskCoverage(unittest.TestCase):
    def test_exact_finite_binomial_endpoints(self):
        self.assertAlmostEqual(upper_cp(0,16,.05),1-.05**(1/16))
        self.assertAlmostEqual(lower_cp(16,16,.05),.05**(1/16))
        self.assertEqual(upper_cp(1,1,.05),1.)
        self.assertEqual(upper_cp(0,0,.05),1.)
        self.assertEqual(lower_cp(0,16,.05),0.)
        self.assertGreater(upper_cp(1,16,.05),.26)

    def test_one_wrong_of_16_cannot_be_promoted_to_safe_risk_claim(self):
        rows=[make("pull_cube",i,good=i!=15) for i in range(16)]
        rows += [make("stack_cube",100+i) for i in range(16)]
        c=calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
          thresholds=[0.,.25,.5,1.],risk_cap=.05,minimum_coverage=.05)
        self.assertFalse(c.certified)
        self.assertIsNone(c.threshold)
        self.assertFalse(authorize_online(.99,"pull_cube",True,True,c))

    def test_degenerate_always_privileged_read_is_NOT_certified(self):
        rows=[make("pull_cube",i,original=False) for i in range(180)]
        rows += [make("stack_cube",200+i,original=False) for i in range(180)]
        c=calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
          thresholds=[0.,.5],risk_cap=.05,minimum_coverage=.1)
        self.assertFalse(c.certified)
        self.assertEqual(c.selected_bounds,())

    def test_large_successful_calibration_and_offline_online_firewall(self):
        rows=[make("pull_cube",i) for i in range(160)]
        rows += [make("stack_cube",1000+i) for i in range(160)]
        c=calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
          thresholds=[0.,.25,.5,1.],risk_cap=.05,minimum_coverage=.4)
        self.assertTrue(c.certified)
        self.assertEqual(c.threshold,0.)
        self.assertTrue(authorize_online(.8,"pull_cube",True,True,c))
        for args in [
          (.8,"unseen_task",True,True),
          (.8,"pull_cube",False,True),
          (.8,"pull_cube",True,False),
          (float("nan"),"pull_cube",True,True)
        ]:
            self.assertFalse(authorize_online(*args,c))

    def test_one_bad_task_cannot_be_diluted_by_other_easy_task(self):
        rows=[make("pull_cube",i) for i in range(240)]
        rows += [make("stack_cube",2000+i,good=i%5!=0) for i in range(160)]
        c=calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
          thresholds=[0.,.25,.5],risk_cap=.1,minimum_coverage=.1)
        self.assertFalse(c.certified)

    def test_finite_grid_selection_pays_multiple_testing_correction(self):
        rows=[make("pull_cube",i,score=.1 if i<30 else .85,
                   good=i>=30) for i in range(210)]
        rows += [make("stack_cube",1000+i,score=.1 if i<30 else .85,
                   good=i>=30) for i in range(210)]
        c=calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
          thresholds=[0.,.25,.5,1.],risk_cap=.05,minimum_coverage=.4)
        self.assertTrue(c.certified)
        self.assertEqual(c.threshold,.25)
        self.assertFalse(authorize_online(.15,"pull_cube",True,True,c))
        self.assertTrue(authorize_online(.9,"stack_cube",True,True,c))

    def test_public_score_never_needs_hidden_controller_state(self):
        rs=[.0039247453,.0121384608,.0245013757,.0092696410]
        score=native_public_score(rs,.00694,.002,0,True)
        self.assertGreater(score,0.)
        self.assertEqual(native_public_score(rs,.00694,.002,0,False),float("-inf"))
        with self.assertRaises(ValueError):
            native_public_score([float("nan"),.1],.01,.002,0,True)
        with self.assertRaises(ValueError):
            native_public_score([.01],.01,.002,0,True)

    def test_duplicated_reused_seed_and_missing_truth_refused(self):
        rows=[make("pull_cube",1),make("pull_cube",1),make("stack_cube",2)]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            calibrate_authority(rows,tasks=["pull_cube","stack_cube"],
              thresholds=[0.],risk_cap=.2,minimum_coverage=.2)
        with self.assertRaises(ValueError):
            calibrate_authority(rows[:1],tasks=["pull_cube","stack_cube"],
              thresholds=[0.,0.],risk_cap=.2,minimum_coverage=.2)
        with self.assertRaises(ValueError):
            calibrate_authority([replace(make("pull_cube",1),true_history_matches_candidate=None),make("stack_cube",2)],
              tasks=["pull_cube","stack_cube"],thresholds=[0.],
              risk_cap=.2,minimum_coverage=.2)

    def test_numerically_stable_at_large_4096_reset_calibration(self):
        for n in (1024,2048,4096):
            hi=upper_cp(0,n,.003125)
            lo=lower_cp(n//4,n,.003125)
            self.assertTrue(0 < hi < .01,(n,hi))
            self.assertTrue(.20 < lo < .25,(n,lo))
        self.assertLess(upper_cp(0,4096,.003125),upper_cp(0,1024,.003125))

    def test_first_actual_640_physx_source_uses_only_public_score_no_fake_retraining(self):
        from research.audit_original640_public_risk_score import descriptive_only
        r=descriptive_only()
        self.assertEqual(r["original_source_PhysX_worlds"],640)
        self.assertEqual(r["original_unique_task_reset_states"],64)
        self.assertEqual(r["original_public_admissions"],16)
        self.assertEqual(r["original_wrong_full_history_admissions"],1)
        self.assertTrue(r["risk_threshold_grid_selected_after_old_witness_was_known"])
        self.assertTrue(r["future_fresh_risk_certificate_not_issued"])
        w=r["original_wrong_full_pose_witness"]["pull_cube:1760020"]
        self.assertEqual(w["actual_original_selected_index"],0)
        self.assertEqual(w["actual_audit_only_true_history_indices"],[3])
        self.assertGreater(w["public_score_not_privileged_truth"],0.)
        self.assertGreater(w["original_full_pose_error"][0],.06)

    def test_prospectively_required_accepted_count_calculation(self):
        n=required_zero_error_authorizations(risk_cap=.05,delta=.05,
                                              threshold_count=4,task_count=2)
        tail=.05/(2*4*2)
        self.assertGreaterEqual(n,100)
        self.assertLessEqual(upper_cp(0,n,tail),.05+1e-12)
        self.assertGreater(upper_cp(0,n-1,tail),.05)

if __name__=="__main__":unittest.main()

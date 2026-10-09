"""Separate source-frozen V1 contamination veto; the V2 study is NOT run."""
import unittest
from unittest.mock import patch
from research.audit_future_authority_risk_cohort_leakage import (
    V1,V2,verify,full_range,signed_git_blob,ROOT
)

ORIGINAL_FACT={
    "pre_outcome":True,
    "seeds":{"pull_cube":[2110001,2110016],"stack_cube":[2120001,2120016]}
}

class FutureRiskStudyCohortIntegrity(unittest.TestCase):
    def test_actual_source_V1_conflicts_32_disclosed(self):
        x=verify(ORIGINAL_FACT)
        self.assertEqual(x["v1_number_preexposed"],32)
        self.assertEqual(x["v2_calibration_ids"],512)
        self.assertEqual(x["v2_test_ids"],256)
        self.assertFalse(x["actual_v2_physx_data_executed"])
        self.assertEqual(x["v1_exposed_original_calibration_identifiers"]["pull_cube"][0],2110001)
        self.assertEqual(x["v1_exposed_original_calibration_identifiers"]["stack_cube"][-1],2120016)

    def test_cannot_replace_original_study_seed_registration(self):
        changed={"pre_outcome":True,"seeds":{"pull_cube":[2119999,2120014],"stack_cube":[2120001,2120016]}}
        with self.assertRaisesRegex(ValueError,"Expected real physical source collision changed"):
            verify(changed)

    def test_modified_V1_exact_git_blob_is_refused(self):
        with patch("research.audit_future_authority_risk_cohort_leakage.subprocess.check_output",
                   return_value="badsha"):
            with self.assertRaisesRegex(ValueError,"Mutated original"):
                signed_git_blob(ROOT,V1,"f79df84a1841e7ddab1331ffa7fad39e72787946")

    def test_fail_closed_if_missing_prefrozen_physics_truth(self):
        bad=dict(ORIGINAL_FACT,pre_outcome=False)
        with self.assertRaisesRegex(ValueError,"preoutcome-frozen"):
            verify(bad)

    def test_incomplete_or_reversed_seed_ranges_rejected(self):
        for pair in [[1,0],[1,1.2],[-1,4],[5],["1",2]]:
            with self.assertRaises(ValueError):
                full_range(pair)
if __name__=="__main__":unittest.main()

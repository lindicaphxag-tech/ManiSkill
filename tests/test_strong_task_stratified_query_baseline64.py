"""Checks against promoting a posthoc task-conditioned PhysX arm splice as new trials."""
import copy
import json
import unittest
from pathlib import Path
from research.frozen_policy_transfer.review.strong_task_stratified_query_baseline64 import audit_and_compare

FILE=Path(__file__).resolve().parents[1]/"research/frozen_policy_transfer/review/original_64_compound_ack_task_shard_logged_summaries.json"

class ReviewerBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=json.loads(FILE.read_text())

    def test_original_eight_untouched_phyxs_shards(self):
        r=audit_and_compare(self.record)
        assert r["actual_native_physx_distinct_state_count"]==64
        assert len(r["original_8_actual_job_ids"])==8
        assert r["actually_run_evidence_triggered"]=={"native_task_successes":45,"privileged_target_reads":44}
        assert r["actually_run_fixed_step4"]=={"native_task_successes":55,"privileged_target_reads":64}

    def test_strong_simple_task_rule_is_NOT_a_new_physical_run(self):
        r=audit_and_compare(self.record)
        x=r["posthoc_task_conditioned_not_executed"]
        assert x["native_task_successes_composed_from_original_results"]==55
        assert x["privileged_reads_composed_from_original_results"]==55
        assert x["fewer_privileged_reads_than_original_fixed"]==9
        assert x["original_state_success_vector_identical_to_fixed_step4"]
        assert x["NOT_prospectively_tested_as_single_controller"]
        assert abs(r["observed_aggregate_query_cost_crossover_lambda_vs_reactive"]-10/11)<1e-12

    def test_modified_shard_seed_and_job_id_fail_closed(self):
        for name,value in [("original_github_actions_job_id",-1),
                           ("registered_seed_end",999999),
                           ("task","stack_cube"),
                           ("maximum_actual_candidate_previous_targets",2),
                           ("provenance","fabricated")]:
            altered=copy.deepcopy(self.record)
            altered["rows"][0][name]=value
            with self.assertRaises(ValueError):audit_and_compare(altered)
        altered=copy.deepcopy(self.record);altered["rows"].pop()
        with self.assertRaises(ValueError):audit_and_compare(altered)

    def test_forged_success_query_and_fault_access_fail(self):
        original=self.record
        changes=[
            ("native_task_success_counts","fault_robust_then_single_privileged_query",7),
            ("all_target_controller_faults_physically_reached_after_double_native_hold","fault_robust_then_single_privileged_query",7)
        ]
        for section,key,value in changes:
            altered=copy.deepcopy(original)
            altered["rows"][0][section][key]=value
            with self.assertRaises(ValueError):audit_and_compare(altered)
        for changed in [[2,0,0,1,0,1,1,1], [1,0,0]]:
            altered=copy.deepcopy(original)
            altered["rows"][0]["evidence_triggered_readbacks_per_original_seed"]=changed
            with self.assertRaises(ValueError):audit_and_compare(altered)

if __name__=="__main__":
    unittest.main()

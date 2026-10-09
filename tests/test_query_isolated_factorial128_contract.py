"""Adversarial CPU-only tests for source-frozen 128 physically matched 2x2 plan.

Fixtures below are EXPLICITLY SYNTHETIC. They are contract tests, NOT
physical trial results. All actual claims require original native PhysX.
"""
from __future__ import annotations
import copy,unittest
from research.run_query_isolated_factorial128 import (
    TASKS,MODELS,ARMS,REG,selected,validate_shard,frozen_preflight
)
from research.audit_query_isolated_same_reset_factorial128 import (
    _swap_exact,bootstrap_cluster_risk
)

def fabricated_original(task="pull_cube",chunk=0,truth=0):
    rows=[]
    for seed in selected(task,chunk):
        faults={a:[{"step":2},{"step":3}] for a in ARMS}
        posed={"valid_exact_prefix":True,
               "audit_only_hidden_target_not_a_method_input":True,
               "native_fault_dispatch_linf_each":[0.,0.],
               "pre_t5_achieved_position_max_abs_m":0.,
               "pre_t5_achieved_orientation_geodesic_rad":0.,
               "pre_t5_target_position_max_abs_m":0.,
               "pre_t5_target_orientation_geodesic_rad":0.}
        rows.append({
         "seed":seed,
         "initial_source_physical_obs_sha256":"f"*64,
         "original_precommitted_physical_t2_execution_truth":"applied" if truth in (1,3) else "held",
         "original_precommitted_physical_t3_execution_truth":"applied" if truth in (2,3) else "held",
         "success_once":{a:False for a in ARMS},
         "privileged_target_readback_decision_count":{a:1 for a in ARMS},
         "public_motion_observation_cost_samples":{a:(0 if a==ARMS[2] else 2) for a in ARMS},
         "faults":faults,
         "shared_neutral_probe_step4":{a:{"physically_dispatched":True} for a in ARMS},
         "matched_prefix_physical_audit":copy.deepcopy(posed),
         "matched_posterior_prefix_audit":copy.deepcopy(posed),
         "public_t3_evidence":{"authorized":False,"wrong_confident":False,
           "audit_only_hidden_target_was_NOT_decision_input":True},
         "same_sensor_posterior_evidence":{"authorized":False,"wrong_confident":False,
           "audit_only_hidden_target_was_NOT_decision_input":True,
           "posterior_threshold_predeclared":.95},
        })
    return {
      "schema":"frozen_ppo_matched_prefix_native_2x2_four_truth_v1",
      "real_physx_simulator":True,
      "frozen_model_retrained":False,
      "task":TASKS[task][0],
      "original_external_frozen_checkpoint_sha256":MODELS[task],
      "frozen_protocol":"research/ISOLATED_QUERY_FACTORIAL128_PREOUTCOME_V1.json",
      "all_nine_actual_control_arms":list(REG),
      "original_seed_population":selected(task,chunk),
      "episodes":rows,
    }

class ReviewCausalIsolationPreregistration(unittest.TestCase):
    def test_exact_frozen_source_is_original_published_640_policy(self):
        p=frozen_preflight()
        self.assertEqual(p["expected_actual_native_controller_worlds"],1280)
        self.assertTrue(p["created_before_any_new_physx_outcome"])
    def test_unseen_32_seed_register(self):
        for task in TASKS:
            self.assertEqual(len(set(selected(task,0)+selected(task,1))),16)
        with self.assertRaises(ValueError):selected("pull_cube",2)
        with self.assertRaises(ValueError):selected("fiction",0)
    def test_synthetic_single_physical_shard_verifier_positive_control_not_evidence(self):
        q=fabricated_original(truth=2)
        r=validate_shard(q,"pull_cube",0,2)
        self.assertEqual(r["n_original_actual_controller_worlds"],80)
        self.assertTrue(r["all_8_valid_matched_A_B_C_native_prefixes"])
    def test_dropped_negative_reset_is_hard_failure(self):
        q=fabricated_original()
        q["episodes"].pop()
        with self.assertRaisesRegex(ValueError,"Dropped"):validate_shard(q,"pull_cube",0,0)
    def test_actual_fault_truth_wrong_does_not_count_as_physical_treatment(self):
        q=fabricated_original(truth=1)
        q["episodes"][0]["original_precommitted_physical_t3_execution_truth"]="applied"
        with self.assertRaisesRegex(ValueError,"ACK truth"):validate_shard(q,"pull_cube",0,1)
    def test_target_SE3_delta_invalidates_matched_causal_claim(self):
        q=fabricated_original()
        q["episodes"][2]["matched_prefix_physical_audit"]["pre_t5_target_orientation_geodesic_rad"]=.002
        with self.assertRaisesRegex(ValueError,"mismatched physical"):validate_shard(q,"pull_cube",0,0)
    def test_hidden_native_action_difference_invalidates_causal_claim(self):
        q=fabricated_original()
        q["episodes"][0]["matched_posterior_prefix_audit"]["native_fault_dispatch_linf_each"][1]=.25
        with self.assertRaisesRegex(ValueError,"mismatched physical"):validate_shard(q,"pull_cube",0,0)
    def test_hidden_private_read_is_counted(self):
        q=fabricated_original()
        q["episodes"][2]["public_t3_evidence"]["authorized"]=True
        with self.assertRaisesRegex(ValueError,"authorized and queried"):validate_shard(q,"pull_cube",0,0)
    def test_public_sensor_cost_and_neutral_probe_not_free(self):
        q=fabricated_original()
        q["episodes"][0]["public_motion_observation_cost_samples"][ARMS[0]]=0
        with self.assertRaisesRegex(ValueError,"public cost"):validate_shard(q,"pull_cube",0,0)
        q=fabricated_original()
        q["episodes"][1]["shared_neutral_probe_step4"][ARMS[2]]["physically_dispatched"]=False
        with self.assertRaisesRegex(ValueError,"public cost"):validate_shard(q,"pull_cube",0,0)
    def test_posthoc_threshold_tuning_forbidden(self):
        q=fabricated_original()
        q["episodes"][0]["same_sensor_posterior_evidence"]["posterior_threshold_predeclared"]=.60
        with self.assertRaisesRegex(ValueError,"score tuned after protocol"):validate_shard(q,"pull_cube",0,0)
    def test_cluster_swap_never_treats_128_cells_as_independent(self):
        self.assertAlmostEqual(_swap_exact([1,1,0,0]),.5)
        self.assertEqual(_swap_exact([0]*32),1.)
        with self.assertRaises(ValueError):_swap_exact([5])
    def test_deterministic_bootstrap_for_whole_four_truth_cluster(self):
        self.assertEqual(bootstrap_cluster_risk([0]*32,draws=1000),[0.,0.])
        a=bootstrap_cluster_risk([4]*32,draws=1000)
        self.assertEqual(a,[1.,1.])

if __name__=="__main__":unittest.main()

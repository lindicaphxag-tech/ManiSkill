"""Scientific adversarial tests of early terminal censoring; no simulator needed.

The 64-trial denominator is never reduced to the 63 (or fewer) episodes that
survive t4.  Missing genuine public observations are not replaced with zeros
or guessed controller targets, and no confidence is awarded to censored rows.
"""
import copy
import unittest
from research.run_dual_evidence_ack_new64 import (
    A,B,C,accepted,independent_eight,MODELS,TASKS,PRE
)

def make_early_episode(task="pull_cube",chunk=0,samples_a=0,samples_b=2,
                       actual_fault_steps=(2,3)):
    seeds=accepted(task,chunk)
    names=("source_no_fault","fault_oracle_private_target",
           "fault_optimistic_unverified_ack","fault_strict_common_exact",
           "fault_robust_two_history_without_query","fault_robust_then_single_privileged_query",
           A,B,C,"fault_assume_held_without_query")
    episodes=[]
    for seed in seeds:
        truth=(seed-1)%4
        e={
            "seed":seed,
            "original_precommitted_physical_t2_execution_truth":
                ("applied" if truth in (1,3) else "held"),
            "original_precommitted_physical_t3_execution_truth":
                ("applied" if truth in (2,3) else "held"),
            "faults":{A:[{"step":j} for j in actual_fault_steps]},
            "pre_t3_reference_censored":{},
            "refusals":{},
            "failure_causes":{},
            "success_once":{n:False for n in names},
            "privileged_target_readback_decision_count":{A:0,B:0,C:0},
            "public_motion_observation_cost_samples":{A:samples_a,B:samples_b,C:0},
        }
        episodes.append(e)
    return {
        "schema":"frozen_ppo_dual_evidence_2x2_real_physx_v1",
        "original_seed_population":seeds,
        "task":TASKS[task],
        "original_external_frozen_checkpoint_sha256":MODELS[task],
        "all_nine_actual_control_arms":list(names),
        "frozen_protocol":PRE,
        "real_physx_simulator":True,
        "frozen_model_retrained":False,
        "matched_prefix_causal_information_ablation":True,
        "episodes":episodes,
    }

class TestCensorAndEvidence(unittest.TestCase):
    def test_second_fault_exists_but_one_arm_exits_before_probe(self):
        raw=make_early_episode()
        audited=independent_eight(raw,"pull_cube",0)
        self.assertEqual(audited["original_intent_to_treat_censored_states"],8)
        self.assertEqual(audited["true_double_ACK_full_exposure_matched_states"],0)
        self.assertEqual(audited["source_outcomes"][A]["public_xyz_events"],0)
        self.assertEqual(audited["source_outcomes"][B]["public_xyz_events"],16)
        self.assertEqual(len(audited["original_all_eight"]),8)
        for row in audited["original_all_eight"]:
            self.assertFalse(row["valid_original_two_faults_and_matched_prefix"])
            self.assertTrue(row["post_t3_public_probe_censored"])
            self.assertTrue(row["asymmetric_public_samples_detected"])
            self.assertEqual((row["actual_public_samples_A"],row["actual_public_samples_B"]),(0,2))
            self.assertFalse(row["posterior_score_confident"])
            self.assertFalse(row["empirical_public_confident"])

    def test_both_probe_missing_still_retained(self):
        raw=make_early_episode(samples_a=0,samples_b=0)
        audited=independent_eight(raw,"pull_cube",0)
        self.assertEqual(audited["original_intent_to_treat_censored_states"],8)
        self.assertEqual(audited["source_outcomes"][A]["official_success"],0)
        self.assertEqual(len(audited["original_all_eight"]),8)

    def test_partial_uncounted_sample_is_not_accepted(self):
        raw=make_early_episode(samples_a=1,samples_b=2)
        with self.assertRaisesRegex(ValueError,"Public samples unaccounted"):
            independent_eight(raw,"pull_cube",0)

    def test_complete_two_probe_samples_require_original_physical_se3_witness(self):
        raw=make_early_episode(samples_a=2,samples_b=2)
        with self.assertRaisesRegex(ValueError,"False physical/evidence matched-prefix declaration"):
            independent_eight(raw,"pull_cube",0)

    def test_early_source_successes_never_cherry_picked(self):
        raw=make_early_episode()
        for row in raw["episodes"][:3]:
            row["success_once"][A]=True
            row["success_once"][B]=True
            row["success_once"][C]=True
        result=independent_eight(raw,"pull_cube",0)
        self.assertEqual(result["source_outcomes"][A]["official_success"],3)
        self.assertEqual(result["source_outcomes"][B]["official_success"],3)
        self.assertEqual(result["source_outcomes"][C]["official_success"],3)
        self.assertEqual(len(result["original_all_eight"]),8)

if __name__=="__main__":
    unittest.main()

"""Independent deterministic falsifiers; no result fabrication or simulator required."""
import unittest
from research.audit_physical_response_32 import validate_data,ARMS
from research.physical_response_classifier import pure_classification

class TestPhysicalResponseContract(unittest.TestCase):
    def test_clear_applied_positional_response(self):
        x=pure_classification([0.030,0,0],[0,0,0],[0.035,0,0])
        self.assertEqual(x["label"],"applied")

    def test_clear_held_positional_response(self):
        x=pure_classification([0.001,0,0],[0,0,0],[0.035,0,0])
        self.assertEqual(x["label"],"held")

    def test_equivocal_ties_abstain(self):
        x=pure_classification([0.0175,0,0],[0,0,0],[0.035,0,0])
        self.assertIsNone(x["label"])

    def test_near_identical_hidden_targets_abstain(self):
        x=pure_classification([0,0,0],[0,0,0],[0.0006,0,0])
        self.assertIsNone(x["label"])

    def test_finite_input_and_preset_margin(self):
        with self.assertRaises(ValueError):
            pure_classification([float("nan"),0,0],[0,0,0],[1,0,0])
        with self.assertRaises(ValueError):
            pure_classification([0,0],[0,0,0],[1,0,0])
        with self.assertRaises(ValueError):
            pure_classification([0,0,0],[0,0,0],[1,0,0],margin=0)

    def sample(self,incorrect=False):
        truth="neutral_arm_delta_no_ack"
        flags={x:x not in ("source_pause_no_fault",) for x in ARMS}
        rows=[]
        for seed in range(140001,140005):
            cls=dict(label="held" if not incorrect else "applied",
                     hold_distance_m=0.0001,
                     applied_distance_m=0.021,
                     target_separation_m=0.0209,
                     decision_margin_m=0.0209,
                     evidence_type="achieved_EE_xyz_after_one_native_zero_arm_delta")
            rows.append(dict(
                seed=seed,task="PullCube-v1",unknown_ack_truth=truth,
                fault_step=2,probe_step=3,
                initial_obs_diff={x:0 for x in ARMS[1:]},
                fault_reached={x:(x!="source_pause_no_fault") for x in ARMS},
                probe_reached={x:True for x in ARMS},
                success_once=flags.copy(),steps={x:10 for x in ARMS},
                classifier=cls,wrong_authorization=incorrect,
                candidate_goal_positions={"held":[0,0,0],"applied":[0.02,0,0]},
                private_memory_reads_during_action_decision={
                    x:1 if x=="privileged_once_after_probe" else 0 for x in ARMS},
                probe_positions={x:{"achieved_post_probe_xyz":[0,0,0]}
                                 for x in ARMS},
                projections={}))
        return dict(schema="physical_response_ack_ambiguity_frozen_ppo_prospective_v1",
                    preoutcome_frozen_commit="f237fadb70895bc94889f3ff44cb6c41d296b323",
                    protocol="research/PHYSICAL_RESPONSE_ACK_PROSPECTIVE_V1.json",
                    task="PullCube-v1",truth=truth,seeds=list(range(140001,140005)),
                    third_party_checkpoint_sha256="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
                    published_revision="6bdeb28810330ab5425ccd629bb561c58a56ff85",
                    real_physx=True,training_performed=False,
                    rows=rows,success_count={x:4 if flags[x] else 0 for x in ARMS},
                    classification_covered=4,
                    false_history_authorizations=4 if incorrect else 0)

    def test_all_four_complete_original_rows(self):
        s=self.sample()
        self.assertEqual(validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)["classifier_covered"],4)

    def test_wrong_authorization_retained_as_negative(self):
        s=self.sample(incorrect=True)
        self.assertEqual(validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)["classifier_wrong_authorizations"],4)

    def test_wrong_truth_label_detected(self):
        s=self.sample()
        s["rows"][0]["classifier"]["label"]="applied"
        with self.assertRaises(ValueError):
            validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)

    def test_private_target_leak_rejected(self):
        s=self.sample()
        s["rows"][0]["private_memory_reads_during_action_decision"]["achieved_probe_classifier"]=1
        with self.assertRaises(ValueError):
            validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)

    def test_missing_source_seed_rejected(self):
        s=self.sample()
        s["rows"].pop()
        with self.assertRaises(ValueError):
            validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)

    def test_native_failure_not_deleted(self):
        s=self.sample()
        s["rows"][0]["success_once"]["achieved_probe_classifier"]=False
        s["success_count"]["achieved_probe_classifier"]=3
        self.assertEqual(validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)["success"]["achieved_probe_classifier"],3)

    def test_fake_exact_projected_action_rejected(self):
        s=self.sample()
        s["rows"][0]["projections"]={"achieved_probe_classifier":[{"exactness":"EXACT"}]}
        with self.assertRaises(ValueError):
            validate_data(s,"pull_cube","neutral_arm_delta_no_ack",0)

if __name__=="__main__":
    unittest.main()

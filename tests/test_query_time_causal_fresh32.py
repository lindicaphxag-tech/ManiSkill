"""Adversarial deterministic checks; synthetic controls are NOT measured PhysX."""
import unittest
from copy import deepcopy
from research.audit_query_time_causal_fresh32 import validate,ARMS,TIMES

class TestQueryTimeCausalOriginalAudit(unittest.TestCase):
    def setUp(self):
        flags={a:False for a in ARMS}
        flags["source_no_fault"]=True
        flags["fault_robust_then_single_privileged_query"]=True
        rows=[]
        for seed in range(280001,280005):
            reads={a:(-1 if a=="fault_oracle_private_target" else
                      1 if a=="fault_robust_then_single_privileged_query" else 0)
                   for a in ARMS}
            rows.append(dict(
                seed=seed,task="PullCube-v1",success_once=deepcopy(flags),
                privileged_target_readback_decision_count=reads,
                private_readback_steps={"fault_robust_then_single_privileged_query":[4]},
                steps={a:10 for a in ARMS},
                faults={a:dict(step=2,actual_native_arm_command="all_zero_hold") for a in ARMS[1:]},
                initial_obs_diff={a:0.0 for a in ARMS[1:]},
                refusals={"fault_fixed_query_t3":{"step":3},
                          "fault_fixed_query_t5":{"step":4},
                          "fault_fixed_query_t6":{"step":4}},
                native_projection_NOT_EXACT={}
            ))
        self.data=dict(
            schema="query_time_causal_intervention_new32_real_physx_v1",
            task="PullCube-v1",
            original_seed_population=list(range(280001,280005)),
            original_external_frozen_checkpoint_sha256="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
            frozen_protocol="research/QUERY_TIME_CAUSAL_FRESH32_PREOUTCOME_V1.json",
            original_source_method_git_blob="1dc653cdc44e422c8340475ad00f828b3a41eb4f",
            original_robust_certifier_git_blob="bb5fd155b7291fb127f94138fca321201c8271c3",
            all_eight_actual_control_arms=list(ARMS),
            frozen_model_retrained=False,real_physx_simulator=True,
            privileged_readback_counts_are_decision_only_not_audit_reads=True,
            precommitted_query_times=TIMES,
            episodes=rows,
            success_counts={a:sum(r["success_once"][a] for r in rows) for a in ARMS},
            selective_readback_counts=[1]*4,
            fixed_readback_counts={a:[0]*4 for a in TIMES}
        )
    def run_validator(self):
        return validate(self.data,"pull_cube",0)
    def test_synthetic_happy_path(self):
        z=self.run_validator()
        self.assertEqual(z["reads"]["fault_robust_then_single_privileged_query"],4)
    def test_missing_episode_fails(self):
        self.data["episodes"].pop()
        with self.assertRaises(ValueError):self.run_validator()
    def test_unauthorized_fixed_late_read_fails(self):
        r=self.data["episodes"][0]
        r["privileged_target_readback_decision_count"]["fault_fixed_query_t6"]=1
        r["private_readback_steps"]={"fault_fixed_query_t6":[3],
                                    "fault_robust_then_single_privileged_query":[4]}
        with self.assertRaises(ValueError):self.run_validator()
    def test_unbudgeted_extra_adaptive_read_fails(self):
        self.data["episodes"][0]["privileged_target_readback_decision_count"]["fault_robust_then_single_privileged_query"]=2
        with self.assertRaises(ValueError):self.run_validator()
    def test_relabelled_controller_success_fails(self):
        self.data["episodes"][0]["success_once"]["fault_fixed_query_t5"]=True
        with self.assertRaises(ValueError):self.run_validator()
    def test_undeclared_fault_drop_fails(self):
        del self.data["episodes"][0]["faults"]["fault_fixed_query_t6"]
        with self.assertRaises(ValueError):self.run_validator()
    def test_missing_truthful_oracle_budget_fails(self):
        self.data["episodes"][0]["privileged_target_readback_decision_count"]["fault_oracle_private_target"]=0
        with self.assertRaises(ValueError):self.run_validator()
    def test_zero_task_success_retained(self):
        z=self.run_validator()
        self.assertEqual(z["success"]["fault_fixed_query_t6"],0)
    def test_not_exact_projection_cannot_be_falsely_exact(self):
        self.data["episodes"][1]["native_projection_NOT_EXACT"]={"fault_fixed_query_t3":[{"exactness":"EXACT"}]}
        with self.assertRaises(ValueError):self.run_validator()
if __name__=="__main__":unittest.main()

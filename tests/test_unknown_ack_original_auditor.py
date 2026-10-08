"""Synthetic, destructive contract tests. These are NOT simulator outcomes."""
import json
import tempfile
import unittest
from pathlib import Path
from research.audit_unknown_ack_physx import audit, ARMS, TASKS, CONDITIONS, PROTOCOL, FROZEN_SHA, HF_REV

class TestNativeLostAckEvidenceAudit(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.folder=Path(self.t.name)
        for name,(env,sha,first) in TASKS.items():
            for fault in CONDITIONS:
                rows=[]
                for seed in range(first,first+8):
                    success={k:seed%2==0 for k in ARMS}
                    rows.append({
                        "seed":seed,"task":env,"fault":fault,"fault_step":2,
                        "fault_reached":{k:True for k in ARMS[1:]},
                        "success_once":success,
                        "steps":{k:3 for k in ARMS},
                        "initial_obs_diff":{k:0.0 for k in ARMS[1:]},
                        "refusals":{"fail_closed_stop":{"step":3}},
                        "approximations":{},
                        "readback_queries":{k:(-1 if k=="oracle_live_memory" else
                                              1 if k=="recovered_one_readback" else 0)
                                            for k in ARMS[1:]},
                        "resync_position_error_m":0.0,
                        "ambiguity_diameter_m":0.02,
                        "post_fault_optimistic_position_error_m":0.02,
                        "post_fault_pessimistic_position_error_m":0.0
                    })
                self.save(name,fault,{
                    "schema":"action_abi_unknown_arm_command_ack_prospective_physx_v1",
                    "preregistration":PROTOCOL,"frozen_prereg_commit":FROZEN_SHA,
                    "task":env,"fault":fault,"checkpoint_sha256":sha,
                    "checkpoint_revision":HF_REV,"backend":"physx_cpu",
                    "real_physx":True,"training_performed":False,
                    "seeds":list(range(first,first+8)),"rows":rows,
                    "success_count":{a:4 for a in ARMS}
                })

    def tearDown(self):
        self.t.cleanup()
    def filename(self,name,fault):
        return self.folder/f"ack_loss_{name}_{fault}_fresh8.json"
    def load(self,name,fault):
        return json.loads(self.filename(name,fault).read_text())
    def save(self,name,fault,data):
        self.filename(name,fault).write_text(json.dumps(data))

    def test_full_stratified_source_cohort(self):
        x=audit(self.folder)
        self.assertEqual(x["n_original_paired_state_conditions"],32)
        self.assertEqual(len(x["results"]),4)
        self.assertTrue(all(not v["source_competent_predeclared"]
                            for v in x["results"].values()))

    def test_negative_performance_is_retained_not_excluded(self):
        b=self.load("pull_cube","applied_no_ack")
        for r in b["rows"]:
            r["success_once"]["recovered_one_readback"]=False
        b["success_count"]["recovered_one_readback"]=0
        self.save("pull_cube","applied_no_ack",b)
        z=audit(self.folder)
        self.assertEqual(z["results"]["pull_cube:applied_no_ack"]
                         ["success"]["recovered_one_readback"],0)

    def test_fails_missing_original_state(self):
        b=self.load("stack_cube","neutral_arm_delta_no_ack")
        b["rows"].pop()
        self.save("stack_cube","neutral_arm_delta_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

    def test_fails_fabricated_privileged_budget(self):
        b=self.load("pull_cube","applied_no_ack")
        b["rows"][0]["readback_queries"]["oracle_live_memory"]=0
        self.save("pull_cube","applied_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

    def test_fails_missing_fault_exposure(self):
        b=self.load("stack_cube","applied_no_ack")
        b["rows"][2]["fault_reached"]["recovered_one_readback"]=False
        self.save("stack_cube","applied_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

    def test_fails_post_fault_stop_control_violation(self):
        b=self.load("pull_cube","neutral_arm_delta_no_ack")
        b["rows"][0]["steps"]["fail_closed_stop"]=4
        self.save("pull_cube","neutral_arm_delta_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

    def test_fails_missing_attested_resync(self):
        b=self.load("pull_cube","neutral_arm_delta_no_ack")
        b["rows"][3]["readback_queries"]["recovered_one_readback"]=0
        self.save("pull_cube","neutral_arm_delta_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

    def test_fails_checkpoint_swap(self):
        b=self.load("stack_cube","applied_no_ack")
        b["checkpoint_sha256"]="000"
        self.save("stack_cube","applied_no_ack",b)
        with self.assertRaises(ValueError):audit(self.folder)

if __name__=="__main__":
    unittest.main()

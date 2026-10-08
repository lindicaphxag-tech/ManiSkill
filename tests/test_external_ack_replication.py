"""Zero-dependency tests for an outsider's source-hash and audit contract."""
import unittest
from research.external_ack_replication import validate_inputs,validate_output

ARMS=("source","oracle_live_memory","recovered_one_readback",
      "optimistic_assume_applied","pessimistic_assume_neutral","fail_closed_stop")

def record(seed=120001):
    flags={k:k!="fail_closed_stop" for k in ARMS}
    row=dict(
        seed=seed,steps={k:3 for k in ARMS},
        fault_reached={k:True for k in ARMS[1:]},
        readback_queries={k:(-1 if k=="oracle_live_memory" else 1 if k=="recovered_one_readback" else 0) for k in ARMS[1:]},
        success_once=flags,refusals={"fail_closed_stop":{"step":3}},
        resync_position_error_m=0.0)
    return dict(schema="action_abi_unknown_arm_command_ack_prospective_physx_v1",
                task="PullCube-v1",fault="applied_no_ack",seeds=[seed],
                real_physx=True,training_performed=False,
                rows=[row],success_count={k:int(flags[k]) for k in ARMS})

class ExternalReplayGuardTest(unittest.TestCase):
    def test_valid_fresh_seed_and_counts(self):
        self.assertEqual(validate_inputs("pull_cube","applied_no_ack",120001,8),
                         list(range(120001,120009)))
        self.assertEqual(validate_output(record(),"pull_cube","applied_no_ack",[120001])
                         ["recovered_one_readback"],1)

    def test_no_original_preregistered_seed_reuse(self):
        with self.assertRaises(ValueError):
            validate_inputs("pull_cube","applied_no_ack",94001,8)

    def test_bad_fault_and_task(self):
        for task,fault in [("invalid","applied_no_ack"),("stack_cube","UNKNOWN")]:
            with self.assertRaises(ValueError):
                validate_inputs(task,fault,120001,8)

    def test_bool_seed_and_invalid_count_denied(self):
        for seed in [True,-1,2147483648]:
            with self.assertRaises(ValueError):
                validate_inputs("pull_cube","applied_no_ack",seed,8)
        with self.assertRaises(ValueError):
            validate_inputs("pull_cube","applied_no_ack",120001,7)

    def test_missing_original_seed_is_rejected(self):
        r=record()
        r["rows"]=[]
        with self.assertRaises(ValueError):
            validate_output(r,"pull_cube","applied_no_ack",[120001])

    def test_false_oracle_access_budget_rejected(self):
        r=record()
        r["rows"][0]["readback_queries"]["oracle_live_memory"]=0
        with self.assertRaises(ValueError):
            validate_output(r,"pull_cube","applied_no_ack",[120001])

    def test_no_fault_hidden_as_success_is_rejected(self):
        r=record()
        r["rows"][0]["fault_reached"]["recovered_one_readback"]=False
        with self.assertRaises(ValueError):
            validate_output(r,"pull_cube","applied_no_ack",[120001])

    def test_negative_outcome_retained(self):
        r=record()
        r["rows"][0]["success_once"]["recovered_one_readback"]=False
        r["success_count"]["recovered_one_readback"]=0
        self.assertEqual(validate_output(r,"pull_cube","applied_no_ack",[120001])
                         ["recovered_one_readback"],0)

    def test_rewritten_score_or_no_stop_refused(self):
        r=record()
        r["success_count"]["optimistic_assume_applied"]=0
        with self.assertRaises(ValueError):
            validate_output(r,"pull_cube","applied_no_ack",[120001])
        r=record()
        r["refusals"]={}
        with self.assertRaises(ValueError):
            validate_output(r,"pull_cube","applied_no_ack",[120001])

if __name__=="__main__":
    unittest.main()

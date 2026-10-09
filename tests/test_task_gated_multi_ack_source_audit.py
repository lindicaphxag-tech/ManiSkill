"""Adversarial independent original-PhysX task-gated source ledger tests.

Synthetic test data exercises the AUDITOR only. Actual result numbers and
research success claims MUST come from the SHA-pinned first full PhysX run.
"""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research.audit_task_gated_multi_ack_new64 import (
    ARMS, SELECTIVE, MANDATORY, TASKS, SOURCE_HASHES, audit,
    exact_two_sided_discordance
)


def create_fake_evidence(root:Path):
    for task,spec in TASKS.items():
        for chunk in range(4):
            dest=root/f"{task}_chunk{chunk}"
            dest.mkdir()
            rows=[]
            successes={a:0 for a in ARMS}
            reads={a:0 for a in ARMS if a!=ARMS[1]}
            fixed_route=spec["selected"]
            routes=[]
            seeds=list(range(spec["first"]+8*chunk,spec["first"]+8*chunk+8))
            for i,seed in enumerate(seeds):
                succ={a:(a != ARMS[3] and not (i==0 and a==MANDATORY)) for a in ARMS}
                n_reads={a:(-1 if a==ARMS[1] else int(a==MANDATORY or (a==SELECTIVE and i%2==0))) for a in ARMS}
                faults={a:[{"step":2},{"step":3}] for a in ARMS[1:]}
                faults[ARMS[3]]=[{"step":2}]
                row={"seed":seed,"success_once":succ,
                     "privileged_target_readback_decision_count":n_reads,
                     "faults":faults,
                     "max_belief_width":{a:4 for a in (ARMS[4],SELECTIVE,MANDATORY)}}
                rows.append(row)
                for a in ARMS:
                    successes[a]+=int(succ[a])
                    if a!=ARMS[1]:
                        reads[a]+=n_reads[a]
                routes.append({
                    "task":task,"seed":seed,"routed_actual_physx_arm":fixed_route,
                    "routed_success":int(succ[fixed_route]),"routed_privileged_reads":n_reads[fixed_route],
                    "fixed_actual_native_success":int(succ[MANDATORY]),
                    "fixed_actual_privileged_reads":n_reads[MANDATORY],
                    "selective_actual_native_success":int(succ[SELECTIVE]),
                    "selective_actual_privileged_reads":n_reads[SELECTIVE],
                    "zero_query_actual_native_success":int(succ[ARMS[4]]),
                })
            original={
                "schema":"compound_two_unknown_ack_multihistory_physx_v1",
                "task":spec["label"],
                "original_seed_population":seeds,
                "two_consecutive_unknown_ack_target_hold_steps":[2,3],
                "preoutcome_protocol":"research/TASK_GATED_MULTI_ACK_FRESH64_V1.json",
                "original_external_frozen_checkpoint_sha256":spec["checkpoint"],
                "frozen_model_retrained":False,
                "real_physx_simulator":True,
                "fault_is_native_target_hold_not_network_loss":True,
                "all_seven_actual_control_arms":list(ARMS),
                "episodes":rows,
                "success_counts":successes,
            }
            original_file=dest/f"task_gated_{task}_chunk{chunk}_original8.json"
            original_file.write_text(json.dumps(original,sort_keys=True))
            digest=hashlib.sha256(original_file.read_bytes()).hexdigest()
            report={
                "task":task,"chunk":chunk,"seed_register":seeds,
                "precommitted_task_route":fixed_route,
                "source_git_blobs":SOURCE_HASHES,
                "frozen_protocol":"research/TASK_GATED_MULTI_ACK_FRESH64_V1.json",
                "policy_decided_at_time":"before environment reset, task ID only",
                "not_independent_external_lab":True,
                "original_physx_raw_sha256":digest,
                "source_full_original_native_success_counts":successes,
                "source_full_original_true_decision_read_counts":reads,
                "all_original_eight_source_state_outcomes":routes,
                "routed_policy_complete_native_successes":sum(r["routed_success"] for r in routes),
                "routed_policy_true_privileged_reads":sum(r["routed_privileged_reads"] for r in routes),
            }
            (dest/"summary.json").write_text(json.dumps(report,sort_keys=True))


class ReviewableOriginalSourceAudit(unittest.TestCase):
    def test_exact_pair_pvalue(self):
        self.assertEqual(exact_two_sided_discordance(0,0),1.0)
        self.assertEqual(exact_two_sided_discordance(12,1),.00341796875)
        self.assertEqual(exact_two_sided_discordance(9,3),.14599609375)
        with self.assertRaises(ValueError):
            exact_two_sided_discordance(-1,3)

    def test_full_64_all_correlated_worlds(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            create_fake_evidence(root)
            r=audit(root)
            self.assertEqual(r["distinct_original_reset_states"],64)
            self.assertEqual(r["genuine_native_7_arm_stepped_worlds_if_source_trusted"],448)
            self.assertEqual(r["routed_true_private_reads_total"],16+32)
            self.assertEqual(r["routed_success_total"],64-4)
            self.assertEqual(r["mandatory_success_total"],64-8)
            self.assertTrue(r["four_target_memory_hypotheses_verified_in_all_relevant_trials"])

    def test_removed_episode_refused_not_hidden(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            create_fake_evidence(root)
            f=root/"stack_cube_chunk2"/"task_gated_stack_cube_chunk2_original8.json"
            obj=json.loads(f.read_text())
            obj["episodes"].pop()
            f.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"source JSON was changed"):
                audit(root)

    def test_task_outcome_selected_route_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            create_fake_evidence(root)
            f=root/"stack_cube_chunk2"/"summary.json"
            obj=json.loads(f.read_text())
            obj["precommitted_task_route"]=SELECTIVE
            f.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"Preregistered routing"):
                audit(root)

    def test_uninjected_second_native_fault_refused(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            create_fake_evidence(root)
            f=root/"pull_cube_chunk1"/"task_gated_pull_cube_chunk1_original8.json"
            obj=json.loads(f.read_text())
            obj["episodes"][0]["faults"][SELECTIVE]=[{"step":2}]
            f.write_text(json.dumps(obj))
            # Update only digest, simulating a tamperer who also repoints SHA.
            sf=root/"pull_cube_chunk1"/"summary.json"
            s=json.loads(sf.read_text())
            s["original_physx_raw_sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
            sf.write_text(json.dumps(s))
            with self.assertRaisesRegex(ValueError,"two physical holds"):
                audit(root)

    def test_fake_privileged_query_not_counted_as_free(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            create_fake_evidence(root)
            f=root/"pull_cube_chunk3"/"task_gated_pull_cube_chunk3_original8.json"
            obj=json.loads(f.read_text())
            obj["episodes"][2]["privileged_target_readback_decision_count"][ARMS[1]]=0
            f.write_text(json.dumps(obj))
            sf=root/"pull_cube_chunk3"/"summary.json"
            s=json.loads(sf.read_text())
            s["original_physx_raw_sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
            sf.write_text(json.dumps(s))
            with self.assertRaisesRegex(ValueError,"read ledger corrupted"):
                audit(root)


if __name__=="__main__":
    unittest.main()

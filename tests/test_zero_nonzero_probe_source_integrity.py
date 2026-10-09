"""Adversarial SOURCE-only tests: these are synthetic fixtures, NOT PhysX."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research.audit_zero_nonzero_probe_two_robots import (
    ROBOTS, PROBES, PROTO_BLOB, SRC_BLOBS, audit
)
from research.cross_robot_online_proprio_classifier import LABELS, train, decide


def make_fake_source(root):
    for robot,(old,new) in ROBOTS.items():
        calibration=[]
        probe_models={}
        for seed in range(old,old+8):
            for truth in LABELS:
                for probe in PROBES:
                    # Ordinary artificial test data, no physics claim.
                    position=0.04 if truth=="applied" else 0.0
                    perturb=0.008 if probe=="nonzero_x" else 0.0
                    physical_delta=[position+perturb,0.,0.]
                    calibration.append({
                        "robot":robot,"seed":seed,
                        "hidden_physical_truth_posthoc_only":truth,
                        "known_delivered_native_probe_id":probe,
                        "actual_native_t3_probe_six":PROBES[probe],
                        "private_target_reads_before_classification":0,
                        "real_physx_cpu":True,
                        "delta_public_xyz":physical_delta,
                    })
        for probe in PROBES:
            data=[dict(robot=r["robot"],seed=r["seed"],
                       truth=r["hidden_physical_truth_posthoc_only"],
                       delta_public_xyz=r["delta_public_xyz"])
                  for r in calibration if r["known_delivered_native_probe_id"]==probe]
            probe_models[probe]=train(data,robot)
        cal={"schema":"original_dual_robot_two_probe_physical_calibration_v1",
             "robot":robot,"prior_source_seeds":list(range(old,old+8)),
             "both_truths":list(LABELS),"both_physical_probes":list(PROBES),
             "preoutcome_proto_blob":PROTO_BLOB,
             "physical_calibration_source_rows":calibration,
             "empirical_envelopes_by_probe":probe_models}
        (root/f"two_probe_prior_calibration_{robot}.json").write_text(json.dumps(cal))
        c_sha=hashlib.sha256(json.dumps(cal,sort_keys=True).encode()).hexdigest()
        for chunk in (0,1):
            seeds=list(range(new+4*chunk,new+4*chunk+4))
            rows=[];totals={}
            for seed in seeds:
                for truth in LABELS:
                    controls=[]
                    for probe in PROBES:
                        position=0.04 if truth=="applied" else 0
                        perturb=.008 if probe=="nonzero_x" else 0
                        delta=[position+perturb,0.,0.]
                        decision=decide(delta,probe_models[probe])
                        guess=decision["label"]
                        controls.append({
                            "robot":robot,"seed":seed,
                            "hidden_physical_truth_posthoc_only":truth,
                            "known_delivered_native_probe_id":probe,
                            "actual_native_t3_probe_six":PROBES[probe],
                            "real_physx_cpu":True,
                            "private_target_reads_before_classification":0,
                            "private_target_reads_before_correction":0,
                            "command_execution_ack_hidden_from_classifier":True,
                            "delta_public_xyz":delta,"decision":decision,
                            "wrong_confident_history":None if guess is None else guess!=truth,
                            "refusal":guess is None,
                            "target_correction_reached":guess is not None,
                            "commanded_target_post_correction_error_inf_m":1e-8 if guess else None,
                            "target_restored_below_1e4_m":guess is not None,
                            "private_target_reads_post_dispatch_audit_only":int(guess is not None),
                        })
                    rows.append({"robot":robot,"seed":seed,
                                 "actual_execution_truth_score_only":truth,
                                 "original_two_physically_stepped_probe_worlds":controls})
            for probe in PROBES:
                xs=[next(c for c in row["original_two_physically_stepped_probe_worlds"]
                         if c["known_delivered_native_probe_id"]==probe) for row in rows]
                totals[probe]={
                    "confidence_coverage":sum(not x["refusal"] for x in xs),
                    "wrong_confident_label_count":sum(x["wrong_confident_history"] is True for x in xs),
                    "abstentions":sum(x["refusal"] for x in xs),
                    "actual_held_commanded_XYZ_corrected":sum(x["target_restored_below_1e4_m"] for x in xs),
                    "private_decision_target_reads":sum(x["private_target_reads_before_classification"] for x in xs),
                }
            original={
                "schema":"zero_nonzero_common_probe_cross_robot_fresh16_truth_probes_v1",
                "robot":robot,"chunk":chunk,"original_seed_register":seeds,
                "preoutcome_proto_blob":PROTO_BLOB,"calibration_sha256":c_sha,
                "source_chart_git_blobs":SRC_BLOBS,
                "test_worlds_actual_native_PhysX":16,
                "both_actuation_truths_and_actual_probes":True,
                "private_target_getter_never_used_in_decision":True,
                "full_task_success_not_tested":True,
                "rows":rows,"statistics":totals,
            }
            (root/f"native_two_probes_{robot}_chunk{chunk}_original16.json").write_text(json.dumps(original))


class SourceVerifierRegression(unittest.TestCase):
    def test_full_64_original_denominator_and_no_query(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);make_fake_source(root)
            observed=audit(root)
            self.assertEqual(observed["unseen_true_delivery_probe_real_physx_worlds"],64)
            self.assertEqual(observed["unseen_distinct_physical_seed_states"],16)
            self.assertEqual(observed["original_calibration_physx_worlds"],64)
            self.assertEqual(observed["per_probe"]["zero"]["confident_public_labels"],32)
            self.assertEqual(observed["per_probe"]["nonzero_x"]["private_predecision_readbacks"],0)

    def test_missing_original_physx_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);make_fake_source(root)
            (root/"native_two_probes_panda_chunk1_original16.json").unlink()
            with self.assertRaisesRegex(ValueError,"missing or additional"):
                audit(root)

    def test_wrong_physical_probe_amplitude_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);make_fake_source(root)
            p=root/"native_two_probes_xarm6_robotiq_chunk0_original16.json"
            x=json.loads(p.read_text())
            x["rows"][0]["original_two_physically_stepped_probe_worlds"][1]["actual_native_t3_probe_six"][0]=0.5
            p.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,"probe changed"):
                audit(root)

    def test_posthoc_faked_correct_label_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);make_fake_source(root)
            p=root/"native_two_probes_panda_chunk1_original16.json"
            x=json.loads(p.read_text())
            x["rows"][0]["original_two_physically_stepped_probe_worlds"][0]["decision"]["label"]="held"
            p.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,"classifier was altered"):
                audit(root)

    def test_truth_was_not_used_as_private_decision_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);make_fake_source(root)
            p=root/"native_two_probes_xarm6_robotiq_chunk1_original16.json"
            x=json.loads(p.read_text())
            x["rows"][0]["original_two_physically_stepped_probe_worlds"][0]["private_target_reads_before_classification"]=1
            p.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,"truth leakage"):
                audit(root)


if __name__=="__main__":
    unittest.main()

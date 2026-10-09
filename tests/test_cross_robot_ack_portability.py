"""Negative and positive controls for archival cross-robot ACK calibration pilot.

These are source-only analyses, NOT new PhysX executions.
"""
from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from research.cross_robot_ack_calibration_portability import (
    DATA, ROBOTS, K, evaluate, immutable_source,
    one_calibrated_model, study,
)


class SourcePortabilityTests(unittest.TestCase):
    def test_exact_source_denominator_and_negative_result(self):
        d=study()
        self.assertEqual(d["schema"],
            "retrospective_original_cross_robot_ack_response_calibration_portability_v1")
        self.assertEqual(set(d["per_target_robot"]),set(ROBOTS))
        self.assertEqual(set(d["pooled"]),set(map(str,K)))
        self.assertEqual(d["pooled"]["0"]["correct_confident"],0)
        self.assertEqual(d["pooled"]["0"]["wrong_confident"],0)
        self.assertEqual(d["pooled"]["0"]["abstain"],32)
        self.assertEqual(d["pooled"]["1"]["correct_confident"],32)
        self.assertEqual(d["pooled"]["1"]["wrong_confident"],0)
        self.assertEqual(d["pooled"]["1"]["abstain"],0)
        self.assertFalse(d["new_physics_run_performed"])
        self.assertFalse(d["third_party_independent_replication"])
        self.assertFalse(d["real_robot_or_frozen_ppo_task_transfer"])

    def test_held_and_applied_are_paired_per_seed_no_test_label_leak(self):
        d=study()
        for robot,v in d["per_target_robot"].items():
            self.assertEqual(len(v["new_seed_population"]),8)
            self.assertEqual(v["new_truth_conditions"],16)
            self.assertEqual(v["zero_to_eight_TARGET_labeled_reset_seed_PAIRS"]["0"]["n"],16)
            self.assertEqual(v["zero_to_eight_TARGET_labeled_reset_seed_PAIRS"]["1"]["n"],16)
            self.assertEqual(v["zero_to_eight_TARGET_labeled_reset_seed_PAIRS"]["0"]["by_truth"]["applied"]["abstain"],8)
            self.assertEqual(v["zero_to_eight_TARGET_labeled_reset_seed_PAIRS"]["0"]["by_truth"]["held"]["abstain"],8)

    def test_source_sha_mutation_fails(self):
        with tempfile.TemporaryDirectory() as td:
            fake=Path(td)/"source"
            shutil.copytree(DATA,fake)
            mutated=fake/"cross_robot_proprio_xarm6_robotiq_chunk0_original8.json"
            mutated.write_bytes(mutated.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                immutable_source(fake)

    def test_unregistered_source_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            fake=Path(td)/"source"
            shutil.copytree(DATA,fake)
            (fake/"extra.json").write_text("{}",encoding="utf-8")
            with self.assertRaises(ValueError):
                immutable_source(fake)

    def test_removed_source_fails(self):
        with tempfile.TemporaryDirectory() as td:
            fake=Path(td)/"source"
            shutil.copytree(DATA,fake)
            (fake/"cross_robot_proprio_calibration_panda.json").unlink()
            with self.assertRaises(ValueError):
                immutable_source(fake)

    def test_calibration_requires_truth_paired_samples(self):
        import json
        model=json.loads((DATA/"cross_robot_proprio_calibration_panda.json").read_text())
        target=json.loads((DATA/"cross_robot_proprio_calibration_xarm6_robotiq.json").read_text())
        x=one_calibrated_model(model["model"],target,"xarm6_robotiq",1)
        self.assertEqual(x["class_models"]["applied"]["mean_public_motion_m"],
            [float(v) for v in target["calibration_source_rows"][0]["delta_public_xyz"]])
        wrong=copy.deepcopy(target)
        wrong["calibration_source_rows"]=[
            a for a in wrong["calibration_source_rows"]
            if not (a["seed"]==430001 and a["hidden_truth"]=="held")]
        with self.assertRaises(ValueError):
            one_calibrated_model(model["model"],wrong,"xarm6_robotiq",1)

    def test_calibration_rejects_cross_robot_identity(self):
        import json
        panda=json.loads((DATA/"cross_robot_proprio_calibration_panda.json").read_text())
        xarm=json.loads((DATA/"cross_robot_proprio_calibration_xarm6_robotiq.json").read_text())
        with self.assertRaises(ValueError):
            one_calibrated_model(panda["model"],xarm,"panda",1)


if __name__=="__main__":
    unittest.main()

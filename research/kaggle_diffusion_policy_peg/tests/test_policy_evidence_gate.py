"""Synthetic fixtures only: no Kaggle training metrics are claimed here."""
import ast
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.kaggle_diffusion_policy_peg.assay_design import (
    FACTORIAL, assay_arms, four_cell_differences, verify_factorial_design,
)
from research.kaggle_diffusion_policy_peg.policy_evidence_gate import (
    ARMS, BASE, CONTROLLER, CONVERSION,
    UnverifiablePolicyEvidence, _source_seed_digest, gate,
)


def make_test_fixture(root: Path, *, factorial: bool = False) -> None:
    specs = assay_arms("factorial" if factorial else "paired")
    arms = tuple(spec.name for spec in specs)
    seeds = [11, 22, 33, 44]
    h = _source_seed_digest(seeds)
    run = {
        "status": "passed", "base_commit": BASE,
        "conversion_pr": {"head": CONVERSION},
        "controller_pr": {"head": CONTROLLER},
        "arms": list(arms),
        "config": {
            **({"experimental_design": "converter_x_controller_2x2_factorial"} if factorial else {}),
            "total_iters": 4, "eval_freq": 2, "num_eval_episodes": 20,
            "seed": 1, "minimum_paired_demos": 2,
            "effective_paired_num_demos": 4, "paired_source_seed_sha256": h,
        },
        "pairing": {
            "requested_episode_seeds_sha256": h,
            "paired_source_seed_sha256": h,
        },
    }
    manifest = {"status": "passed", "pairing_evidence": "pairing_evidence.json"}
    pairing = {
        "requested_episode_seeds": seeds,
        "requested_episode_seeds_sha256": h,
        "paired_episode_seeds": seeds, "paired_episode_seeds_sha256": h,
        "paired_count": 4,
        "arms": {
            arm: {
                "successful_episode_seeds": seeds,
                "successful_episode_seeds_sha256": h, "successful_count": 4,
            }
            for arm in arms
        },
    }
    summaries = [
        {
            "arm": arm, "source_commit": commit,
            "controller_overlay_commit": overlay,
            "source_tree": "a" * 40, "runtime_compatibility_sha256": "b" * 64,
            "demo_sha256": "c" * 64,
            "paired_source_seed_sha256": h, "paired_num_demos": 4,
        }
        for arm, commit, overlay in (spec.source_tuple for spec in specs)
    ]
    for name, data in (
        ("artifacts_manifest.json", manifest),
        ("experiment_log.json", run),
        ("pairing_evidence.json", pairing),
        ("run_summaries.json", summaries),
    ):
        (root / name).write_text(json.dumps(data), encoding="utf-8")
    rows = []
    for index, arm in enumerate(arms):
        rows.append({"arm": arm, "tag": "losses/total_loss", "step": 4, "value": 0.5})
        for step, success in ((0, index), (2, index + 1), (4, index + 2)):
            for tag in ("eval/success_once", "eval/success_at_end"):
                rows.append({
                    "arm": arm, "tag": tag, "step": step,
                    "value": success / 20,
                })
    (root / "metrics.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )


class PolicyEvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_test_fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def mutate_json(self, name, change):
        path = self.root / name
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def mutate_rows(self, change):
        path = self.root / "metrics.jsonl"
        rows = [json.loads(s) for s in path.read_text().splitlines()]
        change(rows)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    def reject(self, expected):
        with self.assertRaisesRegex(UnverifiablePolicyEvidence, expected):
            gate(self.root)

    def test_accepted_result_is_only_descriptive_not_significance(self):
        record = gate(self.root)
        self.assertEqual(record["status"], "descriptive_single_seed_paired_training_only")
        self.assertEqual(record["paired_source_demonstrations"], 4)
        self.assertEqual(record["evaluation_steps"], [0, 2, 4])
        self.assertEqual(record["curves"][-1][ARMS[0]]["eval/success_once"]["successful_episodes"], 2)
        self.assertTrue(any("combined" in s for s in record["limitations"]))

    def test_training_failed_before_first_optimizer_update_rejected(self):
        self.mutate_json("experiment_log.json", lambda x: x.update(status="failed"))
        self.reject("did not complete")

    def test_wrong_source_or_overlay_rejected(self):
        self.mutate_json(
            "run_summaries.json",
            lambda x: x[1].update(controller_overlay_commit="wrong-commit"),
        )
        self.reject("source intervention identity")

    def test_silently_swapped_paired_trajectories_rejected(self):
        self.mutate_json(
            "pairing_evidence.json",
            lambda x: x["arms"][ARMS[1]].update(
                successful_episode_seeds=[11, 22, 33]
            ),
        )
        self.reject("successful episode-seed digest mismatch")

    def test_stale_paired_dataset_identity_rejected(self):
        self.mutate_json(
            "run_summaries.json",
            lambda x: x[1].update(paired_source_seed_sha256="0" * 64),
        )
        self.reject("trained arm differs")

    def test_curve_missing_last_eval_refuses_complete_claim(self):
        self.mutate_rows(lambda rows: rows.__setitem__(
            slice(None), [x for x in rows
             if not (x["arm"] == ARMS[1] and x["tag"] == "eval/success_once" and x["step"] == 4)]
        ))
        self.reject("incomplete or unmatched evaluation")

    def test_impossible_fractional_success_count_rejected(self):
        self.mutate_rows(lambda rows: next(x for x in rows if x["tag"] == "eval/success_once").update(value=0.037))
        self.reject("not representable by 20 episodes")

    def test_duplicate_metric_rejected(self):
        self.mutate_rows(lambda rows: rows.append(copy.deepcopy(rows[0])))
        self.reject("duplicate scalar")

    def test_missing_training_loss_at_final_step_rejected(self):
        self.mutate_rows(lambda rows: [
            x.update(step=3)
            for x in rows if x["tag"] == "losses/total_loss"
        ])
        self.reject("missing complete optimizer loss")

    def test_sensor_origin_is_not_inferred_from_digest(self):
        record = gate(self.root)
        self.assertTrue(any("authenticity" in x for x in record["limitations"]))
        self.assertFalse(any("statistical superiority confirmed" in x for x in record["limitations"]))

    def _factorial(self):
        make_test_fixture(self.root, factorial=True)

    def test_factorial_gpu_runner_contains_exact_preassigned_source_matrix(self):
        # Parse source without executing the GPU experiment. This catches
        # drift between the frozen design specification and its runner.
        script = Path(__file__).resolve().parents[1] / "run_assay_factorial.py"
        tree = ast.parse(script.read_text(encoding="utf-8"))
        arm_assignments = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "arms"
                for target in node.targets
            )
        ]
        self.assertEqual(len(arm_assignments), 1)
        assignments = []
        symbols = {"BASE": BASE, "CONVERSION": CONVERSION, "CONTROLLER": CONTROLLER}
        for item in arm_assignments[0].value.elts:
            values = []
            for value in item.elts:
                if isinstance(value, ast.Constant):
                    values.append(value.value)
                else:
                    self.assertIsInstance(value, ast.Name)
                    values.append(symbols[value.id])
            assignments.append(tuple(values))
        self.assertEqual(
            tuple(assignments), tuple(spec.source_tuple for spec in FACTORIAL)
        )
        self.assertIn(
            'OUTPUT = WORK / "assay_output_factorial"',
            script.read_text(encoding="utf-8"),
        )

    def test_factorial_four_cell_curve_and_all_contrasts(self):
        self._factorial()
        verify_factorial_design(FACTORIAL)
        result = gate(self.root)
        self.assertEqual(result["status"], "descriptive_single_seed_factorial_training_only")
        self.assertEqual(len(result["factorial_contrasts"]), 6)
        self.assertEqual(len(result["curves"]), 3)
        self.assertEqual(len(result["curves"][-1]), 5)  # 4 arms + step
        values = {
            name: result["curves"][-1][name]["eval/success_at_end"]["rate"]
            for name in (spec.name for spec in FACTORIAL)
        }
        self.assertAlmostEqual(
            result["factorial_contrasts"][-1]["descriptive_contrasts"]["difference_in_differences"],
            four_cell_differences(values)["difference_in_differences"],
        )
        self.assertTrue(any("one training seed" in x for x in result["limitations"]))

    def test_factorial_requires_all_four_source_treatments(self):
        self._factorial()
        self.mutate_json(
            "run_summaries.json", lambda x: x.pop(2)
        )
        self.reject("incomplete frozen intervention cell set")

    def test_factorial_rejects_reused_conversion_dataset_identity(self):
        self._factorial()
        self.mutate_json(
            "run_summaries.json",
            lambda x: x[2].update(paired_source_seed_sha256="f" * 64),
        )
        self.reject("trained arm differs from pinned paired seeds")

    def test_factorial_refuses_wrong_controller_only_source(self):
        self._factorial()
        self.mutate_json(
            "run_summaries.json", lambda x: x[2].update(source_commit=CONVERSION)
        )
        self.reject("source intervention identity wrong")

    def test_factorial_rejects_missing_one_arm_metric_step(self):
        self._factorial()
        self.mutate_rows(
            lambda rows: rows.__setitem__(
                slice(None),
                [
                    x for x in rows
                    if not (
                        x["arm"] == FACTORIAL[2].name
                        and x["tag"] == "eval/success_at_end"
                        and x["step"] == 2
                    )
                ],
            )
        )
        self.reject("incomplete or unmatched evaluation schedule")


if __name__ == "__main__":
    unittest.main()

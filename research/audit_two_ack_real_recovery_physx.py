"""Independent artifact-only audit of 160 native PhysX recovery worlds.

Does NOT import simulator code or trust the results script's published mean
matrix. Cross-check exact frozen denominator, candidate/action blindness and
source-based loss comparisons from the raw run artifacts. Integrity checks on
a GitHub-hosted artifact do not independently authenticate the physical robot.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from math import isfinite
from pathlib import Path
import subprocess


PLAN = Path("research/TWO_ACK_REAL_RECOVERY_MATRIX_PREREG_20261013.json")
PLAN_SHA = "6789866ddfdc48350a56be6b50da66fd07014457"
ROBOT_LIST = ("panda", "xarm6_robotiq")


def audit_artifacts(input_dir: Path) -> dict:
    digest = subprocess.check_output(
        ["git", "hash-object", str(PLAN)], text=True
    ).strip()
    if digest != PLAN_SHA:
        raise RuntimeError("Frozen pre-outcome plan content changed")
    spec = json.loads(PLAN.read_text(encoding="utf-8"))
    histories = tuple(spec["histories"])
    decisions = tuple(spec["candidate_decisions"])
    assert histories == ("00", "01", "10", "11")
    assert decisions == (*histories, "NO_ACTION")
    audit = {}
    for robot in ROBOT_LIST:
        path = input_dir / f"two_ack_recovery_matrix_{robot}.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        if (original.get("robot") != robot
                or original.get("preoutcome_protocol_git_blob") != PLAN_SHA
                or original.get("native_mapping_source_git_blob")
                    != "3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7"
                or original.get("unique_reset_clusters") != 4
                or original.get("actual_physical_worlds") != 80
                or original.get("no_probe_classifier_or_adaptive_policy") is not True
                or len(original.get("rows", [])) != 80):
            raise ValueError("Missing/altered native robot / original denominator")
        rows = original["rows"]
        expected = {
            (seed, h, d) for seed in spec["reset_seeds"][robot]
            for h in histories for d in decisions
        }
        actual = [
            (x["reset_seed"], x["true_history_audit_only"],
             x["fixed_recovery_decision"]) for x in rows
        ]
        if len(set(actual)) != 80 or set(actual) != expected:
            raise ValueError("Duplicated/missing/foreign true-history recovery cell")
        for x in rows:
            if (x["robot"] != robot
                    or x.get("real_physx_cpu") is not True
                    or x.get("physical_safety_certificate") is not False
                    or x["decision_time_hidden_ack_reads"] != 0
                    or x["decision_time_private_controller_target_reads"] != 0
                    or x["post_action_target_audit_reads"] != 1):
                raise ValueError("Candidate used privileged state or substituted world")
            nums = [
                x["achieved_xyz_error_m"], x["private_target_audit_residual_m"],
                *x["native_correction"], *x["canonical_goal_source_xyz"],
                *x["pre_recovery_public_ee_xyz"],
                *x["post_recovery_public_ee_xyz"],
            ]
            if (len(x["native_correction"]) != 6
                    or any(not isinstance(v, (float, int)) or not isfinite(v)
                           for v in nums)
                    or x["achieved_xyz_error_m"] < 0
                    or x["private_target_audit_residual_m"] < 0):
                raise ValueError("Invalid/nonfinite robot recovery evidence")
        # The exact same candidate is required across all hidden truths of
        # the same reset: a truth-dependent "oracle action" in the chooser
        # would invalidate any claimed blind recovery capacity experiment.
        for seed in spec["reset_seeds"][robot]:
            seed_rows = [x for x in rows if x["reset_seed"] == seed]
            if len({
                tuple(x["canonical_goal_source_xyz"]) for x in seed_rows
            }) != 1:
                raise ValueError("Truth-dependent recovery target (answer leak)")
            for d in decisions:
                candidates = [x for x in seed_rows
                              if x["fixed_recovery_decision"] == d]
                if len({tuple(x["native_correction"]) for x in candidates}) != 1:
                    raise ValueError("Recovery action covertly depends on ACK truth")
                if d == "NO_ACTION" and any(candidates[0]["native_correction"]):
                    raise ValueError("No-action baseline is not zero native command")
        mean_matrix = {}
        for h in histories:
            mean_matrix[h] = {}
            for d in decisions:
                samples = [
                    x["achieved_xyz_error_m"] for x in rows
                    if x["true_history_audit_only"] == h
                    and x["fixed_recovery_decision"] == d
                ]
                assert len(samples) == 4
                mean_matrix[h][d] = sum(samples) / len(samples)
                # Independently recompute -- don't simply trust the producer
                # summary, which could be mislabelled or cherry-picked.
                if abs(mean_matrix[h][d] -
                       original["source_truth_decision_mean_loss_matrix_m"][h][d]) > 1e-10:
                    raise ValueError("Reported cell average disagrees with raw worlds")
        capacity = {}
        for alphabet in (1, 2, 3, 4):
            choices = combinations(histories, alphabet)
            best = min(
                (sum(min(mean_matrix[h][d] for d in subset)
                     for h in histories) / len(histories), subset)
                for subset in choices
            )
            capacity[str(alphabet)] = {
                "optimistic_uniform_truth_loss_floor_m": best[0],
                "recovery_choices": list(best[1]),
                "best_case_only_not_observed_policy": True,
            }
        diag = sum(mean_matrix[h][h] for h in histories) / len(histories)
        no_action = sum(mean_matrix[h]["NO_ACTION"]
                        for h in histories) / len(histories)
        audit[robot] = {
            "complete_original_physical_worlds": len(rows),
            "unique_reset_clusters": len(spec["reset_seeds"][robot]),
            "blind_candidate_action_checks_passed": True,
            "matrix_m": mean_matrix,
            "truth_aware_oracle_mean_error_m": diag,
            "no_action_mean_error_m": no_action,
            "ideal_sensor_information_floor_by_distinct_outcomes": capacity,
            "task_success_or_new_adaptive_policy_improvement_not_claimed": True,
        }
    return {
        "audit_schema": "two_ack_real_physx_full_original_denominator_audit_v1",
        "original_run_id": 38331837905,
        "num_independent_reset_clusters": 8,
        "num_original_physx_conditions": 160,
        "source_model": "Two-ACK target-relative root-translation controllers",
        "source_authentication_limit": (
            "Artifact source consistency only, no external physical attestation"
        ),
        "robots": audit,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_artifacts(args.input_dir)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("INDEPENDENT_FULL_NATIVE_RECOVERY_AUDIT", json.dumps({
        robot: {
            "worlds": obj["complete_original_physical_worlds"],
            "blind_actions": obj["blind_candidate_action_checks_passed"],
            "oracle_mean_error_mm": round(
                1000 * obj["truth_aware_oracle_mean_error_m"], 4
            ),
            "binary_ideal_error_floor_mm": round(
                1000 * obj["ideal_sensor_information_floor_by_distinct_outcomes"]
                ["2"]["optimistic_uniform_truth_loss_floor_m"], 4
            ),
            "no_action_mean_error_mm": round(
                1000 * obj["no_action_mean_error_m"], 4
            ),
        } for robot, obj in result["robots"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()

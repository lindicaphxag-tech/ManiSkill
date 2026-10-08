#!/usr/bin/env python3
"""Independent standard-library audit of the frozen PPO controller swap evidence.

Reads the immutable archive from GitHub Actions run 37808182157.
Never imports the policy actor, simulator, experiment runner, or train code.
This is an AUTHOR-operated second implementation, not independent adoption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SOURCE_RUN = 37808182157
SOURCE_HEAD = "2f09c737acee78ad40e913ce3593486fa678edf6"
SOURCE_ARTIFACT_ID = 11564305838
SOURCE_ARTIFACT_ZIP_SHA256 = "8c63d67d95d60e0040b9028ed92f1530260eb2a5b4fa6690dd712d98e4ee68f5"
CHECKPOINT_SHA256 = "3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8"
EXPECTED_SEED_ORDER = [10014, *range(10001, 10014), 10014]
ARMS = ("source", "compiled", "naive")
OBS_MAX_TOL = 5e-4


def audit(report: dict, order: dict) -> dict:
    if report.get("checkpoint_sha256") != CHECKPOINT_SHA256:
        raise ValueError("checkpoint hash differs from original frozen actor")
    if report.get("checkpoint_repo") != "kattri15/actionshift-baselines":
        raise ValueError("checkpoint origin changed")
    if report.get("checkpoint") != "ppo/pick_cube_final_ckpt.pt":
        raise ValueError("checkpoint artifact path changed")
    if report.get("policy_frozen") is not True:
        raise ValueError("frozen policy invariant not asserted")
    if report.get("backend") != "physx_cpu":
        raise ValueError("simulator backend changed")
    if report.get("controller_modes") != {
        "source": "pd_ee_delta_pose",
        "compiled": "pd_ee_pose",
        "naive": "pd_ee_pose",
    }:
        raise ValueError("not the designated physical controller ABI comparison")
    episodes = report.get("episodes")
    if not isinstance(episodes, list) or len(episodes) != len(EXPECTED_SEED_ORDER):
        raise ValueError("missing or extra physical episodes")
    seeds = [e.get("seed") for e in episodes]
    if seeds != EXPECTED_SEED_ORDER:
        raise ValueError("episode seed order changed or duplicate quietly removed")
    if len(set(seeds)) != 14 or seeds.count(10014) != 2:
        raise ValueError("14 unique seeds and repeated 10014 are required")

    per_episode_counts = dict.fromkeys(ARMS, 0)
    by_seed: dict[int, dict[str, bool]] = {}
    for e in episodes:
        outcomes = e.get("success_once")
        steps = e.get("episode_steps")
        diffs = e.get("initial_obs_maxdiff")
        traces = e.get("detailed_trace")
        if not isinstance(outcomes, dict) or not isinstance(steps, dict):
            raise ValueError("missing physical episode outcomes")
        if not isinstance(traces, list) or len(traces) < 1:
            raise ValueError("missing step-by-step physical trace")
        if not isinstance(diffs, dict):
            raise ValueError("missing initial-state identity check")
        for arm in ("compiled", "naive"):
            if not isinstance(diffs.get(arm), (float, int)) or not 0 <= diffs[arm] <= OBS_MAX_TOL:
                raise ValueError(f"initial world mismatch in arm {arm}")
        for arm in ARMS:
            value = outcomes.get(arm)
            n = steps.get(arm)
            if not isinstance(value, bool):
                raise ValueError(f"missing/invalid boolean task outcome in {arm}")
            if not isinstance(n, int) or not 1 <= n <= 50:
                raise ValueError(f"nonphysical episode length in {arm}")
            per_episode_counts[arm] += int(value)
        if e["seed"] in by_seed and by_seed[e["seed"]] != outcomes:
            raise ValueError("duplicated source seed has conflicting observed outcomes")
        by_seed[e["seed"]] = {arm: outcomes[arm] for arm in ARMS}

    reported = report.get("success_count")
    if reported != per_episode_counts:
        raise ValueError(f"reported outcome counts differ from raw records: {reported}")
    if report.get("denominator") != len(episodes):
        raise ValueError("reported denominator inconsistent with trial count")
    if order.get("claim") != "exploratory order-sensitivity diagnostic; no holdout redefinition":
        raise ValueError("order-control claim boundary removed")
    if order.get("warmups") != 13:
        # The diagnostic script records 13 *intermediate* seeds.
        raise ValueError("incorrect warmup identity")
    if order.get("first") != episodes[0]["success_once"]:
        raise ValueError("first isolated duplicate does not match evidence")
    if order.get("after_warmup") != episodes[-1]["success_once"]:
        raise ValueError("last repeated seed does not match evidence")
    unique_counts = {
        arm: sum(int(out[arm]) for out in by_seed.values())
        for arm in ARMS
    }
    if unique_counts != {"source": 14, "compiled": 14, "naive": 0}:
        raise ValueError(f"frozen evidence differs from claimed unique-seed outcome: {unique_counts}")
    return {
        "status": "audit_pass",
        "origin_run": SOURCE_RUN,
        "origin_source_sha": SOURCE_HEAD,
        "origin_artifact_id": SOURCE_ARTIFACT_ID,
        "source_artifact_zip_sha256": SOURCE_ARTIFACT_ZIP_SHA256,
        "frozen_checkpoint_sha256": CHECKPOINT_SHA256,
        "total_episodes_including_repeat": len(episodes),
        "n_unique_source_seeds": len(by_seed),
        "repeated_seed": 10014,
        "per_arm_episode_count": per_episode_counts,
        "per_arm_unique_seed_count": unique_counts,
        "repeated_seed_order_check": True,
        "initial_state_match_checked": True,
        "main_limitation": (
            "14 unique intentionally chosen source seeds, not 15 independent "
            "draws; one PickCube task and one frozen PPO policy. Naive wrong-ABI "
            "copying is an intentionally ill-typed negative control; success "
            "here does not prove discovery of hidden semantics or superior "
            "cross-task learned-policy generalization."
        ),
        "external_validation": False,
    }


def self_test() -> None:
    # Synthetic structural test: force detection of hash tamper,
    # duplicate-seed manipulation, changed controller map and forged metrics.
    base = {
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_repo": "kattri15/actionshift-baselines",
        "checkpoint": "ppo/pick_cube_final_ckpt.pt",
        "policy_frozen": True,
        "backend": "physx_cpu",
        "controller_modes": {"source": "pd_ee_delta_pose", "compiled": "pd_ee_pose", "naive": "pd_ee_pose"},
        "episodes": [
            {
                "seed": seed,
                "success_once": {"source": True, "compiled": True, "naive": False},
                "episode_steps": {"source": 12, "compiled": 12, "naive": 50},
                "initial_obs_maxdiff": {"compiled": 0.0, "naive": 0.0},
                "detailed_trace": [{"step": 1}],
            }
            for seed in EXPECTED_SEED_ORDER
        ],
        "success_count": {"source": 15, "compiled": 15, "naive": 0},
        "denominator": 15,
    }
    order = {"claim": "exploratory order-sensitivity diagnostic; no holdout redefinition",
             "warmups": 13, "first": base["episodes"][0]["success_once"],
             "after_warmup": base["episodes"][-1]["success_once"]}
    assert audit(base, order)["n_unique_source_seeds"] == 14
    attacks = [
        ("checkpoint", {"checkpoint_sha256": "0" * 64}),
        ("reported denominator", {"denominator": 14}),
        ("extra success", {"success_count": {"source": 15, "compiled": 15, "naive": 1}}),
        ("wrong controller", {"controller_modes": {"source": "a", "compiled": "b", "naive": "b"}}),
    ]
    for name, changes in attacks:
        try:
            audit({**base, **changes}, order)
        except ValueError:
            pass
        else:
            raise AssertionError(f"tampered {name} passed")
    try:
        e = [{**x} for x in base["episodes"]]
        e[-1] = {**e[-1], "seed": 10015}
        audit({**base, "episodes": e}, order)
    except ValueError:
        pass
    else:
        raise AssertionError("seed replacement passed")
    print("five negative audit mutations rejected")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact-dir", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if args.artifact_dir is None:
        p.error("--artifact-dir is required except for --self-test")
    root = args.artifact_dir.resolve()
    def read_exact(name: str) -> dict:
        matches = list(root.rglob(name))
        if len(matches) != 1:
            raise ValueError(f"{name}: expected exactly one evidence file; found {len(matches)}")
        return json.loads(matches[0].read_text(encoding="utf-8"))
    result = audit(
        read_exact("frozen_ppo_controller_swap.json"),
        read_exact("seed10014_diagnostic.json"),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

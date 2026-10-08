#!/usr/bin/env python3
"""Independent two-cohort audit of frozen PPO controller-memory trade-offs.

Reads unchanged author-operated GitHub Actions archives from runs 37809684134
and 37809892720. Separately reconstructs refused cases, non-exact projections,
true PickCube outcomes, seeds and identity checks. No simulator or policy import.

The result is NOT proof that approximate projections are semantically exact or
deployment safe, and is NOT a third-party reproduction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_COHORTS = {
    "disjoint_seed32": {
        "run_id": 37809892720,
        "head_sha": "d95f136972c69e10c03dfaf032adfe0a958c45d9",
        "artifact_id": 11564138633,
        "archive_zip_sha256": "49fe6b02d34e1f205ed427a39643c72784e419725c6ed980d3b329f531f0b826",
        "seeds": tuple(range(21001,21033)),
        "success": {"source": 31, "memory": 3, "projected": 32, "naive": 0},
        "refusals": 29,
        "approximation_steps": 34,
    },
    "fixed_seed48": {
        "run_id": 37809684134,
        "head_sha": "f69db8a966b3991703965b1961d02837575fbc05",
        "artifact_id": 11563924211,
        "archive_zip_sha256": "15db4f03130102f45a4705d728c2a339a73691738832352849b0fe77777a5d95",
        "seeds": tuple(range(20001,20049)),
        "success": {"source": 47, "memory": 8, "projected": 48, "naive": 6},
        "refusals": 40,
        "approximation_steps": 43,
    },
}
CHECKPOINT_SHA = "3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8"
ARMS = ("source", "memory", "projected", "naive")
CONTRACTS = {
    "source": "pd_ee_delta_pose achieved-relative",
    "memory": "pd_ee_target_delta_pose with live previous-target inversion",
    "projected": "pd_ee_target_delta_pose with bounded non-exact projection",
    "naive": "pd_ee_target_delta_pose direct-copy",
}


def audit(raw: dict, name: str) -> dict:
    cfg = EXPECTED_COHORTS[name]
    if raw.get("checkpoint_sha256") != CHECKPOINT_SHA:
        raise ValueError("frozen official third-party policy weight digest changed")
    if raw.get("public_pretrained") is not True or raw.get("training_performed") is not False:
        raise ValueError("policy was not reported frozen and pretrained")
    if raw.get("backend") != "physx_cpu" or raw.get("controller_contracts") != CONTRACTS:
        raise ValueError("source/target controller ABI changed")
    episodes = raw.get("episodes")
    if not isinstance(episodes, list) or tuple(e.get("seed") for e in episodes) != cfg["seeds"]:
        raise ValueError("cohort seeds missing, duplicated or cherry-picked")
    counts = {key: 0 for key in ARMS}
    refusals, projected_approx_steps = 0, 0
    refusal_seeds, approx_seeds = [], []
    for e in episodes:
        if not isinstance(e.get("success_once"), dict):
            raise ValueError("no official task flag")
        if not isinstance(e.get("initial_obs_diff"), dict):
            raise ValueError("missing physical state identity check")
        for arm in ("memory", "projected", "naive"):
            diff = e["initial_obs_diff"].get(arm)
            if isinstance(diff, bool) or not isinstance(diff, (float, int)) or not 0 <= diff <= 5e-4:
                raise ValueError("initial physical/goal states not comparable")
        for arm in ARMS:
            flag = e["success_once"].get(arm, False)
            if type(flag) is not bool:
                raise ValueError("success flag must be a real Boolean")
            counts[arm] += int(flag)
        notes = e.get("refusals")
        projections = e.get("approximations")
        if not isinstance(notes, dict) or not isinstance(projections, dict):
            raise ValueError("missing refusal/approximation evidence")
        if any(k not in ("memory",) for k in notes):
            raise ValueError("unexpected fail-closed refusal identity")
        if "memory" in notes:
            item = notes["memory"]
            if item.get("reason") != "required delta outside target native bounds":
                raise ValueError("unsupported exact-refusal reason")
            if not isinstance(item.get("required_amp"), (int,float)) or not item["required_amp"] > 1.00001:
                raise ValueError("unsupported exact-refusal amplitude")
            refusals += 1
            refusal_seeds.append(e["seed"])
        if any(k not in ("projected",) for k in projections):
            raise ValueError("unknown approximation arm")
        for item in projections.get("projected", []):
            if item.get("exactness") != "NOT_EXACT":
                raise ValueError("approximate actuation was mislabeled exact")
            if not isinstance(item.get("required_native_amp"), (int,float)) or not item["required_native_amp"] > 1.00001:
                raise ValueError("non-exact projection lacks representability witness")
            projected_approx_steps += 1
            approx_seeds.append(e["seed"])
    if raw.get("success_count") != counts:
        raise ValueError("reported counts differ from original episode flags")
    if raw.get("refused_episodes") != refusals:
        raise ValueError("reported refusal count differs from episodes")
    if counts != cfg["success"] or refusals != cfg["refusals"]:
        raise ValueError("frozen cohort outcome does not match published logs")
    if projected_approx_steps != cfg["approximation_steps"]:
        raise ValueError("projection step count differs from published logs")
    return {
        "status": "audit_pass",
        "cohort": name,
        "source_run_id": cfg["run_id"],
        "source_head_sha": cfg["head_sha"],
        "source_artifact_id": cfg["artifact_id"],
        "source_zip_digest": cfg["archive_zip_sha256"],
        "distinct_seed_count": len(cfg["seeds"]),
        "success_count": counts,
        "exact_refusal_episodes": refusals,
        "nonexact_projection_steps": projected_approx_steps,
        "n_refusal_seeds": len(set(refusal_seeds)),
        "n_projection_seeds": len(set(approx_seeds)),
        "claim_boundary": (
            "Author-operated frozen learned-policy physical execution; "
            "exact adapter refuses out-of-native-bounds goals. Approximate "
            "projection succeeds on this cohort but deliberately changes "
            "the requested physical target: it is NOT an exact semantic "
            "authorization, safety guarantee, or new upstream adoption."
        ),
    }


def self_test():
    cfg = EXPECTED_COHORTS["disjoint_seed32"]
    events = []
    for i, seed in enumerate(cfg["seeds"]):
        ref = (i < 29)
        approx = [dict(step=4, required_native_amp=1.2, exactness="NOT_EXACT")] if ref else []
        if i < 5:  # 29 episodes; add five extra projection steps -> 34
            approx.append(dict(step=5, required_native_amp=1.3, exactness="NOT_EXACT"))
        events.append({
            "seed": seed, "success_once": {
                "source": i < 31,
                "memory": i >= 29,
                "projected": True,
                "naive": False,
            },
            "initial_obs_diff": {"memory": 0., "projected": 0., "naive": 0.},
            "refusals": {"memory": dict(reason="required delta outside target native bounds",
                                        required_amp=1.2)} if ref else {},
            "approximations": {"projected": approx} if approx else {},
        })
    good = {
        "checkpoint_sha256": CHECKPOINT_SHA, "public_pretrained": True,
        "training_performed": False, "backend": "physx_cpu",
        "controller_contracts": CONTRACTS, "episodes": events,
        "success_count": cfg["success"], "refused_episodes": 29,
    }
    assert audit(good, "disjoint_seed32")["nonexact_projection_steps"] == 34
    cases = [
        ("wrong checkpoint", {"checkpoint_sha256": "0"*64}),
        ("forged success", {"success_count": {**cfg["success"], "memory": 32}}),
        ("wrong denominator", {"episodes": events[:-1]}),
        ("wrong controller", {"controller_contracts": {**CONTRACTS, "memory": "unknown"}}),
        ("hidden refusals", {"refused_episodes": 0}),
    ]
    for label, mutation in cases:
        try:
            audit({**good, **mutation}, "disjoint_seed32")
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted tampering: {label}")
    altered_events = [{**e} for e in events]
    altered = dict(altered_events[0])
    altered["approximations"] = {"projected": [dict(step=4, required_native_amp=1.2, exactness="EXACT")]}
    altered_events[0] = altered
    try:
        audit({**good, "episodes": altered_events}, "disjoint_seed32")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted falsely exact projection")
    print("six adverse audit mutations rejected")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort", choices=tuple(EXPECTED_COHORTS))
    p.add_argument("--artifact-dir", type=Path)
    p.add_argument("--self-test", action="store_true")
    a=p.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.cohort or not a.artifact_dir:
        p.error("--cohort and --artifact-dir required")
    files=list(a.artifact_dir.rglob("frozen_ppo_target_memory.json"))
    if len(files)!=1:
        raise ValueError(f"expected one unmodified source JSON, found {len(files)}")
    raw=json.loads(files[0].read_text(encoding="utf-8"))
    print(json.dumps(audit(raw,a.cohort),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

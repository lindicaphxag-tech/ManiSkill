"""Reconstruct controller *state-memory* ablation from authentic per-seed logs.

No pooling of unlike task distributions, no label-imputation for unexecuted
episodes, no independent external-replication claim. Uses two different,
source-frozen PPO/checkpoint and ManiSkill task cohorts.

Usage:
  python research/frozen_policy_transfer/state_memory_mechanism.py
"""
from __future__ import annotations

import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRECOMMITTED = {
    "PickCube": {
        "file": ROOT / "evidence/pickcube_memory_blind_ablation_22001_22032.json",
        "run_id": 37812437614,
        "seed_start": 22001,
        "frozen_hash": "3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8",
        "preregister_commit": "1d2767400492759fc612b46efe85a7572a5e679c",
        "no_memory_arm": "memory_blind",
        "margin_predeclared": True,
    },
    "PushCube": {
        "file": ROOT / "evidence/pushcube_holdout_41001_41032.json",
        "run_id": 37810502800,
        "seed_start": 41001,
        "frozen_hash": "a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf",
        "preregister_commit": "872b633b68499149c7b41685a8d4b453c08f6663",
        "no_memory_arm": "stateless",
        "margin_predeclared": False,  # Source-cohort holdout was frozen, not this contrast
    },
}


def conditional_mcnemar_two_sided(b: int, c: int) -> float:
    if type(b) is not int or type(c) is not int or min(b, c) < 0:
        raise ValueError("paired discordances must be nonnegative ints")
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c)+1)) / 2**n)


def reconstruct(task: str, data: dict) -> dict:
    if task not in PRECOMMITTED:
        raise ValueError("task not in frozen source set")
    cfg = PRECOMMITTED[task]
    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("missing source commit provenance")
    expected_sha = (
        source.get("frozen_checkpoint_sha256") if task == "PickCube"
        else source.get("checkpoint_sha256")
    )
    run = source.get("run_id")
    if (
        run != cfg["run_id"]
        or expected_sha != cfg["frozen_hash"]
        or source.get("preregistration_commit") != cfg["preregister_commit"]
        or data.get("n", data.get("seed_count")) != 32
    ):
        raise ValueError("untrusted source/checkpoint/protocol identity")
    rows = data.get("rows")
    if (
        not isinstance(rows, list)
        or tuple(item.get("seed") for item in rows)
        != tuple(range(cfg["seed_start"], cfg["seed_start"]+32))
    ):
        raise ValueError("cohort not the original unique 32 precommitted seeds")
    good, bad = "projected", cfg["no_memory_arm"]
    b = c = both = neither = 0
    projections = {good: 0, bad: 0}
    for row in rows:
        flags, steps = row.get("success_once"), row.get("steps")
        if not isinstance(flags, dict) or not isinstance(steps, dict):
            raise ValueError("missing per-world original physics outcomes")
        values = {}
        for arm in (good, bad):
            flag = flags.get(arm, False)
            if type(flag) is not bool:
                raise ValueError("non-Boolean observed task success")
            if arm not in steps and arm not in (row.get("refusals") or {}):
                raise ValueError("missing physical execution/refusal for " + arm)
            values[arm] = flag
            observed = (row.get("approximations") or {}).get(arm, [])
            if not isinstance(observed, list):
                raise ValueError("invalid approximate-step log")
            if any(x.get("exactness") != "NOT_EXACT" for x in observed):
                raise ValueError("an inexact correction was misrepresented as exact")
            projections[arm] += len(observed)
        u, v = values[good], values[bad]
        if u and v: both += 1
        elif u: b += 1
        elif v: c += 1
        else: neither += 1
    counted = {good:b+both,bad:c+both}
    record = data.get("paired_successes", data.get("count_success"))
    if not isinstance(record, dict) or any(record.get(k)!=v for k,v in counted.items()):
        raise ValueError("stored aggregates differ from verified original episodes")
    return {
        "task":task,
        "n_paired_orig_episode_seeds":32,
        "full_uses_live_previous_target":counted[good],
        "identical_bounded_adapter_but_without_memory":counted[bad],
        "full_only":b,"blind_only":c,"both":both,"neither":neither,
        "net_gain":b-c,
        "unadjusted_exact_two_sided_mcnemar_p":conditional_mcnemar_two_sided(b,c),
        "inexact_bounded_steps":projections,
        "memory_ablation_margin_preregistered":cfg["margin_predeclared"],
        "original_source_run":run,
        "scope":"owner-operated real ManiSkill PhysX; no real-hardware safety/adoption guarantee",
    }


def main() -> None:
    results = [reconstruct(task,json.loads(cfg["file"].read_text(encoding="utf-8")))
               for task,cfg in PRECOMMITTED.items()]
    print(json.dumps({
        "schema":"two_task_stateful_controller_memory_counterfactual_v1",
        "results":results,
        "notice":[
            "PickCube 22001-22032: explicit separate memory-identity ablation was preregistered",
            "PushCube 41001-41032: stateless ablation was in frozen code, but retrospective mechanism margin/p-value were not preregistered",
            "Unadjusted exact McNemar inference is descriptive, not multiplicity-corrected",
            "No per-task source checkpoint retraining, new VLA policy, external independent execution or real robot physical safety proven",
        ],
    },sort_keys=True,indent=2))


if __name__ == "__main__":
    main()

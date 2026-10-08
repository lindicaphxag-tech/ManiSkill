"""Frozen independent PullCube+StackCube controller-ABI replication auditor.

Only five original actions per task×seed, full 64 paired-seed denominator.
A failure of original frozen policy competence is explicit, not evidence
for or against the transfer adapter. Never drop a failed experiment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TASKS = {
    "pull_cube": {
        "task": "PullCube-v1",
        "sha256": "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
        "seeds": list(range(51001, 51033)),
    },
    "stack_cube": {
        "task": "StackCube-v1",
        "sha256": "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
        "seeds": list(range(61001, 61033)),
    },
}
ARMS = ("source", "memory", "projected", "stateless", "naive")
HF_REVISION = "6bdeb28810330ab5425ccd629bb561c58a56ff85"
PROTOCOL = "research/ACTION_ABI_PULL_STACK_PREREGISTERED_V1.json"


def audit_one(task_name, files):
    spec = TASKS[task_name]
    if len(files) != 4:
        raise ValueError(f"{task_name}: need exactly four eight-seed blocks; found {len(files)}")
    rows = {}
    seen_chunks = set()
    for file in files:
        q = json.loads(file.read_text(encoding="utf-8"))
        chunk = q.get("seed_chunk")
        if chunk not in ("0", "1", "2", "3") or chunk in seen_chunks:
            raise ValueError("Missing/duplicate/wrong chunk")
        seen_chunks.add(chunk)
        start = 8 * int(chunk)
        chunk_seeds = spec["seeds"][start:start+8]
        if q.get("seed_list") != chunk_seeds or q.get("all_preregistered_seeds") != [
            spec["seeds"][0], spec["seeds"][-1]
        ]:
            raise ValueError("Retuned or truncated seed list")
        if (q.get("protocol") != PROTOCOL or q.get("task") != spec["task"] or
                q.get("checkpoint_sha256") != spec["sha256"] or
                q.get("hf_revision") != HF_REVISION or
                q.get("training_performed") is not False or
                q.get("backend") != "physx_cpu"):
            raise ValueError("Experiment source provenance/model/task changed")
        trials = q.get("episodes", [])
        if len(trials) != 8 or [x.get("seed") for x in trials] != chunk_seeds:
            raise ValueError("A source episode was skipped, duplicated or reordered")
        if set(q.get("success_count", {})) != set(ARMS):
            raise ValueError("A planned controller arm is missing")
        for arm in ARMS:
            actual = sum(int(bool(x.get("success_once", {}).get(arm, False))) for x in trials)
            if actual != q["success_count"][arm]:
                raise ValueError("Original reported task-success count does not replay")
        for row in trials:
            seed = row.get("seed")
            if seed in rows:
                raise ValueError("Duplicated paired physical state")
            for arm in ("memory", "projected", "stateless", "naive"):
                err = row.get("initial_obs_diff", {}).get(arm)
                if not isinstance(err, (float, int)) or not 0 <= err <= 5e-4:
                    raise ValueError("Initial source task/observation ABI mismatch")
            for arm in ARMS:
                outcome = row.get("success_once", {}).get(arm, False)
                if type(outcome) is not bool:
                    raise ValueError("Invalid official task-success signal")
                refused = row.get("refusals", {}).get(arm)
                step = row.get("steps", {}).get(arm)
                if refused:
                    if arm != "memory" or outcome:
                        raise ValueError("Nonexact rejection or successful refusal")
                elif not isinstance(step, int) or not 1 <= step <= 50:
                    raise ValueError("Absent/incomplete actual controller execution")
            for arm, corrections in row.get("approximations", {}).items():
                if arm not in ("projected", "stateless"):
                    raise ValueError("An arm without projection claimed approximate correction")
                if not isinstance(corrections, list) or any(
                    c.get("exactness") != "NOT_EXACT" for c in corrections
                ):
                    raise ValueError("Approximate command cannot be called exact")
            rows[seed] = row
    if set(rows) != set(spec["seeds"]):
        raise ValueError("Not all preregistered original-task episodes present")
    ordered = [rows[k] for k in spec["seeds"]]
    count = {arm: sum(int(row.get("success_once", {}).get(arm, False)) for row in ordered)
             for arm in ARMS}
    memory_only = sum(bool(x["success_once"].get("projected")) and
                      not bool(x["success_once"].get("stateless")) for x in ordered)
    blind_only = sum(bool(x["success_once"].get("stateless")) and
                     not bool(x["success_once"].get("projected")) for x in ordered)
    competent = count["source"] >= 24
    return {
        "task": spec["task"],
        "task_key": task_name,
        "checkpoint_sha256": spec["sha256"],
        "frozen_source_qualified": competent,
        "status": ("SOURCE_INCOMPETENT" if not competent else
                   "PREDECLARED_MEMORY_GAIN_PRESENT" if memory_only-blind_only >= 6 else
                   "PREDECLARED_MEMORY_GAIN_NOT_PRESENT"),
        "n": 32,
        "success_by_arm": count,
        "projected_only_success": memory_only,
        "stateless_only_success": blind_only,
        "primary_net_memory_gain": memory_only-blind_only,
        "refused_exact_episodes": sum(bool(x.get("refusals", {}).get("memory")) for x in ordered),
        "nonexact_projection_steps": {
            name: sum(len(x.get("approximations", {}).get(name, [])) for x in ordered)
            for name in ("projected", "stateless")
        },
        "rows": ordered,
    }


def aggregate(root: Path):
    all_files = sorted(root.rglob("abi_independent_*_chunk_*.json"))
    if len(all_files) != 8:
        raise ValueError("Expected eight exact state JSON chunks, four per task")
    results = {}
    for name in TASKS:
        files = [f for f in all_files if f.name.startswith(f"abi_independent_{name}_chunk_")]
        results[name] = audit_one(name, files)
    expected_filenames = {f"abi_independent_{task}_chunk_{i}.json"
                          for task in TASKS for i in range(4)}
    if {f.name for f in all_files} != expected_filenames:
        raise ValueError("Unregistered, duplicated or missing experiment artifact")
    return {
        "schema": "action_abi_pull_stack_prospective_replication_v1",
        "source_protocol": PROTOCOL,
        "hf_model_revision": HF_REVISION,
        "n_independent_tasks": 2,
        "total_original_task_states": 64,
        "preregistered": True,
        "real_robot_test": False,
        "third_party_independent_reproduction": False,
        "no_new_policy_training": True,
        "results": results,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    q = p.parse_args()
    result = aggregate(q.input_dir)
    q.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("PULL_STACK_FROZEN_PROSPECTIVE_REPLICATION", json.dumps({
        name: {k: v[k] for k in ("status", "n", "success_by_arm",
                               "projected_only_success", "stateless_only_success")}
        for name, v in result["results"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()

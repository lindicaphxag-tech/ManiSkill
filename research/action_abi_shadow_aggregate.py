"""Six-arm, preregistered strong-baseline target-memory observability audit.

All 64 original seed-level PhysX outcomes are retained. Source-model
competence, shadow equivalence and goal-reconstruction error are independent
gates. This is an author-operated simulator study, not external validation.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

TASKS = {
    "pull_cube": dict(env="PullCube-v1", first=71001,
        sha="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube": dict(env="StackCube-v1", first=81001,
        sha="e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
ARMS = ("source", "memory", "projected", "stateless", "naive", "shadow")
PROTOCOL = "research/ACTION_ABI_SHADOW_OBSERVER_PREREG_V1.json"
HF_REVISION = "6bdeb28810330ab5425ccd629bb561c58a56ff85"


def audit_one(task_name: str, files: list[Path]) -> dict:
    spec = TASKS[task_name]
    if len(files) != 4:
        raise ValueError("exactly four source chunks required per task")
    rows = {}
    seen_chunks = set()
    for file in files:
        block = json.loads(file.read_text(encoding="utf-8"))
        chunk = block.get("seed_chunk")
        if chunk not in ("0", "1", "2", "3") or chunk in seen_chunks:
            raise ValueError("missing, duplicate or unregistered chunk")
        seen_chunks.add(chunk)
        expected = list(range(spec["first"] + 8 * int(chunk),
                              spec["first"] + 8 * int(chunk) + 8))
        if (block.get("seed_list") != expected
                or block.get("all_preregistered_seeds") !=
                [spec["first"], spec["first"] + 31]
                or block.get("task") != spec["env"]
                or block.get("checkpoint_sha256") != spec["sha"]
                or block.get("hf_revision") != HF_REVISION
                or block.get("protocol") != PROTOCOL
                or block.get("training_performed") is not False
                or block.get("backend") != "physx_cpu"):
            raise ValueError("source protocol/model/state provenance mismatch")
        episodes = block.get("episodes")
        if (not isinstance(episodes, list) or len(episodes) != 8 or
                [r.get("seed") for r in episodes] != expected):
            raise ValueError("incomplete or resequenced original seed states")
        if set(block.get("success_count", {})) != set(ARMS):
            raise ValueError("six-arm source result missing")
        for arm in ARMS:
            count = sum(int(r.get("success_once", {}).get(arm, False))
                        for r in episodes)
            if count != block["success_count"][arm]:
                raise ValueError("source score does not reaggregate")
        for row in episodes:
            seed = row["seed"]
            if seed in rows:
                raise ValueError("duplicate seed")
            if set(row.get("success_once", {})) != set(ARMS):
                raise ValueError("not all six-arm task flags present")
            for arm in ARMS:
                success = row["success_once"][arm]
                if type(success) is not bool:
                    raise ValueError("success must be actual boolean")
                step = row.get("steps", {}).get(arm)
                refused = row.get("refusals", {}).get(arm)
                if refused:
                    if arm != "memory" or success:
                        raise ValueError("incorrect refusal semantic status")
                elif type(step) is not int or not 1 <= step <= 50:
                    raise ValueError("incomplete physical controller rollout")
            for arm in ARMS[1:]:
                residual = row.get("initial_obs_diff", {}).get(arm)
                if type(residual) not in (int, float) or not 0 <= residual <= 5e-4:
                    raise ValueError("non-identical initial physical state")
            for key in ("shadow_max_position_goal_residual_m",
                        "shadow_max_rotation_goal_residual_rad"):
                v = row.get(key)
                if type(v) not in (int, float) or not math.isfinite(v) or v < 0:
                    raise ValueError("missing/nonfinite shadow goal audit")
            for arm, events in row.get("approximations", {}).items():
                if arm not in ("projected", "stateless", "shadow"):
                    raise ValueError("unexpected approximate arm")
                if not isinstance(events, list) or any(
                        event.get("exactness") != "NOT_EXACT" for event in events):
                    raise ValueError("bounded approximation falsely called exact")
            rows[seed] = row
    if set(rows) != set(range(spec["first"], spec["first"] + 32)):
        raise ValueError("not all frozen original states accounted")
    ordered = [rows[i] for i in range(spec["first"], spec["first"] + 32)]
    count = {a:sum(int(row["success_once"][a]) for row in ordered) for a in ARMS}
    agreement = sum(row["success_once"]["shadow"] == row["success_once"]["projected"]
                    for row in ordered)
    live_only = sum(row["success_once"]["projected"] and
                    not row["success_once"]["shadow"] for row in ordered)
    shadow_only = sum(row["success_once"]["shadow"] and
                      not row["success_once"]["projected"] for row in ordered)
    max_p = max(row["shadow_max_position_goal_residual_m"] for row in ordered)
    max_r = max(row["shadow_max_rotation_goal_residual_rad"] for row in ordered)
    competent = count["source"] >= 24
    matched = agreement >= 30 and max_p <= 1e-4
    return {
        "task":spec["env"],"seeds":[spec["first"],spec["first"]+31],
        "model_sha256":spec["sha"],"n":32,"success":count,
        "source_competent":competent,
        "shadow_observer_gate":(
            "SOURCE_INCOMPETENT" if not competent else
            "MATCHED" if matched else "NOT_MATCHED"),
        "matched_episode_outcomes":agreement,"live_only":live_only,
        "shadow_only":shadow_only,
        "max_goal_position_residual_m":max_p,
        "max_goal_rotation_residual_rad":max_r,
        "nonexact_projection_steps":{
            name:sum(len(r.get("approximations", {}).get(name, [])) for r in ordered)
            for name in ("projected","stateless","shadow")},
        "rows":ordered,
    }


def aggregate(folder: Path) -> dict:
    files = sorted(folder.rglob("abi_shadow_*_chunk_*.json"))
    if len(files) != 8:
        raise ValueError("eight original task×chunk result files required")
    needed = {f"abi_shadow_{task}_chunk_{i}.json"
              for task in TASKS for i in range(4)}
    if {f.name for f in files} != needed:
        raise ValueError("unregistered original source file")
    return {
        "schema":"action_abi_shadow_target_observer_prospective_v1",
        "protocol":PROTOCOL,
        "source_commit":"9ffa86c6d3a86d2cee44b6e13c560033a8b373cf",
        "n_task_families":2,"n_original_task_states":64,
        "arms":list(ARMS),
        "results":{
            task:audit_one(task,[
                f for f in files if f.name.startswith(f"abi_shadow_{task}_chunk_")
            ]) for task in TASKS
        },
        "third_party_independently_reproduced":False,
        "no_policy_training":True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args = parser.parse_args()
    output = aggregate(args.input_dir)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("SHADOW_OBSERVER_PROSPECTIVE", json.dumps({
        key:{k:r[k] for k in (
            "shadow_observer_gate","success","matched_episode_outcomes",
            "live_only","shadow_only","max_goal_position_residual_m")}
        for key,r in output["results"].items()
    },sort_keys=True))


if __name__=="__main__":
    main()

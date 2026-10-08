"""Immutable five-arm, 32-seed real PhysX closed-loop ablation audit.

The protocol and seed blocks were preregistered before runner edits.
No failed episode may be dropped; source competence is a separate gate.
No CI-green status is mistaken for positive research evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ARMS = ("source", "memory", "projected", "memory_blind_projected", "naive")
SPLIT = (range(22001, 22009), range(22009, 22017),
         range(22017, 22025), range(22025, 22033))
MODEL = "3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8"
PROTOCOL = "research/STATEFUL_ABI_MEMORY_ABLATION_FROZEN_V1.json"


def aggregate(folder: Path):
    files = sorted(folder.rglob("stateful_abi_memory_ablation_chunk_*.json"))
    if len(files) != 4:
        raise ValueError(f"Expected 4 complete artifact files, got {len(files)}")
    records = {}
    per_chunk = {}
    for file in files:
        block = json.loads(file.read_text(encoding="utf-8"))
        chunk = block.get("seed_chunk")
        if chunk not in ("0", "1", "2", "3") or chunk in per_chunk:
            raise ValueError("Invalid or duplicate chunk")
        seeds = list(SPLIT[int(chunk)])
        if block.get("seed_list") != seeds or block.get("all_preregistered_seeds") != [22001, 22032]:
            raise ValueError(f"Unexpected or missing preregistered seeds in chunk {chunk}")
        if block.get("checkpoint_sha256") != MODEL or block.get("training_performed") is not False:
            raise ValueError("Frozen PPO checkpoint/provenance changed")
        if block.get("backend") != "physx_cpu" or block.get("protocol") != PROTOCOL:
            raise ValueError("Simulator/backend or frozen protocol changed")
        if len(block.get("episodes", [])) != len(seeds):
            raise ValueError("Incomplete chunk")
        by_seed = {row["seed"]: row for row in block["episodes"]}
        if len(by_seed) != 8 or set(by_seed) != set(seeds):
            raise ValueError("Missing, duplicated or swapped frozen episode IDs")
        if set(block.get("success_count", {})) != set(ARMS):
            raise ValueError("Incomplete control-arm success counts")
        for arm in ARMS:
            count = sum(bool(row.get("success_once", {}).get(arm, False)) for row in block["episodes"])
            if count != block["success_count"][arm]:
                raise ValueError(f"Tampered success denominator for {chunk}/{arm}")
        for row in block["episodes"]:
            if row.get("seed") in records:
                raise ValueError("Repeated episode between blocks")
            for arm in ("memory", "projected", "memory_blind_projected", "naive"):
                error = row.get("initial_obs_diff", {}).get(arm, None)
                if not isinstance(error, (float, int)) or not 0 <= error <= 5e-4:
                    raise ValueError(f"Nonidentical task reset / observation ABI: {row['seed']} {arm}")
            for arm in ARMS:
                success = row.get("success_once", {}).get(arm, False)
                if not isinstance(success, bool):
                    raise ValueError("Nonboolean official success indicator")
                steps = row.get("steps", {}).get(arm)
                refusal = row.get("refusals", {}).get(arm)
                if refusal:
                    if arm != "memory" or success:
                        raise ValueError("Only exact-only arm may refuse; refusal is failure")
                elif not isinstance(steps, int) or not 1 <= steps <= 50:
                    raise ValueError(f"Missing or out-of-range controller steps: {row['seed']} {arm}")
            for arm, corrections in row.get("approximations", {}).items():
                if arm not in ("projected", "memory_blind_projected"):
                    raise ValueError("Non-projection arm generated correction")
                if any(c.get("exactness") != "NOT_EXACT" for c in corrections):
                    raise ValueError("Inexact physical controller action mislabelled")
            records[row["seed"]] = row
        per_chunk[chunk] = str(file)

    if set(records) != set(range(22001, 22033)):
        raise ValueError("Incomplete or inconsistent full prespecified denominator")
    ordered = [records[i] for i in range(22001, 22033)]
    totals = {arm: sum(int(row.get("success_once", {}).get(arm, False)) for row in ordered)
              for arm in ARMS}
    memory_only = sum(bool(r.get("success_once", {}).get("projected")) and
                      not bool(r.get("success_once", {}).get("memory_blind_projected")) for r in ordered)
    blind_only = sum(bool(r.get("success_once", {}).get("memory_blind_projected")) and
                     not bool(r.get("success_once", {}).get("projected")) for r in ordered)
    net = memory_only - blind_only
    competence = totals["source"] >= 24
    mechanism = competence and net >= 6
    corrections = {arm: sum(len(r.get("approximations", {}).get(arm, [])) for r in ordered)
                   for arm in ("projected", "memory_blind_projected")}
    data = {
        "schema": "stateful_action_abi_memory_mechanism_v1",
        "protocol": PROTOCOL,
        "source_model_sha256": MODEL,
        "seed_range_inclusive": [22001, 22032],
        "status": "MECHANISM_SUPPORTED_SINGLE_TASK" if mechanism else (
            "SOURCE_INCOMPETENT" if not competence else "MECHANISM_NOT_SUPPORTED"
        ),
        "task": "PickCube-v1",
        "environment": "genuine ManiSkill PhysX CPU",
        "observations": "actual closed-loop official task info.success at any step",
        "frozen_model": True,
        "independent_third_party_replication": False,
        "robot_hardware_tested": False,
        "total_distinct_original_states": 32,
        "successful_episodes_by_arm": totals,
        "primary_memory_projected_only": memory_only,
        "primary_memory_blind_only": blind_only,
        "primary_net_benefit": net,
        "source_competence_gate_min_24": competence,
        "memory_information_gate_min_net_6": mechanism,
        "nonexact_action_projection_steps": corrections,
        "refusal_episodes_exact_only": sum(bool(r.get("refusals", {}).get("memory")) for r in ordered),
        "all_rows": ordered,
    }
    return data


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--input-dir", required=True, type=Path)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    result = aggregate(args.input_dir)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("PRECOMMITTED_ABLATION_SUMMARY", json.dumps({
        "status": result["status"],
        "counts": result["successful_episodes_by_arm"],
        "discordant": [result["primary_memory_projected_only"],
                       result["primary_memory_blind_only"]],
        "net": result["primary_net_benefit"],
        "n": result["total_distinct_original_states"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()

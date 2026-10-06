from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import h5py
import numpy as np

from cst.core import JointControllerContext, JointGoalChart
from cst.provenance import reconstruct_joint_goal_trace


BASE = "https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/resolve/main/demos"
TASKS = ("PickCube-v1", "StackCube-v1", "PegInsertionSide-v1", "PlugCharger-v1")
BOUND = 0.1
ARM = slice(0, 7)
ARM_QPOS = slice(13, 20)
OUT = Path("/tmp/cst_official_sequence_provenance_v0.json")


def download(url: str, path: Path) -> None:
    urllib.request.urlretrieve(url, path)


def chart(mode: str) -> JointGoalChart:
    return JointGoalChart(
        mode=mode,
        normalized=True,
        lower=-BOUND,
        upper=BOUND,
    )


def audit_task(task: str) -> dict:
    prefix = f"{BASE}/{task}/motionplanning"
    json_path = Path(f"/tmp/{task}.prov.json")
    h5_path = Path(f"/tmp/{task}.prov.h5")
    download(f"{prefix}/trajectory.json", json_path)
    meta = json.loads(json_path.read_text())
    if meta["env_info"]["env_kwargs"]["control_mode"] != "pd_joint_pos":
        raise RuntimeError(f"{task}: frozen source is not pd_joint_pos")
    download(f"{prefix}/trajectory.h5", h5_path)
    sha = hashlib.sha256(h5_path.read_bytes()).hexdigest()

    dc_chart = chart("delta_current")
    dt_chart = chart("delta_target")
    trajectories = 0
    actions_total = 0
    dc_decodable = 0
    dt_decodable = 0
    dc_max_residual = 0.0
    dt_max_residual = 0.0
    dt_reference_max_residual = 0.0
    dc_action_only_refusals = 0
    dt_action_only_refusals = 0

    with h5py.File(h5_path, "r") as f:
        keys = sorted(f.keys(), key=lambda x: int(x.split("_", 1)[1]))
        for key in keys:
            g = f[key]
            actions = np.asarray(g["actions"], dtype=np.float64)
            articulations = g["env_states/articulations"]
            candidates = [
                name
                for name in articulations.keys()
                if isinstance(articulations[name], h5py.Dataset)
                and articulations[name].ndim == 2
                and articulations[name].shape[1] == 31
            ]
            if len(candidates) != 1:
                raise RuntimeError(f"{task}/{key}: ambiguous Panda state dataset")
            panda = np.asarray(articulations[candidates[0]], dtype=np.float64)
            goals = actions[:, ARM]
            measured = panda[:-1, ARM_QPOS]
            if panda.shape[0] != actions.shape[0] + 1:
                raise RuntimeError(f"{task}/{key}: state/action length mismatch")

            # Construct the native incremental action sequences that would encode
            # the official absolute semantic goals under each controller chart.
            dc_physical = goals - measured
            previous_target = np.vstack([measured[0], goals[:-1]])
            dt_physical = goals - previous_target
            dc_native = dc_physical / BOUND
            dt_native = dt_physical / BOUND

            # delta_current is only losslessly identifiable with the measured
            # per-step q_current trace.
            try:
                reconstruct_joint_goal_trace(dc_chart, dc_native)
            except ValueError:
                dc_action_only_refusals += 1
            else:
                raise RuntimeError(
                    "delta_current action-only sequence unexpectedly decoded"
                )

            dc_result = reconstruct_joint_goal_trace(
                dc_chart,
                dc_native,
                q_current_trace=measured,
            )
            dc_residual = float(
                np.max(np.abs(dc_result.semantic_goals - goals))
            )
            dc_max_residual = max(dc_max_residual, dc_residual)
            dc_decodable += int(dc_residual <= 1e-10)

            # delta_target requires only q_target at reset. Thereafter q_target
            # is reconstructed from the action sequence, without measured state.
            try:
                reconstruct_joint_goal_trace(dt_chart, dt_native)
            except ValueError:
                dt_action_only_refusals += 1
            else:
                raise RuntimeError(
                    "delta_target without initial q_target unexpectedly decoded"
                )

            dt_result = reconstruct_joint_goal_trace(
                dt_chart,
                dt_native,
                initial_context=JointControllerContext(
                    q_target=measured[0].copy()
                ),
            )
            dt_residual = float(
                np.max(np.abs(dt_result.semantic_goals - goals))
            )
            ref_residual = float(
                np.max(np.abs(dt_result.reference_trace - previous_target))
            )
            dt_max_residual = max(dt_max_residual, dt_residual)
            dt_reference_max_residual = max(
                dt_reference_max_residual, ref_residual
            )
            dt_decodable += int(
                dt_residual <= 1e-10 and ref_residual <= 1e-10
            )

            trajectories += 1
            actions_total += len(actions)

    return {
        "task": task,
        "h5_sha256": sha,
        "trajectories": trajectories,
        "actions": actions_total,
        "delta_current": {
            "trajectories_losslessly_decoded_with_q_current_trace": dc_decodable,
            "action_only_refusals": dc_action_only_refusals,
            "max_semantic_goal_residual": dc_max_residual,
            "minimal_provenance": "q_current at every action",
        },
        "delta_target": {
            "trajectories_losslessly_decoded_from_initial_q_target": dt_decodable,
            "missing_initial_q_target_refusals": dt_action_only_refusals,
            "max_semantic_goal_residual": dt_max_residual,
            "max_reconstructed_reference_residual": dt_reference_max_residual,
            "minimal_provenance": "initial q_target plus action sequence",
        },
    }


def main() -> None:
    rows = [audit_task(task) for task in TASKS]
    result = {
        "protocol": "OFFICIAL_SEQUENCE_PROVENANCE_V0",
        "tasks": rows,
        "aggregate": {
            "tasks": len(rows),
            "trajectories": sum(x["trajectories"] for x in rows),
            "actions": sum(x["actions"] for x in rows),
            "delta_current_trajectories_decoded_with_required_trace": sum(
                x["delta_current"][
                    "trajectories_losslessly_decoded_with_q_current_trace"
                ]
                for x in rows
            ),
            "delta_current_action_only_refusals": sum(
                x["delta_current"]["action_only_refusals"] for x in rows
            ),
            "delta_target_trajectories_decoded_from_one_initial_state": sum(
                x["delta_target"][
                    "trajectories_losslessly_decoded_from_initial_q_target"
                ]
                for x in rows
            ),
            "delta_target_missing_initial_state_refusals": sum(
                x["delta_target"]["missing_initial_q_target_refusals"]
                for x in rows
            ),
            "delta_current_max_semantic_goal_residual": max(
                x["delta_current"]["max_semantic_goal_residual"] for x in rows
            ),
            "delta_target_max_semantic_goal_residual": max(
                x["delta_target"]["max_semantic_goal_residual"] for x in rows
            ),
            "delta_target_max_reference_residual": max(
                x["delta_target"]["max_reconstructed_reference_residual"]
                for x in rows
            ),
        },
        "claim_boundary": (
            "E1 sequence semantic identifiability only; no realized dynamics "
            "or task-success equivalence"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("CST_OFFICIAL_SEQUENCE_PROVENANCE_V0")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

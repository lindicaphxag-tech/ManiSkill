#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import mani_skill
from mani_skill.agents.controllers import PDEEPoseController
from mani_skill.trajectory import replay_trajectory
from mani_skill.trajectory.utils.actions import conversion as action_conversion


def _jsonable(value):
    arr = np.asarray(value)
    if arr.ndim == 0:
        return float(arr)
    return arr.astype(np.float64).tolist()


def _corpus_digest(records):
    payload = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--traj-path", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--corpus", required=True)
    p.add_argument("--expected-source-root", type=Path, required=True)
    args=p.parse_args()

    actual=Path(mani_skill.__file__).resolve()
    expected=args.expected_source_root.resolve()
    if expected not in actual.parents:
        raise SystemExit(f"wrong ManiSkill source imported: {actual}; expected {expected}")

    original=action_conversion.delta_pose_to_pd_ee_delta
    records=[]

    def instrumented(controller, delta_pose, pos_only=False):
        result=original(controller, delta_pose, pos_only=pos_only)
        if pos_only or not isinstance(controller, PDEEPoseController):
            return result

        low=controller.action_space_low.detach().cpu().numpy()
        high=controller.action_space_high.detach().cpu().numpy()
        records.append(
            {
                "p": np.asarray(delta_pose.p, dtype=np.float64).tolist(),
                "q_inverse_input": np.asarray(delta_pose.q, dtype=np.float64).tolist(),
                "action_space_low": np.asarray(low, dtype=np.float64).tolist(),
                "action_space_high": np.asarray(high, dtype=np.float64).tolist(),
                "config": {
                    "use_delta": bool(controller.config.use_delta),
                    "normalize_action": bool(controller.config.normalize_action),
                    "rot_lower": _jsonable(controller.config.rot_lower),
                    "rot_upper": _jsonable(controller.config.rot_upper),
                    "frame": str(controller.config.frame),
                },
            }
        )
        return result

    action_conversion.delta_pose_to_pd_ee_delta=instrumented
    try:
        replay_trajectory.main(
            replay_trajectory.Args(
                traj_path=args.traj_path,
                sim_backend="physx_cpu",
                obs_mode="state",
                target_control_mode="pd_ee_delta_pose",
                save_traj=False,
                save_video=False,
                use_first_env_state=True,
                count=args.count,
                num_envs=1,
            )
        )
    finally:
        action_conversion.delta_pose_to_pd_ee_delta=original

    if not records:
        raise SystemExit("no PDEEPose delta conversion calls captured")

    document={
        "schema_version":1,
        "corpus":args.corpus,
        "source_root":str(expected),
        "mani_skill_import":str(actual),
        "task":"PegInsertionSide-v1",
        "trajectory_count_requested":args.count,
        "request_count":len(records),
        "records":records,
        "claim_boundary":(
            "Frozen production delta-pose requests and exact controller normalization "
            "context captured during official-demo replay. This corpus contains no "
            "post-hoc semantic-fidelity score."
        ),
    }
    document["corpus_sha256"]=_corpus_digest(records)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(document,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in document.items() if k!="records"},indent=2,sort_keys=True))


if __name__=="__main__":
    main()

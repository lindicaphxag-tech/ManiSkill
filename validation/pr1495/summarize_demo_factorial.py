#!/usr/bin/env python3
"""Summarize a four-cell ManiSkill controller/converter factorial on official demos.

The assay uses the same ordered source episodes in every cell and saves failures
with --allow-failure, so output trajectory index i is paired to source episode i.
This script reports behavioral success and normalized action-space differences.
It intentionally does not infer physical SO(3) error from normalized actions
because the controller scaling convention is itself one of the interventions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


VARIANTS = ("old_old", "controller_only", "converter_only", "combined")


def _traj_keys(handle: h5py.File) -> list[str]:
    keys = [k for k in handle.keys() if k.startswith("traj_")]
    return sorted(keys, key=lambda k: int(k.split("_", 1)[1]))


def _load_variant(root: Path, name: str, source_ids: list[int]) -> dict:
    demo_root = root / f"demos-{name}"
    h5_path = demo_root / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
    json_path = h5_path.with_suffix(".json")
    if not h5_path.exists() or not json_path.exists():
        raise FileNotFoundError(f"{name}: missing converted output")

    meta = json.loads(json_path.read_text())
    episodes = meta.get("episodes", [])
    if len(episodes) != len(source_ids):
        raise RuntimeError(
            f"{name}: expected {len(source_ids)} saved episodes, got {len(episodes)}"
        )

    actions: list[np.ndarray] = []
    h5_success: list[bool] = []
    steps: list[int] = []
    with h5py.File(h5_path, "r") as h5:
        keys = _traj_keys(h5)
        if len(keys) != len(source_ids):
            raise RuntimeError(
                f"{name}: expected {len(source_ids)} H5 trajectories, got {len(keys)}"
            )
        for key in keys:
            group = h5[key]
            arr = np.asarray(group["actions"], dtype=np.float64)
            actions.append(arr)
            steps.append(int(arr.shape[0]))
            if "success" in group and len(group["success"]) > 0:
                h5_success.append(bool(np.asarray(group["success"])[-1]))
            else:
                h5_success.append(False)

    json_success = [bool(ep.get("success", False)) for ep in episodes]
    if json_success != h5_success:
        raise RuntimeError(
            f"{name}: JSON/H5 success disagreement: {json_success} vs {h5_success}"
        )

    return {
        "h5_path": str(h5_path),
        "json_path": str(json_path),
        "success": json_success,
        "success_count": int(sum(json_success)),
        "success_rate": float(np.mean(json_success)),
        "steps": steps,
        "actions": actions,
        "source_episode_ids": source_ids,
    }


def _paired_action_delta(a: dict, b: dict) -> dict:
    all_l2: list[np.ndarray] = []
    all_rot_l2: list[np.ndarray] = []
    per_episode: list[dict] = []
    for idx, source_id in enumerate(a["source_episode_ids"]):
        xa = a["actions"][idx]
        xb = b["actions"][idx]
        n = min(len(xa), len(xb))
        if n == 0:
            full = np.array([], dtype=np.float64)
            rot = np.array([], dtype=np.float64)
        else:
            d = xa[:n] - xb[:n]
            full = np.linalg.norm(d, axis=1)
            rot = (
                np.linalg.norm(d[:, 3:6], axis=1)
                if d.shape[1] >= 6
                else np.array([], dtype=np.float64)
            )
        all_l2.append(full)
        all_rot_l2.append(rot)
        per_episode.append(
            {
                "source_episode_id": int(source_id),
                "steps_a": int(len(xa)),
                "steps_b": int(len(xb)),
                "paired_steps": int(n),
                "length_match": bool(len(xa) == len(xb)),
                "mean_action_l2": float(np.mean(full)) if full.size else None,
                "max_action_l2": float(np.max(full)) if full.size else None,
                "mean_rotation_action_l2": float(np.mean(rot)) if rot.size else None,
                "max_rotation_action_l2": float(np.max(rot)) if rot.size else None,
            }
        )

    full = np.concatenate([x for x in all_l2 if x.size]) if any(x.size for x in all_l2) else np.array([])
    rot = np.concatenate([x for x in all_rot_l2 if x.size]) if any(x.size for x in all_rot_l2) else np.array([])
    return {
        "paired_steps": int(full.size),
        "mean_action_l2": float(np.mean(full)) if full.size else None,
        "max_action_l2": float(np.max(full)) if full.size else None,
        "mean_rotation_action_l2": float(np.mean(rot)) if rot.size else None,
        "max_rotation_action_l2": float(np.max(rot)) if rot.size else None,
        "per_episode": per_episode,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--raw-json", type=Path, required=True)
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--identity-json", type=Path, required=True)
    args = p.parse_args()

    raw = json.loads(args.raw_json.read_text())
    raw_eps = raw.get("episodes", [])[: args.count]
    if len(raw_eps) != args.count:
        raise RuntimeError(f"raw metadata has only {len(raw_eps)} episodes")
    source_ids = [int(ep["episode_id"]) for ep in raw_eps]

    identity = json.loads(args.identity_json.read_text())
    variants = {name: _load_variant(args.root, name, source_ids) for name in VARIANTS}

    rates = {name: variants[name]["success_rate"] for name in VARIANTS}
    converter_effect_old_controller = rates["converter_only"] - rates["old_old"]
    converter_effect_fixed_controller = rates["combined"] - rates["controller_only"]
    interaction = converter_effect_fixed_controller - converter_effect_old_controller

    pairs = {
        "converter_effect_with_old_controller": _paired_action_delta(
            variants["old_old"], variants["converter_only"]
        ),
        "converter_effect_with_fixed_controller": _paired_action_delta(
            variants["controller_only"], variants["combined"]
        ),
        "controller_effect_with_old_converter": _paired_action_delta(
            variants["old_old"], variants["controller_only"]
        ),
        "controller_effect_with_fixed_converter": _paired_action_delta(
            variants["converter_only"], variants["combined"]
        ),
    }

    report_variants = {}
    for name, v in variants.items():
        report_variants[name] = {
            "commit": identity[name],
            "success_count": v["success_count"],
            "success_rate": v["success_rate"],
            "success_vector": v["success"],
            "source_episode_ids": v["source_episode_ids"],
            "steps": v["steps"],
            "h5_path": v["h5_path"],
        }

    report = {
        "schema_version": 1,
        "claim_boundary": (
            "Four-cell behavioral/action differential on the same official "
            "PegInsertionSide source episodes. Descriptive causal evidence for "
            "controller/converter interaction; not a learned-policy result and "
            "not a population success-rate estimate."
        ),
        "source_episode_count": args.count,
        "source_episode_ids": source_ids,
        "variants": report_variants,
        "success_interaction": {
            "converter_effect_old_controller": converter_effect_old_controller,
            "converter_effect_fixed_controller": converter_effect_fixed_controller,
            "difference_in_differences": interaction,
            "combined_ge_each_single": bool(
                rates["combined"] >= rates["controller_only"]
                and rates["combined"] >= rates["converter_only"]
            ),
        },
        "paired_action_differences": pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare baseline/fixed converted PegInsertionSide trajectories.

This script consumes two converted ManiSkill HDF5 trajectories generated from
the same raw demonstrations under the frozen baseline and PR #1495 fix.

It interprets both converted rotation actions exactly as PDEEPoseController
does: normalized action -> physical XYZ Euler delta -> SO(3).  The angular
distance between baseline and fixed therefore measures the controller-visible
representation change on real official demonstration steps.

It does not claim which trajectory is behaviorally superior; that remains the
purpose of the maintainer-requested Diffusion Policy experiment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def _iter_action_arrays(path: Path):
    with h5py.File(path, "r") as f:
        for key in sorted(f.keys()):
            if not key.startswith("traj_"):
                continue
            group = f[key]
            if "actions" not in group:
                continue
            actions = np.asarray(group["actions"])
            if actions.ndim != 2 or actions.shape[1] < 6:
                raise ValueError(f"{path}:{key}/actions has unexpected shape {actions.shape}")
            yield key, actions


def _xyz_matrix(euler: np.ndarray) -> np.ndarray:
    """Vectorized intrinsic/extrinsic XYZ convention matching PyTorch3D-style helper.

    For ManiSkill's controller, euler_angles_to_matrix(..., "XYZ") multiplies
    Rx @ Ry @ Rz.  This implementation mirrors that convention.
    """
    x, y, z = np.moveaxis(euler, -1, 0)
    cx, sx = np.cos(x), np.sin(x)
    cy, sy = np.cos(y), np.sin(y)
    cz, sz = np.cos(z), np.sin(z)

    out = np.empty(euler.shape[:-1] + (3, 3), dtype=np.float64)
    out[..., 0, 0] = cy * cz
    out[..., 0, 1] = -cy * sz
    out[..., 0, 2] = sy
    out[..., 1, 0] = sx * sy * cz + cx * sz
    out[..., 1, 1] = -sx * sy * sz + cx * cz
    out[..., 1, 2] = -sx * cy
    out[..., 2, 0] = -cx * sy * cz + sx * sz
    out[..., 2, 1] = cx * sy * sz + sx * cz
    out[..., 2, 2] = cx * cy
    return out


def _rotation_action_to_matrix(actions: np.ndarray) -> np.ndarray:
    # PDEEPoseControllerConfig uses [-2*pi, +2*pi] for each rotational action
    # dimension when normalized. inv_scale_action is affine, so the inverse is:
    # physical = low + (normalized + 1)/2 * (high-low) = normalized * 2*pi.
    euler = actions[:, 3:6].astype(np.float64) * (2.0 * np.pi)
    return _xyz_matrix(euler)


def _angular_distance_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    rel = np.swapaxes(a, -1, -2) @ b
    trace = np.trace(rel, axis1=-2, axis2=-1)
    cos_theta = np.clip((trace - 1.0) / 2.0, -1.0, 1.0)
    return np.degrees(np.arccos(cos_theta))


def _summary(values: np.ndarray) -> dict:
    if values.size == 0:
        return {}
    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p90": float(np.percentile(values, 90)),
        "p95": float(np.percentile(values, 95)),
        "p99": float(np.percentile(values, 99)),
        "max": float(np.max(values)),
        "fraction_gt_0_1_deg": float(np.mean(values > 0.1)),
        "fraction_gt_1_deg": float(np.mean(values > 1.0)),
        "fraction_gt_5_deg": float(np.mean(values > 5.0)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--fixed", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    baseline = dict(_iter_action_arrays(args.baseline))
    fixed = dict(_iter_action_arrays(args.fixed))
    if baseline.keys() != fixed.keys():
        raise SystemExit(
            f"trajectory sets differ: baseline={sorted(baseline)} fixed={sorted(fixed)}"
        )

    all_angles = []
    all_action_l2 = []
    per_traj = {}
    for key in baseline:
        a = baseline[key]
        b = fixed[key]
        if a.shape != b.shape:
            raise SystemExit(f"{key}: action shapes differ: {a.shape} vs {b.shape}")
        angle = _angular_distance_deg(
            _rotation_action_to_matrix(a),
            _rotation_action_to_matrix(b),
        )
        l2 = np.linalg.norm(a[:, 3:6] - b[:, 3:6], axis=1)
        all_angles.append(angle)
        all_action_l2.append(l2)
        per_traj[key] = {
            "steps": int(len(angle)),
            "rotation_disagreement_deg": _summary(angle),
            "normalized_rotation_action_l2": _summary(l2),
        }

    angles = np.concatenate(all_angles) if all_angles else np.array([])
    l2s = np.concatenate(all_action_l2) if all_action_l2 else np.array([])
    report = {
        "schema_version": 1,
        "claim_boundary": (
            "Controller-visible representation difference on paired official "
            "PegInsertionSide converted demonstrations; not a policy-success claim."
        ),
        "baseline_path": str(args.baseline),
        "fixed_path": str(args.fixed),
        "trajectory_count": len(per_traj),
        "total_steps": int(angles.size),
        "rotation_disagreement_deg": _summary(angles),
        "normalized_rotation_action_l2": _summary(l2s),
        "per_trajectory": per_traj,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

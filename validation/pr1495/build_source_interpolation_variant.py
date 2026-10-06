#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


HELPER = r"""

SEMREPAIR_INTERPOLATION_ALPHA = {alpha}


def _semrepair_legacy_compact_axis_angle_from_quaternion(quat: np.ndarray) -> np.ndarray:
    theta, omega = quat2axangle(quat)
    if omega > np.pi:
        omega = omega - 2 * np.pi
    return omega * theta
"""


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--alpha", type=float, required=True)
    a=p.parse_args()
    if not 0.0 <= a.alpha <= 1.0:
        raise SystemExit("alpha must be in [0,1]")

    path=a.source/"mani_skill/trajectory/utils/actions/conversion.py"
    text=path.read_text(encoding="utf-8")

    if "from transforms3d.quaternions import quat2axangle" not in text:
        anchor="from tqdm.auto import tqdm\n"
        if anchor not in text:
            raise SystemExit("import anchor not found")
        text=text.replace(anchor, anchor+"from transforms3d.quaternions import quat2axangle\n", 1)

    marker="def delta_pose_to_pd_ee_delta(\n"
    if marker not in text:
        raise SystemExit("delta-pose function marker not found")
    if "SEMREPAIR_INTERPOLATION_ALPHA" not in text:
        text=text.replace(marker, HELPER.format(alpha=repr(a.alpha))+"\n"+marker, 1)

    old="""    desired_euler = inverse_delta_to_pd_ee_euler(delta_pose.q)\n    rotation_action, _ = _normalized_pd_ee_rotation_action(\n        controller, desired_euler\n    )\n    return np.r_[position_action, rotation_action]\n"""
    new="""    desired_euler = inverse_delta_to_pd_ee_euler(delta_pose.q)\n    repaired_rotation_action, _ = _normalized_pd_ee_rotation_action(\n        controller, desired_euler\n    )\n    legacy_axis_angle = _semrepair_legacy_compact_axis_angle_from_quaternion(\n        delta_pose.q\n    )\n    legacy_rotation_action = gym_utils.inv_scale_action(\n        legacy_axis_angle,\n        low[3:].cpu().numpy(),\n        high[3:].cpu().numpy(),\n    )\n    rotation_action = (\n        (1.0 - SEMREPAIR_INTERPOLATION_ALPHA) * legacy_rotation_action\n        + SEMREPAIR_INTERPOLATION_ALPHA * repaired_rotation_action\n    )\n    return np.r_[position_action, rotation_action]\n"""
    if old not in text:
        raise SystemExit("candidate rotation block not found; frozen source drifted")
    text=text.replace(old,new,1)
    path.write_text(text,encoding="utf-8")
    print(f"patched {path} alpha={a.alpha}")


if __name__=="__main__":
    main()

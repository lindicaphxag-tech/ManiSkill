from __future__ import annotations

import json
import numpy as np
from scipy.spatial.transform import Rotation

from robosuite.controllers.parts.arm.osc import OperationalSpaceController

from cst.robosuite_osc import OSCState, absolute_pose_to_delta_action


ROBOSUITE_COMMIT = "5ce6643f3092639d08f7b0f90ed1c6a84f50552c"


def controller_for_state(state: OSCState, mode: str):
    controller = object.__new__(OperationalSpaceController)
    controller.input_min = -np.ones(6)
    controller.input_max = np.ones(6)
    controller.output_min = np.array([-0.10, -0.10, -0.10, -0.30, -0.30, -0.30])
    controller.output_max = -controller.output_min
    controller.action_scale = None
    controller.action_output_transform = None
    controller.action_input_transform = None

    controller.input_ref_frame = "world"
    controller.ref_pos = np.asarray(state.achieved_pos, dtype=float).copy()
    controller.ref_ori_mat = np.asarray(state.achieved_ori, dtype=float).copy()
    controller.goal_pos = np.asarray(state.desired_pos, dtype=float).copy()
    controller.goal_ori = np.asarray(state.desired_ori, dtype=float).copy()
    controller._goal_update_mode = mode
    controller.position_limits = None
    controller.orientation_limits = None
    return controller


def geodesic(a, b):
    relative = a.T @ b
    return float(
        np.arccos(np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0))
    )


def run(seed: int = 20261006, samples_per_mode: int = 500):
    rng = np.random.default_rng(seed)
    pos_errors = []
    rot_errors = []
    native_margins = []

    for mode in ("achieved", "desired"):
        for _ in range(samples_per_mode):
            achieved_pos = rng.uniform(-0.4, 0.4, 3)
            desired_pos = achieved_pos + rng.uniform(-0.04, 0.04, 3)
            achieved_ori = Rotation.from_rotvec(rng.uniform(-0.5, 0.5, 3)).as_matrix()
            desired_ori = (
                Rotation.from_rotvec(rng.uniform(-0.15, 0.15, 3)).as_matrix()
                @ achieved_ori
            )
            state = OSCState(
                achieved_pos=achieved_pos,
                achieved_ori=achieved_ori,
                desired_pos=desired_pos,
                desired_ori=desired_ori,
            )
            if mode == "achieved":
                base_pos, base_ori = achieved_pos, achieved_ori
            else:
                base_pos, base_ori = desired_pos, desired_ori

            target_pos = base_pos + rng.uniform(-0.07, 0.07, 3)
            target_ori = (
                Rotation.from_rotvec(rng.uniform(-0.20, 0.20, 3)).as_matrix()
                @ base_ori
            )
            absolute = np.concatenate(
                [target_pos, Rotation.from_matrix(target_ori).as_rotvec()]
            )

            controller = controller_for_state(state, mode)
            cert = absolute_pose_to_delta_action(
                absolute_action=absolute,
                state=state,
                goal_update_mode=mode,
                input_min=controller.input_min,
                input_max=controller.input_max,
                output_min=controller.output_min,
                output_max=controller.output_max,
            )
            if not cert.accepted:
                raise AssertionError(f"sample unexpectedly unrepresentable: {cert.reason}")

            physical = controller.scale_action(cert.native_delta_action.copy())
            reconstructed = controller.delta_to_abs_action(
                physical, goal_update_mode=mode
            )
            reconstructed_pos = reconstructed[:3]
            reconstructed_ori = Rotation.from_rotvec(reconstructed[3:]).as_matrix()

            pos_errors.append(float(np.linalg.norm(reconstructed_pos - target_pos)))
            rot_errors.append(geodesic(reconstructed_ori, target_ori))
            native_margins.append(cert.saturation_margin)

    result = {
        "robosuite_commit": ROBOSUITE_COMMIT,
        "seed": seed,
        "samples": 2 * samples_per_mode,
        "modes": ["achieved", "desired"],
        "max_position_residual": float(max(pos_errors)),
        "p99_position_residual": float(np.quantile(pos_errors, 0.99)),
        "max_orientation_residual_rad": float(max(rot_errors)),
        "p99_orientation_residual_rad": float(np.quantile(rot_errors, 0.99)),
        "min_native_saturation_margin": float(min(native_margins)),
    }
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["max_position_residual"] <= 1e-9
    assert result["max_orientation_residual_rad"] <= 1e-7
    assert result["min_native_saturation_margin"] > 0.0

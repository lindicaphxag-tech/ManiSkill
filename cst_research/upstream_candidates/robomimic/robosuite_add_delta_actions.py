"""Candidate upstream implementation for robomimic issue #270.

This mirrors robomimic/scripts/conversion/robosuite_add_absolute_actions.py but
converts absolute OSC pose actions back into policy-native delta actions.

This file is staged in the CST research branch because the connected GitHub
account does not yet have a robomimic fork.  It is intended to be transplanted
verbatim (modulo review feedback) once the fork exists.
"""

import argparse
import collections
import copy
import multiprocessing
import os
import pathlib
import pickle

import h5py
import numpy as np
import robosuite
from scipy.spatial.transform import Rotation
from tqdm import tqdm

import robomimic.utils.env_utils as EnvUtils
import robomimic.utils.file_utils as FileUtils
import robomimic.utils.obs_utils as ObsUtils
from robomimic.config import config_factory


def _inverse_scale_action(controller, physical_delta):
    """Inverse of robosuite Controller.scale_action with saturation evidence."""
    physical_delta = np.asarray(physical_delta, dtype=float)
    input_min = np.asarray(controller.input_min, dtype=float)
    input_max = np.asarray(controller.input_max, dtype=float)
    output_min = np.asarray(controller.output_min, dtype=float)
    output_max = np.asarray(controller.output_max, dtype=float)

    representable_mask = (physical_delta >= output_min) & (
        physical_delta <= output_max
    )
    clipped = np.clip(physical_delta, output_min, output_max)

    input_mid = (input_max + input_min) / 2.0
    output_mid = (output_max + output_min) / 2.0
    inverse_scale = (input_max - input_min) / (output_max - output_min)
    native = (clipped - output_mid) * inverse_scale + input_mid
    native = np.clip(native, input_min, input_max)
    return native, bool(np.all(representable_mask))


def _controller_achieved_pose(controller):
    """Return achieved OSC pose in the same chart as absolute controller input."""
    controller.update(force=True)

    # robosuite >= 1.5
    if hasattr(controller, "input_ref_frame"):
        if controller.input_ref_frame == "base":
            position = controller.world_to_origin_frame(controller.ref_pos)
            orientation = controller.goal_origin_to_eef_pose()[:3, :3]
        elif controller.input_ref_frame == "world":
            position = controller.ref_pos
            orientation = controller.ref_ori_mat
        else:
            raise ValueError(
                f"Unsupported OSC input_ref_frame: {controller.input_ref_frame}"
            )
    # robosuite <= 1.4.1
    else:
        position = controller.ee_pos
        orientation = controller.ee_ori_mat

    return np.asarray(position), np.asarray(orientation)


def _absolute_pose_to_delta(controller, absolute_pose):
    """Convert absolute [pos, rotvec] to policy-native OSC delta action."""
    absolute_pose = np.asarray(absolute_pose)
    if absolute_pose.shape != (6,):
        raise ValueError("absolute_pose must have shape (6,)")

    baseline_pos, baseline_ori = _controller_achieved_pose(controller)
    goal_pos = absolute_pose[:3]
    goal_ori = Rotation.from_rotvec(absolute_pose[3:6]).as_matrix()

    physical_pos_delta = goal_pos - baseline_pos

    # robosuite OSC composes: goal_ori = delta_ori @ baseline_ori
    # therefore: delta_ori = goal_ori @ baseline_ori.T
    delta_ori = goal_ori @ baseline_ori.T
    physical_ori_delta = Rotation.from_matrix(delta_ori).as_rotvec()

    physical_delta = np.concatenate(
        [physical_pos_delta, physical_ori_delta]
    )
    native_delta, representable = _inverse_scale_action(
        controller, physical_delta
    )
    return native_delta, representable, physical_delta


class RobomimicDeltaActionConverter:
    """Convert robomimic datasets with absolute OSC actions to delta actions."""

    def __init__(self, dataset_path, algo_name="bc"):
        config = config_factory(algo_name=algo_name)
        ObsUtils.initialize_obs_utils_with_config(config)

        env_meta = FileUtils.get_env_metadata_from_dataset(dataset_path)
        delta_env_meta = copy.deepcopy(env_meta)

        if robosuite.__version__ < "1.5":
            cfg = delta_env_meta["env_kwargs"]["controller_configs"]
            cfg["control_delta"] = True
        else:
            cfg = delta_env_meta["env_kwargs"]["controller_configs"]["body_parts"][
                "right"
            ]
            # Keep the same compatibility convention used by the existing
            # delta->absolute converter, and update input_type when present.
            cfg["control_delta"] = True
            if "input_type" in cfg:
                cfg["input_type"] = "delta"

        env = EnvUtils.create_env_from_metadata(
            env_meta=delta_env_meta,
            render=False,
            render_offscreen=False,
            use_image_obs=False,
        )
        assert len(env.env.robots) in (1, 2)

        for robot in env.env.robots:
            controller = (
                robot.controller
                if robosuite.__version__ < "1.5"
                else robot.part_controllers["right"]
            )
            if robosuite.__version__ < "1.5":
                assert controller.use_delta
            else:
                assert controller.input_type == "delta"
            if getattr(controller, "impedance_mode", "fixed") != "fixed":
                raise NotImplementedError(
                    "absolute->delta conversion currently supports fixed "
                    "impedance OSC only"
                )

        self.env = env
        self.file = h5py.File(dataset_path, "r")

    def get_demo_keys(self):
        return list(self.file["data"].keys())

    def convert_actions(self, states, actions, initial_state):
        env = self.env
        d_a = len(env.env.robots[0].action_limits[0])
        stacked_actions = actions.reshape(*actions.shape[:-1], -1, d_a)

        stacked_delta_actions = np.array(stacked_actions, copy=True)
        saturation_count = 0
        max_physical_excess = 0.0

        for i in range(len(states)):
            if i == 0:
                env.reset_to(initial_state)
            else:
                env.reset_to({"states": states[i]})

            for idx, robot in enumerate(env.env.robots):
                controller = (
                    robot.controller
                    if robosuite.__version__ < "1.5"
                    else robot.part_controllers["right"]
                )
                native_delta, representable, physical_delta = (
                    _absolute_pose_to_delta(
                        controller,
                        stacked_actions[i, idx, :6],
                    )
                )
                stacked_delta_actions[i, idx, :6] = native_delta

                if not representable:
                    saturation_count += 1
                    output_min = np.asarray(controller.output_min)
                    output_max = np.asarray(controller.output_max)
                    excess = np.maximum(
                        np.maximum(output_min - physical_delta, 0.0),
                        np.maximum(physical_delta - output_max, 0.0),
                    )
                    max_physical_excess = max(
                        max_physical_excess, float(np.max(excess))
                    )

                # stacked_actions[..., 6:] is intentionally untouched so
                # gripper / mobile-base remainder keeps its dataset semantics.

        delta_actions = stacked_delta_actions.reshape(actions.shape)
        info = {
            "saturation_count": saturation_count,
            "max_physical_excess": max_physical_excess,
        }
        return delta_actions, info

    def convert_demo(self, demo_key):
        demo = self.file[f"data/{demo_key}"]
        states = demo["states"][:]
        actions = demo["actions"][:]
        initial_state = dict(states=states[0])
        initial_state["model"] = demo.attrs["model_file"]
        initial_state["ep_meta"] = demo.attrs.get("ep_meta", None)
        return self.convert_actions(
            states,
            actions,
            initial_state=initial_state,
        )


def worker(x):
    path, demo_key = x
    converter = RobomimicDeltaActionConverter(path)
    delta_actions, info = converter.convert_demo(demo_key)
    return delta_actions, info


def add_delta_actions_to_dataset(dataset, num_workers):
    dataset = pathlib.Path(dataset).expanduser()
    assert dataset.is_file()

    converter = RobomimicDeltaActionConverter(dataset)
    demo_keys = converter.get_demo_keys()
    del converter

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(
            worker,
            [(dataset, demo_key) for demo_key in demo_keys],
        )

    total_saturation = 0
    max_physical_excess = 0.0
    with h5py.File(dataset, "r+") as out_file:
        for i in tqdm(range(len(results)), desc="Writing to output"):
            delta_actions, info = results[i]
            demo = out_file[f"data/{demo_keys[i]}"]
            if "actions_delta" not in demo:
                demo.create_dataset(
                    "actions_delta",
                    data=np.asarray(delta_actions),
                )
            else:
                demo["actions_delta"][:] = delta_actions

            total_saturation += info["saturation_count"]
            max_physical_excess = max(
                max_physical_excess,
                info["max_physical_excess"],
            )

    if total_saturation:
        print(
            "Warning: absolute->delta conversion saturated "
            f"{total_saturation} arm-step actions; max physical excess "
            f"was {max_physical_excess:.6g}. Replaying those steps cannot "
            "exactly reproduce the absolute goal under the configured "
            "delta-action limits."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--num_workers", type=int, default=10)
    args = parser.parse_args()

    add_delta_actions_to_dataset(
        dataset=args.dataset,
        num_workers=args.num_workers,
    )

"""Report ACTUAL native LIBERO controller action-history semantics, not VLA success.

This is a diagnostic read-only inspection of a real freshly reset MuJoCo
robot/controller. It NEVER certifies target-history survival or injects ACK
faults; it is designed to falsify unsupported cross-simulator ABI claims.
"""
from __future__ import annotations

import argparse
import ast
import textwrap
import hashlib
import inspect
import json
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path


def pkg_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return "not_installed"


def _source_goal_reference(controller):
    """Classify native source semantics, fail closed if no exact AST witness.

    This inspect confirms the Python controller formula actually loaded during
    the real MuJoCo reset; it does not prove every discrete transport scenario.
    """
    try:
        src = textwrap.dedent(inspect.getsource(type(controller).set_goal))
    except (OSError, AttributeError, TypeError):
        return {"source_goal_relative_to_achieved_ee_pose": False,
                "source_goal_relative_to_previous_desired_target": False,
                "source_semantics_verified": False, "ast_witness": "no_source"}
    tree = ast.parse(src)
    def attr(n, v, prop):
        return (isinstance(n, ast.Attribute) and n.attr == prop
                and isinstance(n.value, ast.Name) and n.value.id == v)
    seen_achieved=False
    seen_target=False
    for n in ast.walk(tree):
        if not isinstance(n,ast.Assign) or not any(attr(t,"self","goal_pos") for t in n.targets):
            continue
        call=n.value
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name):
            continue
        if call.func.id!="set_goal_position" or len(call.args)<2:
            continue
        seen_achieved |= attr(call.args[1],"self","ee_pos")
        seen_target |= attr(call.args[1],"self","goal_pos")
    if seen_target and seen_achieved:
        raise RuntimeError("Ambiguous native controller source has both target and achieved frames")
    return {
        "source_goal_relative_to_achieved_ee_pose": bool(seen_achieved),
        "source_goal_relative_to_previous_desired_target": bool(seen_target),
        "source_semantics_verified": bool(seen_achieved or seen_target),
        "ast_witness": (
            "self.goal_pos = set_goal_position(scaled_delta[:3], self.ee_pos, ...)"
            if seen_achieved else
            "self.goal_pos = set_goal_position(..., self.goal_pos, ...)"
            if seen_target else "unknown"),
    }


def _controller_fields(controller):
    source_path = inspect.getsourcefile(type(controller))
    sha = None
    if source_path and Path(source_path).is_file():
        sha = hashlib.sha256(Path(source_path).read_bytes()).hexdigest()
    def capture(name):
        value = getattr(controller, name, None)
        if value is None or type(value) in (str, bool, int, float):
            return value
        return repr(type(value).__name__)
    return {
        "class": type(controller).__module__ + "." + type(controller).__qualname__,
        "file_sha256": sha,
        "input_type": capture("input_type"),
        "use_delta": capture("use_delta"),
        "goal_update_mode": capture("_goal_update_mode"),
        "goal_pos_initialized": getattr(controller, "goal_pos", None) is not None,
        "goal_ori_initialized": getattr(controller, "goal_ori", None) is not None,
        "has_set_goal": callable(getattr(controller, "set_goal", None)),
        **_source_goal_reference(controller),
    }


def _walk(controller):
    results = [{"label": "robot_controller", **_controller_fields(controller)}]
    for field in ("part_controllers", "controllers"):
        children = getattr(controller, field, None)
        if isinstance(children, dict):
            for key, obj in sorted(children.items(), key=lambda pair: str(pair[0])):
                results.append({"label": field + "/" + str(key), **_controller_fields(obj)})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    from lerobot.envs.libero import LiberoEnv, _get_suite
    suite = _get_suite("libero_spatial")
    env = LiberoEnv(
        task_suite=suite,
        task_id=0,
        task_suite_name="libero_spatial",
        init_states=True,
        hard_reset=True,
        control_mode="relative",
        obs_type="pixels_agent_pos",
        observation_height=256,
        observation_width=256,
        num_steps_wait=10,
    )
    try:
        observation, _ = env.reset(seed=1180001)
        if not isinstance(observation, dict) or env._env is None:
            raise RuntimeError("Real native LIBERO reset did not produce observations")
        real_robot = env._env.robots[0]
        controller = real_robot.controller
        nodes = _walk(controller)
        modes = {node["goal_update_mode"] for node in nodes}
        native_achieved = any(n["source_goal_relative_to_achieved_ee_pose"] for n in nodes)
        native_desired = any(n["source_goal_relative_to_previous_desired_target"] for n in nodes)
        if native_achieved and native_desired:
            raise RuntimeError("Conflicting native reference semantics in active controller")
        recorded = {
            "result": "READ_ONLY_NATIVE_CONTROLLER_ABI_INSPECTION",
            "task": "libero_spatial/0",
            "native_fixed_init_reset_completed": True,
            "robot_class": type(real_robot).__module__ + "." + type(real_robot).__qualname__,
            "controllers": nodes,
            "hf_libero_version": pkg_version("hf-libero"),
            "robosuite_version": pkg_version("robosuite"),
            "mujoco_version": pkg_version("mujoco"),
            "has_desired_history_update_mode": "desired" in modes,
            "source_ast_achieved_pose_relative": native_achieved,
            "source_ast_previous_target_relative": native_desired,
            "has_achieved_history_update_mode": "achieved" in modes,
            "same_target_memory_fault_as_maniskill_proven": False,
            "multiple_unknown_ack_faults_physically_injected": False,
            "is_a_real_vla_task_success_test": False,
            "interpretation": (
                "POTENTIAL_DESIRED_TARGET_HISTORY_NEEDS_PHYSICAL_ACK_FAULT_VALIDATION"
                if native_desired or "desired" in modes else
                "ACHIEVED_FRAME_CANNOT_IMPORT_DESIRED_TARGET_BELIEF"
                if native_achieved or "achieved" in modes else
                "UNKNOWN_REQUIRES_CONTROLLER_SOURCE_AND_NATIVE_FAULT_STUDY"
            ),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(recorded, indent=2, sort_keys=True) + "\n")
        print("AUTHENTIC_LIBERO_CONTROLLER_HISTORY_DIAGNOSTIC", json.dumps(recorded, sort_keys=True))
    finally:
        env.close()


if __name__ == "__main__":
    main()

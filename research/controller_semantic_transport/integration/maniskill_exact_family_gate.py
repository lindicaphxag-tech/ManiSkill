from __future__ import annotations

import json
import numpy as np
import torch
import gymnasium as gym
import mani_skill.envs  # noqa: F401

from cst.core import transport_joint_position_action
from cst.maniskill_adapter import (
    chart_from_maniskill_joint_position_controller,
    state_from_maniskill_joint_position_controller,
)


def arm_controller(agent):
    controller = agent.controller
    if hasattr(controller, "controllers"):
        return controller.controllers["arm"]
    return controller


def run(seed: int = 20261006, samples: int = 64) -> dict:
    env = gym.make(
        "PickCube-v1",
        obs_mode="state",
        control_mode="pd_joint_delta_pos",
        sim_backend="cpu",
        render_mode=None,
        render_backend="cpu",
    )
    try:
        env.reset(seed=seed)
        base = env.unwrapped
        agent = base.agent
        rng = np.random.default_rng(seed)

        residuals = []
        source_contract_residuals = []
        accepted = 0

        for _ in range(samples):
            agent.set_control_mode("pd_joint_delta_pos")
            agent.controller.reset()
            source_arm = arm_controller(agent)
            source_chart = chart_from_maniskill_joint_position_controller(source_arm)
            source_state = state_from_maniskill_joint_position_controller(source_arm)

            dof = source_chart.dof
            source_action = rng.uniform(-0.5, 0.5, size=dof)
            cst_source_goal = source_chart.decode(
                source_action, state=source_state
            ).qpos

            source_arm.set_action(
                torch.as_tensor(source_action, dtype=torch.float32, device=base.device)[None]
            )
            production_source_goal = (
                source_arm._target_qpos.detach().cpu().numpy()[0].copy()
            )
            source_contract_residuals.append(
                float(np.linalg.norm(production_source_goal - cst_source_goal))
            )

            agent.set_control_mode("pd_joint_pos")
            agent.controller.reset()
            target_arm = arm_controller(agent)
            target_chart = chart_from_maniskill_joint_position_controller(target_arm)
            target_state = state_from_maniskill_joint_position_controller(target_arm)

            cert = transport_joint_position_action(
                source_chart=source_chart,
                source_state=source_state,
                source_action=source_action,
                target_chart=target_chart,
                target_state=target_state,
                semantic_tolerance=1e-6,
            )
            if not cert.accepted:
                continue
            accepted += 1

            target_arm.set_action(
                torch.as_tensor(cert.target_action, dtype=torch.float32, device=base.device)[None]
            )
            production_target_goal = (
                target_arm._target_qpos.detach().cpu().numpy()[0].copy()
            )
            residuals.append(
                float(np.linalg.norm(production_target_goal - production_source_goal))
            )

        result = {
            "seed": seed,
            "samples": samples,
            "accepted": accepted,
            "coverage": accepted / samples,
            "source_contract_max_residual": float(max(source_contract_residuals)),
            "target_transport_max_residual": float(max(residuals)) if residuals else None,
            "target_transport_p99_residual": float(np.quantile(residuals, 0.99)) if residuals else None,
        }
        return result
    finally:
        env.close()


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["accepted"] > 0
    assert result["source_contract_max_residual"] <= 1e-6
    assert result["target_transport_max_residual"] <= 1e-6

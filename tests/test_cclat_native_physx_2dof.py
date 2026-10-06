import numpy as np
import sapien
import sapien.physx as physx
import torch

from cst_validation.closed_loop_transport import (
    LinearClosedLoopModel,
    synthesize_closed_loop_transport,
)
from mani_skill.agents.controllers import (
    PDJointPosController,
    PDJointPosControllerConfig,
)
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.envs.utils.system.backend import parse_sim_and_render_backend


class _NativeTwoJointPlant:
    def __init__(self, *, stiffness, damping):
        backend = parse_sim_and_render_backend("cpu", "none")
        px = physx.PhysxCpuSystem()
        px.timestep = 1.0 / 100.0
        raw_scene = sapien.Scene(systems=[px])
        self.scene = ManiSkillScene(
            [raw_scene],
            device=torch.device("cpu"),
            backend=backend,
        )

        builder = self.scene.create_articulation_builder()
        root = builder.create_link_builder(None)
        root.set_name("root")

        link1 = builder.create_link_builder(root)
        link1.set_name("link1")
        link1.add_box_collision(half_size=[0.025, 0.025, 0.08])
        link1.set_joint_name("joint0")
        link1.set_joint_properties(
            type="revolute",
            limits=[[-1.5, 1.5]],
            pose_in_parent=sapien.Pose(),
            pose_in_child=sapien.Pose(),
            friction=0.0,
            damping=0.0,
        )

        link2 = builder.create_link_builder(link1)
        link2.set_name("link2")
        link2.add_box_collision(half_size=[0.02, 0.02, 0.06])
        link2.set_joint_name("joint1")
        link2.set_joint_properties(
            type="revolute",
            limits=[[-1.5, 1.5]],
            pose_in_parent=sapien.Pose(p=[0.0, 0.0, 0.10]),
            pose_in_child=sapien.Pose(),
            friction=0.0,
            damping=0.0,
        )

        self.articulation = builder.build(name="cclat_2dof", fix_root_link=True)

        cfg = PDJointPosControllerConfig(
            ["joint0", "joint1"],
            lower=None,
            upper=None,
            stiffness=stiffness,
            damping=damping,
            force_limit=[1000.0, 1000.0],
            use_delta=False,
            use_target=False,
            normalize_action=False,
        )
        self.controller = PDJointPosController(
            config=cfg,
            articulation=self.articulation,
            scene=self.scene,
            control_freq=20,
            sim_freq=100,
        )
        self.controller.set_drive_property()

    def transition(self, state: np.ndarray, target_qpos: np.ndarray) -> np.ndarray:
        state = np.asarray(state, dtype=np.float64)
        target_qpos = np.asarray(target_qpos, dtype=np.float64)
        assert state.shape == (4,)
        assert target_qpos.shape == (2,)

        self.articulation.set_qpos(
            torch.as_tensor(state[:2][None, :], dtype=torch.float32)
        )
        self.articulation.set_qvel(
            torch.as_tensor(state[2:][None, :], dtype=torch.float32)
        )
        self.controller.reset()
        self.controller.set_action(
            torch.as_tensor(target_qpos[None, :], dtype=torch.float32)
        )
        for _ in range(5):
            self.controller.before_simulation_step()
            self.scene.step()

        q = self.articulation.get_qpos().cpu().numpy()[0]
        v = self.articulation.get_qvel().cpu().numpy()[0]
        return np.concatenate([q, v]).astype(np.float64)


def _linearize(plant: _NativeTwoJointPlant, *, eps_x=1e-3, eps_u=1e-3):
    x0 = np.zeros(4, dtype=np.float64)
    u0 = np.zeros(2, dtype=np.float64)
    A = np.zeros((4, 4), dtype=np.float64)
    B = np.zeros((4, 2), dtype=np.float64)

    for j in range(4):
        d = np.zeros(4, dtype=np.float64)
        d[j] = eps_x
        A[:, j] = (
            plant.transition(x0 + d, u0)
            - plant.transition(x0 - d, u0)
        ) / (2.0 * eps_x)

    for j in range(2):
        d = np.zeros(2, dtype=np.float64)
        d[j] = eps_u
        B[:, j] = (
            plant.transition(x0, u0 + d)
            - plant.transition(x0, u0 - d)
        ) / (2.0 * eps_u)

    return LinearClosedLoopModel(A=A, B=B)


def test_native_2dof_cclat_improves_heldout_controller_swap():
    source = _NativeTwoJointPlant(
        stiffness=[100.0, 80.0],
        damping=[10.0, 8.0],
    )
    target = _NativeTwoJointPlant(
        stiffness=[60.0, 120.0],
        damping=[6.0, 12.0],
    )

    source_model = _linearize(source)
    target_model = _linearize(target)
    cert = synthesize_closed_loop_transport(source_model, target_model)

    heldout = [
        (np.array([0.030, -0.020, 0.050, -0.040]), np.array([0.045, -0.010])),
        (np.array([-0.040, 0.025, 0.080, 0.030]), np.array([-0.020, 0.050])),
        (np.array([0.050, 0.035, -0.100, 0.060]), np.array([0.010, -0.040])),
        (np.array([-0.025, -0.045, -0.070, -0.020]), np.array([0.035, 0.020])),
        (np.array([0.015, -0.030, 0.120, 0.050]), np.array([-0.030, 0.040])),
        (np.array([-0.055, 0.040, 0.020, -0.090]), np.array([0.050, -0.025])),
    ]

    naive_errors = []
    transported_errors = []
    for state, source_action in heldout:
        source_next = source.transition(state, source_action)
        naive_next = target.transition(state, source_action)
        target_action = cert.state_gain @ state + cert.action_gain @ source_action
        transported_next = target.transition(state, target_action)
        naive_errors.append(float(np.linalg.norm(naive_next - source_next)))
        transported_errors.append(float(np.linalg.norm(transported_next - source_next)))

    naive_errors = np.asarray(naive_errors)
    transported_errors = np.asarray(transported_errors)
    improved = transported_errors < naive_errors

    print(
        "CCLAT_2DOF_METRICS",
        {
            "naive_errors": naive_errors.tolist(),
            "transported_errors": transported_errors.tolist(),
            "mean_naive_error": float(np.mean(naive_errors)),
            "mean_transported_error": float(np.mean(transported_errors)),
            "mean_error_ratio": float(np.mean(transported_errors) / np.mean(naive_errors)),
            "num_improved": int(np.sum(improved)),
            "exact_linear_certificate": bool(cert.exact),
            "unavoidable_operator_residual": float(cert.unavoidable_operator_residual),
            "target_effect_rank": int(cert.target_effect_rank),
            "state_gain": cert.state_gain.tolist(),
            "action_gain": cert.action_gain.tolist(),
        },
    )

    # Frozen before seeing the run: improvement must generalize to at least
    # five of six held-out points and halve the mean next-state error.
    assert int(np.sum(improved)) >= 5
    assert float(np.mean(transported_errors)) < 0.5 * float(np.mean(naive_errors))

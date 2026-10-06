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


class _NativeOneJointPlant:
    def __init__(self, *, stiffness: float, damping: float):
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
        child = builder.create_link_builder(root)
        child.set_name("joint_link")
        # Symmetric geometry centered at the revolute joint keeps gravity from
        # introducing an off-axis moment in this local controller assay.
        child.add_box_collision(half_size=[0.02, 0.02, 0.08])
        child.set_joint_name("joint0")
        child.set_joint_properties(
            type="revolute",
            limits=[[-2.0, 2.0]],
            pose_in_parent=sapien.Pose(),
            pose_in_child=sapien.Pose(),
            friction=0.0,
            damping=0.0,
        )
        self.articulation = builder.build(name="cclat_arm", fix_root_link=True)

        cfg = PDJointPosControllerConfig(
            ["joint0"],
            lower=None,
            upper=None,
            stiffness=stiffness,
            damping=damping,
            force_limit=1000.0,
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

    def transition(self, state: np.ndarray, target_qpos: float) -> np.ndarray:
        state = np.asarray(state, dtype=np.float64)
        assert state.shape == (2,)
        self.articulation.set_qpos(
            torch.tensor([[state[0]]], dtype=torch.float32)
        )
        self.articulation.set_qvel(
            torch.tensor([[state[1]]], dtype=torch.float32)
        )
        self.controller.reset()
        self.controller.set_action(
            torch.tensor([[target_qpos]], dtype=torch.float32)
        )
        for _ in range(5):
            self.controller.before_simulation_step()
            self.scene.step()
        return np.array(
            [
                float(self.articulation.get_qpos().cpu().numpy()[0, 0]),
                float(self.articulation.get_qvel().cpu().numpy()[0, 0]),
            ],
            dtype=np.float64,
        )


def _linearize(plant: _NativeOneJointPlant, *, eps_x=1e-3, eps_u=1e-3):
    x0 = np.zeros(2, dtype=np.float64)
    u0 = 0.0
    A = np.zeros((2, 2), dtype=np.float64)
    for j in range(2):
        d = np.zeros(2, dtype=np.float64)
        d[j] = eps_x
        A[:, j] = (
            plant.transition(x0 + d, u0)
            - plant.transition(x0 - d, u0)
        ) / (2.0 * eps_x)
    B = (
        plant.transition(x0, u0 + eps_u)
        - plant.transition(x0, u0 - eps_u)
    )[:, None] / (2.0 * eps_u)
    return LinearClosedLoopModel(A=A, B=B)


def test_native_physx_cclat_improves_heldout_controller_swap():
    """Held-out PhysX transitions improve after local closed-loop transport.

    Source and target are the same one-joint plant with deliberately different
    PD gains.  The adapter is synthesized only from local finite differences at
    the origin.  Evaluation points below are not used in model fitting.
    """
    source_plant = _NativeOneJointPlant(stiffness=100.0, damping=10.0)
    target_plant = _NativeOneJointPlant(stiffness=60.0, damping=6.0)

    source_model = _linearize(source_plant)
    target_model = _linearize(target_plant)
    cert = synthesize_closed_loop_transport(source_model, target_model)

    heldout = [
        (np.array([0.030, 0.060]), 0.045),
        (np.array([-0.040, 0.080]), -0.020),
        (np.array([0.050, -0.100]), 0.010),
        (np.array([-0.025, -0.070]), 0.035),
        (np.array([0.015, 0.120]), -0.030),
        (np.array([-0.055, 0.020]), 0.050),
    ]

    naive_errors = []
    transported_errors = []
    for state, source_action in heldout:
        source_next = source_plant.transition(state, source_action)
        naive_next = target_plant.transition(state, source_action)

        target_action = float(
            (cert.state_gain @ state + cert.action_gain @ np.array([source_action]))[0]
        )
        transported_next = target_plant.transition(state, target_action)

        naive_errors.append(float(np.linalg.norm(naive_next - source_next)))
        transported_errors.append(
            float(np.linalg.norm(transported_next - source_next))
        )

    naive_errors = np.asarray(naive_errors)
    transported_errors = np.asarray(transported_errors)

    # This is a frozen comparative criterion, not threshold tuning: the method
    # must improve every held-out point and reduce mean next-state error by at
    # least 2x relative to copying the source action unchanged.
    assert np.all(transported_errors < naive_errors)
    assert float(np.mean(transported_errors)) < 0.5 * float(np.mean(naive_errors))


def test_native_physx_identical_controller_models_are_exactly_transportable():
    source_plant = _NativeOneJointPlant(stiffness=80.0, damping=8.0)
    target_plant = _NativeOneJointPlant(stiffness=80.0, damping=8.0)

    source_model = _linearize(source_plant)
    target_model = _linearize(target_plant)
    cert = synthesize_closed_loop_transport(source_model, target_model)

    assert cert.exact
    np.testing.assert_allclose(cert.state_gain, 0.0, atol=2e-5)
    np.testing.assert_allclose(cert.action_gain, [[1.0]], atol=2e-4)

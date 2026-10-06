import numpy as np
import sapien
import sapien.physx as physx
import torch

from cst_validation.closed_loop_probe import certify_black_box_closed_loop_transport
from mani_skill.agents.controllers import PDJointPosController, PDJointPosControllerConfig
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.envs.utils.system.backend import parse_sim_and_render_backend


def _controller(*, use_delta: bool):
    backend = parse_sim_and_render_backend("cpu", "none")
    px = physx.PhysxCpuSystem()
    px.timestep = 1.0 / 100.0
    raw_scene = sapien.Scene(systems=[px])
    scene = ManiSkillScene([raw_scene], device=torch.device("cpu"), backend=backend)

    builder = scene.create_articulation_builder()
    root = builder.create_link_builder(None)
    root.set_name("root")
    child = builder.create_link_builder(root)
    child.set_name("joint_link")
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
    articulation = builder.build(name="test_arm", fix_root_link=True)
    articulation.set_qpos(torch.tensor([[0.2]], dtype=torch.float32))
    articulation.set_qvel(torch.zeros((1, 1), dtype=torch.float32))

    config = PDJointPosControllerConfig(
        ["joint0"],
        lower=(-0.1 if use_delta else None),
        upper=(0.1 if use_delta else None),
        stiffness=100.0,
        damping=10.0,
        force_limit=100.0,
        use_delta=use_delta,
        use_target=False,
        normalize_action=use_delta,
    )
    controller = PDJointPosController(
        config=config,
        articulation=articulation,
        scene=scene,
        control_freq=20,
        sim_freq=100,
    )
    controller.set_drive_property()
    controller.reset()
    return scene, articulation, controller


def _query_delta(action: np.ndarray) -> np.ndarray:
    scene, articulation, controller = _controller(use_delta=True)
    controller.set_action(torch.tensor([[float(action[0])]], dtype=torch.float32))
    for _ in range(5):
        controller.before_simulation_step()
        scene.step()
    return np.array(
        [
            float(articulation.get_qpos()[0, 0]),
            float(articulation.get_qvel()[0, 0]),
            float(controller._target_qpos[0, 0]),
        ],
        dtype=float,
    )


def _query_absolute(action: np.ndarray) -> np.ndarray:
    scene, articulation, controller = _controller(use_delta=False)
    controller.set_action(torch.tensor([[float(action[0])]], dtype=torch.float32))
    for _ in range(5):
        controller.before_simulation_step()
        scene.step()
    return np.array(
        [
            float(articulation.get_qpos()[0, 0]),
            float(articulation.get_qvel()[0, 0]),
            float(controller._target_qpos[0, 0]),
        ],
        dtype=float,
    )


def test_black_box_physx_probe_recovers_delta_to_absolute_transport():
    # The source action is normalized in [-1, 1] with a physical delta range
    # [-0.1, 0.1], so the executable adapter should be approximately
    # absolute_target = 0.2 + 0.1 * source_delta.
    cert = certify_black_box_closed_loop_transport(
        _query_delta,
        _query_absolute,
        source_action0=np.array([0.0]),
        target_action0=np.array([0.2]),
        source_epsilon=0.1,
        target_epsilon=0.01,
        heldout_source_deltas=np.array([[0.35], [-0.6], [0.8]]),
        heldout_tolerance=2e-4,
        max_scale_instability=0.05,
        local_atol=2e-4,
        local_rtol=1e-5,
    )

    assert cert.authorized, cert.reason
    assert cert.source_estimate.stable
    assert cert.target_estimate.stable
    assert cert.local_transport is not None
    assert cert.local_transport.exact
    assert cert.heldout is not None
    assert cert.heldout.accepted
    np.testing.assert_allclose(
        cert.local_transport.adapter,
        np.array([[0.1]]),
        atol=2e-3,
        rtol=2e-2,
    )

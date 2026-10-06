import numpy as np
import pytest
import sapien
import sapien.physx as physx
import torch

from mani_skill.agents.controllers import (
    PDJointPosController,
    PDJointPosControllerConfig,
)
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.envs.utils.system.backend import parse_sim_and_render_backend
from mani_skill.trajectory.utils.actions.conversion import (
    normalized_pd_joint_action_to_physical,
    qpos_to_pd_joint_pos,
)
from mani_skill.utils import gym_utils


def _native_one_joint_controller(*, use_delta: bool, use_target: bool = False):
    """Build a real ManiSkill PD controller on a headless PhysX articulation."""
    backend = parse_sim_and_render_backend("cpu", "none")
    px = physx.PhysxCpuSystem()
    px.timestep = 1.0 / 100.0
    raw_scene = sapien.Scene(systems=[px])
    scene = ManiSkillScene(
        [raw_scene],
        device=torch.device("cpu"),
        backend=backend,
    )

    builder = scene.create_articulation_builder()
    root = builder.create_link_builder(None)
    root.set_name("root")
    child = builder.create_link_builder(root)
    child.set_name("joint_link")
    # Collision-only geometry gives PhysX a physical inertia without requiring
    # any render device.
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
        use_target=use_target,
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


@pytest.mark.parametrize("source_native", [-0.75, -0.25, 0.5, 0.9])
def test_real_physx_delta_to_absolute_semantics_are_target_equivalent(source_native):
    """Patch semantics drive the same target and PhysX trajectory as source."""
    source_scene, source_art, source = _native_one_joint_controller(use_delta=True)
    target_scene, target_art, target = _native_one_joint_controller(use_delta=False)

    source_action = np.array([source_native], dtype=np.float64)

    # Concrete pre-patch failure boundary: trajectory conversion gets a NumPy
    # row, but the runtime helper is torch-only.
    with pytest.raises(TypeError):
        gym_utils.clip_and_scale_action(
            source_action,
            source.action_space_low,
            source.action_space_high,
        )

    physical_delta = normalized_pd_joint_action_to_physical(
        source, source_action
    )
    desired_target = source.qpos.detach().cpu().numpy()[0] + physical_delta
    target_native = qpos_to_pd_joint_pos(target, desired_target)

    source.set_action(torch.tensor([[source_native]], dtype=torch.float32))
    target.set_action(torch.tensor([target_native], dtype=torch.float32))

    np.testing.assert_allclose(
        source._target_qpos.detach().cpu().numpy(),
        target._target_qpos.detach().cpu().numpy(),
        atol=1e-7,
        rtol=1e-7,
    )
    np.testing.assert_allclose(
        source._target_qpos.detach().cpu().numpy()[0],
        desired_target,
        atol=1e-7,
        rtol=1e-7,
    )

    # Execute the same real PD target through independent PhysX scenes.
    for _ in range(5):
        source.before_simulation_step()
        target.before_simulation_step()
        source_scene.step()
        target_scene.step()

    np.testing.assert_allclose(
        source_art.get_qpos().detach().cpu().numpy(),
        target_art.get_qpos().detach().cpu().numpy(),
        atol=1e-6,
        rtol=1e-6,
    )
    np.testing.assert_allclose(
        source_art.get_qvel().detach().cpu().numpy(),
        target_art.get_qvel().detach().cpu().numpy(),
        atol=1e-6,
        rtol=1e-6,
    )



def test_real_physx_target_delta_requires_hidden_controller_state():
    """State-aware transport preserves a target-delta controller trajectory.

    A target-delta action is relative to the controller-owned previous target,
    not the measured current qpos. Because finite-stiffness tracking lags the
    target, a stateless current-qpos conversion becomes wrong after the first
    step. CST uses the hidden target state and stays physically equivalent.
    """
    source_scene, source_art, source = _native_one_joint_controller(
        use_delta=True,
        use_target=True,
    )
    target_scene, target_art, target = _native_one_joint_controller(
        use_delta=False,
    )

    sequence = [0.8, 0.6, -0.4, 0.7, -0.3]
    max_naive_target_error = 0.0

    for step, native in enumerate(sequence):
        source_hidden_target = source._target_qpos.detach().cpu().numpy()[0].copy()
        source_current = source.qpos.detach().cpu().numpy()[0].copy()
        physical_delta = normalized_pd_joint_action_to_physical(
            source,
            np.array([native], dtype=np.float64),
        )
        correct_target = source_hidden_target + physical_delta
        naive_current_relative_target = source_current + physical_delta
        max_naive_target_error = max(
            max_naive_target_error,
            float(np.max(np.abs(correct_target - naive_current_relative_target))),
        )

        target_native = qpos_to_pd_joint_pos(target, correct_target)
        source.set_action(torch.tensor([[native]], dtype=torch.float32))
        target.set_action(
            torch.as_tensor(
                np.asarray(target_native, dtype=np.float32)[None, :],
                dtype=torch.float32,
            )
        )

        np.testing.assert_allclose(
            source._target_qpos.detach().cpu().numpy(),
            target._target_qpos.detach().cpu().numpy(),
            atol=1e-7,
            rtol=1e-7,
        )

        for _ in range(5):
            source.before_simulation_step()
            target.before_simulation_step()
            source_scene.step()
            target_scene.step()

        np.testing.assert_allclose(
            source_art.get_qpos().detach().cpu().numpy(),
            target_art.get_qpos().detach().cpu().numpy(),
            atol=1e-6,
            rtol=1e-6,
        )
        np.testing.assert_allclose(
            source_art.get_qvel().detach().cpu().numpy(),
            target_art.get_qvel().detach().cpu().numpy(),
            atol=1e-6,
            rtol=1e-6,
        )

        if step > 0:
            # The hidden target and measured qpos should differ under finite
            # stiffness, making the stateless interpretation observably wrong.
            assert np.max(np.abs(source_hidden_target - source_current)) > 1e-5

    assert max_naive_target_error > 1e-4

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


class _TwoJointRolloutPlant:
    def __init__(self, *, stiffness, damping):
        backend = parse_sim_and_render_backend("cpu", "none")
        px = physx.PhysxCpuSystem()
        px.timestep = 1.0 / 100.0
        raw_scene = sapien.Scene(systems=[px])
        self.scene = ManiSkillScene([raw_scene], device=torch.device("cpu"), backend=backend)

        builder = self.scene.create_articulation_builder()
        root = builder.create_link_builder(None)
        root.set_name("root")
        link1 = builder.create_link_builder(root)
        link1.set_name("link1")
        link1.add_box_collision(half_size=[0.025, 0.025, 0.08])
        link1.set_joint_name("joint0")
        link1.set_joint_properties(
            type="revolute", limits=[[-1.5, 1.5]],
            pose_in_parent=sapien.Pose(), pose_in_child=sapien.Pose(),
            friction=0.0, damping=0.0,
        )
        link2 = builder.create_link_builder(link1)
        link2.set_name("link2")
        link2.add_box_collision(half_size=[0.02, 0.02, 0.06])
        link2.set_joint_name("joint1")
        link2.set_joint_properties(
            type="revolute", limits=[[-1.5, 1.5]],
            pose_in_parent=sapien.Pose(p=[0.0, 0.0, 0.10]),
            pose_in_child=sapien.Pose(),
            friction=0.0, damping=0.0,
        )
        self.articulation = builder.build(name="cclat_rollout_2dof", fix_root_link=True)

        cfg = PDJointPosControllerConfig(
            ["joint0", "joint1"], lower=None, upper=None,
            stiffness=stiffness, damping=damping,
            force_limit=[1000.0, 1000.0],
            use_delta=False, use_target=False, normalize_action=False,
        )
        self.controller = PDJointPosController(
            config=cfg, articulation=self.articulation, scene=self.scene,
            control_freq=20, sim_freq=100,
        )
        self.controller.set_drive_property()

    def reset_state(self, state):
        state=np.asarray(state,dtype=np.float64)
        self.articulation.set_qpos(torch.as_tensor(state[:2][None,:],dtype=torch.float32))
        self.articulation.set_qvel(torch.as_tensor(state[2:][None,:],dtype=torch.float32))
        self.controller.reset()

    def state(self):
        q=self.articulation.get_qpos().cpu().numpy()[0]
        v=self.articulation.get_qvel().cpu().numpy()[0]
        return np.concatenate([q,v]).astype(np.float64)

    def step(self, action):
        action=np.asarray(action,dtype=np.float64)
        self.controller.set_action(torch.as_tensor(action[None,:],dtype=torch.float32))
        for _ in range(5):
            self.controller.before_simulation_step()
            self.scene.step()
        return self.state()

    def transition(self,state,action):
        self.reset_state(state)
        return self.step(action)


def _linearize(plant, eps_x=1e-3, eps_u=1e-3):
    x0=np.zeros(4,dtype=np.float64)
    u0=np.zeros(2,dtype=np.float64)
    A=np.zeros((4,4),dtype=np.float64)
    B=np.zeros((4,2),dtype=np.float64)
    for j in range(4):
        d=np.zeros(4); d[j]=eps_x
        A[:,j]=(plant.transition(x0+d,u0)-plant.transition(x0-d,u0))/(2*eps_x)
    for j in range(2):
        d=np.zeros(2); d[j]=eps_u
        B[:,j]=(plant.transition(x0,u0+d)-plant.transition(x0,u0-d))/(2*eps_u)
    return LinearClosedLoopModel(A=A,B=B)


def _frozen_policy(state):
    q=np.asarray(state[:2])
    v=np.asarray(state[2:])
    cross=np.array([0.08*q[1], -0.06*q[0]])
    target=-0.45*q-0.06*v+cross
    return np.clip(target,-0.12,0.12)


def test_cclat_preserves_frozen_policy_rollout_better_than_naive_controller_swap():
    source=_TwoJointRolloutPlant(stiffness=[100.0,80.0],damping=[10.0,8.0])
    target_model_plant=_TwoJointRolloutPlant(stiffness=[60.0,120.0],damping=[6.0,12.0])
    source_model=_linearize(source)
    target_model=_linearize(target_model_plant)
    cert=synthesize_closed_loop_transport(source_model,target_model)

    initial=np.array([0.06,-0.05,0.10,-0.08],dtype=np.float64)

    ref=_TwoJointRolloutPlant(stiffness=[100.0,80.0],damping=[10.0,8.0])
    naive=_TwoJointRolloutPlant(stiffness=[60.0,120.0],damping=[6.0,12.0])
    adapted=_TwoJointRolloutPlant(stiffness=[60.0,120.0],damping=[6.0,12.0])
    for p in (ref,naive,adapted):
        p.reset_state(initial)

    ref_trace=[ref.state()]
    naive_trace=[naive.state()]
    adapted_trace=[adapted.state()]

    for _ in range(30):
        x_ref=ref.state()
        x_naive=naive.state()
        x_adapted=adapted.state()

        u_ref=_frozen_policy(x_ref)
        u_naive=_frozen_policy(x_naive)
        u_policy_adapted=_frozen_policy(x_adapted)
        u_adapted=cert.state_gain@x_adapted+cert.action_gain@u_policy_adapted

        ref_trace.append(ref.step(u_ref))
        naive_trace.append(naive.step(u_naive))
        adapted_trace.append(adapted.step(u_adapted))

    ref_trace=np.asarray(ref_trace)
    naive_trace=np.asarray(naive_trace)
    adapted_trace=np.asarray(adapted_trace)

    naive_err=np.linalg.norm(naive_trace-ref_trace,axis=1)
    adapted_err=np.linalg.norm(adapted_trace-ref_trace,axis=1)

    metrics={
        "mean_naive_error":float(np.mean(naive_err[1:])),
        "mean_adapted_error":float(np.mean(adapted_err[1:])),
        "mean_error_ratio":float(np.mean(adapted_err[1:])/np.mean(naive_err[1:])),
        "terminal_naive_error":float(naive_err[-1]),
        "terminal_adapted_error":float(adapted_err[-1]),
        "terminal_error_ratio":float(adapted_err[-1]/naive_err[-1]),
        "max_naive_error":float(np.max(naive_err)),
        "max_adapted_error":float(np.max(adapted_err)),
        "exact_linear_certificate":bool(cert.exact),
        "unavoidable_operator_residual":float(cert.unavoidable_operator_residual),
    }
    print("CCLAT_POLICY_ROLLOUT_METRICS",metrics)

    # Frozen before seeing the run.
    assert metrics["mean_error_ratio"] < 0.5
    assert metrics["terminal_error_ratio"] < 0.5

import numpy as np
import sapien
import sapien.physx as physx
import torch

from mani_skill.agents.controllers import PDJointPosController, PDJointPosControllerConfig
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.envs.utils.system.backend import parse_sim_and_render_backend

from .closed_loop_transport import LinearClosedLoopModel


class NativeTwoJointPlant:
    def __init__(self, *, stiffness, damping):
        backend=parse_sim_and_render_backend("cpu","none")
        px=physx.PhysxCpuSystem()
        px.timestep=1.0/100.0
        raw_scene=sapien.Scene(systems=[px])
        self.scene=ManiSkillScene([raw_scene],device=torch.device("cpu"),backend=backend)

        builder=self.scene.create_articulation_builder()
        root=builder.create_link_builder(None); root.set_name("root")
        link1=builder.create_link_builder(root); link1.set_name("link1")
        link1.add_box_collision(half_size=[0.025,0.025,0.08])
        link1.set_joint_name("joint0")
        link1.set_joint_properties(
            type="revolute",limits=[[-1.5,1.5]],
            pose_in_parent=sapien.Pose(),pose_in_child=sapien.Pose(),
            friction=0.0,damping=0.0,
        )
        link2=builder.create_link_builder(link1); link2.set_name("link2")
        link2.add_box_collision(half_size=[0.02,0.02,0.06])
        link2.set_joint_name("joint1")
        link2.set_joint_properties(
            type="revolute",limits=[[-1.5,1.5]],
            pose_in_parent=sapien.Pose(p=[0.0,0.0,0.10]),pose_in_child=sapien.Pose(),
            friction=0.0,damping=0.0,
        )
        self.articulation=builder.build(name="cclat_gate_2dof",fix_root_link=True)

        cfg=PDJointPosControllerConfig(
            ["joint0","joint1"],lower=None,upper=None,
            stiffness=stiffness,damping=damping,force_limit=[1000.0,1000.0],
            use_delta=False,use_target=False,normalize_action=False,
        )
        self.controller=PDJointPosController(
            config=cfg,articulation=self.articulation,scene=self.scene,
            control_freq=20,sim_freq=100,
        )
        self.controller.set_drive_property()

    def reset_state(self,state):
        state=np.asarray(state,dtype=np.float64)
        self.articulation.set_qpos(torch.as_tensor(state[:2][None,:],dtype=torch.float32))
        self.articulation.set_qvel(torch.as_tensor(state[2:][None,:],dtype=torch.float32))
        self.controller.reset()

    def state(self):
        q=self.articulation.get_qpos().cpu().numpy()[0]
        v=self.articulation.get_qvel().cpu().numpy()[0]
        return np.concatenate([q,v]).astype(np.float64)

    def step(self,action):
        action=np.asarray(action,dtype=np.float64)
        self.controller.set_action(torch.as_tensor(action[None,:],dtype=torch.float32))
        for _ in range(5):
            self.controller.before_simulation_step()
            self.scene.step()
        return self.state()

    def transition(self,state,action):
        self.reset_state(state)
        return self.step(action)


def linearize(plant,eps_x=1e-3,eps_u=1e-3):
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


def frozen_policy(state):
    q=np.asarray(state[:2]); v=np.asarray(state[2:])
    cross=np.array([0.08*q[1],-0.06*q[0]])
    return np.clip(-0.45*q-0.06*v+cross,-0.12,0.12)

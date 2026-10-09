"""Typed VLA->hidden-controller-target interface; conditional setpoint bounds ONLY.

NEVER interpret vanilla SmolVLA base output as Panda EE delta: its action
representation, stats, frame, and gripper must be independently established
from a task-specific dataset and LeRobot postprocessor. This layer is not
a collision, trajectory, force, or real-robot safety system.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
import numpy as np
from scipy.spatial.transform import Rotation


class ContractViolation(ValueError):
    """Missing or inconsistent policy/action/controller provenance."""


@dataclass(frozen=True)
class ActionProvenance:
    model_id: str
    checkpoint_sha: str
    dataset_id: str
    normalization_sha: str
    action_representation: str
    action_frame: str
    rotation_rule: str
    linear_units: str
    angular_units: str
    pipeline: str
    task_specific_action_mapping_verified: bool

    def verify(self):
        def sha(x):
            return isinstance(x,str) and len(x)==40 and all(c in "0123456789abcdef" for c in x)
        if not self.model_id or not self.dataset_id or not sha(self.checkpoint_sha) or not sha(self.normalization_sha):
            raise ContractViolation("Missing pinned model and action stats provenance")
        verified=(
            self.action_representation=="ee_delta_xyz_rotvec_gripper"
            and self.action_frame=="root"
            and self.rotation_rule=="root_left_multiply"
            and self.linear_units=="meter"
            and self.angular_units=="radian"
            and self.pipeline=="lerobot_postprocessed_physical"
            and self.task_specific_action_mapping_verified is True
        )
        if not verified:
            raise ContractViolation("Unverified physical action ABI: model output is NOT a generic Panda EE delta")


@dataclass(frozen=True)
class VisualObservation:
    episode: str
    step: int
    achieved_position_m: tuple[float,float,float]
    achieved_quaternion_xyzw: tuple[float,float,float,float]

    def verify(self):
        p=np.asarray(self.achieved_position_m,dtype=float)
        q=np.asarray(self.achieved_quaternion_xyzw,dtype=float)
        if not self.episode or type(self.step) is not int or self.step<0:
            raise ContractViolation("Invalid episode or public-observation index")
        if p.shape!=(3,) or q.shape!=(4,) or not np.isfinite(p).all() or not np.isfinite(q).all():
            raise ContractViolation("Nonfinite or shape-invalid achieved end-effector pose")
        if abs(np.linalg.norm(q)-1)>1e-4:
            raise ContractViolation("Root-frame achieved orientation must be unit quaternion")


@dataclass(frozen=True)
class DispatchDecision:
    code: str  # SEND_CERTIFIED or QUERY_TARGET
    native_arm_command: tuple[float,...]|None
    source_gripper: float|None
    hypothesis_count: int
    worst_position_m: float|None
    worst_angle_rad: float|None
    reason: str
    ticket: Any=None


class RecedingHorizonVLAGateway:
    """One fresh VLA observation -> one bounded native command; no stale chunks.

    belief: existing `UncertainDeliveryBelief`, not achieved-pose memory.
    certifier: existing `common_multi_history_command`.
    pose_type: existing `TargetPose`.
    """

    def __init__(self, provenance:ActionProvenance, belief:Any,
                 certifier:Callable[...,Any], pose_type:Any,
                 *,pos_lower=(-.1,-.1,-.1),pos_upper=(.1,.1,.1),
                 rot_scale=(.2,.2,.2),max_pos_error_m=.05,max_rot_error_rad=.05):
        provenance.verify()
        self.provenance=provenance
        self.belief=belief
        self.certifier=certifier
        self.pose_type=pose_type
        self.low=tuple(pos_lower);self.high=tuple(pos_upper);self.rot_scale=tuple(rot_scale)
        self.pos_budget=float(max_pos_error_m);self.rot_budget=float(max_rot_error_rad)
        if not all(np.isfinite(v) for v in self.low+self.high+self.rot_scale):
            raise ContractViolation("Invalid controller translation/rotation chart")
        if not (0<self.pos_budget<=.5 and 0<self.rot_budget<=np.pi):
            raise ContractViolation("Invalid research tolerance budgets")
        self.last_episode=None;self.last_step=-1
        self.observation=None;self.action=None;self.pending=None

    def observe(self,obs:VisualObservation,physical_action_chunk:Any,
                *,model_checkpoint_sha:str,normalizer_sha:str):
        if self.pending is not None:
            raise ContractViolation("Native action pending acknowledgement")
        obs.verify()
        if (model_checkpoint_sha!=self.provenance.checkpoint_sha
                or normalizer_sha!=self.provenance.normalization_sha):
            raise ContractViolation("Output model/normalization SHA mismatch")
        if obs.episode==self.last_episode and obs.step<=self.last_step:
            raise ContractViolation("Replay/out-of-order visual observation")
        if self.last_episode is not None and obs.episode!=self.last_episode:
            raise ContractViolation("Reset controller target belief before new episode")
        a=np.asarray(physical_action_chunk,dtype=np.float64)
        if a.ndim!=2 or a.shape[1]!=7 or a.shape[0]<1:
            raise ContractViolation("Only task-verified postprocessed action chunk [T,7]")
        if not np.isfinite(a).all():
            raise ContractViolation("Nonfinite VLA physical action")
        if np.max(np.abs(a[:,:3]))>.2 or np.max(np.linalg.norm(a[:,3:6],axis=1))>np.pi:
            raise ContractViolation("Untrusted Cartesian action normalization/unit scale")
        if np.max(np.abs(a[:,6]))>1+1e-10:
            raise ContractViolation("No validated source gripper mapping")
        if not self.belief.valid or self.belief.pending is not None or not self.belief.hypotheses:
            raise ContractViolation("Invalid/incomplete commanded target belief")
        self.observation=obs;self.action=a[0].copy()
        self.last_episode=obs.episode;self.last_step=obs.step

    def decide(self, *,current_belief_trusted=True):
        if self.observation is None or self.action is None or self.pending is not None:
            raise ContractViolation("Requires unused VLA action from fresh public observation")
        a=self.action;obs=self.observation
        target_orientation=Rotation.from_rotvec(a[3:6])*Rotation.from_quat(obs.achieved_quaternion_xyzw)
        target=self.pose_type.from_arrays(
            np.asarray(obs.achieved_position_m)+a[:3],target_orientation.as_quat())
        certificate=self.certifier(
            tuple(self.belief.hypotheses),target,
            pos_lower=self.low,pos_upper=self.high,rot_lower=self.rot_scale,
            position_budget_m=self.pos_budget,rotation_budget_rad=self.rot_budget,
            hypotheses_complete=self.belief.valid,
            trusted_provenance=current_belief_trusted,
            age_steps=0,max_age_steps=0,
            root_translation_root_left_rotation_verified=True)
        if not certificate.authorized:
            self.action=None
            return DispatchDecision(
                "QUERY_TARGET",None,None,len(self.belief.hypotheses),
                certificate.worst_position_inf_m,
                certificate.worst_orientation_geodesic_rad,
                "Private controller target readback or refusal required: "+str(certificate.reason))
        native=tuple(map(float,certificate.normalized_6d))
        if (len(native)!=6 or not np.isfinite(native).all()
                or np.max(np.abs(native[:3]))>1+1e-7
                or np.linalg.norm(native[3:])>=1):
            raise ContractViolation("Geometric authorizer returned illegal native action")
        ticket=self.belief.prepare(native)
        self.pending=ticket
        self.action=None;self.observation=None  # invalidate ALL later chunk actions
        return DispatchDecision(
            "SEND_CERTIFIED",native,float(a[6]),len(self.belief.hypotheses),
            certificate.worst_position_inf_m,
            certificate.worst_orientation_geodesic_rad,
            "Only conditional commanded-target setpoint bound; no physical safety guarantee",
            ticket)

    def acknowledge(self,token,*,applied:bool|None):
        if self.pending is None or token!=self.pending:
            raise ContractViolation("Out-of-order/stale acknowledgement, do not collapse belief")
        self.belief.acknowledge(token,applied=applied)
        self.pending=None;self.observation=None;self.action=None

    def trusted_controller_resync(self,target,*,evidence:str):
        if self.pending is not None:
            raise ContractViolation("Cannot resync during pending native action")
        if evidence!="authoritative_controller_target_readback" or not isinstance(target,self.pose_type):
            raise ContractViolation("Achieved EE pose is NOT private target memory")
        self.belief.require_external_resync(target)
        if len(self.belief.hypotheses)!=1:
            raise ContractViolation("Controller-target readback must produce singleton belief")
        self.observation=None;self.action=None

    def reset_episode(self,target,*,evidence:str):
        if evidence!="authoritative_controller_reset" or not isinstance(target,self.pose_type):
            raise ContractViolation("Episode reset requires authoritative target initialization")
        self.belief.reset(target)
        self.last_episode=None;self.last_step=-1
        self.observation=None;self.action=None;self.pending=None

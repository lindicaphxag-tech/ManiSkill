"""Controller-native public-anchor mode refresh. DEVELOPMENT ONLY.

This capability briefly changes a simulator/controller SOFTWARE configuration
from accumulated-target-relative to achieved-EE-relative for ONE actual step.
It is not a normal hardware command. Count as a mode-write privilege.
No hidden target getter or setter is used in the method decision.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

EXPECTED_CHART = "root_translation:root_aligned_body_rotation"

@dataclass(frozen=True)
class ModeRefreshReceipt:
    kind: str
    mode_writes: int
    hidden_target_reads: int
    hidden_target_writes: int
    public_achieved_pose_reads: int
    actual_world_step_invocations: int
    controller_class: str
    source_frame: str
    success_claimed: bool
    may_be_used_as_robot_safety_certificate: bool

def _validate_public_pose(pose: Any):
    if pose is None or not hasattr(pose, 'p') or not hasattr(pose, 'q'):
        raise ValueError('No public controller EE pose evidence')
    for field, dim in (('p', 3), ('q', 4)):
        a=getattr(pose, field)
        if not hasattr(a,'shape') or a.shape[-1] != dim:
            raise ValueError('Wrong public achieved EE pose shape')
        if hasattr(a,'isfinite'):
            if not bool(a.isfinite().all()):
                raise ValueError('Nonfinite public achieved pose')
    return pose

def with_native_public_mode_refresh(*, arm: Any,
                                    dispatch_actual_world_step: Callable[[], Any],
                                    expected_controller_type: str,
                                    current_cpu_simulator: bool,
                                    mode_mutation_authorized: bool,
                                    dispatch_is_known_delivered: bool):
    """Perform precisely one real native world step in public-achieved pose mode.

    A simulator-internal software mode mutation is privileged; do not infer
    hardware portability or actual task success from the returned receipt.
    """
    if (mode_mutation_authorized is not True
        or current_cpu_simulator is not True
        or dispatch_is_known_delivered is not True):
        raise PermissionError('No unpriced/unverified native mode refresh')
    if (not isinstance(expected_controller_type,str)
        or expected_controller_type != 'PDEEPoseController'
        or type(arm).__name__ != expected_controller_type):
        raise ValueError('Controller type does not match audited native source')
    cfg=arm.config
    if not (cfg.frame == EXPECTED_CHART
            and cfg.use_delta is True
            and cfg.use_target is True
            and cfg.normalize_action is True):
        raise ValueError('Unsupported controller frame or accumulated-target contract')
    _validate_public_pose(arm.ee_pose_at_base)
    if not callable(dispatch_actual_world_step):
        raise TypeError('Must dispatch exactly one world step')
    # Config mutation is the intervention; neither get_state nor set_state is
    # called. For a zero native delta, the target computed by the CPU chart is
    # referenced to the public achieved EE pose, not the unknown old target.
    cfg.use_target=False
    try:
        result=dispatch_actual_world_step()
    finally:
        cfg.use_target=True
    return result, ModeRefreshReceipt(
        kind='DEVELOPMENT_SOFTWARE_NATIVE_MODE_REFRESH',mode_writes=2,
        hidden_target_reads=0,hidden_target_writes=0,
        public_achieved_pose_reads=1,actual_world_step_invocations=1,
        controller_class=expected_controller_type,source_frame=cfg.frame,
        success_claimed=False,may_be_used_as_robot_safety_certificate=False)

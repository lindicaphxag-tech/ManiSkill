from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from maniskill_joint_contract import (
    JointPositionContract,
    JointTransportCertificate,
    transport_joint_position_action,
)


@dataclass(frozen=True)
class ExtractedControllerContract:
    contract: JointPositionContract
    controller_class: str
    normalized: bool
    uses_previous_target: bool
    reference_owner: str
    controller_state_keys: tuple[str, ...]
    controller_state_observable: bool
    requires_stateful_migration: bool
    evidence_fields: tuple[str, ...]


def _numpy(value: Any) -> np.ndarray:
    """Convert numpy / torch-like arrays without importing torch."""
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value, dtype=float)


def extract_maniskill_joint_position_contract(
    controller: Any,
) -> ExtractedControllerContract:
    """Extract executable joint-position semantics from a ManiSkill controller object.

    This intentionally depends on the runtime interface rather than importing a
    concrete controller class, so the extractor can also be tested with a
    minimal contract stub.
    """
    if not hasattr(controller, "config"):
        raise TypeError("controller has no config")
    cfg = controller.config
    required = ("use_delta", "use_target", "normalize_action")
    missing = [name for name in required if not hasattr(cfg, name)]
    if missing:
        raise TypeError(f"controller config missing fields: {missing}")

    normalize = bool(cfg.normalize_action)
    evidence = ["config.use_delta", "config.use_target", "config.normalize_action"]

    if normalize:
        if not hasattr(controller, "action_space_low") or not hasattr(
            controller, "action_space_high"
        ):
            raise TypeError(
                "normalized controller must expose action_space_low/action_space_high"
            )
        low = _numpy(controller.action_space_low)
        high = _numpy(controller.action_space_high)
        evidence.extend(["action_space_low", "action_space_high"])
    else:
        if not hasattr(controller, "single_action_space"):
            raise TypeError(
                "unnormalized controller must expose single_action_space"
            )
        space = controller.single_action_space
        if not hasattr(space, "low") or not hasattr(space, "high"):
            raise TypeError("single_action_space must expose low/high")
        low = _numpy(space.low)
        high = _numpy(space.high)
        evidence.extend(["single_action_space.low", "single_action_space.high"])

    use_delta = bool(cfg.use_delta)
    use_target = bool(cfg.use_target)

    if not use_delta:
        reference_owner = "absolute"
    elif use_target:
        reference_owner = "controller_target"
    else:
        reference_owner = "current_qpos"

    state_keys: tuple[str, ...] = ()
    state_observable = False
    if hasattr(controller, "get_state") and callable(controller.get_state):
        try:
            runtime_state = controller.get_state()
        except Exception:
            runtime_state = None
        if isinstance(runtime_state, dict):
            state_keys = tuple(sorted(str(key) for key in runtime_state.keys()))
            state_observable = True
            evidence.append("get_state()")

    contract = JointPositionContract(
        use_delta=use_delta,
        use_target=use_target,
        normalize_action=normalize,
        low=low,
        high=high,
    )
    return ExtractedControllerContract(
        contract=contract,
        controller_class=controller.__class__.__name__,
        normalized=normalize,
        uses_previous_target=bool(use_delta and use_target),
        reference_owner=reference_owner,
        controller_state_keys=state_keys,
        controller_state_observable=state_observable,
        requires_stateful_migration=bool(use_delta and use_target),
        evidence_fields=tuple(evidence),
    )


def compile_maniskill_joint_position_migration(
    source_controller: Any,
    target_controller: Any,
    *,
    current_qpos: np.ndarray,
    source_target_qpos: np.ndarray,
    target_target_qpos: np.ndarray,
    source_native_action: np.ndarray,
) -> tuple[
    ExtractedControllerContract,
    ExtractedControllerContract,
    JointTransportCertificate,
]:
    """Extract both controller contracts and compile one migration."""
    source = extract_maniskill_joint_position_contract(source_controller)
    target = extract_maniskill_joint_position_contract(target_controller)
    cert = transport_joint_position_action(
        source.contract,
        target.contract,
        current_qpos=current_qpos,
        source_target_qpos=source_target_qpos,
        target_target_qpos=target_target_qpos,
        source_native_action=source_native_action,
    )
    return source, target, cert

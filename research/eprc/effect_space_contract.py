from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import contract_signature, signature_distance
from .support_restricted_authority import support_restricted_authority


@dataclass(frozen=True)
class EffectSpaceContract:
    """DEC projected into a shared task-effect space across embodiments."""

    effect_jacobian: np.ndarray
    signature_distance_ready: bool


def lift_to_effect_space(
    physical_support_jacobian: np.ndarray,
    physical_to_effect_jacobian: np.ndarray,
) -> np.ndarray:
    """Map an embodiment-specific physical DEC into a common task-effect tangent space."""

    j_phys = np.asarray(physical_support_jacobian, dtype=float)
    effect = np.asarray(physical_to_effect_jacobian, dtype=float)
    if j_phys.ndim != 2 or effect.ndim != 2:
        raise ValueError("jacobians must be 2D")
    if effect.shape[1] != j_phys.shape[0]:
        raise ValueError("effect map and physical command dimensions are incompatible")
    return effect @ j_phys


def effect_contract_distance(
    physical_support_jacobian_a: np.ndarray,
    physical_to_effect_a: np.ndarray,
    physical_support_jacobian_b: np.ndarray,
    physical_to_effect_b: np.ndarray,
) -> float:
    j_a = lift_to_effect_space(physical_support_jacobian_a, physical_to_effect_a)
    j_b = lift_to_effect_space(physical_support_jacobian_b, physical_to_effect_b)
    return signature_distance(contract_signature(j_a), contract_signature(j_b))


@dataclass(frozen=True)
class CrossEmbodimentTransport:
    target_action_support_jacobian: np.ndarray
    reconstructed_effect_jacobian: np.ndarray
    relative_effect_residual: float
    exact_on_effect_subspace: bool


def compile_effect_space_transport(
    source_effect_jacobian: np.ndarray,
    target_action_to_physical_jacobian: np.ndarray,
    target_physical_to_effect_jacobian: np.ndarray,
    *,
    tolerance: float = 1e-8,
) -> CrossEmbodimentTransport:
    """Compile support response through a target embodiment in common effect space.

    The effective target authority is E_t L_t, where L_t maps target action to
    target physical command and E_t maps that command to a shared task effect.
    """

    source = np.asarray(source_effect_jacobian, dtype=float)
    l_target = np.asarray(target_action_to_physical_jacobian, dtype=float)
    e_target = np.asarray(target_physical_to_effect_jacobian, dtype=float)
    if source.ndim != 2 or l_target.ndim != 2 or e_target.ndim != 2:
        raise ValueError("jacobians must be 2D")
    if e_target.shape[1] != l_target.shape[0]:
        raise ValueError("target effect and physical-command dimensions are incompatible")
    effective_lift = e_target @ l_target
    result = support_restricted_authority(
        source,
        effective_lift,
        tolerance=tolerance,
    )
    return CrossEmbodimentTransport(
        target_action_support_jacobian=result.target_action_support_jacobian,
        reconstructed_effect_jacobian=result.reconstructed_physical_jacobian,
        relative_effect_residual=result.certificate.relative_projection_residual,
        exact_on_effect_subspace=result.certificate.exact_on_support,
    )
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DifferentialContractSignature:
    """Representation-invariant local physical response signature.

    jacobian_phys maps physical support perturbations -> canonical physical command
    perturbations after controller/action semantic lifting.
    """

    response_projector: np.ndarray
    singular_values_normalized: np.ndarray
    rank: int


def _orthogonal_projector_from_columns(matrix: np.ndarray, *, rtol: float) -> tuple[np.ndarray, int]:
    if matrix.ndim != 2:
        raise ValueError("matrix must be 2D")
    if matrix.size == 0:
        return np.zeros((matrix.shape[0], matrix.shape[0])), 0
    u, s, _ = np.linalg.svd(matrix, full_matrices=False)
    if s.size == 0 or s[0] == 0:
        return np.zeros((matrix.shape[0], matrix.shape[0])), 0
    rank = int(np.sum(s > rtol * s[0]))
    if rank == 0:
        return np.zeros((matrix.shape[0], matrix.shape[0])), 0
    basis = u[:, :rank]
    return basis @ basis.T, rank


def contract_signature(jacobian_phys: np.ndarray, *, rtol: float = 1e-8) -> DifferentialContractSignature:
    """Build a local physical-contract signature.

    jacobian_phys shape: [physical_command_dim, support_perturbation_dim].
    The response projector captures which *physical command directions* are locally
    controlled by support perturbations. The normalized singular spectrum captures
    anisotropy while discarding global gain.
    """

    j = np.asarray(jacobian_phys, dtype=float)
    if j.ndim != 2:
        raise ValueError("jacobian_phys must be 2D")
    projector, rank = _orthogonal_projector_from_columns(j, rtol=rtol)

    s = np.linalg.svd(j, compute_uv=False)
    if s.size == 0 or s[0] == 0:
        spectrum = np.zeros_like(s)
    else:
        spectrum = s / s[0]

    return DifferentialContractSignature(
        response_projector=projector,
        singular_values_normalized=spectrum,
        rank=rank,
    )


def signature_distance(
    a: DifferentialContractSignature,
    b: DifferentialContractSignature,
) -> float:
    """Distance in [0, +inf) combining subspace and normalized-spectrum mismatch."""

    if a.response_projector.shape != b.response_projector.shape:
        raise ValueError("physical command dimensions differ")
    if a.rank != b.rank:
        return float("inf")

    proj = np.linalg.norm(a.response_projector - b.response_projector, ord="fro")
    k = min(len(a.singular_values_normalized), len(b.singular_values_normalized))
    spec = np.linalg.norm(
        a.singular_values_normalized[:k] - b.singular_values_normalized[:k]
    )
    return float(proj + spec)


def semantically_lift_jacobian(
    jacobian_action: np.ndarray,
    action_to_physical_jacobian: np.ndarray,
) -> np.ndarray:
    """Chain-rule lift from policy/controller action coordinates to physical command space."""

    j_action = np.asarray(jacobian_action, dtype=float)
    lift = np.asarray(action_to_physical_jacobian, dtype=float)
    if lift.ndim != 2 or j_action.ndim != 2:
        raise ValueError("jacobians must be 2D")
    if lift.shape[1] != j_action.shape[0]:
        raise ValueError("action lift and policy Jacobian dimensions are incompatible")
    return lift @ j_action


def contracts_equivalent(
    jacobian_action_a: np.ndarray,
    lift_a: np.ndarray,
    jacobian_action_b: np.ndarray,
    lift_b: np.ndarray,
    *,
    tolerance: float = 1e-6,
) -> bool:
    """Test local physical-contract equivalence after semantic lifting."""

    sig_a = contract_signature(semantically_lift_jacobian(jacobian_action_a, lift_a))
    sig_b = contract_signature(semantically_lift_jacobian(jacobian_action_b, lift_b))
    return signature_distance(sig_a, sig_b) <= tolerance

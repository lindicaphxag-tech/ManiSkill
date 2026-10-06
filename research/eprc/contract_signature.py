from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DifferentialContractSignature:
    """Representation-invariant local physical response signature.

    jacobian_phys maps canonical physical support perturbations to canonical
    physical command perturbations after controller/action semantic lifting.

    Coordinate reparameterization should disappear before this object is built.
    Physical response gain must not disappear: a controller/policy that reacts
    7x more strongly to the same physical perturbation has a different local
    execution contract.
    """

    normalized_jacobian: np.ndarray
    response_projector: np.ndarray
    singular_values_normalized: np.ndarray
    frobenius_gain: float
    rank: int


def _orthogonal_projector_from_columns(
    matrix: np.ndarray, *, rtol: float
) -> tuple[np.ndarray, int]:
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


def contract_signature(
    jacobian_phys: np.ndarray, *, rtol: float = 1e-8
) -> DifferentialContractSignature:
    """Build a scale-preserving local physical-contract signature.

    Shape: [physical_command_dim, physical_support_dim].

    The signature separates three pieces:
    - response subspace;
    - anisotropy shape (normalized singular spectrum);
    - absolute physical response gain (Frobenius norm).

    The first two describe geometry. The last prevents a dangerous false
    equivalence in which two physically different gains are normalized away.
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

    gain = float(np.linalg.norm(j, ord="fro"))
    normalized_jacobian = np.zeros_like(j) if gain == 0.0 else j / gain

    return DifferentialContractSignature(
        normalized_jacobian=normalized_jacobian,
        response_projector=projector,
        singular_values_normalized=spectrum,
        frobenius_gain=gain,
        rank=rank,
    )


def _gain_distance(a: float, b: float) -> float:
    """Dimensionless multiplicative gain mismatch in the same physical units."""

    if a == 0.0 and b == 0.0:
        return 0.0
    if a <= 0.0 or b <= 0.0:
        return float("inf")
    return float(abs(np.log(a / b)))


def signature_distance(
    a: DifferentialContractSignature,
    b: DifferentialContractSignature,
) -> float:
    """Distance combining physical subspace, anisotropy and response gain."""

    if a.normalized_jacobian.shape != b.normalized_jacobian.shape:
        raise ValueError("canonical physical command/support dimensions differ")
    if a.response_projector.shape != b.response_projector.shape:
        raise ValueError("physical command dimensions differ")
    if a.rank != b.rank:
        return float("inf")

    # Once action and support charts have been canonicalized, the correspondence
    # between physical support directions and physical command directions is
    # itself part of the contract. Projector/spectrum alone would falsely equate
    # maps such as I and an x/y support-axis swap.
    oriented_map = np.linalg.norm(
        a.normalized_jacobian - b.normalized_jacobian, ord="fro"
    )
    proj = np.linalg.norm(a.response_projector - b.response_projector, ord="fro")
    k = min(len(a.singular_values_normalized), len(b.singular_values_normalized))
    spec = np.linalg.norm(
        a.singular_values_normalized[:k] - b.singular_values_normalized[:k]
    )
    gain = _gain_distance(a.frobenius_gain, b.frobenius_gain)
    return float(oriented_map + proj + spec + gain)


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

    sig_a = contract_signature(
        semantically_lift_jacobian(jacobian_action_a, lift_a)
    )
    sig_b = contract_signature(
        semantically_lift_jacobian(jacobian_action_b, lift_b)
    )
    return signature_distance(sig_a, sig_b) <= tolerance

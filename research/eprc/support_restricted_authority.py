from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SupportRestrictedAuthorityCertificate:
    """Authority of a target controller only on the physical response subspace required now."""

    source_response_rank: int
    target_authority_rank: int
    projection_residual: float
    relative_projection_residual: float
    exact_on_support: bool
    target_action_response_norm: float


@dataclass(frozen=True)
class SupportRestrictedTransport:
    target_action_support_jacobian: np.ndarray
    reconstructed_physical_jacobian: np.ndarray
    certificate: SupportRestrictedAuthorityCertificate


def _matrix_rank(matrix: np.ndarray, *, rtol: float) -> int:
    a = np.asarray(matrix, dtype=float)
    if a.size == 0:
        return 0
    s = np.linalg.svd(a, compute_uv=False)
    if s.size == 0 or s[0] == 0:
        return 0
    return int(np.sum(s > rtol * s[0]))


def support_restricted_authority(
    source_physical_jacobian: np.ndarray,
    target_action_to_physical_jacobian: np.ndarray,
    *,
    tolerance: float = 1e-8,
    rank_rtol: float = 1e-10,
) -> SupportRestrictedTransport:
    """Check whether the target controller can realize the source DEC on its active support subspace.

    Let J be the desired physical support-response Jacobian and L the target
    controller's local action->physical Jacobian. Exact local transport exists iff

        Im(J) subseteq Im(L),

    equivalently (I - L L^+) J = 0.

    The minimum-norm target action response is L^+ J. This remains valid when L is
    rectangular or globally rank deficient.
    """

    j = np.asarray(source_physical_jacobian, dtype=float)
    l = np.asarray(target_action_to_physical_jacobian, dtype=float)

    if j.ndim != 2 or l.ndim != 2:
        raise ValueError("source physical Jacobian and target lift must be 2D")
    if j.shape[0] != l.shape[0]:
        raise ValueError("physical command dimensions differ")

    pinv = np.linalg.pinv(l)
    target_action_j = pinv @ j
    reconstructed = l @ target_action_j
    residual = float(np.linalg.norm(reconstructed - j, ord="fro"))
    denom = float(np.linalg.norm(j, ord="fro"))
    relative = residual if denom == 0 else residual / denom

    cert = SupportRestrictedAuthorityCertificate(
        source_response_rank=_matrix_rank(j, rtol=rank_rtol),
        target_authority_rank=_matrix_rank(l, rtol=rank_rtol),
        projection_residual=residual,
        relative_projection_residual=relative,
        exact_on_support=relative <= tolerance,
        target_action_response_norm=float(np.linalg.norm(target_action_j, ord="fro")),
    )
    return SupportRestrictedTransport(
        target_action_support_jacobian=target_action_j,
        reconstructed_physical_jacobian=reconstructed,
        certificate=cert,
    )


def global_full_rank_required(
    target_action_to_physical_jacobian: np.ndarray,
    *,
    rank_rtol: float = 1e-10,
) -> bool:
    """Legacy conservative gate: useful only as a negative-control baseline."""

    l = np.asarray(target_action_to_physical_jacobian, dtype=float)
    # L maps action coordinates -> physical command coordinates. Global physical
    # authority requires full *row* rank: every local physical command direction
    # must lie in Im(L). Full column rank is insufficient for an underactuated
    # tall map with fewer action DoF than physical-command DoF.
    return _matrix_rank(l, rtol=rank_rtol) == l.shape[0]

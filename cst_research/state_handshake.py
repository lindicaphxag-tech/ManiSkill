from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class HandshakeStatus(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    IMPOSSIBLE = "impossible"


@dataclass(frozen=True)
class ControllerStateHandshakeCertificate:
    """Linear controlled-simulation handshake between controller state models."""

    status: HandshakeStatus
    state_map: np.ndarray
    state_feedback: np.ndarray
    action_map: np.ndarray
    output_residual: float
    dynamics_residual: float
    action_residual: float
    relative_residual: float
    rank: int
    unknowns: int
    equations: int
    reason: str


def _m(value, name):
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _vec(matrix: np.ndarray) -> np.ndarray:
    """Column-major vec compatible with Kronecker identities."""
    return np.asarray(matrix, dtype=float).reshape(-1, order="F")


def _unvec(vector: np.ndarray, rows: int, cols: int) -> np.ndarray:
    return np.asarray(vector, dtype=float).reshape((rows, cols), order="F")


def synthesize_controller_state_handshake(
    source_A: np.ndarray,
    source_B: np.ndarray,
    source_C: np.ndarray,
    target_A: np.ndarray,
    target_B: np.ndarray,
    target_C: np.ndarray,
    *,
    exact_rtol: float = 1e-10,
    approximate_relative_tolerance: float = 5e-2,
) -> ControllerStateHandshakeCertificate:
    """Solve for a state map and target action adapter.

    Source:
        s' = A_s s + B_s u
        y  = C_s s

    Target:
        t' = A_t t + B_t v
        y  = C_t t

    We seek
        t = H s
        v = K_s s + K_u u

    such that
        C_t H = C_s
        A_t H + B_t K_s = H A_s
        B_t K_u = H B_s.

    These equations are jointly linear in H, K_s and K_u, so the minimum
    residual certificate is obtained by one least-squares solve.
    """
    A_s = _m(source_A, "source_A")
    B_s = _m(source_B, "source_B")
    C_s = _m(source_C, "source_C")
    A_t = _m(target_A, "target_A")
    B_t = _m(target_B, "target_B")
    C_t = _m(target_C, "target_C")

    n_s = A_s.shape[0]
    n_t = A_t.shape[0]
    if A_s.shape != (n_s, n_s) or A_t.shape != (n_t, n_t):
        raise ValueError("A matrices must be square")
    if B_s.shape[0] != n_s or B_t.shape[0] != n_t:
        raise ValueError("B matrices have incompatible state dimensions")
    if C_s.shape[1] != n_s or C_t.shape[1] != n_t:
        raise ValueError("C matrices have incompatible state dimensions")
    if C_s.shape[0] != C_t.shape[0]:
        raise ValueError("source and target must expose the same output dimension")
    if exact_rtol <= 0 or not np.isfinite(exact_rtol):
        raise ValueError("exact_rtol must be finite and positive")
    if approximate_relative_tolerance < 0 or not np.isfinite(
        approximate_relative_tolerance
    ):
        raise ValueError("approximate_relative_tolerance must be finite and non-negative")

    m_s = B_s.shape[1]
    m_t = B_t.shape[1]
    p = C_s.shape[0]

    h_size = n_t * n_s
    ks_size = m_t * n_s
    ku_size = m_t * m_s
    total = h_size + ks_size + ku_size

    # Output consistency: C_t H = C_s.
    M_out = np.zeros((p * n_s, total))
    M_out[:, :h_size] = np.kron(np.eye(n_s), C_t)
    b_out = _vec(C_s)

    # Dynamics intertwining: A_t H + B_t K_s - H A_s = 0.
    M_dyn = np.zeros((n_t * n_s, total))
    M_dyn[:, :h_size] = (
        np.kron(np.eye(n_s), A_t)
        - np.kron(A_s.T, np.eye(n_t))
    )
    M_dyn[:, h_size : h_size + ks_size] = np.kron(np.eye(n_s), B_t)
    b_dyn = np.zeros(n_t * n_s)

    # Input transport: B_t K_u - H B_s = 0.
    M_act = np.zeros((n_t * m_s, total))
    M_act[:, :h_size] = -np.kron(B_s.T, np.eye(n_t))
    M_act[:, h_size + ks_size :] = np.kron(np.eye(m_s), B_t)
    b_act = np.zeros(n_t * m_s)

    M = np.vstack([M_out, M_dyn, M_act])
    b = np.concatenate([b_out, b_dyn, b_act])
    solution, _, rank, _ = np.linalg.lstsq(M, b, rcond=exact_rtol)

    H = _unvec(solution[:h_size], n_t, n_s)
    K_s = _unvec(solution[h_size : h_size + ks_size], m_t, n_s)
    K_u = _unvec(solution[h_size + ks_size :], m_t, m_s)

    out_R = C_t @ H - C_s
    dyn_R = A_t @ H + B_t @ K_s - H @ A_s
    act_R = B_t @ K_u - H @ B_s

    out_norm = float(np.linalg.norm(out_R, ord=2))
    dyn_norm = float(np.linalg.norm(dyn_R, ord=2))
    act_norm = float(np.linalg.norm(act_R, ord=2))
    aggregate = np.concatenate([_vec(out_R), _vec(dyn_R), _vec(act_R)])
    residual = float(np.linalg.norm(aggregate))
    scale = max(float(np.linalg.norm(b)), 1.0)
    relative = residual / scale

    if relative <= exact_rtol:
        status = HandshakeStatus.EXACT
        reason = "an exact output-preserving controlled simulation handshake exists"
    elif relative <= approximate_relative_tolerance:
        status = HandshakeStatus.APPROXIMATE
        reason = "only an approximate controller-state handshake was found"
    else:
        status = HandshakeStatus.IMPOSSIBLE
        reason = (
            "the declared source/target state-output dynamics are inconsistent "
            "with one linear controller-state handshake"
        )

    return ControllerStateHandshakeCertificate(
        status=status,
        state_map=H,
        state_feedback=K_s,
        action_map=K_u,
        output_residual=out_norm,
        dynamics_residual=dyn_norm,
        action_residual=act_norm,
        relative_residual=relative,
        rank=int(rank),
        unknowns=total,
        equations=int(M.shape[0]),
        reason=reason,
    )


def verify_handshake_rollout(
    certificate: ControllerStateHandshakeCertificate,
    source_A: np.ndarray,
    source_B: np.ndarray,
    source_C: np.ndarray,
    target_A: np.ndarray,
    target_B: np.ndarray,
    target_C: np.ndarray,
    source_initial_state: np.ndarray,
    source_actions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Roll out source and target under the synthesized handshake."""
    A_s = _m(source_A, "source_A")
    B_s = _m(source_B, "source_B")
    C_s = _m(source_C, "source_C")
    A_t = _m(target_A, "target_A")
    B_t = _m(target_B, "target_B")
    C_t = _m(target_C, "target_C")
    s = np.asarray(source_initial_state, dtype=float)
    actions = np.asarray(source_actions, dtype=float)
    if s.shape != (A_s.shape[0],):
        raise ValueError("source_initial_state dimension mismatch")
    if actions.ndim != 2 or actions.shape[1] != B_s.shape[1]:
        raise ValueError("source_actions dimension mismatch")

    t = certificate.state_map @ s
    source_outputs = [C_s @ s]
    target_outputs = [C_t @ t]
    for u in actions:
        v = certificate.state_feedback @ s + certificate.action_map @ u
        s = A_s @ s + B_s @ u
        t = A_t @ t + B_t @ v
        source_outputs.append(C_s @ s)
        target_outputs.append(C_t @ t)
    return np.stack(source_outputs), np.stack(target_outputs)

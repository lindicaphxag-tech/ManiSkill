from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


@dataclass(frozen=True)
class LinearSemanticTransducer:
    """Linear controller-semantic transducer.

    z_next = A z + B u
    y      = C z + D u

    z may contain controller-owned hidden semantics and any physical state that
    must participate in the simulation relation.  A zero-dimensional z is
    allowed for stateless target charts.
    """

    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def __post_init__(self):
        A = np.asarray(self.A, dtype=float)
        B = np.asarray(self.B, dtype=float)
        C = np.asarray(self.C, dtype=float)
        D = np.asarray(self.D, dtype=float)
        for name, value in (("A", A), ("B", B), ("C", C), ("D", D)):
            if value.ndim != 2 or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be a finite matrix")
        nz = A.shape[0]
        if A.shape != (nz, nz):
            raise ValueError("A must be square")
        if B.shape[0] != nz:
            raise ValueError("B row dimension must equal hidden-state dimension")
        ny = C.shape[0]
        if C.shape[1] != nz:
            raise ValueError("C column dimension must equal hidden-state dimension")
        if D.shape[0] != ny:
            raise ValueError("C and D must share output dimension")
        if B.shape[1] != D.shape[1]:
            raise ValueError("B and D must share action dimension")
        if ny == 0 or D.shape[1] == 0:
            raise ValueError("output and action dimensions must be non-zero")

    @property
    def state_dim(self) -> int:
        return int(np.asarray(self.A).shape[0])

    @property
    def action_dim(self) -> int:
        return int(np.asarray(self.D).shape[1])

    @property
    def output_dim(self) -> int:
        return int(np.asarray(self.D).shape[0])


class StatefulTransportKind(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    NO_LINEAR_SIMULATION = "no_linear_simulation"


@dataclass(frozen=True)
class StatefulTransportCertificate:
    """Linear simulation relation plus a source-state-aware target adapter."""

    kind: StatefulTransportKind
    exact: bool
    state_relation: np.ndarray
    source_state_feedback: np.ndarray
    action_adapter: np.ndarray
    output_state_residual: np.ndarray
    output_action_residual: np.ndarray
    dynamics_state_residual: np.ndarray
    dynamics_action_residual: np.ndarray
    max_abs_residual: float
    residual_l2: float
    linear_system_rank: int
    solution_nullity: int
    allow_source_state_feedback: bool
    source_state_access_mask: np.ndarray
    reason: str


def _zeros(shape):
    return np.zeros(shape, dtype=float)


def _residual_blocks(
    source: LinearSemanticTransducer,
    target: LinearSemanticTransducer,
    M: np.ndarray,
    L: np.ndarray,
    K: np.ndarray,
):
    # Output commutation:
    # C_t M z_s + D_t(L z_s + K u_s) == C_s z_s + D_s u_s.
    output_state = target.C @ M + target.D @ L - source.C
    output_action = target.D @ K - source.D

    # Simulation-relation closure:
    # M(A_s z_s + B_s u_s)
    #   == A_t M z_s + B_t(L z_s + K u_s).
    dynamics_state = M @ source.A - target.A @ M - target.B @ L
    dynamics_action = M @ source.B - target.B @ K
    return output_state, output_action, dynamics_state, dynamics_action


def _flatten_blocks(blocks) -> np.ndarray:
    pieces = [np.asarray(block, dtype=float).reshape(-1) for block in blocks if block.size]
    if not pieces:
        return np.empty((0,), dtype=float)
    return np.concatenate(pieces)


def synthesize_linear_stateful_transport(
    source: LinearSemanticTransducer,
    target: LinearSemanticTransducer,
    *,
    allow_source_state_feedback: bool = True,
    atol: float = 1e-10,
    rtol: float = 1e-10,
    approximate_tolerance: float | None = None,
    source_state_access_mask: np.ndarray | None = None,
) -> StatefulTransportCertificate:
    """Solve for a state relation and stateful action adapter.

    The target action is

        u_t = L z_s + K u_s

    and the hidden-state handshake is

        z_t = M z_s.

    The solver enforces both output commutation and next-state closure.  Setting
    allow_source_state_feedback=False constrains L=0 and therefore asks whether
    a stateless action map alone can realize the same controller semantics.
    """
    if source.output_dim != target.output_dim:
        raise ValueError("source and target must share declared output dimension")
    if atol < 0 or rtol <= 0 or not np.isfinite(atol) or not np.isfinite(rtol):
        raise ValueError("invalid tolerances")
    if approximate_tolerance is not None and (
        approximate_tolerance < 0 or not np.isfinite(approximate_tolerance)
    ):
        raise ValueError("approximate_tolerance must be finite and non-negative")

    ns = source.state_dim
    nt = target.state_dim
    ms = source.action_dim
    mt = target.action_dim

    if source_state_access_mask is None:
        access = np.ones(ns, dtype=bool)
    else:
        access = np.asarray(source_state_access_mask, dtype=bool)
        if access.shape != (ns,):
            raise ValueError("source_state_access_mask must match source state dimension")
    active = np.flatnonzero(access)
    na = int(active.size)

    # Only exposed source-state coordinates may participate in either the
    # target hidden-state handshake M or state-feedback adapter L.  This makes
    # the mask an executable interface contract rather than an analysis hint.
    m_size = nt * na
    l_size = mt * na if allow_source_state_feedback else 0
    k_size = mt * ms
    n_unknown = m_size + l_size + k_size

    def unpack(theta: np.ndarray):
        cursor = 0
        M = _zeros((nt, ns))
        if m_size:
            M[:, active] = theta[cursor : cursor + m_size].reshape(nt, na)
        cursor += m_size
        L = _zeros((mt, ns))
        if allow_source_state_feedback and l_size:
            L[:, active] = theta[cursor : cursor + l_size].reshape(mt, na)
        cursor += l_size
        K = theta[cursor : cursor + k_size].reshape(mt, ms)
        return M, L, K

    theta0 = np.zeros(n_unknown, dtype=float)
    M0, L0, K0 = unpack(theta0)
    r0 = _flatten_blocks(_residual_blocks(source, target, M0, L0, K0))

    operator = np.empty((r0.size, n_unknown), dtype=float)
    for j in range(n_unknown):
        basis = np.zeros(n_unknown, dtype=float)
        basis[j] = 1.0
        Mj, Lj, Kj = unpack(basis)
        rj = _flatten_blocks(_residual_blocks(source, target, Mj, Lj, Kj))
        operator[:, j] = rj - r0

    theta, _, rank, _ = np.linalg.lstsq(operator, -r0, rcond=rtol)
    M, L, K = unpack(theta)
    blocks = _residual_blocks(source, target, M, L, K)
    residual = _flatten_blocks(blocks)
    residual_l2 = float(np.linalg.norm(residual))
    max_abs = float(np.max(np.abs(residual))) if residual.size else 0.0

    scale = max(
        float(np.linalg.norm(source.C)),
        float(np.linalg.norm(source.D)),
        1.0,
    )
    exact = bool(max_abs <= atol + rtol * scale)
    if exact:
        kind = StatefulTransportKind.EXACT
        reason = (
            "output semantics commute and the hidden-state simulation relation "
            "is closed under one-step updates"
        )
    elif approximate_tolerance is not None and residual_l2 <= approximate_tolerance:
        kind = StatefulTransportKind.APPROXIMATE
        reason = (
            "no exact linear simulation relation was found, but the joint "
            "output/dynamics residual is within the declared approximation budget"
        )
    else:
        kind = StatefulTransportKind.NO_LINEAR_SIMULATION
        reason = (
            "the declared target transducer cannot satisfy output equivalence and "
            "hidden-state update closure under the allowed adapter class"
        )

    return StatefulTransportCertificate(
        kind=kind,
        exact=exact,
        state_relation=M,
        source_state_feedback=L,
        action_adapter=K,
        output_state_residual=blocks[0],
        output_action_residual=blocks[1],
        dynamics_state_residual=blocks[2],
        dynamics_action_residual=blocks[3],
        max_abs_residual=max_abs,
        residual_l2=residual_l2,
        linear_system_rank=int(rank),
        solution_nullity=int(n_unknown - rank),
        allow_source_state_feedback=allow_source_state_feedback,
        source_state_access_mask=access,
        reason=reason,
    )

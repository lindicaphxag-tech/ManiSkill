from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .linear_authority import LinearActionAuthority
from .robust_repairability import (
    PhysicalMapUncertainty,
    RobustRepairCertificate,
    RobustRepairDecision,
    robust_repair_certificate,
    robust_support_radius_linear_authority,
)


@dataclass(frozen=True)
class ChunkAuthority:
    authority: LinearActionAuthority
    labels: tuple[str, ...]
    horizon: int
    action_dim: int

    def contains(self, chunk: np.ndarray, *, atol: float = 1e-10) -> bool:
        arr = np.asarray(chunk, dtype=float)
        if arr.shape != (self.horizon, self.action_dim):
            raise ValueError("chunk shape mismatch")
        return self.authority.contains(arr.reshape(-1), atol=atol)


@dataclass(frozen=True)
class RobustChunkRepair:
    certificate: RobustRepairCertificate
    repaired_chunk: np.ndarray
    nominal_chunk: np.ndarray
    action_delta_chunk: np.ndarray
    robust_support_radius: float
    authority_limiting_constraint: int | None
    authority_limiting_label: str | None


def _vector(value: float | np.ndarray, dim: int, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        return np.full(dim, float(arr))
    if arr.shape != (dim,):
        raise ValueError(f"{name} must be scalar or shape [{dim}]")
    return arr


def build_chunk_authority(
    *,
    horizon: int,
    action_low: np.ndarray,
    action_high: np.ndarray,
    previous_action: np.ndarray,
    max_step_delta: float | np.ndarray | None = None,
    max_jerk: float | np.ndarray | None = None,
    previous_delta: np.ndarray | None = None,
) -> ChunkAuthority:
    """Build H vec(chunk) <= h for bounds, discontinuity and jerk.

    This is a pure temporal authority object. It does not decide whether a
    correction is policy-consistent; CRG intersects it with the identified
    chunk-response image.
    """

    lo = np.asarray(action_low, dtype=float)
    hi = np.asarray(action_high, dtype=float)
    prev = np.asarray(previous_action, dtype=float)
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if lo.ndim != 1 or hi.shape != lo.shape or prev.shape != lo.shape:
        raise ValueError("action vectors must be shape-aligned")
    if np.any(lo > hi):
        raise ValueError("action_low exceeds action_high")

    d = lo.size
    n = horizon * d
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    labels: list[str] = []

    def add(coeff: dict[tuple[int, int], float], bound: float, label: str):
        row = np.zeros(n, dtype=float)
        for (t, j), value in coeff.items():
            row[t * d + j] = value
        rows.append(row)
        rhs.append(float(bound))
        labels.append(label)

    for t in range(horizon):
        for j in range(d):
            add({(t, j): 1.0}, hi[j], f"upper[t={t},dim={j}]")
            add({(t, j): -1.0}, -lo[j], f"lower[t={t},dim={j}]")

    if max_step_delta is not None:
        step = _vector(max_step_delta, d, "max_step_delta")
        if np.any(step < 0):
            raise ValueError("max_step_delta must be nonnegative")
        for j in range(d):
            add({(0, j): 1.0}, step[j] + prev[j], f"step+[t=0,dim={j}]")
            add({(0, j): -1.0}, step[j] - prev[j], f"step-[t=0,dim={j}]")
        for t in range(1, horizon):
            for j in range(d):
                add(
                    {(t, j): 1.0, (t - 1, j): -1.0},
                    step[j],
                    f"step+[t={t},dim={j}]",
                )
                add(
                    {(t, j): -1.0, (t - 1, j): 1.0},
                    step[j],
                    f"step-[t={t},dim={j}]",
                )

    if max_jerk is not None:
        jerk = _vector(max_jerk, d, "max_jerk")
        if np.any(jerk < 0):
            raise ValueError("max_jerk must be nonnegative")
        if previous_delta is None:
            raise ValueError("previous_delta is required when max_jerk is set")
        prev_delta = np.asarray(previous_delta, dtype=float)
        if prev_delta.shape != (d,):
            raise ValueError("previous_delta shape mismatch")

        for j in range(d):
            # (a0-prev) - prev_delta <= jerk
            add(
                {(0, j): 1.0},
                jerk[j] + prev[j] + prev_delta[j],
                f"jerk+[t=0,dim={j}]",
            )
            add(
                {(0, j): -1.0},
                jerk[j] - prev[j] - prev_delta[j],
                f"jerk-[t=0,dim={j}]",
            )

        if horizon >= 2:
            for j in range(d):
                # (a1-a0) - (a0-prev) = a1 - 2a0 + prev
                add(
                    {(1, j): 1.0, (0, j): -2.0},
                    jerk[j] - prev[j],
                    f"jerk+[t=1,dim={j}]",
                )
                add(
                    {(1, j): -1.0, (0, j): 2.0},
                    jerk[j] + prev[j],
                    f"jerk-[t=1,dim={j}]",
                )

        for t in range(2, horizon):
            for j in range(d):
                coeff = {
                    (t, j): 1.0,
                    (t - 1, j): -2.0,
                    (t - 2, j): 1.0,
                }
                add(coeff, jerk[j], f"jerk+[t={t},dim={j}]")
                add(
                    {key: -value for key, value in coeff.items()},
                    jerk[j],
                    f"jerk-[t={t},dim={j}]",
                )

    authority = LinearActionAuthority(np.stack(rows), np.asarray(rhs))
    return ChunkAuthority(authority, tuple(labels), horizon, d)


def certify_chunk_repair(
    chunk_action_support_jacobian: np.ndarray,
    chunk_action_to_physical_jacobian: np.ndarray,
    target_physical_correction: np.ndarray,
    *,
    nominal_chunk: np.ndarray,
    chunk_authority: ChunkAuthority,
    epsilon_j: float,
    epsilon_g: float,
    trust_radius: float,
    residual_tolerance: float,
) -> RobustChunkRepair:
    """Robust CRG on a flattened action chunk with temporal authority."""

    nominal = np.asarray(nominal_chunk, dtype=float)
    if nominal.shape != (chunk_authority.horizon, chunk_authority.action_dim):
        raise ValueError("nominal_chunk shape mismatch")
    j = np.asarray(chunk_action_support_jacobian, dtype=float)
    c = np.asarray(chunk_action_to_physical_jacobian, dtype=float)
    if j.shape[0] != nominal.size:
        raise ValueError("chunk Jacobian output dimension mismatch")
    if c.ndim != 2 or c.shape[1] != nominal.size:
        raise ValueError("chunk semantic lift dimension mismatch")

    robust_radius = robust_support_radius_linear_authority(
        nominal.reshape(-1),
        j,
        chunk_authority.authority,
        epsilon_j=epsilon_j,
        trust_radius=trust_radius,
    )
    cert = robust_repair_certificate(
        c @ j,
        target_physical_correction,
        physical_map_uncertainty=PhysicalMapUncertainty(epsilon_g),
        certified_radius=robust_radius.certified_radius,
        residual_tolerance=residual_tolerance,
    )

    if cert.decision is RobustRepairDecision.CERTIFIED_REPAIR:
        action_delta = j @ cert.support_delta
    else:
        action_delta = np.zeros(nominal.size, dtype=float)
    repaired = nominal.reshape(-1) + action_delta

    limiting = robust_radius.limiting_constraint
    label = (
        chunk_authority.labels[limiting]
        if limiting is not None and 0 <= limiting < len(chunk_authority.labels)
        else None
    )

    return RobustChunkRepair(
        certificate=cert,
        repaired_chunk=repaired.reshape(nominal.shape),
        nominal_chunk=nominal.copy(),
        action_delta_chunk=action_delta.reshape(nominal.shape),
        robust_support_radius=robust_radius.certified_radius,
        authority_limiting_constraint=limiting,
        authority_limiting_label=label,
    )

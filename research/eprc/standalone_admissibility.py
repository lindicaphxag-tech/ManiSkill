"""Standalone DEC/locality/admissibility replication core.

Dependency: NumPy only.

Copy this file into an unrelated project and feed it physical-command Jacobian
replicates. It deliberately contains no imports from EPRC so third-party
replication does not depend on the owner package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import numpy as np


class Admissibility(str, Enum):
    ADMISSIBLE_FIRST_ORDER = "ADMISSIBLE_FIRST_ORDER"
    INFORMATION_LIMITED = "INFORMATION_LIMITED"
    LOCALITY_LIMITED = "LOCALITY_LIMITED"
    REJECT_LOCAL_MODEL = "REJECT_LOCAL_MODEL"


@dataclass(frozen=True)
class StandaloneResult:
    dec_q95_radius: float
    dec_stable: bool
    coarse_fine_drift: float
    fine_finer_drift: float
    contraction_ratio: float
    locality_contracting: bool
    finer_stochastic_radius: float
    admissibility: Admissibility


def _projector(j: np.ndarray, rtol: float = 1e-8) -> tuple[np.ndarray, int]:
    u, s, _ = np.linalg.svd(j, full_matrices=False)
    if s.size == 0 or s[0] == 0:
        return np.zeros((j.shape[0], j.shape[0])), 0
    rank = int(np.sum(s > rtol * s[0]))
    if rank == 0:
        return np.zeros((j.shape[0], j.shape[0])), 0
    q = u[:, :rank]
    return q @ q.T, rank


def _signature(j: np.ndarray):
    j = np.asarray(j, dtype=float)
    gain = float(np.linalg.norm(j, ord="fro"))
    norm_j = np.zeros_like(j) if gain == 0.0 else j / gain
    p, rank = _projector(j)
    s = np.linalg.svd(j, compute_uv=False)
    spec = np.zeros_like(s) if s.size == 0 or s[0] == 0 else s / s[0]
    return norm_j, p, spec, gain, rank


def _sig_distance(a, b) -> float:
    ja, pa, sa, ga, ra = a
    jb, pb, sb, gb, rb = b
    if ja.shape != jb.shape or pa.shape != pb.shape:
        raise ValueError("canonical physical dimensions differ")
    if ra != rb:
        return float("inf")
    oriented = np.linalg.norm(ja - jb, ord="fro")
    proj = np.linalg.norm(pa - pb, ord="fro")
    k = min(len(sa), len(sb))
    spec = np.linalg.norm(sa[:k] - sb[:k])
    if ga == 0.0 and gb == 0.0:
        gain = 0.0
    elif ga <= 0.0 or gb <= 0.0:
        gain = float("inf")
    else:
        gain = abs(np.log(ga / gb))
    return float(oriented + proj + spec + gain)


def _dec_q95(reps: np.ndarray) -> float:
    reps = np.asarray(reps, dtype=float)
    if reps.ndim != 3 or reps.shape[0] == 0:
        raise ValueError("replicates must have shape [n, physical_dim, support_dim]")
    center = np.mean(reps, axis=0)
    cs = _signature(center)
    radii = np.asarray([_sig_distance(_signature(r), cs) for r in reps], dtype=float)
    return float(np.quantile(radii, 0.95, method="higher"))


def _operator_center_radius(reps: np.ndarray) -> tuple[np.ndarray, float]:
    reps = np.asarray(reps, dtype=float)
    if reps.ndim != 3 or reps.shape[0] == 0:
        raise ValueError("replicates must have shape [n, physical_dim, support_dim]")
    center = np.mean(reps, axis=0)
    radii = np.asarray([np.linalg.norm(r - center, ord=2) for r in reps])
    return center, float(np.max(radii))


def classify(*, dec_stable: bool, locality_contracting: bool) -> Admissibility:
    if dec_stable and locality_contracting:
        return Admissibility.ADMISSIBLE_FIRST_ORDER
    if (not dec_stable) and locality_contracting:
        return Admissibility.INFORMATION_LIMITED
    if dec_stable and (not locality_contracting):
        return Admissibility.LOCALITY_LIMITED
    return Admissibility.REJECT_LOCAL_MODEL


def evaluate(
    *,
    coarse_map: np.ndarray,
    fine_map_replicates: np.ndarray,
    finer_map_replicates: np.ndarray,
    max_q95_radius: float = 0.15,
    contraction_threshold: float = 0.75,
    atol: float = 1e-12,
) -> StandaloneResult:
    coarse = np.asarray(coarse_map, dtype=float)
    fine = np.asarray(fine_map_replicates, dtype=float)
    finer = np.asarray(finer_map_replicates, dtype=float)
    if fine.ndim != 3 or finer.ndim != 3 or fine.shape[1:] != finer.shape[1:]:
        raise ValueError("fine/finer replicate shapes differ")
    if coarse.shape != fine.shape[1:]:
        raise ValueError("coarse map shape differs")

    q95 = _dec_q95(fine)
    dec_stable = bool(fine.shape[0] >= 5 and np.isfinite(q95) and q95 <= max_q95_radius)

    fine_center, _ = _operator_center_radius(fine)
    finer_center, finer_radius = _operator_center_radius(finer)
    d1 = float(np.linalg.norm(coarse - fine_center, ord=2))
    d2 = float(np.linalg.norm(fine_center - finer_center, ord=2))
    if d1 <= atol:
        ratio = 0.0 if d2 <= atol else float("inf")
    else:
        ratio = d2 / d1
    local = bool(ratio <= contraction_threshold)

    return StandaloneResult(
        dec_q95_radius=q95,
        dec_stable=dec_stable,
        coarse_fine_drift=d1,
        fine_finer_drift=d2,
        contraction_ratio=float(ratio),
        locality_contracting=local,
        finer_stochastic_radius=finer_radius,
        admissibility=classify(
            dec_stable=dec_stable,
            locality_contracting=local,
        ),
    )

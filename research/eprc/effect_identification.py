from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class EffectIdentificationCertificate:
    probe_count: int
    action_dim: int
    effect_dim: int
    probe_rank: int
    full_action_rank: bool
    probe_condition_number: float
    training_residual: float
    held_out_residual: float
    locally_valid: bool


def symmetric_effect_measurements(
    effect_fn: Callable[[np.ndarray], np.ndarray],
    base_action: np.ndarray,
    directions: np.ndarray,
    *,
    epsilon: float,
) -> np.ndarray:
    """Directional derivatives of an observed task effect under action probes."""

    base = np.asarray(base_action, dtype=float)
    z = np.asarray(directions, dtype=float)
    if base.ndim != 1 or z.ndim != 2 or z.shape[1] != base.size:
        raise ValueError("directions must have shape [n_probes, action_dim]")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    rows = []
    for direction in z:
        plus = np.asarray(effect_fn(base + epsilon * direction), dtype=float)
        minus = np.asarray(effect_fn(base - epsilon * direction), dtype=float)
        if plus.shape != minus.shape or plus.ndim != 1:
            raise ValueError("effect_fn must return a fixed one-dimensional effect vector")
        rows.append((plus - minus) / (2.0 * epsilon))
    return np.stack(rows, axis=0)


def estimate_effect_jacobian(
    effect_fn: Callable[[np.ndarray], np.ndarray],
    base_action: np.ndarray,
    probe_directions: np.ndarray,
    held_out_directions: np.ndarray,
    *,
    epsilon: float = 1e-4,
    max_condition_number: float = 1e6,
    max_held_out_residual: float = 0.05,
) -> tuple[np.ndarray, EffectIdentificationCertificate]:
    """Identify d(task_effect)/d(action) from black-box execution probes.

    Probe equation: Y ~= Z J^T. The estimate is J^T = pinv(Z) Y.
    """

    z = np.asarray(probe_directions, dtype=float)
    z_hold = np.asarray(held_out_directions, dtype=float)
    if z.ndim != 2 or z_hold.ndim != 2 or z.shape[1] != z_hold.shape[1]:
        raise ValueError("probe and held-out directions must share action dimension")

    y = symmetric_effect_measurements(effect_fn, base_action, z, epsilon=epsilon)
    y_hold = symmetric_effect_measurements(effect_fn, base_action, z_hold, epsilon=epsilon)

    s = np.linalg.svd(z, compute_uv=False)
    tol = 0.0 if s.size == 0 else np.finfo(float).eps * max(z.shape) * s[0]
    rank = int(np.sum(s > tol))
    full_action_rank = rank == z.shape[1]
    cond = (
        float('inf')
        if not full_action_rank or s.size == 0 or s[-1] == 0
        else float(s[0] / s[-1])
    )

    jt = np.linalg.pinv(z) @ y
    jac = jt.T

    train_pred = z @ jac.T
    hold_pred = z_hold @ jac.T

    train_denom = float(np.linalg.norm(y, ord='fro'))
    hold_denom = float(np.linalg.norm(y_hold, ord='fro'))
    train_res = float(np.linalg.norm(train_pred - y, ord='fro'))
    hold_res = float(np.linalg.norm(hold_pred - y_hold, ord='fro'))
    if train_denom > 0:
        train_res /= train_denom
    if hold_denom > 0:
        hold_res /= hold_denom

    cert = EffectIdentificationCertificate(
        probe_count=int(z.shape[0]),
        action_dim=int(z.shape[1]),
        effect_dim=int(jac.shape[0]),
        probe_rank=rank,
        full_action_rank=bool(full_action_rank),
        probe_condition_number=cond,
        training_residual=train_res,
        held_out_residual=hold_res,
        locally_valid=(
            full_action_rank
            and cond <= max_condition_number
            and hold_res <= max_held_out_residual
        ),
    )
    return jac, cert
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CentralEstimate:
    jacobian: np.ndarray
    symmetry_residual: np.ndarray
    epsilon: float


def estimate_single_support_central(query, *, support_dim: int, epsilon: float, randomness_seed: int):
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    zero = np.zeros((1, support_dim), dtype=float)
    baseline = np.asarray(query(zero, randomness_seed), dtype=float)
    if baseline.ndim != 2:
        raise ValueError("query must return [H, D_action]")
    horizon, action_dim = baseline.shape
    jacobian = np.zeros((horizon, 1, action_dim, support_dim), dtype=float)
    symmetry = np.zeros((horizon, support_dim), dtype=float)
    for q in range(support_dim):
        plus_delta = np.zeros((1, support_dim), dtype=float)
        minus_delta = np.zeros((1, support_dim), dtype=float)
        plus_delta[0, q] = epsilon
        minus_delta[0, q] = -epsilon
        plus = np.asarray(query(plus_delta, randomness_seed), dtype=float)
        minus = np.asarray(query(minus_delta, randomness_seed), dtype=float)
        d_plus = (plus - baseline) / epsilon
        d_minus = (baseline - minus) / epsilon
        central = 0.5 * (d_plus + d_minus)
        jacobian[:, 0, :, q] = central
        symmetry[:, q] = np.linalg.norm(d_plus - d_minus, axis=-1) / np.maximum(
            np.linalg.norm(central, axis=-1), 1e-12
        )
    return CentralEstimate(jacobian, symmetry, float(epsilon))


def scale_curvature(small: CentralEstimate, large: CentralEstimate) -> np.ndarray:
    if small.jacobian.shape != large.jacobian.shape:
        raise ValueError("central estimates must have matching shapes")
    diff = large.jacobian - small.jacobian
    num = np.sqrt(np.sum(diff * diff, axis=(1, 2, 3)))
    den = np.sqrt(np.sum(small.jacobian * small.jacobian, axis=(1, 2, 3)))
    return num / np.maximum(den, 1e-12)

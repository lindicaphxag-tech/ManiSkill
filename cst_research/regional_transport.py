from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

import numpy as np


class RegionalStatus(str, Enum):
    EXACT_ON_SAMPLES = "exact_on_samples"
    APPROXIMATE_ON_SAMPLES = "approximate_on_samples"
    INCONSISTENT = "inconsistent"


@dataclass(frozen=True)
class LinearizationSample:
    """One source/target local closed-loop linearization at a declared point."""

    point: np.ndarray
    source_A: np.ndarray
    source_B: np.ndarray
    target_A: np.ndarray
    target_B: np.ndarray


@dataclass(frozen=True)
class RegionalTransportCertificate:
    status: RegionalStatus
    K_state: np.ndarray
    K_action: np.ndarray
    per_sample_relative_residual: np.ndarray
    max_relative_residual: float
    mean_relative_residual: float
    worst_sample_index: int
    worst_unmatched_direction: np.ndarray
    selected_sample_indices: tuple[int, ...]
    reason: str


@dataclass(frozen=True)
class CEGISTrace:
    selected_sample_indices: tuple[int, ...]
    max_residual_history: tuple[float, ...]
    converged: bool
    iterations: int
    certificate: RegionalTransportCertificate


def _as_matrix(value: np.ndarray, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must be a non-empty matrix")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _validate_samples(samples: Sequence[LinearizationSample]):
    if not samples:
        raise ValueError("at least one linearization sample is required")

    first = samples[0]
    A_s0 = _as_matrix(first.source_A, "source_A")
    B_s0 = _as_matrix(first.source_B, "source_B")
    A_t0 = _as_matrix(first.target_A, "target_A")
    B_t0 = _as_matrix(first.target_B, "target_B")
    n = A_s0.shape[0]
    if A_s0.shape != (n, n) or A_t0.shape != (n, n):
        raise ValueError("A matrices must be square and share one state dimension")
    if B_s0.shape[0] != n or B_t0.shape[0] != n:
        raise ValueError("B matrices must map into the shared state dimension")
    source_action_dim = B_s0.shape[1]
    target_action_dim = B_t0.shape[1]

    for idx, sample in enumerate(samples):
        A_s = _as_matrix(sample.source_A, f"source_A[{idx}]")
        B_s = _as_matrix(sample.source_B, f"source_B[{idx}]")
        A_t = _as_matrix(sample.target_A, f"target_A[{idx}]")
        B_t = _as_matrix(sample.target_B, f"target_B[{idx}]")
        if A_s.shape != (n, n) or A_t.shape != (n, n):
            raise ValueError("all samples must share the state dimension")
        if B_s.shape != (n, source_action_dim):
            raise ValueError("all samples must share the source action dimension")
        if B_t.shape != (n, target_action_dim):
            raise ValueError("all samples must share the target action dimension")

    return n, source_action_dim, target_action_dim


def _demand(sample: LinearizationSample) -> np.ndarray:
    return np.concatenate(
        [
            np.asarray(sample.source_A, dtype=float)
            - np.asarray(sample.target_A, dtype=float),
            np.asarray(sample.source_B, dtype=float),
        ],
        axis=1,
    )


def _residual_for_adapter(
    sample: LinearizationSample,
    adapter: np.ndarray,
) -> tuple[float, np.ndarray]:
    D = _demand(sample)
    B_t = np.asarray(sample.target_B, dtype=float)
    residual = D - B_t @ adapter
    scale = max(float(np.linalg.norm(D, ord=2)), 1.0)
    relative = float(np.linalg.norm(residual, ord=2) / scale)
    if np.linalg.norm(residual) > 0:
        _, _, vh = np.linalg.svd(residual, full_matrices=False)
        witness_input = vh[0]
        unmatched = residual @ witness_input
        norm = float(np.linalg.norm(unmatched))
        direction = unmatched / norm if norm > 0 else np.zeros(residual.shape[0])
    else:
        direction = np.zeros(residual.shape[0])
    return relative, direction


def synthesize_shared_regional_adapter(
    samples: Sequence[LinearizationSample],
    *,
    selected_sample_indices: Sequence[int] | None = None,
    exact_rtol: float = 1e-10,
    approximate_relative_tolerance: float = 5e-2,
) -> RegionalTransportCertificate:
    """Fit one stateful adapter shared by multiple local linearizations.

    Each sample may admit an exact point-wise adapter while the collection does
    not admit any *single* adapter.  This routine exposes that regional
    inconsistency instead of silently switching converters per state.
    """
    samples = list(samples)
    n, _, _ = _validate_samples(samples)
    if selected_sample_indices is None:
        selected = tuple(range(len(samples)))
    else:
        selected = tuple(int(i) for i in selected_sample_indices)
        if not selected:
            raise ValueError("selected_sample_indices must not be empty")
        if min(selected) < 0 or max(selected) >= len(samples):
            raise IndexError("selected sample index out of range")

    B_stack = np.vstack(
        [np.asarray(samples[i].target_B, dtype=float) for i in selected]
    )
    D_stack = np.vstack([_demand(samples[i]) for i in selected])
    adapter = np.linalg.pinv(B_stack, rcond=exact_rtol) @ D_stack

    residuals = []
    directions = []
    for sample in samples:
        residual, direction = _residual_for_adapter(sample, adapter)
        residuals.append(residual)
        directions.append(direction)
    residuals_array = np.asarray(residuals)
    worst = int(np.argmax(residuals_array))
    max_residual = float(residuals_array[worst])

    if max_residual <= exact_rtol:
        status = RegionalStatus.EXACT_ON_SAMPLES
        reason = "one stateful adapter reproduces every sampled local closed-loop demand"
    elif max_residual <= approximate_relative_tolerance:
        status = RegionalStatus.APPROXIMATE_ON_SAMPLES
        reason = "one adapter fits all sampled demands within the declared tolerance"
    else:
        status = RegionalStatus.INCONSISTENT
        reason = (
            "the sampled local closed-loop demands do not admit one shared "
            "adapter within the declared tolerance"
        )

    return RegionalTransportCertificate(
        status=status,
        K_state=adapter[:, :n],
        K_action=adapter[:, n:],
        per_sample_relative_residual=residuals_array,
        max_relative_residual=max_residual,
        mean_relative_residual=float(np.mean(residuals_array)),
        worst_sample_index=worst,
        worst_unmatched_direction=np.asarray(directions[worst]),
        selected_sample_indices=selected,
        reason=reason,
    )


def counterexample_guided_regional_synthesis(
    samples: Sequence[LinearizationSample],
    *,
    seed_sample_index: int = 0,
    tolerance: float = 5e-2,
    exact_rtol: float = 1e-10,
    max_iterations: int | None = None,
) -> CEGISTrace:
    """Counterexample-guided synthesis over a frozen pool of linearizations.

    The procedure begins from one declared sample, fits a shared adapter, scans
    the frozen pool, and adds the worst violating sample.  It stops when all
    pool samples satisfy the tolerance or every sample has become a
    counterexample constraint.

    This is a finite-pool certificate, not a continuous-region proof.
    """
    samples = list(samples)
    _validate_samples(samples)
    if seed_sample_index < 0 or seed_sample_index >= len(samples):
        raise IndexError("seed_sample_index out of range")
    if tolerance < 0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")
    if max_iterations is None:
        max_iterations = len(samples)
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    selected = [int(seed_sample_index)]
    history = []
    certificate = None

    for _ in range(max_iterations):
        certificate = synthesize_shared_regional_adapter(
            samples,
            selected_sample_indices=selected,
            exact_rtol=exact_rtol,
            approximate_relative_tolerance=tolerance,
        )
        history.append(certificate.max_relative_residual)
        if certificate.max_relative_residual <= tolerance:
            return CEGISTrace(
                selected_sample_indices=tuple(selected),
                max_residual_history=tuple(history),
                converged=True,
                iterations=len(history),
                certificate=certificate,
            )

        worst = certificate.worst_sample_index
        if worst in selected:
            break
        selected.append(worst)
        if len(selected) == len(samples):
            # One final fit with the entire frozen counterexample set.
            certificate = synthesize_shared_regional_adapter(
                samples,
                selected_sample_indices=selected,
                exact_rtol=exact_rtol,
                approximate_relative_tolerance=tolerance,
            )
            history.append(certificate.max_relative_residual)
            break

    assert certificate is not None
    return CEGISTrace(
        selected_sample_indices=tuple(selected),
        max_residual_history=tuple(history),
        converged=bool(certificate.max_relative_residual <= tolerance),
        iterations=len(history),
        certificate=certificate,
    )

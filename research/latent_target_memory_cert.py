"""Minimax transport with uncertain target-controller memory (standard-library only).

This is a *commanded-target* certificate, not a physical end-effector,
collision, actuator-tracking or task-completion safety certificate.

Assumptions:
 - target uses an additive position command: commanded_next = previous_target + command
 - previous_target is *independently bounded* in an attested axis-aligned box
 - command has independently audited physical bounds
 - all quantities share a known Cartesian frame and physical length unit
 - no unmodeled output clipping or hidden action transform
Under exactly these assumptions the robust infinity-norm minimax
problem has a closed-form solution. Rotation / SE(3) is NOT certified.

See research/LATENT_MEMORY_MINIMAX_CERTIFICATE_V1.md for proof,
counterexamples and limitations.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Sequence


class Verdict(str, Enum):
    AUTHORIZE_COMMANDED_TARGET = "AUTHORIZE_COMMANDED_TARGET"
    REFUSE_GEOMETRICALLY_IMPOSSIBLE = "REFUSE_GEOMETRICALLY_IMPOSSIBLE"
    REFUSE_UNTRUSTED_MEMORY = "REFUSE_UNTRUSTED_MEMORY"
    REFUSE_STALE_MEMORY = "REFUSE_STALE_MEMORY"
    REFUSE_UNVERIFIED_CONTROLLER = "REFUSE_UNVERIFIED_CONTROLLER"


@dataclass(frozen=True)
class TransportRequest:
    desired_target: tuple[float, ...]
    memory_lower: tuple[float, ...]
    memory_upper: tuple[float, ...]
    command_lower: tuple[float, ...]
    command_upper: tuple[float, ...]
    error_budget: float
    # Attestation is a caller-supplied source declaration; independently
    # verifying sensor authority is a separate application requirement.
    trusted_memory_attestation: bool
    memory_age_steps: int
    max_memory_age_steps: int
    additive_controller_contract_verified: bool


@dataclass(frozen=True)
class TransportResult:
    verdict: Verdict
    command: tuple[float, ...] | None
    optimal_worst_case_setpoint_error: float
    unobservable_memory_radius: float
    saturation_excess: tuple[float, ...]
    active_dimension: int
    adversarial_memory_endpoint: float
    diagnosis: str

    @property
    def may_dispatch(self) -> bool:
        return self.verdict is Verdict.AUTHORIZE_COMMANDED_TARGET


def _numbers(values: Sequence[float], name: str) -> tuple[float, ...]:
    # NumPy arrays and other valid sequence types do not define scalar truth.
    # Inspect their length, never their (ambiguous) boolean interpretation.
    if len(values) == 0:
        raise ValueError(f"{name} must be nonempty")
    out = tuple(float(v) for v in values)
    if not all(isfinite(v) for v in out):
        raise ValueError(f"{name} contains non-finite coordinates")
    return out


def certify_box_memory_transport(
    request: TransportRequest, *, numerical_guard: float = 1e-12
) -> TransportResult:
    """Compute a minimax command and refuse when no robust solution exists.

    For coordinate i, memory m_i ∈ [L_i, H_i] and u_i ∈ [a_i, b_i],
    the optimal command is u_i* = clip(d_i - (L_i+H_i)/2, a_i, b_i).

    The exact mathematical min-max error is:
      E* = max_i ((H_i-L_i)/2 + dist(d_i-(L_i+H_i)/2,[a_i,b_i])).

    This includes *all* target-memory possibilities (not an average
    correction). If E* > budget, NO box-bounded command can satisfy
    the requested commanded-target accuracy. The adversarial endpoint
    supplies a concrete witness against the returned candidate; the
    minimax formula supplies the global impossibility lower bound.

    Fails closed on missing/future/stale provenance or an unverified
    additive controller contract. No floating-point boundary equality
    is automatically authorized.
    """
    d = _numbers(request.desired_target, "desired_target")
    lo = _numbers(request.memory_lower, "memory_lower")
    hi = _numbers(request.memory_upper, "memory_upper")
    cl = _numbers(request.command_lower, "command_lower")
    ch = _numbers(request.command_upper, "command_upper")
    n = len(d)
    if any(len(x) != n for x in (lo, hi, cl, ch)):
        raise ValueError("All controller vectors must have the same dimension")
    if any(a > b for a, b in zip(lo, hi)):
        raise ValueError("Memory-box lower endpoint exceeds upper endpoint")
    if any(a > b for a, b in zip(cl, ch)):
        raise ValueError("Action-box lower endpoint exceeds upper endpoint")
    if not isfinite(request.error_budget) or request.error_budget < 0:
        raise ValueError("error_budget must be finite and nonnegative")
    if not isfinite(numerical_guard) or numerical_guard <= 0:
        raise ValueError("Numerical guard must be positive and finite")
    if isinstance(request.memory_age_steps, bool) or not isinstance(
        request.memory_age_steps, int
    ) or request.memory_age_steps < 0:
        raise ValueError("Invalid memory_age_steps")
    if isinstance(request.max_memory_age_steps, bool) or not isinstance(
        request.max_memory_age_steps, int
    ) or request.max_memory_age_steps < 0:
        raise ValueError("Invalid max_memory_age_steps")

    commands: list[float] = []
    residuals: list[float] = []
    excesses: list[float] = []
    radii: list[float] = []
    for desired, low, high, min_action, max_action in zip(d, lo, hi, cl, ch):
        # Prefer low + (high-low)/2 to avoid overflow of low + high.
        radius = (high - low) / 2.0
        center = low + radius
        target_increment = desired - center
        physical_command = min(max(target_increment, min_action), max_action)
        excess = abs(target_increment - physical_command)
        residual = radius + excess
        if not all(isfinite(v) for v in (center, radius, target_increment,
                                         physical_command, excess, residual)):
            raise ValueError("Intermediate numeric overflow: refuse")
        radii.append(radius)
        excesses.append(excess)
        residuals.append(residual)
        commands.append(physical_command)

    worst_dimension = max(range(n), key=lambda i: residuals[i])
    cand = commands[worst_dimension]
    endpoint = (
        lo[worst_dimension]
        if abs(lo[worst_dimension] + cand - d[worst_dimension])
        >= abs(hi[worst_dimension] + cand - d[worst_dimension])
        else hi[worst_dimension]
    )
    optimal = max(residuals)
    radius = max(radii)
    diagnostic = (
        f"Minimax commanded-target error={optimal:.8g}; "
        f"unobservable memory radius={radius:.8g}; "
        f"active axis={worst_dimension}. "
        "Certified only for a verified additive target-position controller."
    )

    if not request.additive_controller_contract_verified:
        verdict = Verdict.REFUSE_UNVERIFIED_CONTROLLER
    elif not request.trusted_memory_attestation:
        verdict = Verdict.REFUSE_UNTRUSTED_MEMORY
    elif request.memory_age_steps > request.max_memory_age_steps:
        verdict = Verdict.REFUSE_STALE_MEMORY
    elif optimal + numerical_guard > request.error_budget:
        verdict = Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE
    else:
        verdict = Verdict.AUTHORIZE_COMMANDED_TARGET

    return TransportResult(
        verdict=verdict,
        command=tuple(commands) if verdict is Verdict.AUTHORIZE_COMMANDED_TARGET else None,
        optimal_worst_case_setpoint_error=optimal,
        unobservable_memory_radius=radius,
        saturation_excess=tuple(excesses),
        active_dimension=worst_dimension,
        adversarial_memory_endpoint=endpoint,
        diagnosis=diagnostic,
    )


def unavoidable_indistinguishable_history_error(
    memory_a: Sequence[float], memory_b: Sequence[float]
) -> float:
    """Worst-case setpoint-error lower bound for one action under two histories.

    If two hidden previous targets m_A, m_B have identical public EE
    observations and the same policy request, any observation-only
    command must serve BOTH. Triangle inequality yields a lower bound
    ||m_A - m_B||_infinity / 2 before any saturation is considered.
    """
    a = _numbers(memory_a, "memory_a")
    b = _numbers(memory_b, "memory_b")
    if len(a) != len(b):
        raise ValueError("Hidden histories must share physical dimensions")
    return max(abs(x - y) for x, y in zip(a, b)) / 2.0

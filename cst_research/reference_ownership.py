from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ReferenceOwnershipWitness:
    """Witness that a memoryless adapter cannot erase hidden target history.

    ManiSkill PDJointPosController implements:

      use_delta=True, use_target=False:
          goal = current_qpos + delta

      use_delta=True, use_target=True:
          goal = previous_target_qpos + delta

    If two target-controller histories have the same policy-visible current
    state and receive the same memoryless adapted action, their produced goals
    differ by the hidden target-state difference.  They therefore cannot both
    equal the same source goal unless the hidden target states coincide.
    """

    target_state_a: np.ndarray
    target_state_b: np.ndarray
    target_state_gap: np.ndarray
    gap_norm: float
    minimax_memoryless_residual_lower_bound: float
    stateful_action_a: np.ndarray
    stateful_action_b: np.ndarray
    source_goal: np.ndarray


def certify_target_reference_ownership(
    *,
    current_qpos: np.ndarray,
    source_delta: np.ndarray,
    target_state_a: np.ndarray,
    target_state_b: np.ndarray,
) -> ReferenceOwnershipWitness:
    """Construct a two-history impossibility witness.

    The source controller is current-relative:
        g = q + d.

    The target controller is previous-target-relative:
        g_i = r_i + v_i.

    Exact stateful transport requires:
        v_i = g - r_i.

    A memoryless adapter that receives the same (q, d) in both histories must
    output one shared v.  The two target goals then remain separated by
    r_a-r_b.  By the triangle inequality, at least one history has residual
    >= ||r_a-r_b|| / 2 from the common desired goal.
    """
    q = np.asarray(current_qpos, dtype=float)
    d = np.asarray(source_delta, dtype=float)
    r_a = np.asarray(target_state_a, dtype=float)
    r_b = np.asarray(target_state_b, dtype=float)

    if q.ndim != 1 or d.shape != q.shape or r_a.shape != q.shape or r_b.shape != q.shape:
        raise ValueError("all joint vectors must be equal-shape 1D arrays")
    for name, value in (
        ("current_qpos", q),
        ("source_delta", d),
        ("target_state_a", r_a),
        ("target_state_b", r_b),
    ):
        if not np.all(np.isfinite(value)):
            raise ValueError(f"{name} must be finite")

    source_goal = q + d
    gap = r_a - r_b
    gap_norm = float(np.linalg.norm(gap))

    return ReferenceOwnershipWitness(
        target_state_a=r_a,
        target_state_b=r_b,
        target_state_gap=gap,
        gap_norm=gap_norm,
        minimax_memoryless_residual_lower_bound=0.5 * gap_norm,
        stateful_action_a=source_goal - r_a,
        stateful_action_b=source_goal - r_b,
        source_goal=source_goal,
    )


def target_relative_goal(previous_target_qpos: np.ndarray, delta: np.ndarray) -> np.ndarray:
    previous_target_qpos = np.asarray(previous_target_qpos, dtype=float)
    delta = np.asarray(delta, dtype=float)
    if previous_target_qpos.shape != delta.shape:
        raise ValueError("shape mismatch")
    return previous_target_qpos + delta

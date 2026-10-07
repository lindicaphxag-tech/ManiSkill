"""Exact PushT state capture/restore shared by real-policy DEC probes.

Protocol is source-aligned with the already-published Diffusion CASJ evidence:
reset wrapper -> rebuild Pymunk Space -> restore all dynamic body fields ->
reindex shapes -> verify exact readback before querying the policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


STATE_RESTORE_PROTOCOL = "reset-fresh-space-exact-readback-v1"


@dataclass(frozen=True)
class PushTSnapshot:
    agent_position: np.ndarray
    agent_velocity: np.ndarray
    block_position: np.ndarray
    block_angle: float
    block_velocity: np.ndarray
    block_angular_velocity: float

    def shifted_block(self, delta_xy: np.ndarray, delta_angle: float = 0.0) -> "PushTSnapshot":
        return PushTSnapshot(
            agent_position=self.agent_position.copy(),
            agent_velocity=self.agent_velocity.copy(),
            block_position=self.block_position + np.asarray(delta_xy, dtype=np.float64),
            block_angle=float(self.block_angle + delta_angle),
            block_velocity=self.block_velocity.copy(),
            block_angular_velocity=float(self.block_angular_velocity),
        )


def _vec2(value: Any) -> np.ndarray:
    return np.asarray([value[0], value[1]], dtype=np.float64)


def capture_snapshot(env: Any) -> PushTSnapshot:
    u = env.unwrapped
    return PushTSnapshot(
        agent_position=_vec2(u.agent.position),
        agent_velocity=_vec2(u.agent.velocity),
        block_position=_vec2(u.block.position),
        block_angle=float(u.block.angle),
        block_velocity=_vec2(u.block.velocity),
        block_angular_velocity=float(u.block.angular_velocity),
    )


def restore_snapshot(env: Any, snapshot: PushTSnapshot) -> None:
    env.reset(seed=0)
    u = env.unwrapped
    rebuild = getattr(u, "_setup", None)
    if not callable(rebuild):
        raise RuntimeError("unsupported gym-pusht state API: missing _setup")
    rebuild()

    u.agent.position = snapshot.agent_position.tolist()
    u.agent.velocity = snapshot.agent_velocity.tolist()
    u.block.angle = float(snapshot.block_angle)
    u.block.position = snapshot.block_position.tolist()
    u.block.velocity = snapshot.block_velocity.tolist()
    u.block.angular_velocity = float(snapshot.block_angular_velocity)
    u.space.reindex_shapes_for_body(u.agent)
    u.space.reindex_shapes_for_body(u.block)
    u.n_contact_points = 0
    if hasattr(u, "_last_action"):
        u._last_action = None

    restored = capture_snapshot(env)
    for name in ("agent_position", "agent_velocity", "block_position", "block_velocity"):
        expected = getattr(snapshot, name)
        observed = getattr(restored, name)
        if not np.array_equal(observed, expected):
            # Do not silently relax exact restoration: prospective bank seeds,
            # perturbations, and decision thresholds remain frozen. This detail
            # distinguishes invalid/non-finite states from float round-trip drift
            # and helps attribute source-level rather than method-level failures.
            delta = observed - expected
            raise RuntimeError(
                f"PushT exact restore mismatch in {name}: "
                f"expected={expected.tolist()!r}, "
                f"observed={observed.tolist()!r}, "
                f"delta={delta.tolist()!r}, "
                f"expected_finite={bool(np.isfinite(expected).all())}, "
                f"observed_finite={bool(np.isfinite(observed).all())}"
            )
    if restored.block_angle != snapshot.block_angle:
        raise RuntimeError("PushT exact restore mismatch in block_angle")
    if restored.block_angular_velocity != snapshot.block_angular_velocity:
        raise RuntimeError("PushT exact restore mismatch in block_angular_velocity")

    elapsed = getattr(env, "_elapsed_steps", 0)
    if elapsed not in (None, 0):
        raise RuntimeError(f"PushT wrapper counter not reset: {elapsed}")

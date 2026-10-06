"""Minimal external adapter for DEC/locality replication.

Replace query() with one frozen-policy/controller call.

IMPORTANT:
- The input delta is a normalized physical-support perturbation.
- The return value must be a canonical physical command, not an arbitrary raw
  action representation. If your policy/controller uses a different action
  chart, perform the semantic/controller lift inside query().
- The same seed must reproduce the same stochastic policy sample for +delta and
  -delta whenever paired randomness is supported.
"""

from __future__ import annotations

import numpy as np


SUPPORT_DIM = 3

PROVENANCE = {
    "producer": "replace-me",
    "source_repo": "https://github.com/replace/me",
    "source_commit": "replace-with-immutable-commit",
    "policy_family": "replace-me",
    "checkpoint": "replace-with-immutable-checkpoint",
    "task": "replace-me",
    "controller_representation": "replace-me",
    "support_chart": "replace-me",
}

REPLICATE_SEEDS = (123, 456, 789, 101112, 131415)


def query(normalized_support_delta: np.ndarray, seed: int) -> np.ndarray:
    """Return one canonical physical command from the frozen policy stack."""
    raise NotImplementedError("connect a real frozen policy/controller here")

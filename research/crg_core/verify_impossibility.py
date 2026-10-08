"""Arithmetic-only, optimizer-independent robust CRG impossibility check.

The claim and witness must be supplied from SEPARATE sources. Checking the
support-function inequality does not authenticate the physical map, the
operator-norm uncertainty bound, or the producer's identity.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from math import isfinite
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class ProofCheck:
    arithmetic_witness_valid: bool
    separation_margin: float | None
    external_experiment_verified: bool
    reason: str


def check_robust_impossibility(
    physical_map: np.ndarray,
    target: np.ndarray,
    normal: np.ndarray,
    *,
    certified_radius: float,
    operator_error_bound: float,
    trusted_residual_tolerance: float,
    minimum_margin: float = 1e-9,
) -> ProofCheck:
    """Check n^T d - r(||G_hat^T n|| + epsilon) > tau for ||n||=1.

    A successful result is CONDITIONAL on an externally justified
    ||G_true-G_hat||_2 <= epsilon and certified support radius r.
    """

    G = np.asarray(physical_map, dtype=float)
    d = np.asarray(target, dtype=float)
    n = np.asarray(normal, dtype=float)
    scalars = (
        certified_radius,
        operator_error_bound,
        trusted_residual_tolerance,
        minimum_margin,
    )
    if any(not isfinite(float(x)) or float(x) < 0 for x in scalars):
        return ProofCheck(False, None, False, "invalid nonnegative trusted parameters")
    if (
        G.ndim != 2
        or d.ndim != 1
        or n.ndim != 1
        or G.shape[0] != d.size
        or n.size != d.size
        or not G.size
    ):
        return ProofCheck(False, None, False, "invalid physical-map dimensions")
    if not (np.isfinite(G).all() and np.isfinite(d).all() and np.isfinite(n).all()):
        return ProofCheck(False, None, False, "nonfinite physical data")
    if not np.isclose(np.linalg.norm(n), 1.0, atol=1e-10, rtol=0):
        return ProofCheck(False, None, False, "separation normal is not unit length")

    robust_support = certified_radius * (
        np.linalg.norm(G.T @ n) + operator_error_bound
    )
    margin = float(n @ d - robust_support - trusted_residual_tolerance)
    if not isfinite(margin):
        return ProofCheck(False, None, False, "nonfinite recomputed support bound")

    passed = margin > minimum_margin
    return ProofCheck(
        passed,
        margin,
        False,
        "conditional separation verified; empirical assumptions require audit"
        if passed
        else "no valid robust impossibility separation",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Independently check CRG separation arithmetic.")
    parser.add_argument("--claim", required=True, type=Path, help="Trusted CRG problem JSON")
    parser.add_argument("--witness", required=True, type=Path, help="Normal-only witness JSON")
    args = parser.parse_args()
    claim = json.loads(args.claim.read_text(encoding="utf-8"))
    witness = json.loads(args.witness.read_text(encoding="utf-8"))
    required = {
        "physical_map",
        "target",
        "certified_radius",
        "operator_error_bound",
        "residual_tolerance",
    }
    if set(claim) != required or set(witness) != {"normal"}:
        raise SystemExit("claim/witness keys invalid; require distinct trusted parameters and normal")
    result = check_robust_impossibility(
        np.asarray(claim["physical_map"], dtype=float),
        np.asarray(claim["target"], dtype=float),
        np.asarray(witness["normal"], dtype=float),
        certified_radius=claim["certified_radius"],
        operator_error_bound=claim["operator_error_bound"],
        trusted_residual_tolerance=claim["residual_tolerance"],
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.arithmetic_witness_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())

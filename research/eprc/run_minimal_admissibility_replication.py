from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np

from research.eprc.anisotropic_repairability import directional_locality_profile
from research.eprc.dec_uncertainty import estimate_dec_uncertainty
from research.eprc.local_model_admissibility import classify_local_model_admissibility
from research.eprc.locality_refinement import evaluate_locality_refinement


DEFAULT_REPLICATE_SEEDS = (123, 456, 789, 101112, 131415)


def load_adapter(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("eprc_external_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import adapter: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def central_map(query, support_dim: int, radius: float, seed: int) -> np.ndarray:
    columns = []
    for j in range(support_dim):
        direction = np.zeros(support_dim, dtype=float)
        direction[j] = radius
        plus = np.asarray(query(direction.copy(), int(seed)), dtype=float).reshape(-1)
        minus = np.asarray(query(-direction.copy(), int(seed)), dtype=float).reshape(-1)
        if plus.shape != minus.shape or plus.size == 0:
            raise ValueError("adapter query must return equal non-empty 1D physical commands")
        columns.append((plus - minus) / (2.0 * radius))
    return np.stack(columns, axis=1)


def directional_locality_payload(
    *,
    coarse: np.ndarray,
    fine_replicates: np.ndarray,
    finer_replicates: np.ndarray,
    fine_radius: float,
    finer_radius: float,
    contraction_threshold: float,
) -> dict:
    """Return JSON-safe per-support locality evidence.

    The global locality gate uses an operator norm and can reject an otherwise
    useful support chart because one coordinate is nonlocal. This companion
    record preserves that fail-closed global decision while exposing which
    physical support directions are individually supported.
    """

    fine = np.asarray(fine_replicates, dtype=float)
    finer = np.asarray(finer_replicates, dtype=float)
    if fine.ndim != 3 or finer.shape != fine.shape:
        raise ValueError("fine/finer replicates must share [n,physical,support] shape")

    fine_center = np.mean(fine, axis=0)
    finer_center = np.mean(finer, axis=0)
    profile = directional_locality_profile(
        coarse_map=np.asarray(coarse, dtype=float),
        fine_map=fine_center,
        finer_map=finer_center,
        fine_radius=fine_radius,
        finer_radius=finer_radius,
        contraction_threshold=contraction_threshold,
    )

    per_direction_stochastic = np.max(
        np.linalg.norm(finer - finer_center[None, :, :], axis=1),
        axis=0,
    )

    def finite_or_none(values: np.ndarray) -> list[float | None]:
        return [float(x) if np.isfinite(x) else None for x in values]

    return {
        "coarse_fine_drift": [float(x) for x in profile.coarse_fine_drift],
        "fine_finer_drift": [float(x) for x in profile.fine_finer_drift],
        "contraction_ratio": finite_or_none(profile.contraction_ratio),
        "stable_direction": [bool(x) for x in profile.stable_direction],
        "directional_radii": [float(x) for x in profile.directional_radii],
        "finer_stochastic_radius_per_direction": [
            float(x) for x in per_direction_stochastic
        ],
        "semantics": (
            "directional_radii are empirical first-order validity radii in the "
            "adapter's normalized physical-support chart; unstable directions "
            "are assigned radius 0 and remain fail-closed"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal external DEC/locality/admissibility replication harness."
    )
    parser.add_argument("adapter", type=Path)
    parser.add_argument("--output", type=Path, default=Path("eprc_admissibility.json"))
    parser.add_argument("--coarse-radius", type=float, default=0.5)
    parser.add_argument("--fine-radius", type=float, default=0.25)
    parser.add_argument("--finer-radius", type=float, default=0.125)
    parser.add_argument("--max-q95-radius", type=float, default=0.15)
    parser.add_argument("--contraction-threshold", type=float, default=0.75)
    args = parser.parse_args()

    adapter = load_adapter(args.adapter)
    query = getattr(adapter, "query")
    support_dim = int(getattr(adapter, "SUPPORT_DIM"))
    provenance = dict(getattr(adapter, "PROVENANCE"))
    seeds = tuple(int(x) for x in getattr(adapter, "REPLICATE_SEEDS", DEFAULT_REPLICATE_SEEDS))

    if support_dim <= 0:
        raise ValueError("SUPPORT_DIM must be positive")
    if len(seeds) < 5:
        raise ValueError("at least five replicate seeds are required")
    if not (args.coarse_radius > args.fine_radius > args.finer_radius > 0):
        raise ValueError("require coarse > fine > finer > 0")

    coarse = central_map(query, support_dim, args.coarse_radius, seeds[0])
    fine = np.stack(
        [central_map(query, support_dim, args.fine_radius, seed) for seed in seeds]
    )
    finer = np.stack(
        [central_map(query, support_dim, args.finer_radius, seed) for seed in seeds]
    )

    uncertainty = estimate_dec_uncertainty(
        fine, min_replicates=5, max_q95_radius=args.max_q95_radius
    )
    locality, _ = evaluate_locality_refinement(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        contraction_threshold=args.contraction_threshold,
        refined_trust_radius=args.finer_radius,
    )
    admissibility = classify_local_model_admissibility(
        dec_stable=uncertainty.stable,
        locality_contracting=locality.contracting,
    )
    directional = directional_locality_payload(
        coarse=coarse,
        fine_replicates=fine,
        finer_replicates=finer,
        fine_radius=args.fine_radius,
        finer_radius=args.finer_radius,
        contraction_threshold=args.contraction_threshold,
    )

    payload = {
        "status": "completed",
        "adapter_contract": (
            "query(delta, seed) returns canonical physical command; delta is in a "
            "dimensionless normalized physical-support chart"
        ),
        "provenance": provenance,
        "support_dim": support_dim,
        "replicate_seeds": list(seeds),
        "radii": {
            "coarse": args.coarse_radius,
            "fine": args.fine_radius,
            "finer": args.finer_radius,
        },
        "dec": {
            "replicate_count": uncertainty.replicate_count,
            "q95_signature_radius": uncertainty.q95_signature_radius,
            "median_signature_radius": uncertainty.median_signature_radius,
            "max_q95_radius": args.max_q95_radius,
            "stable": uncertainty.stable,
        },
        "locality": {
            "coarse_fine_drift": locality.coarse_fine_drift,
            "fine_finer_drift": locality.fine_finer_drift,
            "contraction_ratio": locality.contraction_ratio,
            "contraction_threshold": args.contraction_threshold,
            "contracting": locality.contracting,
            "finer_stochastic_radius": locality.finer_stochastic_radius,
        },
        "directional_locality": directional,
        "admissibility": {
            "state": admissibility.state.value,
            "same_scale_queries_authorized": admissibility.same_scale_queries_authorized,
            "smaller_scale_model_authorized": admissibility.smaller_scale_model_authorized,
            "repair_certificate_authorized": admissibility.repair_certificate_authorized,
            "reason": admissibility.reason,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Deterministic Monte Carlo characterization of the bounded SO(3) compiler."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from compiler import compile_uniform_geodesic, direct_single_step


def run(n_samples: int = 20_000, seed: int = 20261008) -> dict:
    rng = np.random.default_rng(seed)
    targets = Rotation.random(n_samples, random_state=rng).as_quat()
    configs = {
        "legacy_negative_rot_lower_panda": np.full(3, -0.1),
        "positive_rot_upper_panda": np.full(3, 0.1),
        "asymmetric_rot_scale": np.array([0.10, 0.08, 0.12]),
    }
    results = {}
    for name, scale in configs.items():
        one_step_errors = []
        feasible = 0
        counts = []
        compiled_errors = []
        for q in targets:
            _, err, ok = direct_single_step(q, scale)
            feasible += int(ok)
            one_step_errors.append(err)
            compiled = compile_uniform_geodesic(q, scale)
            counts.append(compiled.steps)
            compiled_errors.append(compiled.endpoint_error_rad)
        results[name] = {
            "action_scale_rad": scale.tolist(),
            "sample_count": n_samples,
            "single_step_feasible_fraction": feasible / n_samples,
            "single_step_error_rad_median": float(np.median(one_step_errors)),
            "single_step_error_rad_p95": float(np.quantile(one_step_errors, 0.95)),
            "uniform_steps_median": int(np.median(counts)),
            "uniform_steps_p95": int(np.quantile(counts, 0.95)),
            "uniform_steps_max": int(np.max(counts)),
            "compiled_endpoint_error_rad_max": float(np.max(compiled_errors)),
        }
    return {
        "method": "minimum feasible uniform subdivision of principal SO(3) geodesic",
        "seed": seed,
        "sampling": "uniform Haar rotations via scipy.spatial.transform.Rotation.random",
        "controller_model": "XYZ intrinsic Euler Rx@Ry@Rz with radial normalized-action clipping",
        "scope": "controller-target reconstruction only; no IK, dynamics, contact, or task-success claim",
        "results": results,
    }


if __name__ == "__main__":
    result = run()
    out = Path(__file__).with_name("monte_carlo_results.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

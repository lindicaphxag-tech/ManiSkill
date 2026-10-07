from __future__ import annotations

import argparse
import json
import numpy as np


def axis_rotation(axis: str, angle: np.ndarray) -> np.ndarray:
    c = np.cos(angle)
    s = np.sin(angle)
    out = np.zeros(angle.shape + (3, 3), dtype=np.float64)
    if axis == "X":
        out[..., 0, 0] = 1.0
        out[..., 1, 1] = c
        out[..., 1, 2] = -s
        out[..., 2, 1] = s
        out[..., 2, 2] = c
    elif axis == "Y":
        out[..., 1, 1] = 1.0
        out[..., 0, 0] = c
        out[..., 0, 2] = s
        out[..., 2, 0] = -s
        out[..., 2, 2] = c
    elif axis == "Z":
        out[..., 2, 2] = 1.0
        out[..., 0, 0] = c
        out[..., 0, 1] = -s
        out[..., 1, 0] = s
        out[..., 1, 1] = c
    else:
        raise ValueError(axis)
    return out


def xyz_euler_to_matrix(euler: np.ndarray) -> np.ndarray:
    euler = np.asarray(euler, dtype=np.float64)
    return (
        axis_rotation("X", euler[..., 0])
        @ axis_rotation("Y", euler[..., 1])
        @ axis_rotation("Z", euler[..., 2])
    )


def matrix_to_rotvec(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float64)
    trace = np.trace(matrix, axis1=-2, axis2=-1)
    cos_theta = np.clip((trace - 1.0) / 2.0, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    skew = np.stack(
        [
            matrix[..., 2, 1] - matrix[..., 1, 2],
            matrix[..., 0, 2] - matrix[..., 2, 0],
            matrix[..., 1, 0] - matrix[..., 0, 1],
        ],
        axis=-1,
    )
    sin_theta = np.sin(theta)
    scale = np.empty_like(theta)
    regular = np.abs(sin_theta) > 1e-8
    scale[regular] = theta[regular] / (2.0 * sin_theta[regular])
    scale[~regular] = 0.5
    return skew * scale[..., None]


def geodesic_angle(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    relative = np.swapaxes(a, -1, -2) @ b
    trace = np.trace(relative, axis1=-2, axis2=-1)
    return np.arccos(np.clip((trace - 1.0) / 2.0, -1.0, 1.0))


def run(seed: int, samples: int, bound: float) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    true_euler = rng.uniform(-bound, bound, size=(samples, 3))
    true_matrix = xyz_euler_to_matrix(true_euler)

    # Historical converter behavior: represent the same rotation by an
    # axis-angle / rotvec coordinate, then feed those three numbers into a
    # controller that interprets them as XYZ Euler coordinates.
    old_native = matrix_to_rotvec(true_matrix)
    old_matrix = xyz_euler_to_matrix(old_native)
    error = geodesic_angle(old_matrix, true_matrix)

    return {
        "seed": seed,
        "samples": samples,
        "euler_bound_rad": bound,
        "mean_error_rad": float(np.mean(error)),
        "median_error_rad": float(np.median(error)),
        "p90_error_rad": float(np.quantile(error, 0.90)),
        "p95_error_rad": float(np.quantile(error, 0.95)),
        "p99_error_rad": float(np.quantile(error, 0.99)),
        "max_error_rad": float(np.max(error)),
        "fraction_error_gt_0_05_rad": float(np.mean(error > 0.05)),
        "fraction_error_gt_0_10_rad": float(np.mean(error > 0.10)),
        "fraction_error_gt_0_20_rad": float(np.mean(error > 0.20)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--samples", type=int, default=20000)
    parser.add_argument("--bound", type=float, default=0.8)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.samples, args.bound), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

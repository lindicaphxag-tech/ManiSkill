from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import torch

from lerobot.datasets import LeRobotDatasetMetadata
from lerobot.envs.utils import preprocess_observation
from lerobot.policies import make_pre_post_processors
from lerobot.policies.vqbet import VQBeTPolicy
from lerobot.utils.constants import OBS_IMAGES, OBS_STATE

from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty


MODEL_ID = "lerobot/vqbet_pusht"
LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
SUPPORT_SCALE = np.array([16.0, 16.0, 0.08], dtype=np.float64)
PROTOCOL_ID = "pusht-block-xyt-fine-4px-4px-0.02rad-coarse-8px-8px-0.04rad-v1"


def _finite_or_raise(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise RuntimeError(f"{name} is not finite: {value}")
    return value


def main(output: Path) -> int:
    device = torch.device("cpu")
    policy = VQBeTPolicy.from_pretrained(MODEL_ID).to(device).eval()
    metadata = LeRobotDatasetMetadata("lerobot/pusht")
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config,
        MODEL_ID,
        dataset_stats=metadata.stats,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )

    if tuple(policy.config.action_feature.shape) != (2,):
        raise RuntimeError(f"unexpected PushT action shape: {policy.config.action_feature.shape}")

    env = gym.make(
        "gym_pusht/PushT-v0",
        obs_type="pixels_agent_pos",
        render_mode="rgb_array",
        observation_width=96,
        observation_height=96,
    )
    _, info0 = env.reset(seed=17)
    base_state = np.concatenate([info0["pos_agent"], info0["block_pose"]]).astype(np.float64)

    def render_state(state: np.ndarray):
        u = env.unwrapped
        u._setup()
        u._set_state(np.asarray(state, dtype=np.float64))
        return u.get_obs()

    def process_raw(raw):
        obs = preprocess_observation({k: np.asarray(v).copy() for k, v in raw.items()})
        return preprocessor(obs)

    baseline_raw = render_state(base_state)
    baseline_processed = process_raw(baseline_raw)
    baseline_processed_repeat = process_raw(baseline_raw)
    preprocess_error = 0.0
    for key in policy.config.input_features:
        if key in baseline_processed:
            err = float(
                torch.max(
                    torch.abs(baseline_processed[key] - baseline_processed_repeat[key])
                ).cpu()
            )
            preprocess_error = max(preprocess_error, err)
    if preprocess_error >= 1e-7:
        raise RuntimeError(f"non-deterministic preprocessing: {preprocess_error}")

    def history_list(curr_processed):
        n = int(policy.config.n_obs_steps)
        return [baseline_processed] * max(n - 1, 0) + [curr_processed]

    def make_batch(curr_processed):
        hist = history_list(curr_processed)
        batch = {OBS_STATE: torch.stack([h[OBS_STATE] for h in hist], dim=1)}
        image_histories = [
            torch.stack([h[key] for h in hist], dim=1)
            for key in policy.config.image_features
        ]
        batch[OBS_IMAGES] = torch.stack(image_histories, dim=2)
        return batch

    def denormalize_chunk(normalized_chunk: torch.Tensor) -> np.ndarray:
        steps = []
        for i in range(normalized_chunk.shape[1]):
            step = postprocessor(normalized_chunk[:, i])
            steps.append(step.detach().cpu().numpy()[0])
        return np.stack(steps, axis=0)

    @torch.inference_mode()
    def paired_chunk(curr_raw, randomness_seed: int) -> np.ndarray:
        curr = process_raw(curr_raw)
        batch = make_batch(curr)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(randomness_seed))
            normalized = policy.vqbet(batch, rollout=True)
        return denormalize_chunk(normalized)

    repeat_a = paired_chunk(baseline_raw, 123)
    repeat_b = paired_chunk(baseline_raw, 123)
    repeat_error = float(np.max(np.abs(repeat_a - repeat_b)))
    if repeat_error >= 1e-6:
        raise RuntimeError(f"paired VQ-BeT query is not repeatable: {repeat_error}")

    query_calls = 0

    def query_support(delta: np.ndarray, seed: int) -> np.ndarray:
        nonlocal query_calls
        changed = base_state.copy()
        changed[2:5] += np.asarray(delta, dtype=np.float64) * SUPPORT_SCALE
        query_calls += 1
        return paired_chunk(render_state(changed), seed)

    def central(epsilon: float, seed: int):
        baseline = query_support(np.zeros(3), seed)
        horizon, action_dim = baseline.shape
        jac = np.zeros((horizon, action_dim, 3), dtype=np.float64)
        symmetry = np.zeros((horizon, 3), dtype=np.float64)
        for q in range(3):
            plus_delta = np.zeros(3)
            minus_delta = np.zeros(3)
            plus_delta[q] = epsilon
            minus_delta[q] = -epsilon
            plus = query_support(plus_delta, seed)
            minus = query_support(minus_delta, seed)
            d_plus = (plus - baseline) / epsilon
            d_minus = (baseline - minus) / epsilon
            center = 0.5 * (d_plus + d_minus)
            jac[:, :, q] = center
            symmetry[:, q] = np.linalg.norm(d_plus - d_minus, axis=-1) / np.maximum(
                np.linalg.norm(center, axis=-1), 1e-12
            )
        return jac, symmetry

    t0 = time.perf_counter()
    small_j, small_sym = central(0.25, 123)
    large_j, _ = central(0.50, 123)

    # Two additional paired-RNG replicates expose stochastic DEC instability
    # without pretending that three seeds satisfy the >=5 replicate certificate.
    replicate_seeds = [123, 456, 789]
    replicate_jacobians = [
        small_j,
        central(0.25, 456)[0],
        central(0.25, 789)[0],
    ]
    flat_replicates = np.stack(
        [j.reshape(-1, j.shape[-1]) for j in replicate_jacobians],
        axis=0,
    )
    dec_uncertainty = estimate_dec_uncertainty(
        flat_replicates,
        min_replicates=5,
        max_q95_radius=0.15,
    )
    replicate_signatures = [
        contract_signature(j) for j in flat_replicates
    ]
    pairwise_dec_distances = [
        signature_distance(replicate_signatures[i], replicate_signatures[j])
        for i in range(len(replicate_signatures))
        for j in range(i + 1, len(replicate_signatures))
    ]
    elapsed = time.perf_counter() - t0

    diff = large_j - small_j
    curvature = np.linalg.norm(diff.reshape(diff.shape[0], -1), axis=1) / np.maximum(
        np.linalg.norm(small_j.reshape(small_j.shape[0], -1), axis=1), 1e-12
    )
    step_gain = np.linalg.norm(small_j.reshape(small_j.shape[0], -1), axis=1)

    report = {
        "status": "completed",
        "claim": "real frozen-policy black-box support-response evidence; not an L8 event",
        "model_id": MODEL_ID,
        "lerobot_commit": LEROBOT_COMMIT,
        "device": str(device),
        "base_state": base_state.tolist(),
        "protocol_id": PROTOCOL_ID,
        "environment_reset_seed": 17,
        "support_scale": SUPPORT_SCALE.tolist(),
        "small_epsilon": 0.25,
        "large_epsilon": 0.50,
        "fine_physical_probe": [4.0, 4.0, 0.02],
        "coarse_physical_probe": [8.0, 8.0, 0.04],
        "preprocess_repeat_max_error": _finite_or_raise("preprocess_error", preprocess_error),
        "paired_policy_repeat_max_error": _finite_or_raise("repeat_error", repeat_error),
        "logical_policy_queries": int(query_calls + 2),
        "probe_seconds": _finite_or_raise("elapsed", elapsed),
        "horizon": int(small_j.shape[0]),
        "action_dim": int(small_j.shape[1]),
        "dec": {
            "jacobian_small": small_j.tolist(),
            "max_symmetry_residual": _finite_or_raise(
                "max_symmetry_residual", np.max(small_sym)
            ),
            "mean_symmetry_residual": _finite_or_raise(
                "mean_symmetry_residual", np.mean(small_sym)
            ),
            "max_scale_curvature": _finite_or_raise(
                "max_scale_curvature", np.max(curvature)
            ),
            "mean_scale_curvature": _finite_or_raise(
                "mean_scale_curvature", np.mean(curvature)
            ),
            "per_action_step_gain": [float(x) for x in step_gain],
            "per_action_step_curvature": [float(x) for x in curvature],
            "rng_seed_replicates": replicate_seeds,
            "pairwise_seed_dec_distances": [float(x) for x in pairwise_dec_distances],
            "q95_seed_dec_radius": _finite_or_raise(
                "q95_seed_dec_radius", dec_uncertainty.q95_signature_radius
            ),
            "replicate_stability_certified": bool(dec_uncertainty.stable),
            "certification_eligible": False,
            "certification_note": (
                "This public-policy smoke uses 3 RNG-seed replicates; "
                "DEC_UNCERTAINTY requires at least 5 for a stability claim."
            ),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    env.close()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("vqbet_pusht_probe.json"),
    )
    args = parser.parse_args()
    raise SystemExit(main(args.output))

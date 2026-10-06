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


MODEL_ID = "lerobot/vqbet_pusht"
LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
SUPPORT_SCALE = np.array([20.0, 20.0, 0.15], dtype=np.float64)


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
    _, info0 = env.reset(seed=7)
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
        "support_scale": SUPPORT_SCALE.tolist(),
        "small_epsilon": 0.25,
        "large_epsilon": 0.50,
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

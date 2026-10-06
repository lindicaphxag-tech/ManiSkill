from __future__ import annotations

import json
from pathlib import Path
import time

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import torch

from lerobot.datasets import LeRobotDatasetMetadata
from lerobot.envs.utils import preprocess_observation
from lerobot.policies import make_pre_post_processors
from lerobot.policies.vqbet import VQBeTPolicy
from lerobot.utils.constants import OBS_IMAGES, OBS_STATE

from vqbet_probe_core import estimate_single_support_central, scale_curvature

MODEL_ID = "lerobot/vqbet_pusht"
LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
DEVICE = torch.device("cpu")
SUPPORT_SCALE = np.array([20.0, 20.0, 0.15], dtype=np.float64)


def main():
    torch.set_num_threads(2)
    policy = VQBeTPolicy.from_pretrained(MODEL_ID).to(DEVICE).eval()
    metadata = LeRobotDatasetMetadata("lerobot/pusht")
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config,
        MODEL_ID,
        dataset_stats=metadata.stats,
        preprocessor_overrides={"device_processor": {"device": str(DEVICE)}},
    )
    env = gym.make(
        "gym_pusht/PushT-v0",
        obs_type="pixels_agent_pos",
        render_mode="rgb_array",
        observation_width=96,
        observation_height=96,
    )
    _, info0 = env.reset(seed=7)
    base_state = np.concatenate([info0["pos_agent"], info0["block_pose"]]).astype(np.float64)

    def render_state(state):
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
    prep_error = 0.0
    for key in policy.config.input_features:
        if key in baseline_processed:
            prep_error = max(
                prep_error,
                float(torch.max(torch.abs(baseline_processed[key] - baseline_processed_repeat[key])).cpu()),
            )

    def make_batch(curr_processed):
        n = policy.config.n_obs_steps
        hist = [baseline_processed] * max(n - 1, 0) + [curr_processed]
        batch = {OBS_STATE: torch.stack([h[OBS_STATE] for h in hist], dim=1)}
        image_histories = [
            torch.stack([h[key] for h in hist], dim=1)
            for key in policy.config.image_features
        ]
        batch[OBS_IMAGES] = torch.stack(image_histories, dim=2)
        return batch

    def denormalize_chunk(normalized):
        steps = []
        for i in range(normalized.shape[1]):
            step = postprocessor(normalized[:, i])
            steps.append(step.detach().cpu().numpy()[0])
        return np.stack(steps, axis=0)

    @torch.inference_mode()
    def paired_chunk(curr_raw, seed):
        batch = make_batch(process_raw(curr_raw))
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(seed))
            normalized = policy.vqbet(batch, rollout=True)
        return denormalize_chunk(normalized)

    a = paired_chunk(baseline_raw, 123)
    b = paired_chunk(baseline_raw, 123)
    repeat_error = float(np.max(np.abs(a - b)))

    def query(support_delta, seed):
        state = base_state.copy()
        state[2:5] += np.asarray(support_delta[0], dtype=np.float64) * SUPPORT_SCALE
        return paired_chunk(render_state(state), seed)

    t0 = time.perf_counter()
    small = estimate_single_support_central(query, support_dim=3, epsilon=0.25, randomness_seed=123)
    large = estimate_single_support_central(query, support_dim=3, epsilon=0.50, randomness_seed=123)
    elapsed = time.perf_counter() - t0

    curvature = scale_curvature(small, large)
    block_norm = np.linalg.norm(small.jacobian[:, 0], axis=(1, 2))
    symmetry = np.max(small.symmetry_residual, axis=1)

    report = {
        "evidence_type": "frozen_public_policy_smoke",
        "model_id": MODEL_ID,
        "lerobot_commit": LEROBOT_COMMIT,
        "device": str(DEVICE),
        "base_state": base_state.tolist(),
        "support_scale": SUPPORT_SCALE.tolist(),
        "preprocessing_repeat_max_error": prep_error,
        "paired_repeat_max_error": repeat_error,
        "probe_seconds": elapsed,
        "small_epsilon": 0.25,
        "large_epsilon": 0.50,
        "max_block_norm": float(np.max(block_norm)),
        "median_block_norm": float(np.median(block_norm)),
        "max_symmetry_residual": float(np.max(symmetry)),
        "median_symmetry_residual": float(np.median(symmetry)),
        "max_scale_curvature": float(np.max(curvature)),
        "median_scale_curvature": float(np.median(curvature)),
        "per_action_step": [
            {
                "action_step": int(i),
                "block_norm": float(block_norm[i]),
                "symmetry_residual": float(symmetry[i]),
                "scale_curvature": float(curvature[i]),
            }
            for i in range(len(block_norm))
        ],
        "claim_boundary": "Smoke evidence only; not cross-policy DEC, repair success, or external adoption.",
    }
    out = Path("artifacts/eprc_vqbet_pusht_smoke.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if prep_error >= 1e-7:
        raise SystemExit("preprocessing is not repeatable")
    if repeat_error >= 1e-6:
        raise SystemExit("paired VQ-BeT query is not repeatable")
    if not np.isfinite(small.jacobian).all():
        raise SystemExit("non-finite action-support derivative")
    env.close()


if __name__ == "__main__":
    main()

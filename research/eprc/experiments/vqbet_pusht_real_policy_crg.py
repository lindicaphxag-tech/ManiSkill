from __future__ import annotations

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
from research.eprc.repairability_geometry import (
    certified_support_radius,
    diagnose_repairability,
    synthesize_repair,
)


MODEL_ID = "lerobot/vqbet_pusht"
LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
SUPPORT_SCALE = np.array([20.0, 20.0, 0.15], dtype=np.float64)
EPSILON = 0.25
TRUST_RADIUS = 0.50
BASE_SEED = 7
POLICY_SEEDS = (123, 124, 125)


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t_load = time.perf_counter()

    policy = VQBeTPolicy.from_pretrained(MODEL_ID).to(device).eval()
    metadata = LeRobotDatasetMetadata("lerobot/pusht")
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config,
        MODEL_ID,
        dataset_stats=metadata.stats,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )

    env = gym.make(
        "gym_pusht/PushT-v0",
        obs_type="pixels_agent_pos",
        render_mode="rgb_array",
        observation_width=96,
        observation_height=96,
    )
    _, info0 = env.reset(seed=BASE_SEED)
    base_state = np.concatenate([info0["pos_agent"], info0["block_pose"]]).astype(
        np.float64
    )

    def render_state(state: np.ndarray):
        u = env.unwrapped
        u._setup()
        u._set_state(np.asarray(state, dtype=np.float64))
        return u.get_obs()

    def process_raw(raw):
        obs = preprocess_observation(
            {k: np.asarray(v).copy() for k, v in raw.items()}
        )
        return preprocessor(obs)

    baseline_raw = render_state(base_state)
    baseline_processed = process_raw(baseline_raw)
    baseline_processed_repeat = process_raw(baseline_raw)

    preprocess_repeat_error = 0.0
    for key in policy.config.input_features:
        if key in baseline_processed:
            err = float(
                torch.max(
                    torch.abs(
                        baseline_processed[key] - baseline_processed_repeat[key]
                    )
                ).cpu()
            )
            preprocess_repeat_error = max(preprocess_repeat_error, err)
    if preprocess_repeat_error >= 1e-7:
        raise RuntimeError(
            f"non-deterministic preprocessing: {preprocess_repeat_error}"
        )

    def history_list(curr_processed):
        n = policy.config.n_obs_steps
        return [baseline_processed] * max(n - 1, 0) + [curr_processed]

    def make_vqbet_batch(curr_processed):
        hist = history_list(curr_processed)
        batch = {
            OBS_STATE: torch.stack([h[OBS_STATE] for h in hist], dim=1),
        }
        image_histories = []
        for key in policy.config.image_features:
            image_histories.append(torch.stack([h[key] for h in hist], dim=1))
        batch[OBS_IMAGES] = torch.stack(image_histories, dim=2)
        return batch

    def denormalize_chunk(normalized_chunk):
        steps = []
        for i in range(normalized_chunk.shape[1]):
            step = postprocessor(normalized_chunk[:, i])
            steps.append(step.detach().cpu().numpy()[0])
        return np.stack(steps, axis=0)

    @torch.inference_mode()
    def query(support_delta: np.ndarray, randomness_seed: int) -> np.ndarray:
        support_delta = np.asarray(support_delta, dtype=np.float64)
        if support_delta.shape != (3,):
            raise ValueError("support_delta must be shape [3]")
        state = base_state.copy()
        state[2:5] += support_delta * SUPPORT_SCALE
        curr = process_raw(render_state(state))
        batch = make_vqbet_batch(curr)

        devices = (
            [device.index if device.index is not None else 0]
            if device.type == "cuda"
            else []
        )
        with torch.random.fork_rng(devices=devices):
            torch.manual_seed(int(randomness_seed))
            if device.type == "cuda":
                torch.cuda.manual_seed_all(int(randomness_seed))
            normalized = policy.vqbet(batch, rollout=True)
        return denormalize_chunk(normalized)

    repeat_a = query(np.zeros(3), POLICY_SEEDS[0])
    repeat_b = query(np.zeros(3), POLICY_SEEDS[0])
    repeat_error = float(np.max(np.abs(repeat_a - repeat_b)))
    if repeat_error >= 1e-6:
        raise RuntimeError(f"paired RNG query is not reproducible: {repeat_error}")

    def central_jacobian(seed: int) -> tuple[np.ndarray, np.ndarray]:
        baseline = query(np.zeros(3), seed)
        j = np.zeros((2, 3), dtype=np.float64)
        symmetry = np.zeros(3, dtype=np.float64)
        for q in range(3):
            delta = np.zeros(3, dtype=np.float64)
            delta[q] = EPSILON
            plus = query(delta, seed)[0]
            minus = query(-delta, seed)[0]
            center = baseline[0]
            d_plus = (plus - center) / EPSILON
            d_minus = (center - minus) / EPSILON
            j[:, q] = 0.5 * (d_plus + d_minus)
            symmetry[q] = np.linalg.norm(d_plus - d_minus) / max(
                np.linalg.norm(j[:, q]), 1e-12
            )
        return j, symmetry

    jacobians = []
    symmetries = []
    for seed in POLICY_SEEDS:
        j, sym = central_jacobian(seed)
        jacobians.append(j)
        symmetries.append(sym)

    signatures = [contract_signature(j) for j in jacobians]
    seed_signature_distances = [
        signature_distance(signatures[0], signatures[i])
        for i in range(1, len(signatures))
    ]

    j = jacobians[0]
    nominal_action = query(np.zeros(3), POLICY_SEEDS[0])[0]
    action_low = np.asarray(env.action_space.low, dtype=np.float64)
    action_high = np.asarray(env.action_space.high, dtype=np.float64)

    radius = certified_support_radius(
        nominal_action,
        j,
        action_low,
        action_high,
        trust_radius=TRUST_RADIUS,
    )

    held_out_directions = np.array(
        [
            [1.0, 1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, -1.0],
            [1.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )
    held_out_directions /= np.linalg.norm(
        held_out_directions, axis=1, keepdims=True
    )
    held_out_magnitudes = (0.15, 0.30, 0.45)

    rows = []
    baseline_chunk = query(np.zeros(3), POLICY_SEEDS[0])
    for direction in held_out_directions:
        for magnitude in held_out_magnitudes:
            delta = direction * magnitude
            actual_chunk = query(delta, POLICY_SEEDS[0])
            actual = actual_chunk[0] - baseline_chunk[0]
            predicted = j @ delta
            rel_error = float(
                np.linalg.norm(predicted - actual)
                / max(np.linalg.norm(actual), 1e-12)
            )

            diag = diagnose_repairability(
                j,
                actual,
                certified_radius=radius.certified_radius,
            )
            synth = synthesize_repair(
                j,
                np.eye(2),
                actual,
                nominal_action=nominal_action,
                action_low=action_low,
                action_high=action_high,
                trust_radius=TRUST_RADIUS,
            )

            rows.append(
                {
                    "support_delta": delta.tolist(),
                    "actual_action_delta": actual.tolist(),
                    "linear_action_delta": predicted.tolist(),
                    "held_out_relative_error": rel_error,
                    "crg_signed_margin": diag.signed_margin,
                    "image_residual_norm": diag.image_residual_norm,
                    "minimum_required_radius": diag.minimum_required_radius,
                    "certified_radius": diag.certified_radius,
                    "synthesized_residual_norm": synth.residual_norm,
                    "separation_margin": synth.separation_margin,
                    "predicted_repairable": bool(diag.signed_margin >= 0),
                }
            )

    report = {
        "model_id": MODEL_ID,
        "lerobot_commit": LEROBOT_COMMIT,
        "device": str(device),
        "load_seconds": time.perf_counter() - t_load,
        "base_state": base_state.tolist(),
        "action_space_low": action_low.tolist(),
        "action_space_high": action_high.tolist(),
        "support_scale": SUPPORT_SCALE.tolist(),
        "epsilon": EPSILON,
        "trust_radius": TRUST_RADIUS,
        "paired_repeat_max_error": repeat_error,
        "preprocess_repeat_max_error": preprocess_repeat_error,
        "policy_seeds": list(POLICY_SEEDS),
        "jacobians_first_step": [x.tolist() for x in jacobians],
        "symmetry_residuals_first_step": [x.tolist() for x in symmetries],
        "seed_signature_distances": seed_signature_distances,
        "authority_radius": radius.authority_radius,
        "certified_radius": radius.certified_radius,
        "limiting_action_dim": radius.limiting_action_dim,
        "held_out": rows,
        "summary": {
            "median_held_out_relative_error": float(
                np.median([r["held_out_relative_error"] for r in rows])
            ),
            "max_seed_signature_distance": float(
                max(seed_signature_distances) if seed_signature_distances else 0.0
            ),
            "repairable_fraction": float(
                np.mean([r["predicted_repairable"] for r in rows])
            ),
        },
    }

    out = Path("vqbet_pusht_real_policy_crg_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

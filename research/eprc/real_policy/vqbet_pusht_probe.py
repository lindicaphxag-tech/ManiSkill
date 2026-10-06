from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import torch

from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty


MODEL_ID = "lerobot/vqbet_pusht"
MODEL_REVISION = "390e5e4c079c880b22e873dad53ecfac706bc78a"
LEROBOT_TRAINING_COMMIT = "3c0a209f9fac4d2a57617e686a7f2a2309144ba2"
SUPPORT_SCALE = np.array([20.0, 20.0, 0.15], dtype=np.float64)
IMAGE_KEY = "observation.image"
STATE_KEY = "observation.state"


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise RuntimeError(f"{name} is not finite: {value}")
    return value


def main(output: Path) -> int:
    device = torch.device("cpu")
    policy = VQBeTPolicy.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        map_location="cpu",
        strict=True,
    ).to(device).eval()

    if policy.config.mlp_hidden_dim != 1024:
        raise RuntimeError("unexpected training-runtime VQ-BeT schema")
    if tuple(policy.config.output_features["action"].shape) != (2,):
        raise RuntimeError("unexpected PushT action shape")

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
        env.reset(seed=7)
        env.unwrapped._set_state(np.asarray(state, dtype=np.float64))
        obs = env.unwrapped.get_obs()
        if not np.allclose(np.asarray(obs["agent_pos"]), state[:2], atol=1e-6):
            raise RuntimeError("support intervention changed held-fixed agent state")
        return obs

    def raw_to_policy(raw):
        image = torch.as_tensor(np.asarray(raw["pixels"]), device=device)
        if image.ndim != 3 or image.shape[-1] != 3:
            raise RuntimeError(f"unexpected PushT pixels shape: {tuple(image.shape)}")
        image = image.permute(2, 0, 1).to(torch.float32) / 255.0
        state = torch.as_tensor(np.asarray(raw["agent_pos"]), dtype=torch.float32, device=device)
        return {IMAGE_KEY: image.unsqueeze(0), STATE_KEY: state.unsqueeze(0)}

    baseline_raw = render_state(base_state)
    baseline_single = raw_to_policy(baseline_raw)

    def normalize_single(single):
        return policy.normalize_inputs({k: v.clone() for k, v in single.items()})

    baseline_norm = normalize_single(baseline_single)
    baseline_norm_repeat = normalize_single(baseline_single)
    preprocess_error = max(
        float(torch.max(torch.abs(baseline_norm[k] - baseline_norm_repeat[k])).cpu())
        for k in (IMAGE_KEY, STATE_KEY)
    )
    if preprocess_error >= 1e-7:
        raise RuntimeError(f"non-deterministic training-runtime normalization: {preprocess_error}")

    def make_batch(curr_raw):
        curr = normalize_single(raw_to_policy(curr_raw))
        n = int(policy.config.n_obs_steps)
        hist = [baseline_norm] * max(n - 1, 0) + [curr]
        state = torch.stack([h[STATE_KEY] for h in hist], dim=1)
        image = torch.stack([h[IMAGE_KEY] for h in hist], dim=1)
        return {STATE_KEY: state, "observation.images": image.unsqueeze(2)}

    @torch.inference_mode()
    def paired_chunk(curr_raw, randomness_seed: int) -> np.ndarray:
        batch = make_batch(curr_raw)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(randomness_seed))
            normalized = policy.vqbet(batch, rollout=True)[:, : policy.config.action_chunk_size]
        actions = policy.unnormalize_outputs({"action": normalized})["action"]
        return actions.detach().cpu().numpy()[0]

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
    replicate_seeds = [123, 456, 789]
    replicate_jacobians = [small_j, central(0.25, 456)[0], central(0.25, 789)[0]]
    flat_replicates = np.stack([j.reshape(-1, j.shape[-1]) for j in replicate_jacobians])
    uncertainty = estimate_dec_uncertainty(
        flat_replicates, min_replicates=5, max_q95_radius=0.15
    )
    sigs = [contract_signature(j) for j in flat_replicates]
    pairwise = [
        signature_distance(sigs[i], sigs[j])
        for i in range(len(sigs))
        for j in range(i + 1, len(sigs))
    ]
    elapsed = time.perf_counter() - t0

    curvature = np.linalg.norm(
        (large_j - small_j).reshape(small_j.shape[0], -1), axis=1
    ) / np.maximum(
        np.linalg.norm(small_j.reshape(small_j.shape[0], -1), axis=1), 1e-12
    )
    step_gain = np.linalg.norm(small_j.reshape(small_j.shape[0], -1), axis=1)

    report = {
        "status": "completed",
        "claim": "real frozen-policy black-box support-response evidence; not an L8 event",
        "policy_identity": {
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "training_runtime_commit": LEROBOT_TRAINING_COMMIT,
            "runtime_mode": "native-training-runtime",
            "schema_compatibility_shim": False,
        },
        "device": "cpu",
        "base_state": base_state.tolist(),
        "support_scale": SUPPORT_SCALE.tolist(),
        "small_epsilon": 0.25,
        "large_epsilon": 0.50,
        "preprocess_repeat_max_error": _finite("preprocess_error", preprocess_error),
        "paired_policy_repeat_max_error": _finite("repeat_error", repeat_error),
        "logical_policy_queries": int(query_calls + 2),
        "probe_seconds": _finite("elapsed", elapsed),
        "horizon": int(small_j.shape[0]),
        "action_dim": int(small_j.shape[1]),
        "dec": {
            "jacobian_small": small_j.tolist(),
            "max_symmetry_residual": _finite("max_symmetry_residual", np.max(small_sym)),
            "mean_symmetry_residual": _finite("mean_symmetry_residual", np.mean(small_sym)),
            "max_scale_curvature": _finite("max_scale_curvature", np.max(curvature)),
            "mean_scale_curvature": _finite("mean_scale_curvature", np.mean(curvature)),
            "per_action_step_gain": [float(x) for x in step_gain],
            "per_action_step_curvature": [float(x) for x in curvature],
            "rng_seed_replicates": replicate_seeds,
            "pairwise_seed_dec_distances": [float(x) for x in pairwise],
            "q95_seed_dec_radius": _finite("q95_seed_dec_radius", uncertainty.q95_signature_radius),
            "replicate_stability_certified": bool(uncertainty.stable),
            "certification_eligible": False,
            "certification_note": "Three RNG replicates are deliberately below the >=5 stability gate.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    env.close()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("vqbet_pusht_probe.json"))
    args = parser.parse_args()
    raise SystemExit(main(args.output))

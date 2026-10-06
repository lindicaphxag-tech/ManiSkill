from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import torch

from lerobot.common.envs.utils import preprocess_observation
from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy

from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty


MODEL_ID = "lerobot/vqbet_pusht"
MODEL_REVISION = "bff7190"
LEROBOT_COMMIT = "2cb0bf5d4154c8fefe03d1dca394fc5e1d778a97"
SUPPORT_SCALE = np.asarray([20.0, 20.0, 0.15], dtype=np.float64)


class HistoricalVQBeTProbe:
    def __init__(self, *, seed: int = 7) -> None:
        self.device = torch.device("cpu")
        self.seed = int(seed)
        self.policy = VQBeTPolicy.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            map_location="cpu",
        ).to(self.device).eval()
        self.env = gym.make(
            "gym_pusht/PushT-v0",
            obs_type="pixels_agent_pos",
            render_mode="rgb_array",
        )
        self.history_prefix, self.current_state, self.baseline_raw = self._capture_history()

    def _capture_history(self):
        obs, info = self.env.reset(seed=self.seed)
        history = [obs]
        n = int(self.policy.config.n_obs_steps)
        for _ in range(max(n - 1, 0)):
            hold = np.asarray(info["pos_agent"], dtype=np.float32)
            obs, _, terminated, truncated, info = self.env.step(hold)
            if terminated or truncated:
                raise RuntimeError("baseline PushT history terminated unexpectedly")
            history.append(obs)
        state = np.concatenate(
            [
                np.asarray(info["pos_agent"], dtype=np.float64),
                np.asarray(info["block_pose"], dtype=np.float64),
            ]
        )
        return history[:-1], state, history[-1]

    def _counterfactual(self, support_delta: np.ndarray):
        state = self.current_state.copy()
        state[2:5] += np.asarray(support_delta, dtype=np.float64) * SUPPORT_SCALE
        self.env.reset(seed=self.seed)
        self.env.unwrapped._set_state(state)
        obs = self.env.unwrapped.get_obs()
        if not np.allclose(obs["agent_pos"], state[:2], atol=1e-6):
            raise RuntimeError("support intervention changed held-fixed agent state")
        return obs

    def _prepare(self, obs):
        mapped = {
            "pixels": np.asarray(obs["pixels"])[None, ...],
            "agent_pos": np.asarray(obs["agent_pos"], dtype=np.float32)[None, ...],
        }
        return preprocess_observation(mapped)

    def _normalized_history_batch(self, current):
        raw_history = [*self.history_prefix, current]
        frames = [self.policy.normalize_inputs(self._prepare(obs)) for obs in raw_history]

        state = torch.stack(
            [frame["observation.state"].squeeze(0) for frame in frames],
            dim=0,
        ).unsqueeze(0)

        image_keys = list(self.policy.config.image_features)
        image_histories = [
            torch.stack(
                [frame[key].squeeze(0) for frame in frames],
                dim=0,
            ).unsqueeze(0)
            for key in image_keys
        ]
        images = torch.stack(image_histories, dim=2)

        return {
            "observation.state": state,
            "observation.images": images,
        }

    @torch.inference_mode()
    def query(self, support_delta: np.ndarray, randomness_seed: int) -> np.ndarray:
        current = self._counterfactual(support_delta)
        batch = self._normalized_history_batch(current)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(randomness_seed))
            normalized = self.policy.vqbet(batch, rollout=True)
        actions = self.policy.unnormalize_outputs({"action": normalized})["action"]
        return actions.detach().cpu().numpy()[0]

    def central_jacobian(self, *, epsilon: float, randomness_seed: int) -> tuple[np.ndarray, float]:
        cols = []
        max_symmetry_residual = 0.0
        baseline = self.query(np.zeros(3), randomness_seed)
        for j in range(3):
            delta = np.zeros(3, dtype=np.float64)
            delta[j] = epsilon
            plus = self.query(delta, randomness_seed)
            minus = self.query(-delta, randomness_seed)
            cols.append(((plus - minus) / (2.0 * epsilon)).reshape(-1))
            residual = np.linalg.norm(plus + minus - 2.0 * baseline)
            denom = max(np.linalg.norm(plus - minus), 1e-12)
            max_symmetry_residual = max(max_symmetry_residual, float(residual / denom))
        return np.stack(cols, axis=1), max_symmetry_residual

    def close(self):
        self.env.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("historical_vqbet_pusht_dec.json"),
    )
    parser.add_argument("--epsilon", type=float, default=0.25)
    args = parser.parse_args()

    t0 = time.perf_counter()
    probe = HistoricalVQBeTProbe()
    try:
        zero = np.zeros(3, dtype=np.float64)
        a = probe.query(zero, 123)
        b = probe.query(zero, 123)
        repeat_error = float(np.max(np.abs(a - b)))

        seeds = [123, 456, 789]
        results = [
            probe.central_jacobian(epsilon=args.epsilon, randomness_seed=seed)
            for seed in seeds
        ]
        jacobians = np.stack([j for j, _ in results], axis=0)
        max_symmetry = max(res for _, res in results)

        signatures = [contract_signature(j) for j in jacobians]
        pairwise = [
            signature_distance(signatures[i], signatures[j])
            for i in range(len(signatures))
            for j in range(i + 1, len(signatures))
        ]
        uncertainty = estimate_dec_uncertainty(
            jacobians,
            min_replicates=5,
            max_q95_radius=0.15,
        )
        response_norms = [
            float(np.linalg.norm(jacobians[:, :, d]))
            for d in range(jacobians.shape[2])
        ]

        report = {
            "schema": "eprc-historical-native-vqbet-v1",
            "runtime_provenance": {
                "lerobot_commit": LEROBOT_COMMIT,
                "model_id": MODEL_ID,
                "model_revision": MODEL_REVISION,
                "execution_mode": "historical-native",
            },
            "device": "cpu",
            "epsilon": float(args.epsilon),
            "support_scale": SUPPORT_SCALE.tolist(),
            "rng_seeds": seeds,
            "paired_repeat_max_abs_error": repeat_error,
            "jacobian_shape": list(jacobians.shape),
            "support_response_norms": response_norms,
            "pairwise_dec_distances": [float(x) for x in pairwise],
            "q95_dec_radius": float(uncertainty.q95_signature_radius),
            "replicate_stability_certified": bool(uncertainty.stable),
            "certification_eligible": False,
            "max_symmetry_residual": float(max_symmetry),
            "elapsed_seconds": float(time.perf_counter() - t0),
            "note": (
                "Three RNG-seed replicates are a smoke only; DEC_UNCERTAINTY "
                "requires at least five for a stability claim."
            ),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))

        if repeat_error > 1e-6:
            raise RuntimeError(
                f"paired RNG replay is not deterministic enough: {repeat_error}"
            )
        return 0
    finally:
        probe.close()


if __name__ == "__main__":
    raise SystemExit(main())

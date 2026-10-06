from __future__ import annotations

import argparse
import json
from pathlib import Path

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import torch

from lerobot.datasets import LeRobotDatasetMetadata
from lerobot.policies import make_pre_post_processors
from lerobot.policies.utils import prepare_observation_for_inference
from lerobot.policies.vqbet import VQBeTPolicy
from lerobot.utils.constants import OBS_IMAGES, OBS_STATE

from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty


MODEL_ID = "lerobot/vqbet_pusht"
DATASET_ID = "lerobot/pusht"
LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
SUPPORT_SCALE = np.asarray([20.0, 20.0, 0.15], dtype=np.float64)


class VQBeTPushTProbe:
    def __init__(self, *, seed: int = 7) -> None:
        self.device = torch.device("cpu")
        self.seed = int(seed)
        self.policy = VQBeTPolicy.from_pretrained(MODEL_ID).to(self.device).eval()
        self.policy.config.device = str(self.device)

        meta = LeRobotDatasetMetadata(DATASET_ID)
        self.preprocess, self.postprocess = make_pre_post_processors(
            self.policy.config,
            dataset_stats=meta.stats,
        )

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
            "observation.image": np.asarray(obs["pixels"]),
            "observation.state": np.asarray(obs["agent_pos"], dtype=np.float32),
        }
        frame = prepare_observation_for_inference(mapped, device=self.device)
        return self.preprocess(frame)

    def _batch(self, current):
        raw_history = [*self.history_prefix, current]
        processed = [self._prepare(x) for x in raw_history]
        state = torch.stack(
            [frame[OBS_STATE].squeeze(0) for frame in processed],
            dim=0,
        ).unsqueeze(0)
        image_histories = [
            torch.stack(
                [frame[key].squeeze(0) for frame in processed],
                dim=0,
            ).unsqueeze(0)
            for key in self.policy.config.image_features
        ]
        return {
            OBS_STATE: state,
            OBS_IMAGES: torch.stack(image_histories, dim=2),
        }

    def _postprocess_chunk(self, normalized: torch.Tensor) -> np.ndarray:
        steps = []
        for t in range(normalized.shape[1]):
            step = torch.as_tensor(self.postprocess(normalized[:, t]))
            steps.append(step.detach().cpu().numpy()[0])
        return np.stack(steps, axis=0)

    @torch.inference_mode()
    def query(self, support_delta: np.ndarray, randomness_seed: int) -> np.ndarray:
        current = self._counterfactual(support_delta)
        batch = self._batch(current)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(randomness_seed))
            normalized = self.policy.vqbet(batch, rollout=True)
        return self._postprocess_chunk(normalized)

    def central_jacobian(self, *, epsilon: float, randomness_seed: int) -> np.ndarray:
        cols = []
        for j in range(3):
            delta = np.zeros(3, dtype=np.float64)
            delta[j] = epsilon
            plus = self.query(delta, randomness_seed)
            minus = self.query(-delta, randomness_seed)
            cols.append(((plus - minus) / (2.0 * epsilon)).reshape(-1))
        return np.stack(cols, axis=1)

    def close(self):
        self.env.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("vqbet_pusht_dec_smoke.json"))
    parser.add_argument("--epsilon", type=float, default=0.25)
    args = parser.parse_args()

    probe = VQBeTPushTProbe()
    try:
        zero = np.zeros(3, dtype=np.float64)
        baseline_a = probe.query(zero, 123)
        baseline_b = probe.query(zero, 123)
        repeat_error = float(np.max(np.abs(baseline_a - baseline_b)))

        seeds = [123, 456, 789]
        jacobians = np.stack(
            [
                probe.central_jacobian(epsilon=args.epsilon, randomness_seed=seed)
                for seed in seeds
            ],
            axis=0,
        )
        signatures = [contract_signature(j) for j in jacobians]
        pairwise = [
            signature_distance(signatures[i], signatures[j])
            for i in range(len(signatures))
            for j in range(i + 1, len(signatures))
        ]

        uncertainty = estimate_dec_uncertainty(
            jacobians,
            min_replicates=5,  # deliberately impossible for this 3-seed smoke
            max_q95_radius=0.15,
        )

        response_norms = [
            float(np.linalg.norm(jacobians[:, :, d]))
            for d in range(jacobians.shape[2])
        ]
        report = {
            "schema": "eprc-public-policy-smoke-v1",
            "policy_family": "VQ-BeT",
            "model_id": MODEL_ID,
            "dataset_id": DATASET_ID,
            "lerobot_commit": LEROBOT_COMMIT,
            "device": "cpu",
            "epsilon": float(args.epsilon),
            "support_scale": SUPPORT_SCALE.tolist(),
            "randomness_seeds": seeds,
            "paired_repeat_max_abs_error": repeat_error,
            "jacobian_shape": list(jacobians.shape),
            "support_response_norms": response_norms,
            "pairwise_dec_distances": pairwise,
            "q95_dec_radius": uncertainty.q95_signature_radius,
            "replicate_stability_certified": bool(uncertainty.stable),
            "certification_eligible": False,
            "certification_note": (
                "This smoke intentionally uses only 3 randomness seeds; "
                "DEC_UNCERTAINTY requires >=5 independent replicates for a stability claim."
            ),
            "measurable_support_response": bool(max(response_norms) > 1e-8),
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

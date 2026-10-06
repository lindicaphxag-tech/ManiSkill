from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import packaging.version  # noqa: F401 - exposes packaging.version for pinned LeRobot loader
import torch

from lerobot.common.envs.utils import preprocess_observation
from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy

from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty
from research.eprc.real_policy.pusht_exact_state import (
    STATE_RESTORE_PROTOCOL,
    PushTSnapshot,
    capture_snapshot,
    restore_snapshot,
)


MODEL_ID = "lerobot/vqbet_pusht"
MODEL_REVISION = "bff7190"
LEROBOT_COMMIT = "2cb0bf5d4154c8fefe03d1dca394fc5e1d778a97"
SUPPORT_SCALE = np.asarray([16.0, 16.0, 0.08], dtype=np.float64)
PROTOCOL_ID = "pusht-block-xyt-fine-4px-4px-0.02rad-coarse-8px-8px-0.04rad-v1"
HELDOUT_PHYSICAL_DELTA = np.asarray([10.0, -6.0, 0.35], dtype=np.float64)


class HistoricalVQBeTProbe:
    def __init__(self, *, seed: int = 17) -> None:
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
        self.history_prefix, self.current_snapshot, self.baseline_raw = self._capture_history()

    def _render_snapshot(self, snapshot: PushTSnapshot):
        restore_snapshot(self.env, snapshot)
        obs = self.env.unwrapped.get_obs()
        if not np.array_equal(
            np.asarray(obs["agent_pos"], dtype=np.float64),
            snapshot.agent_position,
        ):
            raise RuntimeError("support intervention changed held-fixed agent state")
        return obs

    def _capture_history(self):
        self.env.reset(seed=self.seed)
        snapshot = capture_snapshot(self.env)
        obs = self._render_snapshot(snapshot)
        n = int(self.policy.config.n_obs_steps)
        # Match the published Diffusion warmup=0 protocol exactly: the initial
        # observation is repeated to fill the required history; no hold action
        # is executed merely to construct context.
        history_prefix = [obs] * max(n - 1, 0)
        return history_prefix, snapshot, obs

    def _counterfactual(self, support_delta: np.ndarray):
        physical = np.asarray(support_delta, dtype=np.float64) * SUPPORT_SCALE
        changed = self.current_snapshot.shifted_block(
            physical[:2], float(physical[2])
        )
        return self._render_snapshot(changed)

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
            physical_step = float(epsilon * SUPPORT_SCALE[j])
            cols.append(((plus - minus) / (2.0 * physical_step)).reshape(-1))
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
        heldout = probe.query(HELDOUT_PHYSICAL_DELTA / SUPPORT_SCALE, 123)
        heldout_first_action_response = heldout[0] - a[0]

        seeds = [123, 456, 789, 101112, 131415]
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
                "packaging_compatibility": "pyproject dependency name pyav->av only; no policy code changed",
            },
            "device": "cpu",
            "protocol_id": PROTOCOL_ID,
            "environment_reset_seed": 17,
            "state_restore_protocol": STATE_RESTORE_PROTOCOL,
            "fine_physical_probe": [4.0, 4.0, 0.02],
            "coarse_physical_probe": [8.0, 8.0, 0.04],
            "jacobian_support_units": ["pixel", "pixel", "radian"],
            "epsilon": float(args.epsilon),
            "support_scale": SUPPORT_SCALE.tolist(),
            "heldout_physical_delta": HELDOUT_PHYSICAL_DELTA.tolist(),
            "heldout_first_action_response": heldout_first_action_response.tolist(),
            "rng_seeds": seeds,
            "paired_repeat_max_abs_error": repeat_error,
            "jacobian_shape": list(jacobians.shape),
            "first_action_step_jacobian": jacobians[0, :2, :].tolist(),
            "support_response_norms": response_norms,
            "pairwise_dec_distances": [float(x) for x in pairwise],
            "q95_dec_radius": float(uncertainty.q95_signature_radius),
            "replicate_stability_certified": bool(uncertainty.stable),
            "certification_eligible": bool(uncertainty.stable),
            "max_symmetry_residual": float(max_symmetry),
            "elapsed_seconds": float(time.perf_counter() - t0),
            "note": (
                "Five RNG-seed replicates satisfy the pre-registered replicate-count gate. "
                "Certification eligibility is still determined by the frozen q95 DEC-radius threshold."
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

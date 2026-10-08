from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import packaging
from packaging import version as _packaging_version
import torch

packaging.version = _packaging_version

from lerobot.common.policies.diffusion.modeling_diffusion import DiffusionPolicy
from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy

from research.eprc.dec_uncertainty import estimate_dec_uncertainty
from research.eprc.real_policy.pusht_exact_state import (
    STATE_RESTORE_PROTOCOL,
    PushTSnapshot,
    capture_snapshot,
    restore_snapshot,
)


LEROBOT_COMMIT = "3c0a209f9fac4d2a57617e686a7f2a2309144ba2"
VQBET_ID = "lerobot/vqbet_pusht"
VQBET_REV = "390e5e4c079c880b22e873dad53ecfac706bc78a"
DIFFUSION_ID = "lerobot/diffusion_pusht"
DIFFUSION_REV = "d3d143b0342488252497853815b27ce3c0384c6b"

SUPPORT_SCALE = np.array([16.0, 16.0, 0.08], dtype=np.float64)
EPSILON = 0.125
RNG_SEEDS = (123, 456, 789)
HELDOUTS = {
    "A": np.array([4.0, -2.0, 0.02], dtype=np.float64),
    "B": np.array([-5.0, 3.0, -0.025], dtype=np.float64),
}
IMAGE_KEY = "observation.image"
STATE_KEY = "observation.state"


class PolicyProbe:
    def __init__(self, kind: str, base_raw: dict, render_snapshot):
        self.kind = kind
        self.device = torch.device("cpu")
        self.render_snapshot = render_snapshot

        if kind == "vqbet":
            self.model_id = VQBET_ID
            self.revision = VQBET_REV
            self.policy = VQBeTPolicy.from_pretrained(
                self.model_id,
                revision=self.revision,
                map_location="cpu",
                strict=True,
            ).to(self.device).eval()
        elif kind == "diffusion":
            self.model_id = DIFFUSION_ID
            self.revision = DIFFUSION_REV
            self.policy = DiffusionPolicy.from_pretrained(
                self.model_id,
                revision=self.revision,
                map_location="cpu",
                strict=True,
            ).to(self.device).eval()
        else:
            raise ValueError(kind)

        if tuple(self.policy.config.output_features["action"].shape) != (2,):
            raise RuntimeError(f"{kind}: unexpected PushT action shape")

        self.base_raw = base_raw
        self.base_norm = self._normalize_single(self._raw_to_policy(base_raw))
        self.query_count = 0

    def _raw_to_policy(self, raw):
        image = torch.as_tensor(np.asarray(raw["pixels"]), device=self.device)
        if image.ndim != 3 or image.shape[-1] != 3:
            raise RuntimeError(f"unexpected PushT pixels shape: {tuple(image.shape)}")
        image = image.permute(2, 0, 1).to(torch.float32) / 255.0
        state = torch.as_tensor(
            np.asarray(raw["agent_pos"]),
            dtype=torch.float32,
            device=self.device,
        )
        return {IMAGE_KEY: image.unsqueeze(0), STATE_KEY: state.unsqueeze(0)}

    def _normalize_single(self, single):
        return self.policy.normalize_inputs({k: v.clone() for k, v in single.items()})

    def _make_batch(self, curr_raw):
        curr = self._normalize_single(self._raw_to_policy(curr_raw))
        n = int(self.policy.config.n_obs_steps)
        hist = [self.base_norm] * max(n - 1, 0) + [curr]
        state = torch.stack([h[STATE_KEY] for h in hist], dim=1)
        image = torch.stack([h[IMAGE_KEY] for h in hist], dim=1)
        return {STATE_KEY: state, "observation.images": image.unsqueeze(2)}

    @torch.inference_mode()
    def query_first(self, raw, randomness_seed: int) -> np.ndarray:
        batch = self._make_batch(raw)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(randomness_seed))
            if self.kind == "vqbet":
                normalized = self.policy.vqbet(batch, rollout=True)[
                    :, : self.policy.config.action_chunk_size
                ]
            else:
                normalized = self.policy.diffusion.generate_actions(batch)
        action = self.policy.unnormalize_outputs({"action": normalized})["action"]
        self.query_count += 1
        return action.detach().cpu().numpy()[0, 0].astype(np.float64)

    def query_delta(
        self,
        base_snapshot: PushTSnapshot,
        normalized_support_delta: np.ndarray,
        randomness_seed: int,
    ) -> np.ndarray:
        delta = np.asarray(normalized_support_delta, dtype=np.float64)
        physical = delta * SUPPORT_SCALE
        changed = base_snapshot.shifted_block(physical[:2], float(physical[2]))
        return self.query_first(self.render_snapshot(changed), randomness_seed)

    def central_map(
        self,
        base_snapshot: PushTSnapshot,
        randomness_seed: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        baseline = self.query_delta(base_snapshot, np.zeros(3), randomness_seed)
        # Derivative with respect to the normalized / metric-whitened support chart.
        jac = np.zeros((2, 3), dtype=np.float64)
        for q in range(3):
            plus = np.zeros(3)
            minus = np.zeros(3)
            plus[q] = EPSILON
            minus[q] = -EPSILON
            a_plus = self.query_delta(base_snapshot, plus, randomness_seed)
            a_minus = self.query_delta(base_snapshot, minus, randomness_seed)
            jac[:, q] = (a_plus - a_minus) / (2.0 * EPSILON)
        return jac, baseline


def _case(
    center_map: np.ndarray,
    heldout_response: np.ndarray,
    *,
    stability_label: str,
) -> dict:
    return {
        "raw_action_jacobian": center_map.tolist(),
        "action_to_physical_jacobian": np.eye(2).tolist(),
        "physical_support_to_support_chart_jacobian": np.eye(3).tolist(),
        "support_ids": ["block_x", "block_y", "block_theta"],
        "static_representation": "absolute_xy",
        "coarse_contract_class": stability_label,
        # Secondary decision-agreement analysis is deliberately left neutral in
        # this bank. The primary frozen target is fresh held-out response geometry.
        "runtime_decision": "INCONCLUSIVE",
        "heldout_physical_response": heldout_response.tolist(),
    }


def main(reset_seed: int, output: Path) -> int:
    env = gym.make(
        "gym_pusht/PushT-v0",
        obs_type="pixels_agent_pos",
        render_mode="rgb_array",
        observation_width=96,
        observation_height=96,
    )
    env.reset(seed=int(reset_seed))
    base_snapshot = capture_snapshot(env)

    def render_snapshot(snapshot: PushTSnapshot):
        restore_snapshot(env, snapshot)
        obs = env.unwrapped.get_obs()
        if not np.array_equal(
            np.asarray(obs["agent_pos"], dtype=np.float64),
            snapshot.agent_position,
        ):
            raise RuntimeError("support intervention changed held-fixed agent state")
        return obs

    base_raw = render_snapshot(base_snapshot)
    diffusion = PolicyProbe("diffusion", base_raw, render_snapshot)
    vqbet = PolicyProbe("vqbet", base_raw, render_snapshot)

    result = {
        "schema": "eprc-cross-policy-state-v1",
        "reset_seed": int(reset_seed),
        "state_restore_protocol": STATE_RESTORE_PROTOCOL,
        "lerobot_commit": LEROBOT_COMMIT,
        "probe_epsilon": EPSILON,
        "physical_probe": (EPSILON * SUPPORT_SCALE).tolist(),
        "randomness_seeds": list(RNG_SEEDS),
        "heldouts": {k: v.tolist() for k, v in HELDOUTS.items()},
        "policies": {},
        "pairs": [],
    }

    per_policy = {}
    for name, probe in (("diffusion", diffusion), ("vqbet", vqbet)):
        maps = []
        baselines = {}
        for rng_seed in RNG_SEEDS:
            jac, baseline = probe.central_map(base_snapshot, rng_seed)
            maps.append(jac)
            baselines[int(rng_seed)] = baseline

        maps_arr = np.stack(maps)
        uncertainty = estimate_dec_uncertainty(
            maps_arr,
            min_replicates=3,
            max_q95_radius=0.15,
        )
        center = uncertainty.center_jacobian

        responses = {}
        for heldout_id, physical_delta in HELDOUTS.items():
            normalized = physical_delta / SUPPORT_SCALE
            seed_responses = []
            for rng_seed in RNG_SEEDS:
                action = probe.query_delta(base_snapshot, normalized, rng_seed)
                seed_responses.append(action - baselines[int(rng_seed)])
            responses[heldout_id] = np.mean(np.stack(seed_responses), axis=0)

        stability_label = (
            "DEC_STABLE" if uncertainty.stable else "DEC_UNSTABLE"
        )
        per_policy[name] = {
            "model_id": probe.model_id,
            "revision": probe.revision,
            "center_map": center,
            "heldout_responses": responses,
            "stability_label": stability_label,
        }
        result["policies"][name] = {
            "model_id": probe.model_id,
            "revision": probe.revision,
            "replicate_count": uncertainty.replicate_count,
            "q95_signature_radius": uncertainty.q95_signature_radius,
            "median_signature_radius": uncertainty.median_signature_radius,
            "stable": uncertainty.stable,
            "center_first_action_dec": center.tolist(),
            "query_count": probe.query_count,
        }

    for heldout_id in ("A", "B"):
        result["pairs"].append(
            {
                "pair_id": f"seed-{reset_seed}-{heldout_id}",
                "reset_seed": int(reset_seed),
                "heldout_id": heldout_id,
                "a": _case(
                    per_policy["diffusion"]["center_map"],
                    per_policy["diffusion"]["heldout_responses"][heldout_id],
                    stability_label=per_policy["diffusion"]["stability_label"],
                ),
                "b": _case(
                    per_policy["vqbet"]["center_map"],
                    per_policy["vqbet"]["heldout_responses"][heldout_id],
                    stability_label=per_policy["vqbet"]["stability_label"],
                ),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    env.close()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.reset_seed, args.output))

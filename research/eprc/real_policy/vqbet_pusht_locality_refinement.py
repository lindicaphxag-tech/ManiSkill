from __future__ import annotations

import argparse
import json
import math
import sys
import time
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

from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy

from research.eprc.linear_authority import LinearActionAuthority
from research.eprc.locality_refinement import evaluate_locality_refinement
from research.eprc.repairability_geometry import metric_whitened_support_jacobian
from research.eprc.robust_repairability import (
    RobustRepairDecision,
    robust_repair_certificate,
    robust_support_radius_linear_authority,
)
from research.eprc.real_policy.pusht_exact_state import (
    STATE_RESTORE_PROTOCOL,
    PushTSnapshot,
    capture_snapshot,
    restore_snapshot,
)

MODEL_ID = "lerobot/vqbet_pusht"
MODEL_REVISION = "390e5e4c079c880b22e873dad53ecfac706bc78a"
LEROBOT_TRAINING_COMMIT = "3c0a209f9fac4d2a57617e686a7f2a2309144ba2"
PROTOCOL_ID = "vqbet-pusht-locality-refinement-0.50-0.25-0.125-v1"
SUPPORT_SCALE = np.array([16.0, 16.0, 0.08], dtype=np.float64)
SUPPORT_METRIC = np.diag(1.0 / np.square(SUPPORT_SCALE))
FINE_EPSILON = 0.25
FINER_EPSILON = 0.125
REFINED_TRUST_RADIUS = 0.125
CONTRACTION_THRESHOLD = 0.75
RESIDUAL_TOLERANCE = 4.0
NEW_SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]

# Frozen from the fully green run 37456801175 before this prospective assay.
FROZEN_COARSE_MAP = np.array(
    [
        [1.76104736328125, -0.044677734375, 0.24493408203125],
        [3.77911376953125, -1.453033447265625, -0.40081787109375],
    ],
    dtype=np.float64,
)
FROZEN_HELDOUT_ACTION_RESPONSE = np.array(
    [-0.44964599609375, -7.718475341796875], dtype=np.float64
)


def _finite(name: str, x: float) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise RuntimeError(f"{name} is non-finite: {x}")
    return x


def main(output: Path) -> int:
    device = torch.device("cpu")
    policy = VQBeTPolicy.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        map_location="cpu",
        strict=True,
    ).to(device).eval()

    env = gym.make(
        "gym_pusht/PushT-v0",
        obs_type="pixels_agent_pos",
        render_mode="rgb_array",
        observation_width=96,
        observation_height=96,
    )
    env.reset(seed=17)
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

    def raw_to_policy(raw):
        image = torch.as_tensor(np.asarray(raw["pixels"]), device=device)
        image = image.permute(2, 0, 1).to(torch.float32) / 255.0
        state = torch.as_tensor(
            np.asarray(raw["agent_pos"]), dtype=torch.float32, device=device
        )
        return {
            "observation.image": image.unsqueeze(0),
            "observation.state": state.unsqueeze(0),
        }

    baseline_raw = render_snapshot(base_snapshot)
    baseline_single = raw_to_policy(baseline_raw)

    def normalize_single(single):
        return policy.normalize_inputs({k: v.clone() for k, v in single.items()})

    baseline_norm = normalize_single(baseline_single)

    def make_batch(curr_raw):
        curr = normalize_single(raw_to_policy(curr_raw))
        n = int(policy.config.n_obs_steps)
        hist = [baseline_norm] * max(n - 1, 0) + [curr]
        state = torch.stack([h["observation.state"] for h in hist], dim=1)
        image = torch.stack([h["observation.image"] for h in hist], dim=1)
        return {"observation.state": state, "observation.images": image.unsqueeze(2)}

    @torch.inference_mode()
    def paired_chunk(curr_raw, seed: int) -> np.ndarray:
        batch = make_batch(curr_raw)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(int(seed))
            normalized = policy.vqbet(batch, rollout=True)[
                :, : policy.config.action_chunk_size
            ]
        actions = policy.unnormalize_outputs({"action": normalized})["action"]
        return actions.detach().cpu().numpy()[0]

    baseline_action = paired_chunk(baseline_raw, 123)[0]
    action_low = np.asarray(env.action_space.low, dtype=np.float64)
    action_high = np.asarray(env.action_space.high, dtype=np.float64)
    authority = LinearActionAuthority.from_box(action_low, action_high)

    query_count = 0

    def query(delta_normalized: np.ndarray, seed: int) -> np.ndarray:
        nonlocal query_count
        physical = np.asarray(delta_normalized, dtype=np.float64) * SUPPORT_SCALE
        changed = base_snapshot.shifted_block(physical[:2], float(physical[2]))
        query_count += 1
        return paired_chunk(render_snapshot(changed), seed)

    def first_action_map(epsilon: float, seed: int) -> np.ndarray:
        base = query(np.zeros(3), seed)[0]
        j = np.zeros((2, 3), dtype=np.float64)
        for q in range(3):
            direction = np.zeros(3, dtype=np.float64)
            direction[q] = epsilon
            plus = query(direction, seed)[0]
            minus = query(-direction, seed)[0]
            derivative_normalized = (plus - minus) / (2.0 * epsilon)
            # Convert action / normalized-coordinate to action / physical unit,
            # then metric-whiten back to the common dimensionless physical chart.
            j[:, q] = derivative_normalized / SUPPORT_SCALE[q]
        return metric_whitened_support_jacobian(j, SUPPORT_METRIC)

    t0 = time.perf_counter()
    fine_maps = np.stack([first_action_map(FINE_EPSILON, s) for s in NEW_SEEDS])
    finer_maps = np.stack([first_action_map(FINER_EPSILON, s) for s in NEW_SEEDS])
    if query_count != 70:
        raise RuntimeError(f"query accounting changed: expected 70, got {query_count}")

    result, refined_uncertainty = evaluate_locality_refinement(
        coarse_map=FROZEN_COARSE_MAP,
        fine_map_replicates=fine_maps,
        finer_map_replicates=finer_maps,
        contraction_threshold=CONTRACTION_THRESHOLD,
        refined_trust_radius=REFINED_TRUST_RADIUS,
        quantile=1.0,
    )

    robust_payload = None
    terminal_runtime_action = "REPLAN_OR_RICHER_LOCAL_MODEL"
    if result.contracting:
        radius = robust_support_radius_linear_authority(
            baseline_action,
            result.refined_center,
            authority,
            epsilon_j=refined_uncertainty.epsilon_g,
            trust_radius=REFINED_TRUST_RADIUS,
        )
        cert = robust_repair_certificate(
            result.refined_center,
            FROZEN_HELDOUT_ACTION_RESPONSE,
            physical_map_uncertainty=refined_uncertainty,
            certified_radius=radius.certified_radius,
            residual_tolerance=RESIDUAL_TOLERANCE,
        )
        robust_payload = {
            "decision": cert.decision.value,
            "nominal_residual_norm": _finite(
                "nominal_residual", cert.nominal_residual_norm
            ),
            "worst_case_residual_upper": _finite(
                "worst_case_upper", cert.worst_case_residual_upper
            ),
            "best_case_residual_lower": _finite(
                "best_case_lower", cert.best_case_residual_lower
            ),
            "refined_certified_radius": _finite(
                "certified_radius", radius.certified_radius
            ),
            "reason": cert.reason,
        }
        terminal_runtime_action = {
            RobustRepairDecision.CERTIFIED_REPAIR: "REPAIR",
            RobustRepairDecision.CERTIFIED_IMPOSSIBLE: "REPLAN",
            RobustRepairDecision.INCONCLUSIVE: "REPLAN_OR_RICHER_LOCAL_MODEL",
        }[cert.decision]

    report = {
        "status": "completed",
        "claim": (
            "prospective locality-refinement mechanism witness; "
            "single-state result, not an L8 event"
        ),
        "policy_identity": {
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "training_runtime_commit": LEROBOT_TRAINING_COMMIT,
        },
        "protocol_id": PROTOCOL_ID,
        "state_restore_protocol": STATE_RESTORE_PROTOCOL,
        "environment_reset_seed": 17,
        "frozen_before_outcome": {
            "contraction_threshold": CONTRACTION_THRESHOLD,
            "coarse_epsilon": 0.50,
            "fine_epsilon": FINE_EPSILON,
            "finer_epsilon": FINER_EPSILON,
            "refined_trust_radius": REFINED_TRUST_RADIUS,
            "residual_tolerance": RESIDUAL_TOLERANCE,
            "new_seeds": NEW_SEEDS,
            "same_scale_query_budget": 35,
            "finer_scale_query_budget": 35,
            "frozen_coarse_map": FROZEN_COARSE_MAP.tolist(),
            "frozen_heldout_action_response": FROZEN_HELDOUT_ACTION_RESPONSE.tolist(),
        },
        "observed": {
            "fine_maps": fine_maps.tolist(),
            "finer_maps": finer_maps.tolist(),
            "coarse_fine_drift": _finite("d1", result.coarse_fine_drift),
            "fine_finer_drift": _finite("d2", result.fine_finer_drift),
            "contraction_ratio": _finite("q", result.contraction_ratio),
            "contracting": bool(result.contracting),
            "finer_stochastic_radius": _finite(
                "finer_stochastic_radius", result.finer_stochastic_radius
            ),
            "refined_uncertainty_radius": _finite(
                "refined_uncertainty_radius", result.refined_uncertainty_radius
            ),
            "recommended_trust_radius": result.recommended_trust_radius,
            "reason": result.reason,
            "robust_crg_after_refinement": robust_payload,
            "runtime_action": terminal_runtime_action,
            "total_new_policy_queries": query_count,
            "elapsed_seconds": _finite("elapsed", time.perf_counter() - t0),
        },
        "negative_results_retained": True,
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
        default=Path("vqbet_pusht_locality_refinement.json"),
    )
    args = parser.parse_args()
    raise SystemExit(main(args.output))

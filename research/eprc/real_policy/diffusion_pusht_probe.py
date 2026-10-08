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

from lerobot.common.policies.diffusion.modeling_diffusion import DiffusionPolicy

from research.eprc.active_minimal_certificate import plan_minimal_certificate_probes
from research.eprc.certificate_directed_probing import ProbeInformation
from research.eprc.contract_signature import contract_signature, signature_distance
from research.eprc.dec_uncertainty import estimate_dec_uncertainty
from research.eprc.evidence_action_router import route_inconclusive_certificate
from research.eprc.linear_authority import LinearActionAuthority
from research.eprc.locality_uncertainty import empirical_locality_envelope
from research.eprc.robust_repairability import (
    RobustRepairDecision,
    empirical_operator_envelope,
    robust_repair_certificate,
    robust_support_radius_linear_authority,
)
from research.eprc.repairability_geometry import metric_whitened_support_jacobian
from research.eprc.robust_repairability_witness import (
    build_robust_separation_witness,
    verify_robust_separation_witness,
)
from research.eprc.real_policy.pusht_exact_state import (
    STATE_RESTORE_PROTOCOL,
    PushTSnapshot,
    capture_snapshot,
    restore_snapshot,
)


MODEL_ID = "lerobot/diffusion_pusht"
MODEL_REVISION = "d3d143b0342488252497853815b27ce3c0384c6b"
LEROBOT_TRAINING_COMMIT = "3c0a209f9fac4d2a57617e686a7f2a2309144ba2"
SUPPORT_SCALE = np.array([16.0, 16.0, 0.08], dtype=np.float64)
SUPPORT_METRIC = np.diag(1.0 / np.square(SUPPORT_SCALE))
PROTOCOL_ID = "pusht-block-xyt-fine-4px-4px-0.02rad-coarse-8px-8px-0.04rad-v1"
HELDOUT_PHYSICAL_DELTA = np.array([10.0, -6.0, 0.35], dtype=np.float64)
IMAGE_KEY = "observation.image"
STATE_KEY = "observation.state"
FINE_EPSILON = 0.25
COARSE_EPSILON = 0.50
ROBUST_SUPPORT_TRUST_RADIUS = 0.50
ROBUST_ACTION_RESIDUAL_TOLERANCE = 4.0


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise RuntimeError(f"{name} is not finite: {value}")
    return value


def main(output: Path) -> int:
    device = torch.device("cpu")
    policy = DiffusionPolicy.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        map_location="cpu",
        strict=True,
    ).to(device).eval()

    if policy.config.horizon != 16 or policy.config.n_obs_steps != 2:
        raise RuntimeError("unexpected training-runtime Diffusion PushT schema")
    if tuple(policy.config.output_features["action"].shape) != (2,):
        raise RuntimeError("unexpected PushT action shape")

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
        if image.ndim != 3 or image.shape[-1] != 3:
            raise RuntimeError(f"unexpected PushT pixels shape: {tuple(image.shape)}")
        image = image.permute(2, 0, 1).to(torch.float32) / 255.0
        state = torch.as_tensor(np.asarray(raw["agent_pos"]), dtype=torch.float32, device=device)
        return {IMAGE_KEY: image.unsqueeze(0), STATE_KEY: state.unsqueeze(0)}

    baseline_raw = render_snapshot(base_snapshot)
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
            normalized = policy.diffusion.generate_actions(batch)
        actions = policy.unnormalize_outputs({"action": normalized})["action"]
        return actions.detach().cpu().numpy()[0]

    repeat_a = paired_chunk(baseline_raw, 123)
    repeat_b = paired_chunk(baseline_raw, 123)
    repeat_error = float(np.max(np.abs(repeat_a - repeat_b)))
    if repeat_error >= 1e-6:
        raise RuntimeError(f"paired Diffusion query is not repeatable: {repeat_error}")

    query_calls = 0

    def query_support(delta: np.ndarray, seed: int) -> np.ndarray:
        nonlocal query_calls
        delta = np.asarray(delta, dtype=np.float64)
        physical = delta * SUPPORT_SCALE
        changed = base_snapshot.shifted_block(physical[:2], float(physical[2]))
        query_calls += 1
        return paired_chunk(render_snapshot(changed), seed)

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
            # Canonicalize the support chart: query_support multiplies this
            # dimensionless probe by SUPPORT_SCALE[q], so divide by that
            # physical displacement to report action / (pixel or radian).
            jac[:, :, q] = center / SUPPORT_SCALE[q]
            symmetry[:, q] = np.linalg.norm(d_plus - d_minus, axis=-1) / np.maximum(
                np.linalg.norm(center, axis=-1), 1e-12
            )
        return jac, symmetry

    heldout_normalized = HELDOUT_PHYSICAL_DELTA / SUPPORT_SCALE
    heldout_chunk = query_support(heldout_normalized, 123)
    heldout_first_action_response = heldout_chunk[0] - repeat_a[0]

    t0 = time.perf_counter()
    small_j, small_sym = central(FINE_EPSILON, 123)
    large_j, _ = central(COARSE_EPSILON, 123)
    replicate_seeds = [123, 456, 789, 101112, 131415]
    replicate_jacobians = [small_j] + [central(FINE_EPSILON, seed)[0] for seed in replicate_seeds[1:]]
    flat_replicates = np.stack([j.reshape(-1, j.shape[-1]) for j in replicate_jacobians])
    first_action_normalized_support_maps = np.stack(
        [
            metric_whitened_support_jacobian(j[0], SUPPORT_METRIC)
            for j in replicate_jacobians
        ]
    )
    coarse_first_action_normalized_support_map = (
        metric_whitened_support_jacobian(large_j[0], SUPPORT_METRIC)
    )
    robust_center, robust_envelope, locality_breakdown = empirical_locality_envelope(
        first_action_normalized_support_maps,
        coarse_first_action_normalized_support_map,
        quantile=1.0,
    )
    action_low = np.asarray(env.action_space.low, dtype=np.float64)
    action_high = np.asarray(env.action_space.high, dtype=np.float64)
    authority = LinearActionAuthority.from_box(action_low, action_high)
    robust_radius = robust_support_radius_linear_authority(
        repeat_a[0],
        robust_center,
        authority,
        epsilon_j=robust_envelope.epsilon_g,
        trust_radius=ROBUST_SUPPORT_TRUST_RADIUS,
    )
    robust_cert = robust_repair_certificate(
        robust_center,
        heldout_first_action_response,
        physical_map_uncertainty=robust_envelope,
        certified_radius=robust_radius.certified_radius,
        residual_tolerance=ROBUST_ACTION_RESIDUAL_TOLERANCE,
    )

    candidate_probe_bank = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 0.0, 1.0],
            [1.0, 0.0, -1.0],
            [0.0, 1.0, 1.0],
            [0.0, 1.0, -1.0],
        ],
        dtype=np.float64,
    )
    active_plan = plan_minimal_certificate_probes(
        robust_center,
        heldout_first_action_response,
        probe_information=ProbeInformation(
            np.eye(robust_center.shape[1]),
            beta=robust_envelope.epsilon_g,
        ),
        certified_radius=robust_radius.certified_radius,
        residual_tolerance=ROBUST_ACTION_RESIDUAL_TOLERANCE,
        candidate_probes=candidate_probe_bank,
        max_additional_probes=6,
    )
    evidence_action = route_inconclusive_certificate(
        robust_decision=robust_cert.decision,
        planned_decision=active_plan.final_certificate.decision,
        stochastic_radius=locality_breakdown.stochastic_radius,
        scale_drift_radius=locality_breakdown.scale_drift_radius,
    )

    robust_witness_payload = None
    if robust_cert.decision is RobustRepairDecision.CERTIFIED_IMPOSSIBLE:
        robust_normal = heldout_first_action_response - robust_cert.nominal_physical_repair
        robust_witness = build_robust_separation_witness(
            robust_center,
            heldout_first_action_response,
            certified_radius=robust_radius.certified_radius,
            epsilon_g=robust_envelope.epsilon_g,
            residual_tolerance=ROBUST_ACTION_RESIDUAL_TOLERANCE,
            normal=robust_normal,
        )
        robust_witness_verified = verify_robust_separation_witness(
            robust_center,
            heldout_first_action_response,
            certified_radius=robust_radius.certified_radius,
            epsilon_g=robust_envelope.epsilon_g,
            residual_tolerance=ROBUST_ACTION_RESIDUAL_TOLERANCE,
            witness=robust_witness,
        )
        if not robust_witness_verified:
            raise RuntimeError("robust CRG impossibility decision lacks a valid dual witness")
        robust_witness_payload = {
            "verified": True,
            "normal": robust_witness.normal.tolist(),
            "target_projection": float(robust_witness.target_projection),
            "nominal_support": float(robust_witness.nominal_support),
            "uncertainty_support": float(robust_witness.uncertainty_support),
            "robust_support": float(robust_witness.robust_support),
            "distance_lower_bound": float(robust_witness.distance_lower_bound),
            "residual_tolerance": float(robust_witness.residual_tolerance),
            "margin_over_tolerance": float(robust_witness.margin_over_tolerance),
        }

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
        "claim": "second-policy-family real frozen-policy black-box support-response evidence; not an L8 event",
        "policy_identity": {
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "training_runtime_commit": LEROBOT_TRAINING_COMMIT,
            "runtime_mode": "native-training-runtime",
            "schema_compatibility_shim": False,
            "packaging_compatibility": "pyav->av distribution-name fix; explicit packaging.version import; Pymunk 6.11.1 API pin; no policy weights or policy math changed",
        },
        "device": "cpu",
        "protocol_id": PROTOCOL_ID,
        "state_restore_protocol": STATE_RESTORE_PROTOCOL,
        "environment_reset_seed": 17,
        "base_snapshot": {
            "agent_position": base_snapshot.agent_position.tolist(),
            "agent_velocity": base_snapshot.agent_velocity.tolist(),
            "block_position": base_snapshot.block_position.tolist(),
            "block_angle": float(base_snapshot.block_angle),
            "block_velocity": base_snapshot.block_velocity.tolist(),
            "block_angular_velocity": float(base_snapshot.block_angular_velocity),
        },
        "support_scale": SUPPORT_SCALE.tolist(),
        "support_metric_physical": SUPPORT_METRIC.tolist(),
        "support_metric_semantics": (
            "physical support xi=[dx_px,dy_px,dtheta_rad] uses xi^T M xi; "
            "the normalized probe chart is the metric-whitened unit chart"
        ),
        "jacobian_support_units": ["pixel", "pixel", "radian"],
        "small_epsilon": FINE_EPSILON,
        "large_epsilon": COARSE_EPSILON,
        "fine_physical_probe": [4.0, 4.0, 0.02],
        "coarse_physical_probe": [8.0, 8.0, 0.04],
        "heldout_physical_delta": HELDOUT_PHYSICAL_DELTA.tolist(),
        "heldout_first_action_response": heldout_first_action_response.tolist(),
        "preprocess_repeat_max_error": _finite("preprocess_error", preprocess_error),
        "paired_policy_repeat_max_error": _finite("repeat_error", repeat_error),
        "logical_policy_queries": int(query_calls + 2),
        "probe_seconds": _finite("elapsed", elapsed),
        "horizon": int(small_j.shape[0]),
        "action_dim": int(small_j.shape[1]),
        "robust_crg": {
            "support_chart": "dimensionless block-xyt normalized by support_scale",
            "support_trust_radius": ROBUST_SUPPORT_TRUST_RADIUS,
            "action_residual_tolerance": ROBUST_ACTION_RESIDUAL_TOLERANCE,
            "first_action_replicate_maps": first_action_normalized_support_maps.tolist(),
            "operator_norm_uncertainty_observed_max": _finite(
                "robust_operator_uncertainty", robust_envelope.epsilon_g
            ),
            "uncertainty_breakdown": {
                "rng_stochastic_radius": _finite(
                    "rng_stochastic_radius", locality_breakdown.stochastic_radius
                ),
                "finite_difference_scale_drift_radius": _finite(
                    "scale_drift_radius", locality_breakdown.scale_drift_radius
                ),
                "combined_empirical_locality_radius": _finite(
                    "combined_locality_radius", locality_breakdown.combined_radius
                ),
            },
            "coarse_first_action_normalized_support_map": (
                coarse_first_action_normalized_support_map.tolist()
            ),
            "robust_authority_radius": _finite(
                "robust_authority_radius", robust_radius.authority_radius
            ),
            "robust_certified_radius": _finite(
                "robust_certified_radius", robust_radius.certified_radius
            ),
            "decision": robust_cert.decision.value,
            "nominal_residual_norm": _finite(
                "robust_nominal_residual", robust_cert.nominal_residual_norm
            ),
            "worst_case_residual_upper": _finite(
                "robust_worst_case_upper", robust_cert.worst_case_residual_upper
            ),
            "best_case_residual_lower": _finite(
                "robust_best_case_lower", robust_cert.best_case_residual_lower
            ),
            "reason": robust_cert.reason,
            "proof_carrying_impossibility_witness": robust_witness_payload,
            "evidence_scope": (
                "empirical max of RNG repeatability and fine-vs-coarse finite-difference "
                "scale drift; not a formal confidence interval"
            ),
        },
        "evidence_action_router": {
            "bottleneck": evidence_action.bottleneck.value,
            "recommended_action": evidence_action.recommended_action,
            "additional_same_scale_queries_authorized": (
                evidence_action.additional_same_scale_queries_authorized
            ),
            "rationale": evidence_action.rationale,
        },
        "active_minimal_certificate": {
            "status": "planning_only_no_additional_policy_queries_executed",
            "initial_decision": active_plan.initial_certificate.decision.value,
            "final_planned_decision": active_plan.final_certificate.decision.value,
            "planned_probe_count": len(active_plan.steps),
            "planned_symmetric_policy_evaluations": active_plan.symmetric_policy_evaluations,
            "budget_exhausted": active_plan.exhausted_budget,
            "normalized_support_probe_directions": [
                step.probe.tolist() for step in active_plan.steps
            ],
            "physical_symmetric_probe_deltas": [
                (FINE_EPSILON * step.probe * SUPPORT_SCALE).tolist()
                for step in active_plan.steps
            ],
            "decision_after_each_probe": [
                step.decision_after_probe.value for step in active_plan.steps
            ],
            "ambiguity_after_each_probe": [
                float(step.ambiguity_to_decision) for step in active_plan.steps
            ],
            "assumption": (
                "information-only projection at fixed observed-max operator envelope; "
                "future observations must update the map and uncertainty before any "
                "new certificate is accepted"
            ),
        },
        "dec": {
            "first_action_step_jacobian": small_j[0].tolist(),
            "jacobian_small": small_j.tolist(),
            "max_symmetry_residual": _finite("max_symmetry_residual", np.max(small_sym)),
            "mean_symmetry_residual": _finite("mean_symmetry_residual", np.mean(small_sym)),
            "max_scale_curvature": _finite("max_scale_curvature", np.max(curvature)),
            "mean_scale_curvature": _finite("mean_scale_curvature", np.mean(curvature)),
            "per_action_step_gain": [float(x) for x in step_gain],
            "per_action_step_curvature": [float(x) for x in curvature],
            "rng_seed_replicates": replicate_seeds,
            "replicate_count": len(replicate_jacobians),
            "pairwise_seed_dec_distances": [float(x) for x in pairwise],
            "q95_seed_dec_radius": _finite("q95_seed_dec_radius", uncertainty.q95_signature_radius),
            "replicate_stability_certified": bool(uncertainty.stable),
            "certification_eligible": bool(uncertainty.stable),
            "certification_note": ("Five RNG replicates satisfy the count gate; eligibility still depends on the frozen q95 stability threshold." if uncertainty.stable else "Five RNG replicates were run, but the frozen q95 stability threshold was not met."),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    env.close()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("diffusion_pusht_probe.json"))
    args = parser.parse_args()
    raise SystemExit(main(args.output))

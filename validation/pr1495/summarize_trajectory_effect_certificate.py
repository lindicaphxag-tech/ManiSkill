#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED = {
    1: "harmful",
    63: "harmful",
    96: "beneficial",
}


def _step(entry):
    return None if entry is None else int(entry["source_step"])


def _effect_sign(main_success: bool, candidate_success: bool) -> str:
    if main_success and not candidate_success:
        return "harmful"
    if candidate_success and not main_success:
        return "beneficial"
    if main_success == candidate_success:
        return "endpoint_neutral"
    raise AssertionError("unreachable")


def summarize_episode(path: Path) -> dict:
    report = json.loads(path.read_text())
    episode_id = int(report["target_episode"])
    main = report["comparisons"]["main_vs_candidate"]
    migration = report["comparisons"]["candidate_vs_controller_fixed"]

    tau_material = _step(main.get("first_material_physical_divergence"))
    tau_protocol = _step(main.get("first_retry_count_mismatch"))
    protocol_lag = (
        None
        if tau_material is None or tau_protocol is None
        else tau_protocol - tau_material
    )

    main_success = bool(main["a_final_success"])
    candidate_success = bool(main["b_final_success"])
    observed_effect = _effect_sign(main_success, candidate_success)

    migration_material = _step(
        migration.get("first_material_physical_divergence")
    )
    migration_protocol = _step(migration.get("first_retry_count_mismatch"))
    migration_invariant = bool(
        migration["a_final_success"] == migration["b_final_success"]
        and migration_material is None
        and migration_protocol is None
        and float(migration["max_ee_position_delta"]["value"]) <= 1e-6
        and float(migration["max_ee_rotation_delta_deg"]["value"]) <= 1e-3
    )

    return {
        "source_episode_id": episode_id,
        "expected_effect_sign_from_frozen_100_demo_audit": EXPECTED[episode_id],
        "observed_effect_sign": observed_effect,
        "effect_sign_matches_frozen_audit": observed_effect == EXPECTED[episode_id],
        "endpoint": {
            "main_success": main_success,
            "candidate_success": candidate_success,
            "candidate_controller_fixed_success": bool(
                migration["b_final_success"]
            ),
        },
        "main_vs_candidate": {
            "first_tiny_physical_divergence_step": _step(
                main.get("first_post_step_physical_divergence")
            ),
            "first_material_physical_divergence_step": tau_material,
            "first_protocol_retry_divergence_step": tau_protocol,
            "protocol_lag_after_material_steps": protocol_lag,
            "material_precedes_protocol": (
                None
                if protocol_lag is None
                else protocol_lag > 0
            ),
            "main_retried_source_steps": int(main["a_retried_source_steps"]),
            "candidate_retried_source_steps": int(main["b_retried_source_steps"]),
            "main_rotation_clip_events": int(main["a_rotation_clip_events"]),
            "candidate_rotation_clip_events": int(main["b_rotation_clip_events"]),
            "max_ee_position_delta_m": float(
                main["max_ee_position_delta"]["value"]
            ),
            "max_ee_position_delta_step": int(
                main["max_ee_position_delta"]["source_step"]
            ),
            "max_ee_rotation_delta_deg": float(
                main["max_ee_rotation_delta_deg"]["value"]
            ),
            "max_ee_rotation_delta_step": int(
                main["max_ee_rotation_delta_deg"]["source_step"]
            ),
            "max_post_rotation_residual_delta_deg": float(
                main["max_post_rotation_residual_delta_deg"]["value"]
            ),
            "max_post_rotation_residual_delta_step": int(
                main["max_post_rotation_residual_delta_deg"]["source_step"]
            ),
        },
        "controller_migration_control": {
            "migration_invariant": migration_invariant,
            "first_material_physical_divergence_step": migration_material,
            "first_protocol_retry_divergence_step": migration_protocol,
            "max_ee_position_delta_m": float(
                migration["max_ee_position_delta"]["value"]
            ),
            "max_ee_rotation_delta_deg": float(
                migration["max_ee_rotation_delta_deg"]["value"]
            ),
        },
        "material_divergence_window_main": main.get(
            "material_divergence_window_a", []
        ),
        "material_divergence_window_candidate": main.get(
            "material_divergence_window_b", []
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    episodes = []
    for episode_id in sorted(EXPECTED):
        path = a.root / f"episode-{episode_id}" / "episode_trace_summary.json"
        episodes.append(summarize_episode(path))

    all_effects_match = all(
        item["effect_sign_matches_frozen_audit"] for item in episodes
    )
    all_migration_invariant = all(
        item["controller_migration_control"]["migration_invariant"]
        for item in episodes
    )
    material_before_protocol_when_observed = all(
        (
            item["main_vs_candidate"]["material_precedes_protocol"] is not False
        )
        for item in episodes
    )

    result = {
        "schema_version": 1,
        "selection_rule": (
            "all and only discordant source episodes from the frozen current-v2 "
            "same-base 100-demo audit: main-only {1,63}, candidate-only {96}"
        ),
        "frozen_shas": {
            "current_main": "107c9528b23b55bd276cf723c260a45ae7ce00ec",
            "contract_adapter_v2": "bd0e4feae2491a0d433107210ce8c16b8e8fb69a",
            "controller_fix": "eed9be164797d41540421bda8adb3840377d7087",
        },
        "material_divergence_definition": {
            "ee_position_delta_m_gt": 1e-3,
            "ee_rotation_delta_deg_gt": 1.0,
            "or_task_success_differs": True,
        },
        "cross_episode": {
            "all_effect_signs_match_frozen_100_demo_audit": all_effects_match,
            "all_candidate_controller_fixed_controls_invariant": (
                all_migration_invariant
            ),
            "material_precedes_protocol_when_protocol_diverges": (
                material_before_protocol_when_observed
            ),
            "harmful_episode_count": sum(
                item["observed_effect_sign"] == "harmful" for item in episodes
            ),
            "beneficial_episode_count": sum(
                item["observed_effect_sign"] == "beneficial" for item in episodes
            ),
        },
        "episodes": episodes,
        "claim_boundary": (
            "Exhaustive mechanism audit over the three source episodes that "
            "were discordant in the frozen 100-demo paired replay. This "
            "describes trajectory-effect heterogeneity and does not establish "
            "a general dynamical law."
        ),
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    compact = json.loads(json.dumps(result))
    for item in compact["episodes"]:
        item.pop("material_divergence_window_main", None)
        item.pop("material_divergence_window_candidate", None)
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

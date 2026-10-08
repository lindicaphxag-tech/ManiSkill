#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


VARIANTS = ("main", "converter_only", "controller_only", "composed")
CORPORA = ("baseline_generated", "composed_generated")


def _cluster_episode_means(values, episode_ids):
    values = np.asarray(values, dtype=np.float64)
    episode_ids = np.asarray(episode_ids, dtype=np.int64)
    unique = np.unique(episode_ids)
    return unique, np.asarray(
        [values[episode_ids == episode_id].mean() for episode_id in unique],
        dtype=np.float64,
    )


def _episode_cluster_bootstrap_ci(
    values,
    episode_ids,
    *,
    seed=20261006,
    n_boot=5000,
):
    unique, episode_means = _cluster_episode_means(values, episode_ids)
    if episode_means.size == 0:
        return {
            "episode_count": 0,
            "episode_mean": float("nan"),
            "low": float("nan"),
            "high": float("nan"),
        }
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        sampled = rng.integers(0, episode_means.size, size=episode_means.size)
        means[i] = episode_means[sampled].mean()
    return {
        "episode_count": int(unique.size),
        "episode_mean": float(episode_means.mean()),
        "low": float(np.percentile(means, 2.5)),
        "high": float(np.percentile(means, 97.5)),
    }


def _ordered_ids(rows):
    return [
        (int(row["episode_id"]), int(row["step_in_episode"]))
        for row in rows
    ]


def _episode_interaction_certificate(main, conv, ctrl, both, episode_ids, tol=1e-3):
    unique = np.unique(episode_ids)
    per_episode = []
    for episode_id in unique:
        mask = episode_ids == episode_id
        l0 = float(main[mask].mean())
        l1 = float(conv[mask].mean())
        l2 = float(ctrl[mask].mean())
        l12 = float(both[mask].mean())
        per_episode.append(
            {
                "episode_id": int(episode_id),
                "baseline": l0,
                "converter_only": l1,
                "controller_only": l2,
                "composed": l12,
                "converter_harm": l1 - l0,
                "controller_harm": l2 - l0,
                "composed_residual": l12 - l0,
                "semantic_epistasis": l12 - l1 - l2 + l0,
            }
        )

    arr = {
        key: np.asarray([row[key] for row in per_episode], dtype=np.float64)
        for key in (
            "converter_harm",
            "controller_harm",
            "composed_residual",
            "semantic_epistasis",
        )
    }

    cis = {
        "converter_harm": _episode_cluster_bootstrap_ci(
            arr["converter_harm"], unique, seed=20261011
        ),
        "controller_harm": _episode_cluster_bootstrap_ci(
            arr["controller_harm"], unique, seed=20261012
        ),
        "composed_residual": _episode_cluster_bootstrap_ci(
            arr["composed_residual"], unique, seed=20261013
        ),
        "semantic_epistasis": _episode_cluster_bootstrap_ci(
            arr["semantic_epistasis"], unique, seed=20261014
        ),
    }

    means = {k: float(v.mean()) for k, v in arr.items()}
    strict = bool(
        means["converter_harm"] > tol
        and means["controller_harm"] > tol
        and means["composed_residual"] <= tol
    )
    confidence_supported = bool(
        cis["converter_harm"]["low"] > tol
        and cis["controller_harm"]["low"] > tol
        and cis["composed_residual"]["high"] <= tol
    )

    return {
        "objective": "minimize",
        "tolerance_deg": tol,
        "definition": {
            "converter_harm": "L(R_converter) - L(no_repair)",
            "controller_harm": "L(R_controller) - L(no_repair)",
            "composed_residual": "L(R_both) - L(no_repair)",
            "semantic_epistasis": (
                "L(R_both) - L(R_converter) - L(R_controller) + L(no_repair)"
            ),
        },
        "episode_weighted_means_deg": means,
        "episode_cluster_bootstrap_95ci": cis,
        "strict_compensating_bundle": strict,
        "confidence_supported_atomicity": confidence_supported,
        "authorization": {
            "converter_only": "reject" if strict else "undetermined",
            "controller_only": "reject" if strict else "undetermined",
            "composed": (
                "advance_to_execution_domain_gate" if strict else "undetermined"
            ),
        },
        "per_episode": per_episode,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    result = {
        "schema_version": 3,
        "metric": "paired SO(3) converter-to-controller target error",
        "inference_unit": "episode",
        "corpora": {},
        "claim_boundary": (
            "Two frozen official-demo request distributions are evaluated offline. "
            "Within each corpus every implementation receives identical delta poses, "
            "episode identities, within-episode order, and controller normalization "
            "context. Confidence intervals use episode-cluster bootstrap rather than "
            "treating temporally correlated control calls as IID observations. "
            "Scientific hypotheses are reported, never used as workflow pass/fail criteria."
        ),
    }

    for corpus in CORPORA:
        docs = {
            v: json.loads((args.root / f"{corpus}__{v}.json").read_text())
            for v in VARIANTS
        }
        hashes = {docs[v]["corpus_sha256"] for v in VARIANTS}
        counts = {int(docs[v]["request_count"]) for v in VARIANTS}
        if len(hashes) != 1 or len(counts) != 1:
            raise SystemExit(f"{corpus}: pairing identity mismatch")
        corpus_hash = next(iter(hashes))
        count = next(iter(counts))

        ordered_ids = {v: _ordered_ids(docs[v]["paired_rows"]) for v in VARIANTS}
        reference_ids = ordered_ids["main"]
        if any(ordered_ids[v] != reference_ids for v in VARIANTS):
            raise SystemExit(f"{corpus}: episode/step pairing mismatch")

        episode_ids = np.asarray(
            [episode_id for episode_id, _ in reference_ids], dtype=np.int64
        )
        episode_count = int(np.unique(episode_ids).size)

        errors = {
            v: np.asarray(
                [x["rotation_error_deg"] for x in docs[v]["paired_rows"]],
                dtype=np.float64,
            )
            for v in VARIANTS
        }
        if any(len(x) != count for x in errors.values()):
            raise SystemExit(f"{corpus}: paired row count mismatch")
        if any(not np.all(np.isfinite(x)) for x in errors.values()):
            raise SystemExit(f"{corpus}: non-finite semantic error")

        main = errors["main"]
        conv = errors["converter_only"]
        ctrl = errors["controller_only"]
        both = errors["composed"]
        tol = 1e-3

        paired = {
            "converter_minus_main_deg": _episode_cluster_bootstrap_ci(
                conv - main, episode_ids, seed=20261006
            ),
            "controller_minus_main_deg": _episode_cluster_bootstrap_ci(
                ctrl - main, episode_ids, seed=20261007
            ),
            "composed_minus_main_deg": _episode_cluster_bootstrap_ci(
                both - main, episode_ids, seed=20261008
            ),
            "composed_minus_converter_deg": _episode_cluster_bootstrap_ci(
                both - conv, episode_ids, seed=20261009
            ),
            "composed_minus_controller_deg": _episode_cluster_bootstrap_ci(
                both - ctrl, episode_ids, seed=20261010
            ),
            "call_fraction_both_singletons_worse_than_main": float(
                np.mean((conv > main + tol) & (ctrl > main + tol))
            ),
            "call_fraction_composed_no_worse_than_main": float(
                np.mean(both <= main + tol)
            ),
            "call_fraction_full_compensation_pattern": float(
                np.mean(
                    (conv > main + tol)
                    & (ctrl > main + tol)
                    & (both <= main + tol)
                )
            ),
        }

        call_means = {v: float(errors[v].mean()) for v in VARIANTS}
        episode_means = {
            v: float(_cluster_episode_means(errors[v], episode_ids)[1].mean())
            for v in VARIANTS
        }
        strict = bool(
            episode_means["converter_only"] > episode_means["main"]
            and episode_means["controller_only"] > episode_means["main"]
            and episode_means["composed"] <= episode_means["main"] + tol
        )

        interaction_certificate = _episode_interaction_certificate(
            main, conv, ctrl, both, episode_ids, tol=tol
        )

        # Negative control: the two candidate repairs change rotation semantics.
        # Translation is evaluated on the exact same requests/cells and should
        # therefore remain invariant. This tests whether the interaction
        # detector is specific to the affected semantic subspace rather than
        # declaring every four-cell comparison "interactive".
        position = {
            v: np.asarray(
                [x["position_error"] for x in docs[v]["paired_rows"]],
                dtype=np.float64,
            )
            for v in VARIANTS
        }
        pos_main = position["main"]
        pos_conv = position["converter_only"]
        pos_ctrl = position["controller_only"]
        pos_both = position["composed"]
        pos_interaction = pos_both - pos_conv - pos_ctrl + pos_main
        translation_tol = 1e-9
        translation_negative_control = {
            "metric": "paired translation-target error",
            "tolerance": translation_tol,
            "converter_minus_main": _episode_cluster_bootstrap_ci(
                pos_conv - pos_main, episode_ids, seed=20261021
            ),
            "controller_minus_main": _episode_cluster_bootstrap_ci(
                pos_ctrl - pos_main, episode_ids, seed=20261022
            ),
            "composed_minus_main": _episode_cluster_bootstrap_ci(
                pos_both - pos_main, episode_ids, seed=20261023
            ),
            "interaction": _episode_cluster_bootstrap_ci(
                pos_interaction, episode_ids, seed=20261024
            ),
            "max_abs_call_difference_from_main": {
                "converter_only": float(np.max(np.abs(pos_conv - pos_main))),
                "controller_only": float(np.max(np.abs(pos_ctrl - pos_main))),
                "composed": float(np.max(np.abs(pos_both - pos_main))),
            },
            "max_abs_call_interaction": float(np.max(np.abs(pos_interaction))),
            "subspace_invariant": bool(
                np.max(np.abs(pos_conv - pos_main)) <= translation_tol
                and np.max(np.abs(pos_ctrl - pos_main)) <= translation_tol
                and np.max(np.abs(pos_both - pos_main)) <= translation_tol
                and np.max(np.abs(pos_interaction)) <= translation_tol
            ),
            "claim_boundary": (
                "Frozen within-corpus negative control. The compared repairs "
                "target rotation semantics; translation uses the same paired "
                "requests and must not acquire a repair-specific interaction."
            ),
        }

        result["corpora"][corpus] = {
            "corpus_sha256": corpus_hash,
            "request_count": count,
            "episode_count": episode_count,
            "call_weighted_mean_rotation_error_deg": call_means,
            "episode_weighted_mean_rotation_error_deg": episode_means,
            "p95_rotation_error_deg": {
                v: float(np.percentile(errors[v], 95)) for v in VARIANTS
            },
            "paired_effects_episode_cluster_bootstrap": paired,
            "strict_compensating_bundle_episode_weighted": strict,
            "repair_interaction_certificate": interaction_certificate,
            "translation_negative_control": translation_negative_control,
            "variant_summaries": {
                v: {
                    "rotation_error_deg": docs[v]["rotation_error_deg"],
                    "rotation_error_deg_unclipped": docs[v][
                        "rotation_error_deg_unclipped"
                    ],
                    "rotation_error_deg_clipped": docs[v][
                        "rotation_error_deg_clipped"
                    ],
                    "position_error": docs[v]["position_error"],
                    "clipped_calls": docs[v]["clipped_calls"],
                }
                for v in VARIANTS
            },
        }

    result["cross_corpus"] = {
        "strict_compensation_in_both": all(
            result["corpora"][c]["strict_compensating_bundle_episode_weighted"]
            for c in CORPORA
        ),
        "paired_inputs_identical_within_each_corpus": True,
        "input_distributions_independent_of_compared_cell": True,
        "episode_clustered_inference": True,
        "interaction_certificate_in_both": all(
            result["corpora"][c]["repair_interaction_certificate"][
                "strict_compensating_bundle"
            ]
            for c in CORPORA
        ),
        "confidence_supported_atomicity_in_both": all(
            result["corpora"][c]["repair_interaction_certificate"][
                "confidence_supported_atomicity"
            ]
            for c in CORPORA
        ),
        "translation_negative_control_in_both": all(
            result["corpora"][c]["translation_negative_control"][
                "subspace_invariant"
            ]
            for c in CORPORA
        ),
        "corpus_origins": list(CORPORA),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

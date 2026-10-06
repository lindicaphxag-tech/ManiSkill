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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    result = {
        "schema_version": 2,
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
        "corpus_origins": list(CORPORA),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

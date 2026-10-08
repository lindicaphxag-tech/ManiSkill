"""Post-hoc, clustered sensitivity audit for paired frozen-policy comparisons.

This DOES NOT replace a frozen primary gate. Two held-outs from one restored
robot state share their identified DEC, so they are not two independent
experimental units. Bootstrap/permutation units are the restored states.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


PREDICTORS = (
    "dec_distance",
    "raw_distance",
    "support_distance",
    "static_metadata_distance",
    "coarse_class_distance",
)
TARGET = "heldout_response_distance"


def _rank_average(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(x.size, dtype=float)
    i = 0
    while i < x.size:
        j = i + 1
        while j < x.size and x[order[j]] == x[order[i]]:
            j += 1
        ranks[order[i:j]] = 0.5 * (i + j - 1) + 1
        i = j
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if x.ndim != 1 or y.shape != x.shape or x.size < 2:
        raise ValueError("Spearman requires matched one-dimensional arrays")
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise ValueError("nonfinite scores must be reported, not silently dropped")
    a, b = _rank_average(x), _rank_average(y)
    a -= a.mean()
    b -= b.mean()
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if den == 0 else float(np.dot(a, b) / den)


def _matrix(groups: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    if len(groups) < 3:
        raise ValueError("need at least three restored-state clusters")
    ids = [str(group["state_id"]) for group in groups]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate restored-state identity")
    vals = []
    for group in groups:
        records = group["pairs"]
        if not isinstance(records, list) or len(records) != 2:
            raise ValueError("each restored state must have exactly A and B held-outs")
        if [p.get("heldout_id") for p in records] != ["A", "B"]:
            raise ValueError("held-outs must be A then B; no dropped or reordered pairs")
        two = []
        for record in records:
            d = []
            for field in (*PREDICTORS, TARGET):
                value = float(record[field])
                if not np.isfinite(value):
                    raise ValueError(f"nonfinite {field}")
                d.append(value)
            two.append(d)
        vals.append(two)
    arr = np.asarray(vals, dtype=float)
    # A/B are different unseen responses, but both share one same-state DEC.
    if not np.allclose(arr[:, 0, 0], arr[:, 1, 0], atol=1e-12, rtol=0):
        raise ValueError("different DEC within a restored state: provenance drift")
    return arr[:, :, :-1], arr[:, :, -1]


def _correlations(xs: np.ndarray, ys: np.ndarray) -> dict[str, float]:
    flat_y = ys.reshape(-1)
    return {
        key: spearman(xs[:, :, i].reshape(-1), flat_y)
        for i, key in enumerate(PREDICTORS)
    }


def _margin(metrics: dict[str, float]) -> float:
    return metrics["dec_distance"] - max(
        value for key, value in metrics.items() if key != "dec_distance"
    )


def audit_clustered_scores(
    groups: list[dict],
    *,
    random_seed: int = 20261008,
    bootstrap_replicates: int = 1024,
    permutation_replicates: int = 2048,
) -> dict:
    """Diagnostic only: never promote a failed preregistered primary metric.

    The paired 20-case bank consists of 10 state clusters x 2 A/B responses.
    Drawing a state repeats both its responses; permutations shuffle whole
    paired response blocks, not individual held-out outputs.
    """

    if bootstrap_replicates < 100 or permutation_replicates < 100:
        raise ValueError("at least 100 resamples of each type are required")
    xs, ys = _matrix(groups)
    n = xs.shape[0]
    rng = np.random.default_rng(random_seed)
    observed = _correlations(xs, ys)
    observed_margin = _margin(observed)

    bootstrap_dec = np.empty(bootstrap_replicates)
    bootstrap_margin = np.empty(bootstrap_replicates)
    for i in range(bootstrap_replicates):
        selected = rng.integers(0, n, n)
        metrics = _correlations(xs[selected], ys[selected])
        bootstrap_dec[i] = metrics["dec_distance"]
        bootstrap_margin[i] = _margin(metrics)

    leave_one_state_out = []
    for excluded in range(n):
        keep = np.arange(n) != excluded
        metrics = _correlations(xs[keep], ys[keep])
        leave_one_state_out.append({
            "excluded_state": groups[excluded]["state_id"],
            "dec_spearman": metrics["dec_distance"],
            "margin_over_best_baseline": _margin(metrics),
        })

    permuted_at_least_as_large = 0
    for _ in range(permutation_replicates):
        permutation = rng.permutation(n)
        # A/B stay paired and in their original order.
        permuted = spearman(xs[:, :, 0].reshape(-1), ys[permutation].reshape(-1))
        if permuted >= observed["dec_distance"] - 1e-12:
            permuted_at_least_as_large += 1

    return {
        "schema": "crg-clustered-sensitivity-audit-v1",
        "status": "POSTHOC_EXPLORATORY_NOT_PREREGISTERED",
        "n_restored_state_clusters": n,
        "n_dependent_heldout_pairs": n * 2,
        "effective_independent_state_units": n,
        "same_state_dec_is_shared": True,
        "observed_correlations": observed,
        "observed_margin_over_best_baseline": observed_margin,
        "bootstrap_method": "percentile CI; resample whole restored states with A/B kept paired",
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_dec_percentile_95": np.percentile(
            bootstrap_dec, [2.5, 97.5]
        ).tolist(),
        "bootstrap_margin_percentile_95": np.percentile(
            bootstrap_margin, [2.5, 97.5]
        ).tolist(),
        "leave_one_state_out": leave_one_state_out,
        "permutation_method": "one-sided Monte Carlo; permute whole A/B response blocks",
        "permutation_replicates": permutation_replicates,
        "permutation_right_tail_p_exploratory": (
            1 + permuted_at_least_as_large
        ) / (1 + permutation_replicates),
        "random_seed": random_seed,
        "claim_boundary": (
            "Descriptive cluster sensitivity only. Ten states, not twenty "
            "independent samples; post-hoc exploratory p-values are not "
            "confirmatory. State permutation requires exchangeable states; "
            "the v2 restore amendment precludes claiming untouched v1 "
            "preregistration. The frozen primary gate is unchanged."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("score_groups", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.score_groups.read_text(encoding="utf-8"))
    if data.get("schema") != "crg-paired-score-groups-v1":
        raise SystemExit("unexpected score-group schema")
    output = audit_clustered_scores(data["groups"])
    serialized = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

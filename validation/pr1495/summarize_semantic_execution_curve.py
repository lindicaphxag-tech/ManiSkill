#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

FAIL_RE = re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE = re.compile(
    r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved"
)


def key(alpha: float) -> str:
    return str(float(alpha)).replace(".", "p")


def parse_log(path: Path, expected: int) -> tuple[int, ...]:
    text = path.read_text(encoding="utf-8", errors="replace")
    failed = {int(x) for x in FAIL_RE.findall(text)}
    success = tuple(i for i in range(expected) if i not in failed)
    matches = SUMMARY_RE.findall(text)
    if not matches:
        raise RuntimeError(f"missing replay summary in {path}")
    replayed, saved, denom, _ = matches[-1]
    if int(replayed) != expected or int(denom) != expected or int(saved) != len(success):
        raise RuntimeError(f"inconsistent replay summary in {path}")
    return success


def episode_weighted_semantic_mean(doc: dict) -> float:
    by_ep: dict[int, list[float]] = {}
    for row in doc["paired_rows"]:
        by_ep.setdefault(int(row["episode_id"]), []).append(
            float(row["rotation_error_deg"])
        )
    return float(np.mean([np.mean(values) for values in by_ep.values()]))


def transition_count(bits: list[bool]) -> int:
    return sum(a != b for a, b in zip(bits, bits[1:]))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--alphas", nargs="+", type=float, required=True)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--expected", type=int, default=10)
    a = p.parse_args()

    rows = []
    for alpha in a.alphas:
        k = key(alpha)
        semantic = json.loads(
            (a.root / f"semantic_alpha_{k}.json").read_text(encoding="utf-8")
        )
        success_sets = [
            parse_log(
                a.root / f"execution_alpha_{k}" / f"repeat_{i}.log",
                a.expected,
            )
            for i in range(a.repeats)
        ]
        distinct = sorted(set(success_sets))
        ep1 = [1 in s for s in success_sets]
        rows.append(
            {
                "alpha": alpha,
                "semantic_error_deg_episode_weighted_mean":
                    episode_weighted_semantic_mean(semantic),
                "semantic_error_deg_call_weighted_mean":
                    float(semantic["rotation_error_deg"]["mean"]),
                "repeat_count": a.repeats,
                "distinct_success_sets": [list(x) for x in distinct],
                "exactly_repeatable": len(distinct) == 1,
                "success_counts": [len(x) for x in success_sets],
                "episode1_success_frequency": sum(ep1) / len(ep1),
                "episode1_success_bits": ep1,
            }
        )

    semantic = [r["semantic_error_deg_episode_weighted_mean"] for r in rows]
    semantic_monotone_nonincreasing = all(
        right <= left + 1e-9 for left, right in zip(semantic, semantic[1:])
    )

    stable_bits = []
    all_repeatable = all(r["exactly_repeatable"] for r in rows)
    for row in rows:
        freq = row["episode1_success_frequency"]
        stable_bits.append(freq == 1.0)

    transitions = transition_count(stable_bits) if all_repeatable else None

    canonical_main = [0, 1, 3, 4, 5, 6, 7, 8, 9]
    canonical_v2 = [0, 3, 4, 5, 6, 7, 8, 9]
    endpoints = {
        "alpha0_exactly_repeatable": rows[0]["exactly_repeatable"],
        "alpha1_exactly_repeatable": rows[-1]["exactly_repeatable"],
        "alpha0_matches_main": rows[0]["distinct_success_sets"] == [canonical_main],
        "alpha1_matches_v2": rows[-1]["distinct_success_sets"] == [canonical_v2],
    }

    report = {
        "schema_version": 1,
        "protocol": "paired semantic fidelity + five fresh-process execution repeats per frozen alpha",
        "alphas": a.alphas,
        "rows": rows,
        "endpoint_gate": endpoints,
        "all_alpha_execution_exactly_repeatable": all_repeatable,
        "semantic_error_monotone_nonincreasing": semantic_monotone_nonincreasing,
        "episode1_transition_count_if_repeatable": transitions,
        "execution_nonmonotone_if_repeatable":
            bool(all_repeatable and transitions is not None and transitions >= 2),
        "strong_semantic_execution_decoupling":
            bool(
                all(endpoints.values())
                and all_repeatable
                and semantic_monotone_nonincreasing
                and transitions is not None
                and transitions >= 2
            ),
        "claim_boundary": (
            "Frozen PegInsertionSide first-10 replay protocol. A strong decoupling "
            "claim requires endpoint reproduction, exact repeatability at every alpha, "
            "monotone paired semantic improvement, and at least two episode-1 execution "
            "transitions. Otherwise report the weaker observed pattern only."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))

    if not all(endpoints.values()):
        raise SystemExit("endpoint gate failed; decoupling interpretation forbidden")


if __name__ == "__main__":
    main()

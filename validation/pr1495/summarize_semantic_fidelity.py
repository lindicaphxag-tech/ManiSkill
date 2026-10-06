#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = [
        "main",
        "converter_only",
        "controller_only",
        "composed",
        "adaptive_current",
        "adaptive_controller_fixed",
    ]
    variants = {
        name: json.loads((args.root / f"{name}.json").read_text(encoding="utf-8"))
        for name in names
    }

    def p95(name):
        return variants[name]["rotation_error_deg_unclipped"].get(
            "p95", float("inf")
        )

    checks = {
        "baseline_representation_error_detected": p95("main") > 1.0e-3,
        "singleton_failures_detected": (
            p95("converter_only") > 1.0 and p95("controller_only") > 1.0
        ),
        "composed_semantic_fidelity": p95("composed") <= 1.0e-3,
        "adaptive_current_fidelity": p95("adaptive_current") <= 1.0e-3,
        "adaptive_controller_fixed_fidelity": (
            p95("adaptive_controller_fixed") <= 1.0e-3
        ),
    }
    checks["adaptive_controller_invariant"] = bool(
        checks["adaptive_current_fidelity"]
        and checks["adaptive_controller_fixed_fidelity"]
        and abs(
            p95("adaptive_current") - p95("adaptive_controller_fixed")
        )
        <= 1.0e-3
    )

    report = {
        "schema_version": 1,
        "metric": (
            "SO(3) converter-to-controller target round-trip error on "
            "unclipped official-demo conversion calls"
        ),
        "claim_boundary": (
            "Direct local semantic fidelity; independent of task-success labels."
        ),
        "variants": variants,
        "checks": checks,
        "adaptive_decision": (
            "semantic_fidelity_candidate"
            if checks["adaptive_controller_invariant"]
            else "reject_or_revise"
        ),
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

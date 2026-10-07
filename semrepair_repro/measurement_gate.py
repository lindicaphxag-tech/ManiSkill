#!/usr/bin/env python3
"""Turn the LeRobot witness into an explicit measurement-authority decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("result", type=Path)
    args = p.parse_args()

    data = json.loads(args.result.read_text(encoding="utf-8"))
    cert = data["certificate"]

    repeatable = bool(
        cert["self_consistency_passes"]
        and cert["all_sweep_roundtrips_pass"]
    )
    identifiable = not bool(
        cert["forward_semantics_fail"]
        and cert["all_sweep_forward_semantics_fail"]
        and cert["compensating_inverse_hides_forward_defect"]
    )

    report = {
        "schema_version": 1,
        "measurement": "paired forward/inverse roundtrip",
        "repeatable": repeatable,
        "identifiable_for_forward_semantics": identifiable,
        "measurement_qualified": repeatable and identifiable,
        "authority": (
            "advance_to_repair_evidence_gate"
            if repeatable and identifiable
            else "reject_until_external_semantic_anchor"
        ),
        "reason": (
            "repeatability is not sufficient when the observable is invariant "
            "to the latent state/action mapping being claimed"
            if repeatable and not identifiable
            else None
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    # This capsule is expected to demonstrate a rejection. A future upstream
    # source change that makes the measurement identifying should cause this
    # assertion to fail and force the capsule to be reviewed.
    if report["authority"] != "reject_until_external_semantic_anchor":
        raise SystemExit("expected non-identifying roundtrip witness no longer holds")


if __name__ == "__main__":
    main()

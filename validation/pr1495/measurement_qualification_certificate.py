#!/usr/bin/env python3
"""Qualify whether an evidence channel may participate in repair authorization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

VALID={"pass","fail","undetermined"}

def qualify(payload:dict)->dict:
    ident=payload["identifiability"]["status"]
    repeat=payload["repeatability"]["status"]
    if ident not in VALID or repeat not in VALID:
        raise ValueError("status must be one of pass/fail/undetermined")
    if ident=="pass" and repeat=="pass":
        decision="measurement_qualified"
        authority="advance_to_repair_evidence_gate"
    elif ident=="fail":
        decision="non_identifying_measurement"
        authority="reject_until_external_semantic_anchor"
    elif repeat=="fail":
        decision="non_repeatable_measurement"
        authority="reject_single_run_gate_use_replicate_distribution"
    elif ident=="undetermined":
        decision="identifiability_undetermined"
        authority="reject_until_identifiability_resolved"
    else:
        decision="repeatability_undetermined"
        authority="reject_until_repeatability_resolved"
    return {
        "schema_version":1,
        "case":payload["case"],
        "identifiability":payload["identifiability"],
        "repeatability":payload["repeatability"],
        "measurement_qualified":decision=="measurement_qualified",
        "decision":decision,
        "authority":authority,
        "source_evidence":payload.get("source_evidence",[]),
        "claim_boundary":"Qualifies the evidence channel, not the repair. Passing only permits later repair/effect gates."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=qualify(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()

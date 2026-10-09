"""Pre-analysis validator for SAME-HIDDEN-STATE / four-truth ACK comparisons.

Independent unit is initial task/reset state; four ACK truth realizations and
all policy/controller arms are repeated counterfactuals, NOT 4 independent
samples. The matched source must provide an audit-only *complete* simulator
state hash, not merely an initial policy observation hash. The common public
motion prefix is checked within every truth across arms.

No choice of observation modality is automatically free: supply fixed,
pre-committed unit cost weights if making a scalar cost comparison.
Otherwise report separate read, sensing, and probing dimensions.
Does NOT run PhysX, calibrate risk, or certify physical hardware safety.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

TRUTHS = ("held/held", "held/applied", "applied/held", "applied/applied")
FIELDS = ("task", "reset_id", "ack_truth", "arm",
          "complete_initial_state_sha256", "common_prefix_sha256",
          "official_success", "authority_granted", "wrong_full_history",
          "privileged_target_reads", "public_sensing_events",
          "probe_physical_steps")


def _flag(x: str) -> bool:
    if x not in ("0", "1"):
        raise ValueError("boolean must be 0 or 1")
    return x == "1"


def audit(rows: list[dict], control: str, candidate: str) -> dict:
    if not rows or control == candidate:
        raise ValueError("Need two different methods and nonempty data")
    by_cell = defaultdict(dict)
    by_seed = defaultdict(dict)
    for r in rows:
        if any(k not in r or str(r[k]).strip() == "" for k in FIELDS):
            raise ValueError("Missing required exact-source field")
        if r["ack_truth"] not in TRUTHS or r["arm"] not in (control, candidate):
            raise ValueError("unexpected truth or arm")
        key = (r["task"], r["reset_id"], r["ack_truth"])
        if r["arm"] in by_cell[key]:
            raise ValueError("duplicated arm/seed/truth")
        values = {
            "success": _flag(r["official_success"]),
            "authorized": _flag(r["authority_granted"]),
            "wrong": _flag(r["wrong_full_history"]),
        }
        if values["wrong"] and not values["authorized"]:
            raise ValueError("wrong_full_history only defined for authorized decisions")
        for metric in ("privileged_target_reads", "public_sensing_events",
                       "probe_physical_steps"):
            x = int(r[metric])
            if x < 0:
                raise ValueError("negative cost")
            values[metric] = x
        # Require 64 lowercase hex characters, not just matching free text.
        for field in ("complete_initial_state_sha256", "common_prefix_sha256"):
            s = r[field].lower()
            if len(s) != 64 or any(ch not in "0123456789abcdef" for ch in s):
                raise ValueError(f"invalid sha256: {field}")
            values[field] = s
        by_cell[key][r["arm"]] = values
        by_seed[(r["task"], r["reset_id"])][r["ack_truth"]] = values["complete_initial_state_sha256"]
    if any(set(v) != set((control, candidate)) for v in by_cell.values()):
        raise ValueError("each truth must contain BOTH arms")
    for k, group in by_seed.items():
        if set(group) != set(TRUTHS):
            raise ValueError(f"not all four actual ACK truths for {k}")
        if len(set(group.values())) != 1:
            raise ValueError("four truth experiments are NOT same complete initial state")
    per_seed = defaultdict(list)
    per_task = defaultdict(lambda: [0, 0, 0, 0])
    for key, pair in sorted(by_cell.items()):
        a, b = pair[control], pair[candidate]
        if a["complete_initial_state_sha256"] != b["complete_initial_state_sha256"]:
            raise ValueError("hidden initial state differs between arms")
        if a["common_prefix_sha256"] != b["common_prefix_sha256"]:
            raise ValueError("public probe prefix differs BEFORE decision")
        diff = {
            "success_delta": int(b["success"]) - int(a["success"]),
            "read_delta": b["privileged_target_reads"]-a["privileged_target_reads"],
            "public_event_delta": b["public_sensing_events"]-a["public_sensing_events"],
            "probe_step_delta": b["probe_physical_steps"]-a["probe_physical_steps"],
            "candidate_auth": int(b["authorized"]),
            "candidate_wrong": int(b["wrong"]),
        }
        per_seed[key[:2]].append(diff)
        arr = per_task[key[0]]
        arr[0] += diff["candidate_auth"]
        arr[1] += diff["candidate_wrong"]
        arr[2] += int(b["success"])
        arr[3] += int(a["success"])
    clusters = {}
    for key, d in sorted(per_seed.items()):
        if len(d) != 4:
            raise AssertionError("exactly four truth conditions required")
        clusters["/".join(key)] = {
            m: sum(v[m] for v in d)/4.
            for m in ("success_delta", "read_delta", "public_event_delta", "probe_step_delta")
        }
    metrics = {}
    for task, (accepted, wrong, sc, sb) in sorted(per_task.items()):
        metrics[task] = {
            "accepted": accepted, "wrong_authorizations": wrong,
            "observed_selective_error": wrong/accepted if accepted else None,
            "observed_coverage": accepted/(4*sum(k[0] == task for k in per_seed)),
            "candidate_task_success": sc, "control_task_success": sb,
        }
    return {
        "status": "audit_of_supplied_rows_NOT_new_physics_or_statistically_certified_noninferiority",
        "unique_independent_initial_states": len(per_seed),
        "four_truth_cells": len(by_cell),
        "source_pairing": "matching complete initial SHA and common prefix SHA required",
        "per_task": metrics, "per_reset_four_truth_macro_effects": clusters,
        "warning": ("Four truths on same reset are clustered; paired success totals "
                    "do not prove noninferiority. Sensing and probing cost stay "
                    "separate unless precommitted conversion weights exist."),
    }


def self_test():
    data = []
    for truth in TRUTHS:
        for arm in ("fixed", "selective"):
            data.append(dict(task="pull_cube",reset_id="1",ack_truth=truth,arm=arm,
                            complete_initial_state_sha256="a"*64,
                            common_prefix_sha256="b"*64,official_success="1",
                            authority_granted="1" if arm=="selective" else "0",
                            wrong_full_history="0",
                            privileged_target_reads="0" if arm=="selective" else "1",
                            public_sensing_events="3",
                            probe_physical_steps="1"))
    z = audit(data, "fixed", "selective")
    assert z["unique_independent_initial_states"] == 1
    assert z["per_task"]["pull_cube"]["accepted"] == 4
    data[-1]["complete_initial_state_sha256"] = "c"*64
    try:
        audit(data, "fixed", "selective")
        raise AssertionError("unmatched hidden state accepted")
    except ValueError:
        pass
    print("PASS: full initial state, four truth, prefix match, clustered independent unit")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path)
    p.add_argument("--control")
    p.add_argument("--candidate")
    p.add_argument("--out", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        return self_test()
    if not all((args.csv,args.control,args.candidate,args.out)):
        p.error("--csv --control --candidate --out are all required")
    with args.csv.open(newline="",encoding="utf-8") as f:
        report = audit(list(csv.DictReader(f)),args.control,args.candidate)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

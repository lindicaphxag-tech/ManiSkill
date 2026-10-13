"""Independent arithmetic audit of ALL frozen 48 ACK/probe PhysX rows.

Can detect data/denominator/source-label mismatch, not prove source execution
without inspecting the linked original workflow logs and machine receipts.
This is descriptive pilot evidence, not physical safety certification.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

PROTO_BLOB = "6f97dccaa4740039019db0726e21ea0a970a1fa3"
ROBOTS = {"panda": (5601001, 5601002, 5601003, 5601004),
          "xarm6_robotiq": (5701001, 5701002, 5701003, 5701004)}
PROBES = {"zero": (0.,)*6, "native_x": (.15, 0., 0., 0., 0., 0.),
          "native_y": (0., .15, 0., 0., 0., 0.)}
TRUTHS = ("applied", "held")


def require(cond, message):
    if not cond:
        raise ValueError(message)


def audit(inputs):
    all_rows = []
    by_robot = {}
    for robot, seeds in ROBOTS.items():
        name = f"ack_native_probe_physx_pilot_{robot}.json"
        require(name in inputs, "Missing ORIGINAL complete robot shard: "+name)
        data = json.loads(Path(inputs[name]).read_text(encoding="utf-8"))
        require(data["robot"] == robot and
                data["protocol_git_blob"] == PROTO_BLOB and
                data["original_unique_reset_clusters"] == 4 and
                data["original_native_physx_worlds"] == 24,
                "Robot/source/denominator mismatch")
        rows = data["rows"]
        require(len(rows) == 24, "Incomplete per-robot actual worlds")
        seen = set()
        lookup = {}
        for row in rows:
            key = (row["seed"], row["truth_score_only"], row["probe_id"])
            require(key not in seen, "Duplicate physical truth/probe row")
            seen.add(key)
            seed, truth, probe = key
            require(seed in seeds and truth in TRUTHS and probe in PROBES,
                    "Unregistered reset/ACK/probe")
            require(tuple(row["probe_native_six"]) == PROBES[probe],
                    "Original physical probe action substituted")
            require(row["robot"] == robot and
                    row["decision_time_privileged_target_reads"] == 0 and
                    row["post_action_audit_target_reads"] == 1 and
                    row["public_motion_after_true_actuation"] is True and
                    row["no_certified_physical_safety"] is True,
                    "True controller/privilege evidence contract changed")
            require(row["native_target_recurrence_error_linf_m"] <= 1e-4,
                    "Native source recurrence disagrees with simulator audit")
            for field in ("observation_preprobe_xyz", "observation_postprobe_xyz"):
                values = row[field]
                require(len(values) == 3 and all(math.isfinite(float(v))
                        for v in values), "Nonfinite/incorrect public XYZ")
            lookup[key] = row
        require(seen == {(s,t,p) for s in seeds for t in TRUTHS
                                  for p in PROBES},
                "Not the frozen complete factorial denominator")
        estimates = []
        for seed in seeds:
            gaps = {}
            for probe in PROBES:
                a = lookup[(seed,"applied",probe)]["observation_postprobe_xyz"]
                b = lookup[(seed,"held",probe)]["observation_postprobe_xyz"]
                gaps[probe] = math.dist(a,b)
            estimates.append({
                "seed":seed, "zero_gap_m":gaps["zero"],
                "native_x_minus_zero_m":gaps["native_x"]-gaps["zero"],
                "native_y_minus_zero_m":gaps["native_y"]-gaps["zero"],
            })
        by_robot[robot] = estimates
        all_rows.extend(rows)
    require(len(all_rows) == 48,
            "Incomplete full original native PhysX denominator")
    gate = {}
    for probe in ("native_x", "native_y"):
        support = {
            robot:sum(row[probe+"_minus_zero_m"] >= .005
                      for row in estimates)
            for robot,estimates in by_robot.items()
        }
        gate[probe] = {
            "reset_clusters_at_least_5mm_by_robot":support,
            "supports_followup":all(n >= 3 for n in support.values()),
        }
    result = {
        "schema":"audit_frozen_ack_native_probe_physx_pilot_v1",
        "protocol_blob":PROTO_BLOB,
        "unique_reset_clusters":8,"native_physx_worlds":48,
        "results_by_robot":by_robot,
        "prespecified_5mm_3_of_4_gate_per_probe":gate,
        "qualifies_for_followup_any_single_probe":
            any(g["supports_followup"] for g in gate.values()),
        "calibration_independent_response_bounds_proven":False,
        "equal_actuation_energy_or_contact_risk":False,
        "outside_researcher_reproduction":False,
        "not_a_physical_safety_certificate":True,
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = audit({p.name:p for p in args.input_dir.glob("ack_native_probe_physx_pilot_*.json")})
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print("AUDITED_FROZEN_NATIVE_ACK_PHYSX",
          json.dumps({k:v for k,v in result.items() if k != "results_by_robot"},
                     sort_keys=True),flush=True)

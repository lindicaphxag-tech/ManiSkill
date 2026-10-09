"""Independent no-GPU source and outcome auditor for two-robot probe comparison.

All 64 original physically stepped *test* truth×probe worlds are checked,
plus 64 separately stepped historical calibration worlds. Refuses missing
source/reset state, moved truth, hidden private reads, modified fit/label,
or changed probe action. No claim of independent physics replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from research.cross_robot_online_proprio_classifier import LABELS,train,decide

ROBOTS={"panda":(420001,660001),"xarm6_robotiq":(430001,670001)}
PROBES={"zero":[0.]*6,"nonzero_x":[.15,0.,0.,0.,0.,0.]}
PROTO_BLOB="c03e7c6d2343ec6fcfe1824d4f4b76f5df00b755"
SRC_BLOBS={
    "research/cross_robot_ack_physics.py":"3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7",
    "research/cross_robot_online_proprio_classifier.py":"b0d7a767b93fb9f7cab2ba70494947ccb4027979",
}

def audit(folder:Path)->dict:
    expected={f"two_probe_prior_calibration_{robot}.json" for robot in ROBOTS}
    expected|={f"native_two_probes_{robot}_chunk{chunk}_original16.json"
               for robot in ROBOTS for chunk in (0,1)}
    files={x.name for x in folder.glob("*.json")}
    if files!=expected:
        raise ValueError("Original 2 calibration + 4 test JSON files missing or additional")
    models={}
    per_robot_probe={}
    source_sha={}
    all_original=[]
    for robot,(first_old,first_new) in ROBOTS.items():
        path=folder/f"two_probe_prior_calibration_{robot}.json"
        c=json.loads(path.read_text(encoding="utf-8"))
        source_sha[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        if (c.get("schema")!="original_dual_robot_two_probe_physical_calibration_v1"
            or c.get("robot")!=robot
            or c.get("prior_source_seeds")!=list(range(first_old,first_old+8))
            or c.get("both_truths")!=list(LABELS)
            or c.get("both_physical_probes")!=list(PROBES)
            or c.get("preoutcome_proto_blob")!=PROTO_BLOB):
            raise ValueError("Historical calibration source/frozen identities changed")
        rows=c.get("physical_calibration_source_rows",[])
        if not isinstance(rows,list) or len(rows)!=32:
            raise ValueError("All 32 originally physically measured calibration worlds required")
        seen=set()
        for row in rows:
            k=(row.get("seed"),row.get("hidden_physical_truth_posthoc_only"),
               row.get("known_delivered_native_probe_id"))
            if (k in seen or k[0] not in range(first_old,first_old+8)
                or k[1] not in LABELS or k[2] not in PROBES
                or row.get("robot")!=robot
                or row.get("actual_native_t3_probe_six")!=PROBES[k[2]]
                or row.get("private_target_reads_before_classification")!=0
                or row.get("real_physx_cpu") is not True):
                raise ValueError("Calibration omitted or mislabelled a physical source world")
            seen.add(k)
        for probe in PROBES:
            rec=[dict(robot=r["robot"],seed=r["seed"],
                      truth=r["hidden_physical_truth_posthoc_only"],
                      delta_public_xyz=r["delta_public_xyz"])
                 for r in rows if r["known_delivered_native_probe_id"]==probe]
            fitted=train(rec,robot)
            if fitted!=c["empirical_envelopes_by_probe"][probe]:
                raise ValueError("Model no longer derives from independent source calibration")
            models[(robot,probe)]=fitted
        calibration_digest=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
        for chunk in (0,1):
            path=folder/f"native_two_probes_{robot}_chunk{chunk}_original16.json"
            source_sha[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            d=json.loads(path.read_text(encoding="utf-8"))
            seeds=list(range(first_new+4*chunk,first_new+4*chunk+4))
            if (d.get("schema")!="zero_nonzero_common_probe_cross_robot_fresh16_truth_probes_v1"
                or d.get("robot")!=robot or d.get("chunk")!=chunk
                or d.get("original_seed_register")!=seeds
                or d.get("preoutcome_proto_blob")!=PROTO_BLOB
                or d.get("calibration_sha256")!=calibration_digest
                or d.get("source_chart_git_blobs")!=SRC_BLOBS
                or d.get("test_worlds_actual_native_PhysX")!=16
                or d.get("both_actuation_truths_and_actual_probes") is not True
                or d.get("private_target_getter_never_used_in_decision") is not True
                or d.get("full_task_success_not_tested") is not True):
                raise ValueError("New PhysX source, actual world count or preregistered claim changed")
            rows=d.get("rows",[])
            if not isinstance(rows,list) or len(rows)!=8:
                raise ValueError("Missing/duplicated original heldout physical truth row")
            trials={}
            for row in rows:
                seed,truth=row.get("seed"),row.get("actual_execution_truth_score_only")
                if (seed not in seeds or truth not in LABELS or row.get("robot")!=robot):
                    raise ValueError("Disallowed heldout task seed/truth or robot substitution")
                group=row.get("original_two_physically_stepped_probe_worlds")
                if not isinstance(group,list) or len(group)!=2:
                    raise ValueError("Zero and nonzero probes must be separately physically stepped")
                for trial in group:
                    p=trial.get("known_delivered_native_probe_id")
                    k=(seed,truth,p)
                    if (p not in PROBES or k in trials or trial.get("seed")!=seed
                        or trial.get("hidden_physical_truth_posthoc_only")!=truth
                        or trial.get("actual_native_t3_probe_six")!=PROBES[p]
                        or trial.get("real_physx_cpu") is not True
                        or trial.get("private_target_reads_before_classification")!=0
                        or trial.get("private_target_reads_before_correction")!=0
                        or trial.get("command_execution_ack_hidden_from_classifier") is not True):
                        raise ValueError("Physics/truth leakage, duplicate world or probe changed")
                    original_decision=decide(trial["delta_public_xyz"],models[(robot,p)])
                    if trial.get("decision")!=original_decision:
                        raise ValueError("Public-only classifier was altered or used truth")
                    guessed=original_decision["label"]
                    if trial.get("wrong_confident_history")!=(
                        None if guessed is None else guessed!=truth
                    ) or trial.get("refusal")!=(guessed is None):
                        raise ValueError("Truth label or abstention was rewritten after scoring")
                    if trial.get("target_correction_reached")!=(guessed is not None):
                        raise ValueError("Physically corrected trial marked as unstepped")
                    if guessed is not None:
                        error=trial.get("commanded_target_post_correction_error_inf_m")
                        if (not isinstance(error,(int,float)) or error<0
                            or trial.get("target_restored_below_1e4_m")!=(error<=1e-4)
                            or trial.get("private_target_reads_post_dispatch_audit_only")!=1):
                            raise ValueError("Original post-dispatch target audit changed")
                    trials[k]=trial
            required={(seed,truth,probe) for seed in seeds
                      for truth in LABELS for probe in PROBES}
            if set(trials)!=required:
                raise ValueError("Missing paired seed/truth/probe original trials")
            for probe in PROBES:
                chosen=[trials[(seed,truth,probe)] for seed in seeds for truth in LABELS]
                actual={
                    "confidence_coverage":sum(not t["refusal"] for t in chosen),
                    "wrong_confident_label_count":sum(t["wrong_confident_history"] is True for t in chosen),
                    "abstentions":sum(t["refusal"] for t in chosen),
                    "actual_held_commanded_XYZ_corrected":sum(t["target_restored_below_1e4_m"] for t in chosen),
                    "private_decision_target_reads":sum(t["private_target_reads_before_classification"] for t in chosen),
                }
                if d.get("statistics",{}).get(probe)!=actual:
                    raise ValueError("Reported shard successes/abstentions were recomputed incorrectly")
            all_original.extend(trials.values())
    if len(all_original)!=64 or len({(x["robot"],x["seed"]) for x in all_original})!=16:
        raise ValueError("Full new 64-world denominator invalid")
    outcome={}
    for probe in PROBES:
        xs=[x for x in all_original if x["known_delivered_native_probe_id"]==probe]
        outcome[probe]={
            "genuine_native_physx_worlds":len(xs),
            "confident_public_labels":sum(not x["refusal"] for x in xs),
            "wrong_confident_labels":sum(x["wrong_confident_history"] is True for x in xs),
            "abstained":sum(x["refusal"] for x in xs),
            "actual_commanded_target_XYZ_restored":sum(x["target_restored_below_1e4_m"] for x in xs),
            "private_predecision_readbacks":sum(x["private_target_reads_before_classification"] for x in xs),
        }
    for robot in ROBOTS:
        for probe in PROBES:
            subset=[x for x in all_original if x["robot"]==robot and
                    x["known_delivered_native_probe_id"]==probe]
            per_robot_probe[f"{robot}/{probe}"]={
                "n":len(subset),"confident":sum(not x["refusal"] for x in subset),
                "wrong":sum(x["wrong_confident_history"] is True for x in subset),
                "refused":sum(x["refusal"] for x in subset),
                "corrected":sum(x["target_restored_below_1e4_m"] for x in subset),
            }
    return {
        "status":"FULL_ORIGINAL_OWNER_PHYSX_SOURCE_RECOMPUTED_NOT_INDEPENDENT_LAB",
        "first_preoutcome_git_blob":PROTO_BLOB,
        "original_calibration_physx_worlds":64,
        "unseen_distinct_physical_seed_states":16,
        "unseen_true_delivery_probe_real_physx_worlds":64,
        "two_actual_robots":"panda/xarm6_robotiq",
        "not_frozen_PPO_policy_task_success":True,
        "not_real_network_ACK":True,
        "probe_actuation_energy_not_matched":True,
        "calibration_envelopes_are_empirical_not_attested":True,
        "original_source_sha256":source_sha,
        "per_robot_probe":per_robot_probe,
        "per_probe":outcome,
        "claim_limits":[
            "The two probes have equal step count but unequal movement; no equal-energy claim.",
            "Both robot bodies are from one ManiSkill simulator/framework; not outside lab.",
            "One programmed amplitude and fault step per test, not arbitrary contact dynamics.",
            "Exactly 16 independent physical reset states, each tested across two truth branches and two probes.",
            "No learned PPO/VLA task completion is measured; corrected target position is not actual tool safety.",
            "An empirical calibration envelope cannot guarantee zero future mistaken ACK labels.",
            "Nonzero probe is FIXED, not optimization-selected active probe.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    v=p.parse_args()
    result=audit(v.input_dir)
    v.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("FULL_ZERO_NONZERO_PROBE_REAL_NATIVE_PHYSX_AUDIT",
          json.dumps({"probe":result["per_probe"],
                      "robot":result["per_robot_probe"],
                      "n":result["unseen_true_delivery_probe_real_physx_worlds"]},
                     sort_keys=True))

if __name__=="__main__":
    main()

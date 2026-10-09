"""Outsider-selectable fresh-seed, previously unseen action amplitude x robot PhysX replay.

Run from checkout root. Fork author running this is NOT external reproduction.
The ORIGINAL source method is byte-checked. Six actual robot controller
worlds run for EACH selected unique reset seed x each ACTUAL delivery truth.

This code tests commanded native controller target POSITION, NOT task reward,
trained cross-embodiment PPO, SO3 correction, actual network ACK loss or safety.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path

ROBOTS=("panda","xarm6_robotiq")
SCALES=(0.45,0.75,1.2,1.45)
TRUTHS=("applied","held")
ARMS=("foreign_zero_shot","paired_fixed","paired_action_scaled",
      "blind_optimistic","blind_pessimistic","privileged_once_after_probe")
MIN_SEED=700001
ORIGINAL_SOURCE_BLOB="2bfb8c29bd3b4d62c68186579ad0785689c83f27"
HISTORICAL_CALIBRATION_BLOB="743f0990cf4d72838c77e78a3fc78d0414496969"


def need(x,msg):
    if not x:raise ValueError(msg)


def checked_inputs(robot,scale,first_seed,count):
    need(robot in ROBOTS,"Actual unknown robot rejected")
    need(type(scale) in (float,int) and float(scale) in SCALES,
         "Use declared physically bounded fresh test native amplitude")
    need(type(first_seed) is int and MIN_SEED<=first_seed<=2147483000,
         "Use never-before-tested integer seed >=700001")
    need(type(count) is int and count in (1,4,8),
         "Complete 1/4/8 paired reset seeds required")
    need(first_seed+count<2147483647,"Seed overflow")
    return list(range(first_seed,first_seed+count))


def git_object_blob(data: bytes):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()


def actual_original_method_locked():
    src=Path("research/cross_robot_action_scale_physx.py")
    cal=Path("research/cross_robot_ack_calibration_portability.py")
    need(src.is_file() and cal.is_file(),"Run from public ManiSkill checkout root")
    need(git_object_blob(src.read_bytes())==ORIGINAL_SOURCE_BLOB,
         "Original real PhysX experimental method changed bytes")
    need(git_object_blob(cal.read_bytes())==HISTORICAL_CALIBRATION_BLOB,
         "Historical one-paired-seed calibration model changed bytes")


def validate_rows(rows,robot,scale,seeds):
    from research.cross_robot_online_proprio_classifier import decide
    from research.cross_robot_action_scale_physx import models_for_robot,verify_calibrations
    models=models_for_robot(robot,verify_calibrations(),scale)
    need(len(rows)==2*len(seeds),"Must retain BOTH physically simulated ACK truths per seed")
    need([(q.get("seed"),q.get("actual_delivery_truth")) for q in rows]
         ==[(seed,truth) for seed in seeds for truth in TRUTHS],
         "Out-of-register/duplicated/missing PhysX original truth")
    totals={a:{"confident":0,"wrong_confident":0,"abstain":0,
               "actual_native_target_position_restored":0,"target_decision_reads":0}
            for a in ARMS}
    for item in rows:
        six=item.get("six_original_actual_physx_controller_worlds")
        need(isinstance(six,list) and [x.get("control") for x in six]==list(ARMS),
             "Six real and provenance-labelled native control worlds mandatory")
        for row in six:
            a=row["control"]
            need(row.get("robot")==robot and row.get("scale")==scale and
                 row.get("seed")==item["seed"] and
                 row.get("truth")==item["actual_delivery_truth"] and
                 row.get("real_physx_cpu") is True and
                 row.get("step3_common_native_zero_probed") is True and
                 row.get("scripted_native_commands_no_frozen_ppo") is True and
                 row.get("source_policy_trained") is False,
                 "Simulated controller source provenance or physically dispatched probe missing")
            if a in models:
                predicted=decide(row["public_delta_xyz"],models[a])
                label=predicted["label"]
                need(row.get("decision")==predicted,"Public-only model decision drift/label manipulation")
                budget=0
            elif a.startswith("blind_"):
                label="applied" if a=="blind_optimistic" else "held"
                need(row.get("decision",{}).get("label")==label and
                     row["decision"].get("status")=="NO_PUBLIC_RESPONSE_USED",
                     "Blinded comparator changed after outcomes")
                budget=0
            else:
                label=row.get("decision",{}).get("label")
                budget=1
                need(row.get("decision",{}).get("status")=="PRIVILEGED_ONE_TARGET_READ" and
                     label in TRUTHS,
                     "Authoritative comparator did not disclose its one decision read")
            need(row["private_target_getter_calls_at_decision"]==budget,
                 "Private target leaked into public prediction")
            wrong=(None if label is None else label!=item["actual_delivery_truth"])
            need(row.get("wrong_confident_ack_history") is wrong and
                 row.get("refused_ambiguous_public_response") is (label is None),
                 "Physical hidden-state error/refusal concealed")
            score=row.get("corrected_position_within_1e4_m")
            error=row.get("corrected_target_position_linf_m")
            if row.get("correction_actually_physx_executed"):
                need(type(error) in (int,float) and math.isfinite(error)
                     and error>=0 and score is (error<=1e-4),
                     "Post-step controller goal correction provenance lost")
            else:
                need(error is None and score is False,
                     "Refused/native-illegal arm marked as actual correction")
            totals[a]["confident"]+=int(label is not None)
            totals[a]["abstain"]+=int(label is None)
            totals[a]["wrong_confident"]+=int(wrong is True)
            totals[a]["actual_native_target_position_restored"]+=int(score is True)
            totals[a]["target_decision_reads"]+=budget
    for v in totals.values():
        need(v["confident"]+v["abstain"]==2*len(seeds),
             "Partial source denominator")
    return totals


def run(robot,scale,first_seed,count,output_dir):
    seeds=checked_inputs(robot,scale,first_seed,count)
    actual_original_method_locked()
    from research.cross_robot_action_scale_physx import models_for_robot,verify_calibrations,one_actual_world
    models=models_for_robot(robot,verify_calibrations(),scale)
    rows=[]
    for seed in seeds:
        for truth in TRUTHS:
            six=[one_actual_world(robot,seed,scale,truth,a,models) for a in ARMS]
            rows.append(dict(seed=seed,actual_delivery_truth=truth,
                             six_original_actual_physx_controller_worlds=six))
            print("OUTSIDER_SELECTABLE_SIX_NATIVE_PHYSX_ORIGINAL",
                  json.dumps(rows[-1],sort_keys=True),flush=True)
    scores=validate_rows(rows,robot,scale,seeds)
    output_dir.mkdir(parents=True,exist_ok=True)
    source={
        "schema":"outside_selected_cross_robot_action_scale_ack_physical_originals_v1",
        "original_frozen_source_git_blob":ORIGINAL_SOURCE_BLOB,
        "calibration_git_blob":HISTORICAL_CALIBRATION_BLOB,
        "source_selected_reset_seeds":seeds,
        "selected_native_scale":scale,"selected_robot":robot,
        "selected_two_physical_truths":list(TRUTHS),
        "all_six_control_worlds":list(ARMS),"original_physx_source_rows":rows,
        "verified_full_denominator_scores":scores,
        "genuine_native_cpu_physx":True,
        "no_cross_robot_PPO_task_success_claim":True,
        "not_third_party_reproduction_by_author_run":True,
        "investigator_provenance":{
          "github_repository":os.environ.get("GITHUB_REPOSITORY"),
          "github_actor":os.environ.get("GITHUB_ACTOR"),
          "github_run_id":os.environ.get("GITHUB_RUN_ID"),
          "github_source_sha":os.environ.get("GITHUB_SHA")},
        "limits":"Not full SO3, hardware network loss, force/collision safety, population reliability or an automatically independent lab"
    }
    name=f"original_selected_native_ack_{robot}_s{str(scale).replace('.','p')}_{first_seed}_n{count}.json"
    path=output_dir/name
    path.write_text(json.dumps(source,indent=2,sort_keys=True)+"\n")
    manifest=output_dir/"SOURCE_SHA256SUMS"
    manifest.write_text(hashlib.sha256(path.read_bytes()).hexdigest()+"  "+name+"\n")
    print("REPRODUCER_SELECTABLE_NATIVE_ACK_PHYSX_COMPLETE",
          json.dumps({"robot":robot,"scale":scale,"n":2*len(seeds),"scores":scores,
                      "original_sha256":hashlib.sha256(path.read_bytes()).hexdigest()},sort_keys=True),
          flush=True)
    return path


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--robot",choices=ROBOTS,required=True)
    p.add_argument("--scale",choices=SCALES,type=float,required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--count",type=int,default=4,choices=(1,4,8))
    p.add_argument("--output-dir",type=Path,default=Path("outside_robot_reproduction"))
    a=p.parse_args()
    run(a.robot,a.scale,a.first_seed,a.count,a.output_dir)

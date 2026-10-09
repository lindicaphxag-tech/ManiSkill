"""Independent stdlib-only audit of original four real PhysX cross-robot OOD shards.

Never trains or runs simulated controllers. Recomputes ORIGINAL public-only
classification without reading private target labels, checks actual source
target-position audits and every original protocol reset/fault outcome. Do not
confuse true-controller TARGET correction with contact or PPO task success.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from research.cross_robot_ack_calibration_portability import (
    immutable_source,source_audit,DATA,one_calibrated_model
)
from research.cross_robot_online_proprio_classifier import decide,LABELS

ROBOTS=("panda","xarm6_robotiq")
SCALES=(0.6,1.35)
SEED_START={"panda":610001,"xarm6_robotiq":620001}
CONTROL=("foreign_zero_shot","paired_fixed","paired_action_scaled",
         "blind_optimistic","blind_pessimistic","privileged_once_after_probe")
SCHEMA="prospective_cross_robot_action_scale_ack_32_physics_shard_v1"


def need(condition,msg):
    if not condition:raise ValueError(msg)


def equal(a,b):
    if type(a) is bool or type(b) is bool:return type(a) is type(b) and a==b
    if type(a) in (int,float) and type(b) in (int,float):
        return math.isfinite(a) and math.isfinite(b) and math.isclose(
            float(a),float(b),rel_tol=0,abs_tol=2e-10)
    if isinstance(a,dict) and isinstance(b,dict):
        return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)) and isinstance(b,(tuple,list)):
        return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b


def expected_models(robot,scale,calibrations):
    import copy
    other=next(x for x in ROBOTS if x!=robot)
    source=calibrations[other]["model"]
    target=one_calibrated_model(source,calibrations[robot],robot,1)
    scaled=copy.deepcopy(target)
    held=scaled["class_models"]["held"]["mean_public_motion_m"]
    applied=scaled["class_models"]["applied"]["mean_public_motion_m"]
    scaled["class_models"]["applied"]["mean_public_motion_m"]=[
        held[i]+scale*(applied[i]-held[i]) for i in range(3)]
    return {"foreign_zero_shot":source,
            "paired_fixed":target,"paired_action_scaled":scaled}


def one(data,robot,scale,calibrations):
    expected_scale="0p6" if scale==0.6 else "1p35"
    first=SEED_START[robot]
    models=expected_models(robot,scale,calibrations)
    need(data.get("schema")==SCHEMA and
         data.get("protocol")=="research/CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json"
         and data.get("robot")==robot and data.get("scale")==scale and
         data.get("task")=="PickCube-v1" and
         data.get("control_mode")=="pd_ee_target_delta_pose" and
         data.get("original_seed_range")==list(range(first,first+4)) and
         data.get("actual_delivery_truths")==list(LABELS) and
         data.get("control_names")==list(CONTROL) and
         data.get("real_cpu_physx") is True and
         data.get("not_ppo_task_success") is True and
         data.get("not_real_robot_or_network_packet_loss") is True and
         data.get("not_independent_external_lab") is True,
         "Preregistered robot, task, command scale, original seed or scope changed")
    need(data.get("calibration_models") is not None and
         equal(models,data["calibration_models"]),
         "Training/source calibration was tuned after blinded PhysX results")
    rows=data.get("cases")
    need(isinstance(rows,list) and len(rows)==8,
         "Missing original two truth cases per four robot reset seeds")
    expect=[(seed,truth) for seed in range(first,first+4) for truth in LABELS]
    need([(row.get("seed"),row.get("actual_delivery_truth")) for row in rows]==expect,
         "PhysX cases were dropped, substituted or re-ordered")
    totals={k:{"confident":0,"wrong_confident":0,"refusal":0,
               "actual_native_target_position_restored":0,
               "privileged_decision_reads":0} for k in CONTROL}
    decisions=[]
    for row in rows:
        arms=row.get("six_independently_physx_stepped_native_arms")
        need(isinstance(arms,list) and len(arms)==len(CONTROL) and
             [a.get("control") for a in arms]==list(CONTROL),
             "Missing or substituted independent actual native PhysX controller world")
        before=arms[0]["original_public_before_xyz"]
        after=arms[0]["original_public_after_xyz"]
        for c in arms:
            need(c.get("robot")==robot and c.get("seed")==row["seed"] and
                 c.get("scale")==scale and c.get("truth")==row["actual_delivery_truth"] and
                 c.get("real_physx_cpu") is True and
                 c.get("scripted_native_commands_no_frozen_ppo") is True and
                 c.get("source_policy_trained") is False and
                 c.get("step3_common_native_zero_probed") is True and
                 c.get("step2_actual_delivery")==(
                    "scaled_native_applied" if row["actual_delivery_truth"]=="applied"
                    else "native_zero_held") and
                 c.get("native_controller_keys")==(
                    ["arm","gripper"] if robot=="panda" else
                    ["arm","gripper_active","gripper_passive"]),
                 "Native source robot controller, actual physical fault or label forgery")
            need(all(isinstance(c.get(key),list) and len(c[key])==3 and
                     all(type(v) in (int,float) and math.isfinite(v) for v in c[key])
                     for key in ("original_public_before_xyz","original_public_after_xyz",
                                 "public_delta_xyz")),
                 "Public XYZ source evidence incomplete")
            need(max(abs(a-b) for a,b in zip(
                 c["original_public_before_xyz"],before))<1e-4 and
                 max(abs(a-b) for a,b in zip(
                 c["original_public_after_xyz"],after))<1e-4,
                 "Matched native physical probe trajectories differ")
            need(max(abs((y-x)-v) for x,y,v in zip(
                 c["original_public_before_xyz"],
                 c["original_public_after_xyz"],
                 c["public_delta_xyz"]))<1e-7,
                 "Public achieved motion vector manufactured")
            control=c["control"]
            if control in models:
                response=decide(c["public_delta_xyz"],models[control])
                need(equal(c.get("decision"),response),
                     "Public response truth-labelled decision does not match frozen model")
                require_private=0
            elif control=="blind_optimistic":
                response={"label":"applied","status":"NO_PUBLIC_RESPONSE_USED",
                          "private_target_getter_calls_at_decision":0}
                require_private=0
            elif control=="blind_pessimistic":
                response={"label":"held","status":"NO_PUBLIC_RESPONSE_USED",
                          "private_target_getter_calls_at_decision":0}
                require_private=0
            else:
                response=c["decision"]
                require_private=1
                need(response.get("status")=="PRIVILEGED_ONE_TARGET_READ" and
                     response.get("private_target_getter_calls_at_decision")==1,
                     "Oracle source failed to disclose privileged controller target state")
            need(equal(c.get("decision"),response) and
                 c.get("private_target_getter_calls_at_decision")==require_private,
                 "Hidden authority state leaked to public classifier")
            predicted=response.get("label")
            need(predicted in (None,*LABELS),"Unknown physical history")
            wrong=None if predicted is None else predicted!=row["actual_delivery_truth"]
            need(c.get("wrong_confident_ack_history") is wrong and
                 c.get("refused_ambiguous_public_response") is (predicted is None),
                 "Hidden ground truth erroneously scored or withheld")
            success=c.get("corrected_position_within_1e4_m")
            err=c.get("corrected_target_position_linf_m")
            if c.get("correction_actually_physx_executed") is True:
                need(type(err) in (int,float) and math.isfinite(err) and err>=0 and
                     success is (err<=1e-4) and
                     isinstance(c.get("corrective_native6"),list) and
                     len(c["corrective_native6"])==6 and
                     all(type(x) in (int,float) and math.isfinite(x) and
                         abs(x)<=1+1e-5 for x in c["corrective_native6"]),
                     "Actual robot target position result invalid or native action illegal")
            else:
                need(err is None and success is False,
                     "A refused or unrepresentable correction counted as successful")
            totals[control]["confident"]+=int(predicted is not None)
            totals[control]["wrong_confident"]+=int(wrong is True)
            totals[control]["refusal"]+=int(predicted is None)
            totals[control]["actual_native_target_position_restored"]+=int(success is True)
            totals[control]["privileged_decision_reads"]+=require_private
        decisions.append({
            "seed":row["seed"],"truth":row["actual_delivery_truth"],
            "scaled_action_public_label":arms[2]["decision"]["label"],
            "fixed_action_public_label":arms[1]["decision"]["label"],
            "zero_shot_public_label":arms[0]["decision"]["label"],
        })
    need(totals==data.get("scores"),
         "Original study physical source totals do not match raw episode flags")
    return {"original_truth_conditions":8,
            "n_distinct_reset_seeds":4,
            "scores":totals,"source_decisions":decisions}


def audit(folder):
    required={f"cross_robot_ack_scale_{robot}_{str(scale).replace('.','p')}_original8.json"
              for robot in ROBOTS for scale in SCALES}
    actual={p.name for p in folder.glob("cross_robot_ack_scale_*_original8.json")}
    need(required==actual,"Missing or extraneous source PhysX shard")
    immutable_source(DATA)
    source_audit(DATA)
    calibrations={robot:json.loads(
        (DATA/f"cross_robot_proprio_calibration_{robot}.json").read_text())
        for robot in ROBOTS}
    groups={}
    for robot in ROBOTS:
        for scale in SCALES:
            name=f"cross_robot_ack_scale_{robot}_{str(scale).replace('.','p')}_original8.json"
            groups[f"{robot}@{scale}"]=one(json.loads((folder/name).read_text()),
                                           robot,scale,calibrations)
    global_counts={k:{field:sum(v["scores"][k][field] for v in groups.values())
                       for field in ("confident","wrong_confident","refusal",
                                     "actual_native_target_position_restored",
                                     "privileged_decision_reads")}
                   for k in CONTROL}
    return {
      "schema":"prospective_cross_robot_action_amplitude_full32_source_audit_v1",
      "actual_original_physx_conditions":32,
      "distinct_reset_seeds_across_robots":8,
      "matched_two_scales_and_two_truths_per_seed":True,
      "six_actual_independent_physx_arms_per_condition":True,
      "original_frozen_model_calibration_truth_episodes":4,
      "not_ppo_task_success_not_real_robot":True,
      "not_external_independent_lab":True,
      "aggregate_scores":global_counts,"groups":groups,
      "limitations":"No native PPO task success, no end-effector achieved pose safety, no SO3 restoration, no unseen robot type outside Panda/xArm6, no actual network ACK packet loss"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=audit(args.input_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("CROSS_ROBOT_ACTION_SCALE_FULL32_ORIGINAL_PHYSX",
          json.dumps({"n":32,"scores":report["aggregate_scores"]},sort_keys=True))

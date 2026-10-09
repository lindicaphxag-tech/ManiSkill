"""Original prospective Panda+xArm6 online proprioception source audit (stdlib only).

Runs on 4 original shard JSONs and 2 independently executed calibration JSONs.
Refuses cherry-picked negative labels and missing physics arms. Counts wrong
confident history authorizations, abstentions and actually physically stepped
position-target corrections, not just source-selected task success.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from research.cross_robot_online_proprio_classifier import LABELS,train,decide

OLD={"panda":420001,"xarm6_robotiq":430001}
FRESH={"panda":480001,"xarm6_robotiq":490001}
ARMS=("public_proprio_empirical","blind_optimistic","blind_pessimistic")
PROTO_SHA="0cb66afc8a9c362ee764a83b7e558069ef6bd09c"


def calibration(source,robot):
    if (source.get("schema")!="cross_robot_online_ack_calibration_original16_v1"
        or source.get("robot")!=robot
        or source.get("original_preoutcome_protocol_git_blob")!=PROTO_SHA
        or source.get("seed_range")!=list(range(OLD[robot],OLD[robot]+8))
        or source.get("truths")!=list(LABELS)
        or source.get("labels_only_from_prior_calibration_known_physics") is not True
        or source.get("not_outside_independent_replication") is not True):
        raise ValueError("Unfrozen calibration provenance")
    rows=source.get("calibration_source_rows")
    if not isinstance(rows,list) or len(rows)!=16:
        raise ValueError("All 16 calibration physically executed cases required")
    if [(r.get("seed"),r.get("hidden_truth")) for r in rows] != [
        (seed,truth) for seed in range(OLD[robot],OLD[robot]+8) for truth in LABELS]:
        raise ValueError("Calibration omitted or reordered a precommitted seed/truth")
    for r in rows:
        if r.get("robot")!=robot or r.get("private_target_read_calls_before_decision")!=0:
            raise ValueError("Wrong physical robot or private goal contamination")
        if r.get("native_controller_keys")!=(
            ["arm","gripper"] if robot=="panda" else
            ["arm","gripper_active","gripper_passive"]):
            raise ValueError("Mismatched actual robot controller")
        if r.get("unchanged_zero_native_probe_step")!=3:
            raise ValueError("Calibration did not perform physical native zero probe")
    training=[dict(robot=r["robot"],seed=r["seed"],truth=r["hidden_truth"],
                   delta_public_xyz=r["delta_public_xyz"]) for r in rows]
    fitted=train(training,robot)
    if fitted!=source.get("model"):
        raise ValueError("Fitted envelope changed after full calibration cases")
    return fitted


def trial(data,robot,chunk,model):
    first=FRESH[robot]+chunk*4
    seeds=list(range(first,first+4))
    if (data.get("schema")!="cross_robot_online_unknown_ack_proprio_prospective_v1"
        or data.get("robot")!=robot or data.get("chunk")!=chunk
        or data.get("test_seeds")!=seeds
        or data.get("source_protocol_git_blob")!=PROTO_SHA
        or data.get("physical_trial_truth_cases")!=8
        or data.get("real_cpu_physx") is not True
        or data.get("private_target_getter_only_after_corrective_action") is not True
        or data.get("scripted_native_control_not_policy_transfer") is not True
        or data.get("original_frozen_checkpoint_used") is not False
        or data.get("no_actual_network_packet_loss") is not True
        or data.get("not_independent_outside_lab") is not True
        or data.get("model")!=model
        or data.get("calibration_model_hash")!=hashlib.sha256(
            json.dumps(model,sort_keys=True).encode()).hexdigest()):
        raise ValueError("Wrong original robot/frozen training model/provenance")
    rows=data.get("rows")
    if (not isinstance(rows,list) or len(rows)!=8
        or [(r.get("seed"),r.get("truth")) for r in rows] !=
        [(seed,truth) for seed in seeds for truth in LABELS]):
        raise ValueError("All eight paired NEW original physical truths mandatory")
    totals={name:{"confident":0,"wrong":0,"actual_held_target_position_restored":0}
            for name in ARMS}
    for row in rows:
        arms=row.get("independently_real_physx_stepped_arms")
        if not isinstance(arms,list) or len(arms)!=3 or row.get("one_online_public_measurement_per_arm") is not True:
            raise ValueError("Three physical comparator controllers required")
        for i,(name,actual) in enumerate(zip(ARMS,arms)):
            if (actual.get("robot")!=robot or actual.get("seed")!=row["seed"]
                or actual.get("hidden_truth")!=row["truth"]
                or actual.get("control")!=name or
                actual.get("native_controller_keys") !=
                (["arm","gripper"] if robot=="panda" else
                 ["arm","gripper_active","gripper_passive"])
                or actual.get("private_target_read_calls_before_decision")!=0
                or actual.get("unchanged_zero_native_probe_step")!=3):
                raise ValueError("Nonoriginal robot controller, result or private data")
            old=actual.get("public_t1_xyz")
            new=actual.get("public_t3_xyz")
            d=actual.get("delta_public_xyz")
            if any(not isinstance(v,list) or len(v)!=3 or
                   any(type(x) not in (int,float) or not math.isfinite(x) for x in v)
                   for v in (old,new,d)):
                raise ValueError("Unverified public achieved kinematic inputs")
            if max(abs(n-o-v) for n,o,v in zip(new,old,d))>1e-7:
                raise ValueError("Public achieved XYZ delta forged")
            declared=actual.get("decision")
            predicted=(decide(d,model) if name=="public_proprio_empirical"
                       else {"label":"applied" if i==1 else "held",
                             "status":"NO_PHYSICAL_RESPONSE_USED",
                             "private_target_getter_calls_at_decision":0})
            if declared!=predicted:
                raise ValueError("Public-only online decision or blind guessed label changed")
            guessed=predicted["label"]
            refused=guessed is None
            if actual.get("corrective_refusal") is not refused:
                raise ValueError("Wrong refusal or silent advance")
            if actual.get("wrong_history_authorization") is not (
                    None if refused else guessed!=row["truth"]):
                raise ValueError("Incorrect latent ACK authorization scoring")
            if actual.get("correction_reached") is refused:
                raise ValueError("Claimed correction without/against decision")
            if not refused:
                error=actual.get("corrective_target_position_error_m")
                if (type(error) not in (int,float) or not math.isfinite(error)
                    or error<0):
                    raise ValueError("Missing actual post-step target controller audit")
                if actual.get("corrective_commanded_target_within_1e4_m") is not (error<=1e-4):
                    raise ValueError("Physical corrective commanded target falsely scored")
                native=actual.get("corrective_native_six")
                if (not isinstance(native,list) or len(native)!=6 or
                    any(not math.isfinite(x) or abs(x)>1+1e-5 for x in native)):
                    raise ValueError("Invalid corrected legal native action")
            elif (actual.get("corrective_target_position_error_m") is not None
                  or actual.get("corrective_commanded_target_within_1e4_m") is not False):
                raise ValueError("A refused unexecuted correction cannot count success")
            totals[name]["confident"]+=int(not refused)
            totals[name]["wrong"]+=int(actual["wrong_history_authorization"] is True)
            totals[name]["actual_held_target_position_restored"]+=int(
                actual["corrective_commanded_target_within_1e4_m"] is True)
        for other in arms[1:]:
            if max(abs(x-y) for x,y in zip(arms[0]["delta_public_xyz"],other["delta_public_xyz"]))>1e-4:
                raise ValueError("Same seed/fault did not produce equal physical probe responses")
    if totals!=data.get("totals"):
        raise ValueError("Original source success/abstention/wrong count changed")
    return totals


def audit(folder):
    expected={f"cross_robot_proprio_calibration_{r}.json" for r in OLD}
    expected.update(f"cross_robot_proprio_{r}_chunk{c}_original8.json"
                    for r in OLD for c in (0,1))
    files=[p for p in folder.glob("cross_robot_proprio_*.json")]
    if len(files)!=6 or {p.name for p in files}!=expected:
        raise ValueError("Two exact calibrations and all four 8-test physical source shards required")
    data={}
    for robot in OLD:
        model=calibration(json.loads((folder/f"cross_robot_proprio_calibration_{robot}.json").read_text()),robot)
        for chunk in (0,1):
            key=f"{robot}:chunk{chunk}"
            raw=json.loads((folder/f"cross_robot_proprio_{robot}_chunk{chunk}_original8.json").read_text())
            data[key]=trial(raw,robot,chunk,model)
    return {"schema":"cross_robot_online_unknown_ack_full32_source_audit_v1",
            "source_fresh_truth_conditions":32,"two_real_robot_morphologies":True,
            "untrained_scripted_native_commands_not_cross_robot_PPO":True,
            "contributor_executed_not_outside_replication":True,
            "not_network_loss_or_robot_safety":True,"results":data}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=audit(a.input_dir)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("CROSS_ROBOT_ONLINE_ACK_FULL32_SOURCE_AUDIT",json.dumps(d,sort_keys=True))

if __name__=="__main__":main()

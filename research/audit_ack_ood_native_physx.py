"""Strict original full-population real PhysX OOD-ACK evaluation/auditor.

Independent of ManiSkill/Torch. Replays BOTH public classifiers and every
source native-world correction flag; no successful-seed filtering. Reports
wrong confident history authorization separately from physical correction.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from research.cross_robot_online_proprio_classifier import decide,train
from research.ood_ack_motion_response import predict_ood_public_history

BASE={("panda","low"):680001,("panda","high"):681001,
      ("xarm6_robotiq","low"):690001,("xarm6_robotiq","high"):691001}
FACTOR={"low":0.55,"high":1.45}
METHODS=("frozen_old_empirical","gain_segment_empirical","blind_optimistic","blind_pessimistic")
MODELS_SHA={"panda":"f41bd0cc010cdcaf836a6d8ba2722313baf692d3",
             "xarm6_robotiq":"e8ec9c607059c3e538d2e1bfe35f0fdf1bd89830"}
PROTO_SHA="d1f017d8ca994ec6be62daf3dc6940f038b8dff4"
ORIGINAL_DATA=Path("research/frozen_policy_transfer/evidence/"
   "cross_robot_online_public_proprio_new32_480001_490008")

def _git_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()

def locked_training(robot):
    f=ORIGINAL_DATA/f"cross_robot_proprio_calibration_{robot}.json"
    if _git_sha(f.read_bytes())!=MODELS_SHA[robot]:
        raise ValueError("Prior native calibration Git object modified")
    data=json.loads(f.read_text())
    source=data["calibration_source_rows"]
    inp=[dict(robot=r["robot"],seed=r["seed"],truth=r["hidden_truth"],
              delta_public_xyz=r["delta_public_xyz"]) for r in source]
    if len(inp)!=16 or train(inp,robot)!=data.get("model"):
        raise ValueError("Frozen prior calibration not reproducible")
    return data["model"]

def check_row(r,*,robot,scale,seed,truth,method,model):
    if (r.get("robot")!=robot or r.get("seed")!=seed or
        r.get("truth")!=truth or r.get("method")!=method or
        r.get("native_scale")!=FACTOR[scale] or
        r.get("fault_native_zero_physically_dispatched") is not (truth=="held") or
        r.get("native_t3_known_delivered_probe_6d")!=[0.]*6 or
        r.get("private_target_calls_at_decision")!=0 or
        r.get("model_sha256")!=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()):
        raise ValueError("Changed native source/provenance or fabricated private read")
    for vname in ("native_t2_requested_6d","public_t1_xyz","public_t3_before_xyz",
                  "public_t3_after_xyz","old_method_delta_public_t1_t3"):
        a=r[vname]
        n=6 if vname=="native_t2_requested_6d" else 3
        if len(a)!=n or any(type(z) not in (float,int) or not math.isfinite(z) for z in a):
            raise ValueError("Missing original physical finite native/pose vector")
    if len(r["public_hypothesis_target_xyz"])!=2:
        raise ValueError("Missing one hidden commanded-target history")
    before=r["public_t3_before_xyz"]
    after=r["public_t3_after_xyz"]
    old=[a-b for a,b in zip(after,r["public_t1_xyz"])]
    if max(abs(a-b) for a,b in zip(old,r["old_method_delta_public_t1_t3"]))>1e-7:
        raise ValueError("Public pose delta does not match physical source")
    current=[a-b for a,b in zip(after,before)]
    if max(abs(a-b) for a,b in zip(current,r["public_response_current_probe_delta"]))>1e-7:
        raise ValueError("Current-probe physical public delta fake")
    native_expected=[0.45*FACTOR[scale],-.3*FACTOR[scale],
                      .35*FACTOR[scale],.25*FACTOR[scale],
                      -.12*FACTOR[scale],.1*FACTOR[scale]]
    if max(abs(a-b) for a,b in zip(native_expected,r["native_t2_requested_6d"]))>1e-9:
        raise ValueError("Fault amplitude was not prospectively declared")
    if method=="frozen_old_empirical":
        predicted=decide(old,model)
    elif method=="gain_segment_empirical":
        predicted=predict_ood_public_history(
            robot=robot,public_before_xyz=before,public_after_xyz=after,
            applied_history_target_xyz=r["public_hypothesis_target_xyz"]["applied"],
            held_history_target_xyz=r["public_hypothesis_target_xyz"]["held"])
    else:
        predicted={"label":"applied" if method=="blind_optimistic" else "held",
                   "status":"FIXED_NO_PUBLIC_DECISION",
                   "no_privileged_state_reads_for_inference":True}
    if r["decision"]!=predicted:
        raise ValueError("Original public-only decision modified after knowing hidden truth")
    label=predicted["label"]
    if r["wrong_confident_history_label"] is not (None if label is None else label!=truth):
        raise ValueError("Wrong confident latent ACK authorization scored incorrectly")
    if r["refusal"] is not (label is None):
        raise ValueError("Original abstention omitted")
    if r["corrective_action_executed"] is not (label is not None):
        raise ValueError("Unexecuted native actuation counted")
    if label is not None:
        u=r.get("corrective_native_6d")
        if len(u)!=6 or not all(math.isfinite(z) and abs(z)<=1+1e-5 for z in u):
            raise ValueError("Invalid native action in true robot")
        e=r["after_physics_private_target_position_error_m"]
        if not isinstance(e,(float,int)) or not math.isfinite(e) or e<0:
            raise ValueError("Missing genuine post-action controller target audit")
        if r["correct_commanded_target_POSITION_only"] is not (e<=1e-4):
            raise ValueError("Result does not match physically recorded native target")
    elif (r["after_physics_private_target_position_error_m"] is not None or
          r["correct_commanded_target_POSITION_only"] is not False):
        raise ValueError("Cannot count refused actuator action as corrected")
    return (label is not None, label is not None and label!=truth,
            r["correct_commanded_target_POSITION_only"])

def audit(folder):
    expected={f"ood_ack_{robot}_{scale}_chunk{chunk}_original8.json"
              for robot,scale in BASE for chunk in (0,1)}
    got={f.name for f in folder.glob("ood_ack_*_original8.json")}
    if got!=expected:
        raise ValueError("Missing or duplicated source physical native trial shard")
    models={robot:locked_training(robot) for robot,_ in BASE}
    result={}
    all_rows=0
    for robot,scale in BASE:
        model=models[robot]
        tally={name:{"confident":0,"wrong":0,"restored":0,"refused":0} for name in METHODS}
        for chunk in (0,1):
            file=folder/f"ood_ack_{robot}_{scale}_chunk{chunk}_original8.json"
            source=json.loads(file.read_text())
            seeds=list(range(BASE[(robot,scale)]+4*chunk,
                             BASE[(robot,scale)]+4*chunk+4))
            if (source.get("schema")!="ack_ood_native_amplitude_physx_v1"
                or source.get("protocol_git_blob")!=PROTO_SHA
                or source.get("robot")!=robot or source.get("scale")!=scale
                or source.get("scale_factor")!=FACTOR[scale]
                or source.get("chunk")!=chunk or source.get("seeds")!=seeds
                or source.get("source_model_Git_blob")!=MODELS_SHA[robot]
                or source.get("physical_truth_conditions")!=8
                or source.get("physical_comparator_worlds")!=32
                or source.get("real_physx_cpu") is not True
                or source.get("no_ppo_checkpoint_or_task_success_measured") is not True):
                raise ValueError("Tampered native protocol/fault/model/controller job")
            rows=source.get("rows",[])
            if len(rows)!=8 or [(r.get("seed"),r.get("truth")) for r in rows]!=[
                    (seed,truth) for seed in seeds for truth in ("applied","held")]:
                raise ValueError("Missing physically realized applied/held source")
            for row in rows:
                arms=row.get("actual_native_physical_controllers",[])
                if len(arms)!=4:
                    raise ValueError("Missing one of four genuine PhysX competitors")
                if len({tuple(x["public_t3_after_xyz"]) for x in arms})!=1:
                    # Allow original PhysX float nondeterminism up to existing tolerance
                    ref=arms[0]["public_t3_after_xyz"]
                    if any(max(abs(a-b) for a,b in zip(ref,x["public_t3_after_xyz"]))>1e-4
                           for x in arms[1:]):
                        raise ValueError("Different physical motion for paired comparator seed")
                for i,method in enumerate(METHODS):
                    confident,wrong,restored=check_row(arms[i],robot=robot,
                        scale=scale,seed=row["seed"],truth=row["truth"],
                        method=method,model=model)
                    tally[method]["confident"]+=int(confident)
                    tally[method]["wrong"]+=int(wrong)
                    tally[method]["refused"]+=int(not confident)
                    tally[method]["restored"]+=int(restored)
                all_rows+=1
        result[f"{robot}/{scale}"]=tally
    if all_rows!=64:
        raise ValueError("Incorrect total distinct robot/scale/seed/truth physical cases")
    return dict(schema="strict_source_frozen_ood_ack_all64_v1",
                distinct_robot_seed_scale_conditions=32,
                physically_realized_ack_truth_cases=64,
                separately_actuated_physx_worlds=256,
                prior_labels_not_updated_using_new_truths=True,
                no_private_target_reads_in_decision=True,
                NO_PPO_TASK_SUCCESS_CLAIM=True,
                empirical_NOT_safety_certified=True,
                by_robot_scale=result)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    data=audit(a.input_dir)
    a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("REAL_PHYSX_OOD_ACK_UNTOUCHED64",json.dumps(data,sort_keys=True),flush=True)

if __name__=="__main__":
    main()

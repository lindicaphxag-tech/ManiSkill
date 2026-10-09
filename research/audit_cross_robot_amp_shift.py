"""Read-only independent full-source verifier for PhysX amplitude OOD ACK study.

Recomputes ALL confidence labels from published prior calibration and the
actual recorded PUBLIC motion response, not published score summaries. All
negative/confident-wrong and abstain states remain in the 32-case denominator.
No simulator dependency.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from research.cross_robot_online_proprio_classifier import LABELS,train
from research.cross_robot_ack_amplitude_inference import predict

ORIGINAL_ARCHIVE=Path("research/frozen_policy_transfer/evidence/cross_robot_online_public_proprio_new32_480001_490008")
PREREG="24ac966eecb765a609b3f5601c755216b24501c3"
ROBOT={"panda":540001,"xarm6_robotiq":550001}
SCALES={"shift040":0.4,"nominal100":1.0}
ARMS=("frozen_scale1","command_affine","optimistic_applied","pessimistic_held")

def model_from_immutable_old_calibration(robot):
    cal=json.loads((ORIGINAL_ARCHIVE/f"cross_robot_proprio_calibration_{robot}.json").read_text())
    a=[dict(robot=r["robot"],seed=r["seed"],truth=r["hidden_truth"],delta_public_xyz=r["delta_public_xyz"])
       for r in cal["calibration_source_rows"]]
    model=train(a,robot)
    if model!=cal["model"]:
        raise ValueError("Original physical calibration was tampered with")
    return model

def validate(data,robot,tag,model):
    amp=SCALES[tag]
    seeds=list(range(ROBOT[robot],ROBOT[robot]+4))
    modelsha=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()
    if (data.get("schema")!="cross_robot_ack_amplitude_shift_falsifier_original_physx_v1"
        or data.get("preregistration")!="research/CROSS_ROBOT_ACK_AMPLITUDE_SHIFT_PREOUTCOME_V1.json"
        or data.get("prereg_git_blob")!=PREREG or data.get("robot")!=robot
        or data.get("amplitude_tag")!=tag or data.get("amplitude")!=amp
        or data.get("seeds")!=seeds or data.get("prior_model_sha256")!=modelsha
        or data.get("prior_model_fixed") is not True
        or data.get("physx_cpu") is not True
        or data.get("no_predecision_private_target") is not True
        or data.get("all_four_controls_real_native_physx") is not True
        or data.get("total_truth_cases")!=8):
        raise ValueError("Altered preoutcome protocol/model/physics provenance")
    rows=data.get("rows")
    pairs=[(seed,t) for seed in seeds for t in LABELS]
    if not isinstance(rows,list) or [(r.get("seed"),r.get("physical_truth")) for r in rows]!=pairs:
        raise ValueError("Missing/reordered original seed × applied/held truth worlds")
    total={name:{"authorized":0,"wrong_history":0,"target_position_restored":0}
           for name in ARMS}
    for row in rows:
        if row.get("amplitude")!=amp or row.get("robot")!=robot:
            raise ValueError("Wrong original per-case native physical truth")
        truth=row["physical_truth"]
        controls=row.get("four_actual_physx_control_worlds",[])
        if len(controls)!=len(ARMS) or [c.get("control") for c in controls]!=list(ARMS):
            raise ValueError("Missing/altered physically stepped comparison arms")
        public_reference=controls[0].get("public_motion_delta_xyz")
        for c,name in zip(controls,ARMS):
            if (c.get("seed")!=row["seed"] or c.get("robot")!=robot or c.get("truth")!=truth
                or c.get("amplitude")!=amp or c.get("private_target_reads_before_and_during_decision")!=0
                or c.get("original_model_not_refit") is not True):
                raise ValueError("Unauthorized target read or mismatched control-world episode")
            v=c.get("public_motion_delta_xyz",[])
            if (len(v)!=3 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in v)
                or max(abs(v[i]-public_reference[i]) for i in range(3))>1e-4):
                raise ValueError("Nonpaired public physical response; cannot compare labels")
            request=c.get("action_native_t2_requested",[])
            delivered=c.get("action_native_t2_physical",[])
            announced=[0.45,-0.3,0.35,0.25,-0.12,0.1]
            if len(request)!=6 or len(delivered)!=6 or any(abs(request[i]-announced[i]*amp)>1e-6 or
                   abs(delivered[i]-(request[i] if truth=="applied" else 0.))>1e-6 for i in range(6)):
                raise ValueError("Original requested/applied/held arm command truths altered")
            if c.get("probe_native_t3")!=[0.]*6:
                raise ValueError("Information-gathering probe was retuned")
            guess=c.get("inference",{}).get("label")
            if name in ("frozen_scale1","command_affine"):
                reproduced=predict(v,model,amp,name)
                if c["inference"]!=reproduced:
                    raise ValueError("Selective authorization not reproduced independently from public sensor")
            elif guess!=("applied" if name=="optimistic_applied" else "held"):
                raise ValueError("Uninformed controls no longer fixed guesses")
            if (guess not in ("applied","held",None)
                or c.get("incorrect_confident_history_authorization") is not
                 (None if guess is None else guess!=truth)
                or c.get("refused_due_ambiguous_history") is not (guess is None)
                or c.get("correction_physically_executed") is not (guess is not None)):
                raise ValueError("Wrong history authorization/abstention was hidden or changed")
            success=c.get("commanded_target_restored_within_1e4_m")
            if type(success) is not bool:
                raise ValueError("Missing real commanded target correctness")
            if guess is None:
                if success or c.get("corrected_target_position_linf_m") is not None:
                    raise ValueError("Refusal fabricated target-position correctness")
            else:
                err=c.get("corrected_target_position_linf_m")
                if (not isinstance(err,(float,int)) or not math.isfinite(err) or err<0
                    or success!=(err<=1e-4)):
                    raise ValueError("After-physics target audit not consistent")
            total[name]["authorized"]+=int(guess is not None)
            total[name]["wrong_history"]+=int(guess is not None and guess!=truth)
            total[name]["target_position_restored"]+=int(success)
    if total!=data.get("totals"):
        raise ValueError("Summary disagrees with full source physical truth trials")
    return {"n_truth_cases":8,"outcomes":total}

def aggregate(folder):
    expected={f"cross_robot_amp_{robot}_{tag}_original8.json" for robot in ROBOT for tag in SCALES}
    files=list(folder.glob("cross_robot_amp_*_original8.json"))
    if len(files)!=4 or {p.name for p in files}!=expected:
        raise ValueError("All FOUR original Panda/xArm6 × amplitude files required")
    out={}
    for robot in ROBOT:
        model=model_from_immutable_old_calibration(robot)
        for tag in SCALES:
            key=f"{robot}:{tag}"
            out[key]=validate(json.loads((folder/f"cross_robot_amp_{robot}_{tag}_original8.json").read_text()),robot,tag,model)
    return {"schema":"cross_robot_physical_command_amplitude_shift_full_source_audit_v1",
            "source_truth_conditions":32,
            "genuine_real_physx_worlds":128,
            "original_trained_ppo_checkpoints":0,
            "no_external_independent_replication":True,
            "not_robot_safety_or_network_delay":True,
            "results":out}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=aggregate(a.input_dir)
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("CROSS_ROBOT_AMP_SHIFT_FULL_AUDIT",json.dumps(r["results"],sort_keys=True),flush=True)
if __name__=="__main__":
    main()

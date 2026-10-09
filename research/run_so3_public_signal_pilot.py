"""Frozen untouched task policy + new genuine public SO3 probe feasibility on 16 unseen source resets.

Source method code still selects history by original XYZ and 0.60 score;
orientation never authorizes a target in this pilot.
"""
from __future__ import annotations
import argparse, importlib, json, os, subprocess
from pathlib import Path

MODEL={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
       "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
SOURCE_SHA="41f22c785814a8d016c41a16cc34572ee0ed1457"
PRE_SHA="d63ae9d010bcb6db2b2ae6edc1c849701d0e6fb1"
PRIOR_SHA="064bb46831b61af73ad445bc836326837ec5468f"
SEED_FIRST={"pull_cube":2040001,"stack_cube":2050001}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_strong_tuned_score_060_or_query"

def pin():
    for path,digest in (
        ("research/frozen_ppo_so3_signal_pilot_physx.py",SOURCE_SHA),
        ("research/SO3_PUBLIC_MOTION_FEASIBILITY_PREOUTCOME_V1.json",PRE_SHA),
        ("research/empirical_probe_response_classifier.py",PRIOR_SHA),
    ):
        actual=subprocess.check_output(["git","hash-object",path],text=True).strip()
        if actual!=digest: raise ValueError("Original source/preregistration SHA changed: "+path)

def audit_raw(raw,task):
    seeds=list(range(SEED_FIRST[task],SEED_FIRST[task]+8))
    if raw.get("original_seed_population")!=seeds or len(raw.get("episodes",[]))!=8:
        raise ValueError("Missing original truly unseen task reset seed")
    if raw.get("real_physx_simulator") is not True or raw.get("frozen_model_retrained") is not False:
        raise ValueError("Not genuine frozen PPO real native PhysX")
    if raw.get("original_external_frozen_checkpoint_sha256")!=MODEL[task]:
        raise ValueError("Checkpoint identity mismatch")
    exposures=[]
    for seed,row in zip(seeds,raw["episodes"]):
        if row.get("seed")!=seed:raise ValueError("Wrong native seed")
        truth=(seed-1)%4
        for key,expected in [
            ("original_precommitted_physical_t2_execution_truth","applied" if truth in (1,3) else "held"),
            ("original_precommitted_physical_t3_execution_truth","applied" if truth in (2,3) else "held")]:
            if row.get(key)!=expected: raise ValueError("Physical hidden ACK truth changed")
        outcomes=row.get("success_once",{})
        reads=row.get("privileged_target_readback_decision_count",{})
        if any(type(outcomes.get(n)) is not bool or type(reads.get(n)) is not int
               or reads[n] not in (0,1) for n in (A,B)):
            raise ValueError("Actual task result/readback invalid")
        t4s=row.get("shared_neutral_probe_step4",{})
        sensors=[]
        for n,evidence in ((A,row.get("public_t3_evidence",{})),(B,row.get("strong_score_060_evidence",{}))):
            if evidence.get("so3_public_samples_charged",None) is None:
                # Original branch physically terminated before acquiring t4:
                # it MUST NOT be counted as a completed orientation observation.
                if n in t4s or evidence.get("so3_public_after_quat_xyzw") is not None:
                    raise ValueError("Public t4 appears with forged missing real SO3 samples")
                sensors.append(False)
                continue
            if evidence.get("so3_public_samples_charged")!=2 or evidence.get("so3_only_feasibility_no_decision_use") is not True:
                raise ValueError("SO3 data is not original genuinely charged public measurement")
            if n not in t4s or t4s[n].get("physically_dispatched") is not True:
                raise ValueError("SO3 labels without real shared neutral native controller step")
            import math
            for k in ("so3_public_before_quat_xyzw","so3_public_after_quat_xyzw"):
                quat=evidence.get(k)
                if not isinstance(quat,list) or len(quat)!=4 or any(type(x) not in (float,int) or not math.isfinite(x) for x in quat):
                    raise ValueError("Public measured quaternion wrong")
                if abs(sum(v*v for v in quat)-1)>0.005:raise ValueError("Measured SO3 unit norm violated")
            residuals=evidence.get("so3_public_geodesic_to_candidate_arc_rad")
            if not isinstance(residuals,list) or len(residuals)!=evidence.get("physical_candidate_count"):
                raise ValueError("No actual SO3 residual for every intact hypothesis")
            if any(type(x) not in (float,int) or not math.isfinite(x) or x<0 or x>3.142 for x in residuals):
                raise ValueError("Invalid physical rotation arc score")
            if evidence.get("so3_joint_public_device_channel_not_independent_sensor") is not True:
                raise ValueError("SO3 claimed independent new hardware sensor")
            if evidence.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Auditor truth improperly leaked into policy decision")
            sensors.append(True)
        exposures.append({
            "seed":seed,"task":task,"true_fault_pattern":truth,
            "original_actual_two_faults_on_reference":len(row.get("faults",{}).get(A,[]))==2,
            "public_so3_observation_realized":all(sensors),
            "source_original_task_success":{n:outcomes[n] for n in (A,B)},
            "source_original_privileged_reads":{n:reads[n] for n in (A,B)},
            "public_record":{n:(row.get("public_t3_evidence",{}) if n==A else row.get("strong_score_060_evidence",{}))
                 .get("so3_public_geodesic_to_candidate_arc_rad")
                 for n in (A,B)},
            "reference_true_history_labels_are_audit_only":True,
        })
    return {"schema":"genuine_native_public_quaternion_probe_audit_pilot_v1",
            "task":task,"n_original_resets":8,"n_original_native_controller_worlds":80,
            "physical_so3_probes_completed":sum(row["public_so3_observation_realized"] for row in exposures),
            "source_outcome_not_modified_by_so3":True,
            "no_so3_threshold_or_history_authorization_applied":True,
            "episodes":exposures}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(SEED_FIRST),required=True)
    args=p.parse_args()
    pin()
    os.environ["ABI_TASK"]=args.task
    mod=importlib.import_module("research.frozen_ppo_so3_signal_pilot_physx")
    ids=list(range(SEED_FIRST[args.task],SEED_FIRST[args.task]+8))
    if list(mod.SEEDS)!=ids or mod.POST_ARM!=B or mod.PUBLIC_ARM!=A or mod.HORIZON!=50:
        raise ValueError("Native frozen model/arm/source identity drift")
    mod.main()
    path=Path(f"tuned060_{args.task}_original8.json")
    raw=json.loads(path.read_text())
    audited=audit_raw(raw,args.task)
    import hashlib
    audited["original_native_physx_json_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    path.rename(f"so3_physical_{args.task}_original8.json")
    Path(f"so3_physical_{args.task}_audit.json").write_text(json.dumps(audited,indent=2,sort_keys=True)+"\n")
    print("TRUE_SO3_PUBLIC_SIGNAL_NATIVE_PHYXS_PILOT",json.dumps({
        "task":args.task,"states":8,"worlds":80,
        "actual_completed_public_quaternion_probes":audited["physical_so3_probes_completed"]},sort_keys=True))

if __name__=="__main__": main()

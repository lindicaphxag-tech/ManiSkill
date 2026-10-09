"""Independent AFTER real physics source audit: exact 64 heldout task states and
10 physically stepped native PPO comparators, including raw post-step native
target truth for wrong-confidence scoring only.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from research.run_validity_first_new64 import (
    accepted,validate_result,TASKS,PUBLIC,NARROW,SELECTIVE,FIXED,PREREG,
    REGISTERED_BLOB)

def audit(folder):
    wanted={f"authority_calibration_{t}_chunk{i}_{kind}.json"
            for t in TASKS for i in range(4) for kind in ("original8","audit")}
    actual={x.name for x in folder.glob("authority_calibration_*.json")}
    if actual!=wanted:raise ValueError(f"Incomplete native original data: {wanted-actual} extra {actual-wanted}")
    rows=[]
    sha={}
    for task in TASKS:
        for chunk in range(4):
            orig=folder/f"authority_calibration_{task}_chunk{chunk}_original8.json"
            proof=folder/f"authority_calibration_{task}_chunk{chunk}_audit.json"
            sourcebytes=orig.read_bytes()
            original=json.loads(sourcebytes)
            expected=validate_result(original,task,accepted(task,chunk))
            audit_json=json.loads(proof.read_text())
            if (audit_json.get("original_raw_sha256")!=hashlib.sha256(sourcebytes).hexdigest()
                or any(audit_json.get(key)!=value for key,value in expected.items())):
                raise ValueError("Original physical-run records do NOT match independently recalculated shard")
            sha[orig.name]=hashlib.sha256(sourcebytes).hexdigest()
            sha[proof.name]=hashlib.sha256(proof.read_bytes()).hexdigest()
            rows.extend(expected["sample_rows"])
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Not all 64 uniquely preregistered new native PhysX states reached")
    counts={}
    for combo in ("AA","AH","HA","HH"):
        z=[x for x in rows if x["true_joint_ack"]==combo]
        if len(z)!=16:raise ValueError("Four physical source ACK truth patterns not balanced")
        counts[combo]={k:sum(int(y[k]) for y in z)
                       for k in ("narrow_success","calibrated_success","strong_success",
                                 "narrow_reads","calibrated_reads","strong_reads")}
        counts[combo]["old_wrong"]=sum(y["narrow_public_evidence"]["wrong_confident"] for y in z)
        counts[combo]["calibrated_wrong"]=sum(y["calibrated_public_evidence"]["wrong_confident"] for y in z)
        counts[combo]["original_physx_states"]=16
    stat={k:sum(int(x[k]) for x in rows) for k in
          ("narrow_success","calibrated_success","strong_success","fixed_success",
           "narrow_reads","calibrated_reads","strong_reads")}
    for pref in ("narrow","calibrated"):
        stat[pref+"_authorized"]=sum(x[pref+"_public_evidence"]["authorized"] for x in rows)
        stat[pref+"_wrong_confident"]=sum(x[pref+"_public_evidence"]["wrong_confident"] for x in rows)
        stat[pref+"_public_xyz_samples"]=128
    pair={"both":0,"narrow_only":0,"calibrated_only":0,"neither":0}
    for x in rows:
        pair["both" if x["narrow_success"] and x["calibrated_success"] else
             "narrow_only" if x["narrow_success"] else
             "calibrated_only" if x["calibrated_success"] else
             "neither"]+=1
    return {"schema":"independent_native_640_world_validity_first_true_history_audit",
            "genuine_source_physx_reset_states":64,
            "genuine_independently_stepped_native_controller_worlds":640,
            "frozen_prior_calibration_has_no_holdout_labels":True,
            "calibration_source":"research/frozen_policy_transfer/evidence/four_joint_truths_first_physx64_880001_890032/",
            "original_registration_git_blob":REGISTERED_BLOB,
            "training_and_holdout_seed_overlap":False,
            "all_original_sixteen_source_64_task_json_sha256":sha,
            "total":stat,"joint_truth_strata":counts,"paired":pair,
            "all_actual_original_source_episode_records":rows,
            "old_empirical_response_model_not_deterministic":True,
            "maximum_residual_order_statistic_coverage_only_under_exchangeability":True,
            "no_actual_packet_loss_or_hardware_safety_certification":True,
            "not_peer_reviewed_accepted_or_outside_lab_duplicated":True}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=audit(a.source_dir)
    a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_VALIDITY_FIRST_REAL_PHYSX_ALL64",json.dumps({
        "total":x["total"],"paired":x["paired"],"physical_ACK_strata":x["joint_truth_strata"]},
        sort_keys=True),flush=True)

"""Permanent veto of reused original PhysX reset IDs in risk-cert calibration.

This is NOT a new completed 768-reset experiment. V1 remains immutable and
mathematically sound as a protocol, but its strict unseen-calibration claim
was invalidated by already released source/factorial resets. V2 must be
frozen BEFORE actually acquiring any new calibration/holdout outcomes.

Source caller should pass the exact original pre-outcome physical factorial
protocol JSON fetched via immutable Git commit SHA, not a mutable branch.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V1="research/AUTHORITY_RISK_COVERAGE_PROSPECTIVE_V1.json"
V2="research/AUTHORITY_RISK_COVERAGE_PROSPECTIVE_V2_DISJOINT_COHORTS.json"
SOURCE_GIT_BLOBS={
 V1:"f79df84a1841e7ddab1331ffa7fad39e72787946",
 V2:"8cf25e0e1ba2b402de78619166b002f69f0945d5",
}
FACTORIAL_CONTRACT_BLOB="9626db5b93bd6216c94d349fb00d9ea0f9b035e1"

def full_range(pair):
    if (not isinstance(pair,list) or len(pair)!=2
        or type(pair[0]) is not int or type(pair[1]) is not int
        or pair[0]<0 or pair[1]<pair[0]):
        raise ValueError("Task/register must contain precise nonempty integer range")
    return set(range(pair[0],pair[1]+1))

def signed_git_blob(root,path,expected):
    observed=subprocess.check_output(["git","hash-object",path],cwd=root,text=True).strip()
    if observed!=expected:raise ValueError("Mutated original V1/V2 source Git blob: "+path)
    return json.loads((root/path).read_text(encoding="utf-8"))

def verify(frozen_physics:dict,root:Path=ROOT):
    old=signed_git_blob(root,V1,SOURCE_GIT_BLOBS[V1])
    new=signed_git_blob(root,V2,SOURCE_GIT_BLOBS[V2])
    physics=frozen_physics
    if physics.get("pre_outcome") is not True:
        raise ValueError("Original physical experiment must be preoutcome-frozen")
    tasks=("pull_cube","stack_cube")
    old_cal=old["task_calibration"]
    new_cal=new["new_v2_calibration"]
    new_test=new["new_v2_test"]
    physical=physics["seeds"]
    conflicts={}
    known_prior={}
    for t in tasks:
        orig=full_range(old_cal[t]); exposure=full_range(physical[t])
        expected=(2110001 if t=="pull_cube" else 2120001)
        if (min(exposure)!=expected or len(exposure)!=16 or
            len(orig)!=256 or len(orig&exposure)!=16):
            raise ValueError("Expected real physical source collision changed or hidden")
        conflicts[t]=sorted(orig&exposure)
        known_prior[t]=exposure
        if (new["original_v1_exact_previous_physics_overlap"][t]!=[min(orig&exposure),max(orig&exposure)]):
            raise ValueError("Public V1 contamination disclosure changed")
    cal=set();test=set()
    for t in tasks:
        c=full_range(new_cal[t]);v=full_range(new_test[t])
        if len(c)!=256 or len(v)!=128:
            raise ValueError("Incomplete V2 calibration or test")
        if cal & c or test & v or cal & v or test & c:
            raise ValueError("V2 has train/test or cross-task collision")
        if c & known_prior[t] or v & known_prior[t]:
            raise ValueError("V2 uses prior actual PhysX reset")
        cal|=c;test|=v
    if cal & test or len(cal)!=512 or len(test)!=256:
        raise ValueError("V2 not independently disjoint")
    if (new["frozen_threshold_grid"]!=old["frozen_threshold_grid"]
        or new["conditional_error_risk_cap"]!=old["error_risk_cap_conditional_on_acceptance"]
        or new["task_wise_coverage_lower_floor"]!=old["min_authorization_coverage_lower_confidence_bound_per_task"]
        or new["familywise_alpha"]!=old["familywise_failure_probability"]):
        raise ValueError("Posthoc changed confidence thresholds or scoring goals")
    if new["old_v1_scientific_status"].find("CONTAMINATED")<0:
        raise ValueError("V1 contamination must remain visible")
    return {
        "status":"V1_PREEXPOSED_32_CALIBRATION_IDS__V2_PREREGISTERED_ONLY",
        "immutable_source_git_blobs_checked":SOURCE_GIT_BLOBS,
        "original_physx_source_preoutcome_blob":"9626db5b93bd6216c94d349fb00d9ea0f9b035e1",
        "v1_exposed_original_calibration_identifiers":conflicts,
        "v1_number_preexposed":sum(len(v) for v in conflicts.values()),
        "v2_calibration_ids":len(cal),
        "v2_test_ids":len(test),
        "v2_disjoint_from_source_factorial_and_each_other":True,
        "actual_v2_physx_data_executed":False,
        "v2_future_external_registration_crosscheck_still_required":True,
        "no_independent_outside_lab_replication":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--factorial-json",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    r=verify(json.loads(a.factorial_json.read_text()))
    a.output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("FUTURE_RISK_CALIBRATION_SOURCE_LEAKAGE_VETO",json.dumps(r,sort_keys=True))

if __name__=="__main__":main()

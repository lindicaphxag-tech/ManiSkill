"""Outside-investigator fresh-seed genuine native PhysX study of selective authority.

Same frozen published policy/controller/classifier code as the original 32-state
test. Experimenter chooses fresh source seeds AFTER original pre-registration.
Source raw JSON bytes are preserved, and separate follow-up provenance is
attached. Running in our own CI is NOT outside-lab independent validation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys

TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
FAULTS=("applied_no_ack","neutral_arm_delta_no_ack")
ARMS=("source_pause_no_fault","blind_probe_optimistic","blind_probe_pessimistic",
      "achieved_probe_classifier","achieved_probe_then_query","privileged_once_after_probe")
SOURCE=Path("research/frozen_ppo_observability_gated_query_fresh32.py")
CLASSIFIER=Path("research/empirical_probe_response_classifier.py")
FIRST_OUTSIDE_SEED=230001
EXPECTED_SOURCE_BLOB="e0070e5978354917b2a68d5a6230931b5b00cd25"
EXPECTED_CLASSIFIER_BLOB="064bb46831b61af73ad445bc836326837ec5468f"


def git_blob_sha1(content: bytes)->str:
    """Compute Git's exact blob object ID, not just a raw-file SHA1."""
    data=b"blob "+str(len(content)).encode("ascii")+b"\\x00"+content
    return hashlib.sha1(data).hexdigest()


def verify_original_source_blobs():
    require(SOURCE.is_file() and CLASSIFIER.is_file(),
            "Run from an intact ManiSkill checkout")
    require(git_blob_sha1(SOURCE.read_bytes())==EXPECTED_SOURCE_BLOB,
            "Original frozen controller experiment method has changed bytes")
    require(git_blob_sha1(CLASSIFIER.read_bytes())==EXPECTED_CLASSIFIER_BLOB,
            "Frozen historical response-envelope model has changed bytes")


def require(ok,msg):
    if not ok:raise ValueError(msg)


def validate_inputs(task,fault,first,count):
    require(task in TASKS and fault in FAULTS,"Unsupported task or actual physical delivery truth")
    require(type(first) is int and FIRST_OUTSIDE_SEED<=first<2147483000,"Must specify fresh non-overlapping integer reset seed >= 230001")
    require(type(count) is int and count in (1,4,8),"Reproduction must include 1, 4, or 8 complete source seeds")
    require(first+count<2147483647,"32bit seed overflow")
    return list(range(first,first+count))


def validate_original(source,task,fault,seeds):
    """Verify the source report and actor access before it can be described as data.

    Successful or unsuccessful pre-fault episodes are retained: exposure is a
    separate field; neither 'not reached' nor task failures can be excluded.
    """
    require(source.get("schema")=="observability_gated_selective_query_fresh32_physx_v1",
            "Wrong original frozen source trial schema")
    require(source.get("task")==TASKS[task] and source.get("truth")==fault,
            "Physical task/fault truth mismatch")
    require(source.get("seeds")==seeds,"Changed/reordered reset seed denominator")
    require(source.get("training_performed") is False and source.get("real_physx") is True,
            "Missing original frozen PPO genuine PhysX provenance")
    require(source.get("published_revision")=="6bdeb28810330ab5425ccd629bb561c58a56ff85",
            "External published weight revision drift")
    must_sha=("74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"
              if task=="pull_cube" else
              "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")
    require(source.get("third_party_checkpoint_sha256")==must_sha,"Different published PPO weights")
    rows=source.get("rows",[])
    require(len(rows)==len(seeds) and [r.get("seed") for r in rows]==seeds,
            "Incomplete/duplicated source episode denominator")
    from research.empirical_probe_response_classifier import classify_empirical_public_response
    sums={a:0 for a in ARMS}
    reads={a:0 for a in ARMS}
    reached={a:0 for a in ARMS[1:]}
    unique=wrong=0
    for row in rows:
        require(row.get("task")==TASKS[task] and row.get("unknown_ack_truth")==fault,
                "Source row's actual intervention semantics changed")
        flags=row.get("success_once",{})
        require(set(flags)==set(ARMS) and all(type(flags[a]) is bool for a in ARMS),
                "Missing/invalid original official PhysX task flags")
        for a in ARMS:sums[a]+=int(flags[a])
        access=row.get("private_memory_reads_during_action_decision",{})
        require(set(access)==set(ARMS) and all(type(access[a]) is int for a in ARMS),
                "No complete true private target-read ledger")
        faulted=row.get("fault_reached",{})
        probe=row.get("probe_reached",{})
        require(all(type(faulted.get(a)) is bool and type(probe.get(a)) is bool
                    for a in ARMS[1:]),"Unknown fault/probe reach state")
        for a in ARMS[1:]:reached[a]+=int(faulted[a])
        for a in ARMS:reads[a]+=access[a]
        for a in ARMS:
            expected=(1 if a=="privileged_once_after_probe" and probe.get(a,False)
                      else 1 if a=="achieved_probe_then_query" and
                      probe.get(a,False) and
                      (row.get("hybrid_classifier") or {}).get("label") is None
                      else 0)
            require(access[a]==expected,"Source claimed improper privileged memory read")
        cls=row.get("hybrid_classifier")
        if probe.get("achieved_probe_then_query",False):
            require(isinstance(cls,dict),"Missing public history evidence for activated physical probe")
            xyz=row.get("probe_positions",{}).get("achieved_probe_then_query",{})
            goals=row.get("hybrid_candidate_goal_positions",{})
            require(all(k in xyz for k in ("achieved_pre_probe_xyz","achieved_post_probe_xyz")),
                    "No actual public pre/post physical response")
            require(set(goals)=={"held","applied"},"Missing both candidate internal targets")
            expected=classify_empirical_public_response(
                xyz["achieved_pre_probe_xyz"],xyz["achieved_post_probe_xyz"],
                goals["held"],goals["applied"],task=task)
            # Roundoff-only tolerance; labels and access must compare exactly.
            for k,v in expected.items():
                got=cls.get(k)
                if type(v) in (float,int):
                    require(type(got) in (float,int) and math.isfinite(got) and
                            math.isclose(v,got,rel_tol=0,abs_tol=2e-11),
                            "Classifier numeric response is inconsistent with fixed model")
                else:require(got==v,"Classifier discrete model decision changed")
            if cls["label"] is not None:
                unique+=1
                truth="held" if fault=="neutral_arm_delta_no_ack" else "applied"
                misclassified=cls["label"]!=truth
                require(row.get("hybrid_wrong_authorization") is misclassified,
                        "Incorrect hidden-history error disclosure")
                wrong+=int(misclassified)
            else:
                require(row.get("hybrid_wrong_authorization") is None,
                        "Abstention wrongly labelled as successful history prediction")
        else:
            require(cls is None,"Claimed public history inference without a physical probe")
        require(all(e.get("exactness")=="NOT_EXACT" for arr in
                    row.get("projections",{}).values() for e in arr),
                "Approximate controller command disguised as exact")
    require(sums==source.get("success_count"),"Source reported success counts differ from original individual episodes")
    require(unique==source.get("hybrid_classification_covered") and
            wrong==source.get("hybrid_wrong_history_authorizations"),
            "Source hidden history wrong-label totals differ")
    require(reads["achieved_probe_then_query"]==source.get("selective_privileged_queries"),
            "Reported information cost differs from raw episodes")
    return dict(success_counts=sums,privileged_target_reads=reads,
                fault_reached_counts=reached,public_unique_history_labels=unique,
                public_wrong_confident_labels=wrong,full_denominator=len(rows),
                original_seed_exclusions=0)


def run(task,fault,first_seed,count,output):
    seeds=validate_inputs(task,fault,first_seed,count)
    verify_original_source_blobs()
    os.environ.update(ABI_TASK=task,ABI_FAULT=fault,ABI_START="0")
    sys.path.insert(0,str(Path.cwd()))
    sys.path.insert(0,str(Path.cwd()/"research"))
    original=importlib.import_module("frozen_ppo_observability_gated_query_fresh32")
    require(original.FREEZE_COMMIT=="9f4c70d8b0dd45045561dd91b2f0e372fa347135",
            "Original source method protocol changed")
    original.SEEDS=tuple(seeds)
    output.mkdir(parents=True,exist_ok=True)
    native=Path(f"hybrid_observability_query_{task}_{fault}_0_fresh4.json")
    require(not native.exists(),"Stale original output file is present; refuse overwrite")
    original.main()
    require(native.is_file(),"No original actual PhysX source JSON produced")
    raw=native.read_bytes()
    data=json.loads(raw)
    verified=validate_original(data,task,fault,seeds)
    copied=output/f"UNCHANGED_original_physx_{task}_{fault}_{first_seed}_{first_seed+count-1}.json"
    copied.write_bytes(raw)
    native.unlink()
    info={
       "schema":"user_selected_new_seed_observability_hybrid_followup_v1",
       "original_source_json_sha256":hashlib.sha256(raw).hexdigest(),
       "original_32_state_source_method_git_blob":EXPECTED_SOURCE_BLOB,
       "public_response_classifier_git_blob":EXPECTED_CLASSIFIER_BLOB,
       "original_method_source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
       "selected_after_original_method_outcomes":True,
       "original_32_cohort_preregistered":False,
       "new_source_seed_interval":seeds,
       "actual_fault_truth":fault,"task":task,
       "authority_information_cost_vs_mandatory_once":verified,
       "github_identity":{
           "repository":os.getenv("GITHUB_REPOSITORY"),
           "actor":os.getenv("GITHUB_ACTOR"),
           "exact_commit":os.getenv("GITHUB_SHA"),
           "run_id":os.getenv("GITHUB_RUN_ID")},
       "independent_external_team_verified":False,
       "real_hardware_safety_verified":False,
       "scope":"Pure frozen policy actual PhysX simulator; no trained VLA, real robot packet loss or outside adoption by an author-side run",
    }
    dest=output/f"external_hybrid_summary_{task}_{fault}_{first_seed}_{first_seed+count-1}.json"
    dest.write_text(json.dumps(info,sort_keys=True,indent=2)+"\n")
    print("OUTSIDE_SELECTABLE_HYBRID_REAL_PHYSX",json.dumps({
        "selected_seeds":seeds,"score":verified,"original_source_sha256":hashlib.sha256(raw).hexdigest(),
        "NOT_independent_external_lab_by_virtue_of_author_run":True},sort_keys=True))
    return dest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task",choices=list(TASKS),required=True)
    p.add_argument("--fault",choices=list(FAULTS),required=True)
    p.add_argument("--first-seed",type=int,required=True)
    p.add_argument("--count",type=int,default=8,choices=(1,4,8))
    p.add_argument("--output-dir",type=Path,default=Path("replication_artifacts"))
    a=p.parse_args()
    run(a.task,a.fault,a.first_seed,a.count,a.output_dir)


if __name__=="__main__":main()

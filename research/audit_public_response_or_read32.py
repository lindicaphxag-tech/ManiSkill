"""All-original-32-source audit of public-motion inference OR ONE explicit authority read.

The response error envelopes, fault truths, distinct fresh seed ranges, and
readback budget were PREDECLARED before new 6-arm PhysX runner implementation.
Auditing task success is NOT a proof of correct hidden ACK labels.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

TASKS={
"pull_cube":("PullCube-v1",180101,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",0.006944262561376447),
"stack_cube":("StackCube-v1",190101,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",0.00719087965534261),
}
FAULTS=("applied_no_ack","neutral_arm_delta_no_ack")
HYBRID="PUBLIC_FIT_OR_EXPLICIT_ONE_PRIVATE_READ"
PUBLIC="achieved_probe_classifier"
PRIVILEGED="privileged_once_after_probe"
ARMS=("source_pause_no_fault","blind_probe_optimistic","blind_probe_pessimistic",PUBLIC,HYBRID,PRIVILEGED)
PROTO="research/PHYSICAL_RESPONSE_OR_READ32_PREDECLARED_V1.json"
FREEZE="fa17350711f6c2c7cffb4cfa2bb7f8289f3ee0c4"
MODEL_BLOB="064bb46831b61af73ad445bc836326837ec5468f"

def audit(directory:Path)->dict:
    summaries={}
    seen=set()
    for t,(task_name,first,ckpt,eps) in TASKS.items():
        for fault in FAULTS:
            for start in (0,4):
                name=f"public_or_read_{t}_{fault}_{start}_fresh4.json"
                path=directory/name
                if not path.is_file() or not path.stat().st_size:
                    raise ValueError("Missing original registered true-PhysX source "+name)
                rec=json.loads(path.read_text(encoding="utf-8"))
                seeds=list(range(first+start,first+start+4))
                if (rec.get("schema")!="public_response_or_one_authority_read32_precommitted_physx_v1"
                    or rec.get("protocol")!=PROTO
                    or rec.get("preoutcome_frozen_commit")!=FREEZE
                    or rec.get("original_public_response_classifier_git_blob")!=MODEL_BLOB
                    or rec.get("original_public_response_runner_git_blob")!="96f1baaceb87e98d7f7cdf5c3a092b80d7316b15"
                    or rec.get("task")!=task_name
                    or rec.get("truth")!=fault or rec.get("seeds")!=seeds
                    or rec.get("third_party_checkpoint_sha256")!=ckpt
                    or rec.get("published_revision")!="6bdeb28810330ab5425ccd629bb561c58a56ff85"
                    or rec.get("training_performed") is not False
                    or rec.get("real_physx") is not True):
                    raise ValueError("Invalid original model/provenance/seed identity: "+name)
                rows=rec.get("rows")
                if not isinstance(rows,list) or len(rows)!=4:
                    raise ValueError("Missing original failures/complete 4 episode denominator: "+name)
                count={k:0 for k in ARMS}
                hybrid_only=authority_only=0
                public_accept=public_wrong=hybrid_accept=hybrid_wrong=hybrid_reads=exposed=0
                for i,r in enumerate(rows):
                    seed=seeds[i]
                    if r.get("seed")!=seed or r.get("task")!=task_name or r.get("unknown_ack_truth")!=fault:
                        raise ValueError("Original trial identity changed")
                    if (r.get("fault_step")!=2 or r.get("probe_step")!=3
                        or set(r.get("private_memory_reads_during_action_decision",{}))!=set(ARMS)
                        or set(r.get("success_once",{}))!=set(ARMS)
                        or any(type(r["success_once"][a]) is not bool for a in ARMS)):
                        raise ValueError("Native fault/probe/task success ledger corrupted")
                    for a in ARMS:
                        count[a]+=int(r["success_once"][a])
                    hybrid_only+=int(r["success_once"][HYBRID] and
                                     not r["success_once"][PRIVILEGED])
                    authority_only+=int(not r["success_once"][HYBRID] and
                                        r["success_once"][PRIVILEGED])
                    obs=r.get("initial_obs_diff",{})
                    if set(obs)!=set(ARMS[1:]) or any(
                        not isinstance(v,(float,int)) or not 0<=v<=.0005 for v in obs.values()):
                        raise ValueError("Original paired task reset observations differ")
                    reached=r.get("fault_reached",{})
                    probe=r.get("probe_reached",{})
                    if not all(reached.get(a) is True and probe.get(a) is True for a in ARMS[1:]):
                        raise ValueError("Actual native intervention/probe not executed in one arm")
                    exposed+=1
                    reads=r["private_memory_reads_during_action_decision"]
                    if reads[PRIVILEGED]!=1 or any(reads[a]!=0 for a in ARMS if a not in (HYBRID,PRIVILEGED)):
                        raise ValueError("Hidden state getter leaked into unprivileged controls")
                    pc=r.get("classifier")
                    hc=r.get("hybrid_classifier")
                    if not isinstance(pc,dict) or not isinstance(hc,dict):
                        raise ValueError("Neither public response decision may be omitted")
                    truth=("held" if fault=="neutral_arm_delta_no_ack" else "applied")
                    for cl in (pc,hc):
                        if (cl.get("evidence_type")!="achieved_EE_xyz_after_one_native_zero_arm_delta"
                            or cl.get("certification_claim") is not False
                            or cl.get("independent_physical_model_attested") is not False
                            or abs(cl.get("empirical_response_epsilon_m",-1)-eps)>1e-10
                            or cl.get("label") not in ("held","applied",None)):
                            raise ValueError("Classified with changed private/attested/epsilon evidence")
                    for cl,wrong in ((pc,r.get("wrong_authorization")),(hc,r.get("hybrid_wrong_authorization"))):
                        label=cl["label"]
                        if label is None and wrong is not None:
                            raise ValueError("Public inference abstention scored as correct/wrong")
                        if label is not None and wrong is not (label!=truth):
                            raise ValueError("Confident incorrect ACK history concealed")
                    if hc["label"] is not None:
                        if reads[HYBRID]!=0 or r.get("hybrid_query_reason") is not None:
                            raise ValueError("Hybrid queried despite a unique public response fit")
                        hybrid_accept+=1
                        hybrid_wrong+=int(hc["label"]!=truth)
                    else:
                        if (reads[HYBRID]!=1
                            or r.get("hybrid_query_reason")!=hc.get("status")
                            or hc.get("status") not in ("ABSTAIN_TWO_PLAUSIBLE_HISTORIES",
                                                      "REFUSE_EMPIRICAL_MODEL_FALSIFIED")):
                            raise ValueError("Hybrid refused public evidence without precisely one disclosed target read")
                    if pc["label"] is not None:
                        public_accept+=1
                        public_wrong+=int(pc["label"]!=truth)
                    hybrid_reads+=reads[HYBRID]
                    for a in ARMS[1:]:
                        if a not in r.get("probe_positions",{}):
                            raise ValueError("Public achieved joint/EE probe omitted")
                    for a,proj in r.get("projections",{}).items():
                        if a not in ARMS[1:] or any(x.get("exactness")!="NOT_EXACT" for x in proj):
                            raise ValueError("Bounded action projection falsely reported exact")
                    if (t,seed,fault) in seen:
                        raise ValueError("Duplicate episode identity")
                    seen.add((t,seed,fault))
                if (count!=rec.get("success_count")
                    or public_accept!=rec.get("classification_covered")
                    or public_wrong!=rec.get("false_history_authorizations")
                    or hybrid_accept!=rec.get("hybrid_classification_covered")
                    or hybrid_wrong!=rec.get("hybrid_false_history_authorizations")
                    or hybrid_reads!=rec.get("hybrid_authority_reads")):
                    raise ValueError("Original per-trial truth contradicts published summary")
                summaries[f"{t}:{fault}:{start}"]=dict(
                    all_original_four=len(rows),task_success=count,
                    public_decisions=public_accept,public_wrong=public_wrong,
                    hybrid_public_decisions=hybrid_accept,hybrid_wrong=hybrid_wrong,
                    hybrid_explicit_reads=hybrid_reads,
                    hybrid_only=hybrid_only,authority_only=authority_only,
                    fault_probe_reached=exposed,
                    original_source=name)
    if len(seen)!=32 or len({(t,s) for t,s,_ in seen})!=16:
        raise ValueError("32 unique task×truth conditions must cover 16 distinct reset states")
    totals={key:sum(v["task_success"][key] for v in summaries.values()) for key in ARMS}
    return dict(
        schema="public_evidence_or_authority_read_new32_full_original_source_audit",
        total_task_seed_fault_conditions=32,unique_reset_states=16,
        classifier_frozen_from_tiny_historical_training_only=True,
        native_task_success=totals,
        hybrid_decided_by_public=sum(v["hybrid_public_decisions"] for v in summaries.values()),
        hybrid_false_confident_labels=sum(v["hybrid_wrong"] for v in summaries.values()),
        hybrid_privileged_reads=sum(v["hybrid_explicit_reads"] for v in summaries.values()),
        privileged_always_reads=32,
        paired_hybrid_only=sum(v["hybrid_only"] for v in summaries.values()),
        paired_authority_only=sum(v["authority_only"] for v in summaries.values()),
        per_condition=summaries,
        limitations="Same contributor native CPU PhysX on Panda; empirical response envelope not independent physical certification; actual target hold not packet loss.")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    opts=p.parse_args()
    z=audit(opts.input_dir)
    opts.output.write_text(json.dumps(z,sort_keys=True,indent=2)+"\n")
    print("PUBLIC_OR_READ32_FULL_ORIGINAL_AUDIT",json.dumps({
        "n":z["total_task_seed_fault_conditions"],
        "success":z["native_task_success"],
        "public_accepted":z["hybrid_decided_by_public"],
        "public_wrong":z["hybrid_false_confident_labels"],
        "private_reads":z["hybrid_privileged_reads"]
    },sort_keys=True))

if __name__=="__main__":
    main()

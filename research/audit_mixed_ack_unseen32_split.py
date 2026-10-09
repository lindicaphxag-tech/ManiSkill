"""Independent source-locked sensitivity analysis for previously exposed RESET IDs.

Not an independent simulator run. The 64 mixed-ACK prospective *physical*
controller rollouts retain their original first-run source bytes. Research
program used 32 of their same reset IDs in a separate earlier held/held
experiment. Splitting the already observed 64 trial rows is POST-HOC;
it cannot yield a new independent confirmatory trial or new p-value.

Tests both:
  32 previously seen task/reset IDs, 16 with same ACK truth as held/held
  32 never-before-exposed task/reset IDs relative to two cited cohorts
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from research.audit_cross_study_reset_overlap import analyze as overlap_audit

BASE=Path(__file__).resolve().parent/"frozen_policy_transfer/evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032"
NEW="fault_public_t3_fourhistory_or_t4_query"
TASK_ROUTE={"pull_cube":"fault_robust_then_single_privileged_query",
            "stack_cube":"fault_always_single_privileged_query"}
TASKS={"pull_cube":860001,"stack_cube":870001}
CHECKED_SOURCE_RAW=8
EXPECTED_ARCHIVED_OUTCOME_SHA="4d7c1478260d89af3b2c5d719cb5b139db0ad2f89760bfac0fea9747dcfe356e"


def load_originals(folder:Path=BASE):
    manifest=(folder/"SHA256SUMS").read_text().splitlines()
    indexed={}
    for line in manifest:
        sha,name=line.split(maxsplit=1)
        if len(sha)!=64 or name in indexed or "/" in name or "\\" in name:
            raise ValueError("Source manifest has malicious or duplicate entry")
        indexed[name]=sha
    if len(indexed)!=17 or indexed.get("ORIGINAL_MIXED_ACK_ALL64_FULL_AUDIT.json")!=EXPECTED_ARCHIVED_OUTCOME_SHA:
        raise ValueError("Original 17-source physical archive does not match trusted manifest")
    if {p.name for p in folder.glob("*.json")}!=set(indexed):
        raise ValueError("Missing or unregistered PhysX original source file")
    for name,expected in indexed.items():
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=expected:
            raise ValueError("Original PhysX raw bytes were changed: "+name)
    return indexed


def summarize(rows):
    def count(x):return sum(int(r[x]) for r in rows)
    def reads(x):return sum(r[x] for r in rows)
    return {
        "task_reset_n":len(rows),
        "new_official_task_successes":count("new"),
        "strong_task_only_successes":count("baseline"),
        "new_privileged_target_reads":reads("new_reads"),
        "strong_privileged_target_reads":reads("baseline_reads"),
        "public_complete_pose_acceptances":count("unique"),
        "wrong_confident_labels":count("wrong"),
        "new_only_successes":sum(r["new"] and not r["baseline"] for r in rows),
        "strong_only_successes":sum(r["baseline"] and not r["new"] for r in rows),
    }


def audit(folder:Path=BASE,repo:Path|None=None):
    load_originals(folder)
    if repo is None:
        repo=Path(__file__).resolve().parents[1]
    x=overlap_audit(repo)
    if x["mixed64_reused_from_previous_survivor32"]!=32:
        raise ValueError("Original old task/reset reuse definition changed")
    rows=[]
    for task,first in TASKS.items():
        for chunk in range(4):
            path=folder/f"mixed_ack_{task}_chunk{chunk}_original8.json"
            q=json.loads(path.read_text())
            expected_seeds=list(range(first+chunk*8,first+chunk*8+8))
            if q.get("original_seed_population")!=expected_seeds or len(q.get("episodes",[]))!=8:
                raise ValueError("Original 8-seed task population changed")
            if not(q.get("real_physx_simulator") is True and q.get("frozen_model_retrained") is False):
                raise ValueError("Original physical policy identity changed")
            for r in q["episodes"]:
                if r["seed"] not in expected_seeds:
                    raise ValueError("Wrong/fabricated task seed")
                flags=r["success_once"]
                counters=r["privileged_target_readback_decision_count"]
                cmp=TASK_ROUTE[task]
                if type(flags.get(NEW)) is not bool or type(flags.get(cmp)) is not bool:
                    raise ValueError("Original success flag absent/nonboolean")
                if type(counters.get(NEW)) is not int or type(counters.get(cmp)) is not int:
                    raise ValueError("Original privileged read not integer")
                if counters[NEW] not in (0,1) or counters[cmp] not in (0,1):
                    raise ValueError("Read count mismatch")
                faults=r.get("faults",{}).get(NEW)
                if not isinstance(faults,list) or [f.get("step") for f in faults]!=[2,3]:
                    raise ValueError("Both fault interventions must physically occur")
                ev=r["public_t3_evidence"]
                sel=ev.get("authorized")
                if type(sel) is not bool or counters[NEW]!=int(not sel):
                    raise ValueError("Public acceptance/query accounting changed")
                if ev.get("wrong_confident") is not False:
                    raise ValueError("Wrong confident source label or missing audit-only truth")
                parity_applied=r["seed"]%2==0
                physical=r["original_precommitted_physical_t2_execution_truth"]
                if (physical=="applied")!=parity_applied:
                    raise ValueError("Actual precommitted physical truth mismatch")
                rows.append({
                    "task":task,"seed":r["seed"],
                    "reused_initial_state":r["seed"]<first+16,
                    "physical_t2_truth":physical,
                    "new":flags[NEW],"baseline":flags[cmp],
                    "new_reads":counters[NEW],"baseline_reads":counters[cmp],
                    "unique":sel,"wrong":False
                })
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Source contains duplicate/missing physical states")
    reused=[r for r in rows if r["reused_initial_state"]]
    unseen=[r for r in rows if not r["reused_initial_state"]]
    report={
        "status":"POST_HOC_SENSITIVITY_NOT_ANOTHER_PROSPECTIVE_EXPERIMENT",
        "same_full_original_64_physx_results_preserved":True,
        "unique_new_reset_identifiers_relative_to_older_studies":32,
        "previously_exposed_reset_identifiers":32,
        "source_sha256_files_verified":17,
        "all64":summarize(rows),
        "reused_reset32":summarize(reused),
        "not_previously_exposed_reset32":summarize(unseen),
        "by_task_and_exposure":{
            task:{
                label:summarize([r for r in rows if r["task"]==task and
                                 r["reused_initial_state"]==(label=="reused")])
                for label in ("reused","new")
            } for task in TASKS
        },
        "interpretation_limits":[
            "The two original comparison arms were genuinely stepped, but this is posthoc stratification by earlier seed reuse.",
            "The 32 previous IDs were NOT previously blind state identifiers for all earlier experiments.",
            "The method differs in mixed physical ACK truth across even reused seeds; do not label all reused states identical fault trials.",
            "The 32 genuinely novel identifiers may have seen the same two tasks/robot/checkpoints; not unseen policies or embodiments.",
            "Observed identical pooled successes is NOT uniform success preservation in each exposure stratum.",
            "Empirical public response model and same-PPO repeated measurements do not prove robot safety."
        ]
    }
    a=report["all64"]
    b=report["reused_reset32"]
    c=report["not_previously_exposed_reset32"]
    if not (a["new_official_task_successes"]==a["strong_task_only_successes"]==58 and
            a["new_privileged_target_reads"]==31 and a["strong_privileged_target_reads"]==58
            and b["new_official_task_successes"]==30 and b["strong_task_only_successes"]==29 and
            b["new_privileged_target_reads"]==14 and b["strong_privileged_target_reads"]==29 and
            c["new_official_task_successes"]==28 and c["strong_task_only_successes"]==29 and
            c["new_privileged_target_reads"]==17 and c["strong_privileged_target_reads"]==29):
        raise ValueError("All reported original results have changed or expected negative cases missing")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=BASE)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.source)
    body=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(body)
    print("ORIGINAL_MIXED_ACK_UNSEEN_RESET_STRATIFICATION",body)


if __name__=="__main__":
    main()

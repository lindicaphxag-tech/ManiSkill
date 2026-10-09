"""Eight-artifact original-source-only audit of fresh 64-state PhysX query policy.

Runs ZERO simulator episodes. Refuses missing raw worlds, altered SHA256,
unregistered seeds, non-PPO baseline changes, hidden privilege misuse, false
controller setpoint bounds or cherry-picked output rows.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter
from itertools import product
from pathlib import Path
from research.run_phase_information_new64 import (
    TASKS,ARMS,SELECTIVE,FIXED,PROACTIVE,ROUTE,ORIGINAL_SHA,
    PROACTIVE_RUNNER_BLOB,PROTOCOL,group,summarize
)

ORIGINAL_RUN=37911547899
PROTOCOL_BLOB="60854049211c9d0aeee8be5e0f70bd3de14b0f09"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(yes,message):
    if not yes:raise ValueError(message)

def sign_p(w,l):
    n=w+l
    return min(1., 2*sum(math.comb(n,i) for i in range(min(w,l)+1))/2**n) if n else 1.

def get_one(folder,task,chunk):
    name=f"phaseinfo-{task}-{chunk}-{ORIGINAL_RUN}"
    d=folder/name
    require(d.is_dir(),"Missing original PhysX source shard "+name)
    lines=(d/"SHA256SUMS").read_text("utf-8").splitlines()
    require(len(lines)>=7,"Missing full original evidence and environment source manifest")
    names=set()
    for line in lines:
        parts=line.split()
        require(len(parts)==2 and len(parts[0])==64,"Invalid SHA256SUMS entry")
        h,filename=parts
        require(filename not in names and filename not in (".","..")
                and "/" not in filename and "\\" not in filename,
                "Untrusted or duplicated source artifact name")
        names.add(filename)
        require(sha((d/filename).read_bytes())==h,"Altered original SHA256 source "+filename)
    require((d/"phase_runner_blob.txt").read_text().strip()==PROACTIVE_RUNNER_BLOB,
            "New experimental runner SHA changed")
    require((d/"unchanged_base_runner_blob.txt").read_text().strip()==ORIGINAL_SHA[
        "research/frozen_ppo_compound_ack_multi_belief.py"],
        "Published original four-history controller was changed")
    require((d/"preregistered_protocol_blob.txt").read_text().strip()==PROTOCOL_BLOB,
            "Pre-outcome prospective policy contract changed")
    source=f"phase_information_{task}_chunk{chunk}_original8.json"
    require(source in names and "summary.json" in names,
            "Original eight-world native PhysX source JSON missing")
    raw=(d/source).read_bytes()
    record=json.loads(raw)
    report=json.loads((d/"summary.json").read_bytes())
    calc=summarize(record,task,chunk,group(task,chunk))
    for key in ("task","chunk","source_seeds","official_8_arm_success",
                "decision_reads","after_actual_dispatch_checks",
                "deliberately_masked_commands_excluded","per_seed_full_real_native_outcomes"):
        require(report.get(key)==calc[key],"Original simulator source/summary mismatch in "+key)
    if task=="stack_cube":
        # Negative control: the preregistered phase arm ALWAYS requests the
        # same real target read at step 4 as the physically separate fixed
        # comparator. Both run complete independent real controller worlds.
        for trial in calc["per_seed_full_real_native_outcomes"]:
            require(trial["phase_success"]==trial["fixed_success"] and
                    trial["phase_read_count"]==trial["fixed_read_count"],
                    "Stack fixed-phase equivalent query violated matched physics")
    require(report.get("true_original_physx_sha256")==sha(raw)
            and report.get("preoutcome_protocol")==PROTOCOL,
            "Original simulator bytes or registered frozen study do not match")
    return {
      "task":task,"chunk":chunk,"artifact":name,"source_sha256":sha(raw),
      "original_after_dispatch_checks":calc["after_actual_dispatch_checks"],
      "physically_masked_tries_excluded":calc["deliberately_masked_commands_excluded"],
      "per_seed":calc["per_seed_full_real_native_outcomes"],
    }

def audit(folder):
    results=[get_one(folder,t,chunk) for t,chunk in product(TASKS,range(4))]
    rows=[x for item in results for x in item["per_seed"]]
    require(len(rows)==64 and len({(r["task"],r["seed"]) for r in rows})==64,
            "Only complete 64 original physical source states acceptable")
    def calc(task):
        z=[r for r in rows if task is None or task==r["task"]]
        out={"states":len(z)}
        for name,suc,read in (
            ("phase","phase_success","phase_read_count"),
            ("proactive","proactive_success","proactive_read_count"),
            ("fixed","fixed_success","fixed_read_count"),
            ("reactive","reactive_success","reactive_read_count"),
            ("strong_task_gated","prior_task_gated_success","prior_task_gated_read_count")):
            out[name]={"native_success":sum(x[suc] for x in z),
                       "privileged_reads":sum(x[read] for x in z)}
        for opponent,field in (
            ("fixed","fixed_success"),("strong_task_gated","prior_task_gated_success"),
            ("naive_proactive","proactive_success")):
            c=Counter((r["phase_success"],r[field]) for r in z)
            out["paired_vs_"+opponent]={
                "both_success":c[(1,1)],"phase_only":c[(1,0)],
                "opponent_only":c[(0,1)],"both_failed":c[(0,0)],
                "exploratory_exact_two_sided_p":sign_p(c[(1,0)],c[(0,1)])}
        out["proactive_prequery_invoked_at_t4"]=sum(
            r["proactive_prequery_decision"] is not None for r in z)
        out["proactive_prequery_trigger_count"]=sum(
            bool(r["proactive_prequery_decision"] and
                 r["proactive_prequery_decision"]["queried_before_action"]) for r in z)
        out["phase_t4_observed"]=sum(x.get("phase_prequery_decision") is not None for x in z)
        out["phase_t4_triggers"]=sum(bool(x.get("phase_prequery_decision") and
            x["phase_prequery_decision"].get("queried")) for x in z)
        return out
    return {
     "evidence_type":"source-frozen author-run native PhysX, original nine actually stepped controller worlds per seed",
     "run_id":ORIGINAL_RUN,
     "n_distinct_physical_reset_states":64,
     "genuine_native_controller_worlds":576,
     "source_checkpoint_models":2,
     "no_model_retraining":True,
     "no_actual_network_packet_loss":True,
     "setpoint_bound_checks_not_collision_or_hardware_safety":
       sum(x["original_after_dispatch_checks"] for x in results),
     "fault_masked_commands_EXCLUDED":sum(x["physically_masked_tries_excluded"] for x in results),
     "eight_original_physx_sha256_artifacts":[{
       k:x[k] for k in ("task","chunk","artifact","source_sha256")} for x in results],
     "overall":calc(None),"by_task":{t:calc(t) for t in TASKS},
     "all_64_original_native_task_rows":rows,
     "no_claims":["outside research-lab replication","POMDP information-optimal query timing",
                  "new policy pretraining","general robotics safety","superiority over strong task-conditioned baseline unless measured"]
    }

def tagged_nonfinite(v):
    """Preserve honestly unrepresentable raw source limits as tagged strings.

    Original Python JSON can represent Infinity (not RFC 8259). Public audit
    uses strict, portable JSON, and does not erase the source hash or claim
    a finite certified command where the actual solver refused.
    """
    if isinstance(v,float) and not math.isfinite(v):
        if math.isnan(v):
            raise ValueError("Invalid NaN in native PhysX source evidence")
        return "UNREPRESENTABLE_POSITIVE_INFINITY" if v>0 else "UNREPRESENTABLE_NEGATIVE_INFINITY"
    if isinstance(v,list):
        return [tagged_nonfinite(x) for x in v]
    if isinstance(v,dict):
        return {k:tagged_nonfinite(x) for k,x in v.items()}
    return v


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifacts",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.artifacts)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(tagged_nonfinite(result),indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PHASE_INFORMATION_PROSPECTIVE_REAL64_AUDIT",json.dumps({
        "states":result["n_distinct_physical_reset_states"],
        "physx_worlds":result["genuine_native_controller_worlds"],
        "phase":result["overall"]["phase"],
        "proactive":result["overall"]["proactive"],
        "task_gated_strong":result["overall"]["strong_task_gated"],
        "fixed":result["overall"]["fixed"],
        "reactive":result["overall"]["reactive"],
        "checks":result["setpoint_bound_checks_not_collision_or_hardware_safety"],
        "masked":result["fault_masked_commands_EXCLUDED"],
        "paired_vs_task_gated":result["overall"]["paired_vs_strong_task_gated"],
        "phase_t4_triggers":result["overall"]["phase_t4_triggers"]
    },sort_keys=True))

if __name__=="__main__":main()

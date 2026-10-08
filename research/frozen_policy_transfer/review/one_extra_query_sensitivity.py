"""Sensitivity to the ONE additional selective target read in near-budget PhysX.

This is a rigorous *single-episode deletion influence bound*, NOT a new
physics execution, and NOT a measured exactly-budget-matched experiment.

Assumption: each seeded trial is independent of the other 63 seeded
rollouts, so removing a target-state read from ONE trial can change
only that trial's binary task success. Any shared/global state between
trials invalidates the influence statement and requires a rerun.

Requires eight original SHA-pinned source JSONs from the FIRST successful
public run, never later repeats or selected successes.
"""
from __future__ import annotations
from pathlib import Path
from math import comb
import hashlib
import json
import argparse

BASE = Path(__file__).resolve().parents[1] / (
    "evidence/periodic_query_placebo_new64_260001_270032"
)
ADAPTIVE="fault_robust_then_single_privileged_query"
PLACEBO="fault_precommitted_seed_schedule_query"


def exact_p(wins:int,losses:int)->float:
    n=wins+losses
    return 1.0 if n==0 else min(
        1.0, 2*sum(comb(n,k) for k in range(min(wins,losses)+1))/2**n
    )


def analyze(original:Path=BASE)->dict:
    manifest=original/"ORIGINAL_SHA256SUMS"
    if not manifest.is_file():
        raise ValueError("Source-hashed eight original JSONs not published")
    expected={}
    for line in manifest.read_text().splitlines():
        sha,name=line.split(maxsplit=1)
        if name in expected or len(sha)!=64 or "/" in name:
            raise ValueError("Invalid SHA256 manifest or unexpected paths")
        expected[name]=sha
    if len(expected)!=8 or set(expected)!={p.name for p in original.glob("*original8.json")}:
        raise ValueError("Unexpected original source file denominator")
    rows=[]
    for task,first in [("pull_cube",260001),("stack_cube",270001)]:
        for i in range(4):
            filename=f"query_placebo_{task}_chunk{i}_original8.json"
            raw=(original/filename).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=expected[filename]:
                raise ValueError("Original source has changed: "+filename)
            q=json.loads(raw)
            if [z["seed"] for z in q["episodes"]]!=list(range(first+8*i,first+8*i+8)):
                raise ValueError("Missing, duplicated, shuffled original seed")
            for z in q["episodes"]:
                results=z["success_once"]
                reads=z["privileged_target_readback_decision_count"]
                if not (type(results[ADAPTIVE]) is bool
                        and type(results[PLACEBO]) is bool
                        and type(reads[ADAPTIVE]) is int
                        and reads[ADAPTIVE] in (0,1)
                        and reads[PLACEBO]==int(z["seed"]%4==0)):
                    raise ValueError("Invalid original success, budget or placebo allocation")
                rows.append((task,z["seed"],results[ADAPTIVE],results[PLACEBO],
                             reads[ADAPTIVE]))
    if len(rows)!=64 or len({(t,s) for t,s,*_ in rows})!=64:
        raise ValueError("Not all 64 original task states")
    aa=sum(a and not b for _,_,a,b,_ in rows)
    bb=sum(b and not a for _,_,a,b,_ in rows)
    qa=sum(read for *_,read in rows)
    qb=sum(int(seed%4==0) for _,seed,*_ in rows)
    sa=sum(a for _,_,a,_,_ in rows)
    sb=sum(b for _,_,_,b,_ in rows)
    if (aa,bb,qa,qb,sa,sb)!=(12,1,17,16,58,47):
        raise ValueError("First original run changed its predeclared outcomes")
    # At most ONE episode can change when we budget-cap only one extra
    # read and all independently seeded episodes are autonomous.
    queried=[r for r in rows if r[4]==1]
    all_fail_single_read=[]
    for task,seed,a,b,read in queried:
        if a:  # A missed information event may make its episode fail.
            changed_adaptive_only=aa-int(not b)
            changed_placebo_only=bb+int(b)
            changed_success=sa-1
        else:
            # Already failed: loss of this read need not change success.
            changed_adaptive_only=aa
            changed_placebo_only=bb
            changed_success=sa
        all_fail_single_read.append({
            "task":task,"seed":seed,
            "worst_case_adaptive_successes":changed_success,
            "new_adaptive_only":changed_adaptive_only,
            "new_periodic_only":changed_placebo_only,
            "exploratory_unadjusted_conditional_exact_p":
                exact_p(changed_adaptive_only,changed_placebo_only)
        })
    assert len(all_fail_single_read)==17
    worst=max(all_fail_single_read,key=lambda x:x["exploratory_unadjusted_conditional_exact_p"])
    return {
        "status":"THEORETICAL_SINGLE_EPISODE_INFLUENCE_NOT_SIMULATOR_RESULT",
        "first_original_task_state_count":64,
        "initial_adaptive_success":sa,"periodic_success":sb,
        "adaptive_reads_original":qa,"periodic_reads_original":qb,
        "adapt_only":aa,"periodic_only":bb,
        "first_run_exact_conditional_p_unadjusted":exact_p(aa,bb),
        "hypothetical_one_extra_read_deleted":1,
        "remaining_worst_case_adaptive_success_min":min(x["worst_case_adaptive_successes"] for x in all_fail_single_read),
        "worst_conditional_unadjusted_p_after_1_worst_case_flip":worst["exploratory_unadjusted_conditional_exact_p"],
        "worst_case_example_deleted_read":worst,
        "qualifiers":[
            "No exactly-16-query adaptive physics rollout was actually executed.",
            "Requires independence of all seeded trial states and one query removal not altering any other episode.",
            "Conditional on the other 63 original outcomes remaining unchanged; is not a randomized controlled intervention.",
            "No experiment-wise multiplicity correction; two frozen task policies, one Panda control family.",
            "No force, collision or real communication safety guarantee."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,default=BASE)
    p.add_argument("--output",type=Path)
    x=p.parse_args()
    out=analyze(x.input_dir)
    s=json.dumps(out,sort_keys=True,indent=2)+"\n"
    if x.output:x.output.write_text(s)
    print(s)


if __name__=="__main__":
    main()

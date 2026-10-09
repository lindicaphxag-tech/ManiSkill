"""Original-source-only exact paired read economy & per-stratum exceptions.

NO simulator, NO new trials, NO re-tuned thresholds. All claims conditional
on fixed author-operated task and 2x2 ACK fault population.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path("research/frozen_policy_transfer/evidence/true_two_by_two_nonzero_ack64_1340001_1350032")
SRC1 = ROOT/"first_original_64_full_audit.json"
SRC2 = ROOT/"second_independent_64_full_audit.json"

def exact_two_sided_sign_p(wins,losses):
    if type(wins) is not int or type(losses) is not int or min(wins,losses)<0:
        raise ValueError("nonnegative integers required")
    n = wins+losses
    if n == 0: return 1.0
    k = min(wins,losses)
    # Exact binomial p for two-sided sign test, no normal approximation.
    return min(1.0, 2.0*sum(math.comb(n,i) for i in range(k+1))/(2**n))

def source_audit(d):
    if not isinstance(d,dict) or d.get("original_reset_states")!=64 or d.get("physical_worlds")!=576:
        raise ValueError("Incorrect original PhysX cohort identity")
    rows=d.get("all_original_rows")
    if type(rows) is not list or len(rows)!=64:
        raise ValueError("Missing original 64 source outcomes")
    seen=set()
    group=defaultdict(list)
    wins=losses=ties=0
    private_new=private_strong=private_fixed=0
    both=new_only=strong_only=neither=0
    conf=wrong=0
    deltas=[]
    for row in rows:
        task=row.get("task"); seed=row.get("seed")
        if task not in ("pull_cube","stack_cube") or type(seed) is not int:
            raise ValueError("Invalid task/reset identity")
        expected=range(1340001,1340033) if task=="pull_cube" else range(1350001,1350033)
        if seed not in expected or (task,seed) in seen:
            raise ValueError("Duplicated or off-cohort seed")
        seen.add((task,seed))
        p=row.get("public_private_reads"); q=row.get("strong_private_reads"); f=row.get("fixed_private_reads")
        if any(type(x) is not int or x not in (0,1) for x in (p,q,f)):
            raise ValueError("Unreliable original decision-time read counts")
        b=row.get("public_task_success"); c=row.get("strong_task_success")
        if type(b) is not bool or type(c) is not bool:
            raise ValueError("Unreliable original environment success")
        if type(row.get("public_unique")) is not bool or type(row.get("wrong_confident")) is not bool:
            raise ValueError("Missing original public decision flags")
        if row["wrong_confident"] and not row["public_unique"]:
            raise ValueError("Wrong-confident result missing corresponding authorization")
        t2=row.get("physical_t2_applied"); t3=row.get("physical_t3_applied")
        if type(t2) is not bool or type(t3) is not bool: raise ValueError("Missing actual physics ACK truth")
        k=task+"/"+("A" if t2 else "H")+("A" if t3 else "H")
        group[k].append(row)
        private_new+=p;private_strong+=q;private_fixed+=f
        delta=q-p;deltas.append(delta)
        wins+=int(delta>0);losses+=int(delta<0);ties+=int(delta==0)
        both+=int(b and c);new_only+=int(b and not c);strong_only+=int(not b and c);neither+=int(not b and not c)
        conf+=int(row["public_unique"]);wrong+=int(row["wrong_confident"])
    if len(seen)!=64 or len(group)!=8 or any(len(x)!=8 for x in group.values()):
        raise ValueError("Missing or unbalanced 8 original task by truth cells")
    if (private_new,private_strong,private_fixed,conf,wrong,both,new_only,strong_only,neither)!=(
            33,51,64,31,0,49,0,0,15):
        raise ValueError("This is not the unmodified original publicly reported source")
    if d.get("total_outcomes",{})!={"new":{"private_reads":33,"success":49},
        "strong":{"private_reads":51,"success":49},
        "fixed":{"private_reads":64,"success":49}}:
        raise ValueError("Original independent aggregate disagrees")
    by={}
    for key,rs in sorted(group.items()):
        a=sum(r["public_private_reads"] for r in rs)
        b=sum(r["strong_private_reads"] for r in rs)
        by[key]={"n":8,"public_reads":a,"strong_reads":b,
            "paired_net_saved":b-a,
            "unique_complete_history":sum(r["public_unique"] for r in rs),
            "wrong_confident":sum(r["wrong_confident"] for r in rs)}
    # Descriptive uncertainty only, rerandomizing original 64 task/reset pairs.
    # This is NOT a randomized causal effect CI or a joint public-sensing cost.
    rng=random.Random(20261009)
    samples=20000
    means=sorted(sum(deltas[rng.randrange(64)] for _ in range(64))/64 for _ in range(samples))
    ci=[means[int(.025*samples)],means[int(.975*samples)-1]]
    result={
        "schema":"paired_private_target_read_source_exact_test_v1",
        "evidence_scope":"author_operated_native_physx_source_only_not_new_simulation",
        "task_reset_states":64,"native_worlds_reused_not_reexecuted":576,
        "paired_private_read_wins":wins,"paired_private_read_losses":losses,
        "paired_private_read_ties":ties,"net_reads_saved":private_strong-private_new,
        "source_private_reads":private_new,"strong_private_reads":private_strong,"fixed_private_reads":private_fixed,
        "relative_strong_private_read_reduction":(private_strong-private_new)/private_strong,
        "exact_two_sided_sign_test_p_exploratory":exact_two_sided_sign_p(wins,losses),
        "task_success_pair":{"both":both,"public_only":new_only,
            "strong_only":strong_only,"neither":neither,
            "exact_two_sided_mcnemar_p":exact_two_sided_sign_p(new_only,strong_only)},
        "public_complete_history_identifications":conf,
        "wrong_confident_identifications_observed":wrong,
        "by_task_and_original_ack_truth":by,
        "paired_bootstrap_95pct_CI_per_episode_saved_reads_descriptive":ci,
        "extra_public_sensing_not_cost_equated":True,
        "exact_prefix_not_asserted_for_task_aware_strong_comparator":True,
        "no_statistical_task_superiority_or_noninferiority":True,
        "no_external_independent_replication":True,
        "not_a_zero_error_safety_certificate":True,
    }
    return result

def _test():
    assert abs(exact_two_sided_sign_p(24,6)-0.0014309063553810122)<1e-14
    assert exact_two_sided_sign_p(0,0)==1.
    assert exact_two_sided_sign_p(1,0)==1.
    assert exact_two_sided_sign_p(24,6)==exact_two_sided_sign_p(6,24)
    for a,b in [(2,-1),(1.,0),(-1,2)]:
        try: exact_two_sided_sign_p(a,b)
        except ValueError: pass
        else: raise AssertionError("Accepted invalid binomial counts")
    print("PAIRED_NONZERO_ACK_SOURCE_STAT_TESTS_PASS")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test: return _test()
    if args.output is None: p.error("--output required")
    d1=json.loads(SRC1.read_text());d2=json.loads(SRC2.read_text())
    if d1!=d2: raise ValueError("Two original independent source audits do not match")
    result=source_audit(d1)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_LOCKED_PAIRED_QUERY_ECONOMY",json.dumps(result,sort_keys=True))

if __name__=="__main__": main()

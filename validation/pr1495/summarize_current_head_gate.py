#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from itertools import combinations
from pathlib import Path

FAIL_RE=re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE=re.compile(r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved")

def parse(path:Path, expected:int)->dict:
    text=path.read_text(encoding="utf-8",errors="replace")
    failed=sorted({int(x) for x in FAIL_RE.findall(text)})
    success=[i for i in range(expected) if i not in set(failed)]
    summaries=SUMMARY_RE.findall(text)
    if not summaries:
        raise RuntimeError(f"missing replay summary: {path}")
    replayed,saved,denom,pct=summaries[-1]
    if int(replayed)!=expected or int(denom)!=expected or int(saved)!=len(success):
        raise RuntimeError(f"inconsistent replay summary in {path}: {summaries[-1]} vs {success}")
    return {"success_episode_ids":success,"failed_episode_ids":failed,"success_count":len(success),"summary_percent":float(pct)}

def jaccard(a,b):
    a,b=set(a),set(b)
    u=a|b
    return 1.0 if not u else len(a&b)/len(u)

def summarize(root:Path,name:str,repeats:int,expected:int)->dict:
    runs=[parse(root/name/f"repeat_{i}.log",expected) for i in range(repeats)]
    sets=[tuple(x["success_episode_ids"]) for x in runs]
    distinct=sorted(set(sets))
    pairs=[jaccard(sets[i],sets[j]) for i,j in combinations(range(repeats),2)]
    return {
      "success_counts":[x["success_count"] for x in runs],
      "distinct_success_sets":[list(x) for x in distinct],
      "exactly_repeatable":len(distinct)==1,
      "min_pairwise_jaccard":min(pairs) if pairs else 1.0,
      "runs":runs,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--repeats",type=int,default=5)
    p.add_argument("--expected",type=int,default=10)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    names=["main","pr_current","pr_current_plus_1472"]
    variants={n:summarize(a.root,n,a.repeats,a.expected) for n in names}
    main_set=variants["main"]["distinct_success_sets"]
    pr_set=variants["pr_current"]["distinct_success_sets"]
    ctrl_set=variants["pr_current_plus_1472"]["distinct_success_sets"]
    all_repeatable=all(variants[n]["exactly_repeatable"] for n in names)
    exact_main_parity=all_repeatable and pr_set==main_set
    controller_mapping_invariant=all_repeatable and ctrl_set==pr_set
    report={
      "schema_version":1,
      "source_identities":{
        "main":"62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
        "pr_current":"875ae4d8777678119b2f192ee186c6c15e6894d5",
        "controller_1472":"eed9be164797d41540421bda8adb3840377d7087"
      },
      "protocol":{
        "task":"PegInsertionSide-v1",
        "control_mode":"pd_ee_delta_pose",
        "backend":"physx_cpu",
        "use_first_env_state":True,
        "fresh_process_repeats":a.repeats,
        "episodes_per_repeat":a.expected,
      },
      "variants":variants,
      "gates":{
        "all_exactly_repeatable":all_repeatable,
        "current_pr_execution_parity_with_main":exact_main_parity,
        "current_pr_invariant_to_1472_sign_mapping":controller_mapping_invariant,
        "maintainer_evidence_gate_pass":all_repeatable and exact_main_parity and controller_mapping_invariant,
      },
      "claim_boundary":"Exact current PR-head replay gate on the frozen first-10 official PegInsertionSide demonstrations. Passing establishes repeatable execution parity for this protocol and compatibility with the #1472 sign mapping; it is not policy-training improvement, general task equivalence, real-robot safety, or upstream adoption."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()

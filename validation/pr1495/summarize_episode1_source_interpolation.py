#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

FAIL_RE=re.compile(r"Episode\s+(\d+)\s+is not replayed successfully")
SUMMARY_RE=re.compile(r"Replayed\s+(\d+)\s+episodes,\s+(\d+)/(\d+)=([0-9.]+)% demos saved")

def parse(path, expected):
    text=path.read_text(encoding="utf-8",errors="replace")
    failed=sorted({int(x) for x in FAIL_RE.findall(text)})
    success=[i for i in range(expected) if i not in set(failed)]
    matches=SUMMARY_RE.findall(text)
    if not matches:
        raise RuntimeError(f"missing replay summary in {path}")
    replayed,saved,denom,pct=matches[-1]
    if int(replayed)!=expected or int(denom)!=expected or int(saved)!=len(success):
        raise RuntimeError(f"inconsistent replay summary in {path}: {matches[-1]} vs {success}")
    return {"success_episode_ids":success,"failed_episode_ids":failed,"success_count":len(success),"success_fraction":len(success)/expected}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--expected",type=int,default=10)
    p.add_argument("--alphas",nargs="+",type=float,required=True)
    a=p.parse_args()
    rows=[]
    for alpha in a.alphas:
        key=str(alpha).replace(".","p")
        row=parse(a.root/f"alpha_{key}.log",a.expected)
        row["alpha"]=alpha
        row["episode1_success"]=1 in row["success_episode_ids"]
        rows.append(row)

    canonical_main=[0,1,3,4,5,6,7,8,9]
    canonical_v2=[0,3,4,5,6,7,8,9]
    alpha0=next(r for r in rows if abs(r["alpha"]-0.0)<1e-12)
    alpha1=next(r for r in rows if abs(r["alpha"]-1.0)<1e-12)
    endpoints={
      "alpha0_matches_main":alpha0["success_episode_ids"]==canonical_main,
      "alpha1_matches_v2":alpha1["success_episode_ids"]==canonical_v2,
    }
    valid=all(endpoints.values())
    transition=None
    if valid:
        prior=rows[0]["episode1_success"]
        for row in rows[1:]:
            if row["episode1_success"] != prior:
                transition={"between_alpha":[rows[rows.index(row)-1]["alpha"],row["alpha"]],"from_success":prior,"to_success":row["episode1_success"]}
                break
            prior=row["episode1_success"]

    report={
      "schema_version":1,
      "protocol":"source-level converter interpolation on frozen first-10 serial replay",
      "alphas":a.alphas,
      "rows":rows,
      "endpoint_gate":endpoints,
      "valid_for_causal_interpretation":valid,
      "first_episode1_transition":transition,
      "claim_boundary":"Intermediate alpha points are interpretable only when both endpoint-equivalence checks pass. This is a task-basin witness for one frozen replay protocol, not a general robustness law.",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if not valid:
        raise SystemExit("endpoint-equivalence gate failed; causal interpretation forbidden")

if __name__=="__main__":
    main()

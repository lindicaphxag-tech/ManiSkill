"""Interleaved within-one-runner physics getter intervention audit.

Every child subprocess gets its own fresh processes and the exact same
hash-pinned PPO/seed; only the declared read probes change.
This is a *diagnostic*, not a task-performance holdout.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ORDER=[
    ("none","qpos","tcp","both"),
    ("both","tcp","qpos","none"),
    ("qpos","both","none","tcp"),
    ("tcp","none","both","qpos"),
]
rows=[]
Path("getter_factorial_artifacts").mkdir(exist_ok=True)
for block,modes in enumerate(ORDER):
    for mode in modes:
        env=dict(os.environ,CST_PROBE_MODE=mode)
        run=subprocess.run(
            [sys.executable,"research/frozen_ppo_ee_swap.py"],
            env=env,capture_output=True,text=True,
            check=False,
        )
        if run.returncode != 0:
            print("PROBE_ABLATION_CHILD_ERROR",mode,run.stderr[-4000:],flush=True)
            raise RuntimeError(f"mode {mode} child exited {run.returncode}")
        original=Path("frozen_ppo_controller_swap.json")
        if not original.exists():
            raise RuntimeError(f"Missing experiment artifact for mode {mode}")
        results=json.loads(original.read_text())
        episode=results["episodes"][0]
        outcome=dict(block=block,mode=mode,
            sha=episode["initial_obs_sha256"],
            source=episode["success_once"]["source"],
            compiled=episode["success_once"]["compiled"],
            naive=episode["success_once"]["naive"],
            steps=episode["episode_steps"])
        rows.append(outcome)
        Path(f"getter_factorial_artifacts/{block}_{mode}.json").write_text(
            json.dumps({"outcome":outcome,"raw":results},indent=2)
        )
        print("GETTER_CAUSAL_TRIAL",json.dumps(outcome,sort_keys=True),flush=True)

fingerprints={r["sha"] for r in rows}
if len(fingerprints)!=1:
    raise AssertionError("Initial physical task observation changed across probe modes")
counts={m:sum(r["compiled"] for r in rows if r["mode"]==m)
        for m in ("none","qpos","tcp","both")}
source_counts={m:sum(r["source"] for r in rows if r["mode"]==m)
        for m in ("none","qpos","tcp","both")}
summary={"same_sha":next(iter(fingerprints)),"n":len(rows),
         "compiled_success_counts":counts,"source_success_counts":source_counts,
         "rows":rows}
Path("getter_factorial_artifacts/summary.json").write_text(
    json.dumps(summary,indent=2))
print("GETTER_CAUSAL_FINAL",json.dumps({k:v for k,v in summary.items() if k!="rows"}),flush=True)

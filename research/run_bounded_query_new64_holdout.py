"""Frozen-exact-method NEW 64-seed holdout: no edits to original policy/compiler.

Original bounded-or-query PhysX method commit db4fe4dd9d09aaff67c5dcf12213ad737162282d.
This file may ONLY change seed routing, verification, output name; cannot change
original source algorithm, robust budgets or any controller information access.
All failed physical task states retained. No cross-robot or hardware claims.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

TASK=os.environ.get("ABI_TASK")
CHUNK=int(os.environ.get("ABI_CHUNK","-1"))
FIRST={"pull_cube":142001,"stack_cube":152001}
if TASK not in FIRST or CHUNK not in (0,1,2,3):
    raise RuntimeError("Only 8 frozen new 8-state holdout task chunks permitted")

import frozen_ppo_ack_bounded_query as original

seed_list=tuple(range(FIRST[TASK]+8*CHUNK,FIRST[TASK]+8*(CHUNK+1)))
if len(seed_list)!=8 or seed_list[0]<FIRST[TASK] or seed_list[-1]>FIRST[TASK]+31:
    raise RuntimeError("Out-of-protocol seed set")
if original.TASK!=TASK or original.FAULT_STEP!=2 or original.POS_BUDGET!=.05 or original.ROT_BUDGET!=.05:
    raise RuntimeError("Original method semantics unexpectedly changed")
if tuple(original.SEEDS)==seed_list:
    raise RuntimeError("New validation seeds overlap original discovery cohort")

original.SEEDS=seed_list
old=original.COHORT[TASK]
original.COHORT[TASK]=(old[0],seed_list)
original.main()

src=Path(f"unknown_ack_bounded_query_{TASK}_original8.json")
if not src.is_file():
    raise RuntimeError("Original official simulator method produced no raw JSON")
raw=src.read_bytes()
d=json.loads(raw)
names=tuple(original.NAMES)
rows=d["episodes"]
if d.get("original_seed_population")!=list(seed_list) or len(rows)!=8:
    raise RuntimeError("Original 8 unique holdout states missing")
if [r["seed"] for r in rows]!=list(seed_list):
    raise RuntimeError("Original episode identity/order altered")
for r in rows:
    if any(r["faults"].get(n) is None for n in names[1:]):
        raise RuntimeError("Fault not physically reached; cannot silently omit it")
    if any(not isinstance(r["success_once"].get(n),bool) for n in names):
        raise RuntimeError("Missing official source/target task success result")
    if r["privileged_target_readback_decision_count"]["fault_robust_two_history_without_query"]!=0:
        raise RuntimeError("No-query arm consulted private target state")
    if r["privileged_target_readback_decision_count"]["fault_robust_then_single_privileged_query"] not in (0,1):
        raise RuntimeError("Selective query budget exceeded")
    if r["privileged_target_readback_decision_count"]["fault_always_single_privileged_query"]!=1:
        raise RuntimeError("Mandatory-query baseline violated one query per fault")

dst=Path(f"bounded_query_holdout_{TASK}_chunk{CHUNK}_original8.json")
dst.write_bytes(raw)
print("NEW64_UNALTERED_SOURCE_OUTCOME",json.dumps({
    "task":TASK,"chunk":CHUNK,"seeds":list(seed_list),
    "source_json_sha256":hashlib.sha256(raw).hexdigest(),
    "success":d["success_counts"],
    "readback_count_selective":sum(d["selective_readback_counts"]),
    "readback_count_always":8,
    "total_bounded_authorizations_no_query":d["robust_no_query_authorization_count"],
    "source_method_sha":"db4fe4dd9d09aaff67c5dcf12213ad737162282d",
    "new_seeds_preregistered":True
},sort_keys=True))

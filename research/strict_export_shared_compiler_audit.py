"""Strict JSON transport audit for archived native PhysX source; NO simulation.

Original Python-json Infinity values represent UNBOUNDED ROTATION at certain
negative-control controller refusals. Preserve authentic original archive; use
tagged, standards-compliant JSON for portable independent review.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence/shared_compiler_postquery_causal_original64_1480001_1490032")
ORIG=ROOT/"original_independent_full64_audit.json"
STRICT=Path("research/frozen_policy_transfer/derived/shared_compiler_causal64_strict_json.json")
TAG={"nonfinite_numeric":"positive_infinity"}

def fail(message):
    raise ValueError(message)

def _constant(value):
    if value != "Infinity":
        fail(f"Unexpected non-finite numeric source constant: {value}")
    return dict(TAG)

def _scan_tag(node,path=()):
    if isinstance(node,dict):
        if node==TAG:
            return [path]
        hits=[]
        for key,value in node.items():
            hits.extend(_scan_tag(value,path+(key,)))
        return hits
    if isinstance(node,list):
        hits=[]
        for i,value in enumerate(node):
            hits.extend(_scan_tag(value,path+(i,)))
        return hits
    return []

def audit():
    manifest=ROOT/"ORIGINAL_SHA256SUMS"
    lines=manifest.read_text().splitlines()
    source_lines=[x for x in lines if x.endswith("  original_independent_full64_audit.json")]
    if len(source_lines)!=1: fail("Expected one archived ORIGINAL independent full-source checksum")
    expected_sha=source_lines[0].split("  ")[0]
    raw=ORIG.read_bytes()
    source_sha=hashlib.sha256(raw).hexdigest()
    if source_sha!=expected_sha: fail("Original source modified or corrupted")
    original=json.loads(raw,parse_constant=_constant)
    strict_content=STRICT.read_text()
    def reject_nonfinite(value):
        fail("Portable JSON contains bare non-finite numeric value: "+value)
    portable=json.loads(strict_content,parse_constant=reject_nonfinite)
    if original!=portable: fail("Portable output does not exactly preserve original parsed semantic tree")
    tags=_scan_tag(portable)
    if len(tags)!=3 or not all(path[-1]=="worst_rotation_rad" for path in tags):
        fail("Unexpected original Infinity diagnostics; count or paths changed")
    if portable.get("unique_source_reset_states")!=64 or portable.get("actually_stepped_simulator_worlds")!=576:
        fail("Changed original source cohort denominator")
    if portable.get("all_compiler_traces_valid") is not True:
        fail("Original matched post-query compiler gate absent")
    if portable.get("outcomes")!={"public":{"private_reads":48,"task_success":53},
              "fixed_t5":{"private_reads":64,"task_success":53},
              "strong_task":{"private_reads":60,"task_success":50},
              "always_held":{"private_reads":0,"task_success":33}}:
        fail("Original complete strategy endpoints changed")
    rows=portable.get("all_episodes",[])
    if len(rows)!=64: fail("Original 64 source rows missing")
    actual_seeds={(x["task"],x["seed"]) for x in rows}
    expected_seeds={("pull_cube",n) for n in range(1480001,1480033)} | {
                    ("stack_cube",n) for n in range(1490001,1490033)}
    if actual_seeds!=expected_seeds: fail("Original task/seed identities changed")
    paired=collections.Counter()
    strata=collections.Counter()
    for row in rows:
        if not (row.get("pre_t5_matched") is True and row.get("postquery_shared_compiler_gate") is True):
            fail("Missing source-recorded equality of physical prefix/post-query compiler")
        if type(row.get("new_success")) is not bool or type(row.get("fixed_success")) is not bool:
            fail("Original task success flags invalid")
        paired[(row["new_success"],row["fixed_success"])]+=1
        strata[(row["task"],row["truth"])]+=1
    if paired != {(True,True):53,(False,False):11}:
        fail("A paired public-versus-fixed episode was dropped or mutated")
    if len(strata)!=8 or set(strata.values())!={8}:
        fail("Original four true physical faults per task not balanced")
    return {
       "original_source_sha256":source_sha,
       "source_independent_audit_preserved":True,
       "new_strict_derivative_not_new_physics":True,
       "total_original_reset_states":64,
       "actual_physx_controller_worlds":576,
       "identical_physical_prefix_and_postquery_compiler":True,
       "paired_both_succeed":53,
       "paired_both_fail":11,
       "public_only_succeed":0,
       "fixed_only_succeed":0,
       "private_reads_public":48,
       "private_reads_fixed":64,
       "source_nonfinite_diagnostic_fields_converted_to_tags":len(tags),
       "original_nonfinite_paths":[list(x) for x in tags],
       "outside_independent_replication":False,
       "same_total_sensor_information_budget":False,
    }

if __name__=="__main__":
    print("SOURCE_AUTHENTICATED_STRICT_PORTABLE_JSON_AUDIT",json.dumps(audit(),sort_keys=True))

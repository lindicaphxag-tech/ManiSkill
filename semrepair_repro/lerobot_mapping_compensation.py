#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


TARGETS={"to_relative_actions","to_absolute_actions"}


def _slice_uses_prefix_state(fn: ast.FunctionDef) -> bool:
    """Return True iff the function assigns a state-derived prefix slice to state_offset."""
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id=="state_offset" for t in node.targets):
            continue
        text=ast.unparse(node.value)
        # Current upstream multiplies the state prefix by mask_t.
        if "state[..., :dims]" in text and "mask_t" in text:
            return True
    return False


def inspect_upstream(path: Path) -> dict:
    source=path.read_text(encoding="utf-8")
    tree=ast.parse(source)
    funcs={
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in TARGETS
    }
    missing=TARGETS-set(funcs)
    if missing:
        raise RuntimeError(f"missing upstream helpers: {sorted(missing)}")
    prefix={name:_slice_uses_prefix_state(fn) for name,fn in funcs.items()}
    return {
        "source_sha256":hashlib.sha256(source.encode()).hexdigest(),
        "prefix_state_contract":prefix,
        "both_use_same_prefix_state_contract":all(prefix.values()),
    }


def apply_current_forward(action,state,mask):
    dims=len(mask)
    base=state[:dims]
    out=list(action)
    for i,use_relative in enumerate(mask):
        if use_relative:
            out[i]-=base[i]
    return out


def apply_current_inverse(relative,state,mask):
    dims=len(mask)
    base=state[:dims]
    out=list(relative)
    for i,use_relative in enumerate(mask):
        if use_relative:
            out[i]+=base[i]
    return out


def apply_correct_forward(action,state,mask,indices):
    out=list(action)
    base=[state[i] for i in indices]
    for i,use_relative in enumerate(mask):
        if use_relative:
            out[i]-=base[i]
    return out


def linf(a,b):
    return max(abs(x-y) for x,y in zip(a,b))


def l2(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))**0.5


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--upstream-sha",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()

    source=a.source_root/"src/lerobot/processor/relative_action_processor.py"
    inspection=inspect_upstream(source)
    if not inspection["both_use_same_prefix_state_contract"]:
        raise SystemExit("pinned upstream source no longer matches the audited contract")

    # Realistic interleaved [position, velocity] state plus gripper.
    state=[
        10.0,0.1,
        20.0,0.2,
        30.0,0.3,
        40.0,0.4,
        50.0,0.5,
        60.0,0.6,
        99.0,
    ]
    action=[11.0,22.0,33.0,44.0,55.0,66.0,7.0]
    mask=[True,True,True,True,True,True,False]
    correct_indices=[0,2,4,6,8,10,12]

    current_relative=apply_current_forward(action,state,mask)
    recovered=apply_current_inverse(current_relative,state,mask)
    correct_relative=apply_correct_forward(action,state,mask,correct_indices)

    roundtrip_linf=linf(recovered,action)
    forward_linf=linf(current_relative,correct_relative)
    forward_l2=l2(current_relative,correct_relative)

    # A small deterministic sweep makes the identifiability point explicit:
    # for arbitrary prefix-anchor perturbations, the paired wrong inverse still
    # cancels the paired wrong forward transform exactly.
    sweep=[]
    for k in range(1,33):
        st=[
            10.0+k,0.01*k,
            20.0+2*k,0.02*k,
            30.0+3*k,0.03*k,
            40.0+4*k,0.04*k,
            50.0+5*k,0.05*k,
            60.0+6*k,0.06*k,
            99.0+k,
        ]
        act=[12.0+k,23.0+2*k,34.0+3*k,45.0+4*k,56.0+5*k,67.0+6*k,7.0]
        rel=apply_current_forward(act,st,mask)
        back=apply_current_inverse(rel,st,mask)
        correct=apply_correct_forward(act,st,mask,correct_indices)
        sweep.append({
            "roundtrip_linf_error":linf(back,act),
            "forward_semantic_linf_error":linf(rel,correct),
        })

    report={
        "schema_version":2,
        "case":"LeRobot relative-action state/action mapping",
        "upstream_repo":"huggingface/lerobot",
        "upstream_sha":a.upstream_sha,
        "source_path":"src/lerobot/processor/relative_action_processor.py",
        "source_sha256":inspection["source_sha256"],
        "issue":"https://github.com/huggingface/lerobot/issues/3863",
        "source_contract":inspection["prefix_state_contract"],
        "input":{
            "state_layout":"[j0p,j0v,j1p,j1v,...,j5p,j5v,gripper]",
            "state":state,
            "action_layout":"[j0p,j1p,j2p,j3p,j4p,j5p,gripper]",
            "action":action,
            "mask":mask,
            "correct_state_indices":correct_indices,
        },
        "current_relative":current_relative,
        "correct_relative":correct_relative,
        "current_roundtrip_recovered":recovered,
        "metrics":{
            "roundtrip_linf_error":roundtrip_linf,
            "forward_semantic_linf_error":forward_linf,
            "forward_semantic_l2_error":forward_l2,
            "sweep_cases":len(sweep),
            "sweep_max_roundtrip_linf_error":max(x["roundtrip_linf_error"] for x in sweep),
            "sweep_min_forward_semantic_linf_error":min(x["forward_semantic_linf_error"] for x in sweep),
        },
        "certificate":{
            "source_bound_to_same_prefix_contract":inspection["both_use_same_prefix_state_contract"],
            "self_consistency_passes":roundtrip_linf <= 1e-12,
            "forward_semantics_fail":forward_linf > 1e-3,
            "all_sweep_roundtrips_pass":all(x["roundtrip_linf_error"] <= 1e-12 for x in sweep),
            "all_sweep_forward_semantics_fail":all(x["forward_semantic_linf_error"] > 1e-3 for x in sweep),
            "compensating_inverse_hides_forward_defect":(
                roundtrip_linf <= 1e-12
                and forward_linf > 1e-3
                and all(x["roundtrip_linf_error"] <= 1e-12 for x in sweep)
                and all(x["forward_semantic_linf_error"] > 1e-3 for x in sweep)
            ),
        },
        "claim_boundary":(
            "This witness AST-inspects the exact pinned upstream helper bodies to "
            "bind the evidence to their shared positional-prefix contract, then "
            "evaluates that contract on an explicit non-prefix state/action layout. "
            "It establishes a semantic self-consistency blind spot, not policy "
            "performance or upstream adoption."
        ),
    }

    if not report["certificate"]["compensating_inverse_hides_forward_defect"]:
        raise SystemExit("expected compensation witness did not reproduce")

    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

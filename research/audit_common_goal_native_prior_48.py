"""Retrospective audit of original 48 PhysX pilot target histories (NOT new policy worlds).

Source artifact #38294905276 yields only FOUR independent reset groups
per robot. Model goal is the source-constructible intended applied target.
Assume zero model error for a mathematical diagnostic ONLY: this is neither
a calibrated physical error nor a safe robot execution decision.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from research.terminal_common_action_certificate import (
    conditional_common_position_authority,
)

EXPECTED_SHA={
    "panda":"dbffada47a6a4a89633f58ee269fa19f5b95f87ac33d80fbed6099aefdf4d1be",
    "xarm6_robotiq":"cb4ba4a05983f2b40dd9a4bca0efbd7747f6e5a192551aded524c6c009e42153",
}
TOLS=(.0005,.001,.0015,.002)


def audit(path: Path):
    raw=path.read_bytes()
    d=json.loads(raw)
    robot=d["robot"]
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=EXPECTED_SHA[robot]:
        raise RuntimeError("Original PhysX JSON changed: refuse retrospective re-score")
    if d["original_native_physx_worlds"]!=24 or d["original_unique_reset_clusters"]!=4:
        raise ValueError("Original physical/reset denominator unexpected")
    grouped={}
    for row in d["rows"]:
        if row["probe_id"]=="zero" and row["truth_score_only"]=="held":
            if row["seed"] in grouped: raise ValueError("Duplicate original reset")
            grouped[row["seed"]]=row
    if len(grouped)!=4: raise ValueError("Original data missing reset group")
    diagnostics=[]
    for seed,row in sorted(grouped.items()):
        target=row["model_predicted_hidden_targets_xyz"]
        if set(target)!={"held","applied"}: raise ValueError("Source history family changed")
        x=np.asarray([target["held"],target["applied"]],dtype=float)
        diff=x[1]-x[0]
        if not np.allclose(diff,[.0025,-.002,.001],atol=1e-8,rtol=0):
            raise ValueError("Original source target-memory difference changed")
        results={}
        for tolerance in TOLS:
            out=conditional_common_position_authority(
                x,x[1],np.ones(3)*tolerance,
                [-.1]*3,[.1]*3,
                external_error_bound_xyz=[0.]*3,
                external_error_envelope_attested=True,
            )
            # This supplies an *assumed* zero-error mathematical witness,
            # NOT independent physical attestation.
            results[str(tolerance)]={"mathematical_feasible":out.authorized,
                "max_axis_residual_m":out.maximum_axis_residual_m,
                "necessary_half_diameter_m":out.historical_half_diameter_m}
        diagnostics.append({"seed":seed,"history_target_difference_m":diff.tolist(),
                            "conditional_only":results})
    total={str(t):sum(row["conditional_only"][str(t)]["mathematical_feasible"]
                       for row in diagnostics) for t in TOLS}
    if total!={"0.0005":0,"0.001":0,"0.0015":4,"0.002":4}:
        raise AssertionError("Descriptive certificate gate not reproducible")
    return {"robot":robot,"original_artifact_sha256":sha,
        "n_independent_original_resets":4,
        "n_new_physx_worlds":0,
        "diagnostic_uses_unverified_zero_response_error":True,
        "does_not_certify_safe_task_continuation":True,
        "original_reset_rows":diagnostics,"feasible_resets_by_tolerance_m":total}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--panda",type=Path,required=True)
    ap.add_argument("--xarm",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    v=ap.parse_args()
    res={"panda":audit(v.panda),"xarm6_robotiq":audit(v.xarm)}
    v.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:x["feasible_resets_by_tolerance_m"] for k,x in res.items()}))

"""Recompute all physical probe-induced controller-memory shifts without labels."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

ROBOTS={"panda":990001,"xarm6_robotiq":991001}
TRUTHS=("held","applied")
PROBES=("zero","x","y")
BLOB="34cb7673a0d5acd64be25d03b926ea6b0f20b54c"
SOURCE="3b2faf44e5f413911eae25ccfd0c51fbbe2d5fe7"

def audit(directory):
    path=Path(directory)
    by={}
    for robot,start in ROBOTS.items():
        for chunk in (0,1):
            filename=path/f"causal_probe_{robot}_chunk{chunk}.json"
            raw=json.loads(filename.read_text())
            if (raw["frozen_proto_blob"]!=BLOB or raw["frozen_native_source_blob"]!=SOURCE
                or raw["robot"]!=robot or raw["chunk"]!=chunk
                or raw["independent_reset_clusters"]!=4 or raw["physical_worlds"]!=24
                or raw["seeds"]!=list(range(start+4*chunk,start+4*chunk+4))
                or not raw["no_trained_policy_task_success_claim"]
                or not raw["oracle_used_only_for_post_action_audit"]):
                raise ValueError("Source/predeclared population corrupted: "+str(filename))
            for row in raw["rows"]:
                key=(row["robot"],row["seed"],row["truth_posthoc_only"],row["probe"])
                if (key in by or row["robot"]!=robot or row["seed"] not in raw["seeds"]
                    or row["truth_posthoc_only"] not in TRUTHS
                    or row["probe"] not in PROBES
                    or not row["actual_native_physx_cpu"]
                    or row["oracle_targets_used_by_decision"]
                    or not row["native_source_action_reached"]
                    or row["task_success_measured"]):
                    raise ValueError("Duplicate or invalid physical world record")
                by[key]=row
    expected={(robot,seed,truth,probe) for robot,start in ROBOTS.items()
              for seed in range(start,start+8) for truth in TRUTHS for probe in PROBES}
    if set(by)!=expected:
        raise ValueError("Incomplete registered 96-world physical matrix")
    results={}
    pairs=[]
    for robot,start in ROBOTS.items():
        for seed in range(start,start+8):
            for truth in TRUTHS:
                rr={p:by[robot,seed,truth,p] for p in PROBES}
                origin=rr["zero"]["target_before_t3_position_m"]
                # Exactly matched until t3; target is audit-only, not observed by controller decision.
                pre_max=max(math.dist(origin,rr[p]["target_before_t3_position_m"]) for p in PROBES)
                if pre_max>1e-5:raise ValueError("Before-probe native targets are not matched")
                paired={}
                for p in PROBES:
                    current=rr[p]["target_after_t3_position_m"]
                    metric=float(rr[p]["target_change_translation_l2_m"])
                    if not math.isfinite(metric) or metric<0:
                        raise ValueError("Nonfinite target transition")
                    paired[p]=dict(delta_from_before_mm=1000*metric,
                        after_zero_target_delta_mm=1000*math.dist(
                            current,rr["zero"]["target_after_t3_position_m"]),
                        public_delta_norm_mm=1000*math.dist(rr[p]["public_xyz_delta"],[0.,0.,0.]))
                pairs.append(dict(robot=robot,seed=seed,truth=truth,probe=paired))
        rows=[x for x in pairs if x["robot"]==robot]
        def avg(f):return sum(f(x) for x in rows)/len(rows)
        results[robot]=dict(independent_reset_clusters=8,correlated_fault_truths=16,
            mean_target_action_translation_mm={p:avg(lambda x:x["probe"][p]["delta_from_before_mm"]) for p in PROBES},
            mean_postprobe_target_difference_from_zero_mm={p:avg(lambda x:x["probe"][p]["after_zero_target_delta_mm"]) for p in PROBES},
            mean_public_xyz_norm_mm={p:avg(lambda x:x["probe"][p]["public_delta_norm_mm"]) for p in PROBES})
    return dict(scope="NEW_AUTHOR_OPERATED_SCRIPTED_NATIVE_PHYSX_CAUSAL_MECHANISM_ONLY",
        actual_simulator_worlds=96,independent_reset_clusters=16,
        learned_policy_task_success_evaluated=False,
        native_controller_target_oracle_used_for_control=False,
        preregistered_before_outcome=True,by_robot=results,all_pairs=pairs)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    result=audit(args.input_dir)
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result["by_robot"],indent=2))

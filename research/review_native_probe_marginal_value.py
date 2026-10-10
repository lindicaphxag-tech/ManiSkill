"""Immutable, read-only archived PhysX paired-reset analysis.

No fresh simulation and no VLA manipulation success. Unit of independence is
task/reset cluster, not 96 physically stepped correlated conditions.
"""
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

SHAS={
 "low_signal_holdout_panda_chunk0.json":"88e4a1474113a481f7ecc0ac6e563d66a68a08735c41312e3c5803dd619ab342",
 "low_signal_holdout_panda_chunk1.json":"80328f77d24ae2f5ff64fe5153f8f4e086767f0589287b60eed55c04ccbe0d9e",
 "low_signal_holdout_xarm6_robotiq_chunk0.json":"4045aea315394c0326e4087c2368af4edf5a7abdf052fa3550cea54c92d211e2",
 "low_signal_holdout_xarm6_robotiq_chunk1.json":"c702186cdf328ffd2ed6ae89e9455df5b53da53139989269367f5a283eec5986",
}
SEEDS={"panda":range(700001,700009),"xarm6_robotiq":range(710001,710009)}
PROBES=("zero","x","y")
TRUTHS=("applied","held")

def audit(directory):
    root=Path(directory)
    groups=defaultdict(dict)
    for name, sha in SHAS.items():
        raw=(root/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:
            raise ValueError("Archive content differs from frozen SHA256: "+name)
        source=json.loads(raw)
        if (source.get("original_actual_native_physx_worlds")!=24
            or len(source.get("original_rows",[]))!=24):
            raise ValueError("Missing original native physics rows")
        for row in source["original_rows"]:
            robot, seed = row["robot"], row["seed"]
            p,truth = row["known_delivered_native_probe_id"],row["hidden_physical_truth_posthoc_only"]
            if (robot not in SEEDS or seed not in SEEDS[robot]
                or p not in PROBES or truth not in TRUTHS):
                raise ValueError("Not frozen heldout robot/reset/truth")
            if (not row["real_physx_cpu"]
                or not row["command_execution_ack_hidden_from_classifier"]
                or row["private_target_reads_before_classification"] != 0):
                raise ValueError("Invalid native/blinding record")
            key=(robot,seed)
            if (p,truth) in groups[key]:
                raise ValueError("Duplicate physical condition")
            groups[key][p,truth]=row
    expected={(r,s) for r,seeds in SEEDS.items() for s in seeds}
    if set(groups)!=expected:
        raise ValueError("Wrong number of independent reset clusters")
    paired=[]
    for (robot,seed),cells in sorted(groups.items()):
        if set(cells)!={(p,t) for p in PROBES for t in TRUTHS}:
            raise ValueError("Incomplete physically paired ACK worlds")
        distances={}
        correct={}
        for p in PROBES:
            x=cells[p,"applied"]["decision"]["public_motion_xyz_m"]
            y=cells[p,"held"]["decision"]["public_motion_xyz_m"]
            if len(x)!=3 or len(y)!=3:
                raise ValueError("Wrong public XYZ dimension")
            distances[p]=1000*math.dist(x,y)
            correct[p]=sum(cells[p,truth]["decision"]["label"]==truth
                           for truth in TRUTHS)
        paired.append({"robot":robot,"seed":seed,
                       "separation_mm":distances,"correct_truths":correct})
    by={}
    for robot in SEEDS:
        rr=[r for r in paired if r["robot"]==robot]
        avg=lambda xs:sum(xs)/len(xs)
        by[robot]={
            "independent_resets":len(rr),
            "heldout_truths_per_probe":2*len(rr),
            "mean_separation_mm":{p:avg([x["separation_mm"][p] for x in rr])
                                  for p in PROBES},
            "correct_truths":{p:sum(x["correct_truths"][p] for x in rr)
                              for p in PROBES},
            "mean_x_minus_zero_mm":avg([x["separation_mm"]["x"]-x["separation_mm"]["zero"] for x in rr]),
            "mean_y_minus_zero_mm":avg([x["separation_mm"]["y"]-x["separation_mm"]["zero"] for x in rr]),
        }
    return {"scope":"ARCHIVED_AUTHOR_OPERATED_PHYSX_REANALYSIS_ONLY",
            "new_physx_executions":0,"vla_task_success_measured":False,
            "independent_reset_clusters":16,"physx_heldout_worlds":96,
            "source_sha256":SHAS,"by_robot":by,"paired_reset_rows":paired}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("archived_source_dir")
    args=p.parse_args()
    print(json.dumps(audit(args.archived_source_dir),indent=2))

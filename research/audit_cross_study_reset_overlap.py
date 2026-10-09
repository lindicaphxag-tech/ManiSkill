"""Cross-study reset-state and physical fault-truth overlap audit.

Scientific integrity: parallel research branches independently precommitted
overlapping seed ranges. This tool is not a PhysX rerun and does not infer
biological/statistical independence from simulation seeds alone.

Three separately frozen designs:
  primary held/held K4 64: 840001-840032 / 850001-850032
  survivor held/held K4 32: 860001-860016 / 870001-870016
  mixed applied/held K4 64: 860001-860032 / 870001-870032
An earlier held/held trial with the same task and reset seed is NOT a
previously unseen reset, even if another controller/policy arm is run.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTOCOLS={
    "primary64":("research/PPO_DISCRETE_HYPOTHESIS_NEW64_PREOUTCOME_V2.json",
                 "b8c5205ca949720a2d39396c9f8c711e65d7982b"),
    "survivor32":("research/SURVIVOR_CONDITIONED_SO3_NEW32_PRECOMMIT_V1.json",
                  "a51b01d66e2211058854015a31138f6a838eec71"),
    "mixed64":("research/MIXED_ACK_TRUTH_PPO_NEW64_PREOUTCOME_V1.json",
               "039868da753f6fc37217036ed632bf6dca953228"),
}
TASKS=("pull_cube","stack_cube")


def checked_protocols(root:Path=ROOT):
    out={}
    for key,(name,pinned) in PROTOCOLS.items():
        try:
            digest=subprocess.check_output(["git","hash-object",name],cwd=root,text=True).strip()
        except (OSError,subprocess.CalledProcessError) as ex:
            raise ValueError(f"Missing original immutable pre-outcome protocol: {name}") from ex
        if digest!=pinned:
            raise ValueError(f"Original preregistration changed: {key}")
        out[key]=json.loads((root/name).read_text(encoding="utf-8"))
    return out


def registered_pairs(protocols:dict):
    a=protocols["primary64"]["experiment"]["new_seeds"]
    b=protocols["survivor32"]["new_population"]
    c=protocols["mixed64"]["unseen_population"]["tasks"]
    sets={}
    truth={}
    for task in TASKS:
        for study in ("primary64","survivor32","mixed64"):
            if study=="primary64":
                lo,hi=a[task]
                expected=32
            elif study=="survivor32":
                arr=b[f"{task}_seeds"]
                lo,hi=arr[0],arr[-1]
                if arr!=list(range(lo,hi+1)):
                    raise ValueError("Nonconsecutive or omitted original 32-state register")
                expected=16
            else:
                lo,hi=c[task]["start"],c[task]["end"]
                expected=32
            values=list(range(lo,hi+1))
            if len(values)!=expected:
                raise ValueError(f"Unexpected registered reset count for {study}/{task}")
            sets.setdefault(study,set()).update((task,seed) for seed in values)
            for seed in values:
                key=(study,task,seed)
                # In mixed source, t2 execution truth is precommitted
                # deterministically to the parity of that source seed.
                truth[key]=("applied" if study=="mixed64" and seed%2==0 else "held","held")
    return sets,truth


def analyze(root:Path=ROOT):
    regs,truth=registered_pairs(checked_protocols(root))
    pair_overlap={}
    names=tuple(PROTOCOLS)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            overlap=regs[a]&regs[b]
            pair_overlap[f"{a}__{b}"]={
                "reset_count":len(overlap),
                "reset_ids":[f"{task}:{seed}" for task,seed in sorted(overlap)]
            }
    reused=regs["survivor32"]&regs["mixed64"]
    same_truth=sum(truth[("survivor32",task,seed)]==
                   truth[("mixed64",task,seed)] for task,seed in reused)
    changed_truth=len(reused)-same_truth
    total_rows=sum(map(len,regs.values()))
    unique=len(set.union(*regs.values()))
    result={
        "status":"COHORT_OVERLAP_AUDIT_NOT_INDEPENDENT_PHYSX_REEXECUTION",
        "source_protocol_git_blobs_verified":{k:v[1] for k,v in PROTOCOLS.items()},
        "registered_episode_rows_across_three_studies":total_rows,
        "unique_task_reset_identifiers_across_three_studies":unique,
        "reused_original_reset_identifiers":total_rows-unique,
        "per_study_counts":{k:len(v) for k,v in regs.items()},
        "intersections":pair_overlap,
        "mixed64_reused_from_previous_survivor32":len(reused),
        "mixed64_wholly_new_task_reset_ids_relative_to_both_prior_studies":
            len(regs["mixed64"]-(regs["survivor32"]|regs["primary64"])),
        "reused_mixed_conditions_with_same_held_held_fault_truth":same_truth,
        "reused_reset_ids_with_DIFFERENT_t2_applied_truth":changed_truth,
        "distinct_controller_worlds_not_independent_reset_states":True,
        "public_model_calibration_seed_overlap_verified":False,
        "any_prior_task_success_or_baseline_selection_information_leakage_excluded":False,
        "claims_prohibited":[
            "160 unique independent task/reset states for these three studies",
            "64 entirely unseen initial reset states for the mixed-truth study relative to all earlier branches",
            "independent across all three study reset-state cohorts",
            "16 physically applied ACK-truth runs are the same condition as their held/held predecessors",
            "retrospective selection on these overlapping states is a prospective confirmation"
        ]
    }
    if (total_rows,unique,len(reused),same_truth,changed_truth)!=(160,128,32,16,16):
        raise ValueError("Unexpected registered seed or fault-truth overlap")
    if pair_overlap["primary64__mixed64"]["reset_count"]!=0 or pair_overlap["primary64__survivor32"]["reset_count"]!=0:
        raise ValueError("Claimed primary64 disjointness invalid")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    data=analyze(args.root)
    output=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(output,encoding="utf-8")
    print("THREE_COHORT_OVERLAP_PROVENANCE",output)


if __name__=="__main__":
    main()

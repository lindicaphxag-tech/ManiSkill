"""Source-pinned, RETROSPECTIVE achieved-response model falsification.

Data: original public ManiSkill PhysX, two executed-command truths x two tasks.
Calibrate each task on four reset seeds (BOTH truths), then test on four other
reset seeds (BOTH truths). All data had already been generated/published;
this is a diagnostic and NEVER prospective method efficacy evidence.

The decision uses only public before/after achieved EE xyz and two action-
history-computed target hypotheses. Labels are used to fit an error envelope
on the TRAIN split, and only scored AFTER decision on validation split.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import sqrt, isfinite
from pathlib import Path

SOURCE=Path("research/frozen_policy_transfer/evidence/public_response_ack_probe_32_negative")
TASKS={"pull_cube":140001, "stack_cube":150001}
TRUTHS=("applied_no_ack","neutral_arm_delta_no_ack")
GUARD_M=0.001  # fixed optimistic 1-mm empirical generalization allowance
ALPHA_LO=0.0
ALPHA_HI=1.0


def require(x,msg):
    if not x: raise ValueError(msg)


def xyz(values):
    a=tuple(float(x) for x in values)
    require(len(a)==3 and all(isfinite(y) for y in a),"Expected three finite public XYZ values")
    return a


def seg_distance(before,after,goal):
    d=[p-q for p,q in zip(goal,before)]
    dy=[p-q for p,q in zip(after,before)]
    length2=sum(z*z for z in d)
    alpha=(sum(a*b for a,b in zip(d,dy))/length2) if length2 else ALPHA_LO
    alpha=min(ALPHA_HI,max(ALPHA_LO,alpha))
    predicted=[p+alpha*v for p,v in zip(before,d)]
    return sqrt(sum((p-y)**2 for p,y in zip(predicted,after))),alpha


def read_originals(folder: Path):
    manifest=folder/"SOURCE_SHA256SUMS"
    require(manifest.is_file(),"Frozen original SHA256 source manifest absent")
    expected={}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        sha,name=line.split(maxsplit=1)
        name=name.removeprefix("./")
        require(name not in expected,"Repeated source file in manifest")
        expected[name]=sha
    wanted={f"physical_response_{task}_{truth}_{offset}_fresh4.json"
            for task in TASKS for truth in TRUTHS for offset in (0,4)}
    wanted.add("full_original_source_audit.json")
    require(set(expected)==wanted,"Manifest does not pin all and only nine source JSONs")
    for name,digest in expected.items():
        blob=(folder/name).read_bytes()
        require(hashlib.sha256(blob).hexdigest()==digest,
                "Original source file digest altered: "+name)
    data={}
    for task,first in TASKS.items():
        groups=[]
        for truth in TRUTHS:
            for offset in (0,4):
                p=folder/f"physical_response_{task}_{truth}_{offset}_fresh4.json"
                d=json.loads(p.read_text(encoding="utf-8"))
                require(d["truth"]==truth,"Wrong truth")
                require(d["seeds"]==list(range(first+offset,first+offset+4)),
                        "Missing or resequenced precommitted seeds")
                require(d["real_physx"] is True and d["training_performed"] is False,
                        "Not the original frozen real PhysX")
                require(len(d["rows"])==4,"Incomplete source rows")
                for row in d["rows"]:
                    require(row["seed"] in d["seeds"],"Unregistered state seed")
                    require(row["unknown_ack_truth"]==truth,"Outcome truth not independently recorded")
                    require(row["probe_reached"]["achieved_probe_classifier"] is True,
                            "No public motion probe completed")
                    require(row["private_memory_reads_during_action_decision"]["achieved_probe_classifier"]==0,
                            "Classifier received private memory")
                    groups.append(row)
        require(len(groups)==16,"Expected task×two-truth sixteen physical conditions")
        data[task]=groups
    return data


def evaluate(groups,first):
    train=[r for r in groups if first<=r["seed"]<first+4]
    test=[r for r in groups if first+4<=r["seed"]<first+8]
    require(len(train)==len(test)==8,"Split or pseudo-replication mismatch")
    require(set(r["seed"] for r in train).isdisjoint(
        set(r["seed"] for r in test)),"A reset seed appears in BOTH calibration and validation")
    def metrics(r):
        pair=r["probe_positions"]["achieved_probe_classifier"]
        before=xyz(pair["achieved_pre_probe_xyz"])
        after=xyz(pair["achieved_post_probe_xyz"])
        targets=r["candidate_goal_positions"]
        need={"held","applied"}
        require(set(targets)==need,"Ambiguous target provenance")
        return {name:seg_distance(before,after,xyz(targets[name]))[0]
                for name in ("held","applied")}

    # Predeclare scalar response gain alpha in [0,1]. Fit empirical envelope
    # ONLY to the true causal history on the calibration reset seeds.
    train_rows=[]
    for r in train:
        truth="held" if r["unknown_ack_truth"]=="neutral_arm_delta_no_ack" else "applied"
        distances=metrics(r)
        train_rows.append({"seed":r["seed"],"truth":truth,
                           "true_history_residual_m":distances[truth],
                           "wrong_history_residual_m":distances["held" if truth=="applied" else "applied"]})
    eps=max(q["true_history_residual_m"] for q in train_rows)+GUARD_M

    outcomes=[]
    for r in test:
        d=metrics(r)
        consistent={k:d[k]<=eps+1e-12 for k in d}
        chosen=([k for k in d if consistent[k]][0]
                if sum(consistent.values())==1 else None)
        status=("UNIQUE" if chosen else "AMBIGUOUS_BOTH" if all(consistent.values())
                else "REJECTS_BOTH" if not any(consistent.values()) else "UNHANDLED")
        # Truth checked only here for post-decision grading: NEVER a classifier input.
        truth="held" if r["unknown_ack_truth"]=="neutral_arm_delta_no_ack" else "applied"
        outcomes.append({
           "seed":r["seed"],"actual_fault_truth":r["unknown_ack_truth"],
           "public_only_history_decision":chosen,"certificate_status":status,
           "was_true_history_eliminated":not consistent[truth],
           "wrong_confident_authorization":chosen is not None and chosen!=truth,
           "original_nearest_target_decision":r["classifier"]["label"],
           "original_nearest_target_wrong":r["wrong_authorization"],
           "residual_to_each_history_m":d
        })
    return dict(calibration_seed_count=4,validation_seed_count=4,
       calibration_truth_conditions=8,validation_truth_conditions=8,
       physical_model_assumed="achieved_y=x+alpha*(commanded_target-x)+e, alpha in [0,1]",
       attenuation_gain_validity_unproven=True,
       empirical_training_error_bound_m=eps,
       guard_m=GUARD_M,
       max_calibration_true_residual_m=eps-GUARD_M,
       model_false_exclusions=sum(x["was_true_history_eliminated"] for x in outcomes),
       confident_decisions=sum(x["public_only_history_decision"] is not None for x in outcomes),
       wrong_confident_decisions=sum(x["wrong_confident_authorization"] for x in outcomes),
       ambiguous_both=sum(x["certificate_status"]=="AMBIGUOUS_BOTH" for x in outcomes),
       rejects_both=sum(x["certificate_status"]=="REJECTS_BOTH" for x in outcomes),
       original_nearest_target_wrong=sum(x["original_nearest_target_wrong"] is True for x in outcomes),
       training_rows=train_rows,validation_rows=outcomes)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,default=SOURCE)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    d=read_originals(args.input_dir)
    groups={task:evaluate(rows,TASKS[task]) for task,rows in d.items()}
    total=lambda k:sum(groups[g][k] for g in groups)
    result=dict(
       schema="retrospective_only_public_ack_response_model_falsification_v1",
       original_source_run="https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829529190",
       calibration_uses_already_published_data=True,
       physical_validation_PROSPECTIVE=False,
       split="per task: original first four reset seeds calibration, last four validation, BOTH fault truths remain in one split for each seed",
       task_groups=groups,
       descriptive_heldout=dict(task_truth_conditions=16,unique_reset_seeds=8,
         false_exclusions=total("model_false_exclusions"),
         wrong_confident=total("wrong_confident_decisions"),
         confident_decisions=total("confident_decisions"),
         abstentions_or_invalid=16-total("confident_decisions"),
         original_nearest_wrong=total("original_nearest_target_wrong")),
       nonclaims=[
          "A calibration maximum on four prior reset seeds is NOT independent formal physical attestation",
          "A resulting unique response label cannot be called certified under unbounded future model shifts",
          "No task-success or policy recovery results are generated by this retrospective score",
          "No outside research group ran this experiment",
          "Original experiment remains an unmodified published negative result",
       ])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("RETROSPECTIVE_RESPONSE_MODEL_DIAGNOSTIC",
          json.dumps(result["descriptive_heldout"],sort_keys=True))


if __name__=="__main__":
    main()

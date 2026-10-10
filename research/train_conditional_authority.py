"""Fit a frozen intervention-conditional SE(3) authority ranker.

Training data: 8 SOURCE reset clusters per task, both real physical zero/X modes.
Calibration: 8 disjoint source reset clusters per task. Future test: NEW seeds,
NEVER used by this fitting script. No audit-only truth consumed in inference.
No trained confidence is itself a frequentist risk certificate.
"""
from __future__ import annotations
import argparse,hashlib,json,math,random
from pathlib import Path
import torch
from torch import nn
from torch.nn.functional import cross_entropy, softmax
from research.conditional_residual_energy import (
    ConditionalResidualEnergy,public_features,authorize_from_public)

REGISTRY="research/first_source_256_public_residual_training_records.json"
SOURCE_FIELDS=("task","probe","epsilon_m","candidate_residuals_m",
               "public_before_xyz_m","public_after_xyz_m","max_rotation_spread_rad")
TASKS=("pull_cube","stack_cube")
ACTIONS=("zero","x")
SEED_OFFSET={"pull_cube":4100000,"stack_cube":4200000}
CALIBRATION_GRID=tuple(round(.50+i*.01,2) for i in range(50))
MODEL_TYPES=("full","no_action_provenance","no_causal_pair_consistency","no_group_robustness")

def frozen_rows(path:Path=Path(REGISTRY)):
    data=path.read_bytes()
    obj=json.loads(data)
    if obj["schema"]!="native_physx_source_locked_conditional_authority_development_v1":
        raise ValueError("Unregistered source")
    if obj["actual_physx_source_workflow_run"]!=38014679801 or obj["independent_source_sha_review_run"]!=38015149933:
        raise ValueError("Changed physical source")
    rows=obj["rows"]
    if len(rows)!=256:raise ValueError("Original source denominator is not 256")
    seen=set()
    for r in rows:
        key=(r["task"],r["seed"],r["ack_truth_index"],r["probe"])
        if key in seen or r["task"] not in TASKS or r["probe"] not in ACTIONS:
            raise ValueError("Invalid or repeated original PhysX cell")
        seen.add(key)
        if (r["seed"] not in range(SEED_OFFSET[r["task"]]+1,SEED_OFFSET[r["task"]]+17)
            or r["ack_truth_index"] not in range(4)
            or len(r["truth_candidate_indices_AUDIT_ONLY"])!=1
            or r["truth_candidate_indices_AUDIT_ONLY"][0] not in range(4)):
            raise ValueError("Invalid source target audit")
    return hashlib.sha256(data).hexdigest(),rows

def feat(r,provenance=True):
    return public_features(task=r["task"],
        probe=r["probe"] if provenance else "zero",
        epsilon_m=r["epsilon_m"],
        residuals_m=r["candidate_residuals_m"],
        public_before_xyz_m=r["public_before_xyz_m"],
        public_after_xyz_m=r["public_after_xyz_m"],
        rotation_spread_rad=r["max_rotation_spread_rad"])

def split(rows):
    train=[r for r in rows if 1<=r["seed"]-SEED_OFFSET[r["task"]]<=8]
    calib=[r for r in rows if 9<=r["seed"]-SEED_OFFSET[r["task"]]<=16]
    if len(train)!=128 or len(calib)!=128:raise ValueError("Training/calibration split drift")
    train_keys={(r["task"],r["seed"]) for r in train}
    cal_keys={(r["task"],r["seed"]) for r in calib}
    if train_keys&cal_keys or len(train_keys)!=16 or len(cal_keys)!=16:
        raise ValueError("Calibration reset leaks into fitted model")
    return train,calib

def sym_kl(a,b):
    pa=softmax(a,dim=-1).clamp(min=1e-8)
    pb=softmax(b,dim=-1).clamp(min=1e-8)
    return .5*((pa*(pa.log()-pb.log())).sum(-1)
              +(pb*(pb.log()-pa.log())).sum(-1)).mean()

def fit(train,variant,steps=300):
    torch.manual_seed(190027)
    random.seed(190027)
    model=ConditionalResidualEnergy(hidden=24)
    x=torch.stack([feat(r,provenance=(variant!="no_action_provenance")) for r in train])
    true=torch.tensor([r["truth_candidate_indices_AUDIT_ONLY"][0] for r in train],dtype=torch.long)
    groups={(task,probe):torch.tensor([j for j,r in enumerate(train)
                  if (r["task"],r["probe"])==(task,probe)],dtype=torch.long)
            for task in TASKS for probe in ACTIONS}
    pair_map={}
    for j,r in enumerate(train):
        key=(r["task"],r["seed"],r["ack_truth_index"])
        pair_map.setdefault(key,{})[r["probe"]]=j
    pairs=[(v["zero"],v["x"]) for v in pair_map.values() if set(v)=={"zero","x"}]
    if len(pairs)!=64:raise ValueError("Missing paired causal intervention source")
    p0=torch.tensor([a for a,b in pairs])
    p1=torch.tensor([b for a,b in pairs])
    opt=torch.optim.AdamW(model.parameters(),lr=.005,weight_decay=.035)
    for _ in range(steps):
        opt.zero_grad()
        logits=model(x)
        losses=torch.stack([cross_entropy(logits[index],true[index]) for index in groups.values()])
        # worst-group smooth minimax objective: robust across task and action
        group_loss=(.2*torch.logsumexp(losses/.2,dim=0)
                    if variant!="no_group_robustness" else losses.mean())
        # truth labels are the SAME causally tracked ACK history under both
        # interventions; only public observation distribution changes.
        paired=(.09*sym_kl(logits[p0],logits[p1])
                if variant!="no_causal_pair_consistency" else 0.)
        loss=group_loss+paired
        if not bool(torch.isfinite(loss)):raise ValueError("Nonfinite learned loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(),1.)
        opt.step()
    model.eval()
    return model

def infer_raw(model,r,variant):
    with torch.no_grad():
        prob=softmax(model(feat(r,provenance=(variant!="no_action_provenance"))),dim=-1)
    i=int(prob.argmax());s=float(prob.max())
    return i,s

def calibrate_only_on_disjoint_seeds(model,cal,variant):
    groups={}
    for task in TASKS:
        for probe in ACTIONS:
            rs=[r for r in cal if (r["task"],r["probe"])==(task,probe)]
            if len(rs)!=32 or len({r["seed"] for r in rs})!=8:
                raise ValueError("Underspecified independent calibration clusters")
            predictions=[(*infer_raw(model,r,variant),
                          r["truth_candidate_indices_AUDIT_ONLY"][0],
                          r["original_A_authorized"],
                          r["original_A_wrong_confident"]) for r in rs]
            # A fixed, developer-declared candidate grid. We make NO 10% CP
            # claim from eight independent reset clusters. This calibrator only
            # chooses empirical zero-error selective coverage for next test.
            choices=[]
            for threshold in CALIBRATION_GRID:
                accepted=[x for x in predictions if x[1]>=threshold]
                errors=sum(i!=true for i,_,true,_,_ in accepted)
                if not errors:choices.append((len(accepted),threshold))
            if choices:
                covered,th=max(choices,key=lambda v:(v[0],v[1]))
            else:covered,th=0,1.
            groups[task+":"+probe]={
                "threshold":th,"calibration_observed_authorized":covered,
                "calibration_observed_errors":0,
                "calibration_original_A_authorized":sum(x[3] for x in predictions),
                "calibration_original_A_wrong":sum(x[4] for x in predictions),
                "calibration_raw_top1_accuracy":sum(x[0]==x[2] for x in predictions)/len(predictions),
                "independent_calibration_reset_clusters":8,
                "correlated_held_applied_truth_cells":32,
                "frequentist_risk_10pct_certified":False}
    return groups

def calibration_evaluate(model,cal,variant,thresholds):
    rows=[]
    for r in cal:
        i,p=infer_raw(model,r,variant)
        grp=thresholds[r["task"]+":"+r["probe"]]
        accepted=(grp["threshold"]<1. and p>=grp["threshold"])
        rows.append({"task":r["task"],"probe":r["probe"],"seed":r["seed"],
                     "authorized":accepted,"correct":i==r["truth_candidate_indices_AUDIT_ONLY"][0],
                     "original_A_authorized":r["original_A_authorized"],
                     "original_A_wrong":r["original_A_wrong_confident"]})
    metrics={}
    for key in thresholds:
        t,a=key.split(":")
        group=[r for r in rows if (r["task"],r["probe"])==(t,a)]
        metrics[key]={"n_cells":len(group),"learned_authorized":sum(z["authorized"] for z in group),
                      "learned_wrong":sum(z["authorized"] and not z["correct"] for z in group),
                      "original_A_authorized":sum(z["original_A_authorized"] for z in group),
                      "original_A_wrong":sum(z["original_A_wrong"] for z in group)}
    return metrics

def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",default="training_authority_output")
    p.add_argument("--steps",type=int,default=300);a=p.parse_args()
    if a.steps!=300:raise ValueError("Training iterations deliberately frozen to 300")
    source_digest,rows=frozen_rows()
    train,cal=split(rows)
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    results={}
    for variant in MODEL_TYPES:
        model=fit(train,variant,steps=a.steps)
        thresholds=calibrate_only_on_disjoint_seeds(model,cal,variant)
        metrics=calibration_evaluate(model,cal,variant,thresholds)
        path=out/(variant+".pt")
        torch.save(model.state_dict(),path)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        results[variant]={"learned_model_sha256":digest,"thresholds":thresholds,"calibration_metrics":metrics}
        print("FROZEN_DEV_OFFLINE_MODEL",json.dumps({"variant":variant,"model_sha":digest,
              "calibration_metrics":metrics},sort_keys=True),flush=True)
    meta={"schema":"conditional_energy_source_separated_training_v1",
          "source_training_file_sha256":source_digest,
          "train_independent_reset_clusters":16,
          "calibration_disjoint_independent_reset_clusters":16,
          "future_test_reset_clusters":0,
          "model_used_audit_only_truth_at_training_but_not_inference":True,
          "calibrated_10pct_wrong_authorization_guarantee":False,
          "all_models_training_steps":a.steps,
          "models":results}
    (out/"model_registry.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("FROZEN_CONDITIONAL_ENERGY_DEV_FINAL",json.dumps(meta,sort_keys=True),flush=True)
if __name__=="__main__":main()

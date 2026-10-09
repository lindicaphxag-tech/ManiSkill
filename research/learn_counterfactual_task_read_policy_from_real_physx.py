"""A REAL supervised task-cost predictor from physically stepped, paired ACK-truths.

One TRAINING example = one task/reset seed, with all four physically stepped
(held/held, applied/held, held/applied, applied/applied) outcomes.
The supervised target is the four-world average public-vs-task-baseline
official task success difference MINUS charged true target-read cost.
Features are available at env.reset BEFORE any ACK truth is imposed.

This prototype learns a WHOLE-EPISODE method route before reset.
It NEVER splices a policy rollout after seeing its counterfactual outcome.
All nine original physics worlds are retained; the chosen outcome in
offline cross-validation is one of the actual stepped trajectories.
An external live meta-policy is NOT yet evaluated in newly stepped physics.

The 32-cluster CV experiment and thresholds are DEVELOPMENT analysis after
the first real original outcomes were observed, NOT new prospective evidence.
"""
from __future__ import annotations
import argparse,json,math,subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SOURCE=Path(__file__).resolve().parent/"frozen_policy_transfer/evidence/numeric_same_reset_2x2_first1152_2110001_2120016/RECHECKED_ORIGINAL1152_PORTABLE_STRICT_JSON.json"
SOURCE_GIT_BLOB="e91aff77516409863261437a6ffdf475a52686e5"
LAMBDA_PRIVILEGED_READ=0.02
RIDGE_REGULARIZATION=20.0
CONDITIONS=("held/held","applied/held","held/applied","applied/applied")

def frozen_source():
    repo=Path(__file__).resolve().parents[1]
    expected=subprocess.check_output(["git","hash-object",str(SOURCE.relative_to(repo))],
                                     cwd=repo,text=True).strip()
    if expected!=SOURCE_GIT_BLOB:
        raise ValueError("The first physical-source strict JSON mirror changed")
    d=json.loads(SOURCE.read_text(encoding="utf-8"))
    if (d["registered_source_reset_clusters"]!=32 or
        d["registered_task_seed_truth_cells"]!=128 or
        d["separate_physx_worlds"]!=1152 or
        d["paired_public_vs_strong"]!=dict(both=105,neither=9,public_only=11,strong_only=3)):
        raise ValueError("Original source-first physical cohort identities changed")
    return d

def public_reset_features(task,obs,ee):
    """NO label, true hidden target, future ACK, step5 observation or task outcome."""
    if task not in ("pull_cube","stack_cube") or len(obs)!=35 or len(ee)!=7:
        raise ValueError("Original public reset observation contract invalid")
    selected=[float(obs[i]) for i in (0,1,2,3,5,7)]
    v=[float(task=="stack_cube"),*map(float,ee[:3]),*selected]
    if len(v)!=10 or not all(math.isfinite(x) for x in v):
        raise ValueError("Nonfinite or hidden initial-state source features")
    return tuple(v)

@dataclass(frozen=True)
class Cluster:
    task:str
    seed:int
    public_initial_features:tuple[float,...]
    truth_rows:tuple[dict,...]
    delta_utility:float

def groups(d,*,read_cost=LAMBDA_PRIVILEGED_READ):
    if not (0<=read_cost<=1):
        raise ValueError("Read cost must be a frozen, disclosed scalar")
    rows=d["all_source_rows_retained"]
    if len(rows)!=128:raise ValueError("Missing physics or source registers")
    by={}
    for row in rows:
        key=(row["task"],row["seed"])
        by.setdefault(key,{})
        truth=row["truth"]
        if truth in by[key] or truth not in CONDITIONS:
            raise ValueError("Wrong duplicated physical ACK truth")
        by[key][truth]=row
    if len(by)!=32:
        raise ValueError("Not 32 genuinely distinct task/reset clusters")
    out=[]
    for (task,seed),truths in sorted(by.items()):
        if set(truths)!=set(CONDITIONS):
            raise ValueError("Counterfactual source missing one of FOUR physical truths")
        rr=tuple(truths[c] for c in CONDITIONS)
        ref=rr[0]
        features=public_reset_features(task,ref["initial_source_public_observation_f32"],
                                           ref["initial_source_ee_pose7_xyz_xyzw"])
        for r in rr:
            f=public_reset_features(task,r["initial_source_public_observation_f32"],
                                         r["initial_source_ee_pose7_xyz_xyzw"])
            if max(abs(a-b) for a,b in zip(f,features))>5e-5:
                raise ValueError("Four physics worlds do not have matched pre-fault input")
            if not all(type(r[k]) is bool for k in ("new_success","strong_success")):
                raise ValueError("Official native task labels must be true bool")
            if not all(type(r[k]) is int and r[k] in (0,1) for k in ("new_reads","strong_reads")):
                raise ValueError("Privileged private getter cost must be counted")
        dy=sum((int(r["new_success"])-int(r["strong_success"])
               -read_cost*(r["new_reads"]-r["strong_reads"])) for r in rr)/4.
        out.append(Cluster(task,seed,features,rr,dy))
    if len({(c.task,c.seed) for c in out})!=32:
        raise ValueError("Original seed aliases")
    return tuple(out)

def _solve_positive_definite(a:Sequence[Sequence[float]],b:Sequence[float]):
    """Partial-pivot exact deterministic Gaussian elimination; no learned libraries."""
    n=len(b)
    mat=[[float(v) for v in a[i]]+[float(b[i])] for i in range(n)]
    for i in range(n):
        t=max(range(i,n),key=lambda j:abs(mat[j][i]))
        mat[i],mat[t]=mat[t],mat[i]
        pivot=mat[i][i]
        if pivot<1e-10:raise ValueError("Ridge fit is singular/non positive definite")
        for j in range(i+1,n):
            alpha=mat[j][i]/pivot
            for k in range(i,n+1):
                mat[j][k]-=alpha*mat[i][k]
    out=[0.]*n
    for i in reversed(range(n)):
        out[i]=(mat[i][n]-sum(mat[i][j]*out[j] for j in range(i+1,n)))/mat[i][i]
    return tuple(out)

@dataclass(frozen=True)
class FrozenResetRoute:
    mean:tuple[float,...]
    scale:tuple[float,...]
    weights:tuple[float,...]
    training_clusters:tuple[str,...]
    read_price:float
    ridge_lambda:float

    def score(self,task,obs,ee)->float:
        raw=public_reset_features(task,obs,ee)
        z=(1.,)*(1)+tuple((v-m)/scale for v,m,scale in zip(raw,self.mean,self.scale))
        return sum(w*x for w,x in zip(self.weights,z))

    def route(self,task,obs,ee)->str:
        """WHOLE controller branch decided at RESET, not t5 after seeing counterfactual."""
        return "PUBLIC" if self.score(task,obs,ee)>0 else "STRONG_TASK"

def learn(clusters:Sequence[Cluster],*,read_price=LAMBDA_PRIVILEGED_READ,
          ridge_lambda=RIDGE_REGULARIZATION):
    clusters=tuple(clusters)
    if not clusters or len({(c.task,c.seed) for c in clusters})!=len(clusters):
        raise ValueError("Training source duplicated/empty")
    if ridge_lambda<=0 or not math.isfinite(ridge_lambda) or not 0<=read_price<=1:
        raise ValueError("Invalid fixed regularization or cost")
    n=len(clusters);dim=len(clusters[0].public_initial_features)
    means=tuple(sum(c.public_initial_features[i] for c in clusters)/n for i in range(dim))
    scales=tuple(max(.001,math.sqrt(sum((c.public_initial_features[i]-means[i])**2 for c in clusters)/n))
                 for i in range(dim))
    xs=[(1.,)+tuple((v-m)/s for v,m,s in zip(c.public_initial_features,means,scales)) for c in clusters]
    y=[c.delta_utility for c in clusters]
    mat=[[sum(x[i]*x[j] for x in xs)+(0. if i==j==0 else ridge_lambda if i==j else 0.)
         for j in range(dim+1)] for i in range(dim+1)]
    rhs=[sum(x[i]*yy for x,yy in zip(xs,y)) for i in range(dim+1)]
    weights=_solve_positive_definite(mat,rhs)
    return FrozenResetRoute(means,scales,weights,
        tuple(sorted(f"{c.task}:{c.seed}" for c in clusters)),read_price,ridge_lambda)

def outcome_for_route(c:Cluster,route:str):
    if route not in ("PUBLIC","STRONG_TASK"):
        raise ValueError("Policy route not supported")
    succ=sum(int(r["new_success" if route=="PUBLIC" else "strong_success"]) for r in c.truth_rows)
    reads=sum(r["new_reads" if route=="PUBLIC" else "strong_reads"] for r in c.truth_rows)
    # Public XYZ events counted only when choosing PUBLIC; do not invent missing
    # sensor privileges for the strong task comparator.
    public_events=sum(r["public_sample_events"] if route=="PUBLIC" else 0 for r in c.truth_rows)
    return dict(success=succ,reads=reads,public_xyz_events_if_chosen=public_events)

def leave_one_RESET_cluster_out(d):
    clusters=groups(d)
    selected=[]
    for held in clusters:
        others=tuple(c for c in clusters if (c.task,c.seed)!=(held.task,held.seed))
        if len(others)!=len(clusters)-1:raise ValueError("Fold leakage")
        model=learn(others)
        # This choice only consults original pre-fault PUBLIC reset state.
        original=held.truth_rows[0]
        chosen=model.route(held.task,original["initial_source_public_observation_f32"],
                            original["initial_source_ee_pose7_xyz_xyzw"])
        selected.append({"task":held.task,"seed":held.seed,"route":chosen,
          "chosen_real_original_physx_worlds":outcome_for_route(held,chosen),
          "same_cluster_strong_baseline_real_worlds":outcome_for_route(held,"STRONG_TASK"),
          "same_cluster_all_public_real_worlds":outcome_for_route(held,"PUBLIC")})
    def summarize(k):
        return {"official_success":sum(r[k]["success"] for r in selected),
                "private_reads":sum(r[k]["reads"] for r in selected),
                "public_xyz_events_if_chosen":sum(r[k]["public_xyz_events_if_chosen"] for r in selected)}
    full=learn(clusters)
    return {
      "status":"RETROSPECTIVE_32_SEED_CLUSTER_CROSS_FIT__NOT_NEW_PROSPECTIVE_PHYSX",
      "original_first_source_sha256_manifest":SOURCE_GIT_BLOB,
      "all_32_seed_clusters_each_4_actual_physx_truths":True,
      "all_128_original_native_task_cells_kept":True,
      "future_model_training_and_test_not_yet_EXECUTED":True,
      "full_fitted_model_for_subsequent_DISJOINT_future_trial":{
        "mean":full.mean,"scale":full.scale,"weights":full.weights,
        "training_clusters":full.training_clusters,"read_price":full.read_price,
        "ridge_lambda":full.ridge_lambda},
      "leave_one_cluster_out_development":{
        "heldout_choices":selected,
        "chosen":summarize("chosen_real_original_physx_worlds"),
        "strong":summarize("same_cluster_strong_baseline_real_worlds"),
        "always_public":summarize("same_cluster_all_public_real_worlds"),
        "choice_counts":dict(public=sum(r["route"]=="PUBLIC" for r in selected),
                             strong=sum(r["route"]=="STRONG_TASK" for r in selected))},
      "limitations":[
        "This is 32-cluster EXPLORATORY cross validation on earlier outcome-accessed data, not a prospective replication",
        "Meta route is chosen from PUBLIC initial observation BEFORE physical ACK, so each chosen whole trajectory was genuinely stepped, no t5 splice",
        "The learned evaluator has not been executed as a new tenth live controller world",
        "No calibration of incorrect hidden target history; do not claim risk assurance from success reward",
        "Task knowledge and initial object geometry may not generalize to unseen task/robot or novel controller",
        "Offline marginal query price 0.02 is a choice, not measured hardware latency; actual public sampling priced separately",
        "Original fully crossed truths share the same reset cluster; only 32 statistically independent training clusters"]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=frozen_source()
    result=leave_one_RESET_cluster_out(d)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("LEARNED_WHOLE_EPISODE_QUERY_META_POLICY_DEVELOPMENT_ONLY",
          json.dumps({k:result["leave_one_cluster_out_development"][k]
          for k in ("chosen","strong","always_public","choice_counts")},sort_keys=True))

if __name__=="__main__":
    main()

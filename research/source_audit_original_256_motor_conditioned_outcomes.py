"""Original 256-cell source-only motor-parity outcome stratification.

Purpose: distinguish complete strategy success from conditional on actually
dispatched t3 motor equality. This is descriptive, NOT a randomized
query-only effect; parity strata are observed after arms diverge. All 64
seed clusters and 256 physical truth cells are retained and auditable.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,random
from pathlib import Path

def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(path:Path):
    checks=path.parent/"SHA256SUMS"
    line=[x for x in checks.read_text().splitlines() if x.endswith("  "+path.name)]
    if len(line)!=1 or line[0].split("  ")[0]!=sha(path):
        raise ValueError(f"Not the authentic SHA256-archived original: {path}")

def signswap_cluster_p(values):
    # Under an explicitly counterfactual cluster exchangeability assumption
    # ONLY. This is exploratory evidence; not randomized treatment proof.
    if any(type(v) is not int for v in values): raise ValueError("Invalid original discrete success contrast")
    n=len(values)
    if n<1:raise ValueError("No original seeds")
    dist=collections.Counter({0:1})
    for v in values:
        nextdist=collections.Counter()
        for s,w in dist.items():
            nextdist[s+v]+=w;nextdist[s-v]+=w
        dist=nextdist
    if sum(dist.values())!=2**n:raise ValueError("Nonuniform cluster sign swap")
    original=abs(sum(values))
    return sum(w for s,w in dist.items() if abs(s)>=original)/2**n

def bootstrap(values,n_cases_per_cluster,*,draws=20000,seed=20261009):
    if not values or n_cases_per_cluster<=0:raise ValueError("Invalid paired cluster contrast")
    rng=random.Random(seed)
    n=len(values)
    out=sorted(sum(values[rng.randrange(n)] for i in range(n))/(n*n_cases_per_cluster)
               for j in range(draws))
    return [out[int(.025*draws)],out[int(.975*draws)-1]]

def analyze(primary:Path,motor:Path):
    verify(primary);verify(motor)
    d=json.loads(primary.read_text())
    m=json.loads(motor.read_text())
    if (d.get("registered_source_reset_clusters")!=64 or d.get("registered_task_seed_truth_cells")!=256
        or d.get("separate_physx_worlds")!=2304
        or m.get("actual_source_truth_cells")!=256):
        raise ValueError("Original source universe not 64×4 cells, 2304 native worlds")
    r0=d.get("all_source_rows_retained")
    r1=m.get("original_per_condition")
    if not isinstance(r0,list) or not isinstance(r1,list) or len(r0)!=256 or len(r1)!=256:
        raise ValueError("Lost or duplicate original per-episode scientific evidence")
    lookup={}
    for r in r0:
        key=(r["task"],r["seed"],r["truth_index"])
        if key in lookup:raise ValueError("Duplicated original physical cell")
        lookup[key]=r
    if len({(k[0],k[1]) for k in lookup})!=64:raise ValueError("Lost original source seed clusters")
    summary={"same_native_motor_t2_t3":[], "different_native_motor_t3":[]}
    sourceclusters=collections.defaultdict(list)
    matched=collections.Counter()
    raw=[]
    for r in r1:
        key=(r["task"],r["seed"],r["actual_execution_truth_condition"])
        if key not in lookup:raise ValueError("Motor data and original PPO outcome cell keys don't match")
        z=lookup[key]
        if any(bool(r["method_successes"][u])!=bool(z[v])
               for u,v in (("public","new_success"),("strong","strong_success"),("fixed","fixed_success"))):
            raise ValueError("Original first-source tasks differ from motor-conformant auditor")
        if r["public_and_strong_t2_native_identical"] is not True:
            raise ValueError("The predecision first ACK physical motor already differs")
        if r["public_and_strong_t3_native_identical"] not in (True,False):
            raise ValueError("Lacks actual measured second ACK native motor comparison")
        if not r["all_three_probe_steps_reached"] or r["public_before_after_achieved_xyz_samples_paid"]!=2:
            raise ValueError("Missing paid public response event in original source")
        item={
            "task":r["task"],"seed":r["seed"],"truth":r["actual_execution_truth_condition"],
            "matched_native_action_both_predecision_steps":bool(r["public_and_strong_t3_native_identical"]),
            "public_official_success":z["new_success"],"strong_official_success":z["strong_success"],
            "fixed_official_success":z["fixed_success"],"public_target_reads":z["new_reads"],
            "strong_target_reads":z["strong_reads"],
            "public_confident_wrong":z["wrong_confident"],
            "public_sensor_samples_paid":z["public_sample_events"],
        }
        bucket="same_native_motor_t2_t3" if item["matched_native_action_both_predecision_steps"] else "different_native_motor_t3"
        summary[bucket].append(item)
        raw.append(item)
        sourceclusters[(item["task"],item["seed"])].append(item)
        matched[bucket]+=1
    if len(sourceclusters)!=64 or any(len(rows)!=4 for rows in sourceclusters.values()):
        raise ValueError("Original within-seed four physical truth conditions absent")
    def aggregate(group):
        out={"n_original_task_truth_conditions":len(group),
            "public_task_success":sum(int(x["public_official_success"]) for x in group),
            "strong_task_success":sum(int(x["strong_official_success"]) for x in group),
            "fixed_task_success":sum(int(x["fixed_official_success"]) for x in group),
            "public_private_reads":sum(x["public_target_reads"] for x in group),
            "strong_private_reads":sum(x["strong_target_reads"] for x in group),
            "public_sensor_samples_paid":sum(x["public_sensor_samples_paid"] for x in group),
            "original_public_confident_wrong":sum(int(x["public_confident_wrong"]) for x in group)}
        p=collections.Counter()
        for x in group:
            a=x["public_official_success"];b=x["strong_official_success"]
            p["both" if a and b else "public_only" if a else "strong_only" if b else "neither"]+=1
        out["paired_success_categories"]=dict(p)
        return out
    primary_total=aggregate(raw)
    if any((primary_total[k]!=expected) for k,expected in {
        "n_original_task_truth_conditions":256,"public_task_success":221,
        "strong_task_success":202,"fixed_task_success":210,
        "public_private_reads":195,"strong_private_reads":221,
        "public_sensor_samples_paid":512,"original_public_confident_wrong":0}.items()):
        raise ValueError("Original source whole-population scientific endpoint drift")
    if len(summary["same_native_motor_t2_t3"])!=192 or len(summary["different_native_motor_t3"])!=64:
        raise ValueError("Original actual t3 native motor disagreement cohorts not correct")
    matched_values=[]
    for key,rows in sorted(sourceclusters.items()):
        matched_values.append(sum(
            int(x["public_official_success"])-int(x["strong_official_success"])
            for x in rows if x["matched_native_action_both_predecision_steps"]))
    # The differing number of matched physical truth cells per task makes
    # CI over per-cluster TOTAL differences more honest than pretending 192 iid.
    rng=random.Random(20261009)
    boots=sorted(sum(matched_values[rng.randrange(64)] for i in range(64))
                 for j in range(20000))
    per={task+"/"+str(truth):aggregate([x for x in raw if x["task"]==task and x["truth"]==truth])
         for task in ("pull_cube","stack_cube") for truth in range(4)}
    result={
        "evidence_type":"SOURCE_LOCKED_256_ACTUAL_MOTOR_PREDECISION_CONFOUND_DESCRIPTIVE",
        "original_full256_sha256":sha(primary),"source_native_motor256_sha256":sha(motor),
        "genuine_original_independent_seed_clusters":64,
        "original_all_256_physically_executed_truth_conditions":256,
        "original_native_physx_worlds":2304,
        "all_original_256_descriptive_end_to_end":primary_total,
        "observed_predecision_native_motor_equal_192_CONDITIONAL_NOT_CAUSAL":aggregate(summary["same_native_motor_t2_t3"]),
        "observed_predecision_native_motor_different_64_CONDITIONAL_NOT_CAUSAL":aggregate(summary["different_native_motor_t3"]),
        "by_task_actual_physical_ack_truth":per,
        "matched_motor_subgroup_selected_after_physics":True,
        "all_64_cluster_exact_signswap_exploratory_not_randomized_effect_p":
            signswap_cluster_p(matched_values),
        "matched_motor_cluster_sum_success_delta_95pct_bootstrap_NOT_EFFECT_CI":
            [boots[int(.025*len(boots))],boots[int(.975*len(boots))-1]],
        "native_action_parity_does_not_prove_identical_hidden_controller_state":True,
        "native_action_parity_does_not_prove_same_postquery_compiler":True,
        "same_total_public_sensor_action_latency_budget_not_shown":True,
        "equal_motor_selection_observed_after_execution_not_randomized":True,
        "ALL_RAW_256_ORIGINAL_SOURCE_OUTCOMES_RETAINED":raw,
        "not_independent_external_investigator_reproduction":True,
        "not_general_VLA_or_hardware_safety_evidence":True,
        "publication_limit":"Positive END-TO-END method outcome descriptive; query-only causal advantage UNIDENTIFIED",
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--motor",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    out=analyze(a.original,a.motor)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_256_NATIVE_MOTOR_QUERY_CONFOUND_ANALYSIS",json.dumps({
        k:v for k,v in out.items() if k in (
            "original_all_256_descriptive_end_to_end",
            "observed_predecision_native_motor_equal_192_CONDITIONAL_NOT_CAUSAL",
            "observed_predecision_native_motor_different_64_CONDITIONAL_NOT_CAUSAL",
            "all_64_cluster_exact_signswap_exploratory_not_randomized_effect_p",
            "matched_motor_cluster_sum_success_delta_95pct_bootstrap_NOT_EFFECT_CI"
        )},sort_keys=True))

if __name__=="__main__":main()

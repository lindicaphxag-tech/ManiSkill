"""Full original source audit for truly new-seed empirical-response PhysX.

Scoring and verification do not import torch or the simulator.
"""
import argparse
import json
import math
from pathlib import Path
from research.empirical_probe_response_classifier import classify_empirical_public_response

TASKS={"pull_cube":("PullCube-v1",160101,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
       "stack_cube":("StackCube-v1",170101,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
FAULTS=("applied_no_ack","neutral_arm_delta_no_ack")
ARMS=("source_pause_no_fault","blind_probe_optimistic","blind_probe_pessimistic",
      "achieved_probe_classifier","privileged_once_after_probe")
PROTO="research/EMPIRICAL_RESPONSE_NEW32_FROZEN_BEFORE_RUN_V1.json"
COMMIT="31adfccc285acd2b43fcb8047cc31fbccaa64b25"

def validate_data(d,task,fault,start):
    env,first,sha=TASKS[task]
    seeds=list(range(first+start,first+start+4))
    if (d.get("schema")!="empirical_response_ack_new32_precommitted_physx_v1"
        or d.get("preoutcome_frozen_commit")!=COMMIT
        or d.get("protocol")!=PROTO or d.get("task")!=env
        or d.get("truth")!=fault or d.get("seeds")!=seeds
        or d.get("third_party_checkpoint_sha256")!=sha
        or d.get("published_revision")!="6bdeb28810330ab5425ccd629bb561c58a56ff85"
        or d.get("real_physx") is not True or d.get("training_performed") is not False):
        raise ValueError("Changed prospective source, task, checkpoint or controller provenance")
    rows=d.get("rows")
    if not isinstance(rows,list) or len(rows)!=4 or [r.get("seed") for r in rows]!=seeds:
        raise ValueError("All four original source episodes must be preserved, in order")
    totals={a:0 for a in ARMS}
    coverage=wrong=exposures=abstain=empirical_model_falsified=true_history_excluded=0
    for r in rows:
        if (r.get("task")!=env or r.get("unknown_ack_truth")!=fault
            or r.get("fault_step")!=2 or r.get("probe_step")!=3):
            raise ValueError("Physical fault/probe condition differs from frozen source")
        flags=r.get("success_once",{})
        if set(flags)!=set(ARMS) or any(type(flags[a]) is not bool for a in ARMS):
            raise ValueError("Official simulator per-arm success flags missing")
        for a in ARMS:
            totals[a]+=int(flags[a])
        init=r.get("initial_obs_diff",{})
        if any(a not in init or not math.isfinite(float(init[a])) or init[a]>5e-4
               for a in ARMS[1:]):
            raise ValueError("Not the same paired task reset state")
        gate=r.get("fault_reached",{})
        probe=r.get("probe_reached",{})
        reads=r.get("private_memory_reads_during_action_decision",{})
        if set(reads)!=set(ARMS) or any(type(reads[a]) is not int for a in ARMS):
            raise ValueError("Missing per-arm hidden memory access ledger")
        for a in ARMS:
            if reads[a] != (1 if a=="privileged_once_after_probe" and probe.get(a) else 0):
                raise ValueError("Illegal target-state getter or fake one-read disclosure")
        for a in ARMS[1:]:
            if type(gate.get(a)) is not bool or type(probe.get(a)) is not bool:
                raise ValueError("Unknown fault/probe exposure; do not cherry-pick")
        if all(gate[a] for a in ARMS[1:]):
            exposures+=1
        cls=r.get("classifier")
        got_probe=probe["achieved_probe_classifier"]
        if got_probe:
            if not isinstance(cls,dict):
                raise ValueError("Missing blind classification and geometry audit")
            if cls.get("evidence_type")!="achieved_EE_xyz_after_one_native_zero_arm_delta":
                raise ValueError("Private target-telemetry disguised as public proprioception")
            if any(not isinstance(cls.get(k),(int,float)) or not math.isfinite(cls[k]) or cls[k]<0
                   for k in ("hold_distance_m","applied_distance_m","target_separation_m","decision_margin_m")):
                raise ValueError("Missing numerical evidence for unknown-ACK inference")
            if cls.get("label") not in ("held","applied",None):
                raise ValueError("Unknown/non-fail-closed label")
            probe=r["probe_positions"].get("achieved_probe_classifier")
            candidates=r.get("candidate_goal_positions",{})
            if not probe or any(k not in candidates for k in ("held","applied")):
                raise ValueError("Missing public probe or both pre-fault history candidates")
            calculated=classify_empirical_public_response(
                probe["achieved_pre_probe_xyz"],probe["achieved_post_probe_xyz"],
                candidates["held"],candidates["applied"],task=task)
            def _cross_python_equal(left,right):
                # Numerical distances from the unchanged Python/NumPy PhysX
                # source may differ by a few ulps across CPython/libm builds.
                # Never relax exact labels, state compatibility or provenance.
                if type(left) is bool or type(right) is bool:
                    return type(left) is type(right) and left==right
                if type(left) in (int,float) and type(right) in (int,float):
                    return math.isfinite(left) and math.isfinite(right) and math.isclose(
                        float(left),float(right),rel_tol=0,abs_tol=2e-11)
                if isinstance(left,dict) and isinstance(right,dict):
                    return left.keys()==right.keys() and all(
                        _cross_python_equal(left[k],right[k]) for k in left)
                if isinstance(left,(list,tuple)) and isinstance(right,(list,tuple)):
                    return len(left)==len(right) and all(
                        _cross_python_equal(a,b) for a,b in zip(left,right))
                return type(left) is type(right) and left==right
            if not _cross_python_equal(cls,calculated):
                raise ValueError("Submitted public-only history label or response evidence differs from frozen source calculator")
            truth_name="held" if fault=="neutral_arm_delta_no_ack" else "applied"
            if not cls[f"{truth_name}_compatible"]:
                true_history_excluded+=1
            if cls["label"] is None:
                abstain+=1
            if cls["status"]=="REFUSE_EMPIRICAL_MODEL_FALSIFIED":
                empirical_model_falsified+=1

            if cls["label"] is not None:
                coverage+=1
                iswrong=cls["label"]!=("held" if fault=="neutral_arm_delta_no_ack" else "applied")
                if r.get("wrong_authorization") is not iswrong:
                    raise ValueError("Wrong-authorization label mismatch")
                wrong+=int(iswrong)
            elif r.get("wrong_authorization") is not None:
                raise ValueError("Abstention must NOT be relabeled as correct or wrong")
            cand=r.get("candidate_goal_positions",{})
            if not all(len(cand.get(k,[]))==3 for k in ("held","applied")):
                raise ValueError("Missing both possible commanded target hypotheses")
            if not all(a in r.get("probe_positions",{}) for a in ARMS if probe.get(a)):
                raise ValueError("Missing matched raw physical probe trajectories")
        elif cls is not None:
            raise ValueError("Reported decision without physical probe")
        if any(p.get("exactness")!="NOT_EXACT"
               for entries in r.get("projections",{}).values() for p in entries):
            raise ValueError("Projected bounded actions silently declared exact")
    if totals!=d.get("success_count") or coverage!=d.get("classification_covered") or wrong!=d.get("false_history_authorizations"):
        raise ValueError("Submitted summary does not match original full per-seed rows")
    return dict(success=totals,classifier_covered=coverage,
                classifier_wrong_authorizations=wrong,
                classifier_abstentions=abstain,
                empirical_model_falsified=empirical_model_falsified,
                true_history_incompatible_with_train_error_envelope=true_history_excluded,
                paired_fault_exposed=exposures,paired_n=4)


def aggregate(folder):
    expected={f"empirical_response_{t}_{f}_{s}_fresh4.json"
              for t in TASKS for f in FAULTS for s in (0,4)}
    paths=list(folder.glob("empirical_response_*_fresh4.json"))
    if {p.name for p in paths}!=expected or len(paths)!=8:
        raise ValueError("All eight original task×truth×chunk PhysX source files required")
    data={}
    for t in TASKS:
        for f in FAULTS:
            for s in (0,4):
                key=f"{t}:{f}:{s}"
                p=folder/f"empirical_response_{t}_{f}_{s}_fresh4.json"
                data[key]=validate_data(json.loads(p.read_text()),t,f,s)
    return dict(schema="empirical_response_ack_fresh32_native_physx_audit_v1",
                trial_conditions=32,independent_policy_checkpoints=2,
                contributor_executed_not_outside_replication=True,
                no_hardware_or_network_fault=True,
                results=data)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=aggregate(a.input_dir)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("EMPIRICAL_RESPONSE_NEW32_FULL_AUDIT",json.dumps({
        k:dict(s=v["success"],covered=v["classifier_covered"],
               wrong=v["classifier_wrong_authorizations"],
               fault_exposed=v["paired_fault_exposed"])
        for k,v in d["results"].items()},sort_keys=True))

if __name__=="__main__":
    main()

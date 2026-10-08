"""Read-only replay of original 20-pair experiment arithmetic.

Equivalent to frozen score_pair/contract_signature at 8207ac01, using
NumPy and original ranks. No sample selection or threshold changes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from research.crg_core.clustered_evidence_audit import audit_clustered_scores, spearman

SEEDS = (17,29,43,59,71,89,101,131,151,181)
SHA = "8207ac01c56e75ccee19cba0e75eb0978cde37b2"
PROTOCOL = "reset-fresh-space-block-position-4ulp-v2"
DIGEST = "ae4590eb2a152bfa2367bbe1e8bc204e05721c4481b7422597054c1a160edcd0"
ROOT = Path(__file__).resolve().parent


def signature(j):
    u,s,_ = np.linalg.svd(j,full_matrices=False)
    rank = 0 if s.size==0 or s[0]==0 else int(np.sum(s>1e-8*s[0]))
    projector = u[:,:rank]@u[:,:rank].T if rank else np.zeros((j.shape[0],j.shape[0]))
    spectrum = np.zeros_like(s) if s.size==0 or s[0]==0 else s/s[0]
    gain = float(np.linalg.norm(j,ord="fro"))
    normalized = np.zeros_like(j) if gain==0 else j/gain
    return normalized,projector,spectrum,gain,rank


def signature_distance(a,b):
    A,Pa,Sa,Ga,Ra=signature(a)
    B,Pb,Sb,Gb,Rb=signature(b)
    if Ra!=Rb:
        return float("inf")
    gain = 0.0 if Ga==Gb==0 else float("inf") if Ga<=0 or Gb<=0 else abs(float(np.log(Ga/Gb)))
    k=min(len(Sa),len(Sb))
    return float(np.linalg.norm(A-B,ord="fro")+np.linalg.norm(Pa-Pb,ord="fro")+np.linalg.norm(Sa[:k]-Sb[:k])+gain)


def score_pair(pair):
    a,b=pair["a"],pair["b"]
    def physical(x):
        return np.asarray(x["action_to_physical_jacobian"],float) @ np.asarray(x["raw_action_jacobian"],float) @ np.asarray(x["physical_support_to_support_chart_jacobian"],float)
    ja,jb=(np.asarray(x["raw_action_jacobian"],float) for x in (a,b))
    na,nb=np.linalg.norm(ja),np.linalg.norm(jb)
    raw=(0.0 if na==nb==0 else float("inf")) if (na==0 or nb==0) else float(np.linalg.norm(ja/na-jb/nb))
    pa,pb=(np.asarray(x["heldout_physical_response"],float) for x in (a,b))
    denom=max(float(np.linalg.norm(pa)),float(np.linalg.norm(pb)),1e-12)
    ia,ib=set(a["support_ids"]),set(b["support_ids"])
    union=ia|ib
    return {
        "heldout_id":pair["heldout_id"],
        "dec_distance":signature_distance(physical(a),physical(b)),
        "raw_distance":raw,
        "support_distance":1-len(ia&ib)/len(union) if union else 0.0,
        "static_metadata_distance":float(a["static_representation"]!=b["static_representation"]),
        "coarse_class_distance":float(a["coarse_contract_class"]!=b["coarse_contract_class"]),
        "heldout_response_distance":float(np.linalg.norm(pa-pb)/denom),
    }


def replay(root=ROOT):
    manifest=json.loads((root/"manifest.json").read_text())
    archived=json.loads((root/"primary_result.json").read_text())
    if (manifest["source_head_sha"]!=SHA or manifest["gate_digest"]!=DIGEST or
        archived["n_pairs"]!=20 or archived["n_unstable_states"]!=10 or
        archived["primary_gate"]["gate_digest"]!=DIGEST or
        archived["primary_gate"]["passed"] or archived["state_restore_protocol"]!=PROTOCOL):
        raise ValueError("frozen aggregate provenance/status mismatch")
    groups=[]
    for seed in SEEDS:
        state=json.loads((root/f"state-{seed}.json").read_text())
        if (state["reset_seed"]!=seed or state["state_restore_protocol"]!=PROTOCOL or
            state["lerobot_commit"]!="3c0a209f9fac4d2a57617e686a7f2a2309144ba2" or
            state["probe_epsilon"]!=0.125 or
            state["physical_probe"]!=[2.0,2.0,0.01] or
            state["randomness_seeds"]!=[123,456,789] or
            state["heldouts"]!={"A":[4.0,-2.0,0.02],"B":[-5.0,3.0,-0.025]}):
            raise ValueError(f"frozen state metadata changed: {seed}")
        if [p["heldout_id"] for p in state["pairs"]] != ["A","B"]:
            raise ValueError("heldout ordering changed")
        for kind,checkpoint in [("diffusion","d3d143b0342488252497853815b27ce3c0384c6b"),("vqbet","390e5e4c079c880b22e873dad53ecfac706bc78a")]:
            policy=state["policies"][kind]
            if policy["revision"]!=checkpoint or policy["replicate_count"]!=3 or policy["query_count"]!=27:
                raise ValueError(f"frozen policy mismatch: {seed}/{kind}")
        groups.append({"state_id":seed,"pairs":[score_pair(p) for p in state["pairs"]]})
    y=np.array([p["heldout_response_distance"] for g in groups for p in g["pairs"]])
    fields=[("dec_distance","dec_spearman"),("raw_distance","raw_spearman"),("support_distance","support_spearman"),("static_metadata_distance","static_metadata_spearman"),("coarse_class_distance","coarse_class_spearman")]
    measured={}
    for key,field in fields:
        x=np.array([p[key] for g in groups for p in g["pairs"]])
        got=spearman(x,y)
        target=archived["primary_gate"][field]
        if not np.isclose(got,target,atol=1e-10,rtol=0):
            raise AssertionError(f"{field}: recomputed {got}, frozen {target}")
        measured[field]=got
    audit=audit_clustered_scores(groups,random_seed=20261008)
    return {
        "schema":"crg-20case-v2-replay-report-v1",
        "source_workflow_run_id":37706099258,
        "source_sha":SHA,
        "frozen_gate_digest":DIGEST,
        "archived_result_replayed_exactly":True,
        "original_primary_passed":False,
        "original_v1_bank_completed":False,
        "post_run_amended_protocol":PROTOCOL,
        "n_independent_state_clusters":10,
        "n_dependent_heldout_observations":20,
        "policy_queries":540,
        "frozen_correlations":measured,
        "exploratory_cluster_sensitivity":audit,
        "independently_reproduced_by_external_lab":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    payload=json.dumps(replay(),indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload)
    print(payload)


if __name__=="__main__":
    main()

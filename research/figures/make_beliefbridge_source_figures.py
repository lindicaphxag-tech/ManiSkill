"""Vector figures from SHA-audited ORIGINAL native robot PhysX JSON.

No simulation, fitting, hidden seed exclusion or author-entered performance
numbers. Every figure regenerates from 64+64 actual controller-source rows.
Run from repository root:
  python -m research.figures.make_beliefbridge_source_figures
       --dual-root /path/to/checkouted/evidence/dual065-negative-native64-20261009
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PRIMARY=Path("research/frozen_policy_transfer/evidence/shared_compiler_postquery_causal_original64_1480001_1490032")
DERIVED=Path("research/frozen_policy_transfer/derived/shared_compiler_causal64_strict_json.json")
DUAL_REL=Path("research/frozen_policy_transfer/evidence/dual065_observer_negative_original64_1820001_1830032")

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def lock_to_archived_original(folder,filename):
    manifest=(folder/"ORIGINAL_SHA256SUMS").read_text().splitlines()
    target=[entry for entry in manifest if entry.endswith("  "+filename)]
    if len(target)!=1 or target[0].split("  ")[0]!=sha256(folder/filename):
        raise ValueError("Source original physical evidence checksum failed: "+filename)

def load(dual_root):
    lock_to_archived_original(PRIMARY,"original_independent_full64_audit.json")
    a=json.loads(DERIVED.read_text(),parse_constant=lambda s: (_ for _ in ()).throw(ValueError("non-standard JSON")))
    original_text=(PRIMARY/"original_independent_full64_audit.json").read_text()
    repaired=json.loads(original_text,parse_constant=lambda x: {"nonfinite_numeric":"positive_infinity"} if x=="Infinity" else (_ for _ in ()).throw(ValueError(x)))
    if a!=repaired: raise ValueError("Semantic tree of primary strict JSON changed")
    if len(a["all_episodes"])!=64 or a["actually_stepped_simulator_worlds"]!=576:
        raise ValueError("Primary frozen original sample size changed")
    folder=dual_root/DUAL_REL
    lock_to_archived_original(folder,"original_all64_independent_audit.json")
    b=json.loads((folder/"original_all64_independent_audit.json").read_text(),parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    if b["n_original_task_reset_states"]!=64 or b["real_native_PhysX_controller_worlds"]!=640:
        raise ValueError("Secondary source is not original 64x10 native PhysX")
    if len(b["all_original_rows"])!=64:raise ValueError("Secondary original sample rows dropped")
    return a,b,{"primary_original_sha256":sha256(PRIMARY/"original_independent_full64_audit.json"),
                "dual_original_sha256":sha256(folder/"original_all64_independent_audit.json")}

def config():
    plt.rcParams.update({
        "font.family":"DejaVu Sans",
        "font.size":8.5,
        "axes.titlesize":10,
        "axes.labelsize":9,
        "xtick.labelsize":8,
        "ytick.labelsize":8,
        "axes.spines.top":False,
        "axes.spines.right":False,
        "svg.fonttype":"none",      # real editable vector text
        "savefig.facecolor":"white",
        "figure.facecolor":"white",
        "axes.linewidth":0.7,
    })

def header(ax,title,subtitle):
    ax.set_title(title,loc="left",fontweight="bold",pad=18)
    ax.text(0.0,1.045,subtitle,transform=ax.transAxes,fontsize=7.1,
            va="bottom",color="#586577")

def fig_primary(a,out):
    outcomes=a["outcomes"]
    assert outcomes["public"]=={"private_reads":48,"task_success":53}
    assert outcomes["fixed_t5"]=={"private_reads":64,"task_success":53}
    labels=["Public history; read if ambiguous","Same compiler; mandatory private read"]
    reads=[outcomes["public"]["private_reads"],outcomes["fixed_t5"]["private_reads"]]
    completed=[outcomes["public"]["task_success"],outcomes["fixed_t5"]["task_success"]]
    fig,ax=plt.subplots(figsize=(6.75,2.63),layout="constrained")
    y=np.array([1,0]);bars=ax.barh(y,reads,height=.38,color=["#355d85","#a9b0b8"])
    for i,v in enumerate(reads):
        ax.text(v+1,y[i],str(v)+" reads",va="center",fontsize=8.6,color="#1e293b",fontweight="bold")
        ax.text(78,y[i],str(completed[i])+"/64 tasks",va="center",ha="right",fontsize=8.4,color="#374151")
    ax.set_yticks(y,labels)
    ax.set_xlim(0,82);ax.set_xticks([0,16,32,48,64])
    ax.set_xlabel("Actually counted privileged controller-target readbacks (lower is better)")
    ax.grid(axis="x",alpha=.16,zorder=-1)
    header(ax,"A. Identical physical prefix AND post-query compiler",
           "64 original new reset states · 576 genuine ManiSkill PhysX controller worlds")
    fig.savefig(out/"figure2a_matched_compiler_read_budget.svg",format="svg")
    plt.close(fig)

def fig_fourtruth(a,out):
    source=a["four_truth_strata"]
    labels=["Applied/Applied","Applied/Held","Held/Applied","Held/Held"]
    shorten={"applied/applied":"Applied/Applied","applied/held":"Applied/Held","held/applied":"Held/Applied","held/held":"Held/Held"}
    fig,ax=plt.subplots(figsize=(6.75,2.68),layout="constrained")
    x=np.arange(4);width=.33
    for task,delta,c in [("pull_cube",-width/2,"#355d85"),("stack_cube",width/2,"#d48c49")]:
        vals=[]
        for tail in ["applied/applied","applied/held","held/applied","held/held"]:
            k=task+"/"+tail
            if source[k]["n"]!=8:raise ValueError("Physical truth case missing")
            vals.append(source[k]["public_confident"])
        ax.bar(x+delta,vals,width,color=c,label="PullCube" if task=="pull_cube" else "StackCube",zorder=3)
        for i,v in enumerate(vals):
            ax.text(x[i]+delta,v+.12,str(v)+"/8",ha="center",fontsize=7.7,color="#263445")
    ax.set_xticks(x,labels)
    ax.set_ylim(0,8);ax.set_yticks([0,2,4,6,8])
    ax.set_ylabel("Publicly admitted complete histories")
    ax.legend(loc="upper right",frameon=False,ncol=2,fontsize=8)
    ax.grid(axis="y",alpha=.16,zorder=-1)
    header(ax,"B. Physical ACK-truth strata are not uniformly identifiable",
           "Exactly eight genuine reset states per fault pattern and task; no observed wrong admissions in this cohort")
    fig.savefig(out/"figure2b_true_execution_strata.svg",format="svg")
    plt.close(fig)

def fig_negative(b,out):
    A="fault_public_t3_fourhistory_or_t4_query"
    B="fault_dual_evidence_065_or_query"
    C="fault_always_single_privileged_query"
    data=b["total"]
    assert data[A]["official_success"]==data[B]["official_success"]==54
    assert (data[A]["private_reads"],data[B]["private_reads"],data[C]["private_reads"])==(41,45,62)
    fig,ax=plt.subplots(figsize=(6.75,2.68),layout="constrained")
    xs=[data[A]["private_reads"],data[B]["private_reads"],data[C]["private_reads"]]
    ys=[data[A]["official_success"],data[B]["official_success"],data[C]["official_success"]]
    colors=["#355d85","#d48c49","#a9b0b8"]
    for xx,yy,col in zip(xs,ys,colors):
        ax.scatter([xx],[yy],s=82,c=[col],edgecolors="white",linewidths=.65,zorder=5)
    ax.annotate("Same-XYZ set-membership\n54/64; 21 admissions; 0 wrong observed",
                (xs[0],ys[0]),xytext=(13,56.0),fontsize=7.6,
                arrowprops={"arrowstyle":"-","color":"#7c8b99"},color="#20364b")
    ax.annotate("Extra 0.65 score gate\n54/64; 17 admissions; 0 wrong observed",
                (xs[1],ys[1]),xytext=(47,52.15),fontsize=7.6,
                arrowprops={"arrowstyle":"-","color":"#ad7b48"},color="#794519")
    ax.annotate("Mandatory read\n55/64",
                (xs[2],ys[2]),xytext=(63,55.7),fontsize=8.0,
                arrowprops={"arrowstyle":"-","color":"#8390a0"},color="#405060")
    ax.annotate("",xy=(45,54),xytext=(41,54),arrowprops={"arrowstyle":"->","color":"#9b6230","lw":1.5})
    ax.set_xlim(7,77);ax.set_ylim(50.5,57.4)
    ax.set_xticks([16,32,41,45,62,72]);ax.set_yticks([51,52,53,54,55,56,57])
    ax.set_xlabel("Counted private controller-target reads")
    ax.set_ylabel("Official task successes / 64")
    ax.grid(alpha=.15,zorder=-1)
    header(ax,"C. The deterministic second score adds cost, not observed utility",
           "Separate original 640-world cohort: 62 fully matched public-probe episodes; 2 censoring cases retained")
    fig.savefig(out/"figure3_same_residual_gate_negative.svg",format="svg")
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dual-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,default=Path("research/figures/generated"))
    args=p.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    a,b,ident=load(args.dual_root)
    config()
    fig_primary(a,args.output_dir)
    fig_fourtruth(a,args.output_dir)
    fig_negative(b,args.output_dir)
    files=sorted(args.output_dir.glob("figure*.svg"))
    if len(files)!=3:raise RuntimeError("Three original-source vectors required")
    manifest={"schema":"source_verified_embodied_ack_manuscript_figures_v1","raw_sources":ident,
              "graphics":{f.name:sha256(f) for f in files},
              "source_cohorts_separate_not_pooled":True,
              "source_method_author_run_not_independent_external":True,
              "vla_fault_recovery_shown":False}
    (args.output_dir/"ORIGINAL_DATA_FIGURE_SHA256.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("NATIVE_PHYSX_SOURCE_VECTOR_FIGURES_VERIFIED",json.dumps(manifest,sort_keys=True))

if __name__=="__main__":main()

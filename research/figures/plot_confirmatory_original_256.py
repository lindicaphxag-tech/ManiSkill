"""Paper-grade vector plots FROM original source-authenticated 256-cell native PhysX.

No invented task successes, manual values, test-set fitting, or per-cell IID
significance. Original source archive and original immutable manifest REQUIRED.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path("research/frozen_policy_transfer/evidence/confirmatory_original64clusters_256cells_2304worlds")
PRIMARY=ROOT/"original_full256_source_audit.json"
NAMES={"public":"Public complete-history witness","strong_task":"Task-aware native comparator",
       "fixed_t5":"Mandatory trusted target read","always_held":"Never read; always assume held"}
COL={"public":"#174D72","strong_task":"#C47A45","fixed_t5":"#8797A6","always_held":"#B6BECA"}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def original():
    sig=ROOT/"ORIGINAL_SHA256SUMS"
    expected=[line.split("  ")[0] for line in sig.read_text().splitlines()
              if line.endswith("  "+PRIMARY.name)]
    if len(expected)!=1 or expected[0]!=sha(PRIMARY):
        raise ValueError("Original 256-cell auditor archive SHA mismatch")
    d=json.loads(PRIMARY.read_text())
    if (d["registered_source_reset_clusters"]!=64
        or d["registered_task_seed_truth_cells"]!=256 or d["separate_physx_worlds"]!=2304
        or d["numerically_matched_public_source_observation_per_truth_verified"] is not True):
        raise ValueError("Missing original fully matched physical source cohort")
    s=d["primary_outcomes"]
    assert {k:(v["official_task_success"],v["decision_private_reads"]) for k,v in s.items()} == {
      "public":(221,195),"strong_task":(202,221),"fixed_t5":(210,256),"always_held":(133,0)}
    assert d["paired_public_vs_strong"]=={"both":197,"neither":30,"public_only":24,"strong_only":5}
    assert d["public_wrong_confident_count"]==0
    if sum(row["source_seed_clusters"] for row in d["per_task_per_truth"].values())!=256:
        raise ValueError("Per-task and original actual ACK truth source groups are incomplete")
    return d

def init_style():
    plt.rcParams.update({
      "font.family":"DejaVu Sans","font.size":8.4,
      "axes.labelsize":8.5,"axes.titlesize":10,
      "figure.facecolor":"white","axes.facecolor":"white",
      "axes.spines.top":False,"axes.spines.right":False,
      "xtick.labelsize":8,"ytick.labelsize":8,
      "svg.fonttype":"none",
      "axes.linewidth":.7,
    })

def panel_title(ax,title,sub):
    ax.set_title(title,loc="left",pad=23,fontweight="bold")
    ax.text(0,1.045,sub,transform=ax.transAxes,fontsize=7.2,
        color="#586577",ha="left",va="bottom")

def plot_paired(d,out):
    fig,axes=plt.subplots(1,2,figsize=(9.4,3.0),
                          gridspec_kw={"width_ratios":[1.12,1]},layout="constrained")
    order=["public","strong_task","fixed_t5","always_held"]
    y=np.arange(4)[::-1]
    success=[d["primary_outcomes"][k]["official_task_success"] for k in order]
    reads=[d["primary_outcomes"][k]["decision_private_reads"] for k in order]
    for ax,vals,maximum,title in [(axes[0],success,256,"A. Official physical task success"),
                                  (axes[1],reads,256,"B. Controller-private target reads")]:
        ax.barh(y,vals,color=[COL[k] for k in order],height=.55,zorder=3)
        for v,yy in zip(vals,y):
            ax.text(min(v+3,maximum+17),yy,f"{v}/256",va="center",fontsize=8.7,
                    fontweight="bold",color="#253748")
        ax.set_xlim(0,maximum+44)
        ax.set_xticks([0,64,128,192,256])
        ax.grid(axis="x",alpha=.18,zorder=0)
        ax.set_yticks(y,[NAMES[k] for k in order] if ax is axes[0] else [""]*4)
        ax.set_xlabel("Number of true task/fault cells" if ax is axes[0] else
                      "Actually counted native privileged target reads")
        panel_title(ax,title,"64 original source-reset clusters × 4 physically executed ACK truths")
    fig.savefig(out/"fig1_confirmatory256_success_and_privileged_reads.svg",format="svg")
    plt.close(fig)

def plot_strata(d,out):
    order=[("pull_cube","applied/applied"),("pull_cube","applied/held"),
           ("pull_cube","held/applied"),("pull_cube","held/held"),
           ("stack_cube","applied/applied"),("stack_cube","applied/held"),
           ("stack_cube","held/applied"),("stack_cube","held/held")]
    strata=d["per_task_per_truth"];vals=[]
    for task,truth in order:
        row=strata[task+"/"+truth]
        if row["source_seed_clusters"]!=32:raise ValueError("Task/fault counterfactual denominator changed")
        vals.append(row)
    fig,ax=plt.subplots(figsize=(9.4,3.35),layout="constrained")
    x=np.arange(8);w=.36
    a=np.array([v["public_success"] for v in vals])
    b=np.array([v["strong_success"] for v in vals])
    ax.bar(x-w/2,a,w,color=COL["public"],label="BeliefBridge public-or-read",zorder=3)
    ax.bar(x+w/2,b,w,color=COL["strong_task"],label="Task-aware comparator",zorder=3)
    for dx,series in [(-w/2,a),(w/2,b)]:
        for i,v in enumerate(series):
            ax.text(i+dx,v+.35,str(v),ha="center",va="bottom",fontsize=7.2)
    ax.set_ylim(0,37);ax.set_yticks([0,8,16,24,32])
    ax.set_xticks(x,["AA","AH","HA","HH"]*2)
    ax.axvline(3.5,color="#A2AAB6",lw=.9,ls="--")
    ax.text(1.5,-.15,"PullCube",ha="center",va="top",transform=ax.get_xaxis_transform(),fontweight="bold")
    ax.text(5.5,-.15,"StackCube",ha="center",va="top",transform=ax.get_xaxis_transform(),fontweight="bold")
    ax.set_ylabel("Official task completions / 32 original seeds")
    ax.legend(frameon=False,loc="upper right",fontsize=8.2,ncol=2)
    ax.grid(axis="y",alpha=.17,zorder=0)
    panel_title(ax,"C. Full executed/held × executed/held physical factorial",
         "Both tasks preserve all AA, AH, HA, HH; 32 source resets per task-truth stratum")
    fig.savefig(out/"fig2_confirmatory256_task_ack_truth_stratification.svg",format="svg")
    plt.close(fig)

def plot_decision(d,out):
    v=d["paired_public_vs_strong"]
    fig,ax=plt.subplots(figsize=(6.3,2.7),layout="constrained")
    labels=["Both complete","Only public complete","Only strong complete","Neither completes"]
    vals=[v["both"],v["public_only"],v["strong_only"],v["neither"]]
    colors=["#8797A6","#174D72","#C47A45","#B6BECA"]
    y=np.arange(4)[::-1]
    ax.barh(y,vals,height=.56,color=colors,zorder=3)
    for yy,n in zip(y,vals):
        ax.text(n+1.8,yy,str(n),va="center",fontweight="bold")
    ax.set_xlim(0,233);ax.set_xticks([0,50,100,150,200])
    ax.set_yticks(y,labels);ax.grid(axis="x",alpha=.15,zorder=0)
    ax.set_xlabel("Paired original task × ACK cells (total = 256)")
    panel_title(ax,"D. Every paired success and failure was preserved",
         "64 source clusters; do NOT calculate independent-cell p-values on 256 correlated cells")
    fig.savefig(out/"fig3_confirmatory256_paired_outcome_evidence.svg",format="svg")
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=Path("research/figures/generated_confirmatory256"))
    x=p.parse_args()
    d=original()
    x.output_dir.mkdir(parents=True,exist_ok=True)
    init_style()
    plot_paired(d,x.output_dir)
    plot_strata(d,x.output_dir)
    plot_decision(d,x.output_dir)
    paths=sorted(x.output_dir.glob("fig*.svg"))
    if len(paths)!=3:raise ValueError("Missing three actual-source vector figures")
    meta={
      "evidence":"Genuine original physically executed 64-cluster/256-cell/2304-worlds",
      "original_source_SHA256":sha(PRIMARY),
      "original_source_run":"37934425888",
      "independent_correct_full_audit":"37936177368",
      "descriptive_cluster_bootstrap95":d["seed_cluster_bootstrap_95pct_public_minus_strong_success_gap"],
      "exact_cluster_swap_p_exploratory":d["seed_cluster_exact_swap_two_sided_sensitivity_p_not_randomized_proof"],
      "no_independent_outside_replication":True,
      "not_full_public_actuation_equal_information_budget":True,
      "svg_files":{q.name:sha(q) for q in paths},
    }
    (x.output_dir/"ORIGINAL_SOURCE_FIGURE_HASHES.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("CONFIRMATORY_256_ORIGINAL_SOURCE_VECTOR_FIGURES",json.dumps(meta,sort_keys=True))

if __name__=="__main__":main()

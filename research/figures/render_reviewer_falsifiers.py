"""Generate true source-only editable SVG methodological falsifiers for top-track robotics.

This code explicitly treats quaternion ranking as an observational pilot and
treats seven mismatched original StackCube initial-state hashes as invalidating
strict same-reset counterfactual causal interpretation. Do not present either
as an improved robot task method.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SO3_REL=Path("research/frozen_policy_transfer/evidence/physical_public_so3_original16_2040001_2050008")
FAC_REL=Path("research/frozen_policy_transfer/evidence/original_1152_factorial_failed_identity_audit")
ARM="fault_public_t3_fourhistory_or_t4_query"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def load(root,relative,report):
    base=root/relative
    original=base/report
    sums=(base/"ORIGINAL_SHA256SUMS").read_text().splitlines()
    expected=[line for line in sums if line.endswith("  "+report)]
    if len(expected)!=1 or expected[0].split("  ")[0]!=sha(original):
        raise RuntimeError("Missing or modified original-source SHA proof: "+str(original))
    return json.loads(original.read_text()),sha(original)

def setup():
    plt.rcParams.update({
        "font.family":"DejaVu Sans","font.size":8.7,"axes.titlesize":10.3,
        "axes.labelsize":8.6,"axes.spines.top":False,"axes.spines.right":False,
        "axes.linewidth":.8,"svg.fonttype":"none","figure.facecolor":"white",
        "savefig.facecolor":"white"
    })

def so3_fig(data,out):
    if len(data["all_original_16_intent_to_treat_rows"])!=16: raise RuntimeError("SO3 original denominator")
    counts={"both_correct":0,"xyz_only":0,"so3_only":0,"both_wrong":0}
    for row in data["all_original_16_intent_to_treat_rows"]:
        r=row["public_orientation_channel"][ARM]
        a=bool(r["xyz_argmin_matches_audited_true"])
        b=bool(r["so3_argmin_matches_audited_true"])
        k="both_correct" if a and b else "xyz_only" if a else "so3_only" if b else "both_wrong"
        counts[k]+=1
    if counts!={"both_correct":7,"xyz_only":6,"so3_only":0,"both_wrong":3}:
        raise RuntimeError("Cannot fabricate pilot orientation/position ranking contingency")
    fig,ax=plt.subplots(figsize=(6.8,3.0),layout="constrained")
    cells=np.array([[counts["both_correct"],counts["xyz_only"]],
                    [counts["so3_only"],counts["both_wrong"]]],dtype=float)
    from matplotlib.colors import ListedColormap
    ax.imshow(cells,cmap=ListedColormap(["#f2f4f5","#c9d9e8","#6992b6"]),vmin=0,vmax=8,aspect="auto")
    for i in range(2):
        for j in range(2):
            ax.text(j,i,str(int(cells[i,j]))+" / 16",va="center",ha="center",
                    color="#163049",fontsize=13,weight="bold")
    ax.set_xticks([0,1],["XYZ argmin correct","XYZ argmin wrong"])
    ax.set_yticks([0,1],["SO(3) argmin correct","SO(3) argmin wrong"])
    ax.set_title("D. Genuine measured SO(3) is NOT an automatic history oracle",
                 loc="left",weight="bold",pad=15)
    ax.text(0,1.03,"16 new frozen-PPO resets / 160 actual native worlds · audit-only true histories",
             transform=ax.transAxes,color="#526273",fontsize=7.5)
    ax.text(0,-.24,"SO(3): 7/16 correct; XYZ: 13/16. Pure diagnostic rankings, NOT online VLA/PPO recovery.",
            transform=ax.transAxes,color="#6b4d33",fontsize=7.4)
    fig.savefig(out/"figure4_actual_public_SO3_negative.svg",format="svg")
    plt.close(fig)
    return counts

def factorial_fig(data,out):
    if len(data["source_initial_MISMATCHES"])!=7 or len(data["source_initial_exact_matches"])!=25:
        raise RuntimeError("Original physical initial-state-match failure results changed")
    def n(group,task):return sum(1 for x in group if x["task"]==task)
    labels=["PullCube","StackCube"]
    matching=[n(data["source_initial_exact_matches"],t) for t in ("pull_cube","stack_cube")]
    mismatching=[n(data["source_initial_MISMATCHES"],t) for t in ("pull_cube","stack_cube")]
    if matching!=[16,9] or mismatching!=[0,7]:
        raise RuntimeError("Original mismatched StackCube source identity unexpectedly repaired")
    fig,ax=plt.subplots(figsize=(6.8,2.8),layout="constrained")
    x=np.arange(2)
    ax.barh(x,matching,color="#355d85",height=.46,label="All four source SHA identical")
    ax.barh(x,mismatching,left=matching,color="#d48c49",height=.46,label="Initial source SHA differs")
    for i in range(2):
        ax.text(matching[i]/2,x[i],str(matching[i])+"/16",ha="center",va="center",
                color="white",fontsize=9,weight="bold")
        if mismatching[i]:ax.text(matching[i]+mismatching[i]/2,x[i],
                                  str(mismatching[i])+"/16",ha="center",va="center",
                                  color="#3d250d",fontsize=9,weight="bold")
    ax.set_yticks(x,labels)
    ax.set_xlim(0,18);ax.set_xticks([0,4,8,12,16]);ax.invert_yaxis()
    ax.set_xlabel("Nominal within-seed 4-truth clusters (16 original reset IDs per task)")
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.29),ncol=2,frameon=False,fontsize=7.8)
    ax.set_title("E. Source hash falsifies full 32-seed counterfactual pairing",
                 loc="left",weight="bold",pad=15)
    ax.text(0,1.03,"128 actual task/truth cells, 1,152 real native PhysX worlds. Final strict pairing audit FAILED.",
            transform=ax.transAxes,color="#526273",fontsize=7.35)
    fig.savefig(out/"figure5_initial_source_identity_failure.svg",format="svg")
    plt.close(fig)
    return {"matching_by_task":matching,"mismatching_by_task":mismatching}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--so3-root",required=True,type=Path)
    p.add_argument("--factorial-root",required=True,type=Path)
    p.add_argument("--output",default="research/figures/generated",type=Path)
    args=p.parse_args()
    so3,so3hash=load(args.so3_root,SO3_REL,"source_only_all16_so3_discriminability.json")
    fac,fachash=load(args.factorial_root,FAC_REL,"complete_forensic_all128.json")
    args.output.mkdir(parents=True,exist_ok=True);setup()
    c=so3_fig(so3,args.output)
    f=factorial_fig(fac,args.output)
    figure_names=("figure4_actual_public_SO3_negative.svg","figure5_initial_source_identity_failure.svg")
    manifest={"original_source_sha256":{"real_so3_160_worlds":so3hash,"real_factorial_1152_worlds":fachash},
              "true_so3_pilot_diagnostic_counts":c,"real_factorial_failed_identity_counts":f,
              "vector_images_sha256":{n:sha(args.output/n) for n in figure_names},
              "never_infer_POSE_safety_or_new_model_performance_from_these_source_only_figures":True}
    (args.output/"SOURCE_AUTHENTICATED_NEGATIVE_FIGURES_SHA256.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("SOURCE_VERIFIED_ACTUAL_PHYSX_FALSIFICATION_VECTOR_ARTWORK",json.dumps(manifest,sort_keys=True))

if __name__=="__main__":main()

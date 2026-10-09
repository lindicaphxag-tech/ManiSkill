"""Vector RSS scientific plots: genuine source audited 256 robot condition truths.

Pure presentation: original motor+outcome SHA checked by research
source_audit_original_256_motor_conditioned_outcomes.py. Not a new result.
Visually name t3 motor mismatch to PREVENT accidental causal interpretation.
"""
from __future__ import annotations
import argparse, json, math, hashlib
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def setup():
    plt.rcParams.update({
        "font.family":"DejaVu Sans","font.size":8.8,
        "axes.titlesize":10,"axes.labelsize":8.7,
        "xtick.labelsize":8.2,"ytick.labelsize":8.2,
        "axes.spines.top":False,"axes.spines.right":False,
        "svg.fonttype":"none","savefig.facecolor":"white",
        "figure.facecolor":"white","axes.linewidth":0.7,
    })

def group(dic):
    p=dic["paired_success_categories"]
    return [p.get("both",0),p.get("public_only",0),p.get("strong_only",0),p.get("neither",0)]

def source(inp):
    obj=json.loads(inp.read_text())
    if obj["original_all_256_descriptive_end_to_end"]["n_original_task_truth_conditions"]!=256:
        raise ValueError("Not 256 physical source-backed task condition audits")
    all_=obj["all_original_256_descriptive_end_to_end"]
    same=obj["observed_predecision_native_motor_equal_192_CONDITIONAL_NOT_CAUSAL"]
    different=obj["observed_predecision_native_motor_different_64_CONDITIONAL_NOT_CAUSAL"]
    if ([all_["public_task_success"],all_["strong_task_success"],all_["public_private_reads"],all_["strong_private_reads"],all_["public_sensor_samples_paid"]] !=[221,202,195,221,512] or
        [same["n_original_task_truth_conditions"],same["public_task_success"],same["strong_task_success"],same["public_private_reads"],same["strong_private_reads"]]!=[192,172,162,143,157] or
        [different["n_original_task_truth_conditions"],different["public_task_success"],different["strong_task_success"]]!=[64,49,40]):
        raise ValueError("Unexpected mutated authenticated PhysX original")
    if len(obj["ALL_RAW_256_ORIGINAL_SOURCE_OUTCOMES_RETAINED"])!=256:
        raise ValueError("Original missing trial not visualizable")
    if not obj["matched_motor_subgroup_selected_after_physics"]:
        raise ValueError("Figure MUST label postexecution subgroup selection")
    return all_,same,different,obj

def fig_paired(all_,same,diff,out):
    cats=["Both succeed","Public only","Strong only","Neither"]
    cs=["#527fa6","#2b7564","#cc8451","#afb8c3"]
    dat=[group(x) for x in (all_,same,diff)]
    if any(sum(row)!=n for row,n in zip(dat,[256,192,64])):
        raise ValueError("Original physically executed denominator was dropped")
    fig,ax=plt.subplots(figsize=(7.0,3.0),layout="constrained")
    labels=["All 256 original conditions","t3 native motors equal (192)","t3 native motors DIFFER (64)"]
    ys=[2,1,0]
    for y,vals in zip(ys,dat):
        start=0
        for value,col in zip(vals,cs):
            ax.barh(y,value,left=start,color=col,height=.48,zorder=2)
            if value>=12:
                ax.text(start+value/2,y,str(value),ha="center",va="center",
                        fontsize=8,fontweight="medium",color="#ffffff" if col not in ("#afb8c3",) else "#202832")
            start+=value
    ax.set_yticks(ys,labels)
    ax.set_xlim(0,266)
    ax.set_xticks([0,64,128,192,256])
    ax.set_xlabel("Genuinely executed original task/fault conditions; paired official success")
    ax.set_title("Actual native motor parity separates two explanatory mechanisms",loc="left",weight="bold",pad=13)
    ax.grid(axis="x",alpha=.12,zorder=1)
    ax.legend(handles=[Patch(color=c,label=label) for c,label in zip(cs,cats)],
              loc="upper center",bbox_to_anchor=(.5,-.29),ncol=4,frameon=False,fontsize=7.5)
    ax.text(0,-.78,"Observed parity AFTER execution; neither subgroup is randomized. 64 source seeds, 4 fault truths each.",
            ha="left",va="bottom",fontsize=7.1,color="#687788")
    fig.savefig(out/"rss_fig2_actual_motor_confounded_paired_outcomes.svg",format="svg")
    plt.close(fig)

def fig_cost(all_,same,out):
    # c_publicXYZ/c_privateGetter. Actuation/delay omitted, explicitly visible.
    from numpy import linspace
    import numpy as np
    x=linspace(0,.12,400)
    total=all_["public_sensor_samples_paid"]*x-(
       all_["strong_private_reads"]-all_["public_private_reads"])
    sub=same["public_sensor_samples_paid"]*x-(
        same["strong_private_reads"]-same["public_private_reads"])
    fig,ax=plt.subplots(figsize=(6.7,3.0),layout="constrained")
    ax.axhline(0,color="#5f6e80",linewidth=.75,zorder=0)
    ax.plot(x,total,color="#527fa6",lw=2.2,label="All original 256 conditions")
    ax.plot(x,sub,color="#cc8451",lw=2.0,ls="--",label="t3 native motors equal (192)")
    z1=(all_["strong_private_reads"]-all_["public_private_reads"])/all_["public_sensor_samples_paid"]
    z2=(same["strong_private_reads"]-same["public_private_reads"])/same["public_sensor_samples_paid"]
    for z,c,label,dy in [(z1,"#527fa6","0.0508",10),(z2,"#cc8451","0.0365",-13)]:
        ax.axvline(z,color=c,lw=.85,alpha=.52,ls=":")
        ax.annotate(label,(z,0),xytext=(z+.009,dy),fontsize=8,
                    color=c,arrowprops={"arrowstyle":"-","color":c,"lw":.7})
    ax.set_xlim(0,.12)
    ax.set_xticks([0,.02,.04,.06,.08,.10,.12])
    ax.set_ylabel("Extra cost of public-history route\n(relative to task-aware baseline)")
    ax.set_xlabel("Assumed cost: one XYZ sampling event / one private target read")
    ax.grid(alpha=.12)
    ax.set_title("Read savings are NOT total-information savings",loc="left",weight="bold",pad=12)
    ax.legend(loc="upper left",frameon=False,fontsize=8)
    ax.text(.0,-.32,"Includes 512 real public XYZ sample events; excludes probe movement, delay and bandwidth.",
            transform=ax.transAxes,fontsize=7.15,color="#687788",va="top")
    fig.savefig(out/"rss_fig3_private_vs_public_sensing_cost_break_even.svg",format="svg")
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    all_,same,diff,_=source(a.input)
    setup()
    fig_paired(all_,same,diff,a.output)
    fig_cost(all_,same,a.output)
    files=sorted(a.output.glob("rss_fig*.svg"))
    if len(files)!=2:raise ValueError("Expected two real-PhysX vector figures")
    manifest={
        "real_original_256_source_derived_hash":hashlib.sha256(a.input.read_bytes()).hexdigest(),
        "plots_sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
        "no_new_actual_physics_claimed":True,
        "actual_t3_motor_equality_post_execution_stratum":True,
        "no_total_sensor_actuator_latency_cost_equality_claimed":True,
    }
    (a.output/"SVG_SOURCE_SHA256_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("SOURCE_LOCKED_256_NATIVE_PHYSX_TWO_CAREFULLY_LABELED_SVG",json.dumps(manifest,sort_keys=True))

if __name__=="__main__":main()

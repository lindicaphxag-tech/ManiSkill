#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


VARIANTS=("main","converter_only","controller_only","composed")
CORPORA=("baseline_generated","composed_generated")


def _bootstrap_mean_ci(values, seed=20261006, n_boot=5000):
    a=np.asarray(values,dtype=np.float64)
    if a.size==0:
        return {"mean":float("nan"),"low":float("nan"),"high":float("nan")}
    rng=np.random.default_rng(seed)
    means=np.empty(n_boot,dtype=np.float64)
    for i in range(n_boot):
        idx=rng.integers(0,a.size,size=a.size)
        means[i]=a[idx].mean()
    return {
        "mean":float(a.mean()),
        "low":float(np.percentile(means,2.5)),
        "high":float(np.percentile(means,97.5)),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()

    result={
        "schema_version":1,
        "metric":"paired SO(3) converter-to-controller target error",
        "corpora":{},
        "claim_boundary":(
            "Two frozen official-demo request distributions are evaluated offline. "
            "Within each corpus every implementation receives identical delta poses "
            "and exact captured controller normalization context. Scientific "
            "hypotheses are reported, never used as workflow pass/fail criteria."
        ),
    }

    for corpus in CORPORA:
        docs={
            v:json.loads((args.root/f"{corpus}__{v}.json").read_text())
            for v in VARIANTS
        }
        hashes={docs[v]["corpus_sha256"] for v in VARIANTS}
        counts={int(docs[v]["request_count"]) for v in VARIANTS}
        if len(hashes)!=1 or len(counts)!=1:
            raise SystemExit(f"{corpus}: pairing identity mismatch")
        corpus_hash=next(iter(hashes))
        count=next(iter(counts))

        errors={
            v:np.asarray(
                [x["rotation_error_deg"] for x in docs[v]["paired_rows"]],
                dtype=np.float64,
            )
            for v in VARIANTS
        }
        if any(len(x)!=count for x in errors.values()):
            raise SystemExit(f"{corpus}: paired row count mismatch")
        if any(not np.all(np.isfinite(x)) for x in errors.values()):
            raise SystemExit(f"{corpus}: non-finite semantic error")

        main=errors["main"]
        conv=errors["converter_only"]
        ctrl=errors["controller_only"]
        both=errors["composed"]
        tol=1e-3

        paired={
            "converter_minus_main_deg":_bootstrap_mean_ci(conv-main,seed=20261006),
            "controller_minus_main_deg":_bootstrap_mean_ci(ctrl-main,seed=20261007),
            "composed_minus_main_deg":_bootstrap_mean_ci(both-main,seed=20261008),
            "composed_minus_converter_deg":_bootstrap_mean_ci(both-conv,seed=20261009),
            "composed_minus_controller_deg":_bootstrap_mean_ci(both-ctrl,seed=20261010),
            "fraction_both_singletons_worse_than_main":float(
                np.mean((conv>main+tol)&(ctrl>main+tol))
            ),
            "fraction_composed_no_worse_than_main":float(
                np.mean(both<=main+tol)
            ),
            "fraction_full_compensation_pattern":float(
                np.mean(
                    (conv>main+tol)
                    &(ctrl>main+tol)
                    &(both<=main+tol)
                )
            ),
        }
        means={v:float(errors[v].mean()) for v in VARIANTS}
        strict=bool(
            means["converter_only"]>means["main"]
            and means["controller_only"]>means["main"]
            and means["composed"]<=means["main"]+tol
        )
        result["corpora"][corpus]={
            "corpus_sha256":corpus_hash,
            "request_count":count,
            "mean_rotation_error_deg":means,
            "p95_rotation_error_deg":{
                v:float(np.percentile(errors[v],95)) for v in VARIANTS
            },
            "paired_effects":paired,
            "strict_compensating_bundle":strict,
            "variant_summaries":{
                v:{
                    "rotation_error_deg":docs[v]["rotation_error_deg"],
                    "rotation_error_deg_unclipped":docs[v]["rotation_error_deg_unclipped"],
                    "rotation_error_deg_clipped":docs[v]["rotation_error_deg_clipped"],
                    "position_error":docs[v]["position_error"],
                    "clipped_calls":docs[v]["clipped_calls"],
                }
                for v in VARIANTS
            },
        }

    result["cross_corpus"]={
        "strict_compensation_in_both":all(
            result["corpora"][c]["strict_compensating_bundle"] for c in CORPORA
        ),
        "paired_inputs_identical_within_each_corpus":True,
        "input_distributions_independent_of_compared_cell":True,
        "corpus_origins":list(CORPORA),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

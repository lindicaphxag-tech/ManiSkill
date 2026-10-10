"""Reset-cluster secondary statistics for a COMPLETED, SHA-audited frozen PPO experiment.

This module cannot revalidate original source bytes: pass it ONLY the exact output
of research.audit_active_probe_full_task_physx. It does not tune the policy.
Bootstrap percentiles and sign flips are descriptive; no randomized assignment
or population noninferiority is implied by this deterministic paired experiment.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import product
from random import Random
from pathlib import Path
import argparse
import json

A='fault_public_t3_fourhistory_or_t4_query'
B='fault_same_public_posterior_or_query'
C='fault_always_single_privileged_query'
ARMS=(A,B,C)
TASKS={'pull_cube':4100001,'stack_cube':4200001}

def signflip(deltas):
    nonzero=[float(v) for v in deltas if v]
    if len(nonzero)>20:raise ValueError('too many exact sign flips')
    if not nonzero:return 1.
    threshold=abs(sum(nonzero))-1e-10
    return sum(abs(sum(x*s for x,s in zip(nonzero,z)))>=threshold
               for z in product((-1,1),repeat=len(nonzero)))/2**len(nonzero)

def pct(values,p):
    s=sorted(values)
    if not s:raise ValueError('empty')
    x=(len(s)-1)*p
    i=int(x)
    return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(x-i)

def science(original:dict,n_boot:int=2000,seed:int=20261010)->dict:
    if (original.get('status')!='REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED'
        or original.get('physically_executed_original_controller_worlds')!=2560
        or original.get('new_independent_reset_clusters')!=32):
        raise ValueError('Not a complete independently audited native task source')
    cells=original['all_full_actual_PPO_task_outcomes']
    if len(cells)!=384:raise ValueError('missing original observed A/B/C task cells')
    grouped=defaultdict(list)
    for x in cells:
        task=x.get('task');seed0=TASKS.get(task);arm=x.get('arm')
        if (seed0 is None or arm not in ARMS or type(x.get('seed')) is not int
            or x['seed'] not in range(seed0,seed0+16)
            or type(x.get('truth')) is not int or x['truth'] not in range(4)):
            raise ValueError('Invalid original independent reset / fault truth')
        for k in ('zero_success','x_success','zero_wrong','x_wrong'):
            if type(x.get(k)) is not bool:raise ValueError('Invalid binary task/safety endpoint')
        for k in ('zero_privileged_reads','x_privileged_reads'):
            if type(x.get(k)) is not int or x[k] not in (0,1):
                raise ValueError('Invalid authority read cost')
        grouped[task,x['seed'],arm].append(x)
    valid={(task,seed,arm) for task,first in TASKS.items()
           for seed in range(first,first+16) for arm in ARMS}
    if set(grouped)!=valid:raise ValueError('missing original reset groups')
    for cells4 in grouped.values():
        if len(cells4)!=4 or {x['truth'] for x in cells4}!={0,1,2,3}:
            raise ValueError('ACK repeated-measure case missing/duplicated')
    rng=Random(seed)
    results={}
    for task,first in TASKS.items():
        results[task]={}
        for arm in ARMS:
            sample=[grouped[task,i,arm] for i in range(first,first+16)]
            delta=[sum(int(x['x_success'])-int(x['zero_success']) for x in rows)
                   for rows in sample]
            draws=[sum(delta[rng.randrange(16)] for _ in range(16))/64
                   for _ in range(n_boot)]
            flat=[x for rows in sample for x in rows]
            results[task][arm]=dict(
                original_independent_reset_clusters=16,
                repeated_ACK_truths_per_cluster=4,
                paired_real_task_cells=64,
                x_success=sum(x['x_success'] for x in flat),
                zero_success=sum(x['zero_success'] for x in flat),
                task_success_rate_x_minus_zero=sum(delta)/64,
                x_only_success=sum(x['x_success'] and not x['zero_success'] for x in flat),
                zero_only_success=sum(x['zero_success'] and not x['x_success'] for x in flat),
                authority_getter_x_minus_zero=sum(x['x_privileged_reads']-x['zero_privileged_reads'] for x in flat),
                wrong_confident_x_minus_zero=sum(x['x_wrong']-x['zero_wrong'] for x in flat),
                exploratory_two_sided_cluster_signflip_p=signflip(delta),
                descriptive_reset_cluster_bootstrap_95=[pct(draws,.025),pct(draws,.975)],
                observed_per_reset_four_truth_task_deltas=delta)
    return dict(status='POST_SOURCE_AUDIT_DESCRIPTIVE_STATISTICS_ONLY',
                task_success_noninferiority_certified=False,
                no_claim_of_independent_confirmatory_replication=True,
                n_independent_resets=32,by_task=results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original_audit');p.add_argument('output')
    a=p.parse_args()
    d=science(json.loads(Path(a.original_audit).read_text()))
    Path(a.output).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps(d['by_task'],indent=2,sort_keys=True))

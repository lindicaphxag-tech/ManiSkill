"""Retrospective 128 PhysX-cell reset-cluster error/coverage power audit.

Source-PINNED, previously owner-executed native PhysX. NOT a new experiment,
not a calibration/test split, and NOT a deployable selective safety certificate.
"""
import hashlib
import json
from pathlib import Path
from dataclasses import asdict
from research.reset_cluster_authority_calibration import Cluster,Cell,calibrate,cp_upper,cp_lower

SHA='57485114f58101a24c20d2f1155ac96482a7754693878e940a2197215cf142e8'
A='fault_public_t3_fourhistory_or_t4_query'

def audit(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('frozen old PhysX source hash changed')
    source=json.loads(raw)
    rows=source['all_orig_source_seed_cell_vectors']
    if len(rows)!=128 or source['actual_genuine_native_controller_worlds']!=1280:
        raise ValueError('original physical denominator is wrong')
    grouped={}
    for r in rows:
        key=(r['task'],r['seed'])
        x=grouped.setdefault(key,{})
        if r['truth'] in x: raise ValueError('duplicate ACK truth')
        x[r['truth']]=Cell(str(r['truth']),float(r['confidence'][A]),not r['wrong'][A])
    expected={(task,seed) for task,start in [('pull_cube',3110001),('stack_cube',3120001)]
              for seed in range(start,start+16)}
    if set(grouped)!=expected or any(set(g)!=set(range(4)) for g in grouped.values()):
        raise ValueError('incomplete independent reset/fault grid')
    clusters=tuple(Cluster(task,seed,tuple(g[k] for k in range(4)))
                   for (task,seed),g in sorted(grouped.items()))
    d=calibrate(clusters,tasks=('pull_cube','stack_cube'),grid=(.5,),
                delta=.05,conditional_cap=.1,min_coverage=.2)
    if d.certified: raise AssertionError('unexpected high-confidence pass')
    eta=.05/(2*2*1)
    evidence={}
    for task in ('pull_cube','stack_cube'):
        allrows=[x for x in clusters if x.task==task]
        auth=sum(any(c.public_score>=.5 for c in x.truths) for x in allrows)
        bad=sum(any(not c.correct_afterrun and c.public_score>=.5 for c in x.truths)
                for x in allrows)
        u=cp_upper(bad,len(allrows),eta)
        cov=cp_lower(auth,len(allrows),eta)
        evidence[task]=dict(independent_resets=len(allrows),
            any_authorized_resets=auth,any_wrong_authorized_resets=bad,
            upper_unconditional_wrong_reset=u,lower_coverage_reset=cov,
            upper_conditional_wrong_reset=min(1.,u/cov) if cov>0 else 1.)
    return {'source_sha256':SHA,'status':'RETROSPECTIVE_SOURCE_ONLY_NOT_CALIBRATED_DEPLOYMENT',
            'original_native_worlds':1280,'independent_reset_clusters':32,
            'correlated_ack_conditions':128,
            'per_task':evidence,'decision':asdict(d),
            'original_authority_claim_10pct_selective_error_certified':False}

if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2))

"""Exact IID binary public-response reliability/cost tradeoff; NOT real PhysX.

This introduces an ADDITIONAL independence assumption beyond the deterministic
<=K-corruption minimax guarantee. Never call this measured robot safety.
"""
from itertools import product
from research.adversarial_probe_budget import Model,synthesize,follow
import json

def analyze(p):
    if not 0<=p<=.5:raise ValueError('binary noise p out of range')
    m=Model({'applied':'continue','held':'reset'},
            {'applied':'a','held':'h'},('a','h'),1,5,3,1)
    proof=synthesize(m)
    out={}
    for truth in m.repairs:
        total_error=0.;total_cost=0.;mass=0.
        for seq in product(m.alphabet,repeat=3):
            flips=sum(x!=m.probe_truth[truth] for x in seq)
            weight=p**flips*(1-p)**(3-flips)
            for n in range(4):
                status=follow(m,proof,seq[:n])
                if status['decision']!='probe':break
            assert status['decision']=='authorize',status
            total_cost+=weight*n
            mass+=weight
            total_error+=weight*(status['repair']!=m.repairs[truth])
        assert abs(mass-1)<1e-10
        out[truth]={'one_probe_wrong_prob':p,
                    'repeated_probe_wrong_prob':total_error,
                    'expected_public_probes':total_cost,
                    'worst_public_probes':proof['cost']}
        assert abs(total_error-(3*p*p-2*p**3))<1e-10
        assert abs(total_cost-(2+2*p*(1-p)))<1e-10
    return out

def correlated_noise_stress(p=.1):
    """Mixture: with rho probability a systematic error flips ALL probes.
    Independent wrong-probe probability remains p in either component.
    Repeated measurements cannot resolve the rho=1 failure mode.
    """
    if not 0<=p<=.5:raise ValueError('invalid p')
    independent=3*p*p-2*p**3
    return {str(rho):{
        'all_probes_wrong_prob':(1-rho)*independent+rho*p,
        'mean_probes':(1-rho)*(2+2*p*(1-p))+rho*2}
        for rho in (0.,.5,1.)}

def main():
    cases={str(p):analyze(p) for p in (0.,.01,.05,.1,.3,.5)}
    assert abs(cases['0.1']['applied']['repeated_probe_wrong_prob']-.028)<1e-10
    correlated=correlated_noise_stress(.1)
    assert abs(correlated['0.5']['all_probes_wrong_prob']-.064)<1e-10
    assert abs(correlated['1.0']['all_probes_wrong_prob']-.1)<1e-10
    return {'status':'IID_BINARY_MODEL_MATHEMATICS_NOT_PHYSX',
            'cases':cases, 'correlated_error_stress_at_10pct':correlated,
            'at_10pct_iid_noise':{'one_probe_error':.1,'repeated_probe_error':.028,
                 'relative_error_reduction':.72,'average_probe_cost':2.18,
                 'worst_probe_cost':3},
            'scope':'Deterministic K<=1 and iid Bernoulli noise require distinct evidence. K+1 corruptions can produce incorrect authorization; not real robot safety.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))

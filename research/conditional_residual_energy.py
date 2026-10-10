"""Intervention-Conditioned Equivariant Residual Energy (ICERE) hypothesis ranker.

Input ONLY public motion, action provenance, candidate public geometric residuals,
training-time task ID and frozen response scale. Hidden target/audit truth is NEVER
accepted by the inference API. Built-in strict NaN/invalidity -> getter.
Finite candidate scoring is permutation-equivariant, unlike index-memorization.
This is a learned candidate-ranking operator, NOT a safety certificate.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence
import torch
from torch import nn

VALID_TASKS={"pull_cube":0, "stack_cube":1}
VALID_ACTIONS={"zero":0, "x":1}
FEATURES=12

def public_features(*,task:str,probe:str,epsilon_m:float,
                    residuals_m:Sequence[float],
                    public_before_xyz_m:Sequence[float],
                    public_after_xyz_m:Sequence[float],
                    rotation_spread_rad:float=0.)->torch.Tensor:
    if task not in VALID_TASKS or probe not in VALID_ACTIONS:
        raise ValueError("Unregistered task / native probe identity")
    if not math.isfinite(epsilon_m) or not 0<epsilon_m<=.1:
        raise ValueError("Invalid source-registered response noise scale")
    if len(residuals_m)!=4 or len(public_before_xyz_m)!=3 or len(public_after_xyz_m)!=3:
        raise ValueError("Four full-target hypotheses and complete public XYZ observations required")
    v=tuple(float(x) for x in (*residuals_m,*public_before_xyz_m,*public_after_xyz_m,rotation_spread_rad))
    if not all(math.isfinite(x) for x in v) or any(x<0 for x in residuals_m) or rotation_spread_rad<0:
        raise ValueError("Invalid public signal")
    rr=[x/epsilon_m for x in residuals_m]
    lo=min(rr); av=sum(rr)/4
    move=[(a-b)/epsilon_m for a,b in zip(public_after_xyz_m,public_before_xyz_m)]
    # Public xyz movement, action identity, and task provenance are shared;
    # candidate residual features are applied equivariantly across 4 hypotheses.
    result=[]
    for d in rr:
        result.append([min(d,12), min((d-lo),12), min((d-av),12),
            min(d*d,144),min((d-lo)**2,144),
            min(math.hypot(*move),12),max(-12,min(move[0],12)),
            max(-12,min(move[1],12)),max(-12,min(move[2],12)),
            min(rotation_spread_rad/.1,12),float(VALID_ACTIONS[probe]),
            float(VALID_TASKS[task])])
    return torch.tensor(result,dtype=torch.float32)

class ConditionalResidualEnergy(nn.Module):
    """DeepSets shared nonlinear encoding + context-conditioned pairwise contrast.

    Permuting candidate indices permutes logits identically; no candidate index
    feature or privileged truth can influence prediction.
    """
    def __init__(self,hidden:int=24):
        super().__init__()
        self.embed=nn.Sequential(nn.Linear(FEATURES,hidden),
                                  nn.Tanh(),nn.Linear(hidden,hidden),nn.Tanh())
        self.context=nn.Sequential(nn.Linear(hidden+2,hidden),
                                    nn.Tanh(),nn.Linear(hidden,hidden))
        self.score=nn.Sequential(nn.Linear(hidden*2,hidden),
                                  nn.Tanh(),nn.Linear(hidden,1))
        self.log_inverse_temperature=nn.Parameter(torch.tensor(0.))
    def forward(self,features:torch.Tensor)->torch.Tensor:
        if features.shape[-2:]!=(4,FEATURES):
            raise ValueError("Four full target histories required")
        h=self.embed(features)
        mean=h.mean(dim=-2,keepdim=True).expand_as(h)
        context=self.context(torch.cat((mean,features[...,10:12]),dim=-1))
        logits=self.score(torch.cat((h,context),dim=-1)).squeeze(-1)
        t=self.log_inverse_temperature.clamp(-3.,3.).exp()
        return t*(logits-logits.mean(dim=-1,keepdim=True))

@dataclass(frozen=True)
class Decision:
    kind:str
    candidate_index:int|None
    score:float
    reason:str

def authorize_from_public(model:ConditionalResidualEnergy,*,threshold:float,
                           task:str,probe:str,epsilon_m:float,
                           residuals_m:Sequence[float],
                           public_before_xyz_m:Sequence[float],
                           public_after_xyz_m:Sequence[float],
                           rotation_spread_rad:float)->Decision:
    """No audit-only target is in signature. Return QUERY on invalid signal or low confidence."""
    if not math.isfinite(threshold) or not 0<threshold<=1:
        raise ValueError("Invalid frozen conditional authorization threshold")
    try:
        feature=public_features(task=task,probe=probe,epsilon_m=epsilon_m,
            residuals_m=residuals_m,public_before_xyz_m=public_before_xyz_m,
            public_after_xyz_m=public_after_xyz_m,rotation_spread_rad=rotation_spread_rad)
        with torch.no_grad():
            scores=model(feature)
            prob=torch.softmax(scores,dim=-1)
        if not bool(torch.isfinite(prob).all()):
            raise ValueError("Invalid learned energy response")
        certainty,index=prob.max(dim=-1)
        conf=float(certainty)
        i=int(index)
        if conf<threshold:
            return Decision("QUERY",None,conf,"LOW_CONDITIONAL_CONFIDENCE")
        return Decision("AUTHORIZE",i,conf,"ACTION_PROVENANCE_AND_SCORE_MATCHED")
    except (ValueError,RuntimeError,OverflowError):
        return Decision("QUERY",None,float("nan"),"MISSING_OR_INVALID_PUBLIC_MODEL_INPUT")

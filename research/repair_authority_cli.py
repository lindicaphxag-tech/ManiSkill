"""Standard-library-only third-party contract file / decision-certificate CLI.

Deliberately separated from the ManiSkill native physics dependency tree.
Input is UNTRUSTED MODEL DATA. Passing verification certifies only the
conditional finite model, not the input's applicability to a real robot.

Example:
 python -m research.repair_authority_cli --mode synthesize --contract research/fixtures/repair_authority_partial_getter.json --output /tmp/cert.json
 python -m research.repair_authority_cli --mode verify --contract research/fixtures/repair_authority_partial_getter.json --certificate /tmp/cert.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

from research.effect_aware_authority_certificate import (
    Action, Contract, synthesize, verify_optimality, verify_policy,
)


def parse_contract(data:Any)->Contract:
    if not isinstance(data,dict) or data.get("schema")!="effect_aware_partial_getter_contract_v1":
        raise ValueError("Expected exact finite-contract JSON schema")
    keys={"schema","initial","goals","forbidden","probes","repair_effects",
          "read_support","read_atomic_and_fresh","read_cost","stop_cost","horizon"}
    if set(data)!=keys or not isinstance(data["probes"],list):
        raise ValueError("Unexpected/missing JSON contract property")
    ps=[]
    for p in data["probes"]:
        if not isinstance(p,dict) or set(p)!={"name","cost","transitions"}:
            raise ValueError("Probe must have exact name/cost/transitions")
        trans=p["transitions"]
        if not isinstance(trans,dict):
            raise ValueError("Incorrect probe transition map")
        ps.append(Action(name=p["name"],cost=p["cost"],
                         transitions={s:tuple(tuple(pair) for pair in edges)
                                      for s,edges in trans.items()}))
    effects=data["repair_effects"]
    reads=data["read_support"]
    if not isinstance(effects,dict) or not isinstance(reads,dict):
        raise ValueError("Invalid repair or getter effect mapping")
    model=Contract(
        initial=tuple(data["initial"]),goals=tuple(data["goals"]),
        forbidden=tuple(data["forbidden"]),probes=tuple(ps),
        repair_effects={action:{s:tuple(dest) for s,dest in mapping.items()}
                        for action,mapping in effects.items()},
        read_support={s:tuple(values) for s,values in reads.items()},
        read_atomic_and_fresh=data["read_atomic_and_fresh"],
        read_cost=data["read_cost"],stop_cost=data["stop_cost"],
        horizon=data["horizon"])
    from research.effect_aware_authority_certificate import validate
    validate(model)
    return model


def main():
    p=argparse.ArgumentParser(description="Conditional, finite repair effect certificate; no physical safety guarantee")
    p.add_argument("--mode",required=True,choices=("synthesize","verify"))
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--certificate",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    m=parse_contract(json.loads(a.contract.read_text(encoding="utf-8")))
    if a.mode=="synthesize":
        cert=synthesize(m)
        if a.output is None:p.error("synthesize requires --output")
        a.output.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("FINITE_MODEL_ONLY_CERTIFICATE_CREATED",cert["model_hash"],cert["minimax_cost"])
    else:
        if a.certificate is None:p.error("verify requires --certificate")
        cert=json.loads(a.certificate.read_text(encoding="utf-8"))
        sound=verify_policy(m,cert)
        optimal=verify_optimality(m,cert)
        print("PASS_CONDITIONAL_FINITE_MODEL_ONLY",
              json.dumps({"soundness":sound,"optimality":optimal},sort_keys=True))


if __name__=="__main__":
    main()

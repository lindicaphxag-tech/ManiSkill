"""Finite-model synthetic stale-authority benchmark, NOT real-robot task metrics.

Baseline deliberately represents the *unfenced* convenience API accepting
caller asserted fresh=True, as in the preceding source. It is a weakness
demonstration, NOT a competitive distributed-systems fencing baseline.
"""
from __future__ import annotations
import json
import random
from research.effect_aware_authority_certificate import examples, synthesize, request
from research.epoch_fenced_repair_authority import FencedAuthority
from research.repair_authority_cli import parse_contract
from pathlib import Path


def benchmark(seed:int=20261010,n:int=512)->dict:
    if n<2 or n%2:
        raise ValueError("Use even positive paired case count")
    rng=random.Random(seed)
    m=examples()["fresh_discriminating_getter"]
    c=synthesize(m)
    total={"fenced_stale_halts":0,"fenced_fresh_correct":0,
           "legacy_stale_claimed_fresh_authorizations":0,
           "legacy_fresh_correct":0}
    # Every case generated from fixture's modeled exact read response; half
    # late and half current. We do NOT infer future noise from this construction.
    order=[False]*(n//2)+[True]*(n//2)
    rng.shuffle(order)
    for i,is_stale in enumerate(order):
        reply= "good_seen" if rng.randrange(2) else "held_seen"
        expected="GO" if reply=="good_seen" else "RESET"
        legacy=request(m,c,(("read",reply,True),))
        if is_stale:
            total["legacy_stale_claimed_fresh_authorizations"]+=legacy["request"]=="authorize"
        else:
            total["legacy_fresh_correct"]+=legacy.get("repair")==expected
        fenced=FencedAuthority(m,c,session=i+1)
        ticket=fenced.next()
        assert ticket.kind=="read"
        observed=ticket.command_epoch+(rng.choice((-100,-1,1,77)) if is_stale else 0)
        fenced.commit_read(ticket,reply,observed_command_epoch=observed)
        decision=fenced.next()
        if is_stale:
            total["fenced_stale_halts"]+=decision["request"]=="halt"
        else:
            total["fenced_fresh_correct"]+=decision.get("repair")==expected
    if any(total[k]!=n//2 for k in total):
        raise AssertionError("Diagnostic gate failed: unknown read-authority behavior")
    # Intentionally force every unconfirmed probe into fail closed; unguarded
    # caller-provided public response could falsely be treated as delivered.
    f=Path("research/fixtures/authority_cheap_discriminating_probe.json")
    probe_model=parse_contract(json.loads(f.read_text(encoding="utf-8")))
    probe_cert=synthesize(probe_model)
    lost=0
    for i in range(n//2):
        s=FencedAuthority(probe_model,probe_cert,session=n+i+1)
        ticket=s.next()
        s.commit_probe(ticket,"good_seen",acknowledged_delivered=False)
        lost+=s.next()["request"]=="halt"
    assert lost==n//2
    return {"schema":"synthetic_epoch_gate_construction_v1",
        "seed":seed,"paired_cases":n,
        "constructed_stale_reads":n//2,
        "constructed_fresh_reads":n//2,
        "constructed_undelivered_probes":n//2,
        **total,"fenced_unknown_probe_delivery_halts":lost,
        "old_convenience_API_is_NOT_strong_distributed_systems_baseline":True,
        "actual_cpu_physx_trials":0,"physical_task_successes":None,
        "externally_independently_run":False,
        "end_to_end_network_identity_authentication_proved":False}


if __name__=="__main__":
    print("SYNTHETIC_CONTRACT_DIAGNOSTIC",json.dumps(benchmark(),sort_keys=True))

"""Atomic repair commitment after finite-model authorization (local mock backend).

This closes a TIME-OF-CHECK/ TIME-OF-USE gap in the previously authored
epoch-fenced authority *handoff*. The previously returned "authorize" string
did not atomically reserve the controller state while a real repair command
could be dispatched later. A strong ordinary CAS baseline has the SAME
correctness on this local atomic model; do not claim superiority over it.

No real robot actuator, network binding, cryptographic attestation, ROS
controller or physical contact safety is provided here.
"""
from __future__ import annotations
from dataclasses import dataclass
from threading import RLock
from typing import Any
from research.epoch_fenced_repair_authority import FencedAuthority


@dataclass(frozen=True)
class RepairReservation:
    session: int
    nonce: int
    expected_epoch: int
    model_sha256: str
    repair: str


class LocalAtomicController:
    """Clearly labeled TEST DOUBLE, not a hardware adapter.

    Every write is serialized against a monotonically increasing epoch;
    'if current_epoch == expected' and physical command publication belong
    to ONE indivisible in-memory critical section.
    """
    def __init__(self):
        self._lock=RLock()
        self._epoch=0
        self._events: list[tuple[int,str,str]]=[]
        self._mutations=0

    def current_epoch(self)->int:
        with self._lock:
            return self._epoch

    def external_mutation(self, marker: str="interfering_action")->int:
        with self._lock:
            self._epoch+=1
            self._mutations+=1
            self._events.append((self._epoch,"external",marker))
            return self._epoch

    def atomic_repair_if_epoch(self, expected_epoch:int, repair:str)->bool:
        if type(expected_epoch) is not int or not isinstance(repair,str) or not repair:
            raise ValueError("Invalid repair CAS contract")
        with self._lock:
            if self._epoch!=expected_epoch:
                return False
            self._epoch+=1
            self._events.append((self._epoch,"repair",repair))
            return True

    @property
    def audit(self)->dict[str,Any]:
        with self._lock:
            return {"current_epoch":self._epoch,
                    "external_mutations":self._mutations,
                    "committed_repairs":[e for e in self._events if e[1]=="repair"],
                    "events":list(self._events),"simulation_only":True}


class AtomicRepairHandoff:
    """Reserve certificate repair, then CAS-dispatch at the model's epoch.

    All client-visible repairs MUST be sent through commit(); callers MUST
    NOT invoke the backend outside this interface without an epoch change.
    """
    def __init__(self, authority:FencedAuthority, controller:LocalAtomicController):
        if not isinstance(authority,FencedAuthority):
            raise TypeError("Requires verified FencedAuthority")
        if not isinstance(controller,LocalAtomicController):
            raise TypeError("Only local atomic model adapter provided")
        self._authority=authority
        self._controller=controller
        self._nonce=0
        self._reservation:RepairReservation|None=None
        self._closed=False
        self._outcome:str|None=None

    def reserve(self)->RepairReservation|dict[str,Any]:
        if self._closed:
            return {"request":"halt","reason":self._outcome or "closed"}
        if self._reservation is not None:
            return self._reservation
        answer=self._authority.next()
        if not isinstance(answer,dict) or answer.get("request")!="authorize":
            return {"request":"not_authorized","reason":"unfinished_read_or_probe"}
        own=self._authority.audit
        controller_epoch=self._controller.current_epoch()
        if own["epoch"]!=controller_epoch:
            self._closed=True
            self._outcome="backend_epoch_not_equal_to_certified_epoch"
            return {"request":"halt","reason":self._outcome}
        self._nonce+=1
        ticket=RepairReservation(session=own["session"],nonce=self._nonce,
                                 expected_epoch=own["epoch"],
                                 model_sha256=own["model_sha256"],
                                 repair=answer["repair"])
        self._reservation=ticket
        return ticket

    def commit(self, ticket:RepairReservation)->dict[str,Any]:
        if self._closed:
            return {"committed":False,"reason":"closed_or_already_used"}
        if (not isinstance(ticket,RepairReservation) or
                self._reservation is None or ticket!=self._reservation):
            self._closed=True
            self._outcome="wrong_or_replayed_reservation"
            return {"committed":False,"reason":self._outcome}
        local=self._authority.audit
        if (local["halted"] or local["authorized_repair"]!=ticket.repair or
                local["model_sha256"]!=ticket.model_sha256 or
                local["session"]!=ticket.session or
                local["epoch"]!=ticket.expected_epoch):
            self._closed=True
            self._outcome="authority_changed_after_reservation"
            return {"committed":False,"reason":self._outcome}
        # The controller implementation owns the actual indivisible CAS.
        # A separate pre-dispatch epoch check WOULD be racy.
        committed=self._controller.atomic_repair_if_epoch(ticket.expected_epoch,ticket.repair)
        self._closed=True
        self._reservation=None
        self._outcome="committed" if committed else "epoch_advanced_during_handoff"
        if committed:
            self._authority.invalidate_on_external_command()  # consumed irrevocably
        return {"committed":committed,"reason":self._outcome,
                "controller_epoch_after":self._controller.current_epoch(),
                "local_test_double_only":True}


def weak_precheck_then_unconditional_send(ctl:LocalAtomicController,repair:str,
                                          inject_after_precheck:bool)->bool:
    """Deliberately unsafe ablation: NOT a competitive controller baseline."""
    sampled=ctl.current_epoch()
    if inject_after_precheck:
        ctl.external_mutation()
    # A bad API sends unconditionally after stale preflight.
    ctl.external_mutation("UNCONDITIONAL_"+repair)
    return ctl.current_epoch()==sampled+1


def strong_cas_baseline(ctl:LocalAtomicController,repair:str,
                        inject_after_precheck:bool)->bool:
    """Correct reference CAS protocol; same expected correctness as ours."""
    expected=ctl.current_epoch()
    if inject_after_precheck:
        ctl.external_mutation()
    return ctl.atomic_repair_if_epoch(expected,repair)

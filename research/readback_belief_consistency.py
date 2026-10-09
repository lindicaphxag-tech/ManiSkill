"""Versioned readback authority: a compiler cannot use stale belief width.

The original frozen-policy comparison revealed a cached maybe_two boolean
that survived require_external_resync(actual_target) and selected the wrong
control conversion after obtaining the same privileged target measurement.
This zero-simulator module makes belief-version equality an explicit contract.

Epoch and sequence are LOCAL software invariants, not attested sensor/ACK
provenance. It does not prove physical safety, task success, or novelty of
concurrency versioning. It is a reusable fail-closed comparator primitive.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from research.action_abi_uncertain_delivery_belief import UncertainDeliveryBelief


@dataclass(frozen=True)
class BeliefReadVersion:
    epoch: int
    sequence: int
    number_hypotheses: int


@dataclass(frozen=True)
class DispatchAuthority:
    kind: Literal["HYPOTHESIS_SET", "SINGLE_MEMORY", "REJECT"]
    version: BeliefReadVersion
    explanation: str


def snapshot(belief: UncertainDeliveryBelief) -> BeliefReadVersion:
    """Never cache only whether the history set has multiple members."""
    if not isinstance(belief, UncertainDeliveryBelief):
        raise TypeError("Declared source of controller last-target memory required")
    if not belief.valid or belief.pending is not None or not belief.hypotheses:
        raise RuntimeError("Invalid or pending controller belief; fail closed")
    return BeliefReadVersion(
        epoch=belief.epoch, sequence=belief.sequence,
        number_hypotheses=len(belief.hypotheses))


def authorize_dispatch(
    belief: UncertainDeliveryBelief,
    observed: BeliefReadVersion,
) -> DispatchAuthority:
    """Reject if any piece of a previously held belief view became stale."""
    current=snapshot(belief)
    if not isinstance(observed, BeliefReadVersion):
        raise TypeError("Belief dispatch witness must carry epoch and sequence")
    if current!=observed:
        return DispatchAuthority(
            "REJECT", current,
            "STALE_BELIEF_VIEW_AFTER_RESET_READBACK_OR_ACTION_ACK")
    return DispatchAuthority(
        "HYPOTHESIS_SET" if current.number_hypotheses>1 else "SINGLE_MEMORY",
        current,
        "CURRENT_BELIEF_ACTUAL_CONTROLLER_TARGET_CHART")


def refresh_after_private_read(
    belief: UncertainDeliveryBelief, measured_target,
)->DispatchAuthority:
    """One authoritative input invalidates every pre-read branch/handle."""
    belief.require_external_resync(measured_target)
    return authorize_dispatch(belief, snapshot(belief))

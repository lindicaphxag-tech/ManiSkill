"""Version-fenced execution adapter for a FINITE-MODEL repair certificate.

Safety scope: prevents accidental stale/replayed/out-of-order local probe/read
responses from authorizing a repair, WHEN this object is the sole trusted
command dispatcher. Tokens are NOT cryptographically authenticated; the
physical controller, network and read origin remain outside the proof.

No ManiSkill dependency. This composes with existing effect-aware certificate
soundness and independent global optimality checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from research.effect_aware_authority_certificate import (
    Contract, model_hash, request, verify_optimality, verify_policy,
)


@dataclass(frozen=True)
class CommandTicket:
    """Machine-local, unforgeability NOT claimed; issued only by the adapter."""
    session: int
    request_id: int
    command_epoch: int
    kind: str
    action: str | None


class FencedAuthority:
    """Strict single-inflight local state machine for probe/readback/repair."""

    def __init__(self, model: Contract, certificate: dict[str, Any], *,
                 session: int = 1, oracle_cap: int = 200000):
        if type(session) is not int or session <= 0:
            raise ValueError("Invalid positive session identifier")
        verify_policy(model, certificate)
        verify_optimality(model, certificate, max_oracle_nodes=oracle_cap)
        self._model = model
        self._cert = certificate
        self._model_id = model_hash(model)
        self._session = session
        self._epoch = 0
        self._seq = 0
        self._events: list[tuple[str, str, bool]] = []
        self._pending: CommandTicket | None = None
        self._last_authorization: str | None = None
        self._halt_reason: str | None = None
        self._read_receipts = 0
        self._probes_committed = 0

    @property
    def audit(self) -> dict[str, Any]:
        return {"model_sha256": self._model_id, "session": self._session,
                "epoch": self._epoch, "pending": self._pending is not None,
                "halted": self._halt_reason is not None,
                "halt_reason": self._halt_reason,
                "authorized_repair": self._last_authorization,
                "verified_read_receipts": self._read_receipts,
                "verified_probe_receipts": self._probes_committed,
                "model_only": True,
                "real_robot_safety_proven": False}

    def _halt(self, reason: str):
        self._pending = None
        self._last_authorization = None
        self._halt_reason = reason

    def invalidate_on_external_command(self):
        """Call before any command issued outside the guarded adapter.

        If this is bypassed, all version claims become inapplicable.
        """
        self._epoch += 1
        self._halt("external_command_not_in_model")

    def next(self) -> dict[str, Any] | CommandTicket:
        """Returns a ticket for ONE actual dispatch, or a model-only repair decision.

        No caller-provided fresh=True can bypass a read receipt.
        """
        if self._halt_reason is not None:
            return {"request": "halt", "reason": self._halt_reason,
                    "model_only": True}
        if self._pending is not None:
            return self._pending  # idempotent: never issue two concurrent commands
        if self._last_authorization is not None:
            return {"request": "authorize", "repair": self._last_authorization,
                    "model_only": True}
        result = request(self._model, self._cert, tuple(self._events))
        if not result["model_bound_valid"]:
            self._halt("out_of_model_response")
            return self.next()
        kind = result["request"]
        if kind == "halt":
            self._halt("insufficient_authority")
            return self.next()
        if kind == "authorize":
            self._last_authorization = result["repair"]
            return self.next()
        if kind not in ("read", "probe"):
            raise RuntimeError("Unknown certificate command")
        self._seq += 1
        ticket = CommandTicket(self._session, self._seq, self._epoch,
                               kind, result.get("probe") if kind == "probe" else None)
        self._pending = ticket
        return ticket

    def commit_probe(self, ticket: CommandTicket, response: str, *,
                     acknowledged_delivered: bool) -> None:
        if (self._halt_reason is not None or self._pending != ticket or
                not isinstance(ticket, CommandTicket) or
                ticket.kind != "probe"):
            self._halt("wrong_or_replayed_probe_ticket")
            return
        if type(acknowledged_delivered) is not bool or acknowledged_delivered is not True:
            self._halt("probe_delivery_not_confirmed")
            return
        if ticket.command_epoch != self._epoch:
            self._halt("probe_epoch_mismatch")
            return
        if not isinstance(response, str) or not response:
            self._halt("invalid_public_probe_response")
            return
        self._epoch += 1  # actual known-delivered probe may change controller state
        self._events.append(("probe", response, True))
        self._pending = None
        self._probes_committed += 1
        if not request(self._model, self._cert, tuple(self._events))["model_bound_valid"]:
            self._halt("unknown_physical_probe_response")

    def commit_read(self, ticket: CommandTicket, response: str, *,
                    observed_command_epoch: int) -> None:
        if (self._halt_reason is not None or self._pending != ticket or
                not isinstance(ticket, CommandTicket) or
                ticket.kind != "read"):
            self._halt("wrong_or_replayed_read_ticket")
            return
        if (type(observed_command_epoch) is not int or
                ticket.command_epoch != self._epoch or
                observed_command_epoch != self._epoch):
            self._halt("read_does_not_match_current_controller_epoch")
            return
        if not isinstance(response, str) or not response:
            self._halt("invalid_privileged_read_response")
            return
        self._events.append(("read", response, True))
        self._pending = None
        self._read_receipts += 1
        if not request(self._model, self._cert, tuple(self._events))["model_bound_valid"]:
            self._halt("unknown_privileged_read_response")

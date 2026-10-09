"""Correct CAS baseline versus intentionally unsafe preflight ablation.

All results are deterministic, local in-memory event-interleaving tests, NOT
physical control outcomes or improvements over a correctly fenced controller.
"""
import random
import unittest

from research.atomic_repair_handoff import (
    AtomicRepairHandoff, LocalAtomicController, RepairReservation,
    weak_precheck_then_unconditional_send, strong_cas_baseline,
)
from research.effect_aware_authority_certificate import examples, synthesize
from research.epoch_fenced_repair_authority import FencedAuthority


def prepared(backend=None):
    m=examples()["fresh_discriminating_getter"]
    auth=FencedAuthority(m,synthesize(m),session=19)
    read=auth.next()
    assert read.kind=="read"
    auth.commit_read(read,"good_seen",observed_command_epoch=0)
    assert auth.next()["repair"]=="GO"
    ctl=backend or LocalAtomicController()
    return ctl,auth,AtomicRepairHandoff(auth,ctl)


class AtomicRepairHandoffCases(unittest.TestCase):
    def test_clean_repair_commits_once_with_matching_epoch(self):
        ctl,_,handoff=prepared()
        ticket=handoff.reserve()
        self.assertIsInstance(ticket,RepairReservation)
        self.assertIs(ticket,handoff.reserve())
        outcome=handoff.commit(ticket)
        self.assertTrue(outcome["committed"])
        self.assertEqual(len(ctl.audit["committed_repairs"]),1)
        self.assertEqual(ctl.audit["committed_repairs"][0][2],"GO")
        self.assertFalse(handoff.commit(ticket)["committed"])
        self.assertEqual(len(ctl.audit["committed_repairs"]),1)

    def test_external_mutation_between_reservation_and_actual_dispatch_rejected(self):
        ctl,_,handoff=prepared()
        ticket=handoff.reserve()
        ctl.external_mutation()
        result=handoff.commit(ticket)
        self.assertFalse(result["committed"])
        self.assertEqual(result["reason"],"epoch_advanced_during_handoff")
        self.assertEqual(ctl.audit["committed_repairs"],[])

    def test_preflight_only_baseline_can_dispatch_stale_repair(self):
        ctl=LocalAtomicController()
        self.assertFalse(weak_precheck_then_unconditional_send(ctl,"GO",True))
        self.assertIn("UNCONDITIONAL_GO",[x[2] for x in ctl.audit["events"]])
        other=LocalAtomicController()
        self.assertFalse(strong_cas_baseline(other,"GO",True))
        self.assertEqual(other.audit["committed_repairs"],[])

    def test_correct_cas_baseline_has_no_exaggerated_proposed_advantage(self):
        rng=random.Random(20261010)
        summary={"atomic_clean":0,"atomic_stale_refused":0,
                 "strong_clean":0,"strong_stale_refused":0,
                 "weak_stale_dispatches":0}
        inject=[False]*256+[True]*256
        rng.shuffle(inject)
        for noisy in inject:
            ctl,_,bridge=prepared()
            reservation=bridge.reserve()
            if noisy:
                ctl.external_mutation()
            result=bridge.commit(reservation)
            reference=LocalAtomicController()
            got=strong_cas_baseline(reference,"GO",noisy)
            self.assertEqual(result["committed"],got)
            self.assertEqual(len(ctl.audit["committed_repairs"]),
                             len(reference.audit["committed_repairs"]))
            if noisy:
                summary["atomic_stale_refused"]+=not result["committed"]
                summary["strong_stale_refused"]+=not got
                bad=LocalAtomicController()
                weak_precheck_then_unconditional_send(bad,"GO",True)
                summary["weak_stale_dispatches"]+=bool([
                    e for e in bad.audit["events"] if e[2]=="UNCONDITIONAL_GO"])
            else:
                summary["atomic_clean"]+=result["committed"]
                summary["strong_clean"]+=got
        self.assertEqual(summary,{"atomic_clean":256,
            "atomic_stale_refused":256,"strong_clean":256,
            "strong_stale_refused":256,"weak_stale_dispatches":256})

    def test_false_ticket_is_not_actuator_authority(self):
        ctl,_,bridge=prepared()
        ticket=bridge.reserve()
        fake=RepairReservation(ticket.session,ticket.nonce+1,
                               ticket.expected_epoch,ticket.model_sha256,ticket.repair)
        self.assertFalse(bridge.commit(fake)["committed"])
        self.assertEqual(ctl.audit["committed_repairs"],[])

    def test_session_or_repair_mutation_invalidates_handoff(self):
        ctl,auth,bridge=prepared()
        ticket=bridge.reserve()
        auth.invalidate_on_external_command()
        self.assertFalse(bridge.commit(ticket)["committed"])
        self.assertEqual(ctl.audit["committed_repairs"],[])

    def test_unresolved_read_never_receives_repair_reservation(self):
        m=examples()["fresh_discriminating_getter"]
        auth=FencedAuthority(m,synthesize(m))
        bridge=AtomicRepairHandoff(auth,LocalAtomicController())
        self.assertEqual(bridge.reserve()["request"],"not_authorized")

    def test_mismatched_controller_initial_epoch_never_authorized(self):
        ctl,_,bridge=prepared()
        ctl.external_mutation()
        self.assertEqual(bridge.reserve()["request"],"halt")
        self.assertEqual(bridge.commit(RepairReservation(19,1,0,"x","GO"))["committed"],False)

    def test_invalid_cas_args_fail_closed(self):
        ctl=LocalAtomicController()
        with self.assertRaises(ValueError):
            ctl.atomic_repair_if_epoch(False,"GO")
        with self.assertRaises(ValueError):
            ctl.atomic_repair_if_epoch(0,"")

    def test_exact_epoch_change_after_dispatch_does_not_fake_rollback(self):
        ctl,_,bridge=prepared()
        t=bridge.reserve()
        self.assertTrue(bridge.commit(t)["committed"])
        ctl.external_mutation()
        self.assertEqual(len(ctl.audit["committed_repairs"]),1)
        self.assertEqual(ctl.current_epoch(),2)  # no safety claim about later mutation


if __name__=="__main__":
    unittest.main()

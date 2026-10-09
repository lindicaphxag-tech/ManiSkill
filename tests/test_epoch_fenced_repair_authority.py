"""Attack the local ACK/read epoch, stale/forged responses, and cheap probe path."""
import unittest
from pathlib import Path
import json
from research.effect_aware_authority_certificate import examples, synthesize, request
from research.epoch_fenced_repair_authority import FencedAuthority, CommandTicket
from research.repair_authority_cli import parse_contract


class FencedAuthorityTests(unittest.TestCase):
    def test_perfect_read_issues_ticket_then_authorizes_only_after_correlated_receipt(self):
        model=examples()["fresh_discriminating_getter"]
        s=FencedAuthority(model,synthesize(model),session=7)
        t=s.next()
        self.assertEqual((t.session,t.command_epoch,t.kind),(7,0,"read"))
        self.assertEqual(s.next(),t) # no duplicate concurrent dispatch
        self.assertIsNone(s.commit_read(t,"good_seen",observed_command_epoch=0))
        self.assertEqual(s.next()["repair"],"GO")
        self.assertEqual(s.audit["verified_read_receipts"],1)

    def test_old_boolean_fresh_accepts_stale_string_but_fenced_rejects(self):
        model=examples()["fresh_discriminating_getter"]
        cert=synthesize(model)
        # Historical convenience API accepts caller's unverified fresh=True.
        old=request(model,cert,(("read","good_seen",True),))
        self.assertEqual((old["request"],old["repair"]),("authorize","GO"))
        s=FencedAuthority(model,cert)
        t=s.next()
        s.commit_read(t,"good_seen",observed_command_epoch=-1)
        self.assertEqual(s.next()["request"],"halt")
        self.assertEqual(s.audit["halt_reason"],
                         "read_does_not_match_current_controller_epoch")
        self.assertEqual(s.audit["verified_read_receipts"],0)

    def test_replayed_read_receipt_after_authorization_fails_closed(self):
        m=examples()["fresh_discriminating_getter"]
        s=FencedAuthority(m,synthesize(m))
        t=s.next()
        s.commit_read(t,"good_seen",observed_command_epoch=0)
        self.assertEqual(s.next()["request"],"authorize")
        s.commit_read(t,"good_seen",observed_command_epoch=0)
        self.assertEqual(s.next()["request"],"halt")

    def test_read_outside_expected_observation_support_fails_closed(self):
        m=examples()["fresh_discriminating_getter"]
        s=FencedAuthority(m,synthesize(m))
        t=s.next()
        s.commit_read(t,"unknown_physically_observed_value",
                      observed_command_epoch=0)
        self.assertEqual(s.next()["request"],"halt")
        self.assertEqual(s.audit["halt_reason"],"unknown_privileged_read_response")

    def test_concurrent_external_command_invalidates_inflight_read(self):
        m=examples()["fresh_discriminating_getter"]
        s=FencedAuthority(m,synthesize(m))
        t=s.next()
        s.invalidate_on_external_command()
        s.commit_read(t,"good_seen",observed_command_epoch=0)
        self.assertEqual(s.next()["request"],"halt")
        self.assertEqual(s.audit["epoch"],1)
        self.assertIsNone(s.audit["authorized_repair"])

    def test_probe_receipt_triggers_post_action_state_and_new_plan(self):
        f=Path("research/fixtures/authority_cheap_discriminating_probe.json")
        m=parse_contract(json.loads(f.read_text()))
        s=FencedAuthority(m,synthesize(m))
        t=s.next()
        self.assertEqual((t.kind,t.action),("probe","discriminating_probe"))
        s.commit_probe(t,"held_seen",acknowledged_delivered=True)
        self.assertEqual(s.audit["epoch"],1)
        self.assertEqual(s.next()["repair"],"RESET")

    def test_probe_unknown_ack_fails_closed_not_optimistic_continue(self):
        f=Path("research/fixtures/authority_cheap_discriminating_probe.json")
        m=parse_contract(json.loads(f.read_text()))
        s=FencedAuthority(m,synthesize(m))
        t=s.next()
        s.commit_probe(t,"good_seen",acknowledged_delivered=False)
        self.assertEqual(s.next()["request"],"halt")
        self.assertEqual(s.audit["halt_reason"],"probe_delivery_not_confirmed")

    def test_probe_unknown_observation_exits_certified_domain(self):
        f=Path("research/fixtures/authority_cheap_discriminating_probe.json")
        m=parse_contract(json.loads(f.read_text()))
        s=FencedAuthority(m,synthesize(m))
        s.commit_probe(s.next(),"unknown_external_sensor",acknowledged_delivered=True)
        self.assertEqual(s.next()["request"],"halt")
        self.assertEqual(s.audit["halt_reason"],"unknown_physical_probe_response")

    def test_wrong_session_ticket_kills_request(self):
        m=examples()["fresh_discriminating_getter"]
        s=FencedAuthority(m,synthesize(m),session=2)
        t=s.next()
        fake=CommandTicket(t.session+1,t.request_id,t.command_epoch,t.kind,t.action)
        s.commit_read(fake,"good_seen",observed_command_epoch=0)
        self.assertEqual(s.next()["request"],"halt")

    def test_incomplete_getter_means_halt_without_unneeded_ticket(self):
        m=examples()["aliased_getter"]
        s=FencedAuthority(m,synthesize(m))
        self.assertEqual(s.next()["request"],"halt")
        self.assertIsNone(s.audit["authorized_repair"])

    def test_invalid_session_must_reject(self):
        m=examples()["fresh_discriminating_getter"]
        for session in (0,-1,False,3.14):
            with self.assertRaises(ValueError):
                FencedAuthority(m,synthesize(m),session=session)


if __name__=="__main__":
    unittest.main()

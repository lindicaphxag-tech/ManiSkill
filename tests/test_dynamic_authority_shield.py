"""Adversarial dynamic-control repair authority tests; no physics and no real safety claims."""
import copy
import random
import unittest

from research.dynamic_authority_shield import (
    DynamicContract, DynamicProbe, brute_force_value, cases, check,
    model_digest, next_request, successors, synthesize,
)
from research.authority_probe_minimax import Model, Probe, synthesize as static_synthesize


class DynamicControllerAuthority(unittest.TestCase):
    def test_probe_changes_repair_and_static_assumption_really_fails(self):
        m=cases()["shifting_repair"]
        dynamic=synthesize(m)
        self.assertEqual(dynamic["root"]["kind"], "probe")
        self.assertEqual(dynamic["worst_abstract_cost"], 1)
        self.assertEqual(next_request(m,dynamic,("ack",))["repair"],"REINITIALIZE")
        self.assertEqual(next_request(m,dynamic,("no_ack",))["repair"],"REINITIALIZE")
        # A naive repair-preserving static planner would issue CONTINUE on ack.
        old=Model({"delivered":"CONTINUE","held":"REINITIALIZE"},
                  (Probe("diagnostic_move",1,
                         {"delivered":("ack",),"held":("no_ack",)}),),5,1)
        stat=static_synthesize(old)
        self.assertEqual(stat["root"]["branches"]["ack"]["repair"], "CONTINUE")
        self.assertNotEqual(stat["root"]["branches"]["ack"]["repair"],
                            dynamic["root"]["branches"]["ack"]["repair"])

    def test_all_feasible_transitions_must_be_model_safe(self):
        m=cases()["unsafe_probe_veto"]
        cert=synthesize(m)
        self.assertEqual(cert["root"]["kind"],"read")
        self.assertEqual(cert["worst_abstract_cost"],5)
        unsafe=copy.deepcopy(cert)
        unsafe["root"]={"kind":"probe","probe":m.probes[0].name,
                         "belief":list(sorted(m.initial_states)), "remaining_cost":1,
                         "branches":{}}
        with self.assertRaisesRegex(ValueError,"unsafe probe"):
            check(m,unsafe)

    def test_uninformative_nonzero_actuation_is_rejected(self):
        m=cases()["costly_uninformative_probe"]
        cert=synthesize(m)
        self.assertEqual(cert["root"]["kind"],"read")
        self.assertEqual(cert["worst_abstract_cost"],m.read_cost)

    def test_multiple_next_states_same_observation_preserve_ambiguity(self):
        m=DynamicContract(
            {"s1":"A","s2":"B","s3":"A"},("s1","s2"),(),
            (DynamicProbe("noisy",1,{
                "s1":(("visible","s3"),("shared","s1")),
                "s2":(("visible","s2"),("shared","s2")),
                "s3":(("visible","s3"),),
            }),),5,2)
        next_b=successors(m,m.probes[0],tuple(sorted(m.initial_states)))
        self.assertEqual(next_b["visible"],("s2","s3"))
        self.assertEqual(synthesize(m)["root"]["kind"],"read")

    def test_unknown_runtime_outcome_invalidates_old_cost_bound(self):
        m=cases()["shifting_repair"]
        cert=synthesize(m)
        request=next_request(m,cert,("unexpected_camera_measurement",))
        self.assertEqual(request["request"],"read")
        self.assertFalse(request["model_bound_valid_for_trace"])
        self.assertEqual(request["already_spent_cost"],1)
        self.assertEqual(request["additional_read_cost"],5)
        with self.assertRaisesRegex(ValueError,"extra observation"):
            next_request(m,cert,("ack","invalid_extra"))

    def test_proof_checker_rejects_corrupted_belief_cost_and_repair(self):
        m=cases()["shifting_repair"]
        cert=synthesize(m)
        for wrong,regex in [
            (("belief",["delivered"]), "belief"),
            (("remaining_cost",999),"cost"),
        ]:
            fake=copy.deepcopy(cert)
            fake["root"][wrong[0]]=wrong[1]
            with self.assertRaisesRegex(ValueError,regex):
                check(m,fake)
        fake=copy.deepcopy(cert)
        fake["root"]["branches"]["ack"]["repair"]="CONTINUE"
        with self.assertRaisesRegex(ValueError,"wrong repair"):
            check(m,fake)
        fake=copy.deepcopy(cert)
        del fake["root"]["branches"]["no_ack"]
        with self.assertRaisesRegex(ValueError,"missing"):
            check(m,fake)

    def test_stale_model_digest_prohibits_authorizing_old_certificate(self):
        m=cases()["shifting_repair"]
        cert=synthesize(m)
        changed=DynamicContract(dict(m.repair_by_state),m.initial_states,m.forbidden_states,
                                m.probes,6,m.horizon)
        self.assertNotEqual(model_digest(m),model_digest(changed))
        with self.assertRaisesRegex(ValueError,"identity"):
            check(changed,cert)

    def test_incomplete_or_forbidden_initial_model_fail_closed(self):
        bad=DynamicContract({"s":"A","u":"B"},("s",),(),
                            (DynamicProbe("p",1,{"s":(("o","s"),)}),),5,1)
        with self.assertRaisesRegex(ValueError,"incomplete"):
            synthesize(bad)
        bad=DynamicContract({"s":"A","u":"B"},("s","u"),("s",),(),5,1)
        with self.assertRaisesRegex(ValueError,"unsafe"):
            synthesize(bad)

    def test_equal_repair_initial_belief_needs_no_controller_getter(self):
        m=DynamicContract({"s":"reset","t":"reset"},("s","t"),(),(),8,3)
        cert=synthesize(m)
        self.assertEqual(cert["root"]["kind"],"authorize")
        self.assertEqual(cert["worst_abstract_cost"],0)
        self.assertEqual(next_request(m,cert,())["repair"],"reset")

    def test_exhaustive_model_oracle_160_random_cases(self):
        rng=random.Random(20261010)
        for trial in range(160):
            n=rng.randint(2,4)
            states=tuple("abcd"[:n])
            repairs={s:"r"+str(rng.randrange(3)) for s in states}
            initial=tuple(sorted(rng.sample(states,rng.randint(1,n))))
            forbidden=tuple(s for s in states if s not in initial and rng.random()<.25)
            probes=[]
            for i in range(rng.randint(0,3)):
                trans={}
                for s in states:
                    draws=set()
                    for _ in range(rng.randint(1,3)):
                        draws.add((rng.choice(("x","y","z")),rng.choice(states)))
                    trans[s]=tuple(sorted(draws))
                probes.append(DynamicProbe("p"+str(i),rng.randint(1,4),trans))
            m=DynamicContract(repairs,initial,forbidden,tuple(probes),
                              rng.randint(2,7),rng.randint(0,3))
            cert=synthesize(m)
            self.assertEqual(cert["worst_abstract_cost"],brute_force_value(m),trial)
            self.assertEqual(check(m,cert)["worst_abstract_cost"],
                             cert["worst_abstract_cost"],trial)


if __name__=="__main__":
    unittest.main()

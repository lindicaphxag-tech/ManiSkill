"""Adversarial, deterministic checks for repair-aware minimax certificates.

No PhysX run or claim of empirical benefit; source-only soundness tests.
"""
import copy
import random
import unittest
from research.authority_probe_minimax import (
    Model, Probe, synthesize, certify, brute_force_minimax_value,
    possible_posteriors, showcase, next_request,
)


class AuthorityProbeMinimax(unittest.TestCase):
    def test_task_equivalent_histories_do_not_need_hidden_history_identity(self):
        m=Model({"a":"same","b":"same","c":"same"}, (), 9, 1)
        result=synthesize(m)
        self.assertEqual(result["root"]["kind"], "authorize")
        self.assertEqual(result["worst_cost_units"], 0)
        self.assertGreater(certify(m,result)["authorized_leaf_world_traces"], 0)

    def test_colliding_zero_and_nonzero_both_abstain_and_read(self):
        m=Model({"held":"reset","applied":"continue"},
                (Probe("zero",1,{"held":("same",),"applied":("same",)}),
                 Probe("nonzero",2,{"held":("same",),"applied":("same",)})),5,4)
        self.assertEqual(synthesize(m)["root"]["kind"], "read")

    def test_global_planner_beats_greedy_cheapest_probe(self):
        h=tuple("ABCD")
        m=Model({x:"repair"+x for x in h},
                (Probe("cheap",1,{"A":("x",),"B":("x",),"C":("y",),"D":("y",)}),
                 Probe("complete",3,{x:(x,) for x in h})),5,2)
        output=synthesize(m)
        self.assertEqual(output["root"]["probe"], "complete")
        self.assertEqual(output["worst_cost_units"],3)
        self.assertEqual(certify(m,output)["worst_cost_units"],3)

    def test_noisy_overlapping_support_is_not_safety_evidence(self):
        m=Model({"a":"repair1","b":"repair2"},
                (Probe("maybe",1,{"a":("a_seen","shared"),
                                   "b":("b_seen","shared")}),),5,1)
        output=synthesize(m)
        self.assertEqual(output["root"]["kind"],"read")
        self.assertEqual(output["worst_cost_units"],5)

    def test_optimistic_information_is_insufficient_for_worst_case(self):
        m=Model({"a":"a","b":"b","c":"c"},
                (Probe("maybe",1,{"a":("a",),"b":("shared",),"c":("shared",)}),),4,2)
        self.assertEqual(synthesize(m)["worst_cost_units"],4)

    def test_adversarial_verifier_rejects_false_authority(self):
        m=Model({"h1":"A","h2":"B"},
                (Probe("split",1,{"h1":("o1",),"h2":("o2",)}),),5,1)
        good=synthesize(m)
        self.assertEqual(good["root"]["kind"],"probe")
        altered=copy.deepcopy(good)
        altered["root"]["branches"]["o1"]["repair"]="B"
        with self.assertRaisesRegex(ValueError,"wrong authority"):
            certify(m,altered)
        altered=copy.deepcopy(good)
        del altered["root"]["branches"]["o2"]
        with self.assertRaisesRegex(ValueError,"missing"):
            certify(m,altered)
        altered=copy.deepcopy(good)
        altered["root"]["worst_remaining_cost"]=0
        with self.assertRaisesRegex(ValueError,"cost"):
            certify(m,altered)

    def test_forged_self_consistent_but_nonoptimal_certificate_is_rejected(self):
        # This attack formerly passed certify(): the branch and cost are
        # internally valid, but there is a distinguishing one-unit probe.
        m=Model({"a":"A","b":"B"},
                (Probe("split",1,{"a":("left",),"b":("right",)}),),
                authoritative_read_cost=5,max_probe_depth=1)
        true_plan=synthesize(m)
        self.assertEqual(true_plan["worst_cost_units"],1)
        self.assertEqual(certify(m,true_plan)["independent_optimal_cost"],1)
        forged=copy.deepcopy(true_plan)
        forged["root"]={"kind":"read","belief":["a","b"],"worst_remaining_cost":5}
        forged["worst_cost_units"]=5
        with self.assertRaisesRegex(ValueError,"NOT globally minimax"):
            certify(m,forged)
        # Conversely a verifier that only checks an expected root number
        # would miss a nonoptimal *internal subtree*.
        m2=Model({"a":"A","b":"B","c":"C"},
                 (Probe("first",1,{"a":("a",),"b":("bc",),"c":("bc",)}),
                  Probe("second",1,{"a":("a",),"b":("b",),"c":("c",)})),
                 authoritative_read_cost=5,max_probe_depth=2)
        correct=synthesize(m2)
        self.assertEqual(certify(m2,correct)["independent_optimal_cost"],1)
        other=copy.deepcopy(correct)
        other["root"]={"kind":"read","belief":["a","b","c"],"worst_remaining_cost":5}
        other["worst_cost_units"]=5
        with self.assertRaisesRegex(ValueError,"NOT globally minimax"):
            certify(m2,other)

    def test_unsafe_probes_or_incomplete_responses_fail_closed(self):
        m=Model({"a":"A","b":"B"},
                (Probe("p",1,{"a":("x",),"b":("y",)},preserves_repair=False),),5,1)
        with self.assertRaisesRegex(ValueError,"invariance"):
            synthesize(m)
        bad=Model({"a":"A","b":"B"},(Probe("p",1,{"a":("x",)}),),5,2)
        with self.assertRaisesRegex(ValueError,"missing"):
            synthesize(bad)

    def test_dynamic_program_matches_separate_exhaustive_oracle_on_70_cases(self):
        rng=random.Random(20261010)
        for case in range(70):
            h=tuple("ABCD"[:rng.randint(2,4)])
            repairs={x:str(rng.randrange(3)) for x in h}
            probes=[]
            for i in range(rng.randint(0,3)):
                support={x:tuple(k for k in "xyz" if rng.randrange(2)) or ("x",)
                         for x in h}
                probes.append(Probe("p"+str(i),rng.randint(1,4),support))
            model=Model(repairs,tuple(probes),rng.randint(2,6),rng.randint(0,3))
            tree=synthesize(model)
            self.assertEqual(tree["worst_cost_units"],brute_force_minimax_value(model),case)
            self.assertEqual(certify(model,tree)["worst_cost_units"],tree["worst_cost_units"])

    def test_runtime_request_is_fail_closed_on_unmodeled_public_response(self):
        model=Model({"a":"A","b":"B"},
                    (Probe("visible",1,{"a":("a_only",),"b":("b_only",)}),),5,1)
        cert=synthesize(model)
        first=next_request(model,cert,())
        self.assertEqual((first["request"],first["probe"]),("probe","visible"))
        self.assertEqual(next_request(model,cert,("a_only",))["repair"],"A")
        self.assertEqual(next_request(model,cert,("b_only",))["repair"],"B")
        unknown=next_request(model,cert,("unmodeled_or_shifted",))
        self.assertEqual(unknown["request"],"read")
        self.assertEqual(unknown["reason"],"unmodeled_observation")
        self.assertFalse(unknown["model_certificate_valid_for_this_trace"])
        self.assertEqual(unknown["spent_abstract_probe_cost"],1)
        with self.assertRaisesRegex(ValueError,"unexpected observation"):
            next_request(model,cert,("a_only","late_extra"))

    def test_synthetic_demo_is_clearly_labeled(self):
        result=showcase()
        self.assertTrue(result["synthetic_only"])
        self.assertEqual(set(result["examples"]),
                         {"repair_quotient","globally_cheapest_probe","uninformative_actuation"})


if __name__=="__main__":
    unittest.main()

"""Model-only independent verifier and nontransitive repair-overlap tests."""
import copy
import random
import unittest

from research.action_set_authority_minimax import (
    ActionSetModel, ActionProbe, plan, verify, exhaustive_oracle, decision,
)
from research.authority_probe_minimax import Model, Probe, synthesize


class CommonActionAuthority(unittest.TestCase):
    def test_nontransitive_action_overlap_changes_information_requirement(self):
        # h1+h2 permit command B, h2+h3 permit C, but all three have no
        # single universally valid command. A public probe separates h3.
        allowed={"h1":("A","B"),"h2":("B","C"),"h3":("C","D")}
        probe=ActionProbe("observed",1,{
            "h1":("left",),"h2":("left",),"h3":("right",)})
        m=ActionSetModel(allowed,(probe,),5,1)
        cert=plan(m)
        self.assertEqual(cert["worst_cost"],1)
        self.assertEqual(cert["root"]["kind"],"probe")
        self.assertEqual(decision(m,cert,("left",))["action"],"B")
        self.assertEqual(decision(m,cert,("right",))["action"],"C")
        self.assertTrue(verify(m,cert)["verified"])
        # The earlier one-repair-per-state symbolic contract is STRICTLY
        # less expressive for this admissible-action case.
        old=Model({"h1":"A","h2":"B","h3":"C"},
            (Probe("observed",1,{"h1":("left",),"h2":("left",),
                                  "h3":("right",)}),),5,1)
        self.assertEqual(synthesize(old)["worst_cost_units"],5)

    def test_pairwise_compatibility_does_not_imply_global_common_command(self):
        m=ActionSetModel({"x":("A","B"),"y":("B","C"),"z":("A","C")},(),4,2)
        self.assertEqual(plan(m)["root"]["kind"],"read")
        self.assertEqual(plan(m)["worst_cost"],4)

    def test_forged_unsafe_command_and_missing_response_refused(self):
        m=ActionSetModel({"x":("A",),"y":("B",)},
          (ActionProbe("test",1,{"x":("o1",),"y":("o2",)}),),5,1)
        original=plan(m)
        self.assertEqual(original["root"]["kind"],"probe")
        forged=copy.deepcopy(original)
        forged["root"]["branches"]["o1"]["action"]="B"
        with self.assertRaisesRegex(ValueError,"false authority"):
            verify(m,forged)
        forged=copy.deepcopy(original)
        del forged["root"]["branches"]["o2"]
        with self.assertRaisesRegex(ValueError,"missing"):
            verify(m,forged)
        forged=copy.deepcopy(original)
        forged["worst_cost"]=0
        with self.assertRaisesRegex(ValueError,"root cost"):
            verify(m,forged)

    def test_unmodeled_observation_triggers_read_not_action(self):
        m=ActionSetModel({"x":("A",),"y":("B",)},
           (ActionProbe("test",1,{"x":("x_seen",),
                                  "y":("y_seen",)}),),5,1)
        c=plan(m)
        fallback=decision(m,c,("sensor_shift",))
        self.assertEqual(fallback["request"],"read")
        self.assertFalse(fallback["certificate_valid_for_trace"])

    def test_incomplete_action_set_or_unsafe_actuation_refused(self):
        for m in (
          ActionSetModel({"x":("A",),"y":()},(),5,1),
          ActionSetModel({"x":("A",),"y":("B",)},
            (ActionProbe("bad",1,{"x":("seen",)}),),5,1),
          ActionSetModel({"x":("A",),"y":("B",)},
            (ActionProbe("unsafe",1,{"x":("seen",),"y":("seen",)},
                         preserves_action_sets=False),),5,1),
        ):
            with self.assertRaises(ValueError):
                plan(m)

    def test_exhaustive_oracle_agreement_in_100_seeded_models(self):
        rng=random.Random(20261010)
        letters=("A","B","C","D")
        for i in range(100):
            histories=tuple("h"+str(j) for j in range(rng.randint(2,4)))
            permitted={h:tuple(a for a in letters if rng.randrange(2)) or ("A",)
                       for h in histories}
            probes=[]
            for j in range(rng.randrange(4)):
                supports={h:tuple(s for s in ("o1","o2","o3")
                                  if rng.randrange(2)) or ("o1",)
                          for h in histories}
                probes.append(ActionProbe("p"+str(j),rng.randint(1,4),supports))
            model=ActionSetModel(permitted,tuple(probes),rng.randint(2,6),
                                 rng.randint(0,2))
            result=plan(model)
            self.assertEqual(result["worst_cost"],exhaustive_oracle(model),i)
            self.assertEqual(verify(model,result)["worst_cost"],result["worst_cost"])


if __name__=="__main__":
    unittest.main()

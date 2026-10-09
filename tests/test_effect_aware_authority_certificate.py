"""Adversarial proof-carrying repair authorization tests; synthetic only."""
import copy
import random
import unittest
from research.effect_aware_authority_certificate import (
    Action, Contract, examples, model_hash, request, safe_repairs,
    synthesize, validate, verify_optimality, verify_policy,
)


def intervention_model():
    states=("a","b","stabilized","goal","danger")
    repairs={
        "CONTINUE":{"a":("goal",),"b":("danger",),
                    "stabilized":("danger",),"goal":("goal",),"danger":("danger",)},
        "RESET":{"a":("danger",),"b":("goal",),
                 "stabilized":("danger",),"goal":("goal",),"danger":("danger",)},
        "RESTORE":{"a":("danger",),"b":("danger",),
                   "stabilized":("goal",),"goal":("goal",),"danger":("danger",)},
    }
    make=lambda next_a,next_b: Action("diagnose",1,{
        "a":(("same",next_a),),"b":(("same",next_b),),
        "stabilized":(("same","stabilized"),),
        "goal":(("same","goal"),),"danger":(("same","danger"),)})
    return Contract(initial=("a","b"),goals=("goal",),forbidden=("danger",),
                    probes=(make("stabilized","stabilized"),),
                    repair_effects=repairs,
                    read_support={s:(s,) for s in states},
                    read_atomic_and_fresh=True,
                    read_cost=6,stop_cost=15,horizon=1)


class FullRepairAuthorityCertificate(unittest.TestCase):
    def test_aliased_read_cannot_claim_perfect_state_authority(self):
        d=examples()
        self.assertEqual(synthesize(d["aliased_getter"])["root"]["kind"],"halt")
        self.assertEqual(synthesize(d["fresh_discriminating_getter"])["root"]["kind"],"read")
        self.assertEqual(synthesize(d["unattested_getter"])["root"]["kind"],"halt")

    def test_post_probe_repair_can_change_and_remain_safely_authorized(self):
        m=intervention_model()
        cert=synthesize(m)
        self.assertEqual(cert["root"]["kind"],"probe")
        self.assertEqual(cert["minimax_cost"],1)
        self.assertEqual(cert["root"]["branches"]["same"]["repair"],"RESTORE")
        self.assertEqual(safe_repairs(m,tuple(sorted(m.initial))),())
        self.assertEqual(request(m,cert,())["probe"],"diagnose")
        self.assertEqual(request(m,cert,(("probe","same",True),))["repair"],"RESTORE")

    def test_all_possible_latent_transitions_including_rare_forbidden_are_vetoed(self):
        m=intervention_model()
        old=m.probes[0]
        poisoned=dict(old.transitions)
        poisoned["a"]=(("same","stabilized"),("rare","danger"))
        broken=Contract(m.initial,m.goals,m.forbidden,
                        (Action("diagnose",1,poisoned),),m.repair_effects,
                        m.read_support,True,m.read_cost,m.stop_cost,m.horizon)
        cert=synthesize(broken)
        self.assertEqual(cert["root"]["kind"],"read")
        self.assertEqual(cert["minimax_cost"],6)

    def test_postrepair_effect_is_required_for_every_possible_state(self):
        m=intervention_model()
        cert=synthesize(m)
        fake=copy.deepcopy(cert)
        fake["root"]={"kind":"authorize","repair":"CONTINUE",
                       "belief":list(sorted(m.initial)),"cost":0}
        fake["minimax_cost"]=0
        with self.assertRaisesRegex(ValueError,"Unsafe repair effect"):
            verify_policy(m,fake)
        fake=copy.deepcopy(cert)
        fake["root"]["branches"]["same"]["repair"]="CONTINUE"
        with self.assertRaisesRegex(ValueError,"Unsafe repair effect"):
            verify_policy(m,fake)

    def test_sound_policy_certificate_can_be_suboptimal_so_need_oracle(self):
        m=examples()["fresh_discriminating_getter"]
        cert=synthesize(m)
        assert cert["minimax_cost"]==2
        fake=copy.deepcopy(cert)
        fake["root"]={"kind":"halt","belief":list(sorted(m.initial)),
                      "cost":m.stop_cost}
        fake["minimax_cost"]=m.stop_cost
        # Deliberately true: soundness alone CANNOT certify optimality.
        self.assertEqual(verify_policy(m,fake)["checked_worst_cost"],m.stop_cost)
        with self.assertRaisesRegex(ValueError,"NOT minimax optimal"):
            verify_optimality(m,fake)

    def test_unknown_or_unattested_read_has_no_authority(self):
        m=examples()["fresh_discriminating_getter"]
        cert=synthesize(m)
        self.assertEqual(request(m,cert,())["request"],"read")
        late=request(m,cert,(("read","good_seen",False),))
        self.assertEqual(late["request"],"halt")
        self.assertFalse(late["model_bound_valid"])
        unknown=request(m,cert,(("read","out_of_contract",True),))
        self.assertEqual(unknown["request"],"halt")
        self.assertFalse(unknown["model_bound_valid"])
        valid=request(m,cert,(("read","good_seen",True),))
        self.assertEqual(valid["request"],"authorize")
        self.assertEqual(valid["repair"],"GO")

    def test_model_hash_detects_changed_getter_capability(self):
        m=examples()["fresh_discriminating_getter"]
        cert=synthesize(m)
        altered=examples()["unattested_getter"]
        self.assertNotEqual(model_hash(m),model_hash(altered))
        with self.assertRaisesRegex(ValueError,"provenance"):
            verify_policy(altered,cert)

    def test_invalid_partial_read_or_missing_effect_map_refused(self):
        m=examples()["aliased_getter"]
        bad=Contract(m.initial,m.goals,m.forbidden,m.probes,m.repair_effects,
                     {"good":("same",)},m.read_atomic_and_fresh,
                     m.read_cost,m.stop_cost,m.horizon)
        with self.assertRaisesRegex(ValueError,"state"):
            validate(bad)
        bad_effects={k:dict(v) for k,v in m.repair_effects.items()}
        del bad_effects["GO"]["held"]
        bad=Contract(m.initial,m.goals,m.forbidden,m.probes,bad_effects,
                     m.read_support,True,m.read_cost,m.stop_cost,m.horizon)
        with self.assertRaisesRegex(ValueError,"repair effect"):
            validate(bad)

    def test_exact_oracle_fails_closed_when_resource_cap_too_small(self):
        m=intervention_model()
        cert=synthesize(m)
        with self.assertRaisesRegex(ValueError,"state cap exceeded"):
            verify_optimality(m,cert,max_oracle_nodes=1)

    def test_randomized_80_contracts_have_independent_global_optimality(self):
        rng=random.Random(20261010)
        for i in range(80):
            names=tuple("abc"[:rng.randint(2,3)])
            goal="goal";bad="bad";states=names+(goal,bad)
            effects={}
            for action in ("left","right"):
                effects[action]={s:(rng.choice(states),) if s!=goal else (goal,)
                                 for s in states}
            reads={s:(rng.choice(("x","y")),) for s in states}
            probes=[]
            for k in range(rng.randint(0,3)):
                trans={}
                for s in states:
                    options={(rng.choice(("p","q")),rng.choice(states))
                             for _ in range(rng.randint(1,3))}
                    trans[s]=tuple(sorted(options))
                probes.append(Action(f"p{k}",rng.randint(1,3),trans))
            m=Contract(names,(goal,),(bad,),tuple(probes),effects,reads,
                       rng.choice((True,False)),rng.randint(1,5),
                       rng.randint(5,11),rng.randint(0,3))
            cert=synthesize(m)
            sound=verify_policy(m,cert)
            optimum=verify_optimality(m,cert)
            self.assertEqual(sound["checked_worst_cost"],optimum["optimal_cost"],i)
            self.assertTrue(optimum["exact_independent_oracle_optimal"])


if __name__=="__main__":
    unittest.main()

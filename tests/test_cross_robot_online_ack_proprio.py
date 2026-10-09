"""Pure causal decision checks, not fabricated physics outcomes."""
import unittest

from research.cross_robot_online_proprio_classifier import train,decide

def synthetic_cal(robot="panda"):
    return [dict(robot=robot,seed=i,truth=t,
                 delta_public_xyz=[0.003*i + (0.045 if t=="applied" else 0.),-0.002,0.001])
            for i in range(8) for t in ("applied","held")]

class OnlineAckProprioPureUnit(unittest.TestCase):
    def test_no_hidden_target_getter_and_unique_applied(self):
        m=train(synthetic_cal(),"panda")
        x=decide([0.054,-0.002,0.001],m)
        self.assertEqual(x["label"],"applied")
        self.assertEqual(x["private_target_getter_calls_at_decision"],0)

    def test_held_uses_only_public_xyz(self):
        m=train(synthetic_cal(),"panda")
        x=decide([0.010,-0.002,0.001],m)
        self.assertEqual(x["label"],"held")

    def test_both_compatible_abstains(self):
        records=synthetic_cal()
        # Model's support overlap heavily after deliberately inflating prior
        # public motion variability. Do not force a guessed ACK label.
        for r in records:
            r["delta_public_xyz"][0] += 0.2*r["seed"]
        m=train(records,"panda")
        x=decide([m["class_models"]["held"]["mean_public_motion_m"][0],
                  -0.002,0.001],m)
        self.assertIsNone(x["label"])

    def test_none_compatible_abstains(self):
        m=train(synthetic_cal(),"panda")
        self.assertIsNone(decide([100.,100.,100.],m)["label"])

    def test_not_hardware_certified(self):
        m=train(synthetic_cal(),"panda")
        self.assertIs(m["not_a_safety_certificate"],True)

    def test_wrong_robot_training_refused(self):
        with self.assertRaises(ValueError):
            train(synthetic_cal("xarm6_robotiq"),"panda")

    def test_missing_or_duplicate_training_seed_refused(self):
        r=synthetic_cal()
        with self.assertRaises(ValueError):
            train(r[:-1],"panda")
        r[-1]=r[-2]
        with self.assertRaises(ValueError):
            train(r,"panda")

    def test_mutated_envelope_margin_refused(self):
        m=train(synthetic_cal(),"panda")
        m["radius_margin_m"]=0.2
        with self.assertRaises(ValueError):
            decide([0.05,0.,0.],m)

    def test_corrupt_nonfinite_input_refused(self):
        m=train(synthetic_cal(),"panda")
        with self.assertRaises(ValueError):
            decide([float("nan"),0.,0.],m)
        with self.assertRaises(ValueError):
            decide([0.,0.],m)

    def test_training_digest_changes_on_content_mutation(self):
        a=synthetic_cal()
        b=synthetic_cal()
        b[0]["delta_public_xyz"][0] += 0.001
        self.assertNotEqual(train(a,"panda")["training_sha256"],
                            train(b,"panda")["training_sha256"])

if __name__=="__main__":unittest.main()

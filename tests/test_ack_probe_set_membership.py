"""Adversarial, zero-dependency source tests for declared-response observability."""
import random
import unittest

from research.ack_probe_set_membership import (
    Decision, ProbeEvidence, distinguish_history,
)


def sample(*,before=(0,0,0),observed=(0.05,0,0),held=(0,0,0),
           applied=(0.1,0,0),alpha=(0.4,0.6),error=0.001,
           trusted=True,zero_command=True):
    return ProbeEvidence(before,observed,applied,held,alpha[0],alpha[1],
                         error,trusted,zero_command)


class ResponseCertificateTests(unittest.TestCase):
    def test_applied_identified_from_public_achieved_motion(self):
        z=distinguish_history(sample())
        self.assertEqual(z.decision,Decision.APPLIED)
        self.assertTrue(z.may_select_history)
        self.assertGreater(z.identification_margin_m,0.02)

    def test_held_identified_from_public_achieved_motion(self):
        z=distinguish_history(sample(observed=(0,0,0)))
        self.assertEqual(z.decision,Decision.HELD)

    def test_overlap_means_must_abstain(self):
        z=distinguish_history(sample(
            observed=(0.001,0,0),held=(0,0,0),applied=(0.003,0,0),
            alpha=(0.2,0.8),error=0.003))
        self.assertEqual(z.decision,Decision.ABSTAIN_OVERLAP)
        self.assertFalse(z.may_select_history)

    def test_equal_histories_cannot_be_distinguished(self):
        z=distinguish_history(sample(held=(.1,0,0),applied=(.1,0,0)))
        self.assertEqual(z.decision,Decision.ABSTAIN_OVERLAP)

    def test_model_falsification_does_not_force_choice(self):
        z=distinguish_history(sample(observed=(2,0,0)))
        self.assertEqual(z.decision,Decision.REFUSE_MODEL_FALSIFIED)
        self.assertFalse(z.may_select_history)

    def test_no_calibration_attestation_fails_closed(self):
        z=distinguish_history(sample(trusted=False))
        self.assertEqual(z.decision,Decision.REFUSE_UNATTESTED_DYNAMICS)

    def test_no_confirmed_zero_delta_fails_closed(self):
        z=distinguish_history(sample(zero_command=False))
        self.assertEqual(z.decision,Decision.REFUSE_UNATTESTED_DYNAMICS)

    def test_bad_alpha_or_noise_not_silent(self):
        for alpha in [(-.1,.5),(.9,.5),(.1,1.5)]:
            with self.assertRaises(ValueError):
                distinguish_history(sample(alpha=alpha))
        for noise in [-.1,.26,float("nan")]:
            with self.assertRaises(ValueError):
                distinguish_history(sample(error=noise))

    def test_untrusted_inf_pose_is_not_a_valid_certificate(self):
        with self.assertRaises(ValueError):
            distinguish_history(sample(held=(float("inf"),0,0)))

    def test_interval_endpoint_inclusive(self):
        for a in (.4,.6):
            z=distinguish_history(sample(observed=(.1*a,0,0),error=0.))
            self.assertEqual(z.decision,Decision.APPLIED)

    def test_noise_boundary_uses_numeric_guard(self):
        z=distinguish_history(sample(observed=(0.051,0,0),error=.001))
        self.assertEqual(z.decision,Decision.APPLIED)

    def test_one_step_no_movement_does_not_always_imply_held(self):
        # If the independently verified alpha interval includes 0, both
        # target hypotheses can produce exactly zero response. Never guess.
        z=distinguish_history(sample(observed=(0,0,0),
                      alpha=(0.,.6),error=0.))
        self.assertEqual(z.decision,Decision.ABSTAIN_OVERLAP)

    def test_1200_true_model_instances_never_eliminate_ground_truth(self):
        # Deterministic pre-chosen synthetic families, no result tuning.
        rng=random.Random(440)
        decisions=0
        for i in range(1200):
            x=[rng.uniform(-.5,.5) for _ in range(3)]
            h=[x[j]+rng.uniform(-.08,.08) for j in range(3)]
            a=[x[j]+rng.uniform(-.08,.08) for j in range(3)]
            truth="applied" if i%2 else "held"
            target=a if truth=="applied" else h
            lo=rng.uniform(0.05,0.4)
            hi=rng.uniform(0.6,1.)
            alpha=rng.uniform(lo,hi)
            eps=0.0015
            # Physically admissible disturbance in [-eps/sqrt(3),eps/sqrt(3)]^3.
            y=[x[j]+alpha*(target[j]-x[j])+rng.uniform(-eps/1.7321,eps/1.7321)
               for j in range(3)]
            z=distinguish_history(sample(
                before=x,observed=y,held=h,applied=a,
                alpha=(lo,hi),error=eps))
            self.assertNotEqual(z.decision,Decision.REFUSE_MODEL_FALSIFIED)
            self.assertNotEqual(
                z.decision, Decision.HELD if truth=="applied" else Decision.APPLIED
            )
            decisions+=int(z.may_select_history)
        self.assertGreater(decisions,0)

    def test_response_assumptions_must_be_declared_per_probe(self):
        z=distinguish_history(sample(trusted=False,observed=(.05,0,0)))
        self.assertFalse(z.may_select_history)
        self.assertEqual(z.applied_residual_m,float("inf"))


if __name__=="__main__":
    unittest.main()

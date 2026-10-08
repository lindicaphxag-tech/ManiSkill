"""Falsification-oriented, dependency-free tests of memory-uncertainty transport.

Synthetic mathematical tests, NOT real robot/simulator effectiveness claims.
"""
import math
import random
import unittest

from research.latent_target_memory_cert import (
    TransportRequest, Verdict, certify_box_memory_transport,
    unavoidable_indistinguishable_history_error,
)


def req(
    d=(0.1,), ml=(0.0,), mh=(0.0,), al=(-1.0,), ah=(1.0,),
    eps=0.001, attested=True, age=0, maximum_age=0, verified=True,
):
    return TransportRequest(
        desired_target=d, memory_lower=ml, memory_upper=mh,
        command_lower=al, command_upper=ah, error_budget=eps,
        trusted_memory_attestation=attested, memory_age_steps=age,
        max_memory_age_steps=maximum_age,
        additive_controller_contract_verified=verified,
    )


class TestLatentMemoryTransport(unittest.TestCase):
    def test_fresh_exact_memory_recovers_existing_controller_inversion(self):
        result = certify_box_memory_transport(req())
        self.assertTrue(result.may_dispatch)
        self.assertEqual(result.verdict, Verdict.AUTHORIZE_COMMANDED_TARGET)
        self.assertAlmostEqual(result.command[0], 0.1)
        self.assertAlmostEqual(result.optimal_worst_case_setpoint_error, 0.0)

    def test_identical_observations_multiple_hidden_targets_obstruct_exact(self):
        # Same observed achieved pose x and same desired source target d,
        # but unseen previous target m=0 or m=.2. No common action can
        # command the same target to better than .1 under both histories.
        self.assertAlmostEqual(
            unavoidable_indistinguishable_history_error((0.0,), (0.2,)), 0.1
        )
        result = certify_box_memory_transport(req(
            d=(0.1,), ml=(0.0,), mh=(0.2,), eps=0.05
        ))
        self.assertEqual(result.verdict, Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE)
        self.assertIsNone(result.command)
        self.assertAlmostEqual(result.optimal_worst_case_setpoint_error, 0.1)
        self.assertAlmostEqual(result.unobservable_memory_radius, 0.1)

    def test_interval_information_allows_robust_approximation_when_budget_big(self):
        r=certify_box_memory_transport(req(
            d=(0.3,), ml=(0.0,), mh=(0.2,), eps=0.11
        ))
        self.assertTrue(r.may_dispatch)
        self.assertAlmostEqual(r.command[0], 0.2)
        self.assertAlmostEqual(r.optimal_worst_case_setpoint_error, 0.1)

    def test_saturation_adds_unavoidable_error_even_when_memory_known(self):
        p = req(d=(1.0,), ml=(0.5,), mh=(0.5,),
                al=(-0.2,), ah=(0.2,), eps=0.2)
        r=certify_box_memory_transport(p)
        self.assertFalse(r.may_dispatch)
        self.assertAlmostEqual(r.optimal_worst_case_setpoint_error, 0.3)
        self.assertAlmostEqual(r.saturation_excess[0], 0.3)
        q=certify_box_memory_transport(req(d=(1.0,), ml=(0.5,), mh=(0.5,),
                al=(-0.2,), ah=(0.2,), eps=0.31))
        self.assertTrue(q.may_dispatch)
        self.assertAlmostEqual(q.command[0], 0.2)

    def test_noncentered_target_native_physical_command_limits(self):
        r=certify_box_memory_transport(req(
            d=(0.0,), ml=(-0.5,), mh=(-0.5,),
            al=(0.1,), ah=(0.2,), eps=0.4
        ))
        self.assertTrue(r.may_dispatch)
        self.assertEqual(r.command, (0.2,))
        self.assertAlmostEqual(r.optimal_worst_case_setpoint_error, 0.3)

    def test_three_axis_supremum_and_adversarial_endpoint(self):
        r=certify_box_memory_transport(req(
            d=(0.0, 0.1, -0.2),
            ml=(-0.01, -0.05, 0.1), mh=(0.01, 0.15, 0.3),
            al=(-1., -1., -0.1), ah=(1.,1.,0.1), eps=1.
        ))
        self.assertTrue(r.may_dispatch)
        self.assertEqual(r.active_dimension, 2)
        self.assertAlmostEqual(r.optimal_worst_case_setpoint_error, 0.4)
        self.assertAlmostEqual(
            abs(r.adversarial_memory_endpoint +
                r.command[r.active_dimension] -
                (-0.2)), r.optimal_worst_case_setpoint_error
        )

    def test_missing_attested_memory_cannot_authorize(self):
        r=certify_box_memory_transport(req(attested=False, eps=1.))
        self.assertEqual(r.verdict,Verdict.REFUSE_UNTRUSTED_MEMORY)
        self.assertIsNone(r.command)

    def test_stale_memory_cannot_authorize(self):
        r=certify_box_memory_transport(req(age=1,maximum_age=0,eps=1.))
        self.assertEqual(r.verdict,Verdict.REFUSE_STALE_MEMORY)

    def test_unknown_native_controller_contract_cannot_authorize(self):
        r=certify_box_memory_transport(req(verified=False,eps=1.))
        self.assertEqual(r.verdict,Verdict.REFUSE_UNVERIFIED_CONTROLLER)

    def test_uncertain_memory_information_cannot_shrink_by_open_loop_control(self):
        width_before=0.32
        # A known issued action translates both plausible latent targets
        # by the same increment and therefore cannot identify either one.
        a,b=0.05,0.37
        command=-0.1
        self.assertAlmostEqual(
            unavoidable_indistinguishable_history_error(
                (a,), (b,)),
            unavoidable_indistinguishable_history_error(
                (a+command,), (b+command,))
        )
        self.assertAlmostEqual(b-a,width_before)

    def test_numpy_like_sequences_with_ambiguous_truth_are_supported(self):
        # Regression: NumPy arrays raise when converted to a scalar bool;
        # the native robot control path supplies exactly this shape.
        class NumpyLike:
            def __init__(self, entries):
                self.entries = tuple(entries)
            def __len__(self):
                return len(self.entries)
            def __iter__(self):
                return iter(self.entries)
            def __bool__(self):
                raise ValueError("Truth value of an array is ambiguous")
        width = unavoidable_indistinguishable_history_error(
            NumpyLike((0., 0., 0.)), NumpyLike((.02, 0., 0.))
        )
        self.assertAlmostEqual(width, 0.01)
        result = certify_box_memory_transport(req(
            d=NumpyLike((0.1,)),
            ml=NumpyLike((0.,)), mh=NumpyLike((.2,)),
            al=NumpyLike((-1.,)), ah=NumpyLike((1.,)),
            eps=.11
        ))
        self.assertTrue(result.may_dispatch)
        self.assertAlmostEqual(result.optimal_worst_case_setpoint_error, .1)

    def test_numerical_boundary_fails_closed(self):
        r=certify_box_memory_transport(req(eps=0.0))
        self.assertFalse(r.may_dispatch)
        self.assertEqual(r.verdict,Verdict.REFUSE_GEOMETRICALLY_IMPOSSIBLE)

    def test_reject_invalid_bounds_and_nan_injection(self):
        cases=[
            req(ml=(0.2,),mh=(0.1,)),
            req(al=(1.,),ah=(-1.,)),
            req(d=(math.nan,)),
            req(d=(math.inf,)),
            req(d=(0.,0.)),
            req(eps=-1.),
            req(eps=math.nan),
            req(age=-1),
            req(maximum_age=-1),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                certify_box_memory_transport(case)

    def test_random_optimality_against_action_grid_and_all_memory_corners(self):
        # 320 randomized independent physical command boxes and memory
        # intervals; verify every enumerated feasible competing command
        # has worst-case error >= the proposed lower bound.
        gen=random.Random(20261009)
        for _ in range(320):
            ml, mh=sorted((gen.uniform(-1,1), gen.uniform(-1,1)))
            cl, ch=sorted((gen.uniform(-1,1), gen.uniform(-1,1)))
            d=gen.uniform(-1.2,1.2)
            r=certify_box_memory_transport(req(
                d=(d,),ml=(ml,),mh=(mh,),al=(cl,),ah=(ch,),eps=5.,
            ))
            self.assertTrue(r.may_dispatch)
            actual=max(abs(ml+r.command[0]-d),abs(mh+r.command[0]-d))
            self.assertAlmostEqual(actual,r.optimal_worst_case_setpoint_error,places=10)
            for k in range(41):
                u=cl+(ch-cl)*k/40
                competitor=max(abs(ml+u-d),abs(mh+u-d))
                self.assertGreaterEqual(
                    competitor+1e-9,r.optimal_worst_case_setpoint_error
                )

    def test_monotonic_memory_uncertainty_increases_minimax_bound(self):
        p=certify_box_memory_transport(req(
            d=(0.8,),ml=(0.2,),mh=(0.4,),
            al=(-0.2,),ah=(0.3,),eps=5.
        ))
        q=certify_box_memory_transport(req(
            d=(0.8,),ml=(0.0,),mh=(0.6,),
            al=(-0.2,),ah=(0.3,),eps=5.
        ))
        self.assertGreaterEqual(
            q.optimal_worst_case_setpoint_error,
            p.optimal_worst_case_setpoint_error
        )


if __name__=="__main__":
    unittest.main()

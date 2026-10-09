"""Probe selection must refuse observationally equivalent measured target histories."""
import unittest
from dataclasses import replace

from research.audit_counterfactual_execution_observability import checked_sources,DEFAULT_SOURCE
from research.conditional_probe_or_read import (
    ResponseBall,ProbeOption,choose_probe_or_read
)

HISTORY=("applied_held","applied_applied")
def option(name="probe",means=((0.,0.,0.),(.020,0.,0.)),radii=(.001,.001),
           valid=True,source=True,coverage=True,cal=True,cost=.1,regret=.002):
    return ProbeOption(
        name,(0.02,0.,0.,0.,0.,0.),valid,source,coverage,cal,
        tuple(ResponseBall(h,tuple(cent),rad)
              for h,cent,rad in zip(HISTORY,means,radii)),
        .003,.002,regret,cost,.02
    )
def decide(*options):
    return choose_probe_or_read(
        histories=HISTORY,proposed_probes=tuple(options),
        authoritative_read_cost=.5,
        sensor_separation_margin_m=.001,
        maximum_target_position_error_m=.005,
        maximum_target_orientation_error_rad=.005,
        maximum_incremental_task_regret=.005
    )

class GenuineObservabilityDrivenProbe(unittest.TestCase):
    def test_source_physx_identical_public_xyz_requires_read_or_different_probe(self):
        rows,_=checked_sources(DEFAULT_SOURCE)
        for seed in (2110003,2110004,2110012):
            x=rows[("pull_cube",seed)][1]["public_t3_evidence"]
            y=rows[("pull_cube",seed)][3]["public_t3_evidence"]
            self.assertEqual(x["before_xyz"]+x["after_xyz"],y["before_xyz"]+y["after_xyz"])
            still=option("actual_zero_probe",means=(tuple(x["after_xyz"]),tuple(y["after_xyz"])),
                         radii=(0.,0.),cost=0.)
            ans=decide(still)
            self.assertEqual(ans.mode,"READ_TRUE_TARGET")
            self.assertIsNone(ans.candidate_probe_name)

    def test_only_discriminating_and_cheaper_native_probe_selected(self):
        zero=option("zero",means=((0,0,0),(0,0,0)),cost=0.)
        good=option("genuine_separation",cost=.14)
        expensive=option("expensive",cost=.49)
        ans=decide(zero,expensive,good)
        self.assertEqual(ans.mode,"TAKE_CONDITIONAL_PROBE")
        self.assertEqual(ans.candidate_probe_name,"genuine_separation")
        self.assertGreater(ans.worst_pairwise_response_separation_lower_m,.015)

    def test_stale_or_untrusted_counterfactual_model_fails_closed(self):
        good=option()
        for bad in (replace(good, trusted_response_model_provenance=False),
                    replace(good, source_distribution_coverage_attested=False),
                    replace(good, trusted_calibration_validity=False),
                    replace(good, action_chart_valid_for_all_histories=False)):
            self.assertEqual(decide(bad).mode,"READ_TRUE_TARGET")

    def test_too_large_contact_and_target_error_cannot_buy_speculative_information(self):
        good=option()
        self.assertEqual(decide(replace(good, conservative_task_regret_bound=.2)).mode,"READ_TRUE_TARGET")
        self.assertEqual(decide(replace(good, maximum_native_target_position_error_m=.1)).mode,"READ_TRUE_TARGET")
        self.assertEqual(decide(replace(good, maximum_native_target_orientation_error_rad=.1)).mode,"READ_TRUE_TARGET")

    def test_overlapping_uncertain_response_sets_are_not_discriminating(self):
        x=option(means=((0,0,0),(.008,0,0)),radii=(.005,.005))
        self.assertEqual(decide(x).mode,"READ_TRUE_TARGET")

    def test_equal_or_greater_query_cost_chooses_authoritative_getter(self):
        self.assertEqual(decide(option(cost=.49)).mode,"READ_TRUE_TARGET")
        self.assertEqual(decide(option(cost=.5)).mode,"READ_TRUE_TARGET")

    def test_missing_history_or_corrupt_prediction_never_chooses_probe(self):
        good=option()
        dup=replace(good,calibrated_response_balls=(good.calibrated_response_balls[0],)*2)
        miss=replace(good,calibrated_response_balls=(good.calibrated_response_balls[0],))
        nan=replace(good,calibrated_response_balls=(
            ResponseBall("applied_held",(float("nan"),0.,0.),.001),
            good.calibrated_response_balls[1]))
        for p in (dup,miss,nan):
            self.assertEqual(decide(p).mode,"READ_TRUE_TARGET")

    def test_invalid_nonunique_id_rejected(self):
        with self.assertRaises(ValueError):
            choose_probe_or_read(
                histories=("same","same"),proposed_probes=(option(),),
                authoritative_read_cost=.5,sensor_separation_margin_m=.001,
                maximum_target_position_error_m=.005,
                maximum_target_orientation_error_rad=.005,
                maximum_incremental_task_regret=.005)
if __name__=="__main__": unittest.main()

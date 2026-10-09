"""Adversarial prospective-read contract for source-frozen learned meta-policy."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path

from research.learn_counterfactual_task_read_policy_from_real_physx import (
    SOURCE_GIT_BLOB,public_reset_features,groups,frozen_source,
    learn,leave_one_RESET_cluster_out,outcome_for_route
)

class TestCounterfactualLearnedResetSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=frozen_source()
        cls.clusters=groups(cls.original)

    def test_exact_original_first_physics_32_clusters_with_4_truths_each(self):
        self.assertEqual(len(self.clusters),32)
        self.assertEqual(sum(len(c.truth_rows) for c in self.clusters),128)
        self.assertEqual(self.original["separate_physx_worlds"],1152)
        self.assertEqual(self.original["primary_outcomes"]["public"]["official_task_success"],116)
        self.assertEqual(self.original["primary_outcomes"]["strong_task"]["official_task_success"],108)
        self.assertTrue(all(len(c.public_initial_features)==10 for c in self.clusters))
        self.assertTrue(all(len({r["truth"] for r in c.truth_rows})==4 for c in self.clusters))

    def test_original_counterfactual_rewards_sum_to_actual_physics(self):
        pub=[outcome_for_route(c,"PUBLIC") for c in self.clusters]
        old=[outcome_for_route(c,"STRONG_TASK") for c in self.clusters]
        self.assertEqual(sum(x["success"] for x in pub),116)
        self.assertEqual(sum(x["success"] for x in old),108)
        self.assertEqual(sum(x["reads"] for x in pub),91)
        self.assertEqual(sum(x["reads"] for x in old),109)
        self.assertEqual(sum(x["public_xyz_events_if_chosen"] for x in pub),252)

    def test_outcome_and_true_ack_never_runtime_features(self):
        r=self.clusters[0].truth_rows[0]
        f=public_reset_features(r["task"],r["initial_source_public_observation_f32"],
                                 r["initial_source_ee_pose7_xyz_xyzw"])
        self.assertEqual(f,self.clusters[0].public_initial_features)
        for bad in [[],r["initial_source_public_observation_f32"]+[3]]:
            with self.assertRaises(ValueError):
                public_reset_features(r["task"],bad,r["initial_source_ee_pose7_xyz_xyzw"])

    def test_duplicate_and_missing_counterfactual_truths_refuse(self):
        d=copy.deepcopy(self.original)
        d["all_source_rows_retained"].pop()
        with self.assertRaises(ValueError):
            groups(d)
        d=copy.deepcopy(self.original)
        r=copy.deepcopy(d["all_source_rows_retained"][0])
        d["all_source_rows_retained"][0]["truth"]="held/held"
        d["all_source_rows_retained"][1]=r
        with self.assertRaises(ValueError):
            groups(d)

    def test_32_independent_groups_full_fit_reproducible(self):
        a=learn(self.clusters)
        b=learn(self.clusters)
        self.assertEqual(a,b)
        self.assertEqual(len(a.training_clusters),32)
        self.assertEqual(len(a.weights),11)
        self.assertTrue(all(abs(x)<100 for x in a.weights))
        held=self.clusters[0].truth_rows[0]
        self.assertIn(a.route(held["task"],held["initial_source_public_observation_f32"],
                               held["initial_source_ee_pose7_xyz_xyzw"]),
                      ("PUBLIC","STRONG_TASK"))

    def test_one_original_seed_cluster_left_out_of_its_own_training(self):
        held=self.clusters[3]
        training=tuple(c for c in self.clusters if c.seed!=held.seed or c.task!=held.task)
        model=learn(training)
        self.assertEqual(len(model.training_clusters),31)
        self.assertNotIn(f"{held.task}:{held.seed}",model.training_clusters)
        row=held.truth_rows[0]
        route=model.route(held.task,row["initial_source_public_observation_f32"],
                                row["initial_source_ee_pose7_xyz_xyzw"])
        # Two identical pre-ACK inputs must have EXACT SAME route regardless of
        # any changed audit-only outcome label; the decision only sees input.
        swapped=dict(row,success_once={"made_up_outcome":True})
        self.assertEqual(route,model.route(held.task,swapped["initial_source_public_observation_f32"],
                                             swapped["initial_source_ee_pose7_xyz_xyzw"]))

    def test_cross_validation_is_development_not_independent_confirmation(self):
        r=leave_one_RESET_cluster_out(self.original)
        self.assertTrue(r["future_model_training_and_test_not_yet_EXECUTED"])
        self.assertEqual(len(r["leave_one_cluster_out_development"]["heldout_choices"]),32)
        self.assertEqual(r["leave_one_cluster_out_development"]["strong"]["official_success"],108)
        self.assertEqual(r["leave_one_cluster_out_development"]["always_public"]["official_success"],116)
        self.assertEqual(sum(r["leave_one_cluster_out_development"]["choice_counts"].values()),32)
        self.assertEqual(len(r["full_fitted_model_for_subsequent_DISJOINT_future_trial"]["training_clusters"]),32)

    def test_cost_and_route_not_allowed_to_change_without_prospective_retraining(self):
        with self.assertRaises(ValueError):
            groups(self.original,read_cost=-.01)
        with self.assertRaises(ValueError):
            learn(self.clusters,ridge_lambda=-1)
        with self.assertRaises(ValueError):
            outcome_for_route(self.clusters[0],"RETROSPECTIVELY_BEST")

if __name__=="__main__":
    unittest.main()

"""Evidence-frozen, CPU-only paired exact statistic and readback accounting."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest
from copy import deepcopy

from research.frozen_policy_transfer.review.paired_impact_statistics import (
    audit_record, exact_paired_binary
)

ORIGINAL=Path("research/frozen_policy_transfer/evidence/unknown_ack_bounded_query_16/original_ack_bounded_query_16_aggregate.json")
SOURCE_SHA256="1246afcd6a1b88922a5d1e9f0c73ebb858179a09770d5c2d46032763591955c8"


class TestPairedSourceEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ORIGINAL.read_bytes()
        assert hashlib.sha256(source).hexdigest()==SOURCE_SHA256, "Frozen original source changed"
        cls.data=json.loads(source)

    def test_exact_original_16state_mechanism_without_pseudoreplication(self):
        record=audit_record(self.data)
        self.assertEqual(record["n_distinct_original_task_seeds"],16)
        self.assertEqual(record["n_original_frozen_policies"],2)
        arms="fault_robust_two_history_without_query_vs_fault_optimistic_unverified_ack"
        found=record["paired_comparisons"][arms]
        self.assertEqual(found["a_success"],11)
        self.assertEqual(found["b_success"],6)
        self.assertEqual((found["a_only"],found["b_only"]),(5,0))
        self.assertAlmostEqual(found["two_sided_exact_mcnemar_p_exploratory"],.0625)
        self.assertFalse(record["noninferiority_statistically_established"])

    def test_original_selective_query_ties_aggregate_but_not_per_state(self):
        report=audit_record(self.data)
        key="fault_robust_then_single_privileged_query_vs_fault_always_single_privileged_query"
        d=report["paired_comparisons"][key]
        self.assertEqual((d["a_success"],d["b_success"]),(15,15))
        self.assertEqual((d["a_only"],d["b_only"]),(1,1))
        self.assertEqual(d["two_sided_exact_mcnemar_p_exploratory"],1.0)
        self.assertEqual(report["privileged_target_decision_reads_selective"],4)
        self.assertEqual(report["privileged_target_decision_reads_mandatory"],16)
        self.assertAlmostEqual(report["decision_read_fraction_saved"],.75)
        self.assertTrue(report["audit_only_privileged_readbacks_not_counted_as_free_hardware_measurement"])

    def test_bad_denominator_rejected(self):
        record=deepcopy(self.data)
        record["results"]["pull_cube"]["complete_original_rows"].pop()
        with self.assertRaises(ValueError):
            audit_record(record)

    def test_false_zero_cost_oracle_rejected(self):
        record=deepcopy(self.data)
        record["results"]["stack_cube"]["complete_original_rows"][0][
            "privileged_target_readback_decision_count"]["fault_oracle_private_target"]=0
        with self.assertRaises(ValueError):
            audit_record(record)

    def test_nonboolean_success_rejected(self):
        record=deepcopy(self.data)
        record["results"]["pull_cube"]["complete_original_rows"][0][
            "success_once"]["fault_robust_two_history_without_query"]=1
        with self.assertRaises(ValueError):
            audit_record(record)

    def test_discordance_sign_conventions(self):
        a=[True,True,False,False]
        b=[False,True,True,False]
        d=exact_paired_binary(a,b)
        self.assertEqual((d["a_only"],d["b_only"],d["binary_agreement"]),(1,1,2))
        self.assertEqual(d["two_sided_exact_mcnemar_p_exploratory"],1.0)


if __name__=="__main__":
    unittest.main()

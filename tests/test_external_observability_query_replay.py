"""Negative controls for investigator-selected PhysX artifact provenance.

These synthetic fixtures test the *auditor*, never claim to reproduce PhysX.
The actual runner is exercised separately on GitHub official native PhysX.
"""
import copy
import unittest
from research.external_observability_query_replay import (
    validate_inputs,validate_original,ARMS)
from research.empirical_probe_response_classifier import classify_empirical_public_response


def fixture():
    task="pull_cube"
    fault="applied_no_ack"
    seeds=[230001]
    cls=classify_empirical_public_response(
        (0,0,0),(.04,0,0),(0,0,0),(.1,0,0),task=task)
    assert cls["label"]=="applied"
    row={
      "task":"PullCube-v1","seed":230001,
      "unknown_ack_truth":fault,
      "success_once":{a:True for a in ARMS},
      "fault_reached":{a:True for a in ARMS[1:]},
      "probe_reached":{a:True for a in ARMS},
      "private_memory_reads_during_action_decision":{
        a:(1 if a=="privileged_once_after_probe" else 0) for a in ARMS},
      "hybrid_classifier":cls,
      "hybrid_wrong_authorization":False,
      "probe_positions":{
        "achieved_probe_then_query":{
          "achieved_pre_probe_xyz":[0,0,0],
          "achieved_post_probe_xyz":[.04,0,0]}},
      "hybrid_candidate_goal_positions":{
        "held":[0,0,0],"applied":[.1,0,0]},
      "projections":{},
    }
    return dict(
      schema="observability_gated_selective_query_fresh32_physx_v1",
      task="PullCube-v1",truth=fault,seeds=seeds,
      real_physx=True,training_performed=False,
      published_revision="6bdeb28810330ab5425ccd629bb561c58a56ff85",
      third_party_checkpoint_sha256="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
      rows=[row],success_count={a:1 for a in ARMS},
      hybrid_classification_covered=1,hybrid_wrong_history_authorizations=0,
      selective_privileged_queries=0)


class ExternalAuditTests(unittest.TestCase):
    def test_accept_new_seed_one(self):
        self.assertEqual(validate_inputs("pull_cube","applied_no_ack",230001,1),[230001])
        self.assertEqual(validate_inputs("stack_cube","neutral_arm_delta_no_ack",280000,4),
                         [280000,280001,280002,280003])

    def test_reject_seen_reset_seed(self):
        with self.assertRaises(ValueError):
            validate_inputs("pull_cube","applied_no_ack",190101,8)

    def test_reject_invalid_fault(self):
        with self.assertRaises(ValueError):
            validate_inputs("pull_cube","network_delayed_ack",230001,8)

    def test_reject_negative_and_nonint(self):
        for v in (-1,230000,230001.0,2147483648):
            with self.subTest(v=v),self.assertRaises(ValueError):
                validate_inputs("pull_cube","applied_no_ack",v,1)

    def test_reject_wrong_denominator(self):
        for count in (0,2,3,5,7,9,1.0):
            with self.subTest(count=count),self.assertRaises(ValueError):
                validate_inputs("pull_cube","applied_no_ack",230001,count)

    def test_reject_overflow(self):
        with self.assertRaises(ValueError):
            validate_inputs("pull_cube","applied_no_ack",2147483000,8)

    def test_valid_source_record(self):
        x=validate_original(fixture(),"pull_cube","applied_no_ack",[230001])
        self.assertEqual(x["full_denominator"],1)
        self.assertEqual(x["privileged_target_reads"]["achieved_probe_then_query"],0)
        self.assertEqual(x["public_unique_history_labels"],1)
        self.assertEqual(x["public_wrong_confident_labels"],0)

    def test_no_false_privileged_read_authorized(self):
        raw=fixture()
        raw["rows"][0]["private_memory_reads_during_action_decision"]["achieved_probe_then_query"]=1
        raw["selective_privileged_queries"]=1
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_label_error_must_be_disclosed(self):
        raw=fixture()
        raw["rows"][0]["hybrid_wrong_authorization"]=True
        raw["hybrid_wrong_history_authorizations"]=1
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_no_private_memory_alias(self):
        raw=fixture()
        raw["rows"][0]["private_memory_reads_during_action_decision"]["blind_probe_optimistic"]=1
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_forged_classification_rejected(self):
        raw=fixture()
        raw["rows"][0]["hybrid_classifier"]["label"]="held"
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_forged_physx_source_denominator_rejected(self):
        raw=fixture()
        raw["seeds"]=[230002]
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_reject_retrained_weights(self):
        raw=fixture()
        raw["training_performed"]=True
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_reject_missing_actual_fault(self):
        raw=fixture()
        del raw["rows"][0]["fault_reached"]["achieved_probe_then_query"]
        with self.assertRaises(ValueError):
            validate_original(raw,"pull_cube","applied_no_ack",[230001])

    def test_refusal_requires_one_authoritative_read(self):
        raw=fixture()
        cls=classify_empirical_public_response(
            (0,0,0),(0,0,0),(0,0,0),(.1,0,0),task="pull_cube")
        assert cls["label"] is None
        row=raw["rows"][0]
        row["hybrid_classifier"]=cls
        row["hybrid_wrong_authorization"]=None
        row["probe_positions"]["achieved_probe_then_query"]["achieved_post_probe_xyz"]=[0,0,0]
        row["private_memory_reads_during_action_decision"]["achieved_probe_then_query"]=1
        raw["hybrid_classification_covered"]=0
        raw["selective_privileged_queries"]=1
        result=validate_original(raw,"pull_cube","applied_no_ack",[230001])
        self.assertEqual(result["privileged_target_reads"]["achieved_probe_then_query"],1)


if __name__=="__main__":
    unittest.main()

"""Adversarial integrity tests for a physically materialized heldout HDF5."""
import copy
import hashlib
import json
import unittest

from research.kaggle_diffusion_policy_peg.audit_factorial_replay import (
    ARMS, verify_execution_binding,
)


def _build_fixture():
    rows=[
        {"source_seed":1000+i,**{name:(i+j)%3!=0 for j,name in enumerate(ARMS)}}
        for i in range(4)
    ]
    doc={"source_seed_matrix":rows}
    indices=list(range(100,104))
    ids=[200,201,202,203]
    seeds=[row["source_seed"] for row in rows]
    proof={
        "selection_verified":True,
        "original_source_episode_indices":indices,
        "original_source_episode_ids":ids,
        "original_source_episode_seeds":seeds,
        "replay_h5_group_count":4,
        "selected_h5_sha256":"a"*64,
        "selected_json_sha256":"b"*64,
    }
    proof["identity_sha256"]=hashlib.sha256(json.dumps({
        "indices":indices,"ids":ids,"seeds":seeds,
        "h5":proof["selected_h5_sha256"],
        "json":proof["selected_json_sha256"],
    },sort_keys=True,separators=(",",":")).encode()).hexdigest()
    execution={
        "status":"passed",
        "source_episode_offset":100,
        "source_episode_indices":indices,
        "factorial_replay":copy.deepcopy(doc),
        "source_materialization":{arm:copy.deepcopy(proof) for arm in ARMS},
    }
    return doc, execution


class BindingTests(unittest.TestCase):
    def test_valid_physical_source_membership(self):
        doc, execution = _build_fixture()
        result=verify_execution_binding(doc,execution,offset=100,count=4)
        self.assertTrue(result["physical_hdf5_cohort_verified"])
        self.assertTrue(result["all_four_arms_bound_to_same_original_episode_seeds"])
        self.assertEqual(len(result["physical_source_identity_sha256_by_arm"]),4)

    def test_wrong_or_rewritten_source_details_fail_closed(self):
        cases=(
            ("original_source_episode_indices",[0,1,2,3]),
            ("original_source_episode_seeds",[0,1,2,3]),
            ("original_source_episode_ids",[200,200,202,203]),
            ("replay_h5_group_count",5),
            ("identity_sha256","0"*64),
            ("selected_h5_sha256","c"*64),
            ("selection_verified",False),
        )
        for field, val in cases:
            with self.subTest(field=field):
                doc, execution = _build_fixture()
                execution["source_materialization"][ARMS[0]][field]=val
                with self.assertRaises(ValueError):
                    verify_execution_binding(doc,execution,offset=100,count=4)

    def test_source_matrix_cannot_be_swapped(self):
        doc, execution=_build_fixture()
        execution["factorial_replay"]={"source_seed_matrix":[]}
        with self.assertRaisesRegex(ValueError,"factorial record"):
            verify_execution_binding(doc,execution,offset=100,count=4)

    def test_each_arm_independently_bound(self):
        doc, execution=_build_fixture()
        del execution["source_materialization"][ARMS[2]]
        with self.assertRaisesRegex(ValueError,"arm-specific"):
            verify_execution_binding(doc,execution,offset=100,count=4)


if __name__=="__main__":
    unittest.main()

"""Synthetic adversarial AUDITOR tests — NOT new native PhysX evidence."""
import json

import pytest

from research.audit_ack_active_native_probe_physx_pilot import (
    PROBES, ROBOTS, TRUTHS, PROTO_BLOB, audit,
)


def fake_original_complete_receipts(tmp_path):
    paths = {}
    for robot, seeds in ROBOTS.items():
        rows = []
        for seed in seeds:
            for truth in TRUTHS:
                for name, action in PROBES.items():
                    # Deliberately synthetic arithmetic-only fixture.
                    # Same common probe shift for both physical histories.
                    after = [(.01 if truth == "applied" else 0)
                             + action[0], action[1], 0]
                    rows.append({
                        "robot": robot, "seed": seed,
                        "truth_score_only": truth, "probe_id": name,
                        "probe_native_six": list(action),
                        "decision_time_privileged_target_reads": 0,
                        "post_action_audit_target_reads": 1,
                        "public_motion_after_true_actuation": True,
                        "no_certified_physical_safety": True,
                        "native_target_recurrence_error_linf_m": 1e-8,
                        "observation_preprobe_xyz": [0, 0, 0],
                        "observation_postprobe_xyz": after,
                    })
        name = f"ack_native_probe_physx_pilot_{robot}.json"
        data = {
            "robot": robot, "protocol_git_blob": PROTO_BLOB,
            "original_unique_reset_clusters": 4,
            "original_native_physx_worlds": 24,
            "rows": rows,
        }
        file = tmp_path / name
        file.write_text(json.dumps(data), encoding="utf-8")
        paths[name] = file
    return paths


def rewrite(path, mutate):
    d = json.loads(path.read_text(encoding="utf-8"))
    mutate(d)
    path.write_text(json.dumps(d), encoding="utf-8")


def test_all_48_fake_condition_receipts_audit_without_false_gain(tmp_path):
    fixtures = fake_original_complete_receipts(tmp_path)
    result = audit(fixtures)
    assert result["native_physx_worlds"] == 48
    assert result["unique_reset_clusters"] == 8
    assert not result["qualifies_for_followup_any_single_probe"]
    assert not result["calibration_independent_response_bounds_proven"]


def test_audit_fails_closed_on_missing_actual_world(tmp_path):
    files = fake_original_complete_receipts(tmp_path)
    rewrite(files["ack_native_probe_physx_pilot_panda.json"],
            lambda d: d["rows"].pop())
    with pytest.raises(ValueError, match="Incomplete"):
        audit(files)


def test_audit_detects_duplicate_condition_not_48_independent_seeds(tmp_path):
    files = fake_original_complete_receipts(tmp_path)
    def modify(d):
        d["rows"][0] = d["rows"][1].copy()
    rewrite(files["ack_native_probe_physx_pilot_panda.json"], modify)
    with pytest.raises(ValueError, match="Duplicate"):
        audit(files)


@pytest.mark.parametrize("field,new,problem", [
    ("probe_native_six",[.99,0,0,0,0,0],"substituted"),
    ("decision_time_privileged_target_reads",1,"privilege"),
    ("native_target_recurrence_error_linf_m",.1,"recurrence"),
    ("observation_postprobe_xyz",[float("nan"),0,0],"Nonfinite"),
])
def test_audit_rejects_source_manipulation(tmp_path, field, new, problem):
    files = fake_original_complete_receipts(tmp_path)
    rewrite(files["ack_native_probe_physx_pilot_panda.json"],
            lambda d: d["rows"][0].__setitem__(field,new))
    with pytest.raises(ValueError, match=problem):
        audit(files)


def test_audit_requires_exact_frozen_protocol_blob(tmp_path):
    files = fake_original_complete_receipts(tmp_path)
    rewrite(files["ack_native_probe_physx_pilot_panda.json"],
            lambda d: d.__setitem__("protocol_git_blob", "wrong"))
    with pytest.raises(ValueError, match="source"):
        audit(files)

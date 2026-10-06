from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


PLUGIN_CORE = (
    Path(__file__).parents[1]
    / "research"
    / "eprc"
    / "lerobot_plugin"
    / "src"
    / "lerobot_processor_eprc"
    / "core.py"
)


def _load_core():
    spec = spec_from_file_location("eprc_plugin_core", PLUGIN_CORE)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _base_evidence():
    return {
        "semantics_known": True,
        "provenance_valid": True,
        "representability_margin": 0.2,
        "canonical_command_error": 0.1,
        "exact_transport_available": False,
        "support_stability": 0.97,
        "held_out_residual": 0.02,
        "transverse_norm": 0.03,
        "certified_repair_radius": 0.05,
        "contract_class": "RELATIONAL_INVARIANT",
        "support_ids": ["a", "b"],
    }


def test_plugin_core_emits_repair_and_binds_provenance():
    core = _load_core()
    evidence = _base_evidence()
    cert = core.compile_evidence(
        evidence,
        provenance_parts=["policy=p", "checkpoint=sha256:x", "trial=1"],
        thresholds=core.Thresholds(),
    )
    assert cert["decision"] == "REPAIR"
    assert len(cert["provenance_digest"]) == 64


def test_plugin_core_fails_closed_on_unrepresentable_command():
    core = _load_core()
    evidence = _base_evidence()
    evidence["representability_margin"] = -0.01
    cert = core.compile_evidence(
        evidence,
        provenance_parts=["policy=p"],
        thresholds=core.Thresholds(),
    )
    assert cert["decision"] == "REJECT"
    assert "cannot represent" in cert["reason"]


def test_plugin_core_rejects_unstable_support_before_repair():
    core = _load_core()
    evidence = _base_evidence()
    evidence["support_stability"] = 0.4
    cert = core.compile_evidence(
        evidence,
        provenance_parts=["policy=p"],
        thresholds=core.Thresholds(),
    )
    assert cert["decision"] == "REJECT"
    assert "unstable" in cert["reason"]

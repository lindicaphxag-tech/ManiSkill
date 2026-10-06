from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from research.eprc.runtime import (
    ContractClass,
    Evidence,
    Thresholds,
    compile_contract,
)


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
    spec = spec_from_file_location("eprc_plugin_core_conformance", PLUGIN_CORE)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dict_to_evidence(raw):
    return Evidence(
        semantics_known=raw["semantics_known"],
        provenance_valid=raw["provenance_valid"],
        representability_margin=raw["representability_margin"],
        canonical_command_error=raw["canonical_command_error"],
        exact_transport_available=raw["exact_transport_available"],
        support_stability=raw["support_stability"],
        held_out_residual=raw["held_out_residual"],
        transverse_norm=raw["transverse_norm"],
        certified_repair_radius=raw["certified_repair_radius"],
        contract_class=ContractClass(raw["contract_class"]),
        support_ids=tuple(raw["support_ids"]),
    )


def _base():
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


def _cases():
    base = _base()
    edits = [
        {"semantics_known": False},
        {"provenance_valid": False},
        {"representability_margin": -0.1},
        {"canonical_command_error": 0.0},
        {"exact_transport_available": True},
        {"contract_class": "UNKNOWN"},
        {"support_stability": 0.2},
        {"held_out_residual": 0.9},
        {"certified_repair_radius": 0.0},
        {"transverse_norm": 0.9},
        {},
    ]
    for edit in edits:
        case = dict(base)
        case.update(edit)
        yield case


def test_plugin_decisions_conform_to_canonical_runtime_for_every_branch():
    core = _load_core()
    provenance = ["policy=p", "checkpoint=sha256:x", "trial=1"]
    canonical_thresholds = Thresholds()
    plugin_thresholds = core.Thresholds()

    for raw in _cases():
        canonical = compile_contract(
            _dict_to_evidence(raw),
            provenance_parts=provenance,
            thresholds=canonical_thresholds,
        )
        plugin = core.compile_evidence(
            raw, provenance_parts=provenance, thresholds=plugin_thresholds
        )
        assert plugin["decision"] == canonical.decision.value
        assert plugin["reason"] == canonical.reason
        assert plugin["provenance_digest"] == canonical.provenance_digest
        assert plugin["contract_class"] == canonical.contract_class.value
        assert plugin["support_ids"] == list(canonical.support_ids)

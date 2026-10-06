from __future__ import annotations

import torch

from lerobot.lerobot_types import TransitionKey
from lerobot.processor import ProcessorStepRegistry
from lerobot.utils.import_utils import register_third_party_plugins


def main() -> None:
    assert "eprc_contract_gate" not in ProcessorStepRegistry.list()
    register_third_party_plugins()
    assert "eprc_contract_gate" in ProcessorStepRegistry.list()

    step_cls = ProcessorStepRegistry.get("eprc_contract_gate")
    step = step_cls(fail_closed=False)
    transition = {
        TransitionKey.OBSERVATION: None,
        TransitionKey.ACTION: torch.zeros(2),
        TransitionKey.REWARD: None,
        TransitionKey.DONE: None,
        TransitionKey.TRUNCATED: None,
        TransitionKey.INFO: None,
        TransitionKey.COMPLEMENTARY_DATA: {
            "eprc_evidence": {
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
            },
            "eprc_provenance": [
                "policy=compat-probe",
                "checkpoint=sha256:fixture",
                "controller=joint_position",
            ],
        },
    }

    out = step(transition)
    cert = out[TransitionKey.COMPLEMENTARY_DATA]["eprc_certificate"]
    assert cert["decision"] == "REPAIR"
    assert len(cert["provenance_digest"]) == 64
    assert torch.equal(out[TransitionKey.ACTION], transition[TransitionKey.ACTION])

    # Discovery must remain idempotent.
    register_third_party_plugins()
    assert ProcessorStepRegistry.get("eprc_contract_gate") is step_cls
    print("LeRobot #4592 EPRC plugin compatibility: PASS")


if __name__ == "__main__":
    main()

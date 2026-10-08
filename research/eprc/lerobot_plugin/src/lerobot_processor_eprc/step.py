from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lerobot.lerobot_types import EnvTransition, TransitionKey
from lerobot.processor import ProcessorStep, ProcessorStepRegistry

from .core import Thresholds, compile_evidence


@ProcessorStepRegistry.register(name="eprc_contract_gate")
@dataclass
class EPRCContractGateStep(ProcessorStep):
    """Audit or fail closed on a provenance-bound EPRC evidence bundle."""

    evidence_key: str = "eprc_evidence"
    provenance_key: str = "eprc_provenance"
    certificate_key: str = "eprc_certificate"
    fail_closed: bool = False
    pass_error: float = 1e-6
    min_support_stability: float = 0.9
    max_held_out_residual: float = 0.05

    def __call__(self, transition: EnvTransition) -> EnvTransition:
        self._current_transition = transition
        complementary = dict(transition.get(TransitionKey.COMPLEMENTARY_DATA) or {})

        if self.evidence_key not in complementary:
            raise ValueError(
                f"missing EPRC evidence at complementary_data[{self.evidence_key!r}]"
            )
        if self.provenance_key not in complementary:
            raise ValueError(
                f"missing EPRC provenance at complementary_data[{self.provenance_key!r}]"
            )

        evidence = complementary[self.evidence_key]
        provenance = complementary[self.provenance_key]

        if not isinstance(evidence, dict):
            raise TypeError("EPRC evidence must be a dictionary")
        if not isinstance(provenance, (list, tuple)) or not all(
            isinstance(x, str) for x in provenance
        ):
            raise TypeError("EPRC provenance must be a list/tuple of strings")

        cert = compile_evidence(
            evidence,
            provenance_parts=provenance,
            thresholds=Thresholds(
                pass_error=self.pass_error,
                min_support_stability=self.min_support_stability,
                max_held_out_residual=self.max_held_out_residual,
            ),
        )
        complementary[self.certificate_key] = cert

        out = dict(transition)
        out[TransitionKey.COMPLEMENTARY_DATA] = complementary

        if self.fail_closed and cert["decision"] == "REJECT":
            raise RuntimeError(f"EPRC rejected action: {cert['reason']}")

        return out  # type: ignore[return-value]

    def transform_features(self, features):
        return features

    def get_config(self) -> dict[str, Any]:
        return {
            "evidence_key": self.evidence_key,
            "provenance_key": self.provenance_key,
            "certificate_key": self.certificate_key,
            "fail_closed": self.fail_closed,
            "pass_error": self.pass_error,
            "min_support_stability": self.min_support_stability,
            "max_held_out_residual": self.max_held_out_residual,
        }

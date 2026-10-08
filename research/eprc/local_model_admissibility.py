from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LocalModelAdmissibility(str, Enum):
    ADMISSIBLE_FIRST_ORDER = "ADMISSIBLE_FIRST_ORDER"
    INFORMATION_LIMITED = "INFORMATION_LIMITED"
    LOCALITY_LIMITED = "LOCALITY_LIMITED"
    REJECT_LOCAL_MODEL = "REJECT_LOCAL_MODEL"


@dataclass(frozen=True)
class LocalModelAdmissibilityResult:
    dec_stable: bool
    locality_contracting: bool
    state: LocalModelAdmissibility
    same_scale_queries_authorized: bool
    smaller_scale_model_authorized: bool
    repair_certificate_authorized: bool
    reason: str


def classify_local_model_admissibility(
    *,
    dec_stable: bool,
    locality_contracting: bool,
) -> LocalModelAdmissibilityResult:
    """Separate repeatability/identifiability from first-order locality.

    These are logically independent gates:
      - DEC stability asks whether repeated probes identify a reproducible map.
      - locality contraction asks whether that map converges as the physical
        intervention radius shrinks.

    A first-order CRG certificate is authorized only when both pass.
    """

    if dec_stable and locality_contracting:
        return LocalModelAdmissibilityResult(
            dec_stable=True,
            locality_contracting=True,
            state=LocalModelAdmissibility.ADMISSIBLE_FIRST_ORDER,
            same_scale_queries_authorized=False,
            smaller_scale_model_authorized=True,
            repair_certificate_authorized=True,
            reason="repeated probes are stable and the local map contracts across scale",
        )

    if (not dec_stable) and locality_contracting:
        return LocalModelAdmissibilityResult(
            dec_stable=False,
            locality_contracting=True,
            state=LocalModelAdmissibility.INFORMATION_LIMITED,
            same_scale_queries_authorized=True,
            smaller_scale_model_authorized=True,
            repair_certificate_authorized=False,
            reason=(
                "the scale ladder is locally consistent, but repeated probes do "
                "not yet identify a stable DEC"
            ),
        )

    if dec_stable and (not locality_contracting):
        return LocalModelAdmissibilityResult(
            dec_stable=True,
            locality_contracting=False,
            state=LocalModelAdmissibility.LOCALITY_LIMITED,
            same_scale_queries_authorized=False,
            smaller_scale_model_authorized=False,
            repair_certificate_authorized=False,
            reason=(
                "the DEC is repeatable, but the first-order map does not converge "
                "under smaller physical interventions"
            ),
        )

    return LocalModelAdmissibilityResult(
        dec_stable=False,
        locality_contracting=False,
        state=LocalModelAdmissibility.REJECT_LOCAL_MODEL,
        same_scale_queries_authorized=False,
        smaller_scale_model_authorized=False,
        repair_certificate_authorized=False,
        reason=(
            "neither repeated-probe identifiability nor first-order locality is "
            "supported; do not spend additional local repair queries"
        ),
    )

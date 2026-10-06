from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import numpy as np

from controller_semantic_ir import AffineControllerIR, AffineTransportCertificate, compile_affine_transport
from semantic_morphism import LinearSemanticMorphismCertificate, SemanticMorphismKind, analyze_linear_semantic_morphism


class TransportAuthority(str, Enum):
    EXACT_SEMANTIC = "exact_semantic"
    OBSERVABLE_EXACT = "observable_exact"
    APPROXIMATE_ONLY = "approximate_only"
    REFUSE = "refuse"


@dataclass(frozen=True)
class CertifiedAffineTransport:
    """Structural + runtime certificate for one controller transport."""
    authority: TransportAuthority
    structure: LinearSemanticMorphismCertificate
    instance: AffineTransportCertificate
    executable_action: np.ndarray | None
    reason: str


def compile_certified_affine_transport(
    *,
    source: AffineControllerIR,
    target: AffineControllerIR,
    source_action: np.ndarray,
    source_state: np.ndarray,
    source_hidden: np.ndarray,
    target_state: np.ndarray,
    target_hidden: np.ndarray,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> CertifiedAffineTransport:
    """Compile a transport without confusing one-off solvability with semantic equivalence.

    First classify the action-to-goal maps U structurally. Then solve the
    concrete bounded transport including state and hidden-controller offsets.
    Approximate bounded solutions are reported but never silently authorized.
    """
    if source.goal_dim != target.goal_dim:
        raise ValueError("source and target canonical goal dimensions must match")

    structure = analyze_linear_semantic_morphism(source.U, target.U, rtol=rtol)
    instance = compile_affine_transport(
        source=source,
        target=target,
        source_action=source_action,
        source_state=source_state,
        source_hidden=source_hidden,
        target_state=target_state,
        target_hidden=target_hidden,
        atol=atol,
        rtol=rtol,
    )

    if structure.kind is SemanticMorphismKind.LOCALLY_UNREPRESENTABLE:
        return CertifiedAffineTransport(
            TransportAuthority.REFUSE,
            structure,
            instance,
            None,
            "controller pair cannot preserve every source canonical-goal direction",
        )

    if instance.bounded_representable:
        if structure.kind in {
            SemanticMorphismKind.EXACT_EQUIVALENCE,
            SemanticMorphismKind.FAITHFUL_EMBEDDING,
        }:
            return CertifiedAffineTransport(
                TransportAuthority.EXACT_SEMANTIC,
                structure,
                instance,
                instance.bounded_target_action.copy(),
                "injective source semantics and exact bounded target representation",
            )
        return CertifiedAffineTransport(
            TransportAuthority.OBSERVABLE_EXACT,
            structure,
            instance,
            instance.bounded_target_action.copy(),
            "physical observable is exact, but semantic information is projected or ambiguous",
        )

    if instance.bounded_solver_success:
        return CertifiedAffineTransport(
            TransportAuthority.APPROXIMATE_ONLY,
            structure,
            instance,
            None,
            "no bounded exact transport; closest bounded solution is diagnostic only",
        )

    return CertifiedAffineTransport(
        TransportAuthority.REFUSE,
        structure,
        instance,
        None,
        "target solve failed; no execution authority issued",
    )

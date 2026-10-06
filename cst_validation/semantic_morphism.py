from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class SemanticMorphismKind(str, Enum):
    """Directional relation between source and target semantic spaces."""

    EXACT_EQUIVALENCE = "exact_equivalence"
    FAITHFUL_EMBEDDING = "faithful_embedding"
    SOURCE_PROJECTION = "source_projection"
    TARGET_AMBIGUITY = "target_ambiguity"
    PROJECTION_AND_AMBIGUITY = "projection_and_ambiguity"
    LOCALLY_UNREPRESENTABLE = "locally_unrepresentable"


@dataclass(frozen=True)
class LinearSemanticMorphismCertificate:
    kind: SemanticMorphismKind
    source_rank: int
    target_rank: int
    source_kernel_dim: int
    target_kernel_dim: int
    source_image_dim: int
    target_image_dim: int
    source_image_in_target_residual: float
    target_image_in_source_residual: float
    images_equal: bool
    source_injective: bool
    target_injective: bool
    target_nonzero_condition_number: float
    reason: str


@dataclass(frozen=True)
class LinearSemanticWitness:
    """Constructive witnesses for semantic non-equivalence.

    Every non-null vector is unit norm.  The witness is deliberately
    constructive: callers can feed the source direction back through the
    source map or perturb the target along its nullspace and reproduce the
    failed / ambiguous semantic relation.
    """

    unrepresentable_source_direction: np.ndarray | None
    unrepresentable_observable_residual: np.ndarray | None
    source_invisible_direction: np.ndarray | None
    target_ambiguity_direction: np.ndarray | None
    unrepresentable_residual_norm: float


@dataclass(frozen=True)
class SharedObservableTransport:
    target_semantic: np.ndarray
    source_observable: np.ndarray
    reconstructed_observable: np.ndarray
    residual_norm: float
    relative_residual: float
    exact: bool


def _matrix(value: np.ndarray, name: str) -> np.ndarray:
    out = np.asarray(value, dtype=float)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise ValueError(f"{name} must have non-empty shape [common_dim, semantic_dim]")
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} must be finite")
    return out


def _rank(matrix: np.ndarray, rtol: float) -> int:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return 0
    threshold = rtol * max(float(singular[0]), 1.0)
    return int(np.sum(singular > threshold))


def _image_inclusion_residual(
    source_map: np.ndarray,
    target_map: np.ndarray,
) -> float:
    """Relative Frobenius residual after projecting source image onto target image."""
    projector = target_map @ np.linalg.pinv(target_map)
    residual = (np.eye(source_map.shape[0]) - projector) @ source_map
    return float(
        np.linalg.norm(residual, ord="fro")
        / max(float(np.linalg.norm(source_map, ord="fro")), 1e-12)
    )


def _nonzero_condition_number(matrix: np.ndarray, rtol: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return float("inf")
    threshold = rtol * max(float(singular[0]), 1.0)
    nz = singular[singular > threshold]
    if nz.size == 0:
        return float("inf")
    return float(nz[0] / nz[-1])


def analyze_linear_semantic_morphism(
    source_to_common: np.ndarray,
    target_to_common: np.ndarray,
    *,
    rtol: float = 1e-10,
) -> LinearSemanticMorphismCertificate:
    """Classify source->target transport through a shared physical observable.

    source_to_common maps source canonical semantics into a shared physical
    observable. target_to_common does the same for the target controller.

    Examples:
      - joint -> joint: both maps can be identity;
      - joint -> EE locally: source map can be the FK Jacobian J, target map I;
      - EE -> joint locally: source map I, target map J.
    """
    A = _matrix(source_to_common, "source_to_common")
    B = _matrix(target_to_common, "target_to_common")
    if A.shape[0] != B.shape[0]:
        raise ValueError("source and target must share one observable dimension")
    if rtol <= 0 or not np.isfinite(rtol):
        raise ValueError("rtol must be finite and positive")

    rank_a = _rank(A, rtol)
    rank_b = _rank(B, rtol)
    kernel_a = A.shape[1] - rank_a
    kernel_b = B.shape[1] - rank_b
    a_in_b = _image_inclusion_residual(A, B)
    b_in_a = _image_inclusion_residual(B, A)
    representable = a_in_b <= rtol
    images_equal = representable and b_in_a <= rtol
    source_injective = kernel_a == 0
    target_injective = kernel_b == 0

    if not representable:
        kind = SemanticMorphismKind.LOCALLY_UNREPRESENTABLE
        reason = (
            "some source-observable directions lie outside the target semantic image"
        )
    elif source_injective and target_injective and images_equal:
        kind = SemanticMorphismKind.EXACT_EQUIVALENCE
        reason = "source and target are injective charts of the same local observable image"
    elif source_injective and target_injective:
        kind = SemanticMorphismKind.FAITHFUL_EMBEDDING
        reason = (
            "source semantics embed uniquely into a larger target-observable image"
        )
    elif not source_injective and target_injective:
        kind = SemanticMorphismKind.SOURCE_PROJECTION
        reason = (
            "target can reproduce the shared observable, but source semantic "
            "directions are lost by the source-to-common projection"
        )
    elif source_injective and not target_injective:
        kind = SemanticMorphismKind.TARGET_AMBIGUITY
        reason = (
            "source observable is representable, but multiple target semantics "
            "produce the same shared observable"
        )
    else:
        kind = SemanticMorphismKind.PROJECTION_AND_AMBIGUITY
        reason = (
            "transport preserves only a shared quotient: source information is "
            "lost and target semantics are non-unique"
        )

    return LinearSemanticMorphismCertificate(
        kind=kind,
        source_rank=rank_a,
        target_rank=rank_b,
        source_kernel_dim=kernel_a,
        target_kernel_dim=kernel_b,
        source_image_dim=rank_a,
        target_image_dim=rank_b,
        source_image_in_target_residual=a_in_b,
        target_image_in_source_residual=b_in_a,
        images_equal=images_equal,
        source_injective=source_injective,
        target_injective=target_injective,
        target_nonzero_condition_number=_nonzero_condition_number(B, rtol),
        reason=reason,
    )



def _right_nullspace_witness(matrix: np.ndarray, rank: int) -> np.ndarray | None:
    """Return one deterministic unit vector from the right nullspace."""
    if rank >= matrix.shape[1]:
        return None
    _, _, vh = np.linalg.svd(matrix, full_matrices=True)
    witness = np.asarray(vh[rank], dtype=float)
    norm = float(np.linalg.norm(witness))
    if norm == 0.0:
        return None
    witness = witness / norm
    # Fix the SVD sign ambiguity so evidence is stable across runs.
    first = int(np.argmax(np.abs(witness) > 1e-14))
    if witness[first] < 0:
        witness = -witness
    return witness


def construct_linear_semantic_witness(
    source_to_common: np.ndarray,
    target_to_common: np.ndarray,
    *,
    rtol: float = 1e-10,
) -> LinearSemanticWitness:
    """Construct counterexamples / ambiguity witnesses for a semantic morphism.

    For non-representability, the returned source direction maximizes the
    norm of the source observable component orthogonal to the target image.
    For source projection and target ambiguity, returned nullspace directions
    are concrete semantic perturbations that are invisible in the shared
    observable.
    """
    A = _matrix(source_to_common, "source_to_common")
    B = _matrix(target_to_common, "target_to_common")
    if A.shape[0] != B.shape[0]:
        raise ValueError("source and target must share one observable dimension")
    if rtol <= 0 or not np.isfinite(rtol):
        raise ValueError("rtol must be finite and positive")

    rank_a = _rank(A, rtol)
    rank_b = _rank(B, rtol)
    projector_b = B @ np.linalg.pinv(B)
    residual_operator = (np.eye(A.shape[0]) - projector_b) @ A

    source_direction = None
    observable_residual = None
    residual_norm = 0.0
    if np.linalg.norm(residual_operator, ord="fro") > rtol:
        _, singular, vh = np.linalg.svd(residual_operator, full_matrices=False)
        source_direction = np.asarray(vh[0], dtype=float)
        source_direction /= max(float(np.linalg.norm(source_direction)), 1e-12)
        first = int(np.argmax(np.abs(source_direction) > 1e-14))
        if source_direction[first] < 0:
            source_direction = -source_direction
        observable_residual = residual_operator @ source_direction
        residual_norm = float(np.linalg.norm(observable_residual))

    return LinearSemanticWitness(
        unrepresentable_source_direction=source_direction,
        unrepresentable_observable_residual=observable_residual,
        source_invisible_direction=_right_nullspace_witness(A, rank_a),
        target_ambiguity_direction=_right_nullspace_witness(B, rank_b),
        unrepresentable_residual_norm=residual_norm,
    )


def transport_shared_observable(
    source_semantic: np.ndarray,
    source_to_common: np.ndarray,
    target_to_common: np.ndarray,
    *,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> SharedObservableTransport:
    """Minimum-norm target semantic that matches the source shared observable."""
    A = _matrix(source_to_common, "source_to_common")
    B = _matrix(target_to_common, "target_to_common")
    source = np.asarray(source_semantic, dtype=float)
    if source.shape != (A.shape[1],):
        raise ValueError("source semantic dimension mismatch")
    if A.shape[0] != B.shape[0]:
        raise ValueError("common observable dimensions differ")

    obs = A @ source
    target = np.linalg.pinv(B) @ obs
    reconstructed = B @ target
    residual = float(np.linalg.norm(reconstructed - obs))
    scale = max(float(np.linalg.norm(obs)), 1.0)
    return SharedObservableTransport(
        target_semantic=target,
        source_observable=obs,
        reconstructed_observable=reconstructed,
        residual_norm=residual,
        relative_residual=residual / scale,
        exact=bool(residual <= atol + rtol * scale),
    )

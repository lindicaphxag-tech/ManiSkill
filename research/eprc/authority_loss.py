from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .contract_signature import contract_signature, signature_distance


@dataclass(frozen=True)
class SaturatingController:
    """Local controller chart with component-wise bounded physical authority."""

    scale: np.ndarray
    lower: np.ndarray
    upper: np.ndarray

    def decode(self, action: np.ndarray) -> np.ndarray:
        action = np.asarray(action, dtype=float)
        scaled = self.scale * action
        return np.clip(scaled, self.lower, self.upper)

    def local_action_to_physical_jacobian(
        self,
        action: np.ndarray,
        *,
        eps: float = 1e-7,
    ) -> np.ndarray:
        """Numerically identify local controller authority at an action point."""

        action = np.asarray(action, dtype=float)
        d = action.size
        jac = np.zeros((d, d), dtype=float)
        for j in range(d):
            e = np.zeros(d, dtype=float)
            e[j] = eps
            jac[:, j] = (self.decode(action + e) - self.decode(action - e)) / (2 * eps)
        return jac


@dataclass(frozen=True)
class AuthorityCertificate:
    local_rank: int
    full_rank: int
    minimum_singular_value: float
    lost_directions: int
    admissible_for_exact_transport: bool


def authority_certificate(
    controller: SaturatingController,
    action: np.ndarray,
    *,
    singular_tolerance: float = 1e-8,
) -> AuthorityCertificate:
    jac = controller.local_action_to_physical_jacobian(action)
    singular = np.linalg.svd(jac, compute_uv=False)
    rank = int(np.sum(singular > singular_tolerance))
    full_rank = int(action.size)
    minimum = float(singular.min()) if singular.size else 0.0
    return AuthorityCertificate(
        local_rank=rank,
        full_rank=full_rank,
        minimum_singular_value=minimum,
        lost_directions=full_rank - rank,
        admissible_for_exact_transport=rank == full_rank,
    )


def lifted_contract_under_controller(
    action_support_jacobian: np.ndarray,
    controller: SaturatingController,
    action: np.ndarray,
):
    lift = controller.local_action_to_physical_jacobian(action)
    physical = lift @ np.asarray(action_support_jacobian, dtype=float)
    return physical, contract_signature(physical), authority_certificate(controller, action)


def authority_aware_equivalence(
    action_support_jacobian_a: np.ndarray,
    controller_a: SaturatingController,
    action_a: np.ndarray,
    action_support_jacobian_b: np.ndarray,
    controller_b: SaturatingController,
    action_b: np.ndarray,
    *,
    tolerance: float = 1e-6,
) -> tuple[bool, str]:
    phys_a, sig_a, cert_a = lifted_contract_under_controller(
        action_support_jacobian_a, controller_a, action_a
    )
    phys_b, sig_b, cert_b = lifted_contract_under_controller(
        action_support_jacobian_b, controller_b, action_b
    )

    if not cert_a.admissible_for_exact_transport:
        return False, "source controller has lost local physical authority"
    if not cert_b.admissible_for_exact_transport:
        return False, "target controller has lost local physical authority"
    if phys_a.shape[0] != phys_b.shape[0]:
        return False, "physical command dimensions differ"
    if signature_distance(sig_a, sig_b) > tolerance:
        return False, "differential execution contracts differ"
    return True, "locally equivalent and full-authority"

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np

try:
    from .linear_stateful_transport import (
        LinearSemanticTransducer,
        StatefulTransportCertificate,
        synthesize_linear_stateful_transport,
    )
except ImportError:
    from linear_stateful_transport import (
        LinearSemanticTransducer,
        StatefulTransportCertificate,
        synthesize_linear_stateful_transport,
    )


@dataclass(frozen=True)
class MinimalHandshakeCertificate:
    """Smallest source hidden-state interface that admits exact transport."""

    exact: bool
    selected_state_indices: tuple[int, ...]
    selected_state_names: tuple[str, ...]
    exposed_state_count: int
    source_state_dim: int
    transport: StatefulTransportCertificate | None
    tested_subsets: int
    all_minimal_exact_subsets: tuple[tuple[int, ...], ...]
    reason: str


def synthesize_minimal_source_state_handshake(
    source: LinearSemanticTransducer,
    target: LinearSemanticTransducer,
    *,
    state_names: tuple[str, ...] | None = None,
    allow_source_state_feedback: bool = True,
    max_exact_search_dim: int = 16,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> MinimalHandshakeCertificate:
    """Enumerate source-state interfaces from smallest to largest.

    This is deliberately exact and combinatorial for small semantic states,
    which are typically controller-owned variables such as previous targets,
    integrator state, mode bits, or filtered references rather than the full
    robot state.

    A subset is accepted only if the same output-commutation and next-state
    closure equations used by CST admit an exact solution when *both* the
    state relation M and state-feedback term L are restricted to that subset.

    Returning every exact subset at the minimum cardinality makes interface
    ambiguity visible rather than silently choosing one arbitrary handshake.
    """
    ns = source.state_dim
    if ns > max_exact_search_dim:
        raise ValueError(
            f"exact handshake search supports at most {max_exact_search_dim} "
            f"source semantic-state coordinates, got {ns}"
        )
    if state_names is None:
        names = tuple(f"z[{i}]" for i in range(ns))
    else:
        names = tuple(state_names)
        if len(names) != ns:
            raise ValueError("state_names must match source state dimension")
        if len(set(names)) != len(names):
            raise ValueError("state_names must be unique")

    tested = 0
    for cardinality in range(ns + 1):
        exact_at_level: list[tuple[tuple[int, ...], StatefulTransportCertificate]] = []
        for subset in combinations(range(ns), cardinality):
            access = np.zeros(ns, dtype=bool)
            if subset:
                access[list(subset)] = True
            cert = synthesize_linear_stateful_transport(
                source,
                target,
                allow_source_state_feedback=allow_source_state_feedback,
                atol=atol,
                rtol=rtol,
                source_state_access_mask=access,
            )
            tested += 1
            if cert.exact:
                exact_at_level.append((subset, cert))

        if exact_at_level:
            selected, selected_cert = exact_at_level[0]
            all_subsets = tuple(item[0] for item in exact_at_level)
            return MinimalHandshakeCertificate(
                exact=True,
                selected_state_indices=selected,
                selected_state_names=tuple(names[i] for i in selected),
                exposed_state_count=cardinality,
                source_state_dim=ns,
                transport=selected_cert,
                tested_subsets=tested,
                all_minimal_exact_subsets=all_subsets,
                reason=(
                    "found the minimum-cardinality source semantic-state "
                    "interface that closes the executable simulation relation"
                ),
            )

    return MinimalHandshakeCertificate(
        exact=False,
        selected_state_indices=(),
        selected_state_names=(),
        exposed_state_count=0,
        source_state_dim=ns,
        transport=None,
        tested_subsets=tested,
        all_minimal_exact_subsets=(),
        reason=(
            "no subset of the declared source semantic state admits an exact "
            "transport under the selected adapter class"
        ),
    )

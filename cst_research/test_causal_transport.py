from causal_transport import (
    AdapterPhase,
    CausalStatus,
    analyze_chunk_transport_causality,
)
from reference_semantics import ReferenceKind


def test_chunk_anchor_to_absolute_is_precomputable_for_full_chunk():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CHUNK_ANCHOR,
        ReferenceKind.ABSOLUTE,
        horizon=16,
    )
    assert cert.status is CausalStatus.PRECOMPUTABLE
    assert cert.minimum_phase is AdapterPhase.QUERY_TIME


def test_sequential_delta_to_chunk_anchor_is_precomputable():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.PREVIOUS_COMMAND,
        ReferenceKind.CHUNK_ANCHOR,
        horizon=8,
    )
    assert cert.status is CausalStatus.PRECOMPUTABLE


def test_future_current_state_target_cannot_be_precomputed_at_query_time():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CHUNK_ANCHOR,
        ReferenceKind.CURRENT_STATE,
        horizon=8,
        requested_phase=AdapterPhase.QUERY_TIME,
    )
    assert cert.status is CausalStatus.REQUIRES_STEP_HOOK
    assert cert.earliest_unavailable_step == 1
    assert cert.target_action_available_at == tuple(range(8))


def test_current_state_source_also_requires_execution_time_decode():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CURRENT_STATE,
        ReferenceKind.ABSOLUTE,
        horizon=5,
        requested_phase=AdapterPhase.QUERY_TIME,
    )
    assert cert.status is CausalStatus.REQUIRES_STEP_HOOK
    assert cert.earliest_unavailable_step == 1


def test_single_step_current_state_conversion_is_query_time_available():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CURRENT_STATE,
        ReferenceKind.ABSOLUTE,
        horizon=1,
        requested_phase=AdapterPhase.QUERY_TIME,
    )
    assert cert.status is CausalStatus.PRECOMPUTABLE


def test_step_hook_makes_current_state_transport_causal():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CHUNK_ANCHOR,
        ReferenceKind.CURRENT_STATE,
        horizon=8,
        requested_phase=AdapterPhase.STEP_TIME,
        step_hook_has_physical_state=True,
    )
    assert cert.status is CausalStatus.EXECUTABLE_WITH_STEP_HOOK
    assert cert.minimum_phase is AdapterPhase.STEP_TIME


def test_step_hook_must_expose_controller_owned_target_state():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.ABSOLUTE,
        ReferenceKind.CONTROLLER_TARGET,
        horizon=6,
        requested_phase=AdapterPhase.STEP_TIME,
        step_hook_has_controller_target=False,
    )
    assert cert.status is CausalStatus.REFUSE_MISSING_RUNTIME_STATE
    assert cert.requires_controller_target


def test_query_time_controller_target_conversion_requires_step_hook():
    cert = analyze_chunk_transport_causality(
        ReferenceKind.CONTROLLER_TARGET,
        ReferenceKind.ABSOLUTE,
        horizon=4,
        requested_phase=AdapterPhase.QUERY_TIME,
    )
    assert cert.status is CausalStatus.REQUIRES_STEP_HOOK
    assert cert.earliest_unavailable_step == 1

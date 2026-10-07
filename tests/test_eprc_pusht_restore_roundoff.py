"""Regression against Pymunk float64 readback drift in frozen PushT bank.

Values are taken from failed upstream-CI job diagnostics, not fabricated
posthoc repair outcomes. Scientific gate thresholds and states are unchanged.
"""
import numpy as np

from research.eprc.real_policy.pusht_exact_state import (
    BLOCK_POSITION_MAX_ULPS,
    STATE_RESTORE_PROTOCOL,
    _block_position_roundtrip_allowed,
)


def test_known_failed_seed_readbacks_are_bounded_floating_roundoff():
    observed = (
        ([288.4250657450654, 249.32821179243305],
         [288.4250657450654, 249.32821179243302]),
        ([200.07948724792587, 280.9254845595014],
         [200.0794872479259, 280.92548455950146]),
        ([214.3517050599082, 202.6441123136045],
         [214.3517050599082, 202.64411231360452]),
    )
    assert BLOCK_POSITION_MAX_ULPS == 4
    assert STATE_RESTORE_PROTOCOL.endswith("4ulp-v2")
    for expected, readback in observed:
        assert _block_position_roundtrip_allowed(expected, readback)


def test_large_physical_disturbance_cannot_pass_ulps_gate():
    expected = np.array([250.0, 200.0])
    for shift in ([0.001, 0.0], [0.0, 1e-8], [1e-4, -1e-4]):
        assert not _block_position_roundtrip_allowed(expected, expected + shift)


def test_more_than_four_ulps_is_rejected():
    expected = np.array([250.0, 200.0], dtype=float)
    altered = expected.copy()
    for _ in range(BLOCK_POSITION_MAX_ULPS + 1):
        altered[0] = np.nextafter(altered[0], np.inf)
    assert not _block_position_roundtrip_allowed(expected, altered)


def test_nonfinite_and_shape_mismatches_are_rejected():
    expected = np.array([250.0, 200.0])
    for other in ([np.nan, 200.0], [250.0, np.inf], [250.0], [250.0, 200.0, 1.0]):
        assert not _block_position_roundtrip_allowed(expected, np.asarray(other))

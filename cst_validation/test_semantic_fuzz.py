import numpy as np

from controller_semantic_transport import (
    AffineActionChart,
    JointPositionMode,
    JointPositionSemantics,
)
from semantic_fuzz import audit_converter, sample_joint_position_cases


def _norm(low, high):
    return AffineActionChart(np.asarray(low, float), np.asarray(high, float), True)


def test_semantic_fuzzer_accepts_reference_equivalent_converter():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.1, -0.1], [0.1, 0.1]),
    )
    target = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0, -2.0], [2.0, 2.0]),
    )
    cases = sample_joint_position_cases(
        source=source,
        target=target,
        count=200,
        seed=20261006,
    )

    def correct(case):
        physical_delta = source.chart.decode(case.source_native_action, clip_native=True)
        desired_target = case.current_qpos + physical_delta
        native, representable = target.chart.encode(desired_target)
        assert np.all(representable)
        return native

    report = audit_converter(
        source=source,
        target=target,
        cases=cases,
        converter=correct,
    )
    assert report.exact_reference_cases == 200
    assert report.violations == ()
    assert report.violation_rate_on_exact_cases == 0.0


def test_semantic_fuzzer_catches_double_normalization_bug():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.1, -0.1], [0.1, 0.1]),
    )
    target = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0, -2.0], [2.0, 2.0]),
    )
    cases = sample_joint_position_cases(
        source=source,
        target=target,
        count=100,
        seed=17,
    )

    def buggy(case):
        physical_delta = source.chart.decode(case.source_native_action, clip_native=True)
        physical_target = case.current_qpos + physical_delta
        # Real-world bug class: physical qpos is returned directly even though
        # target native action is normalized. The target controller scales it
        # again, changing the physical goal.
        return physical_target

    report = audit_converter(
        source=source,
        target=target,
        cases=cases,
        converter=buggy,
    )
    assert report.exact_reference_cases == 100
    assert len(report.violations) > 90
    assert all(v.kind == "semantic_target_mismatch" for v in report.violations)


def test_semantic_fuzzer_catches_current_vs_target_reference_confusion():
    source = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.5], [0.5]),
    )
    target = JointPositionSemantics(
        JointPositionMode.DELTA_TARGET,
        _norm([-1.0], [1.0]),
    )
    cases = sample_joint_position_cases(
        source=source,
        target=target,
        count=300,
        seed=29,
        qpos_low=-0.2,
        qpos_high=0.2,
        native_low=-0.5,
        native_high=0.5,
    )

    def buggy_copy(case):
        # A common "both are delta" assumption: copy the native delta without
        # compensating for target-controller memory.
        return case.source_native_action.copy()

    report = audit_converter(
        source=source,
        target=target,
        cases=cases,
        converter=buggy_copy,
    )
    assert report.exact_reference_cases > 250
    assert report.violation_rate_on_exact_cases > 0.95


def test_unrepresentable_reference_cases_are_not_mislabeled_converter_bugs():
    source = JointPositionSemantics(
        JointPositionMode.ABSOLUTE,
        _norm([-2.0], [2.0]),
    )
    target = JointPositionSemantics(
        JointPositionMode.DELTA_CURRENT,
        _norm([-0.01], [0.01]),
    )
    cases = sample_joint_position_cases(
        source=source,
        target=target,
        count=50,
        seed=31,
    )

    report = audit_converter(
        source=source,
        target=target,
        cases=cases,
        converter=lambda case: np.zeros(1),
    )
    assert report.exact_reference_cases < report.total_cases

import numpy as np

from piecewise_affine_clip import (
    clipped_affine_reference,
    compile_clipped_affine_partition,
)


def test_scalar_clip_compiles_three_active_regions():
    partition = compile_clipped_affine_partition(
        A=np.array([[1.0]]),
        b=np.array([0.0]),
        clip_low=np.array([-1.0]),
        clip_high=np.array([1.0]),
        input_low=np.array([-2.0]),
        input_high=np.array([2.0]),
    )
    assert {cell.active_set for cell in partition.cells} == {(-1,), (0,), (1,)}
    for x in np.linspace(-2, 2, 101):
        actual = partition.evaluate(np.array([x]))
        expected = np.array([np.clip(x, -1, 1)])
        np.testing.assert_allclose(actual, expected, atol=1e-9)


def test_multidimensional_partition_matches_clipped_affine_reference():
    A = np.array([[0.5, 1.0], [-1.0, 0.25]])
    b = np.array([0.1, -0.2])
    low = np.array([-0.4, -0.5])
    high = np.array([0.7, 0.6])
    input_low = np.array([-1.0, -1.0])
    input_high = np.array([1.0, 1.0])
    partition = compile_clipped_affine_partition(
        A=A,
        b=b,
        clip_low=low,
        clip_high=high,
        input_low=input_low,
        input_high=input_high,
    )
    rng = np.random.default_rng(20261006)
    for _ in range(2000):
        v = rng.uniform(input_low, input_high)
        actual = partition.evaluate(v)
        expected = clipped_affine_reference(A, b, low, high, v)
        np.testing.assert_allclose(actual, expected, atol=1e-8)


def test_boundary_overlap_is_semantically_consistent():
    partition = compile_clipped_affine_partition(
        A=np.array([[1.0]]),
        b=np.array([0.0]),
        clip_low=np.array([-1.0]),
        clip_high=np.array([1.0]),
        input_low=np.array([-2.0]),
        input_high=np.array([2.0]),
    )
    matches = partition.matching_cells(np.array([1.0]))
    assert len(matches) >= 2
    outputs = [cell.evaluate(np.array([1.0])) for cell in matches]
    for output in outputs:
        np.testing.assert_allclose(output, [1.0], atol=1e-9)


def test_infeasible_active_sets_are_removed():
    partition = compile_clipped_affine_partition(
        A=np.array([[1.0], [1.0]]),
        b=np.zeros(2),
        clip_low=np.array([-1.0, -1.0]),
        clip_high=np.array([1.0, 1.0]),
        input_low=np.array([-0.25]),
        input_high=np.array([0.25]),
    )
    # Both outputs are always free in this restricted input domain.
    assert len(partition.cells) == 1
    assert partition.cells[0].active_set == (0, 0)

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class PolyhedralAffineCell:
    """One exact active-set cell of a clipped affine map.

    The cell is {v | H v <= h}. Inside it,

        clip(A v + b, low, high) = P v + q.

    active_set uses -1 for lower-saturated, 0 for free, +1 for
    upper-saturated output coordinates.
    """

    H: np.ndarray
    h: np.ndarray
    P: np.ndarray
    q: np.ndarray
    active_set: tuple[int, ...]
    feasibility_point: np.ndarray

    def contains(self, value, tol=1e-9) -> bool:
        value = np.asarray(value, dtype=float)
        return bool(np.all(self.H @ value <= self.h + tol))

    def evaluate(self, value) -> np.ndarray:
        value = np.asarray(value, dtype=float)
        if value.shape != (self.P.shape[1],):
            raise ValueError("input dimension mismatch")
        return self.P @ value + self.q


@dataclass(frozen=True)
class PiecewiseAffinePartition:
    cells: tuple[PolyhedralAffineCell, ...]
    input_low: np.ndarray
    input_high: np.ndarray
    output_low: np.ndarray
    output_high: np.ndarray

    def matching_cells(self, value, tol=1e-9):
        return tuple(cell for cell in self.cells if cell.contains(value, tol=tol))

    def evaluate(self, value, tol=1e-9):
        matches = self.matching_cells(value, tol=tol)
        if not matches:
            raise ValueError("input lies outside certified partition")
        outputs = [cell.evaluate(value) for cell in matches]
        for other in outputs[1:]:
            np.testing.assert_allclose(other, outputs[0], atol=10 * tol, rtol=0)
        return outputs[0]


def _box_inequalities(low, high):
    low = np.asarray(low, dtype=float)
    high = np.asarray(high, dtype=float)
    if low.shape != high.shape or low.ndim != 1:
        raise ValueError("box bounds must share shape [N]")
    if np.any(high < low):
        raise ValueError("box high must be >= low")
    eye = np.eye(low.size)
    H = np.concatenate([eye, -eye], axis=0)
    h = np.concatenate([high, -low], axis=0)
    return H, h


def compile_clipped_affine_partition(
    *,
    A,
    b,
    clip_low,
    clip_high,
    input_low,
    input_high,
    feasibility_tol=1e-10,
):
    """Compile exact polyhedral cells for coordinate-wise clipped affine map.

    Every active-set pattern is intersected with the declared input box and
    retained only if feasible. The resulting cells cover the full box. Cells
    can overlap on clipping boundaries, where their affine outputs coincide.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    clip_low = np.asarray(clip_low, dtype=float)
    clip_high = np.asarray(clip_high, dtype=float)
    input_low = np.asarray(input_low, dtype=float)
    input_high = np.asarray(input_high, dtype=float)

    if A.ndim != 2:
        raise ValueError("A must have shape [M, N]")
    m, n = A.shape
    if b.shape != (m,) or clip_low.shape != (m,) or clip_high.shape != (m,):
        raise ValueError("output vectors must match A rows")
    if input_low.shape != (n,) or input_high.shape != (n,):
        raise ValueError("input bounds must match A columns")
    if np.any(clip_high < clip_low):
        raise ValueError("clip_high must be >= clip_low")

    H_box, h_box = _box_inequalities(input_low, input_high)
    cells = []

    for active in product((-1, 0, 1), repeat=m):
        rows = [H_box]
        rhs = [h_box]
        P = np.zeros_like(A)
        q = np.zeros(m)

        extra_H = []
        extra_h = []
        for i, mode in enumerate(active):
            ai = A[i]
            bi = b[i]
            if mode == -1:
                # A_i v + b_i <= low_i
                extra_H.append(ai)
                extra_h.append(clip_low[i] - bi)
                q[i] = clip_low[i]
            elif mode == 0:
                # low_i <= A_i v + b_i <= high_i
                extra_H.extend([ai, -ai])
                extra_h.extend([clip_high[i] - bi, bi - clip_low[i]])
                P[i] = ai
                q[i] = bi
            else:
                # A_i v + b_i >= high_i
                extra_H.append(-ai)
                extra_h.append(bi - clip_high[i])
                q[i] = clip_high[i]

        if extra_H:
            rows.append(np.asarray(extra_H, dtype=float))
            rhs.append(np.asarray(extra_h, dtype=float))
        H = np.concatenate(rows, axis=0)
        h = np.concatenate(rhs, axis=0)

        feasibility = linprog(
            c=np.zeros(n),
            A_ub=H,
            b_ub=h + feasibility_tol,
            bounds=[(None, None)] * n,
            method="highs",
        )
        if not feasibility.success:
            continue

        cells.append(
            PolyhedralAffineCell(
                H=H,
                h=h,
                P=P,
                q=q,
                active_set=tuple(int(x) for x in active),
                feasibility_point=np.asarray(feasibility.x, dtype=float),
            )
        )

    if not cells:
        raise ValueError("declared input box has no feasible active-set cell")

    return PiecewiseAffinePartition(
        cells=tuple(cells),
        input_low=input_low,
        input_high=input_high,
        output_low=clip_low,
        output_high=clip_high,
    )


def clipped_affine_reference(A, b, low, high, value):
    return np.clip(
        np.asarray(A, dtype=float) @ np.asarray(value, dtype=float)
        + np.asarray(b, dtype=float),
        np.asarray(low, dtype=float),
        np.asarray(high, dtype=float),
    )

"""AXION-GEO geometric feature extraction for Lotofacil 5x5 grids.

Each draw is represented as a binary 5x5 matrix in row-major order:
01..05, 06..10, 11..15, 16..20, 21..25.

The functions in this module are descriptive. They do not imply predictive
ability and are intended to be evaluated against explicit null models.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple

import numpy as np


N_ROWS = 5
N_COLS = 5
N_SELECTED = 15


def validate_grid(grid: np.ndarray) -> np.ndarray:
    """Return a validated 5x5 int8 binary grid containing exactly 15 ones."""
    a = np.asarray(grid, dtype=np.int8)
    if a.size != 25:
        raise ValueError(f"Expected 25 cells, got {a.size}.")
    a = a.reshape(N_ROWS, N_COLS)
    if not np.isin(a, [0, 1]).all():
        raise ValueError("Grid must be binary.")
    if int(a.sum()) != N_SELECTED:
        raise ValueError(f"Expected {N_SELECTED} selected cells, got {int(a.sum())}.")
    return a


def draw_to_grid(selected_numbers: Iterable[int]) -> np.ndarray:
    """Convert an iterable of 15 numbers in 1..25 to a 5x5 binary grid."""
    nums = sorted({int(x) for x in selected_numbers})
    if len(nums) != N_SELECTED:
        raise ValueError("A Lotofacil draw must contain 15 distinct numbers.")
    if nums[0] < 1 or nums[-1] > 25:
        raise ValueError("Numbers must lie in 1..25.")
    flat = np.zeros(25, dtype=np.int8)
    flat[np.asarray(nums) - 1] = 1
    return flat.reshape(N_ROWS, N_COLS)


def _component_sizes(a: np.ndarray, diagonal: bool = False) -> Tuple[int, int]:
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        neighbors += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    seen = np.zeros_like(a, dtype=bool)
    sizes = []

    for r, c in zip(*np.where(a == 1)):
        if seen[r, c]:
            continue
        stack = [(int(r), int(c))]
        seen[r, c] = True
        size = 0
        while stack:
            rr, cc = stack.pop()
            size += 1
            for dr, dc in neighbors:
                nr, nc = rr + dr, cc + dc
                if (
                    0 <= nr < N_ROWS
                    and 0 <= nc < N_COLS
                    and a[nr, nc]
                    and not seen[nr, nc]
                ):
                    seen[nr, nc] = True
                    stack.append((nr, nc))
        sizes.append(size)

    return len(sizes), max(sizes) if sizes else 0


def _runs_1d(x: np.ndarray) -> Tuple[int, int]:
    x = np.asarray(x, dtype=np.int8)
    starts = int(np.sum((x == 1) & np.r_[True, x[:-1] == 0]))
    longest = 0
    current = 0
    for value in x:
        if value:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return starts, longest


def _longest_diagonal_run(a: np.ndarray) -> int:
    longest = 0
    for matrix in (a, np.fliplr(a)):
        for offset in range(-4, 5):
            diagonal = np.diag(matrix, k=offset)
            if diagonal.size:
                _, run = _runs_1d(diagonal)
                longest = max(longest, run)
    return int(longest)


def _overlap_symmetry(a: np.ndarray, transformed: np.ndarray) -> float:
    """Overlap of occupied cells after a symmetry transformation, scaled by 15."""
    return float(np.sum((a == 1) & (transformed == 1)) / N_SELECTED)


def extract_features(grid: np.ndarray) -> Dict[str, float]:
    """Extract the preregistered AXION-GEO phase-0 feature set."""
    a = validate_grid(grid)

    row_counts = a.sum(axis=1)
    col_counts = a.sum(axis=0)

    adj_h = int(np.sum(a[:, :-1] * a[:, 1:]))
    adj_v = int(np.sum(a[:-1, :] * a[1:, :]))
    adj_diag_dr = int(np.sum(a[:-1, :-1] * a[1:, 1:]))
    adj_diag_dl = int(np.sum(a[:-1, 1:] * a[1:, :-1]))
    adj_orth = adj_h + adj_v
    adj_diag = adj_diag_dr + adj_diag_dl

    comp4_count, comp4_largest = _component_sizes(a, diagonal=False)
    comp8_count, comp8_largest = _component_sizes(a, diagonal=True)

    isolated4 = 0
    for r, c in zip(*np.where(a == 1)):
        neighbors = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = int(r) + dr, int(c) + dc
            if 0 <= nr < N_ROWS and 0 <= nc < N_COLS:
                neighbors += int(a[nr, nc])
        isolated4 += int(neighbors == 0)

    rr, cc = np.where(a == 1)
    x = cc.astype(float) - 2.0
    y = rr.astype(float) - 2.0
    centroid_x = float(x.mean())
    centroid_y = float(y.mean())
    var_x = float(x.var())
    var_y = float(y.var())
    cov_xy = float(np.mean((x - centroid_x) * (y - centroid_y)))

    eig_minor, eig_major = np.linalg.eigvalsh(
        np.array([[var_x, cov_xy], [cov_xy, var_y]], dtype=float)
    )
    eig_minor = float(eig_minor)
    eig_major = float(eig_major)
    eig_sum = eig_major + eig_minor
    anisotropy = float((eig_major - eig_minor) / eig_sum) if eig_sum else 0.0
    radius_gyration = float(math.sqrt(max(0.0, eig_sum)))

    bbox_width = int(cc.max() - cc.min() + 1)
    bbox_height = int(rr.max() - rr.min() + 1)
    bbox_area = int(bbox_width * bbox_height)

    perimeter4 = int(4 * N_SELECTED - 2 * adj_orth)
    compactness = float(4 * math.pi * N_SELECTED / (perimeter4**2))

    outer_ring = int(
        sum(
            1
            for r, c in zip(rr, cc)
            if int(r) in (0, 4) or int(c) in (0, 4)
        )
    )
    center = int(a[2, 2])
    inner_ring = int(N_SELECTED - outer_ring - center)

    h_runs = 0
    v_runs = 0
    longest_h = 0
    longest_v = 0
    for r in range(N_ROWS):
        runs, longest = _runs_1d(a[r, :])
        h_runs += runs
        longest_h = max(longest_h, longest)
    for c in range(N_COLS):
        runs, longest = _runs_1d(a[:, c])
        v_runs += runs
        longest_v = max(longest_v, longest)

    features: Dict[str, float] = {}
    features.update({f"row_{i}": int(v) for i, v in enumerate(row_counts, 1)})
    features.update({f"col_{i}": int(v) for i, v in enumerate(col_counts, 1)})
    features.update(
        {
            "adj_h": adj_h,
            "adj_v": adj_v,
            "adj_diag_dr": adj_diag_dr,
            "adj_diag_dl": adj_diag_dl,
            "adj_orth": adj_orth,
            "adj_diag": adj_diag,
            "comp4_count": comp4_count,
            "comp4_largest": comp4_largest,
            "isolated4": isolated4,
            "comp8_count": comp8_count,
            "comp8_largest": comp8_largest,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "centroid_radius": float(math.hypot(centroid_x, centroid_y)),
            "var_x": var_x,
            "var_y": var_y,
            "cov_xy": cov_xy,
            "anisotropy": anisotropy,
            "radius_gyration": radius_gyration,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
            "bbox_area": bbox_area,
            "perimeter4": perimeter4,
            "compactness": compactness,
            "outer_ring": outer_ring,
            "inner_ring": inner_ring,
            "center": center,
            "h_runs": h_runs,
            "v_runs": v_runs,
            "longest_h": longest_h,
            "longest_v": longest_v,
            "longest_diag": _longest_diagonal_run(a),
            "sym_lr": _overlap_symmetry(a, np.fliplr(a)),
            "sym_ud": _overlap_symmetry(a, np.flipud(a)),
            "sym_rot180": _overlap_symmetry(a, np.rot90(a, 2)),
            "sym_diag_main": _overlap_symmetry(a, a.T),
            "sym_diag_anti": _overlap_symmetry(a, np.rot90(a, 2).T),
        }
    )
    return features

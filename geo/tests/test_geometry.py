import numpy as np

from geometry import draw_to_grid, extract_features, validate_grid


def test_draw_to_grid_mapping():
    grid = draw_to_grid(range(1, 16))
    assert grid.shape == (5, 5)
    assert int(grid.sum()) == 15
    assert grid[0, 0] == 1
    assert grid[2, 4] == 1
    assert grid[3, 0] == 0


def test_row_col_sums_are_conserved():
    grid = draw_to_grid([1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18, 21, 22, 23])
    f = extract_features(grid)
    assert sum(f[f"row_{i}"] for i in range(1, 6)) == 15
    assert sum(f[f"col_{i}"] for i in range(1, 6)) == 15


def test_perimeter_identity():
    grid = draw_to_grid(range(1, 16))
    f = extract_features(grid)
    assert f["perimeter4"] == 60 - 2 * f["adj_orth"]


def test_symmetry_scores_are_bounded():
    grid = draw_to_grid([1, 2, 4, 5, 6, 8, 10, 11, 12, 14, 15, 16, 20, 22, 25])
    f = extract_features(grid)
    for key in ["sym_lr", "sym_ud", "sym_rot180", "sym_diag_main", "sym_diag_anti"]:
        assert 0.0 <= f[key] <= 1.0


def test_validate_grid_rejects_wrong_selection_count():
    bad = np.zeros((5, 5), dtype=int)
    try:
        validate_grid(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

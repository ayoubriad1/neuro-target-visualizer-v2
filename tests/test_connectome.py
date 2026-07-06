import pandas as pd
import pytest

import connectome
from connectome import propagate_effect
from models import make_region_entry


def test_propagate_effect_empty_regions_returns_empty():
    assert propagate_effect([]) == []


def test_propagate_effect_only_exact_coordinates_returns_empty():
    regions = [make_region_entry("Custom (0, 0, 0)", -9.0, coordinates=(0.0, 0.0, 0.0))]
    assert propagate_effect(regions) == []


def test_propagate_effect_real_matrix_returns_sorted_positive_scores():
    # Real, precomputed connectivity matrix (data/connectivity_matrix.csv) -
    # no network needed, it's a static bundled file.
    regions = [make_region_entry("Striatum (Putamen)", -12.0)]
    result = propagate_effect(regions)
    assert len(result) > 0
    assert all(0 < r.score <= 100.0 for r in result)
    scores = [r.score for r in result]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == pytest.approx(100.0)
    # The selected region itself must never appear as a "propagated" target.
    assert all(r.name != "Striatum (Putamen)" for r in result)


def test_propagate_effect_respects_top_n():
    regions = [make_region_entry("Thalamus", -9.0)]
    result = propagate_effect(regions, top_n=3)
    assert len(result) <= 3


def test_propagate_effect_with_synthetic_matrix(monkeypatch):
    # A small, fully controlled matrix makes the expected scores exactly
    # verifiable, independent of the real data's specific values.
    names = ["A", "B", "C", "D"]
    matrix = pd.DataFrame(
        [
            [1.0, 0.8, -0.5, 0.0],
            [0.8, 1.0, 0.2, 0.1],
            [-0.5, 0.2, 1.0, 0.4],
            [0.0, 0.1, 0.4, 1.0],
        ],
        index=names, columns=names,
    )
    monkeypatch.setattr(connectome, "_load_matrix", lambda: matrix)

    regions = [make_region_entry("A", -15.0)]  # normalized_intensity = 100.0
    result = propagate_effect(regions)
    scores_by_name = {r.name: r.score for r in result}

    # B: connectivity 0.8 * affinity 100 = 80 (raw) -> becomes the new peak (100.0 rescaled)
    # C: negative connectivity (-0.5) is excluded entirely (not a defensible "downstream" claim)
    # D: connectivity 0.0 -> raw score 0 -> excluded (score > 0 required)
    assert set(scores_by_name) == {"B"}
    assert scores_by_name["B"] == pytest.approx(100.0)


def test_propagate_effect_all_atlas_regions_selected_returns_empty(monkeypatch):
    # If literally every region in the matrix is already selected, there are
    # no remaining candidates to propagate to.
    names = ["A", "B"]
    matrix = pd.DataFrame([[1.0, 0.5], [0.5, 1.0]], index=names, columns=names)
    monkeypatch.setattr(connectome, "_load_matrix", lambda: matrix)
    regions = [make_region_entry("A", -9.0), make_region_entry("B", -7.0)]
    assert propagate_effect(regions) == []


def test_propagate_effect_ignores_regions_not_in_matrix(monkeypatch):
    names = ["A", "B"]
    matrix = pd.DataFrame([[1.0, 0.5], [0.5, 1.0]], index=names, columns=names)
    monkeypatch.setattr(connectome, "_load_matrix", lambda: matrix)
    # "Not A Real Region" has no matrix row and must be silently skipped
    # rather than raising a KeyError.
    regions = [make_region_entry("A", -9.0), make_region_entry("Not A Real Region", -20.0)]
    result = propagate_effect(regions)
    assert len(result) == 1
    assert result[0].name == "B"

import pandas as pd
import pytest

import connectome
from connectome import propagate_effect, region_centroids, simulate_diffusion
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


def test_region_centroids_cover_every_matrix_region():
    centroids = region_centroids()
    assert len(centroids) == 28
    for _name, (x, y, z) in centroids.items():
        assert isinstance(x, float) and isinstance(y, float) and isinstance(z, float)


def test_simulate_diffusion_step_zero_is_raw_input():
    regions = [make_region_entry("Thalamus", -15.0)]  # normalized_intensity = 100.0
    steps = simulate_diffusion(regions, n_steps=3)
    assert len(steps) == 4
    assert steps[0]["Thalamus"] == pytest.approx(1.0)
    assert all(v == 0.0 for name, v in steps[0].items() if name != "Thalamus")


def test_simulate_diffusion_spreads_to_neighbors_after_one_step():
    regions = [make_region_entry("Striatum (Putamen)", -15.0)]
    steps = simulate_diffusion(regions, n_steps=1)
    # After one diffusion step, at least one other region must have picked
    # up some signal - otherwise nothing is "propagating" at all.
    assert any(v > 0 for name, v in steps[1].items() if name != "Striatum (Putamen)")


def test_simulate_diffusion_empty_regions_stays_all_zero():
    steps = simulate_diffusion([], n_steps=4)
    assert len(steps) == 5
    assert all(v == 0.0 for step in steps for v in step.values())


def test_simulate_diffusion_with_synthetic_matrix(monkeypatch):
    names = ["A", "B", "C"]
    matrix = pd.DataFrame(
        [[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]], index=names, columns=names,
    )
    monkeypatch.setattr(connectome, "_load_matrix", lambda: matrix)
    regions = [make_region_entry("A", -15.0)]
    steps = simulate_diffusion(regions, n_steps=5, restart_prob=0.5)
    # C is disconnected from A/B entirely - it must never receive any signal.
    assert all(step["C"] == 0.0 for step in steps)
    # B is fully connected to A, so it should pick up signal and the process
    # should be numerically stable (bounded, no runaway growth/explosion).
    assert steps[-1]["B"] > 0.0
    assert all(0.0 <= v <= 1.0 for step in steps for v in step.values())

import numpy as np

import spatial_stats
from mni_space import MNI_SHAPE
from models import make_region_entry
from spatial_stats import MIN_REGIONS, compute_spatial_correlation


def test_returns_none_for_unknown_receptor():
    regions = (
        make_region_entry("Thalamus", -9.0),
        make_region_entry("Hippocampus", -7.0),
        make_region_entry("Amygdala", -5.0),
    )
    assert compute_spatial_correlation(regions, "Not a real receptor") is None


def test_returns_none_below_min_regions(monkeypatch):
    # Even with a valid (fake) density map, fewer than MIN_REGIONS usable
    # regions must short-circuit to None rather than report a meaningless
    # 2-point "correlation".
    fake_density = np.random.default_rng(0).random(MNI_SHAPE)
    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: fake_density)
    regions = (make_region_entry("Thalamus", -9.0), make_region_entry("Hippocampus", -7.0))
    assert len(regions) < MIN_REGIONS
    assert compute_spatial_correlation(regions, "Fake") is None


def test_returns_none_when_affinities_are_constant(monkeypatch):
    fake_density = np.random.default_rng(0).random(MNI_SHAPE)
    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: fake_density)
    regions = (
        make_region_entry("Thalamus", -7.0),
        make_region_entry("Hippocampus", -7.0),
        make_region_entry("Amygdala", -7.0),
    )
    assert compute_spatial_correlation(regions, "Fake") is None


def test_perfect_correlation_with_synthetic_density(monkeypatch):
    # Build a density map that is a known, deterministic function of region
    # identity (encode it directly into the region's mean-mask value) so the
    # observed correlation is verifiably close to +1 - a strong sanity check
    # that the plumbing (mask -> weighted mean -> corrcoef) is wired right,
    # without depending on any specific real region's real anatomy.
    from atlas_regions import get_region_mask

    names = ["Thalamus", "Hippocampus", "Amygdala", "Insula"]
    kcal_values = [-15.0, -11.0, -7.0, -3.0]  # -> normalized 100, 71.4, 42.9, 14.3 (decreasing)
    density = np.zeros(MNI_SHAPE, dtype=np.float64)
    # Assign each region's mask a distinct uniform density level so its
    # weighted mean equals that level, matching the affinity ranking exactly.
    levels = [1.0, 0.7, 0.4, 0.1]
    for name, level in zip(names, levels, strict=True):
        mask = get_region_mask(name)
        density = np.where(mask > 0.5, level, density)

    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: density)
    regions = tuple(make_region_entry(n, k) for n, k in zip(names, kcal_values, strict=True))
    result = compute_spatial_correlation(regions, "Fake")
    assert result is not None
    assert result.r > 0.9
    assert result.n_regions == 4


def test_result_is_deterministic_even_without_cache_reuse(monkeypatch):
    # The permutation test uses a fixed RNG seed specifically so the
    # reported r/p don't jitter across reruns - verify that by clearing the
    # cache between two calls (so the second is a genuine recomputation,
    # not a cache hit) and confirming the result is bit-for-bit identical.
    fake_density = np.random.default_rng(1).random(MNI_SHAPE)
    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: fake_density)
    regions = (
        make_region_entry("Thalamus", -9.0),
        make_region_entry("Hippocampus", -7.0),
        make_region_entry("Amygdala", -3.0),
    )
    result1 = compute_spatial_correlation(regions, "Fake")
    compute_spatial_correlation.clear()
    result2 = compute_spatial_correlation(regions, "Fake")
    assert result1 == result2


def test_p_value_and_r_are_bounded(monkeypatch):
    fake_density = np.random.default_rng(2).random(MNI_SHAPE)
    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: fake_density)
    regions = (
        make_region_entry("Thalamus", -9.0),
        make_region_entry("Hippocampus", -7.0),
        make_region_entry("Amygdala", -3.0),
        make_region_entry("Insula", -12.0),
    )
    result = compute_spatial_correlation(regions, "Fake")
    assert result is not None
    assert -1.0 <= result.r <= 1.0
    assert 0.0 < result.p_value <= 1.0
    assert result.n_permutations == 5000


def test_exact_coordinates_entry_uses_point_density(monkeypatch):
    fake_density = np.zeros(MNI_SHAPE, dtype=np.float64)
    fake_density[45, 63, 36] = 0.9  # MNI (0,0,0)
    monkeypatch.setattr(spatial_stats, "get_receptor_density", lambda name: fake_density)
    regions = (
        make_region_entry("Custom (0, 0, 0)", -9.0, coordinates=(0.0, 0.0, 0.0)),
        make_region_entry("Thalamus", -7.0),
        make_region_entry("Hippocampus", -3.0),
    )
    result = compute_spatial_correlation(regions, "Fake")
    assert result is not None
    assert result.n_regions == 3


def test_real_receptor_end_to_end():
    # Real network fetch (D2, cached under ~/neuromaps-data by
    # tests/test_receptor_atlas.py) - confirms the whole pipeline works
    # against actual PET data, not just synthetic stand-ins.
    regions = (
        make_region_entry("Thalamus", -12.0),
        make_region_entry("Hippocampus", -8.0),
        make_region_entry("Amygdala", -4.0),
    )
    result = compute_spatial_correlation(regions, "D2 (dopamine receptor)")
    assert result is not None
    assert -1.0 <= result.r <= 1.0
    assert 0.0 < result.p_value <= 1.0
    assert result.n_regions == 3
    assert result.receptor_name == "D2 (dopamine receptor)"

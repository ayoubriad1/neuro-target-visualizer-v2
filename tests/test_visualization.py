import numpy as np
import pytest

from visualization import MNI_SHAPE, _mni_to_voxel, create_activation_volume


def test_mni_to_voxel_roundtrip_origin():
    # MNI (0,0,0) should map to the voxel center implied by the affine
    vi, vj, vk = _mni_to_voxel(0, 0, 0)
    assert (vi, vj, vk) == (45, 63, 36)


def test_create_activation_volume_shape_and_range():
    img = create_activation_volume([("Hippocampus", 80.0)], sigma=6.0)
    data = img.get_fdata()
    assert data.shape == MNI_SHAPE
    assert data.min() >= 0.0
    assert data.max() <= 1.0
    assert data.max() > 0.0


def test_create_activation_volume_ignores_nonpositive_scores():
    img_zero = create_activation_volume([("Hippocampus", 0.0)])
    assert np.allclose(img_zero.get_fdata(), 0.0)


def test_create_activation_volume_empty_region_list():
    img = create_activation_volume([])
    assert np.allclose(img.get_fdata(), 0.0)


def test_create_activation_volume_exact_coordinates_not_mirrored():
    # A custom coordinate at x=40 (clearly off-midline) must NOT also light
    # up x=-40 - unlike named regions, an exact user-supplied point is never
    # mirrored across the midline.
    img = create_activation_volume([("Custom (40, 0, 0)", 80.0, (40.0, 0.0, 0.0))], sigma=6.0)
    data = img.get_fdata()
    vi_pos, vj, vk = _mni_to_voxel(40, 0, 0)
    vi_neg, _, _ = _mni_to_voxel(-40, 0, 0)
    assert data[vi_pos, vj, vk] > 0.5
    assert data[vi_neg, vj, vk] < 0.01


def test_create_activation_volume_exact_coordinates_peak_location():
    img = create_activation_volume([("Custom (10, -20, 5)", 100.0, (10.0, -20.0, 5.0))], sigma=6.0)
    data = img.get_fdata()
    peak_voxel = np.unravel_index(np.argmax(data), data.shape)
    assert peak_voxel == tuple(_mni_to_voxel(10, -20, 5))


def test_create_activation_volume_accepts_mixed_named_and_exact():
    img = create_activation_volume([
        ("Hippocampus", 60.0),
        ("Custom (0, 0, 0)", 80.0, (0.0, 0.0, 0.0)),
    ], sigma=6.0)
    assert img.get_fdata().max() > 0.0


def test_create_activation_volume_receptor_weight_reshapes_the_map():
    # Real end-to-end integration: fetches the D2 receptor density map (see
    # tests/test_receptor_atlas.py, which caches it under ~/neuromaps-data).
    # A real PET density map isn't spatially flat, so weighting must actually
    # change the map relative to the unweighted version.
    pairs = [("Hippocampus", 80.0)]
    unweighted = create_activation_volume(pairs, sigma=6.0).get_fdata()
    weighted = create_activation_volume(
        pairs, sigma=6.0, receptor_weight="D2 (dopamine receptor)"
    ).get_fdata()
    assert not np.allclose(unweighted, weighted)
    assert weighted.max() == pytest.approx(1.0)
    assert weighted.min() >= 0.0


def test_create_activation_volume_unknown_receptor_weight_leaves_map_unchanged():
    pairs = [("Hippocampus", 80.0)]
    unweighted = create_activation_volume(pairs, sigma=6.0).get_fdata()
    still_unweighted = create_activation_volume(
        pairs, sigma=6.0, receptor_weight="Not a real receptor"
    ).get_fdata()
    assert np.allclose(unweighted, still_unweighted)

import numpy as np

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

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

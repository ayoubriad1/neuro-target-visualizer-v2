"""Tests for atlas_regions.py.

These fetch real atlas data (Harvard-Oxford, Pauli 2017) via nilearn on first
run, so they require network access the first time; nilearn caches the
downloads under ~/nilearn_data afterwards, matching the app's own behaviour.
"""
import numpy as np
import pytest

from atlas_regions import ATLAS_REGIONS, get_atlas_source, get_region_mask, is_atlas_backed
from brain_regions import get_region_names
from mni_space import MNI_SHAPE

ILLUSTRATIVE_REGIONS = set(get_region_names()) - ATLAS_REGIONS


def test_atlas_regions_are_a_real_subset_of_brain_regions():
    assert ATLAS_REGIONS.issubset(set(get_region_names()))
    # Every atlas-backed region must have a human-readable source.
    for name in ATLAS_REGIONS:
        assert get_atlas_source(name)


def test_illustrative_regions_have_no_atlas_source():
    for name in ILLUSTRATIVE_REGIONS:
        assert not is_atlas_backed(name)
        assert get_atlas_source(name) is None
        assert get_region_mask(name) is None


@pytest.mark.parametrize("name", sorted(ATLAS_REGIONS))
def test_atlas_mask_shape_and_range(name):
    mask = get_region_mask(name)
    assert mask.shape == MNI_SHAPE
    assert mask.min() >= 0.0
    assert mask.max() <= 1.0
    assert mask.max() > 0.0, f"{name} atlas mask is all-zero"


def test_bilateral_subcortical_mask_spans_both_hemispheres():
    # Thalamus is a large bilateral structure: voxels should appear on both
    # sides of the midline (i index 45, since MNI x=0 maps to voxel i=45).
    mask = get_region_mask("Thalamus")
    xs = np.where(mask > 0.1)[0]
    assert (xs < 45).any() and (xs > 45).any()

"""Tests for receptor_atlas.py.

get_receptor_density fetches real PET data (via the `neuromaps` package) on
first run, so it requires network access the first time; the data is cached
under ~/neuromaps-data afterwards, matching this app's nilearn cache
behaviour. To keep CI/test runtime reasonable, only one representative
receptor is actually fetched end-to-end here - the rest of the module
(name/citation coverage, unknown-name handling) is tested without a network
call.
"""
import pytest

from mni_space import MNI_SHAPE
from receptor_atlas import (
    RECEPTOR_CITATIONS,
    RECEPTOR_MAPS,
    RECEPTOR_NAMES,
    get_receptor_citation,
    get_receptor_density,
)


def test_every_receptor_has_a_citation():
    assert set(RECEPTOR_MAPS) == set(RECEPTOR_CITATIONS)
    for name in RECEPTOR_MAPS:
        assert get_receptor_citation(name)


def test_receptor_names_sorted_and_match_maps():
    assert RECEPTOR_NAMES == sorted(RECEPTOR_MAPS)


def test_get_receptor_density_unknown_name_returns_none():
    assert get_receptor_density("Not a real receptor") is None


def test_get_receptor_citation_unknown_name_returns_none():
    assert get_receptor_citation("Not a real receptor") is None


def test_get_receptor_density_shape_and_range():
    # D2 is the one receptor map actually fetched over the network in this
    # test suite (see module docstring) - real PET data, resampled onto this
    # app's MNI152 2mm grid and normalized to [0, 1].
    density = get_receptor_density("D2 (dopamine receptor)")
    assert density.shape == MNI_SHAPE
    assert density.ndim == 3
    assert density.min() >= 0.0
    assert density.max() <= 1.0 + 1e-9
    assert density.max() > 0.0


@pytest.mark.parametrize("name", RECEPTOR_NAMES)
def test_every_receptor_density_is_3d_grid(name):
    # Regression guard: some neuromaps PET volumes ship as 4D (91,109,91,1)
    # with a trailing singleton axis. Every map must come back as a bare 3D
    # (91,109,91) grid - a 4D one silently broke the elementwise density
    # weighting in visualization._compute_activation_array (broadcast error).
    # Fetches all 18 maps over the network on first run; cached afterwards.
    density = get_receptor_density(name)
    assert density.shape == MNI_SHAPE
    assert density.ndim == 3

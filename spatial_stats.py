"""Spatial correspondence test: does the user's selected set of regions line
up with where a chosen receptor is actually dense, more than a random set of
atlas regions of the same size would?

This is deliberately **not** a vertex-level "spin test" in the
Alexander-Bloch/Vasa/Burt sense (those rotate a spherical projection of a
registered cortical-surface parcellation to build a spatial-autocorrelation-
preserving null - out of scope here, since this app's region set mixes
cortical and subcortical atlases with no single unified surface parcellation
object to spin). Instead this is a **region-resampling permutation test**:
the null distribution comes from swapping in random atlas regions (same
count as the user's selection) in place of the ones actually chosen. It
answers a related but narrower question - "is the correspondence between MY
chosen regions and this receptor stronger than a random set of N atlas
regions would show?" - not the stronger claim a true spin test would
support. See docs/RECEPTOR_WEIGHTING.md for the full caveat.
"""
from dataclasses import dataclass

import numpy as np
import streamlit as st

from atlas_regions import ATLAS_REGIONS, get_region_mask
from mni_space import MNI_AFFINE
from models import RegionEntry
from receptor_atlas import get_receptor_density

MIN_REGIONS = 3
N_PERMUTATIONS = 5000
# Fixed seed: a permutation p-value that jittered on every Streamlit rerun
# (e.g. moving an unrelated slider) would look like a bug rather than the
# expected behavior of a stochastic test - a fixed seed makes the reported
# r/p reproducible for a given region selection + receptor.
_PERMUTATION_SEED = 42


@dataclass(frozen=True)
class SpatialTestResult:
    r: float
    p_value: float
    n_regions: int
    n_permutations: int
    receptor_name: str


def _mni_to_voxel(x: float, y: float, z: float) -> tuple[int, int, int]:
    coord = np.array([x, y, z, 1.0])
    voxel = np.linalg.inv(MNI_AFFINE).dot(coord)[:3]
    rounded = np.round(voxel).astype(int)
    return int(rounded[0]), int(rounded[1]), int(rounded[2])


def _mean_density_in_region(name: str, density: np.ndarray) -> float | None:
    mask = get_region_mask(name)
    if mask is None or mask.sum() == 0:
        return None
    return float(np.average(density, weights=mask))


def _density_at_coordinates(coordinates: tuple[float, float, float],
                            density: np.ndarray) -> float | None:
    i, j, k = _mni_to_voxel(*coordinates)
    shape = density.shape
    if not (0 <= i < shape[0] and 0 <= j < shape[1] and 0 <= k < shape[2]):
        return None
    return float(density[i, j, k])


@st.cache_data(show_spinner=False)
def compute_spatial_correlation(
    regions: tuple[RegionEntry, ...], receptor_weight: str
) -> SpatialTestResult | None:
    """Returns None if there's nothing meaningful to test: fewer than
    MIN_REGIONS regions have a usable density value, the affinities or
    sampled densities are constant (correlation undefined), or the atlas
    doesn't have enough regions to build a same-size random comparison set.
    """
    density = get_receptor_density(receptor_weight)
    if density is None:
        return None

    # Precompute once: mean receptor density within every atlas region's
    # mask. Reused both to score the user's own named regions and as the
    # fixed pool the permutation test resamples from - avoids recomputing a
    # masked average over the full (91,109,91) grid on every one of the
    # N_PERMUTATIONS trials.
    pool: dict[str, float] = {}
    for name in ATLAS_REGIONS:
        val = _mean_density_in_region(name, density)
        if val is not None:
            pool[name] = val

    affinities = []
    density_values = []
    for r in regions:
        if r.coordinates is not None:
            val = _density_at_coordinates(r.coordinates, density)
        else:
            val = pool.get(r.name)
        if val is None:
            continue
        affinities.append(r.normalized_intensity)
        density_values.append(val)

    n = len(affinities)
    if n < MIN_REGIONS or len(pool) < n:
        return None

    affinities_arr = np.array(affinities, dtype=np.float64)
    density_arr = np.array(density_values, dtype=np.float64)
    if np.std(affinities_arr) == 0 or np.std(density_arr) == 0:
        return None

    observed_r = float(np.corrcoef(affinities_arr, density_arr)[0, 1])

    rng = np.random.default_rng(_PERMUTATION_SEED)
    pool_values = np.array(list(pool.values()), dtype=np.float64)
    null_rs = np.empty(N_PERMUTATIONS, dtype=np.float64)
    for p in range(N_PERMUTATIONS):
        sample = rng.choice(pool_values, size=n, replace=False)
        if np.std(sample) == 0:
            null_rs[p] = 0.0
            continue
        null_rs[p] = np.corrcoef(affinities_arr, sample)[0, 1]

    p_value = float((np.sum(np.abs(null_rs) >= abs(observed_r)) + 1) / (N_PERMUTATIONS + 1))

    return SpatialTestResult(
        r=observed_r, p_value=p_value, n_regions=n,
        n_permutations=N_PERMUTATIONS, receptor_name=receptor_weight,
    )

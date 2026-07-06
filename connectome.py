"""Circuit-level effect propagation: a directly-activated region's effect
doesn't stay confined to where it binds - it propagates through functional
circuits (e.g. a striatal drug effect reaching motor, mood and cognitive
domains via separate cortico-striato-thalamic loops). This module estimates
a simple linear "propagated effect" for atlas regions the user did NOT
directly select, weighted by real functional connectivity to the regions
that were.

Data: a precomputed 28x28 group-average functional connectivity matrix
(data/connectivity_matrix.csv), derived from real naturalistic-viewing fMRI
(see scripts/compute_connectivity_matrix.py for exactly how, and
docs/CONNECTOME_PROPAGATION.md for the full methodology and caveats). This
is a linear estimate, not a validated pharmacokinetic or circuit simulation
- see propagate_effect's docstring for precisely what the score does and
doesn't mean.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy import ndimage

from atlas_regions import get_region_mask
from mni_space import MNI_AFFINE
from models import RegionEntry

# Resolved relative to this file, not the process's current working
# directory - Streamlit can be launched from a different CWD depending on
# how it's started (e.g. the Docker entrypoint vs. a local dev launcher),
# which would otherwise make this path fail unpredictably.
_MATRIX_PATH = Path(__file__).parent / "data" / "connectivity_matrix.csv"


@st.cache_resource(show_spinner=False)
def _load_matrix() -> pd.DataFrame:
    return pd.read_csv(_MATRIX_PATH, index_col=0)


@dataclass(frozen=True)
class PropagatedRegion:
    name: str
    score: float  # 0-100, relative to the strongest propagated (non-selected) region


def propagate_effect(regions: list[RegionEntry], top_n: int = 8) -> list[PropagatedRegion]:
    """For each atlas region NOT among the user's directly-selected named
    regions, estimates a propagated-effect score as the connectivity-weighted
    sum of the selected regions' normalized affinities:

        propagated[j] = sum_i  connectivity[i, j] * affinity[i]   (i selected, j not)

    Only positive connectivity contributes - an anti-correlated region isn't
    a defensible "downstream effect" claim from a same-sign linear model.
    Scores are rescaled to 0-100 relative to the strongest propagated
    region, purely for display - they are on a **different scale** than the
    directly-entered affinities and must not be compared to them directly.

    Exact-coordinate entries (no atlas region name) don't have a matrix row
    and are excluded from both the source side and the candidate side.

    Returns the top `top_n` propagated regions sorted by score descending
    (score > 0 only), or an empty list if no selected region has a matrix
    row, or every candidate's propagated score is non-positive.
    """
    matrix = _load_matrix()
    selected_in_matrix = [
        (r.name, r.normalized_intensity) for r in regions
        if r.coordinates is None and r.name in matrix.index
    ]
    if not selected_in_matrix:
        return []

    selected_names = {name for name, _ in selected_in_matrix}
    candidates = [name for name in matrix.columns if name not in selected_names]
    if not candidates:
        return []

    raw_scores: dict[str, float] = {}
    for candidate in candidates:
        total = 0.0
        for name, affinity in selected_in_matrix:
            weight = matrix.loc[name, candidate]
            if weight > 0:
                total += weight * affinity
        raw_scores[candidate] = total

    peak = max(raw_scores.values())
    if peak <= 0:
        return []

    ranked = sorted(raw_scores.items(), key=lambda kv: kv[1], reverse=True)
    return [
        PropagatedRegion(name=name, score=100.0 * value / peak)
        for name, value in ranked[:top_n] if value > 0
    ]


@st.cache_resource(show_spinner=False)
def region_centroids() -> dict[str, tuple[float, float, float]]:
    """MNI (mm) centroid of every region in the connectivity matrix, for
    plotting each region as a single node in the propagation-animation
    network view. Computed as the mask-weighted center of mass in voxel
    space, then converted to world (mm) coordinates via this app's MNI152
    2mm affine - a single representative point, not the region's full
    extent (matches how the animation renders it: one node per region).
    """
    matrix = _load_matrix()
    centroids = {}
    for name in matrix.index:
        mask = get_region_mask(name)
        if mask is None:
            continue
        i, j, k = ndimage.center_of_mass(mask)
        x, y, z = MNI_AFFINE.dot([i, j, k, 1.0])[:3]
        centroids[name] = (float(x), float(y), float(z))
    return centroids


_DEFAULT_N_STEPS = 8
_DEFAULT_RESTART_PROB = 0.5


def simulate_diffusion(
    regions: list[RegionEntry], n_steps: int = _DEFAULT_N_STEPS,
    restart_prob: float = _DEFAULT_RESTART_PROB,
) -> list[dict[str, float]]:
    """A discrete-step random-walk-with-restart diffusion over the real
    functional connectivity graph: at each step, signal already at a region
    spreads to its positively-connected neighbors (weighted by connection
    strength, row-normalized so each region distributes at most its own
    current signal), while `restart_prob` keeps re-injecting the original
    directly-entered affinities at their source regions - the standard
    formulation used for spreading-process modeling on brain networks
    (e.g. Abdelnour et al. 2014's linear diffusion model; the same
    restart-based idea as personalized PageRank).

    Returns a list of `n_steps + 1` dicts (step 0 = the raw input, i.e. only
    the directly-selected regions, at their normalized_intensity/100 value;
    each subsequent step is one diffusion iteration), each mapping every
    region name in the connectivity matrix to its current activation level.
    These are **relative units from an abstract iterative model - not
    seconds/minutes and not a validated pharmacokinetic timescale.** Returns
    a list containing only the all-zero step 0 if no selected region has a
    matrix row.
    """
    matrix = _load_matrix()
    names = list(matrix.index)
    index = {name: i for i, name in enumerate(names)}
    n = len(names)

    x0 = np.zeros(n, dtype=np.float64)
    for r in regions:
        if r.coordinates is None and r.name in index:
            x0[index[r.name]] = r.normalized_intensity / 100.0

    w_pos = np.clip(matrix.values, 0.0, None)
    np.fill_diagonal(w_pos, 0.0)
    row_sums = w_pos.sum(axis=1, keepdims=True)
    transition = np.divide(w_pos, row_sums, out=np.zeros_like(w_pos), where=row_sums > 0)

    steps = [x0]
    x = x0
    for _ in range(n_steps):
        x = (1.0 - restart_prob) * (transition.T @ x) + restart_prob * x0
        steps.append(x)

    return [dict(zip(names, step, strict=True)) for step in steps]

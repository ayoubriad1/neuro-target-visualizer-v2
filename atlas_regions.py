"""Atlas-backed region masks.

Replaces the illustrative point+Gaussian model (brain_regions.py) with real,
citable, published parcellation masks for the regions that have one available
through nilearn. Verified sources, all resampled/fetched onto the exact
MNI152 2mm grid (mni_space.MNI_SHAPE / MNI_AFFINE) already used everywhere
else in this app:

- Harvard-Oxford cortical + subcortical probabilistic atlases (maxprob,
  thresholded at 25%), distributed with FSL (Makris et al. 2006; Frazier et
  al. 2005; Desikan et al. 2006). Fetched via nilearn at MNI152 2mm - no
  resampling needed, the shipped volume already matches this app's grid.
- Pauli, Nili & Tyszka (2017), "A high-resolution probabilistic in vivo atlas
  of human subcortical brain nuclei", Scientific Data 4:170063. Covers basal
  ganglia / midbrain structures absent from Harvard-Oxford (substantia nigra,
  VTA, hypothalamus). Published at 1mm and resampled here to 2mm.

A few structures have no standard, openly-fetchable atlas at all (small
brainstem nuclei like the raphe nuclei / locus coeruleus, and the cerebellum,
which needs its own dedicated parcellation) and have been dropped from the
region list entirely rather than kept as unverified illustrative points -
see brain_regions.py's module docstring for the reasoning. get_region_mask()
returns None for any name it doesn't recognize, so callers can still fall
back gracefully if an illustrative-only region is ever reintroduced.
"""
import nibabel as nib
import numpy as np
import streamlit as st
from scipy import ndimage

from mni_space import MNI_AFFINE, MNI_SHAPE

# region name (must match brain_regions.BRAIN_REGIONS keys) -> (left label, right label)
_HO_SUBCORTICAL_PAIRS = {
    "Thalamus": ("Left Thalamus", "Right Thalamus"),
    "Striatum (Caudate)": ("Left Caudate", "Right Caudate"),
    "Striatum (Putamen)": ("Left Putamen", "Right Putamen"),
    "Globus Pallidus": ("Left Pallidum", "Right Pallidum"),
    "Hippocampus": ("Left Hippocampus", "Right Hippocampus"),
    "Amygdala": ("Left Amygdala", "Right Amygdala"),
    "Nucleus Accumbens": ("Left Accumbens", "Right Accumbens"),
}

# region name -> Harvard-Oxford cortical label(s) to union (already bilateral
# in each label). Tuples of >1 label combine the atlas's separate
# anterior/posterior divisions into one region.
_HO_CORTICAL_LABELS = {
    "Anterior Cingulate Cortex": ("Cingulate Gyrus, anterior division",),
    "Posterior Cingulate Cortex": ("Cingulate Gyrus, posterior division",),
    "Insula": ("Insular Cortex",),
    "Primary Motor Cortex": ("Precentral Gyrus",),
    "Somatosensory Cortex": ("Postcentral Gyrus",),
    "Visual Cortex (V1)": ("Intracalcarine Cortex",),
    "Auditory Cortex": ("Heschl's Gyrus (includes H1 and H2)",),
    "Temporal Pole": ("Temporal Pole",),
    "Parietal Cortex (SPL)": ("Superior Parietal Lobule",),
    # Replaces the old illustrative "Orbitofrontal Cortex" point with a real mask.
    "Orbitofrontal Cortex": ("Frontal Orbital Cortex",),
    # Replace the old illustrative "Prefrontal Cortex (DLPFC/VMPFC)" points:
    # DLPFC/VMPFC are functional labels that don't correspond to a single atlas
    # region, so these use the real Harvard-Oxford anatomical names instead of
    # a functional label nothing in the atlas actually matches.
    "Middle Frontal Gyrus": ("Middle Frontal Gyrus",),
    "Frontal Medial Cortex": ("Frontal Medial Cortex",),
    "Frontal Pole": ("Frontal Pole",),
    "Precuneous Cortex": ("Precuneous Cortex",),
    "Angular Gyrus": ("Angular Gyrus",),
}

# region name -> Pauli 2017 label(s) to union (already bilateral / midline)
_PAULI_LABELS = {
    "Substantia Nigra": ("SNc", "SNr"),
    "Ventral Tegmental Area": ("VTA",),
    "Hypothalamus": ("HTH",),
    "Subthalamic Nucleus": ("STH",),
    "Habenula": ("HN",),
    "Ventral Pallidum": ("VeP",),
}

ATLAS_REGIONS = set(_HO_SUBCORTICAL_PAIRS) | set(_HO_CORTICAL_LABELS) | set(_PAULI_LABELS)

ATLAS_SOURCE = {
    **{name: "Harvard-Oxford subcortical" for name in _HO_SUBCORTICAL_PAIRS},
    **{name: "Harvard-Oxford cortical" for name in _HO_CORTICAL_LABELS},
    **{name: "Pauli et al. 2017" for name in _PAULI_LABELS},
}

ATLAS_CITATIONS = {
    "Harvard-Oxford subcortical": "Harvard-Oxford atlas (FSL); Frazier et al. 2005, Am J Psychiatry",
    "Harvard-Oxford cortical": "Harvard-Oxford atlas (FSL); Desikan et al. 2006, NeuroImage",
    "Pauli et al. 2017": "Pauli, Nili & Tyszka (2017), Scientific Data 4:170063",
}


def is_atlas_backed(name):
    return name in ATLAS_REGIONS


def get_atlas_source(name):
    """Human-readable atlas source label, or None if illustrative-only."""
    return ATLAS_SOURCE.get(name)


@st.cache_resource(show_spinner=False)
def _load_harvard_oxford(atlas_name):
    from nilearn import datasets
    atlas = datasets.fetch_atlas_harvard_oxford(atlas_name)
    img = nib.load(atlas.maps) if isinstance(atlas.maps, str) else atlas.maps
    return np.asarray(img.get_fdata()), list(atlas.labels)


@st.cache_resource(show_spinner=False)
def _load_pauli_2017():
    from nilearn import datasets
    from nilearn.image import resample_img
    atlas = datasets.fetch_atlas_pauli_2017()
    img = nib.load(atlas.maps) if isinstance(atlas.maps, str) else atlas.maps
    resampled = resample_img(img, target_affine=MNI_AFFINE, target_shape=MNI_SHAPE,
                             interpolation="continuous")
    return np.asarray(resampled.get_fdata()), list(atlas.labels)


def _label_mask(data, labels, label_name):
    return (data == labels.index(label_name)).astype(np.float64)


def _smooth_binary_mask(mask, sigma_vox=1.0):
    """Light Gaussian smoothing of a deterministic (hard-edged) atlas mask,
    for anti-aliased rendering only - it doesn't add anatomical information,
    just avoids blocky voxel edges in the 3-D views.
    """
    return np.clip(ndimage.gaussian_filter(mask, sigma=sigma_vox), 0.0, 1.0)


def get_region_mask(name):
    """Return a (91,109,91) float64 array in [0, 1] - a real anatomical
    probability/membership map for an atlas-backed region - or None if `name`
    has no atlas backing (caller should fall back to the illustrative
    point+Gaussian model in that case).
    """
    if name in _HO_SUBCORTICAL_PAIRS:
        data, labels = _load_harvard_oxford("sub-maxprob-thr25-2mm")
        left, right = _HO_SUBCORTICAL_PAIRS[name]
        mask = _label_mask(data, labels, left) + _label_mask(data, labels, right)
        return _smooth_binary_mask(np.clip(mask, 0.0, 1.0))

    if name in _HO_CORTICAL_LABELS:
        data, labels = _load_harvard_oxford("cort-maxprob-thr25-2mm")
        mask = np.zeros(MNI_SHAPE, dtype=np.float64)
        for label_name in _HO_CORTICAL_LABELS[name]:
            mask = np.maximum(mask, _label_mask(data, labels, label_name))
        return _smooth_binary_mask(mask)

    if name in _PAULI_LABELS:
        data, labels = _load_pauli_2017()
        prob = np.zeros(MNI_SHAPE, dtype=np.float64)
        for label_name in _PAULI_LABELS[name]:
            prob = np.maximum(prob, data[..., labels.index(label_name)])
        return np.clip(prob, 0.0, 1.0)

    return None

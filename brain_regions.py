"""Illustrative-point fallback for regions with no atlas coverage, plus the
merged region-name list the UI actually offers (see get_region_names()).

Provenance note (read before trusting these numbers for a publication): these
remaining points are hand-curated, approximate MNI152 coordinates - NOT
extracted from a specific published atlas or meta-analysis. The original 25
names in this project were originally selected from an older stereotaxic
neurosurgical atlas (a printed reference, not a versioned/citable digital
dataset), which is why they couldn't be tied to a specific citation.

19 of the original 25 names were migrated to a real, cited atlas mask in
atlas_regions.py (see ATLAS_REGIONS there); of the remaining 6, 3 had a direct
or near-direct atlas equivalent and were replaced outright (Orbitofrontal
Cortex, and the functional "DLPFC"/"VMPFC" labels replaced by their real
Harvard-Oxford anatomical names, Middle Frontal Gyrus / Frontal Medial
Cortex). The other 3 (Raphe Nuclei, Locus Coeruleus, Cerebellum) have no
standard, openly-fetchable atlas at all and were dropped entirely rather than
kept as unverified data.

Only the names below still use a hand-placed point, mirrored across the
midline by default (see MIDLINE_EPS_MM in visualization.py) since real ligand
binding is normally bilateral. See ENHANCEMENT_REPORT.md for exact citations
and CHANGELOG.md for the full migration history.
"""
BRAIN_REGIONS: dict[str, tuple[float, float, float]] = {}


# Regions that sit too deep for the cortical-surface views ("Interactive 3D",
# "3D Surface") to show meaningfully: vol_to_surf samples signal near the pial
# surface, and a Gaussian/mask centered in these structures barely reaches it.
# app.py uses this to warn the user instead of silently rendering what looks
# like "no binding".
SUBCORTICAL_REGIONS = {
    "Striatum (Caudate)",
    "Striatum (Putamen)",
    "Nucleus Accumbens",
    "Hippocampus",
    "Amygdala",
    "Thalamus",
    "Hypothalamus",
    "Substantia Nigra",
    "Ventral Tegmental Area",
    "Globus Pallidus",
    "Subthalamic Nucleus",
    "Habenula",
    "Ventral Pallidum",
}


def get_region_names():
    """All region names the UI offers: the illustrative fallback points in
    BRAIN_REGIONS, plus every atlas-backed region from atlas_regions.py (most
    of which have no illustrative point at all - the atlas mask is their only
    representation).
    """
    from atlas_regions import ATLAS_REGIONS
    return sorted(set(BRAIN_REGIONS) | ATLAS_REGIONS)


def get_coordinates(name):
    return BRAIN_REGIONS[name]


def is_subcortical(name):
    return name in SUBCORTICAL_REGIONS

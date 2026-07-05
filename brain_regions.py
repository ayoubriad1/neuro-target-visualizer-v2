# Provenance note (read before trusting these numbers for a publication):
# these are hand-curated, approximate MNI152 coordinates chosen to be
# "typically representative" of each named region, illustrative reference
# points for visualization — they are NOT extracted from a specific published
# atlas or meta-analysis.
#
# 19 of these 25 names now have a real, cited atlas mask in atlas_regions.py
# (see ATLAS_REGIONS there); for those, the coordinate below is unused
# (vestigial) since visualization.py checks atlas_regions.get_region_mask()
# first. Only the 6 names NOT in ATLAS_REGIONS still use the point here,
# mirrored across the midline by default (see MIDLINE_EPS_MM in
# visualization.py) since real ligand binding is normally bilateral.
# See ENHANCEMENT_REPORT.md for exact citations and what remains uncovered.
BRAIN_REGIONS = {
    "Striatum (Caudate)": (12, 12, 8),
    "Striatum (Putamen)": (28, 4, 2),
    "Nucleus Accumbens": (10, 12, -8),
    "Prefrontal Cortex (DLPFC)": (-40, 32, 30),
    "Prefrontal Cortex (VMPFC)": (2, 46, -10),
    "Orbitofrontal Cortex": (-30, 28, -14),
    "Anterior Cingulate Cortex": (0, 34, 18),
    "Posterior Cingulate Cortex": (0, -50, 30),
    "Hippocampus": (-28, -22, -14),
    "Amygdala": (-24, -4, -18),
    "Thalamus": (0, -12, 8),
    "Hypothalamus": (0, -4, -10),
    "Substantia Nigra": (-10, -18, -12),
    "Ventral Tegmental Area": (0, -16, -14),
    "Raphe Nuclei": (0, -28, -24),
    "Locus Coeruleus": (-2, -36, -24),
    "Insula": (-36, 14, 2),
    "Cerebellum": (0, -60, -30),
    "Primary Motor Cortex": (-38, -22, 56),
    "Somatosensory Cortex": (-42, -28, 54),
    "Visual Cortex (V1)": (4, -82, 4),
    "Auditory Cortex": (-54, -22, 8),
    "Temporal Pole": (-38, 14, -30),
    "Parietal Cortex (SPL)": (-26, -58, 52),
    "Globus Pallidus": (16, 2, -2),
}


# Regions that sit too deep for the cortical-surface views ("Interactive 3D",
# "3D Surface") to show meaningfully: vol_to_surf samples signal near the pial
# surface, and a Gaussian centered in these structures barely reaches it at
# the sigma used in visualization.py. app.py uses this to warn the user
# instead of silently rendering what looks like "no binding".
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
    "Raphe Nuclei",
    "Locus Coeruleus",
    "Cerebellum",
    "Globus Pallidus",
}


def get_region_names():
    return sorted(BRAIN_REGIONS.keys())


def get_coordinates(name):
    return BRAIN_REGIONS[name]


def is_subcortical(name):
    return name in SUBCORTICAL_REGIONS

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


def get_region_names():
    return sorted(BRAIN_REGIONS.keys())


def get_coordinates(name):
    return BRAIN_REGIONS[name]

"""Curated gene/receptor -> atlas brain-region lookup, for *suggesting*
where a docked target likely engages when a bulk docking-results import
gives a gene/PDB target but no brain-region column (see docking_import.py).

Why this can't just come from RCSB: the RCSB Data API was checked directly
(see rcsb_lookup.py) and confirmed to expose only structural/genetic
metadata - UniProt accession, gene symbol, source organism, GO terms. There
is no anatomical or brain-region field anywhere in it. Region association is
a pharmacology/neuroanatomy fact, not a crystallography one, so this module
hand-curates it instead, reusing the same 18 PET-imaging targets already
weighted in receptor_atlas.py wherever they overlap (same citations - see
RECEPTOR_CITATIONS there) so the two modules never disagree on a source.

Each entry lists the *principal* reported site(s) of highest receptor
density among this app's 28 atlas-backed regions - not an exhaustive
expression map, and not every region a gene is expressed in at all (most are
expressed far more broadly at low levels). Regions with no standard atlas
mask (e.g. locus coeruleus, raphe nuclei) were already dropped app-wide (see
brain_regions.py) and can't appear here either.

Consistent with docking_import.py's own design (a Vina score has no inherent
region association - the user picks it), this module only ever *suggests*
candidate regions in a hint/warning message. It never silently assigns one -
final region assignment stays the researcher's call.
"""
from receptor_atlas import RECEPTOR_CITATIONS

# gene symbol / common synonym (case-insensitive) -> receptor_atlas.py display name
_GENE_ALIASES: dict[str, str] = {
    "DRD1": "D1 (dopamine receptor)", "D1": "D1 (dopamine receptor)",
    "DRD2": "D2 (dopamine receptor)", "D2": "D2 (dopamine receptor)",
    "SLC6A3": "DAT (dopamine transporter)", "DAT": "DAT (dopamine transporter)",
    "SLC6A2": "NET (norepinephrine transporter)", "NET": "NET (norepinephrine transporter)",
    "HTR1A": "5-HT1a (serotonin receptor)", "5-HT1A": "5-HT1a (serotonin receptor)",
    "HTR1B": "5-HT1b (serotonin receptor)", "5-HT1B": "5-HT1b (serotonin receptor)",
    "HTR2A": "5-HT2a (serotonin receptor)", "5-HT2A": "5-HT2a (serotonin receptor)",
    "HTR4": "5-HT4 (serotonin receptor)", "5-HT4": "5-HT4 (serotonin receptor)",
    "SLC6A4": "5-HTT (serotonin transporter)", "SERT": "5-HTT (serotonin transporter)",
    "SLC18A3": "VAChT (acetylcholine transporter)", "VACHT": "VAChT (acetylcholine transporter)",
    "CHRNA4": "α4β2 (nicotinic acetylcholine receptor)",
    "CHRNB2": "α4β2 (nicotinic acetylcholine receptor)",
    "CHRM1": "M1 (muscarinic acetylcholine receptor)",
    "GRM5": "mGluR5 (glutamate receptor)",
    "GRIN1": "NMDA (glutamate receptor)",
    "GRIN2A": "NMDA (glutamate receptor)",
    "GRIN2B": "NMDA (glutamate receptor)",
    "GABRA1": "GABAa (GABA receptor)",
    "HRH3": "H3 (histamine receptor)",
    "CNR1": "CB1 (cannabinoid receptor)",
    "OPRM1": "MOR (mu-opioid receptor)",
}

# receptor_atlas.py display name -> principal atlas region(s), highest
# reported density / most-cited site(s) for that target (see module docstring)
_RECEPTOR_TO_REGIONS: dict[str, tuple[str, ...]] = {
    "D1 (dopamine receptor)": ("Striatum (Caudate)", "Striatum (Putamen)", "Nucleus Accumbens"),
    "D2 (dopamine receptor)": (
        "Striatum (Caudate)", "Striatum (Putamen)", "Nucleus Accumbens",
        "Substantia Nigra", "Ventral Tegmental Area",
    ),
    "DAT (dopamine transporter)": (
        "Striatum (Caudate)", "Striatum (Putamen)", "Substantia Nigra", "Ventral Tegmental Area",
    ),
    "NET (norepinephrine transporter)": ("Thalamus", "Hypothalamus"),
    "5-HT1a (serotonin receptor)": ("Hippocampus", "Anterior Cingulate Cortex", "Orbitofrontal Cortex"),
    "5-HT1b (serotonin receptor)": ("Globus Pallidus", "Substantia Nigra", "Striatum (Putamen)"),
    "5-HT2a (serotonin receptor)": ("Orbitofrontal Cortex", "Frontal Pole", "Middle Frontal Gyrus", "Insula"),
    "5-HT4 (serotonin receptor)": ("Striatum (Caudate)", "Striatum (Putamen)", "Hippocampus"),
    "5-HTT (serotonin transporter)": ("Thalamus", "Insula", "Amygdala"),
    "VAChT (acetylcholine transporter)": ("Striatum (Caudate)", "Striatum (Putamen)", "Nucleus Accumbens"),
    "α4β2 (nicotinic acetylcholine receptor)": ("Thalamus", "Frontal Pole"),
    "M1 (muscarinic acetylcholine receptor)": ("Hippocampus", "Middle Frontal Gyrus"),
    "mGluR5 (glutamate receptor)": ("Hippocampus", "Amygdala", "Striatum (Caudate)"),
    "NMDA (glutamate receptor)": ("Hippocampus", "Anterior Cingulate Cortex"),
    "GABAa (GABA receptor)": ("Thalamus", "Hippocampus"),
    "H3 (histamine receptor)": ("Globus Pallidus", "Striatum (Caudate)", "Substantia Nigra"),
    "CB1 (cannabinoid receptor)": (
        "Globus Pallidus", "Substantia Nigra", "Hippocampus", "Amygdala", "Striatum (Putamen)",
    ),
    "MOR (mu-opioid receptor)": ("Thalamus", "Amygdala", "Nucleus Accumbens", "Insula"),
}


def _normalize(gene_or_alias: str) -> str:
    return gene_or_alias.strip().upper()


def suggest_regions(gene_or_alias: str) -> tuple[str, ...] | None:
    """Candidate atlas region(s) for a gene symbol or common receptor alias
    (case-insensitive matching), or None if it isn't in this curated table.
    A hypothesis to confirm, not an answer - callers must never auto-assign
    the result, only display it as a suggestion (see module docstring).
    """
    receptor_name = _GENE_ALIASES.get(_normalize(gene_or_alias))
    if receptor_name is None:
        return None
    return _RECEPTOR_TO_REGIONS.get(receptor_name)


def get_gene_citation(gene_or_alias: str) -> str | None:
    receptor_name = _GENE_ALIASES.get(_normalize(gene_or_alias))
    if receptor_name is None:
        return None
    return RECEPTOR_CITATIONS.get(receptor_name)


def known_genes() -> list[str]:
    return sorted(_GENE_ALIASES)

"""Real PET-derived neurotransmitter receptor/transporter density maps.

Lets a docking result be weighted by where a target receptor actually sits in
the brain, instead of treating a whole atlas region as uniformly "affected".
Data comes from Hansen, Shafiei et al. (2022), "Mapping neurotransmitter
systems to the structural and functional organization of the human
neocortex", Nature Neuroscience 25:1569-1581 - a compilation of 18
group-averaged human PET tracer maps, fetched here through the `neuromaps`
package (https://github.com/netneurolab/neuromaps) and resampled onto the
same MNI152 2mm grid used everywhere else in this app.

One representative tracer study is used per receptor/transporter (the
original paper sometimes offers more than one; see RECEPTOR_CITATIONS for the
exact one used and its own citation - Hansen et al. 2022 must additionally be
cited whenever a map from this module drives a figure, per the data's
CC BY-NC-SA 4.0 license). This is a real, published measurement of receptor
availability - not a simulation - but it is still a *structural* map: real
regional receptor density, not a guarantee of functional effect.
"""
import contextlib
import io

import nibabel as nib
import numpy as np
import streamlit as st
from nilearn.image import resample_img

from mni_space import MNI_AFFINE, MNI_SHAPE

# receptor/transporter display name -> (neuromaps source, desc, res)
RECEPTOR_MAPS = {
    "D1 (dopamine receptor)": ("kaller2017", "sch23390", "3mm"),
    "D2 (dopamine receptor)": ("jaworska2020", "fallypride", "1mm"),
    "DAT (dopamine transporter)": ("dukart2018", "fpcit", "3mm"),
    "NET (norepinephrine transporter)": ("ding2010", "mrb", "1mm"),
    "5-HT1a (serotonin receptor)": ("savli2012", "way100635", "3mm"),
    "5-HT1b (serotonin receptor)": ("gallezot2010", "p943", "1mm"),
    "5-HT2a (serotonin receptor)": ("beliveau2017", "cimbi36", "1mm"),
    "5-HT4 (serotonin receptor)": ("beliveau2017", "sb207145", "1mm"),
    "5-HTT (serotonin transporter)": ("beliveau2017", "dasb", "1mm"),
    "VAChT (acetylcholine transporter)": ("aghourian2017", "feobv", "1mm"),
    "α4β2 (nicotinic acetylcholine receptor)": ("hillmer2016", "flubatine", "1mm"),
    "M1 (muscarinic acetylcholine receptor)": ("naganawa2020", "lsn3172176", "1mm"),
    "mGluR5 (glutamate receptor)": ("dubois2015", "abp688", "1mm"),
    "NMDA (glutamate receptor)": ("galovic2021", "ge179", "1mm"),
    "GABAa (GABA receptor)": ("norgaard2021", "flumazenil", "1mm"),
    "H3 (histamine receptor)": ("gallezot2017", "gsk189254", "1mm"),
    "CB1 (cannabinoid receptor)": ("normandin2015", "omar", "1mm"),
    "MOR (mu-opioid receptor)": ("kantonen2020", "carfentanil", "3mm"),
}

RECEPTOR_CITATIONS = {
    "D1 (dopamine receptor)": "Kaller et al. 2017, NeuroImage (SCH-23390 PET)",
    "D2 (dopamine receptor)": "Jaworska et al. 2020, NeuroImage (fallypride PET)",
    "DAT (dopamine transporter)": "Dukart et al. 2018, Hum Brain Mapp (FP-CIT PET)",
    "NET (norepinephrine transporter)": "Ding et al. 2010, Biol Psychiatry (MRB PET)",
    "5-HT1a (serotonin receptor)": "Savli et al. 2012, NeuroImage (WAY-100635 PET)",
    "5-HT1b (serotonin receptor)": "Gallezot et al. 2010, J Cereb Blood Flow Metab (P943 PET)",
    "5-HT2a (serotonin receptor)": "Beliveau et al. 2017, J Neurosci (Cimbi-36 PET)",
    "5-HT4 (serotonin receptor)": "Beliveau et al. 2017, J Neurosci (SB207145 PET)",
    "5-HTT (serotonin transporter)": "Beliveau et al. 2017, J Neurosci (DASB PET)",
    "VAChT (acetylcholine transporter)": "Aghourian et al. 2017, Mol Psychiatry (FEOBV PET)",
    "α4β2 (nicotinic acetylcholine receptor)": "Hillmer et al. 2016, NeuroImage ((-)-flubatine PET)",
    "M1 (muscarinic acetylcholine receptor)": "Naganawa et al. 2020, J Cereb Blood Flow Metab (LSN3172176 PET)",
    "mGluR5 (glutamate receptor)": "Dubois et al. 2015 (ABP688 PET)",
    "NMDA (glutamate receptor)": "Galovic et al. 2021, J Cereb Blood Flow Metab (GE-179 PET)",
    "GABAa (GABA receptor)": "Norgaard et al. 2021, J Cereb Blood Flow Metab (flumazenil PET)",
    "H3 (histamine receptor)": "Gallezot et al. 2017, J Cereb Blood Flow Metab (GSK189254 PET)",
    "CB1 (cannabinoid receptor)": "Normandin et al. 2015, NeuroImage (Omar PET)",
    "MOR (mu-opioid receptor)": "Kantonen et al. 2020, NeuroImage (carfentanil PET)",
}

HANSEN_2022_CITATION = (
    "Hansen, Shafiei et al. 2022, Nature Neuroscience 25:1569-1581 "
    "(compilation via the neuromaps package, CC BY-NC-SA 4.0)"
)

RECEPTOR_NAMES = sorted(RECEPTOR_MAPS)


@st.cache_resource(show_spinner=False)
def _fetch_receptor_volume(source: str, desc: str, res: str) -> np.ndarray:
    from neuromaps.datasets import fetch_annotation

    # neuromaps prints a mandatory citation notice on every fetch (its own
    # source paper titles sometimes contain non-Latin-1 characters, e.g. the
    # Greek "alpha/beta" in nicotinic receptor names) - this crashes outright
    # on Windows consoles whose default codepage (cp1252/charmap) can't encode
    # them. The citation itself is redundant with RECEPTOR_CITATIONS /
    # HANSEN_2022_CITATION shown in this app's own UI, so it's safe to
    # capture and discard rather than let it hit the real stdout.
    with contextlib.redirect_stdout(io.StringIO()):
        path = fetch_annotation(source=source, desc=desc, space="MNI152", res=res)
    if isinstance(path, (list, tuple)):
        path = path[0]
    img = nib.load(path)
    resampled = resample_img(img, target_affine=MNI_AFFINE, target_shape=MNI_SHAPE,
                             interpolation="continuous")
    # Some neuromaps PET volumes ship as 4D with a trailing singleton time/
    # frame axis, so the resampled array comes back as (91,109,91,1) rather
    # than a bare 3D volume; squeeze it so the elementwise density weighting
    # downstream (visualization._compute_activation_array) gets a clean
    # (91,109,91) grid instead of raising a broadcast error against the 3D
    # activation volume.
    data = np.squeeze(np.asarray(resampled.get_fdata(), dtype=np.float64))
    data = np.nan_to_num(data, nan=0.0, neginf=0.0, posinf=0.0)
    data = np.clip(data, 0.0, None)
    peak = data.max()
    return data / peak if peak > 0 else data


def get_receptor_density(name: str) -> np.ndarray | None:
    """Return a (91,109,91) float64 density map normalized to [0, 1] (1.0 at
    the voxel of peak tracer binding), or None if `name` isn't a known
    receptor/transporter map.
    """
    entry = RECEPTOR_MAPS.get(name)
    if entry is None:
        return None
    source, desc, res = entry
    return _fetch_receptor_volume(source, desc, res)


def get_receptor_citation(name: str) -> str | None:
    return RECEPTOR_CITATIONS.get(name)

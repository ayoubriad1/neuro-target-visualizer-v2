# Receptor density weighting

Design notes for the optional "weight affinity by real receptor density"
sidebar feature (`receptor_atlas.py`, wired into `visualization.py`,
`ui_sidebar.py`, `interpretation.py`, `ai_agent.py`).

## What problem this solves

A docking result normally reports one affinity number for one target
(protein/receptor). Painting that affinity uniformly across a whole atlas
region implies the target is equally present everywhere in that region,
which usually isn't true. Two compounds with identical affinity on the same
receptor can still be expected to act very differently across the brain if
that receptor's real density is concentrated in different places.

This feature lets a researcher pick the receptor/transporter a compound
targets and weight the rendered map by that receptor's **real, published,
PET-measured density** — turning "affinity alone, painted uniformly" into
"affinity, shaped by where the target actually is."

## Data source

[Hansen, Shafiei et al. (2022)](https://www.nature.com/articles/s41593-022-01186-3),
*"Mapping neurotransmitter systems to the structural and functional
organization of the human neocortex,"* Nature Neuroscience 25:1569-1581 — a
curated compilation of group-averaged human PET tracer maps, fetched here
through the [`neuromaps`](https://github.com/netneurolab/neuromaps) package
rather than bundled with the app.

18 receptors/transporters are exposed, one representative tracer study per
target (see `receptor_atlas.RECEPTOR_CITATIONS` for the exact tracer/paper
used for each): D1, D2, DAT (dopamine); NET (norepinephrine); 5-HT1a, 5-HT1b,
5-HT2a, 5-HT4, 5-HTT (serotonin); VAChT, α4β2, M1 (acetylcholine); mGluR5,
NMDA (glutamate); GABAa; H3 (histamine); CB1 (cannabinoid); MOR (opioid).

**License: CC BY-NC-SA 4.0 (non-commercial).** This is why the feature stays
optional and why this app must remain free/non-commercial as long as it's
enabled. Citation is mandatory whenever a receptor-weighted figure is used
in a publication or report — cite **both** the specific tracer paper shown
in the Methods panel/sidebar caption **and** Hansen et al. 2022.

## How it works technically

1. `receptor_atlas.get_receptor_density(name)` calls
   `neuromaps.datasets.fetch_annotation(source=..., desc=..., space="MNI152", res=...)`,
   which downloads (and caches under `~/neuromaps-data`, mirroring nilearn's
   own `~/nilearn_data` cache) a group-averaged PET volume in MNI152 space.
2. The volume is resampled onto this app's exact MNI152 2mm grid
   (`mni_space.MNI_AFFINE` / `MNI_SHAPE`) with `nilearn.image.resample_img`
   — the same pattern already used for the Pauli et al. 2017 atlas (1mm →
   2mm).
3. The result is normalized so its peak voxel is 1.0, and cached via
   `@st.cache_resource` (fetched once per receptor, not per rerun).
4. `visualization._compute_activation_array` multiplies the raw
   affinity volume by this normalized density map elementwise, then
   renormalizes the *result's* peak back to 1.0 — this keeps the display
   threshold slider's meaning unchanged (it always operates on a 0-1 scale
   whose peak is "the strongest voxel in this particular map"), whether or
   not receptor weighting is active.

## What this is not

- Not a simulation — the density maps are real PET measurements.
- Not a guarantee of functional effect — receptor density is a **structural**
  quantity (how much of the target protein is physically present); it does
  not by itself confirm that engagement there produces a particular
  physiological or behavioral effect.
- Not per-study-averaged the way Hansen et al. 2022's own summary figures
  are for receptors with multiple available tracer maps (e.g. D2 has three
  candidate tracer studies in neuromaps) — this app picks one representative
  tracer per receptor to keep the sidebar simple. See `RECEPTOR_MAPS` in
  `receptor_atlas.py` if you want to add an alternate tracer as a second
  option for the same receptor.

## Adding another receptor/transporter

1. Find the `source`/`desc`/`res` (or `den`) values for the tracer you want
   in [neuromaps' list of maps](https://netneurolab.github.io/neuromaps/listofmaps.html).
2. Add an entry to `RECEPTOR_MAPS` and its matching citation to
   `RECEPTOR_CITATIONS` in `receptor_atlas.py`.
3. No other code changes needed — `RECEPTOR_NAMES` (sidebar dropdown),
   the Methods panel note, and the AI-interpretation prompt all read from
   these two dicts dynamically.

# Roadmap & Scientific Scope

This document records what the tool currently does, and what would be required to
extend it toward measured, ground-truth-backed analysis.

## Implemented

- **Five view modes** — Interactive 3-D (Plotly), 3-D Surface, Glass Brain,
  Stat Map, Interactive Slices.
- **Interactive 3-D brain** — a rotatable WebGL model on the folded pial surface
  (real gyri/sulci) with a gray→red intensity map; a light, near-white cortex for
  clarity.
- **Higher-resolution surface** — `fsaverage6` by default, selectable up to full
  `fsaverage`; inflated ↔ pial toggle.
- **User controls** — a display-threshold slider threaded through every renderer;
  surface-resolution and inflate options.
- **Binding-affinity summary** with per-region strength tags, a written
  interpretation, and a methods / provenance panel.
- **Packaging** — pinned dependencies, a self-bootstrapping Windows launcher, and
  an Obsidian documentation vault under `docs/`.

## Scientific scope

The tool is a **visualization aid**. Affinity values are entered by the user; the
app does not read measured PET or mRNA data and does not perform docking. Rendered
maps therefore represent **predicted localization and relative strength**, not
measured receptor occupancy or in-vivo concentration. The kcal/mol → intensity
mapping is a fixed, documented linear scale over `[-1, -15]` kcal/mol.

## Roadmap (not yet implemented)

These require real datasets and a larger data model, and are intentionally **not**
faked:

1. **Molecule input.** Accept a molecule (e.g. SMILES) and compute standard
   descriptors (QED, physicochemical properties, a CNS desirability score) and
   look up measured affinities from curated databases.
2. **Measured ground truth.** Compare a predicted map against in-vivo PET
   receptor-density atlases, and quantify agreement with
   spatial-autocorrelation-preserving null models (spin tests).
3. **Atlas parcellations.** Move from fixed MNI point coordinates to per-parcel
   scoring with selectable atlases (e.g. Glasser, Schaefer, Desikan-Killiany).
4. **Region interactivity.** Click a region to reveal the targets and affinities
   that drive it (depends on the molecule/affinity layer above).

## Notes

- Coordinate space: MNI152, 2 mm (`91 × 109 × 91`).
- Region model: 25 regions as single MNI points → Gaussian blobs.
- Activation spread (σ): 12 mm for the surface views, 6 mm for glass/stat.
- Colormaps: `YlOrRd` (static/glass/stat) and a gray→red scale (interactive 3-D),
  both mapped to the same 0–100 % normalized intensity.

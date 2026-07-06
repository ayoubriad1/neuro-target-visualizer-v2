# Roadmap & Scientific Scope

This document records what the tool currently does, and what would be required to
extend it toward measured, ground-truth-backed analysis.

## Implemented

- **Five view modes** — Interactive 3-D (Plotly), 3-D Surface, Glass Brain,
  Stat Map, Interactive Slices.
- **Interactive 3-D brain** — a rotatable WebGL model on the folded pial surface
  (real gyri/sulci) with a gray→red intensity map, a persistent L/R orientation
  compass, and one-click camera presets (Left/Right/Top/Front/Default); a
  light, near-white cortex for clarity. (Always rendered on the pial surface —
  there is no inflated/pial toggle in the current UI.)
- **Higher-resolution surface** — `fsaverage6` by default, selectable up to full
  `fsaverage`.
- **User controls** — a display-threshold slider threaded through every renderer;
  surface-resolution option; a colorblind-safe (viridis) color scheme alongside
  the default warm gray→red palette.
- **Binding-affinity summary** with per-region strength tags, a written
  interpretation, an optional AI-generated interpretation (see below), and a
  methods / provenance panel.
- **Export** — download the active static figure as PNG, or a full Markdown
  report (affinity table + interpretation + methods).
- **Packaging** — pinned dependencies (`requirements.lock.txt`), Docker, a
  self-bootstrapping Windows/macOS/Linux launcher, GitHub Actions CI
  (lint + type-check + tests), and an Obsidian documentation vault under `docs/`.
- **Atlas-backed regions** — **all 28 regions** now use a real, cited
  parcellation mask (Harvard-Oxford cortical/subcortical, Pauli et al. 2017)
  instead of a hand-placed point, fetched via `atlas_regions.py`. The 6
  regions that used to be illustrative points (traced back to an older printed
  stereotaxic atlas, not a citable digital dataset) were either upgraded to a
  real atlas mask, renamed to their true anatomical equivalent, or dropped
  entirely when no atlas existed at all — see "Region model" below and
  `CHANGELOG.md`.
- **Optional AI interpretation (BYOK)** — `ai_agent.py` / `ui_ai.py` call the
  user's own Claude (Anthropic) or ChatGPT (OpenAI) key, picked and entered in
  the sidebar — never bundled or paid for by this app. The prompt forbids
  inventing citations/PMIDs and asks for an explicit confidence label. This is
  a single constrained LLM call from general knowledge, **not**
  literature-grounded RAG — see the roadmap item below for that larger design.

## Scientific scope

The tool is a **visualization aid**. Affinity values are entered by the user; the
app does not perform docking. Rendered maps represent **predicted localization
and relative strength**, not measured receptor occupancy or in-vivo
concentration. The kcal/mol → intensity mapping is a fixed, documented linear
scale over `[-1, -15]` kcal/mol. Optionally, the map can additionally be
weighted by a real, published in-vivo PET receptor-density atlas (see
[`docs/RECEPTOR_WEIGHTING.md`](docs/RECEPTOR_WEIGHTING.md)) — that weighting
is real measured data, but affinity itself is still user-entered, not
measured or docking-derived.

## Roadmap (not yet implemented)

These require real datasets and a larger data model, and are intentionally **not**
faked:

1. **Molecule input.** Accept a molecule (e.g. SMILES) and compute standard
   descriptors (QED, physicochemical properties, a CNS desirability score) and
   look up measured affinities from curated databases. *Partially adjacent:*
   `docking_import.py` now bulk-imports already-computed docking scores from
   a CSV or an AutoDock Vina result file, removing the manual re-entry step -
   but it doesn't compute anything from a molecule itself; that remains open.
2. ~~**Measured ground truth.**~~ **Done, with a scoped caveat** — the map
   can be weighted by real in-vivo PET receptor-density atlases (Hansen et
   al. 2022, 18 receptors/transporters), and a "🧪 Spatial correspondence
   test" quantifies agreement between the user's affinity pattern and real
   receptor density via a 5,000-sample region-resampling permutation test
   (`spatial_stats.py`). This is **not** a full vertex-level spin test
   (Alexander-Bloch/Vasa/Burt) - those need a single registered
   cortical-surface parcellation to rotate, which this app's mixed
   cortical/subcortical/coordinate region set doesn't have. A true spin test
   would require building that unified surface parcellation object first;
   left as a further-future upgrade if the region model is ever
   surface-unified. See `docs/RECEPTOR_WEIGHTING.md`.
3. ~~**Full atlas coverage.**~~ **Done** — all 28 regions are now atlas-backed;
   see "Region model" below. Raphe Nuclei, Locus Coeruleus, and Cerebellum
   were dropped entirely (no standard, openly-fetchable atlas exists for any
   of them); a dedicated brainstem or cerebellar atlas (e.g. the Diedrichsen
   cerebellar atlas) could reintroduce them properly in the future.
4. **Region interactivity.** Click a region to reveal the targets and affinities
   that drive it (depends on the molecule/affinity layer above).
5. **Literature-grounded AI interpretation.** Upgrade the current single-call
   AI interpretation (general knowledge only) into a RAG pipeline: retrieve
   from PubMed (NCBI E-utilities), Semantic Scholar, and OpenAlex, ground each
   claim in a retrieved passage with an inline citation, verify citation
   support with an entailment check, and calibrate the confidence score from
   source agreement instead of the model's own self-report.

## Notes

- Coordinate space: MNI152, 2 mm (`91 × 109 × 91`).
- Region model: 28/28 regions use a real atlas mask (`atlas_regions.py`:
  Harvard-Oxford cortical + subcortical, Pauli et al. 2017, resampled to this
  grid where needed). `brain_regions.py`'s illustrative MNI point → Gaussian
  blob fallback (mirrored across the midline) is currently unused but kept as
  infrastructure in case a future region has no atlas match.
- Activation spread (σ, illustrative regions only - currently none): 12 mm for
  the surface views, 6 mm for glass/stat.
- Colormaps: `YlOrRd` (static/glass/stat) and a gray→red scale (interactive 3-D),
  both mapped to the same 0–100 % normalized intensity.

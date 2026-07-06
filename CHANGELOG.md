# Changelog — engineering session summary

This document summarizes every improvement made to the Neuro-Target Affinity
Visualizer during this engineering session, organized by phase in the order they
were done. See [`ENHANCEMENT_REPORT.md`](ENHANCEMENT_REPORT.md) for the
scientific scope and remaining roadmap, and
[`docs/AI_AGENT.md`](docs/AI_AGENT.md) for a deep dive on the AI interpretation
feature specifically.

---

## Phase 1 — Performance, reliability & correctness

**Problem**: no caching anywhere (every Streamlit rerun recomputed everything from
scratch, up to ~20-35s per render), unpinned dependencies, and two real bugs
hiding in the original code.

- Added `@st.cache_data` / `@st.cache_resource` across every rendering function in
  `visualization.py`. Measured impact: the "3D Surface" view went from **~19-35s
  to ~0.1-1s** on repeat renders with unchanged inputs.
- Generated [`requirements.lock.txt`](requirements.lock.txt) (exact, hash-verified
  pins via `pip-compile`) alongside the original loose `requirements.txt`.
- Fixed a real crash bug: `app.py` referenced an undefined `surf_inflate`
  variable that raised `NameError` every time the "Methods & provenance" panel
  was opened.
- Added a warning banner when a selected region is a deep/subcortical structure
  that would otherwise render as invisible on the cortical-surface views
  ("Interactive 3D", "3D Surface") — prevents mistaking "not rendered" for "no
  binding".
- Fixed inconsistent hemisphere handling: illustrative (non-atlas) regions are
  now mirrored across the midline by default, since systemic ligand binding is
  normally bilateral — the original code stamped a single, arbitrarily-sided
  point per region.
- Cleaned up all ruff/mypy findings; added Docker, `start_app.sh` (macOS/Linux
  launcher), dev tooling (`pyproject.toml`, `requirements-dev.txt`), and the
  **first test suite** (7 tests — there were previously zero).

## Phase 2 — Real anatomical atlases

**Problem**: all 25 brain regions were single illustrative MNI points with no
cited source, stamped with a Gaussian blob — not defensible beyond casual
visualization.

- New module [`atlas_regions.py`](atlas_regions.py): fetches and caches real,
  published parcellation atlases via nilearn — Harvard-Oxford
  cortical + subcortical, and Pauli et al. (2017) for basal ganglia/midbrain
  nuclei absent from Harvard-Oxford (substantia nigra, VTA, hypothalamus).
- **19 of 25 regions** now render on a real anatomical mask instead of a
  hand-placed point; the remaining 6 (small brainstem nuclei, composite
  prefrontal subdivisions) have no standard openly-available atlas and stay
  illustrative — clearly labeled as such in the UI ("✅ Atlas-backed" vs
  "⚠️ Illustrative") and in the Methods & provenance panel, with exact
  citations.
- New shared module [`mni_space.py`](mni_space.py) to avoid a circular import
  between `visualization.py` and `atlas_regions.py`.
- 13 new tests verifying mask shape/range/bilaterality for every atlas-backed
  region.

## Phase 3 — Architecture, CI, palette, export

**Problem**: `app.py` was a 587-line monolith mixing theme CSS, business logic,
state management, and rendering — untestable and hard to extend.

- Split into 8 single-responsibility modules: `config.py`, `styles.py`,
  `models.py` (typed `RegionEntry` dataclass replacing bare positional tuples),
  `state.py`, `ui_sidebar.py`, `ui_views.py`, `interpretation.py`, plus a
  ~40-line `app.py` orchestrator.
- Added GitHub Actions CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):
  ruff + mypy + pytest on Python 3.11/3.12, with dependency and atlas-download
  caching.
- Added a **colorblind-safe color scheme** (viridis) alongside the original warm
  gray→red palette, selectable per-render, applied consistently across all 5
  view modes.
- Added **export**: high-res PNG download for the 3 static views, and a
  self-contained Markdown report (affinity table + interpretation +
  methods/provenance) for any view.
- Replaced the deprecated `st.components.v1.html` with `st.iframe`, and
  `use_container_width` with `width="stretch"` (both flagged for removal by
  Streamlit itself in the server logs).

## Design pass

- Persistent **"L"/"R" orientation labels** on the Interactive 3D view, so
  orientation stays legible after free rotation.
- One-click **camera presets** (Left/Right/Top/Front/Default) on the
  Interactive 3D view, reusing the same angles as the static "3D Surface"
  montage — purely client-side (Plotly `updatemenus`), no server rerun.
- `initial_sidebar_state="expanded"` so the sidebar (the app's only interaction
  point) is never hidden behind an unlabeled arrow on first load.
- Restyled the sidebar "Active Regions" list as compact cards matching the main
  "Affinity Summary" cards (same strength badges, same visual language) —
  previously plain text, visually inconsistent with the rest of the app.
- Restyled the "View Mode" radio group as a segmented pill control, and gave
  `st.expander` panels card-style chrome (border, radius, soft shadow), instead
  of default Streamlit chrome.

## Accessibility pass

- Audited the strength-badge colors ("Weak"/"Moderate"/"Strong"/"Very strong")
  against WCAG AA contrast (4.5:1 for small text) using the actual
  relative-luminance formula, not eyeballing: **"Weak" failed outright (2.09:1)**,
  "Strong" and "Moderate" fell just short (4.08 and 3.20). Adjusted the palette
  minimally (same hues, same gradient order) so all four now clear 4.5:1, with a
  regression test (`test_strength_label_meets_wcag_aa_contrast`) to catch any
  future palette change that reintroduces the problem.
- Added `prefers-reduced-motion: reduce` support: the rotating-brain icon,
  shimmer effect, and loading animations are disabled for users with that
  OS/browser preference set (WCAG 2.3.3, vestibular-disorder consideration).

## AI scientific interpretation (BYOK)

See [`docs/AI_AGENT.md`](docs/AI_AGENT.md) for the full write-up. In short: an
optional, bring-your-own-key LLM call (Claude or ChatGPT, user's choice,
configured from the sidebar) that generates a short interpretation constrained
to general neuroscience knowledge, with an explicit, prompt-enforced
prohibition on inventing citations — this app never bundles or pays for API
access on anyone's behalf.

## Data quality pass — 100% atlas-backed regions

**Problem**: of the original 25 regions, 6 were still illustrative points with
no citable source — traced back to an older printed stereotaxic atlas, not a
versioned digital dataset, so they couldn't be tied to a real reference.

- Removed 3 regions with no standard, openly-fetchable atlas at all: **Raphe
  Nuclei, Locus Coeruleus, Cerebellum**. Dropped entirely rather than kept as
  unverified data.
- Upgraded **Orbitofrontal Cortex** to a real atlas mask (Harvard-Oxford's
  "Frontal Orbital Cortex" is a direct match) instead of removing it.
- Replaced the functional labels **"Prefrontal Cortex (DLPFC)"** and
  **"(VMPFC)"** — neither corresponds to a single atlas region — with their
  real Harvard-Oxford anatomical equivalents, **Middle Frontal Gyrus** and
  **Frontal Medial Cortex**, rather than keep a label nothing in any atlas
  actually matches.
- Added **8 new atlas-backed regions** that were already available in the
  atlases this app already fetches, just not yet exposed: Subthalamic
  Nucleus, Habenula, Ventral Pallidum (Pauli et al. 2017); Frontal Pole,
  Precuneous Cortex, Angular Gyrus (Harvard-Oxford cortical).
- Generalized `atlas_regions.py`'s cortical mapping to union multiple atlas
  divisions into one region (previously only the subcortical/Pauli paths
  supported this), and refactored `get_region_names()` so a region can exist
  purely as an atlas entry with no `brain_regions.py` fallback point at all —
  `brain_regions.py` is now an empty illustrative-fallback dict, kept as
  infrastructure for any future region with no atlas match.
- The Methods & Provenance panel's atlas/region table is now built
  dynamically from the actual region→source mapping instead of a hardcoded
  list, so it can't silently go stale the next time a region changes (as the
  previous version had, twice).
- **Result: 28/28 regions are now atlas-backed — zero illustrative points
  remain.**

## Advanced input: exact MNI coordinates

**Problem**: whole-region atlas masks are more scientifically defensible than
a single point, but they lose precision for a researcher who already knows
exactly where they're targeting (e.g. a neurosurgeon planning DBS, or someone
reproducing a specific peak coordinate from a paper) — a named region can't
express "this one exact spot."

- Added a second sidebar input mode, **"Exact MNI coordinates (advanced)"**,
  alongside the default named-region picker: three X/Y/Z number inputs
  (bounded to the MNI152 template extent) replace the region dropdown.
- `RegionEntry` gained an optional `coordinates` field; when set,
  `visualization.py` stamps a single Gaussian exactly there instead of
  consulting the atlas/illustrative catalog by name, and — deliberately —
  does **not** mirror it across the midline (unlike named regions), since an
  exact coordinate was chosen on purpose and may be intentionally unilateral.
- The AI interpretation prompt and the region chip/summary UI both handle
  this case explicitly rather than mislabeling it as "illustrative."

## Receptor density weighting

**Problem**: affinity is painted uniformly across a whole selected region,
implying the target is equally present everywhere in it - not generally true,
and something two compounds with identical affinity on the same receptor
would still show identically, even if the real receptor is concentrated in
very different places for each.

- New module [`receptor_atlas.py`](receptor_atlas.py): fetches 18 real,
  published PET-derived receptor/transporter density maps (Hansen, Shafiei et
  al. 2022, Nature Neuroscience) via the `neuromaps` package, resampled onto
  this app's MNI152 2mm grid the same way the Pauli 2017 atlas already is.
  Covers dopamine (D1, D2, DAT), norepinephrine (NET), serotonin (5-HT1a/1b/
  2a/4, 5-HTT), acetylcholine (VAChT, α4β2, M1), glutamate (mGluR5, NMDA),
  GABAa, histamine (H3), cannabinoid (CB1), and opioid (MOR) systems.
- New optional sidebar section, **"Receptor Weighting"**: pick a target, and
  `visualization.create_activation_volume` multiplies the raw affinity volume
  by that receptor's real density (renormalized so the display-threshold
  slider's semantics stay unchanged) instead of leaving the whole region
  uniform.
- The Methods & provenance panel and the AI-interpretation prompt both
  explicitly note when weighting is active and cite the specific tracer
  study + Hansen et al. 2022, so neither a downloaded report nor the AI
  interpretation can imply the map is affinity-only when it isn't.
- **License note**: this data is CC BY-NC-SA 4.0 (non-commercial, attribution
  required) - see [`docs/RECEPTOR_WEIGHTING.md`](docs/RECEPTOR_WEIGHTING.md)
  for the full design write-up, citation requirements, and how to add another
  receptor/tracer.

## Importing docking results

**Problem**: every region had to be added one at a time through the sidebar
form - the single biggest friction point for anyone with an actual
virtual-screening or docking run's worth of results (tens of targets) to
visualize, rather than a handful typed in for a demo.

- New module [`docking_import.py`](docking_import.py): `parse_csv` for
  bulk `region,kcal` (+ optional `x,y,z`) rows, with per-row validation
  (unknown region names, non-negative or unparseable affinities) reported
  individually rather than failing or silently dropping the whole batch;
  `parse_vina_score` extracts the best pose's affinity from either a raw
  AutoDock Vina `.pdbqt` output or its plain-text results table.
- New sidebar section, **"📥 Import docking results (optional)"**: a CSV/TSV
  uploader previews valid rows and imports them in one click, and a Vina
  file uploader prefills the "Binding Affinity" field with the extracted
  score so it doesn't have to be retyped (the user still assigns it to a
  region, since a docking score alone has no brain-region association).

## Spatial correspondence test

**Problem**: receptor weighting shows *where* a receptor is dense, but gave
no way to ask the natural follow-up - does the user's own affinity pattern
actually correspond to that density any more than chance would?

- New module [`spatial_stats.py`](spatial_stats.py): correlates each
  selected region's normalized affinity against the real receptor density
  in that region (mean within the atlas mask, or the value at the exact
  voxel for coordinate-based entries), then runs a 5,000-sample
  region-resampling permutation test (swapping in random same-size sets of
  atlas regions) to report a p-value. Explicitly **not** a vertex-level
  "spin test" (no unified surface parcellation to rotate, given this app's
  mixed cortical/subcortical/coordinate region set) - documented as such in
  the UI, the downloadable report, and `docs/RECEPTOR_WEIGHTING.md`.
- New results section, **"🧪 Spatial correspondence test"**: only appears
  when receptor weighting is active and at least 3 selected regions have a
  usable density value; included in the downloadable report too.
- Deterministic (fixed permutation seed) so the reported r/p don't jitter
  across unrelated reruns.

## Circuit propagation (experimental)

**Problem**: every view answers "where does the compound bind?" - but a
pharmacological effect doesn't stay confined to its binding site, it
propagates through functional circuits (the textbook example: a
dopaminergic compound reaches motor, mood, and cognitive domains
simultaneously via separate parallel cortico-striato-thalamic loops, not by
binding all three directly).

- New precomputed data asset [`data/connectivity_matrix.csv`](data/connectivity_matrix.csv):
  a real 28x28 group-average functional connectivity matrix, derived from
  15 adult subjects' naturalistic-viewing fMRI (Richardson et al. 2018) via
  [`scripts/compute_connectivity_matrix.py`](scripts/compute_connectivity_matrix.py)
  (confound-regressed, detrended, band-pass filtered regional timeseries;
  Fisher-z-averaged Pearson correlation) - fully reproducible, not a
  hand-tuned or opaque bundled file. Sanity-checked against known
  neuroanatomy (e.g. Putamen's top connections are Caudate/Insula/Motor
  cortex/Thalamus, matching established cortico-striato-thalamic loops).
- New module [`connectome.py`](connectome.py): `propagate_effect` ranks
  atlas regions the user did **not** select by a connectivity-weighted sum
  of their selected regions' affinities (positive connections only).
- New results section, **"🔗 Circuit propagation (experimental)"**:
  deliberately its own section, never blended into the 3-D heatmap, with an
  explicit "linear estimate, not a simulation" caveat and a percentage scale
  documented as non-comparable to the directly-entered affinities.
- Full methodology and caveats in [`docs/CONNECTOME_PROPAGATION.md`](docs/CONNECTOME_PROPAGATION.md).
- **Animated network view** ([`connectome_viz.py`](connectome_viz.py)): a
  Play/step-slider Plotly animation of `connectome.simulate_diffusion` (a
  random-walk-with-restart multi-step diffusion over the same connectivity
  matrix) - one node per atlas region at its real MNI centroid, edges above
  a connectivity threshold, node size/color animating through each step. A
  cool blue/teal palette (vs. the warm red used for measured affinity
  everywhere else) and a gold ring on the directly-selected source
  region(s) keep it visually unmistakable as an estimate, not measured
  data. Explicitly labeled: **"step" is an abstract diffusion iteration,
  not real elapsed time.**

---

## Numbers

| Metric | Before | After |
|---|---|---|
| Tests | 0 | 121 (all passing) |
| `app.py` size | 587 lines, monolithic | ~40 lines, 17 focused modules |
| Ruff/mypy findings | unmeasured | 0 across all first-party modules |
| Regions on a real cited atlas | 0 / 25 | 28 / 28 (0 illustrative) |
| Receptor/transporter density maps available | 0 | 18 (real PET data, optional weighting) |
| Docking result import formats | 0 (manual entry only) | CSV/TSV batch + AutoDock Vina |
| Circuit propagation | none | real 28x28 functional connectivity matrix |
| "3D Surface" repeat-render time | ~19-35s | ~0.1-1s |
| CI | none | GitHub Actions (lint + type-check + test) |

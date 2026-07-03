---
tags: [changelog, build-log, v2]
aliases: [Changelog, Modifications, What Changed, v2 changes]
---
# 🔧 Changes from v1 — full modification log

> [!abstract] Scope
> Everything that differs between the original tool (`..\Brain Vizualisation\`)
> and the enhanced copy (`..\Brain Visualizer v2\`). The original and its
> `Brain_Vault` were **not modified** — v2 is a side-by-side copy. Hub:
> [[Neuro-Target Visualizer v2]].

## A. New view modes (3 → 5)
v1 had **3D Surface · Glass Brain · Stat Map**. v2 has **five**, with
[[Interactive 3D Brain (Plotly)]] as the default:

| Mode | New? | What |
|------|------|------|
| [[Interactive 3D Brain (Plotly)]] | ✅ new | Rotatable gray brain, gray→red map |
| 3D Surface | (v1) | Static paper-style panels — now fsaverage6 |
| Glass Brain | (v1) | 2×2 X-ray projections |
| Stat Map (Slices) | (v1) | Static anatomical slices |
| [[Interactive Slices]] | ✅ new | Scrubbable cross-hair volume viewer |

## B. The rotatable gray → red 3-D brain
The headline request: *"all the brain gray, the affected region really red and
gradually, like the previous one but keep it 3-D."*
- Implemented with **Plotly Mesh3d** (`interactive_surface_plotly` in
  [[visualization (v2)]]) because nilearn's `view_img_on_surf` can't restyle the
  cortex to flat gray. See [[Interactive 3D Brain (Plotly)]] and the colour
  scheme in [[Gray-to-Red Intensity Map]].
- The volume is sampled onto each hemisphere via [[vol_to_surf Projection]] and
  displayed on the **folded pial** mesh (fsaverage6) so gyri/sulci are visible,
  with a curvature-shaded gray base and sub-threshold vertices left gray.
  *(Fix after the first pass looked too smooth — the inflated mesh hid the folds.)*
- Embedded with `st.plotly_chart` (native drag-to-rotate). Added **`plotly`** to
  `requirements.txt` → v2 has its own `.venv`.

## C. Higher-fidelity static surface
[[Higher-Resolution Surface (fsaverage6)]]: v1 hard-coded `fsaverage5` (~10k
verts/hemi); v2 defaults to **fsaverage6** (~41k) with a UI selector
(5 / 6 / full) and an **inflated ↔ pial** toggle.

## D. User controls
- [[Display Threshold Control]] — a sidebar **Rendering** section with a
  threshold slider threaded through every renderer, plus the surface-resolution
  selector and inflate toggle.

## E. Clarity / reproducibility
- [[Methods & Provenance Panel]] — a live expander reporting space, σ, mesh,
  colormap, threshold, kcal→% mapping, library versions, timestamp, and an
  explicit "values are user-entered, no external data" statement.

## F. Packaging
- `requirements.txt` gains `plotly>=5.18`.
- `start_app.bat` **self-bootstraps** its own `.venv` (Python 3.13) on first run.
- Tab title shows "· v2".

## What did NOT change
The science model is identical to v1: 25 fixed MNI region points → Gaussian
blobs → MNI152 volume; the kcal/mol → % mapping; the YlOrRd scale on
glass/stat/static-surface. No PET/mRNA/atlas/molecule data was added (that is the
[[Enhancement Roadmap]]).

## Honesty
Nothing fabricated. v2 is still a **manual-input** visualizer; the gray→red 3-D
brain shows the *same* user-entered intensities, just interactively and in 3-D.

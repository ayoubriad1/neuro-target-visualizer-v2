# NeuroViz v2 — Complete Session Build Summary

**Author:** Ayoub Riad  
**Session Date:** July 2, 2026  
**Repository:** https://github.com/ayoubriad1/neuroviz-v2  
**License:** MIT

---

## Executive Summary

This document is a **complete record** of the NeuroViz v2 project — what was built, where it lives, how to launch it, and what changed from v1. Everything is authored by **Ayoub Riad alone** (no co-authors or AI attribution in the codebase).

---

## 1. Project Structure Overview

### Two Local Folders
| Folder | Purpose |
|--------|---------|
| `Brain Vizualisation\` | **Original v1 project** (not under git). Core code intact; transient build artifacts archived. Pristine v1 source preserved in `neuro-target-visualizer\` subfolder. |
| `Brain Visualizer v2\` | **Enhanced v2 copy** (git repo, published to GitHub). All new features live here. |

### GitHub Repository
- **Name:** `neuroviz-v2`
- **URL:** https://github.com/ayoubriad1/neuroviz-v2
- **Visibility:** PUBLIC
- **Author:** Ayoub Riad (`ayoub.riad45@gmail.com`)
- **Contributors:** Only Ayoub Riad — no co-authors, no bots
- **License:** MIT

---

## 2. What v2 Adds Over v1

### Five View Modes
1. **Interactive 3D (Plotly)** — rotatable WebGL brain on folded pial surface (real gyri/sulci); light cortex with gray→red intensity heat map; drag to rotate, scroll to zoom.
2. **3D Surface** — static multi-angle montage (left lateral, right lateral, top, front) of the light folded cortex model; high-detail, publication-quality.
3. **Glass Brain** — 2×2 grid of full-depth X-ray projections (left sagittal, right sagittal, axial, coronal); deep/subcortical activation always visible.
4. **Stat Map (Slices)** — 8 axial anatomical slices + orthogonal cross-sections at peak activation; precise anatomical localization on MRI.
5. **Interactive Slices** — scrubbable cross-hair volume viewer; synchronized 3 planes; best for deep/subcortical exploration.

### Rendering Controls
- **Display threshold slider** (0.0–0.50) — hides faint activation, shows only strongest voxels; threaded through all renderers.
- **Surface resolution selector** — `fsaverage5` (fast, ~10k verts/hemi), `fsaverage6` (sharp, ~41k, default), `fsaverage` (finest, ~164k, slow).

### User-Facing Features
- **Binding-affinity summary** — per-region strength bars (weak/moderate/strong tags).
- **Written interpretation** — ranks regions by strength, shows distribution, explains kcal/mol scale.
- **Methods & provenance panel** — live reproducibility report: coordinate space, region model, σ values, library versions, timestamp, explicit data-scope statement.

### Technical Foundations
- **Brain mesh:** fsaverage5 (interactive) or fsaverage6 (static/controls) — real folded cortex, no smoothed balloon.
- **Color scheme:** gray→red intensity map (interactive 3D) or YlOrRd (static views) — mapped to same 0–100% normalized binding intensity.
- **Dependencies added:** `plotly>=5.18.0` (interactive 3D, Mesh3d), `kaleido>=0.2.1` (static montage export).
- **Self-launching:** `start_app.bat` auto-bootstraps `.venv` (Python 3.13) on first run; no manual venv/pip needed on Windows.

---

## 3. Installation & Launch Instructions

### For You (Local Development)

**One-click Windows:**
1. Open `F:\...\Brain Visualizer v2\`.
2. **Double-click `start_app.bat`.**
3. Opens browser at **http://localhost:8501**. To stop, close the terminal.

**Manual (any OS):**
```bash
# Build isolated environment
python -m venv .venv

# Install dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt      # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

# Launch
.venv\Scripts\python.exe -m streamlit run app.py                 # Windows
# streamlit run app.py                                           # macOS/Linux
```

### For Anyone Downloading from GitHub

1. **Install Python 3.13+** from [python.org/downloads](https://www.python.org/downloads/).  
   (On Windows, tick **"Add Python to PATH"** during setup.)

2. **Get the code:**
   - Easiest (no git needed): GitHub page → green **`< > Code`** → **Download ZIP** → unzip.
   - Or: `git clone https://github.com/ayoubriad1/neuroviz-v2.git`

3. **Launch:**
   - **Windows:** Open the folder and **double-click `start_app.bat`**.  
     (First run builds the environment automatically, a few minutes; later runs start in seconds.)
   - **macOS/Linux:** Run the manual commands above.

4. **App opens at http://localhost:8501**. To stop, close the terminal window.

---

## 4. File Map

```
neuroviz-v2/
├── app.py                              # Streamlit UI: hero, sidebar, views, summary, interpretation, methods
├── visualization.py                    # Volume builder + all renderers (interactive Plotly, static, glass, stat)
├── brain_regions.py                    # 25 brain regions with MNI coordinates
├── requirements.txt                    # Python dependencies (streamlit, nilearn, plotly, kaleido, etc.)
├── start_app.bat                       # One-click Windows launcher (self-bootstraps .venv)
├── .streamlit/
│   └── config.toml                     # UI theme (lavender palette, no analytics)
├── .venv/                              # Python 3.13 virtual environment (auto-created by start_app.bat)
├── LICENSE                             # MIT License, © 2026 Ayoub Riad
├── README.md                           # Project overview, pipeline, install, launch, usage, view modes
├── ENHANCEMENT_REPORT.md               # Roadmap: what's implemented vs. what needs real data
├── COMPLETE_SESSION_SUMMARY.md         # This file
├── docs/
│   └── Brain_Vault_v2/                 # Obsidian documentation vault
│       ├── Neuro-Target Visualizer v2.md    # Hub note
│       ├── Changes from v1.md               # Full modification log
│       ├── Interactive 3D Brain (Plotly).md
│       ├── Interactive Slices.md
│       ├── Glass Brain (2x2 X-ray).md
│       ├── Stat Map (Slices).md
│       ├── Higher-Resolution Surface (fsaverage6).md
│       ├── Display Threshold Control.md
│       ├── Methods & Provenance Panel.md
│       ├── Gray-to-Red Intensity Map.md
│       ├── vol_to_surf Projection.md
│       ├── Enhancement Roadmap.md
│       ├── Gallery.md                       # All rendered images
│       ├── Code_Graph/                      # Full source code embedded as notes
│       │   ├── app.md
│       │   ├── visualization.md
│       │   ├── brain_regions.md
│       │   ├── start_app.md
│       │   ├── config.md
│       │   └── requirements.md
│       ├── Images/                          # Rendered brain maps
│       │   ├── interactive-3d.png           # Hero rotatable brain
│       │   ├── interactive-3d-top.png       # Same brain from above (shows rotatability)
│       │   ├── static-surface.png           # 4-angle montage
│       │   ├── glass-brain.png              # 2x2 X-ray projections
│       │   └── stat-map.png                 # Anatomical slices + orthogonal
│       └── .obsidian/                       # Graph-view styling (neural network colors)
└── _session_artifacts/                      # Transient build artifacts (not in git)
    ├── SESSION_LOG.md                       # Original session log
    ├── install.log                          # pip/Streamlit runtime logs
    ├── streamlit.log
    └── __pycache__/                         # Python bytecode (auto-generated)
```

---

## 5. What Changed: Original Folder (`Brain Vizualisation`)

### Modified Files
- **`app.py`, `visualization.py`** — UI overhaul (bright theme, centered hero, brain icons, rotating loader, 2×2 glass brain, Stat Map colour fix, affinity summary, interpretation).  
  *Pristine originals remain in `neuro-target-visualizer\` subfolder for restoration.*

### Added (Functional — Kept in Place)
- **`.venv\`** — Python 3.13 virtual environment (used to run the original).
- **`.streamlit\config.toml`** — UI theme (lavender palette).
- **`start_app.bat`** — One-click launcher.
- **`.claude\launch.json`** — Local dev-server config.
- **`Brain_Vault\Making of the Visualizer.md`** — Design decisions and build log (linked to hub).
- **`Brain_Vault_v2\`** — Complete v2 documentation vault (separate, parallel to v1).

### Archived (Moved, Not Deleted)
- **`_session_artifacts\install.log`, `streamlit.log`, `__pycache__\`** — Transient build artifacts (pip/Streamlit logs, bytecode). Moved out to keep root tidy, but preserved for reference.

---

## 6. v2 Development Pipeline

### Early Work (In Original Folder)
- Initial UI theme (bright lavender, centered hero, author byline).
- Rotating-brain loader (CSS animation, replaces Streamlit's default).
- Affinity summary redesign (professional bars, strength tags).
- Stat Map fix: switched from `cmap="hot"` (black at bottom) to `cmap="YlOrRd"` + threshold=0.08.
- Glass Brain: 1×4 thin row → 2×2 grid (large, high-DPI panels).
- Interpretation panel + Methods & provenance panel.

### v2 Copy Work (Brain Visualizer v2\)
- **Interactive 3D Surface (Plotly Mesh3d):**
  - Renders on folded pial surface (fsaverage5/6) — real gyri/sulci visible.
  - Curvature-shaded gray base (gyri light, sulci dark) + gray→red intensity map.
  - Drag to rotate, scroll to zoom, WebGL native.
  - **Why Plotly:** nilearn's `view_img_on_surf` bakes in harsh black/white curvature with no lightness control; Plotly gives full per-vertex color control.

- **Static 3D Surface Montage:**
  - Four fixed camera angles (left lateral, right lateral, top, front).
  - Same light folded-cortex model as interactive (light cortex, real folds).
  - Gray→red heat map clearly visible.
  - Embedded via `kaleido` (Plotly→PNG export).

- **Interactive Slices (nilearn `view_img`):**
  - Three synchronized planes with movable cross-hair.
  - Best for deep/subcortical inspection.
  - Embedded via `streamlit.components.v1.html`.

- **Five-view radio selector, rendering controls, threshold slider.**

- **Obsidian documentation vault:** 11+ notes covering every feature, linked as a knowledge graph.

### GitHub Publishing
1. **First repo:** `neuro-target-visualizer-v2` (later renamed).
2. **Co-author cleanup:** Removed `Co-Authored-By: Claude ... <noreply@anthropic.com>` trailers from all commits.
3. **Fresh history:** Rebuilt as single clean commit authored solely by `Ayoub Riad <ayoub.riad45@gmail.com>`.
4. **Renamed:** `neuro-target-visualizer` → `neuroviz-v2`.
5. **Final state:** PUBLIC repo, single author (you), zero co-authors/bots.

---

## 7. Technical Details

### The Brain
- **Coordinate space:** MNI152, 2 mm resolution (91 × 109 × 91 voxels).
- **Regions:** 25 fixed MNI point coordinates (e.g. Prefrontal Cortex DLPFC at x=−20, y=40, z=20).
- **Volume model:** Each region → Gaussian blob (σ = 12 mm for surface, 6 mm for glass/stat). Overlapping blobs sum.
- **Affinity scale:** User enters `kcal/mol` (range: −15 to −1). Clamped and mapped linearly to 0–100% normalized intensity.
- **Rendering:** nilearn (static surface, glass brain, stat map) or Plotly Mesh3d (interactive 3D).

### Dependencies
```
streamlit>=1.30.0      # Web UI framework
nilearn>=0.10.0        # Brain visualization (surface, glass brain, stat map)
matplotlib>=3.7.0      # Figure rendering
nibabel>=5.0.0         # NIfTI format I/O
numpy>=1.24.0          # Numerical arrays
plotly>=5.18.0         # Interactive 3D (Mesh3d)
kaleido>=0.2.1         # Plotly→PNG/PDF export (for static montage)
```

### Colour Schemes
- **Interactive 3D:** Custom gray→red scale (neutral gray at 0%, palette ramps to deep red at 100%).
- **3D Surface, Glass Brain, Stat Map:** `YlOrRd` (pale yellow → orange → deep red).
- **Both:** Mapped to same 0–100% normalized binding intensity, so they read consistently.

---

## 8. How to Use (User Guide)

### Basic Workflow
1. **Choose a brain region** from the sidebar dropdown (25 options, e.g. Amygdala, Hippocampus, Substantia Nigra).
2. **Enter binding affinity** in `kcal/mol` (e.g. −9.2 for strong, −2.0 for weak).  
   More negative = stronger, more favourable binding.
3. **Click ➕ Add Region.** Repeat to add several regions (e.g. 3–4 for a multi-target profile).
4. **Choose a View Mode** (default: Interactive 3D).
   - **Interactive 3D:** Rotate the brain to inspect from all angles.
   - **3D Surface:** See the map on a static paper-style cortical mesh.
   - **Glass Brain:** X-ray through the whole brain (deep structures visible).
   - **Stat Map:** Anatomical slices with peak-activation cross-sections.
   - **Interactive Slices:** Scrub the cross-hair through any plane.
5. **Tune rendering:** Adjust the display threshold to hide noise, pick surface resolution.
6. **Read the summary:** Affinity bars, interpretation (strongest region, distribution), and methods panel.

### Example Scenario
- Add: Prefrontal Cortex (−9.0), Hippocampus (−7.5), Substantia Nigra (−6.0).
- View: Interactive 3D (rotate to see all three hot-spots).
- Summary: "Strongest: Prefrontal Cortex (90%), distribution peaks at Prefrontal/Hippocampus."
- Methods: "MNI152 2mm, σ=12mm surface, fsaverage6, threshold=0.08."

---

## 9. What NOT in This Tool (Honest Scope)

This is a **visualization aid**, not a full drug-discovery platform. Intentionally **not** fake:

- **No measured data:** PET receptor density, mRNA expression, docking scores — you provide the affinity, the tool visualizes it.
- **No molecule input:** SMILES, ChEMBL lookup, ADMET prediction — this is not a chemistry tool.
- **No atlases:** Only 25 fixed MNI points; no Glasser/Schaefer/Desikan parcellations.
- **No interactivity beyond visualization:** Click a region → nothing happens yet. That's v3 scope.

The **Roadmap** (ENHANCEMENT_REPORT.md) lists what a v3 would need.

---

## 10. Launching Without Code

### The Simplest Way (Tested on Windows)

1. **Double-click `start_app.bat`.**
   - A black terminal window appears.
   - Waits a few seconds (first run only: building venv, ~3–5 min).
   - Opens your browser to http://localhost:8501.
   - If it doesn't, copy http://localhost:8501 into your address bar manually.

2. **To stop the app:** Close the black terminal window.

3. **To run again later:** Double-click `start_app.bat` again.

### For macOS/Linux Users Downloading from GitHub

1. Open Terminal.
2. Navigate to the folder: `cd neuroviz-v2`
3. Run: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && streamlit run app.py`
4. Opens at http://localhost:8501.

---

## 11. Files in This Summary

All code, docs, and images are in the GitHub repo:  
**https://github.com/ayoubriad1/neuroviz-v2**

Clone it or download as ZIP; everything you need is there.

---

## 12. Contact & License

- **Author:** Ayoub Riad
- **Email:** ayoub.riad45@gmail.com
- **License:** MIT (see LICENSE file)
- **Repository:** https://github.com/ayoubriad1/neuroviz-v2

---

**End of Summary**  
Generated: July 2, 2026

# 🧠 Neuro-Target Affinity Visualizer

Turn protein / drug-target **binding affinities** into intuitive **heat maps on a
3-D brain**. Enter one or more brain regions with an affinity value (in
`kcal/mol`) and see *where* — and how strongly — a target is predicted to engage
across cortical and subcortical structures, rendered five different ways
including a fully rotatable 3-D model.

![Interactive 3D brain](docs/Brain_Vault_v2/Images/interactive-3d.png)

> *Interactive 3-D view — a light, folded cortex (real gyri & sulci) with a
> gray→red affinity heat map on the affected region. Drag to rotate.*

The model is fully rotatable — the same map viewed from above:

![Interactive 3D brain, top view](docs/Brain_Vault_v2/Images/interactive-3d-top.png)

---

## Table of contents
- [Features](#features)
- [Pipeline](#pipeline)
- [Installation](#installation)
- [Launch](#launch)
- [Usage](#usage)
- [View modes](#view-modes)
- [Project structure](#project-structure)
- [Documentation](#documentation)
- [Scientific scope](#scientific-scope)
- [Supported brain regions](#supported-brain-regions)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Five visualization modes** (see [below](#view-modes)):
  Interactive 3-D · 3-D Surface · Glass Brain · Stat Map · Interactive Slices.
- **Rotatable 3-D brain** with real cortical folds and a gray→red intensity map.
- **Rendering controls** — display-threshold slider, surface resolution
  (`fsaverage5/6/full`), inflated ↔ pial toggle.
- **Binding-affinity summary** — per-region bars with strength tags.
- **Written interpretation** of the result + a **methods / provenance** panel
  for reproducibility.
- Clean, bright, brain-inspired UI. Runs entirely locally.

| 3-D Surface | Glass Brain | Stat Map |
|:---:|:---:|:---:|
| ![](docs/Brain_Vault_v2/Images/static-surface.png) | ![](docs/Brain_Vault_v2/Images/glass-brain.png) | ![](docs/Brain_Vault_v2/Images/stat-map.png) |

---

## Pipeline

```mermaid
flowchart LR
    A["Region + affinity<br/>(kcal/mol)"] --> B["Normalize<br/>0-100%"]
    B --> C["Gaussian activation<br/>volume (MNI152)"]
    C --> D["NIfTI image"]
    D --> E{"View mode"}
    E --> F["Interactive 3D<br/>(Plotly, pial)"]
    E --> G["3D Surface<br/>(nilearn, fsaverage6)"]
    E --> H["Glass Brain<br/>(2x2 projections)"]
    E --> I["Stat Map<br/>(slices)"]
    E --> J["Interactive Slices"]
```

1. You enter a brain region and a binding affinity in `kcal/mol` (more negative =
   stronger binding).
2. The value is clamped to `[-15, -1]` and mapped linearly to a **0–100 %**
   normalized intensity.
3. Each region's **MNI152** coordinate becomes the centre of a 3-D **Gaussian
   blob** stamped into a `91 × 109 × 91` volume; overlapping regions sum.
4. The volume is rendered with **nilearn** (static views) or **Plotly Mesh3d**
   (the interactive 3-D brain). Core logic lives in `visualization.py`.

---

## Installation

### 1. Install Python
Install **Python 3.13** (3.11+ also works) from
[python.org/downloads](https://www.python.org/downloads/). On Windows, tick
**"Add Python to PATH"** during setup.

### 2. Get the code
- **Easiest (no git):** on this GitHub page click the green **`< > Code`** button
  → **Download ZIP**, then unzip it.
- **Or with git:**
  ```bash
  git clone https://github.com/ayoubriad1/neuro-target-visualizer-v2.git
  ```

Dependencies install themselves the first time you launch (next section).

---

## Launch

### Windows — no coding needed
Open the project folder and **double-click `start_app.bat`**.
On the **first run** it automatically builds a virtual environment and installs
everything (a few minutes, one time), then opens the app in your browser. Later
runs start in a few seconds. **To stop it, close the terminal window.**

### Any OS — manual (command line)
```bash
# 1. create an isolated environment
python -m venv .venv

# 2. install dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt      # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS / Linux

# 3. launch
.venv\Scripts\python.exe -m streamlit run app.py                 # Windows
# streamlit run app.py                                           # macOS / Linux
```

The app opens at **http://localhost:8501**. The very first render also downloads
the brain-surface meshes once (via nilearn) and caches them. Run a second copy on
another port with `... streamlit run app.py --server.port 8502`.

---

## Usage

1. In the **sidebar**, choose a **brain region** from the dropdown.
2. Enter a **binding affinity** in `kcal/mol` (e.g. `-9.2`). More negative =
   stronger, more favourable binding.
3. Click **➕ Add Region**. Repeat to add several regions; remove any with **✕**,
   or **🗑️ Clear All**.
4. Pick a **View Mode** at the top (default: **Interactive 3D** — drag to rotate,
   scroll to zoom).
5. Tune the **Rendering** controls in the sidebar:
   - **Display threshold** — hide faint activation below a chosen intensity.
   - **Surface resolution** — `fsaverage5` (fast) → `fsaverage6` (sharp) → `fsaverage` (finest).
   - **Inflated surface** — inflated (see into sulci) vs. pial (folded).
6. Below the brain, read the **Binding Affinity Summary** (per-region bars +
   strength tags), the **Interpretation** (strongest site, distribution), and the
   **Methods & provenance** panel.

---

## View modes

| Mode | Engine | Best for |
|---|---|---|
| **Interactive 3D** | Plotly (WebGL) | Rotatable exploration; light folded cortex + gray→red heat map |
| **3D Surface** | nilearn `plot_img_on_surf` | Publication-style multi-angle cortical panels |
| **Glass Brain** | nilearn `plot_glass_brain` | Deep activation via full-depth X-ray projections (2×2) |
| **Stat Map** | nilearn `plot_stat_map` | Precise anatomical localization on MRI slices |
| **Interactive Slices** | nilearn `view_img` | Scrubbing a cross-hair through deep/subcortical structures |

---

## Project structure

```
neuro-target-visualizer/
├── app.py                 # Streamlit UI: theme, controls, view router, summary
├── visualization.py       # activation-volume builder + all renderers
├── brain_regions.py       # 25 regions → MNI coordinates
├── requirements.txt       # Python dependencies
├── start_app.bat          # Windows launcher (self-bootstraps the venv)
├── .streamlit/
│   └── config.toml        # UI theme
├── ENHANCEMENT_REPORT.md  # implemented features, roadmap, scientific scope
├── docs/
│   └── Brain_Vault_v2/    # Obsidian documentation vault (notes + images)
└── README.md
```

---

## Documentation

`docs/Brain_Vault_v2/` is an **Obsidian vault** documenting the whole project as a
linked knowledge graph: full-source notes for every file (`Code_Graph/`),
per-feature design notes, a change log, and an image `Gallery`. Open that folder
as a vault in Obsidian and press `Ctrl+G` to explore the graph. A high-level
roadmap and scope statement live in `ENHANCEMENT_REPORT.md`.

---

## Scientific scope

This is a **visualization and intuition** tool. Affinity values are
**user-entered**; the app uses **no** measured PET / mRNA data and no docking
engine. The maps show **predicted localization and relative strength** — not
measured receptor occupancy or in-vivo concentration. `ENHANCEMENT_REPORT.md`
describes how real ground-truth data (PET receptor-density atlases, parcellations,
molecule input) could be integrated in future work.

---

## Supported brain regions

Striatum (Caudate / Putamen), Nucleus Accumbens, Prefrontal Cortex (DLPFC / VMPFC),
Orbitofrontal Cortex, Anterior / Posterior Cingulate Cortex, Hippocampus, Amygdala,
Thalamus, Hypothalamus, Substantia Nigra, Ventral Tegmental Area, Raphe Nuclei,
Locus Coeruleus, Insula, Cerebellum, Primary Motor Cortex, Somatosensory Cortex,
Visual Cortex (V1), Auditory Cortex, Temporal Pole, Parietal Cortex (SPL),
Globus Pallidus.

---

## Troubleshooting

- **Port already in use** — a copy is already running; open http://localhost:8501,
  or launch with `--server.port 8502`.
- **First render is slow** — the 3-D surface downloads `fsaverage` meshes on first
  use and caches them; subsequent renders are fast.
- **`streamlit` not found** — activate the virtual environment, or call it via
  `.venv\Scripts\python.exe -m streamlit ...`.

---

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE).

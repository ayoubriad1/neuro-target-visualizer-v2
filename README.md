---
title: Neuro-Target Affinity Visualizer
emoji: 🧠
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🧠 Neuro-Target Affinity Visualizer

[![CI](https://github.com/ayoubriad1/neuroviz-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/ayoubriad1/neuroviz-v2/actions/workflows/ci.yml)

> **Deploying this yourself?** See
> [`docs/DEPLOY_HUGGINGFACE.md`](docs/DEPLOY_HUGGINGFACE.md) for a free,
> permanent, no-code deployment guide (Hugging Face Spaces). The YAML block
> above this line is Hugging Face Spaces' required metadata header — it's
> invisible on GitHub's README rendering and harmless everywhere else.

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
- [AI Interpretation](#ai-interpretation)
- [Scientific scope](#scientific-scope)
- [Supported brain regions](#supported-brain-regions)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Five visualization modes** (see [below](#view-modes)):
  Interactive 3-D · 3-D Surface · Glass Brain · Stat Map · Interactive Slices.
- **Rotatable 3-D brain** with real cortical folds and a gray→red intensity map,
  a persistent **L/R orientation compass**, and one-click **camera presets**
  (Left/Right/Top/Front/Default) so you never lose your bearings after
  rotating freely.
- **19/25 regions on real atlas masks** (Harvard-Oxford, Pauli et al. 2017) — see
  [Scientific scope](#scientific-scope).
- **Rendering controls** — display-threshold slider, surface resolution
  (`fsaverage5/6/full`), and a **colorblind-safe (viridis) color scheme** option
  alongside the default warm gray→red palette.
- **Binding-affinity summary** — per-region bars with strength tags.
- **Written interpretation** of the result + a **methods / provenance** panel
  for reproducibility.
- **Export** — download the current static figure as a high-res PNG, or the
  full affinity summary + interpretation + methods as a Markdown report.
- **Optional AI interpretation** — bring your own Claude or ChatGPT API key
  (configurable in the sidebar, never bundled or paid for by this app) to get
  a short, hallucination-guarded interpretation grounded in general
  neuroscience knowledge. See [AI Interpretation](#ai-interpretation) below.
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
  git clone https://github.com/ayoubriad1/neuroviz-v2.git
  ```

Dependencies install themselves the first time you launch (next section).

---

## Launch

### Windows — no coding needed
Open the project folder and **double-click `start_app.bat`**.
On the **first run** it automatically builds a virtual environment and installs
everything (a few minutes, one time), then opens the app in your browser. Later
runs start in a few seconds. **To stop it, close the terminal window.**

### macOS / Linux — no coding needed
Open a terminal in the project folder and run `./start_app.sh` (same
self-bootstrapping behaviour as `start_app.bat`).

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

### Docker (fully reproducible, no local Python needed)
```bash
docker compose up --build
```
Builds a container with the exact dependency set and, network permitting,
pre-downloads the brain-surface meshes and atlas data at build time (so the
first render is instant and works offline). Serves the app at
**http://localhost:7860**. (Port 7860 is also what
[Hugging Face Spaces](docs/DEPLOY_HUGGINGFACE.md) expects, so the same image
deploys there unchanged — some build environments, including HF Spaces, block
network access during the build itself, in which case this download simply
happens lazily on the first real request instead.)

### Exact reproducibility
`requirements.txt` only pins lower bounds. For a fully pinned, hash-verified
environment (recommended before citing results from this tool), install from
[`requirements.lock.txt`](requirements.lock.txt) instead:
```bash
pip install -r requirements.lock.txt
```

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
neuroviz-v2/
├── app.py                 # thin orchestrator: page config, wires the modules below
├── config.py              # affinity-scale constants, view modes, per-view guide text
├── styles.py              # theme CSS + hero header / loader HTML
├── models.py              # RegionEntry dataclass, kcal -> normalized-intensity
├── state.py               # typed session_state helpers (add/remove/clear regions)
├── ui_sidebar.py          # sidebar: region picker, active-region list, rendering options
├── ui_views.py            # view-mode selector, subcortical warning, render dispatch
├── interpretation.py      # affinity summary cards, interpretation text, methods panel
├── ai_agent.py            # optional BYOK LLM client (Claude / ChatGPT)
├── ui_ai.py               # sidebar config + trigger for the AI interpretation
├── visualization.py       # activation-volume builder + all renderers
├── brain_regions.py       # 25 regions → MNI coordinates (illustrative fallback)
├── atlas_regions.py       # 19/25 regions → real atlas masks (Harvard-Oxford, Pauli 2017)
├── mni_space.py           # shared MNI152 2mm grid constants
├── requirements.txt       # Python dependencies (lower-bound pins)
├── requirements.lock.txt  # exact, hash-verified pins for reproducibility
├── requirements-dev.txt   # + pytest / ruff / mypy
├── pyproject.toml         # ruff / mypy / pytest config
├── tests/                 # tests for models/brain_regions/atlas_regions/visualization
├── start_app.bat          # Windows launcher (self-bootstraps the venv)
├── start_app.sh           # macOS/Linux launcher (same behaviour)
├── Dockerfile             # reproducible container, best-effort mesh/atlas pre-warm
├── docker-compose.yml
├── .env.example           # API keys for the optional AI interpretation agent
├── CITATION.cff           # how to cite this tool
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

- **[`CHANGELOG.md`](CHANGELOG.md)** — everything improved in this engineering
  session (performance, real atlases, architecture, design, accessibility, AI
  interpretation), organized by phase.
- **[`docs/AI_AGENT.md`](docs/AI_AGENT.md)** — design notes for the AI
  Interpretation feature specifically: prompt design, BYOK cost model,
  provider abstraction, and testing approach.

---

## AI Interpretation

An optional sidebar section lets you generate a short, LLM-written
interpretation of your selected regions, using **your own** Claude or ChatGPT
API key — this tool never bundles, proxies, or pays for API access on your
behalf.

1. In the sidebar, under **🤖 AI Interpretation**, pick a provider (or leave it
   `Disabled`, the default).
2. Paste your API key (kept in the browser session only, never written to
   disk) and, optionally, adjust the model — a small/cheap model is
   preselected (`claude-haiku-4-5-20251001` or `gpt-4o-mini`) to keep costs low.
3. Click **Generate AI interpretation**. The result is cached per region
   selection so moving a slider or switching view mode won't silently trigger
   another paid call.

**What this is not**: it is a single constrained LLM call from general
neuroscience knowledge, not a literature search. The prompt explicitly
forbids inventing citations, PMIDs, or specific studies, and the model is
asked to flag its own confidence as low/moderate — but always verify any
claim against primary sources before relying on it. A fuller, literature-
grounded RAG design (PubMed/Semantic Scholar/OpenAlex retrieval + citation
verification) is sketched in `ENHANCEMENT_REPORT.md` as a future upgrade.

---

## Scientific scope

This is a **visualization and intuition** tool. Affinity values are
**user-entered**; the app uses **no** measured PET / mRNA data and no docking
engine. The maps show **predicted localization and relative strength** — not
measured receptor occupancy or in-vivo concentration.

**Region model** — 19 of the 25 regions render on a real, cited parcellation
mask (`atlas_regions.py`): Harvard-Oxford cortical/subcortical atlases and
Pauli et al. (2017) for basal ganglia/midbrain nuclei. The remaining 6 (small
brainstem nuclei, composite prefrontal subdivisions) have no standard
openly-available atlas and stay as illustrative MNI points — the app labels
each region "✅ Atlas-backed" or "⚠️ Illustrative" when you select it. See
`ENHANCEMENT_REPORT.md` for exact citations and the remaining roadmap
(PET-density ground truth, molecule input, spin tests).

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

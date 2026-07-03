---
tags: [code, py, ui, streamlit, v2]
path: ..\Brain Visualizer v2\app.py
---
# app.py (v2)

> [!info] Source file
> `..\Brain Visualizer v2\app.py` — the v2 Streamlit front-end. Same hero /
> sidebar / summary / interpretation as v1, **plus** five view modes, a
> Rendering controls section, and a methods panel. Full source lives in the file;
> the v2-specific pieces are below. Hub: [[Neuro-Target Visualizer v2]].

## v2 additions over v1

**Imports** — interactive renderers + components:
```python
import streamlit.components.v1 as components
from visualization import (
    create_activation_volume, plot_brain_surface, plot_brain_glass,
    plot_brain_stat, interactive_surface_plotly, interactive_volume_html,
)
```

**Five view modes** (default = Interactive 3D):
```python
VIEW_MODES = ["Interactive 3D", "3D Surface", "Glass Brain",
              "Stat Map (Slices)", "Interactive Slices"]
```

**Rendering controls** (sidebar) — feeds every renderer:
```python
threshold   = st.slider("Display threshold (intensity)", 0.0, 0.50, 0.08, 0.01)
surf_res    = st.selectbox("Surface resolution (3D Surface)", [...])  # fsaverage5/6/full
surf_inflate= st.toggle("Inflated surface", value=True)
```
See [[Display Threshold Control]] · [[Higher-Resolution Surface (fsaverage6)]].

**Interactive 3D branch** — the gray→red rotatable brain:
```python
if view_mode == "Interactive 3D":
    nifti_img = create_activation_volume(pairs, sigma=SURFACE_SIGMA)
    fig3d = interactive_surface_plotly(nifti_img, threshold=threshold)
    st.plotly_chart(fig3d, use_container_width=True)
```
See [[Interactive 3D Brain (Plotly)]]. The **Interactive Slices** branch uses
`components.html(interactive_volume_html(...))` → [[Interactive Slices]].

**Methods panel** — [[Methods & Provenance Panel]] (an `st.expander` after the
interpretation).

## Connected
Renderers in [[visualization (v2)]] · controls [[Display Threshold Control]] ·
modes [[Interactive 3D Brain (Plotly)]] / [[Interactive Slices]] · full change
list [[Changes from v1]].

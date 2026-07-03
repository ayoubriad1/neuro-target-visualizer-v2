---
tags: [code, py, rendering, v2]
path: ..\Brain Visualizer v2\visualization.py
---
# visualization.py (v2)

> [!info] Source file
> `..\Brain Visualizer v2\visualization.py` — the volume builder and renderers.
> Same `create_activation_volume` + static renderers as v1 (now with `threshold`
> / `surf_mesh` / `inflate` parameters), **plus** the interactive renderers. Hub:
> [[Neuro-Target Visualizer v2]].

## What changed vs v1
- `plot_brain_surface(nifti_img, surf_mesh="fsaverage6", inflate=True, threshold=0.01)`
  — resolution + inflate now parameterised → [[Higher-Resolution Surface (fsaverage6)]].
- `plot_brain_glass(..., threshold=0.08)` and `plot_brain_stat(..., threshold=0.08)`
  — threshold now a parameter → [[Display Threshold Control]].
- **New:** `interactive_volume_html()` (nilearn `view_img`) → [[Interactive Slices]].
- **New:** `interactive_surface_plotly()` → [[Interactive 3D Brain (Plotly)]].

## The Plotly gray→red surface (core new function)
```python
def interactive_surface_plotly(nifti_img, threshold=0.08,
                               surf_mesh="fsaverage5", height=680):
    import numpy as np, plotly.graph_objects as go
    from nilearn import datasets, surface
    fs = datasets.fetch_surf_fsaverage(surf_mesh)
    tex_l = surface.vol_to_surf(nifti_img, fs.pial_left)     # see [[vol_to_surf Projection]]
    tex_r = surface.vol_to_surf(nifti_img, fs.pial_right)
    cL, fL = _coords_faces(surface.load_surf_mesh(fs.infl_left))
    cR, fR = _coords_faces(surface.load_surf_mesh(fs.infl_right))
    # ...place hemispheres side by side, force sub-threshold vertices to gray...
    return go.Figure(go.Mesh3d(..., colorscale=_GRAY_RED, cmin=0, cmax=1))
```
Colour scheme: [[Gray-to-Red Intensity Map]] (`_GRAY_RED`). Helper
`_coords_faces()` handles any nilearn surf-mesh return type.

## Connected
Called by [[app (v2)]] · projection concept [[vol_to_surf Projection]] · full
change list [[Changes from v1]].

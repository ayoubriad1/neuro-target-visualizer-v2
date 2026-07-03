---
tags: [feature, surface, v2]
aliases: [fsaverage6, Higher Resolution Surface, Surface Resolution]
---
# 🧩 Higher-Resolution Surface (fsaverage6)

> [!info] Sharper cortex resolution selector
> v1 hard-coded the low-res `fsaverage5` mesh (~10k verts/hemi). v2 defaults to
> **`fsaverage6`** (~41k verts/hemi) for finer folds, with a UI selector. Part of
> [[Changes from v1]] · hub [[Neuro-Target Visualizer v2]].

UI (sidebar **Rendering** — see [[Display Threshold Control]]):
- **Surface resolution:** `fsaverage5` (fast) · `fsaverage6` (sharp, default) ·
  `fsaverage` (~164k, slow). Controls both the Interactive 3D and the static
  3D Surface montage.

Feeds both 3D views:
```python
fig3d = interactive_surface_plotly(nifti_img, surf_mesh=surf_mesh, threshold=threshold)
fig   = plot_brain_surface(nifti_img, surf_mesh=surf_mesh, threshold=threshold)
```

> [!note] Both 3D views use the fsaverage6 *pial* mesh
> [[Interactive 3D Brain (Plotly)]] and the static 3D Surface montage both render
> the **folded pial** surface (light cortex, real gyri/sulci) — the static view
> is just that same model captured from four fixed camera angles.

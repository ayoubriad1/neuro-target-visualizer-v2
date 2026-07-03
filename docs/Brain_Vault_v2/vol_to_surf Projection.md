---
tags: [concept, surface, v2]
aliases: [vol_to_surf, Volume to Surface, Surface Projection]
---
# 🧮 vol_to_surf Projection

> [!info] Volume → per-vertex surface colour
> How the 3-D [[NIfTI]] affinity volume becomes a colour value at every vertex of
> the cortical mesh — the step that makes [[Interactive 3D Brain (Plotly)]]
> possible. Concept note for [[Neuro-Target Visualizer v2]].

`nilearn.surface.vol_to_surf(img, mesh)` samples the volume at each mesh vertex's
location and returns a 1-D array of values (one per vertex).

Key detail used in v2:
- **Sample *and* display on the `pial` mesh** — the folded surface with real
  gyri/sulci. (v1's interactive briefly displayed on the *inflated* mesh, which
  looked too smooth; v2 uses pial so the ridges show.)

```python
tex_l = surface.vol_to_surf(nifti_img, fs.pial_left)          # sample (pial)
tex_r = surface.vol_to_surf(nifti_img, fs.pial_right)
cL, fL = _coords_faces(surface.load_surf_mesh(fs.pial_left))  # display (pial)
cR, fR = _coords_faces(surface.load_surf_mesh(fs.pial_right))
```

The two hemispheres' textures are concatenated, thresholded, and turned into
per-vertex colours ([[Gray-to-Red Intensity Map]] over a curvature-shaded gray
base). Pial coordinates *are* in MNI-aligned fsaverage space and already sit in
true anatomical position, so no offset is needed. Used by
`interactive_surface_plotly()` in [[visualization (v2)]].

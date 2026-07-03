---
tags: [feature, view-mode, interactive, v2]
aliases: [Interactive 3D, Rotatable Brain, Plotly Brain]
---
# 🧠 Interactive 3D Brain (Plotly)

> [!info] The headline v2 feature
> A **fully rotatable 3-D brain**: a **light / near-white folded cortex** (real
> gyri & sulci) with affected regions ramping **gray → yellow → orange → red** by
> binding intensity — the look of the static [[app (v2)|3D Surface]] view, but you
> can spin it in real time. Default view mode in v2. Part of [[Changes from v1]] ·
> hub [[Neuro-Target Visualizer v2]].

![[interactive-3d.png]]

## Why Plotly (not nilearn's viewer)
nilearn's `view_img_on_surf` renders the cortex with a fixed black/white
sulcal-curvature background and gives no control to flatten it to gray. To get
*"gray brain, red hot-spots"* with full vertex-level colour control, v2 builds
the mesh directly with **Plotly `Mesh3d`** (`intensitymode="vertex"`), which is
natively rotatable inside Streamlit via `st.plotly_chart`.

## How it works
1. Fetch **fsaverage6** surfaces (~41k verts/hemi) for real fold detail.
2. **Display on the folded `pial` mesh** (real gyri/sulci) — *not* the inflated
   balloon — and sample the [[NIfTI]] volume there too ([[vol_to_surf Projection]]).
3. Concatenate the two pial hemispheres (already anatomically positioned).
4. Shade the base by **curvature / sulcal depth** — near-white gyri, light-gray
   sulci — so the ridges/folds read while the cortex stays **light/white**; then
   blend the [[Gray-to-Red Intensity Map]] over vertices above the
   [[Display Threshold Control|threshold]] via `vertexcolor`.
5. Bright, even `lighting` (high ambient) keeps the brain light and clear rather
   than dark/shadowy.

```python
mesh3d = go.Mesh3d(
    x=coords[:,0], y=coords[:,1], z=coords[:,2],   # folded PIAL coords
    i=faces[:,0], j=faces[:,1], k=faces[:,2],
    vertexcolor=vertexcolor,                        # light-gray curvature + gray→red
    lighting=dict(ambient=0.78, diffuse=0.55, specular=0.05, roughness=1.0),
)
# a hidden Scatter3d marker carries the gray→red colorbar
```
Full function: `interactive_surface_plotly()` in [[visualization (v2)]]; wired
into the UI by [[app (v2)]].

## Controls
Drag = rotate · scroll = zoom · double-click = reset. Only **cortical surface**
activation shows here; for deep/subcortical hot-spots use [[Interactive Slices]].

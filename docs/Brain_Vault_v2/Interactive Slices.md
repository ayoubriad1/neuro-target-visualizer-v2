---
tags: [feature, view-mode, interactive, v2]
aliases: [Interactive Slices, Scrubbable Slices, Volume Viewer]
---
# 🩻 Interactive Slices

> [!info] Scrubbable cross-hair viewer
> A **live** anatomical viewer with three synchronized planes — click or drag to
> move the cross-hair through the brain. Best for **deep / subcortical**
> structures (hippocampus, thalamus, amygdala, substantia nigra) that the
> surface views can't show. Part of [[Changes from v1]] · hub
> [[Neuro-Target Visualizer v2]].

Built on nilearn's `view_img` (brainsprite), returned as an HTML iframe and
embedded with `streamlit.components.v1.html`:

```python
view = plotting.view_img(
    nifti_img, threshold=threshold, cmap="YlOrRd",
    symmetric_cmap=False, vmax=1.0, black_bg=False, colorbar=True,
)
return view.get_iframe(width=width, height=height)
```

Function `interactive_volume_html()` in [[visualization (v2)]]; the affinity map
is overlaid (warm) on the gray MNI anatomical template, so you can read off the
exact slice where a region lights up. Complements
[[Interactive 3D Brain (Plotly)]] (cortex-only) by exposing depth.
Honours the [[Display Threshold Control]].

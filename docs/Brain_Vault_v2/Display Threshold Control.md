---
tags: [feature, ui, control, v2]
aliases: [Display Threshold, Threshold Slider, Rendering Controls]
---
# 🎚️ Display Threshold Control

> [!info] One slider, every view
> A sidebar **Rendering** section (new in v2) lets the user set a single
> **display threshold** (0.00–0.50) that is threaded through *all* renderers, so
> faint activation can be hidden and only the strongest voxels shown. Part of
> [[Changes from v1]] · hub [[Neuro-Target Visualizer v2]].

```python
threshold = st.slider("Display threshold (intensity)",
                      min_value=0.0, max_value=0.50, value=0.08, step=0.01)
```

It feeds:
- [[Interactive 3D Brain (Plotly)]] — vertices below threshold are forced gray.
- Glass Brain & Stat Map — `threshold=` on the nilearn renderers.
- [[Interactive Slices]] — `view_img(threshold=…)`.
- Static 3D Surface — `plot_brain_surface(threshold=…)`.

The same **Rendering** section also holds the surface-resolution selector —
see [[Higher-Resolution Surface (fsaverage6)]]. All wired in [[app (v2)]];
renderer signatures in [[visualization (v2)]].

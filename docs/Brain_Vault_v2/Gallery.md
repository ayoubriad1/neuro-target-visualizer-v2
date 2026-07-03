---
tags: [images, gallery, v2]
aliases: [Images, Screenshots, Renders]
---
# 🖼️ Gallery — v2 rendered views

> [!abstract] Actual output
> Real renders from the v2 tool (fsaverage6, MNI152), one per view mode. Hub:
> [[Neuro-Target Visualizer v2]]. Example regions: DLPFC, Hippocampus,
> Substantia Nigra, Caudate.

## Interactive 3D — rotatable, light folded brain
The headline v2 view: a white folded cortex (real gyri/sulci) with a gray → red
heat map on affected regions. Rotatable live; static export shown here.
See [[Interactive 3D Brain (Plotly)]].

![[interactive-3d.png]]

The same map from above — the model rotates freely:

![[interactive-3d-top.png]]

## Static 3D Surface (paper-style, fsaverage6)
Multi-angle cortical panels. See [[Higher-Resolution Surface (fsaverage6)]].

![[static-surface.png]]

## Glass Brain — 2×2 X-ray projections
Full-depth projections; deep activation always visible.

![[glass-brain.png]]

## Stat Map — anatomical slices
Axial strip + orthogonal cross-sections at the peak. See [[Interactive Slices]]
for the scrubbable version.

![[stat-map.png]]

---
Colour scale on every view = normalized binding intensity (0 % → 100 %) via the
[[Gray-to-Red Intensity Map]] / YlOrRd. Full code: [[_Code Graph Index]].

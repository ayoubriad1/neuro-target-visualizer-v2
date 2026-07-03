---
tags: [feature, color, design, v2]
aliases: [Gray to Red, Gray-Red Colormap, Intensity Colormap]
---
# 🎨 Gray-to-Red Intensity Map

> [!info] The colour scheme for the 3-D brain
> Requested look: *"all the brain in a gray colour, but the affected region gets
> really red and gradually."* This is the colorscale that delivers it for
> [[Interactive 3D Brain (Plotly)]]. Part of [[Changes from v1]].

The whole cortex sits at intensity `0` → neutral gray. Above the
[[Display Threshold Control|threshold]], intensity ramps warm:

```python
_GRAY_RED = [
    [0.000, "#9aa0a6"],   # no activation → neutral gray
    [0.001, "#9aa0a6"],
    [0.150, "#ffe49c"],   # pale yellow
    [0.400, "#ff9d3a"],   # orange
    [0.700, "#f24420"],   # red
    [1.000, "#b40426"],   # deep red
]
```

- Vertices below threshold are set to exactly `0.0`, so they render gray.
- `cmin=0, cmax=1` ties the ramp to the normalized 0–100 % binding intensity, so
  the colours mean the same thing as the YlOrRd scale on the other views and the
  bars in the affinity summary.

This intentionally mirrors the *static* 3D-surface aesthetic (gray cortex, warm
hot-spots) while staying interactive. Defined in [[visualization (v2)]] as
`_GRAY_RED`.

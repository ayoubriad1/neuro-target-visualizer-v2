"""Static configuration: affinity scale constants, view modes, and the
per-view-mode "how to read this" guide text shown in app.py.
"""

KCAL_MIN = -15.0
KCAL_MAX = -1.0
SURFACE_SIGMA = 12.0
DEFAULT_SIGMA = 6.0

VIEW_MODES = [
    "Interactive 3D",
    "3D Surface",
    "Glass Brain",
    "Stat Map (Slices)",
    "Interactive Slices",
]

# Display name -> matplotlib colormap name. "YlOrRd" is the original warm
# gray->red ramp; "viridis" is a perceptually-uniform, colorblind-safe
# alternative (see visualization._scheme_colormap / _scheme_gray_ramp).
COLOR_SCHEMES = {
    "Warm (gray → red)": "YlOrRd",
    "Colorblind-safe (viridis)": "viridis",
}
DEFAULT_COLOR_SCHEME = "Warm (gray → red)"

VIEW_MODE_HELP = (
    "Interactive 3D — rotate/zoom the cortical surface in your browser (WebGL). "
    "3D Surface — static cortical mesh from multiple angles (paper style). "
    "Glass Brain — transparent X-ray projection, best for deep structures. "
    "Stat Map — static anatomical MRI slices. "
    "Interactive Slices — scrub the cross-hair through the brain in 3 planes."
)

GUIDE_SURFACE = """
| Panel | What you are seeing |
|-------|---------------------|
| **Left — Lateral (Outer Surface)** | Side view of the left hemisphere from the outside. Shows lateral cortex (motor, parietal, temporal areas). |
| **Right — Lateral** | Same as above for the right hemisphere. |
| **Front (Anterior)** | Looking straight at the forehead side of the brain. Shows frontal lobes. |
| **Top (Dorsal)** | Bird's-eye view from above the head. Shows superior cortex. |
| **Bottom (Inferior)** | View from below the head, looking up. Shows orbitofrontal cortex and temporal poles. |

**Color scale** — Gray surface = no activation (below threshold).
Yellow → Orange → Red = increasing binding affinity.
Only regions with ≥ 1 % intensity are colored, matching the style of *Yachou et al. 2025* (Fig. 2–3).
"""

GUIDE_GLASS = """
The four projections are arranged in a **2 × 2 grid** so each panel is large and high-detail:

| Panel | Direction | What you are seeing |
|-------|-----------|---------------------|
| **Top-left — Left Sagittal** | From the left side | Full left-to-right projection through the brain |
| **Top-right — Right Sagittal** | From the right side | Mirror of the left sagittal panel |
| **Bottom-left — Axial (Top-down)** | From above | Projection from the crown — like an X-ray from the top |
| **Bottom-right — Coronal (Front)** | From the front | Front-to-back projection — shows bilateral activation |

Because each panel is a **full-depth projection** (like an X-ray), deep subcortical regions (thalamus, hippocampus, striatum) are always visible, even if they cannot be seen on the cortical surface.
"""

GUIDE_STAT = """
| Row | What you are seeing |
|-----|---------------------|
| **Axial slices (Row 1)** | Eight horizontal cuts through the brain, equally spaced from bottom to top. Each slice is like one layer of an MRI scan. Useful for seeing bilateral and deep structures. |
| **Orthogonal cross-sections (Row 2)** | Three perpendicular slices placed at the coordinates of the **peak activation** in your data: sagittal (left–right cut), coronal (front–back cut), axial (top–bottom cut). The cross-hair marks the exact peak location. |

Use this mode when you need to inspect **subcortical structures** (hippocampus, thalamus, amygdala, basal ganglia) that sit deep inside the brain and may not appear prominently on the cortical surface view.
"""

GUIDE_INTER3D = """
A **live, fully rotatable 3-D brain** (Plotly / WebGL):

- The whole cortex is shown in **neutral gray**; **affected regions ramp
  gray → yellow → orange → deep-red** as binding intensity increases — the same
  read as the static *3D Surface* view, but you can spin it.
- **Drag** to rotate in any direction · **scroll** to zoom · **double-click**
  to reset.

It uses a lighter mesh (fsaverage5) so rotation stays smooth. Only cortical
surface activation is visible here; for deep subcortical hot-spots use
*Interactive Slices* or *Glass Brain*.
"""

GUIDE_INTERSLICES = """
A **live, scrubbable** anatomical viewer with three synchronized planes:

- **Click or drag** on any panel to move the **cross-hair**; all three planes
  update together.
- The affinity map is overlaid on the MNI anatomical template, so you can read
  off the exact slice where a region lights up.

Best for **deep / subcortical** structures (hippocampus, thalamus, amygdala,
basal ganglia, substantia nigra) that the surface views cannot show.
"""

GUIDES = {
    "Interactive 3D": GUIDE_INTER3D,
    "3D Surface": GUIDE_SURFACE,
    "Glass Brain": GUIDE_GLASS,
    "Stat Map (Slices)": GUIDE_STAT,
    "Interactive Slices": GUIDE_INTERSLICES,
}

---
tags: [code, py, v2]
path: app.py
lines: 562
---
# app.py

> [!info] Source file (v2)
> `app.py` &middot; 562 lines &middot; Streamlit front-end: theme, centered hero, sidebar region picker + rendering controls, the 5-way view router, affinity summary, interpretation, and methods panel.

## Connected notes
[[visualization]] &middot; [[brain_regions]] &middot; [[config]] &middot; [[start_app]]

## Full source

```python
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from brain_regions import get_region_names
from visualization import (
    create_activation_volume,
    plot_brain_surface,
    plot_brain_glass,
    plot_brain_stat,
    interactive_surface_plotly,
    interactive_volume_html,
)

KCAL_MIN = -15.0
KCAL_MAX = -1.0
SURFACE_SIGMA = 12.0
DEFAULT_SIGMA = 6.0

GUIDE_SURFACE = """
| Panel | What you are seeing |
|-------|---------------------|
| **Left â€” Lateral (Outer Surface)** | Side view of the left hemisphere from the outside. Shows lateral cortex (motor, parietal, temporal areas). |
| **Right â€” Lateral** | Same as above for the right hemisphere. |
| **Front (Anterior)** | Looking straight at the forehead side of the brain. Shows frontal lobes. |
| **Top (Dorsal)** | Bird's-eye view from above the head. Shows superior cortex. |
| **Bottom (Inferior)** | View from below the head, looking up. Shows orbitofrontal cortex and temporal poles. |

**Color scale** â€” Gray surface = no activation (below threshold).
Yellow â†’ Orange â†’ Red = increasing binding affinity.
Only regions with â‰¥ 1 % intensity are colored, matching the style of *Yachou et al. 2025* (Fig. 2â€“3).
"""

GUIDE_GLASS = """
The four projections are arranged in a **2 Ã— 2 grid** so each panel is large and high-detail:

| Panel | Direction | What you are seeing |
|-------|-----------|---------------------|
| **Top-left â€” Left Sagittal** | From the left side | Full left-to-right projection through the brain |
| **Top-right â€” Right Sagittal** | From the right side | Mirror of the left sagittal panel |
| **Bottom-left â€” Axial (Top-down)** | From above | Projection from the crown â€” like an X-ray from the top |
| **Bottom-right â€” Coronal (Front)** | From the front | Front-to-back projection â€” shows bilateral activation |

Because each panel is a **full-depth projection** (like an X-ray), deep subcortical regions (thalamus, hippocampus, striatum) are always visible, even if they cannot be seen on the cortical surface.
"""

GUIDE_STAT = """
| Row | What you are seeing |
|-----|---------------------|
| **Axial slices (Row 1)** | Eight horizontal cuts through the brain, equally spaced from bottom to top. Each slice is like one layer of an MRI scan. Useful for seeing bilateral and deep structures. |
| **Orthogonal cross-sections (Row 2)** | Three perpendicular slices placed at the coordinates of the **peak activation** in your data: sagittal (leftâ€“right cut), coronal (frontâ€“back cut), axial (topâ€“bottom cut). The cross-hair marks the exact peak location. |

Use this mode when you need to inspect **subcortical structures** (hippocampus, thalamus, amygdala, basal ganglia) that sit deep inside the brain and may not appear prominently on the cortical surface view.
"""

GUIDE_INTER3D = """
A **live, fully rotatable 3-D brain** (Plotly / WebGL):

- The whole cortex is shown in **neutral gray**; **affected regions ramp
  gray â†’ yellow â†’ orange â†’ deep-red** as binding intensity increases â€” the same
  read as the static *3D Surface* view, but you can spin it.
- **Drag** to rotate in any direction Â· **scroll** to zoom Â· **double-click**
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


def kcal_to_normalized(kcal):
    clamped = max(KCAL_MIN, min(KCAL_MAX, kcal))
    return (abs(clamped) - abs(KCAL_MAX)) / (abs(KCAL_MIN) - abs(KCAL_MAX)) * 100.0


# Page config
st.set_page_config(
    page_title="Neuro-Target Affinity Visualizer Â· v2",
    page_icon="ðŸ§ ",
    layout="wide",
)

# Theme & custom styling
# Bright, brain-inspired palette (soft lavender-gray on near-white) plus a
# rotating-brain loader that replaces Streamlit's default sport-icon splash.
st.markdown(
    """
    <style>
    /* ---- Base palette ---------------------------------------------------- */
    .stApp {
        background: linear-gradient(160deg, #FBFBFE 0%, #F2F1F9 55%, #ECEAF6 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F3F1FB 0%, #E8E5F4 100%);
        border-right: 1px solid #E0DCEF;
    }

    /* ---- Centered hero header -------------------------------------------- */
    .brain-hero { text-align: center; margin: 0.2rem 0 1.3rem 0; }
    .brain-hero .brain-icon {
        font-size: 56px; display: inline-block; line-height: 1;
        animation: brainspin 3.4s linear infinite;
        filter: drop-shadow(0 5px 12px rgba(138,111,196,0.35));
    }
    .brain-hero h1 {
        font-size: 2.5rem; font-weight: 800; margin: 0.35rem 0 0 0;
        background: linear-gradient(90deg, #6E5BB5 0%, #9A6FC9 45%, #C77FB4 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .brain-hero .subtitle {
        color: #5C5570; font-size: 1.05rem; margin-top: 0.4rem;
    }
    .brain-hero .byline {
        margin-top: 0.75rem; font-size: 1.25rem; color: #5C5570; font-weight: 500;
    }
    .brain-hero .byline b {
        color: #6E5BB5; font-size: 1.45rem; font-weight: 800;
        letter-spacing: 0.3px;
    }
    .brain-hero hr {
        border: none; height: 2px; width: 130px; margin: 1rem auto 0 auto;
        background: linear-gradient(90deg, transparent, #B49BDE, transparent);
    }

    /* ---- Rotating brain at the top of the sidebar ------------------------ */
    .sidebar-brain { text-align: center; margin: 0.1rem 0 0.5rem 0; }
    .sidebar-brain .spin {
        font-size: 46px; display: inline-block; line-height: 1;
        animation: brainspin 3.4s linear infinite;
        filter: drop-shadow(0 4px 10px rgba(138,111,196,0.35));
    }

    /* ---- Buttons --------------------------------------------------------- */
    .stButton > button {
        border-radius: 10px; border: 1px solid #CFC4EA;
        background: #FFFFFF; color: #4B4368; font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        border-color: #8A6FC4; color: #6E5BB5;
        box-shadow: 0 2px 10px rgba(138,111,196,0.25);
    }

    /* ---- Affinity summary (professional / futuristic bars) --------------- */
    .aff-wrap { margin-top: 0.4rem; }
    .aff-card {
        background: rgba(255,255,255,0.66);
        border: 1px solid #E2DCF1; border-radius: 14px;
        padding: 0.85rem 1.1rem; margin-bottom: 0.7rem;
        box-shadow: 0 2px 12px rgba(110,91,181,0.07);
        backdrop-filter: blur(4px);
    }
    .aff-head {
        display: flex; align-items: baseline; justify-content: space-between;
        gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.55rem;
    }
    .aff-name { font-weight: 700; font-size: 1.02rem; color: #2D2A3A; }
    .aff-meta { display: flex; align-items: center; gap: 0.5rem; }
    .aff-kcal {
        font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.8rem;
        color: #6E5BB5; background: #EFEAF9;
        padding: 0.12rem 0.5rem; border-radius: 6px;
    }
    .aff-tag {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.4px;
        text-transform: uppercase; color: #FFFFFF;
        padding: 0.12rem 0.55rem; border-radius: 6px;
    }
    .aff-bar-row { display: flex; align-items: center; gap: 0.85rem; }
    .aff-track {
        position: relative; flex: 1; height: 13px; border-radius: 999px;
        background: #E8E3F4; overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(76,67,104,0.18);
    }
    .aff-fill {
        position: relative; height: 100%; border-radius: 999px; overflow: hidden;
        background: linear-gradient(90deg, #6E5BB5 0%, #9A6FC9 50%, #C77FB4 100%);
        box-shadow: 0 0 10px rgba(154,111,201,0.55);
    }
    .aff-fill::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        transform: translateX(-100%);
        animation: shimmer 2.2s ease-in-out infinite;
    }
    @keyframes shimmer { 100% { transform: translateX(100%); } }
    .aff-pct {
        min-width: 50px; text-align: right; font-weight: 800;
        font-size: 1.0rem; color: #6E5BB5;
    }

    /* ---- Rotating-brain loader (reusable + first-load splash) ------------ */
    @keyframes brainspin {
        0%   { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    @keyframes slidebar {
        0%   { margin-left: -45%; }
        100% { margin-left: 100%; }
    }
    .brain-loader-wrap {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; padding: 2.6rem 0; gap: 0.9rem;
    }
    .brain-loader-wrap .spin {
        font-size: 74px; display: inline-block; line-height: 1;
        animation: brainspin 1.5s linear infinite;
        filter: drop-shadow(0 5px 14px rgba(138,111,196,0.40));
    }
    .brain-loader-wrap .msg {
        color: #6E5BB5; font-weight: 600; letter-spacing: 0.3px;
    }
    .brain-loader-wrap .track {
        width: 230px; height: 6px; border-radius: 999px;
        background: #E2DCF1; overflow: hidden;
    }
    .brain-loader-wrap .track .bar {
        height: 100%; width: 45%; border-radius: 999px;
        background: linear-gradient(90deg, #8A6FC4, #C77FB4);
        animation: slidebar 1.4s ease-in-out infinite;
    }

    /* Replace Streamlit's built-in first-load sport icons with a brain */
    [data-testid="stSkeleton"],
    .stApp [class*="loading"] svg,
    .stApp [class*="Loading"] svg,
    div[data-testid="stDecoration"],
    div[class*="loaderContainer"] svg,
    div[class*="loaderContainer"] img,
    div[class*="LoadingContainer"] svg,
    div[class*="LoadingContainer"] img { display: none !important; }
    div[class*="loaderContainer"]::before,
    div[class*="LoadingContainer"]::before {
        content: "ðŸ§ "; font-size: 72px; display: block; text-align: center;
        animation: brainspin 1.5s linear infinite;
    }

    /* ---- Top-right "Runningâ€¦" indicator â†’ spinning brain (was a runner) -- */
    [data-testid="stStatusWidgetRunningIcon"] svg,
    [data-testid="stStatusWidgetRunningManIcon"] { display: none !important; }
    [data-testid="stStatusWidgetRunningIcon"]::before {
        content: "ðŸ§ "; font-size: 1.55rem; line-height: 1;
        display: inline-block; transform-origin: center;
        animation: brainspin 1.4s linear infinite;
    }

    /* ---- Remove the Deploy button (not relevant for local use) ---------- */
    [data-testid="stAppDeployButton"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def brain_loader_html(message):
    """A centered, rotating-brain spinner with an indeterminate progress bar."""
    return (
        '<div class="brain-loader-wrap">'
        '<span class="spin">ðŸ§ </span>'
        f'<div class="msg">{message}</div>'
        '<div class="track"><div class="bar"></div></div>'
        '</div>'
    )


# Centered hero header
st.markdown(
    """
    <div class="brain-hero">
        <span class="brain-icon">ðŸ§ </span>
        <h1>Neuro-Target Affinity Visualizer</h1>
        <div class="subtitle">Visualize protein / target binding affinity across brain regions</div>
        <div class="byline">ðŸ”¬ Made by <b>Ayoub Riad</b> &nbsp;Â·&nbsp; Researcher in Bioinformatics</div>
        <hr/>
    </div>
    """,
    unsafe_allow_html=True,
)

if "regions" not in st.session_state:
    st.session_state.regions = []

# Sidebar
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brain"><span class="spin">ðŸ§ </span></div>',
        unsafe_allow_html=True,
    )
    st.header("Add Brain Region")
    region = st.selectbox("Brain Region", get_region_names())
    kcal_score = st.number_input(
        "Binding Affinity (kcal/mol)",
        min_value=-15.0,
        max_value=-0.1,
        value=-7.0,
        step=0.1,
        format="%.1f",
        help="Enter a negative value. More negative = stronger binding. "
             "Typical range: -1 (weak) to -15 (very strong).",
    )

    if st.button("âž• Add Region", use_container_width=True):
        st.session_state.regions.append(
            (region, kcal_score, kcal_to_normalized(kcal_score))
        )
        st.rerun()

    st.divider()
    st.header("Active Regions")

    if not st.session_state.regions:
        st.info("No regions added yet.")
    else:
        to_remove = None
        for i, (name, kcal, norm) in enumerate(st.session_state.regions):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{name}**  \n{kcal:.1f} kcal/mol ({norm:.0f} %)")
            if col2.button("âœ•", key=f"rm_{i}"):
                to_remove = i

        if to_remove is not None:
            st.session_state.regions.pop(to_remove)
            st.rerun()

        if st.button("ðŸ—‘ï¸ Clear All", use_container_width=True):
            st.session_state.regions.clear()
            st.rerun()

    # Rendering options (v2)
    st.divider()
    st.header("Rendering")
    threshold = st.slider(
        "Display threshold (intensity)",
        min_value=0.0, max_value=0.50, value=0.08, step=0.01,
        help="Hide activation below this normalized intensity. Higher = only the "
             "strongest voxels are shown. Applies to all three views.",
    )
    surf_res = st.selectbox(
        "Surface resolution (3D views)",
        ["fsaverage6  Â·  ~41k/hemi (sharp)",
         "fsaverage5  Â·  ~10k/hemi (fast)",
         "fsaverage   Â·  ~164k/hemi (slow)"],
        index=0,
        help="Higher-resolution cortical mesh = finer folds, slower render.",
    )

# View mode selector
VIEW_MODES = [
    "Interactive 3D",
    "3D Surface",
    "Glass Brain",
    "Stat Map (Slices)",
    "Interactive Slices",
]
view_mode = st.radio(
    "View Mode",
    VIEW_MODES,
    horizontal=True,
    help=(
        "Interactive 3D â€” rotate/zoom the cortical surface in your browser (WebGL). "
        "3D Surface â€” static cortical mesh from multiple angles (paper style). "
        "Glass Brain â€” transparent X-ray projection, best for deep structures. "
        "Stat Map â€” static anatomical MRI slices. "
        "Interactive Slices â€” scrub the cross-hair through the brain in 3 planes."
    ),
)

# Per-mode guide
GUIDES = {
    "Interactive 3D": GUIDE_INTER3D,
    "3D Surface": GUIDE_SURFACE,
    "Glass Brain": GUIDE_GLASS,
    "Stat Map (Slices)": GUIDE_STAT,
    "Interactive Slices": GUIDE_INTERSLICES,
}
with st.expander(f"How to read the {view_mode} view", expanded=False):
    st.markdown(GUIDES[view_mode])

# Main visualization
if st.session_state.regions:
    pairs = [(name, norm) for name, _, norm in st.session_state.regions]
    surf_mesh = surf_res.split()[0]   # "fsaverage6" / "fsaverage5" / "fsaverage"

    loader = st.empty()
    if view_mode == "Interactive 3D":
        loader.markdown(
            brain_loader_html("Building interactive 3D brainâ€¦"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=SURFACE_SIGMA)
        fig3d = interactive_surface_plotly(nifti_img, threshold=threshold, surf_mesh=surf_mesh)
        loader.empty()
        st.caption("ðŸ–±ï¸ Drag to rotate Â· scroll to zoom â€” gray cortex; affected "
                   "regions ramp gray â†’ red by intensity.")
        st.plotly_chart(fig3d, use_container_width=True)
    elif view_mode == "Interactive Slices":
        loader.markdown(
            brain_loader_html("Building interactive slice viewerâ€¦"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        html = interactive_volume_html(nifti_img, threshold=threshold)
        loader.empty()
        st.caption("ðŸ–±ï¸ Click or drag on any panel to move the cross-hair through "
                   "the brain â€” best for deep / subcortical structures.")
        components.html(html, height=560, scrolling=False)
    elif view_mode == "3D Surface":
        loader.markdown(
            brain_loader_html("Rendering 3D surface â€” this takes ~20 secondsâ€¦"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=SURFACE_SIGMA)
        fig = plot_brain_surface(nifti_img, surf_mesh=surf_mesh, threshold=threshold)
        loader.empty()
        st.pyplot(fig)
        plt.close(fig)
    elif view_mode == "Glass Brain":
        loader.markdown(
            brain_loader_html("Rendering glass brainâ€¦"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        fig = plot_brain_glass(nifti_img, threshold=threshold)
        loader.empty()
        st.pyplot(fig)
        plt.close(fig)
    else:  # Stat Map (Slices)
        loader.markdown(
            brain_loader_html("Rendering anatomical slicesâ€¦"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        fig = plot_brain_stat(nifti_img, threshold=threshold)
        loader.empty()
        st.pyplot(fig)
        plt.close(fig)

    # Summary - professional affinity bars
    st.subheader("Binding Affinity Summary")
    st.caption(
        "Normalized binding intensity per region â€” 0 % (weak) â†’ 100 % (very strong)."
    )

    def _strength(norm):
        if norm >= 75:
            return "Very strong", "#6E5BB5"
        if norm >= 50:
            return "Strong", "#8A6FC4"
        if norm >= 25:
            return "Moderate", "#B07CC9"
        return "Weak", "#C9A7DE"

    rows = []
    for name, kcal, norm in st.session_state.regions:
        label, color = _strength(norm)
        rows.append(
            '<div class="aff-card">'
            '<div class="aff-head">'
            f'<span class="aff-name">{name}</span>'
            '<span class="aff-meta">'
            f'<span class="aff-kcal">{kcal:.1f} kcal/mol</span>'
            f'<span class="aff-tag" style="background:{color}">{label}</span>'
            '</span>'
            '</div>'
            '<div class="aff-bar-row">'
            f'<div class="aff-track"><div class="aff-fill" style="width:{norm:.0f}%"></div></div>'
            f'<span class="aff-pct">{norm:.0f}%</span>'
            '</div>'
            '</div>'
        )
    st.markdown(f'<div class="aff-wrap">{"".join(rows)}</div>', unsafe_allow_html=True)

    # Interpretation
    st.divider()
    st.subheader("Interpretation")

    ranked = sorted(st.session_state.regions, key=lambda r: r[2], reverse=True)
    n = len(ranked)
    top_name, top_kcal, top_norm = ranked[0]
    n_strong = sum(1 for _, _, nm in ranked if nm >= 50)
    n_moderate = sum(1 for _, _, nm in ranked if 25 <= nm < 50)
    n_weak = sum(1 for _, _, nm in ranked if nm < 25)
    mean_kcal = sum(k for _, k, _ in ranked) / n
    region_word = "region" if n == 1 else "regions"

    if n > 1:
        runner_up = ranked[1][0]
        secondary = (
            f" The next strongest site is **{runner_up}**, and the mean affinity "
            f"across the selection is **{mean_kcal:.1f} kcal/mol**."
        )
    else:
        secondary = ""

    st.markdown(
        f"""
Across the **{n}** selected {region_word}, **{top_name}** shows the strongest
predicted binding affinity at **{top_kcal:.1f} kcal/mol** (â‰ˆ {top_norm:.0f} %
normalized intensity) â€” the most likely engagement site in this map.{secondary}

**Strength distribution:** {n_strong} strongâ€“toâ€“very-strong (â‰¥ 50 %),
{n_moderate} moderate (25â€“50 %), and {n_weak} weak (< 25 %).

**How to read these results** â€” affinity is reported in **kcal/mol**, where a
*more negative* value means *stronger, more favourable* binding. Values are
normalized to the âˆ’1 kcal/mol (weak) â†’ âˆ’15 kcal/mol (very strong) range that
drives the colour scale, so the percentages and the warm colours on the maps
track the same quantity. The renderings show **where** a target is predicted to
engage across cortical and subcortical structures and their **relative**
strength â€” they indicate predicted localization, not measured receptor
occupancy or in-vivo concentration.
"""
    )

    # Methods & provenance (v2)
    st.divider()
    with st.expander("ðŸ”¬ Methods & provenance (for reproducibility)", expanded=False):
        import sys, datetime
        try:
            import nilearn as _nl, matplotlib as _mpl, numpy as _np
            _vers = f"nilearn {_nl.__version__} Â· matplotlib {_mpl.__version__} Â· numpy {_np.__version__}"
        except Exception:
            _vers = "n/a"
        _surf_mesh = surf_res.split()[0]
        st.markdown(
            f"""
| Item | Value |
|------|-------|
| Tool version | **v2** (enhanced) |
| Coordinate space | MNI152, 2 mm (91Ã—109Ã—91) |
| Region model | {len(get_region_names())} regions as single MNI points â†’ Gaussian blobs |
| Activation Ïƒ | surface = {SURFACE_SIGMA} mm Â· glass/stat = {DEFAULT_SIGMA} mm |
| Cortical surface | `{_surf_mesh}` Â· {'inflated' if surf_inflate else 'pial'} |
| Colormap | YlOrRd (0 â†’ 1 normalized intensity) |
| Display threshold | {threshold:.2f} |
| kcal/mol â†’ % | linear over [{KCAL_MIN:.0f}, {KCAL_MAX:.0f}] |
| Renderer | {_vers} Â· Python {sys.version.split()[0]} |
| Generated | {datetime.datetime.now():%Y-%m-%d %H:%M} |

**Data provenance** â€” affinity values are **user-entered** (`kcal/mol`); v2 uses
**no** external database or measured PET/mRNA map. Region coordinates are fixed
MNI points (`brain_regions.py`). See **`ENHANCEMENT_REPORT.md`** for the full
upgrade plan, including what real data would be needed to add PET-density,
atlas-based scoring, and spatial null models.
"""
        )

else:
    st.info("Add brain regions from the sidebar to begin visualization.")
```

Part of [[_Code Graph Index]] &middot; v2 hub [[Neuro-Target Visualizer v2]].

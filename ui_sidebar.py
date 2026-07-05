"""Sidebar: region picker + active-region list + rendering options."""
import streamlit as st

from atlas_regions import get_atlas_source, is_atlas_backed
from brain_regions import get_region_names
from config import COLOR_SCHEMES, DEFAULT_COLOR_SCHEME
from mni_space import MNI_X_RANGE, MNI_Y_RANGE, MNI_Z_RANGE
from models import strength_label
from state import add_region, clear_regions, get_regions, remove_region
from styles import render_sidebar_brain_icon

_INPUT_MODE_NAMED = "Named region (atlas-verified)"
_INPUT_MODE_EXACT = "Exact MNI coordinates (advanced)"


def render_sidebar() -> tuple[float, str, str]:
    """Renders the full sidebar; returns (threshold, surf_mesh, mpl_cmap) for the main view."""
    with st.sidebar:
        render_sidebar_brain_icon()
        st.header("Add Brain Region")

        input_mode = st.radio(
            "Input mode",
            [_INPUT_MODE_NAMED, _INPUT_MODE_EXACT],
            help="Named region: pick from the 28 atlas-verified regions below. "
                 "Exact coordinates: for researchers who already know their precise "
                 "target (e.g. a DBS contact or a paper-reported peak) - renders a "
                 "focused point exactly there instead of a whole-region mask.",
        )

        coordinates = None
        if input_mode == _INPUT_MODE_NAMED:
            region = st.selectbox("Brain Region", get_region_names())
            if is_atlas_backed(region):
                st.caption(f"✅ Atlas-backed — {get_atlas_source(region)}")
            else:
                st.caption("⚠️ Illustrative point (no standard atlas available for this region)")
        else:
            st.caption(
                "Renders a single focused point at this exact MNI152 coordinate - "
                "not tied to any atlas region, and **not** mirrored across the "
                "midline (unlike named regions, since this location was chosen on "
                "purpose and may be intentionally one-sided)."
            )
            col_x, col_y, col_z = st.columns(3)
            x = col_x.number_input("X (mm)", min_value=MNI_X_RANGE[0], max_value=MNI_X_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = left, positive = right.")
            y = col_y.number_input("Y (mm)", min_value=MNI_Y_RANGE[0], max_value=MNI_Y_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = posterior, positive = anterior.")
            z = col_z.number_input("Z (mm)", min_value=MNI_Z_RANGE[0], max_value=MNI_Z_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = inferior, positive = superior.")
            coordinates = (x, y, z)
            region = f"Custom ({x:.0f}, {y:.0f}, {z:.0f})"

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

        if st.button("➕ Add Region", width="stretch"):
            add_region(region, kcal_score, coordinates)
            st.rerun()

        st.divider()
        st.header("Active Regions")

        regions = get_regions()
        if not regions:
            st.info("No regions added yet.")
        else:
            to_remove = None
            for i, entry in enumerate(regions):
                label, color, text_color = strength_label(entry.normalized_intensity)
                col1, col2 = st.columns([4, 1])
                col1.markdown(
                    '<div class="region-chip">'
                    f'<div class="region-chip-name">{entry.name}</div>'
                    '<div class="region-chip-meta">'
                    f'<span>{entry.kcal:.1f} kcal/mol · {entry.normalized_intensity:.0f}%</span>'
                    f'<span class="region-chip-tag" style="background:{color};color:{text_color}">{label}</span>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                if col2.button("✕", key=f"rm_{i}", help=f"Remove {entry.name}"):
                    to_remove = i

            if to_remove is not None:
                remove_region(to_remove)
                st.rerun()

            if st.button("🗑️ Clear All", width="stretch"):
                clear_regions()
                st.rerun()

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
            ["fsaverage6  ·  ~41k/hemi (sharp)",
             "fsaverage5  ·  ~10k/hemi (fast)",
             "fsaverage   ·  ~164k/hemi (slow)"],
            index=0,
            help="Higher-resolution cortical mesh = finer folds, slower render.",
        )
        surf_mesh = surf_res.split()[0]   # "fsaverage6" / "fsaverage5" / "fsaverage"

        scheme_name = st.selectbox(
            "Color scheme",
            list(COLOR_SCHEMES.keys()),
            index=list(COLOR_SCHEMES.keys()).index(DEFAULT_COLOR_SCHEME),
            help="Warm (gray → red) is the original palette. Colorblind-safe "
                 "(viridis) is a perceptually-uniform alternative for red-green "
                 "color vision deficiency, applied to all five views.",
        )
        mpl_cmap = COLOR_SCHEMES[scheme_name]

    return threshold, surf_mesh, mpl_cmap

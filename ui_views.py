"""View-mode selector, per-mode guide, subcortical warning, and the main
render dispatch across the 5 view modes.
"""
import streamlit as st

from brain_regions import SUBCORTICAL_REGIONS
from config import DEFAULT_SIGMA, GUIDES, SURFACE_SIGMA, VIEW_MODE_HELP, VIEW_MODES
from models import RegionEntry
from styles import brain_loader_html
from visualization import (
    create_activation_volume,
    interactive_surface_plotly,
    interactive_volume_html,
    plot_brain_glass,
    plot_brain_stat,
    plot_brain_surface,
)


def render_view_mode_selector() -> str:
    return st.radio(
        "View Mode",
        VIEW_MODES,
        horizontal=True,
        help=VIEW_MODE_HELP,
    )


def render_guide(view_mode: str):
    with st.expander(f"How to read the {view_mode} view", expanded=False):
        st.markdown(GUIDES[view_mode])


def render_subcortical_warning(regions: list[RegionEntry], view_mode: str):
    """Warn instead of silently rendering a blank cortex: cortical-surface
    views can't show deep/subcortical activation, which would otherwise look
    like "no binding" to the user.
    """
    if not regions or view_mode not in ("Interactive 3D", "3D Surface"):
        return
    selected_names = {r.name for r in regions}
    deep_selected = sorted(selected_names & SUBCORTICAL_REGIONS)
    if not deep_selected:
        return
    deep_list = ", ".join(f"**{name}**" for name in deep_selected)
    verb = "is a deep structure" if len(deep_selected) == 1 else "are deep structures"
    st.warning(
        f"⚠️ {deep_list} {verb} that {'is' if len(deep_selected) == 1 else 'are'} "
        "barely visible on this cortical-surface view. Switch to **Glass Brain** "
        "or **Interactive Slices** to see subcortical activation clearly."
    )


def render_main_view(regions: list[RegionEntry], view_mode: str, threshold: float,
                     surf_mesh: str, mpl_cmap: str = "YlOrRd"):
    """Renders the selected view. Returns the matplotlib Figure behind it for
    the static views (so it can be offered as a PNG download), or None for
    the two HTML/WebGL-based interactive views (nothing static to export).
    """
    pairs = [(r.name, r.normalized_intensity) for r in regions]

    loader = st.empty()
    if view_mode == "Interactive 3D":
        loader.markdown(
            brain_loader_html("Building interactive 3D brain…"), unsafe_allow_html=True
        )
        nifti_img = create_activation_volume(pairs, sigma=SURFACE_SIGMA)
        fig3d = interactive_surface_plotly(nifti_img, threshold=threshold, surf_mesh=surf_mesh,
                                           mpl_cmap=mpl_cmap)
        loader.empty()
        st.caption("🖱️ Drag to rotate · scroll to zoom — gray cortex; affected "
                   "regions ramp gray → red by intensity.")
        st.plotly_chart(fig3d, width="stretch")
        return None
    elif view_mode == "Interactive Slices":
        loader.markdown(
            brain_loader_html("Building interactive slice viewer…"), unsafe_allow_html=True
        )
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        html = interactive_volume_html(nifti_img, threshold=threshold, mpl_cmap=mpl_cmap)
        loader.empty()
        st.caption("🖱️ Click or drag on any panel to move the cross-hair through "
                   "the brain — best for deep / subcortical structures.")
        st.iframe(html, height=560)
        return None
    elif view_mode == "3D Surface":
        loader.markdown(
            brain_loader_html("Rendering 3D surface — this takes ~20 seconds…"),
            unsafe_allow_html=True,
        )
        nifti_img = create_activation_volume(pairs, sigma=SURFACE_SIGMA)
        fig = plot_brain_surface(nifti_img, surf_mesh=surf_mesh, threshold=threshold,
                                 mpl_cmap=mpl_cmap)
    elif view_mode == "Glass Brain":
        loader.markdown(brain_loader_html("Rendering glass brain…"), unsafe_allow_html=True)
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        fig = plot_brain_glass(nifti_img, threshold=threshold, mpl_cmap=mpl_cmap)
    else:  # Stat Map (Slices)
        loader.markdown(
            brain_loader_html("Rendering anatomical slices…"), unsafe_allow_html=True
        )
        nifti_img = create_activation_volume(pairs, sigma=DEFAULT_SIGMA)
        fig = plot_brain_stat(nifti_img, threshold=threshold, mpl_cmap=mpl_cmap)

    loader.empty()
    st.pyplot(fig)
    return fig

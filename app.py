import matplotlib.pyplot as plt
import streamlit as st

from interpretation import (
    render_affinity_summary,
    render_connectome_propagation,
    render_export_buttons,
    render_interpretation,
    render_methods_panel,
    render_spatial_test,
)
from state import get_regions, init_state
from styles import inject_theme, render_hero_header
from ui_ai import render_ai_interpretation, render_ai_sidebar_config
from ui_sidebar import render_sidebar
from ui_views import (
    render_guide,
    render_main_view,
    render_subcortical_warning,
    render_view_mode_selector,
)

st.set_page_config(
    page_title="Neuro-Target Affinity Visualizer · v2",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
render_hero_header()
init_state()

threshold, surf_mesh, mpl_cmap, receptor_weight = render_sidebar()
ai_config = render_ai_sidebar_config()

view_mode = render_view_mode_selector()
render_guide(view_mode)

regions = get_regions()
render_subcortical_warning(regions, view_mode)

if regions:
    fig = render_main_view(regions, view_mode, threshold, surf_mesh, mpl_cmap, receptor_weight)
    render_affinity_summary(regions)
    render_interpretation(regions)
    render_connectome_propagation(regions)
    render_spatial_test(regions, receptor_weight)
    render_ai_interpretation(regions, ai_config, receptor_weight)
    render_methods_panel(threshold, surf_mesh, mpl_cmap, receptor_weight)
    render_export_buttons(fig, regions, threshold, surf_mesh, mpl_cmap, receptor_weight)
    if fig is not None:
        plt.close(fig)
else:
    st.info("Add brain regions from the sidebar to begin visualization.")

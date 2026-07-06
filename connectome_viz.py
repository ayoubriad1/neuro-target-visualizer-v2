"""Animated network view for the circuit-propagation diffusion
(connectome.simulate_diffusion): one node per atlas region at its real MNI
centroid, connected by real functional-connectivity edges, with node
size/color animating through each diffusion step via Plotly frames.

Deliberately a *network graph in brain space*, not another anatomical brain
render - a cool blue/purple palette (vs. the warm red used everywhere else
for directly-entered/measured affinity) and a distinct node shape for the
directly-selected "source" region(s) keep this visually unmistakable as a
different kind of view: an estimated propagation model, not a measurement.
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from connectome import region_centroids, simulate_diffusion
from models import RegionEntry

_EDGE_THRESHOLD = 0.3
_NODE_BASE_SIZE = 8.0
_NODE_MAX_SIZE = 40.0
_COOL_COLORSCALE = [
    [0.0, "#2B2A3D"],   # inactive -> dark neutral (reads on the light page bg via marker fill)
    [0.15, "#3A4E8C"],
    [0.45, "#4C7EBF"],
    [0.75, "#63B7C9"],
    [1.0, "#8FE3D0"],   # peak -> cool teal/mint, deliberately not the warm red used for affinity
]
# Static translucent backdrop only - same pial mesh/style as the "Interactive
# 3D" view, so this animation reads as "the real brain" rather than an
# abstract diagram, but pale and see-through enough that the animated nodes
# (the actual point of this view) stay the visual focus.
_BRAIN_SHELL_COLOR = "#dcdce4"
_BRAIN_SHELL_OPACITY = 0.12


@st.cache_data(show_spinner=False)
def _brain_shell() -> go.Mesh3d:
    """A static, pale, translucent pial-cortex mesh - reusing the exact same
    fsaverage5 mesh/coordinate pipeline as the "Interactive 3D" view - purely
    for anatomical context, so the animated network below reads as sitting
    inside a real brain rather than floating in empty space. No per-vertex
    coloring, no per-frame updates: it never changes across animation steps.
    """
    from nilearn import surface

    from visualization import _coords_faces, _load_fsaverage

    fs = _load_fsaverage("fsaverage5")
    c_left, f_left = _coords_faces(surface.load_surf_mesh(fs.pial_left))
    c_right, f_right = _coords_faces(surface.load_surf_mesh(fs.pial_right))
    coords = np.vstack([c_left, c_right])
    faces = np.vstack([f_left, f_right + len(c_left)])
    return go.Mesh3d(
        x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        color=_BRAIN_SHELL_COLOR, opacity=_BRAIN_SHELL_OPACITY,
        lighting=dict(ambient=0.9, diffuse=0.3, specular=0.0),
        hoverinfo="skip", showlegend=False, name="cortex (context only)",
    )


@st.cache_data(show_spinner=False)
def _edge_trace(_names_key: tuple[str, ...]) -> go.Scatter3d:
    from connectome import _load_matrix  # local import: internal helper, not part of the public API

    matrix = _load_matrix()
    centroids = region_centroids()
    xs: list[float | None] = []
    ys: list[float | None] = []
    zs: list[float | None] = []
    names = list(matrix.index)
    for i, a in enumerate(names):
        if a not in centroids:
            continue
        for b in names[i + 1:]:
            if b not in centroids or matrix.loc[a, b] < _EDGE_THRESHOLD:
                continue
            ax, ay, az = centroids[a]
            bx, by, bz = centroids[b]
            xs += [ax, bx, None]
            ys += [ay, by, None]
            zs += [az, bz, None]
    return go.Scatter3d(
        x=xs, y=ys, z=zs, mode="lines",
        line=dict(color="rgba(150,140,180,0.35)", width=2),
        hoverinfo="skip", showlegend=False, name="connectivity",
    )


def build_propagation_animation(regions: list[RegionEntry], height: int = 560) -> go.Figure | None:
    """Returns a Plotly figure with Play/Pause + a step slider animating the
    diffusion simulation across the region network, or None if there's
    nothing to animate (mirrors connectome.propagate_effect's "no usable
    selected region" case).
    """
    steps = simulate_diffusion(regions)
    centroids = region_centroids()
    names = [n for n in steps[0] if n in centroids]
    if not names or all(v == 0.0 for v in steps[0].values()):
        return None

    selected_names = {r.name for r in regions if r.coordinates is None}
    coords = np.array([centroids[n] for n in names])
    global_max = max(max(step[n] for n in names) for step in steps) or 1.0

    def marker_for(step: dict[str, float]) -> dict:
        values = np.array([step[n] for n in names])
        sizes = _NODE_BASE_SIZE + (_NODE_MAX_SIZE - _NODE_BASE_SIZE) * (values / global_max)
        return dict(
            size=sizes, color=values, cmin=0.0, cmax=global_max,
            colorscale=_COOL_COLORSCALE, showscale=True,
            colorbar=dict(title="Activation", len=0.6, thickness=14),
            # scatter3d.marker.line.width is scalar-only (unlike .color, which
            # accepts a per-point array) - a uniform width with a transparent
            # vs. gold per-point color still renders a highlighted ring only
            # around the directly-selected "source" region(s).
            line=dict(
                color=["#F2B84B" if n in selected_names else "rgba(0,0,0,0)" for n in names],
                width=3,
            ),
        )

    node_trace = go.Scatter3d(
        x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
        mode="markers", text=names, hoverinfo="text",
        marker=marker_for(steps[0]), name="regions",
    )
    edge_trace = _edge_trace(tuple(sorted(names)))
    brain_shell = _brain_shell()

    # Trace order: [0] static brain shell, [1] static edges, [2] animated
    # nodes - frames only touch index 2 (`traces=[2]`), so the brain mesh
    # and the connectivity edges are drawn once and never redrawn per frame.
    fig = go.Figure(data=[brain_shell, edge_trace, node_trace])
    fig.frames = [
        go.Frame(data=[go.Scatter3d(marker=marker_for(step))], traces=[2], name=str(t))
        for t, step in enumerate(steps)
    ]

    ax = dict(showbackground=False, showgrid=False, showticklabels=False, zeroline=False, visible=False)
    fig.update_layout(
        scene=dict(xaxis=ax, yaxis=ax, zaxis=ax, aspectmode="data",
                   camera=dict(eye=dict(x=1.6, y=-1.5, z=0.55))),
        margin=dict(l=0, r=0, t=10, b=0), height=height,
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        updatemenus=[dict(
            type="buttons", direction="left", x=0.0, y=0.0, xanchor="left", yanchor="bottom",
            pad=dict(t=4, r=4),
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, dict(frame=dict(duration=600, redraw=True),
                                      fromcurrent=True, transition=dict(duration=200))]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
            ],
        )],
        sliders=[dict(
            active=0, x=0.15, len=0.85, y=0.0, yanchor="bottom",
            currentvalue=dict(prefix="Step: ", visible=True),
            steps=[
                dict(label=str(t), method="animate",
                     args=[[str(t)], dict(mode="immediate",
                                          frame=dict(duration=0, redraw=True))])
                for t in range(len(steps))
            ],
        )],
    )
    return fig

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

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.frames = [
        go.Frame(data=[edge_trace, go.Scatter3d(marker=marker_for(step))], name=str(t))
        for t, step in enumerate(steps)
    ]

    ax = dict(showbackground=False, showgrid=False, showticklabels=False, zeroline=False, visible=False)
    fig.update_layout(
        scene=dict(xaxis=ax, yaxis=ax, zaxis=ax, aspectmode="data"),
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

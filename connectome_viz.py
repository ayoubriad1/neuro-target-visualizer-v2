"""Animated network view for the circuit-propagation diffusion
(connectome.simulate_diffusion): one node per atlas region at its real MNI
centroid, connected by real functional-connectivity edges, with node
size/color animating through each diffusion step via Plotly frames.

Deliberately a *network graph in brain space*, not another anatomical brain
render - a cool blue/teal palette (vs. the warm red used everywhere else
for directly-entered/measured affinity) and a gold-ringed marker for the
directly-selected "source" region(s) keep this visually unmistakable as a
different kind of view: an estimated propagation model, not a measurement.

On top of the animated nodes, a set of static gold arrows (see
_relation_traces) points from the single strongest directly-selected region
("the main affected region") to every other region it has real,
above-threshold functional connectivity to - so the relationship between the
strongest binding site and the rest of the network reads as directional at a
glance. Functional connectivity itself is symmetric/undirected; "directed"
here means "drawn as emanating from the main region for legibility", not an
anatomical or causal directionality claim.
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from connectome import region_centroids, simulate_diffusion
from models import RegionEntry

_EDGE_THRESHOLD = 0.3
_NODE_BASE_SIZE = 10.0
_NODE_MAX_SIZE = 40.0
_SEED_SIZE = 34.0
_SEED_COLOR = "#F2B84B"  # fixed gold - the seed's own value never meaningfully
                        # animates (the restart term keeps re-injecting it every
                        # step), so it gets a distinct fixed marker instead of
                        # competing for the same color/size scale as the
                        # propagated regions, which is the part that's actually
                        # supposed to be visible animating.
_ARROW_COLOR = _SEED_COLOR  # same gold as the seed marker - visually ties each
                           # arrow back to "this relationship emanates from the
                           # main affected region", not just "these two nodes
                           # are connected" (which the faint purple edges below
                           # already show for the whole network)
_ARROW_TIP_FRACTION = 0.85  # place the cone tip 85% of the way to the target
                           # node, short of its marker, so the arrowhead
                           # doesn't visually disappear inside/behind it
_ARROW_SIZEREF = 6.0
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


def _main_region(regions: list[RegionEntry], matrix) -> str | None:
    """The single strongest directly-selected region that has a connectivity-
    matrix row - the same "top region" idea as
    interpretation._interpretation_text, restricted to regions this network
    view can actually place on the graph. None if no selected region
    qualifies (mirrors connectome.propagate_effect's precondition).
    """
    candidates = [r for r in regions if r.coordinates is None and r.name in matrix.index]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r.normalized_intensity).name


def _relation_traces(
    main_name: str | None, centroids: dict[str, tuple[float, float, float]], matrix,
) -> list[go.Scatter3d | go.Cone]:
    """A directed line + arrowhead (cone) from `main_name` - the main
    affected region - to every other region it has real, above-threshold
    functional connectivity to (same cutoff as the plain connectivity
    edges), so the relationship between the strongest binding site and the
    rest of the network reads as directional at a glance instead of just
    "these nodes are connected".

    Real functional connectivity is symmetric/undirected by construction -
    "directed" here means "drawn as emanating from the main region for
    legibility", not a claim about anatomical or causal directionality.
    Returns an empty list if there's no main region, it has no centroid, or
    none of its connections clear the threshold.
    """
    if main_name is None or main_name not in centroids or main_name not in matrix.index:
        return []
    start = np.array(centroids[main_name])

    xs: list[float | None] = []
    ys: list[float | None] = []
    zs: list[float | None] = []
    cone_x, cone_y, cone_z = [], [], []
    cone_u, cone_v, cone_w = [], [], []
    for other in matrix.columns:
        if other == main_name or other not in centroids:
            continue
        weight = matrix.loc[main_name, other]
        if weight < _EDGE_THRESHOLD:
            continue
        end = np.array(centroids[other])
        vector = end - start
        xs += [start[0], end[0], None]
        ys += [start[1], end[1], None]
        zs += [start[2], end[2], None]
        tip = start + _ARROW_TIP_FRACTION * vector
        direction = vector * (1.0 - _ARROW_TIP_FRACTION)
        cone_x.append(tip[0])
        cone_y.append(tip[1])
        cone_z.append(tip[2])
        cone_u.append(direction[0])
        cone_v.append(direction[1])
        cone_w.append(direction[2])

    if not xs:
        return []

    line_trace = go.Scatter3d(
        x=xs, y=ys, z=zs, mode="lines",
        line=dict(color=_ARROW_COLOR, width=5),
        hoverinfo="skip", showlegend=False, name=f"{main_name} -> connected regions",
    )
    cone_trace = go.Cone(
        x=cone_x, y=cone_y, z=cone_z, u=cone_u, v=cone_v, w=cone_w,
        anchor="tip", sizemode="absolute", sizeref=_ARROW_SIZEREF,
        colorscale=[[0.0, _ARROW_COLOR], [1.0, _ARROW_COLOR]], showscale=False,
        hoverinfo="skip", showlegend=False, name="direction",
    )
    return [line_trace, cone_trace]


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

    # The seed region(s)' own value barely changes across steps (the
    # restart term keeps re-injecting the original input every iteration),
    # so scaling size/color against the *global* max - dominated by the
    # seed sitting near 1.0 - squeezed every propagated region's real
    # variation into a sliver of the visual range, making the animation
    # look frozen. Scaling against the propagated (non-seed) regions' own
    # max instead gives the part that's actually supposed to animate the
    # full visual range; the seed gets a fixed size/is clipped to the top
    # color instead of competing for the same scale.
    propagated_max = max(
        (step[n] for step in steps for n in names if n not in selected_names),
        default=0.0,
    ) or 1e-9

    def marker_for(step: dict[str, float]) -> dict:
        values = np.array([step[n] for n in names])
        ratios = np.clip(values / propagated_max, 0.0, 1.0)
        sizes = _NODE_BASE_SIZE + (_NODE_MAX_SIZE - _NODE_BASE_SIZE) * ratios
        colors = np.clip(values, 0.0, propagated_max)
        for i, n in enumerate(names):
            if n in selected_names:
                sizes[i] = _SEED_SIZE
        return dict(
            size=sizes, color=colors, cmin=0.0, cmax=propagated_max,
            colorscale=_COOL_COLORSCALE, showscale=True,
            colorbar=dict(title="Propagated<br>activation", len=0.6, thickness=14),
            # scatter3d.marker.line.width is scalar-only (unlike .color, which
            # accepts a per-point array) - a uniform width with a transparent
            # vs. gold per-point color still renders a highlighted ring only
            # around the directly-selected "source" region(s).
            line=dict(
                color=[_SEED_COLOR if n in selected_names else "rgba(0,0,0,0)" for n in names],
                width=4,
            ),
        )

    node_trace = go.Scatter3d(
        x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
        mode="markers", text=names, hoverinfo="text",
        marker=marker_for(steps[0]), name="regions",
    )
    edge_trace = _edge_trace(tuple(sorted(names)))
    brain_shell = _brain_shell()

    from connectome import _load_matrix  # local import: internal helper, not part of the public API
    matrix = _load_matrix()
    main_name = _main_region(regions, matrix)
    relation_traces = _relation_traces(main_name, centroids, matrix)

    # Trace order: [0] static brain shell, [1] static edges, [2] animated
    # nodes, [3+] static directed arrows from the main region (only present
    # when it has at least one above-threshold connection) - frames only
    # touch index 2 (`traces=[2]`), so the brain mesh, connectivity edges and
    # arrows are drawn once and never redrawn per frame.
    fig = go.Figure(data=[brain_shell, edge_trace, node_trace, *relation_traces])
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
                     args=[None, dict(frame=dict(duration=1000, redraw=True),
                                      fromcurrent=True, transition=dict(duration=500, easing="linear"))]),
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

import io
import numpy as np
import nibabel as nib
from nilearn import plotting
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from brain_regions import get_coordinates

MNI_SHAPE = (91, 109, 91)
MNI_AFFINE = np.array([
    [2., 0., 0., -90.],
    [0., 2., 0., -126.],
    [0., 0., 2., -72.],
    [0., 0., 0., 1.],
])


def _mni_to_voxel(x, y, z):
    coord = np.array([x, y, z, 1.0])
    inv_affine = np.linalg.inv(MNI_AFFINE)
    voxel = inv_affine.dot(coord)[:3]
    return np.round(voxel).astype(int)


def create_activation_volume(regions_and_scores, sigma=6.0):
    volume = np.zeros(MNI_SHAPE, dtype=np.float64)
    sigma_vox = sigma / 2.0
    ii, jj, kk = np.mgrid[0:MNI_SHAPE[0], 0:MNI_SHAPE[1], 0:MNI_SHAPE[2]]

    for name, score in regions_and_scores:
        if score <= 0:
            continue
        x, y, z = get_coordinates(name)
        vi, vj, vk = _mni_to_voxel(x, y, z)
        amplitude = score / 100.0
        dist_sq = (ii - vi)**2 + (jj - vj)**2 + (kk - vk)**2
        gaussian = amplitude * np.exp(-dist_sq / (2 * sigma_vox**2))
        volume += gaussian

    volume = np.clip(volume, 0, 1)
    return nib.Nifti1Image(volume, MNI_AFFINE)


# 3D Surface - multi-angle montage of the light folded-cortex model
def plot_brain_surface(nifti_img, surf_mesh="fsaverage6", threshold=0.05):
    """
    Static "paper-style" figure built from the same light, folded-cortex 3D model
    as the Interactive 3D view: the model is captured from four fixed viewpoints
    (left, right, top, front) and composited into a 2x2 panel with a shared
    colorbar. The cortex is light with a gray-to-red heat map - no harsh
    black/white curvature.

    `surf_mesh` sets cortical resolution; `threshold` hides faint activation.
    """
    import plotly.io as pio

    base = interactive_surface_plotly(nifti_img, threshold=threshold,
                                      surf_mesh=surf_mesh, colorbar=False)
    views = [
        ("Left lateral",      dict(x=-1.9, y=-0.6, z=0.40)),
        ("Right lateral",     dict(x=1.9,  y=-0.6, z=0.40)),
        ("Top (dorsal)",      dict(x=0.0,  y=-0.2, z=2.20)),
        ("Front (anterior)",  dict(x=0.0,  y=2.10, z=0.35)),
    ]
    panels = []
    for label, eye in views:
        base.update_layout(scene=dict(camera=dict(eye=eye)))
        png = pio.to_image(base, format="png", width=620, height=520, scale=1.3)
        panels.append((mpimg.imread(io.BytesIO(png)), label))

    fig = plt.figure(figsize=(14, 12), facecolor="white")
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1.0, 1.0, 0.06],
                  wspace=0.02, hspace=0.10)
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for (img, label), (r, c) in zip(panels, positions):
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(img, interpolation="lanczos")
        ax.axis("off")
        ax.set_title(label, fontsize=12, fontweight="bold", pad=4)

    cax = fig.add_subplot(gs[:, 2])
    cb = plt.colorbar(
        cm.ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap="YlOrRd"),
        cax=cax, orientation="vertical",
    )
    cb.set_label("Binding Intensity", fontsize=10, labelpad=10)
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cb.set_ticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"])
    cb.ax.tick_params(labelsize=8)

    fig.suptitle("Brain Region Affinity Map", fontsize=16, fontweight="bold", y=0.97)
    return fig


# Helper: render ONE glass-brain projection to a high-resolution PNG buffer
def _glass_panel(nifti_img, mode, dpi=200, threshold=0.08):
    display = plotting.plot_glass_brain(
        nifti_img,
        display_mode=mode,
        colorbar=False,
        cmap="YlOrRd",
        vmax=1.0,
        vmin=0.0,
        threshold=threshold,   # keep the projection clean (no pale-yellow wash)
        plot_abs=False,
        alpha=0.95,
    )
    fig = display.frame_axes.figure
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return mpimg.imread(buf)


# Glass Brain - 2x2 grid of LARGE, high-detail X-ray projections
def plot_brain_glass(nifti_img, threshold=0.08):
    """
    Four full-depth X-ray projections arranged in a 2x2 grid (instead of one
    thin row), so each panel is large and high-detail:

        Top-left: Left Sagittal      Top-right: Right Sagittal
        Bottom-left: Axial (Top)     Bottom-right: Coronal (Front)

    Each panel is a full projection through the brain, so deep subcortical
    activation is always visible regardless of depth.
    """
    panels = [
        ("l", "Left Sagittal",      "anterior ◄ | ► posterior"),
        ("r", "Right Sagittal",     "anterior ◄ | ► posterior"),
        ("z", "Axial — Top-down",   "left ◄ | ► right"),
        ("y", "Coronal — Front",    "left ◄ | ► right"),
    ]
    rendered = [
        (_glass_panel(nifti_img, mode, dpi=200, threshold=threshold), title, sub)
        for mode, title, sub in panels
    ]

    fig = plt.figure(figsize=(15, 12), facecolor="white")
    gs = GridSpec(
        2, 3, figure=fig,
        width_ratios=[1.0, 1.0, 0.06],
        wspace=0.04, hspace=0.16,
    )
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for (img, title, sub), (r, c) in zip(rendered, positions):
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(img, interpolation="lanczos")
        ax.axis("off")
        ax.set_title(f"{title}\n{sub}", fontsize=11.5, fontweight="bold",
                     pad=6, linespacing=1.5)

    # Shared vertical colorbar spanning both rows
    cax = fig.add_subplot(gs[:, 2])
    cb = plt.colorbar(
        cm.ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap="YlOrRd"),
        cax=cax, orientation="vertical",
    )
    cb.set_label("Binding Intensity", fontsize=10, labelpad=10)
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cb.set_ticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"])
    cb.ax.tick_params(labelsize=8)

    fig.suptitle(
        "Brain Region Affinity Map — Glass Brain  (X-ray Projections)",
        fontsize=15, fontweight="bold", y=0.965,
    )
    return fig


# Stat Map (Slices) - axial strip + orthogonal cross-sections at peak
def plot_brain_stat(nifti_img, threshold=0.08):
    """
    Two-row layout:
      Row 1 — 6 axial slices (horizontal cuts, top to bottom through the brain)
      Row 2 — 3 orthogonal cross-sections (sagittal / coronal / axial)
               placed at the coordinates of peak activation

    Use this mode to inspect deep subcortical structures that may not appear
    on the cortical surface rendering above.
    """
    # Find peak activation coordinate for orthogonal cut placement
    try:
        cut_xyz = plotting.find_xyz_cut_coords(nifti_img, activation_threshold=0.05)
    except Exception:
        cut_xyz = (0, 0, 0)

    # A threshold keeps only meaningful activation, so faint sub-threshold
    # voxels are transparent instead of rendering as dark/black specks.
    # YlOrRd (pale-yellow -> deep-red) reads cleanly on the light template and
    # never goes black, unlike the previous "hot" map.
    stat_kw = dict(
        cmap="YlOrRd",
        vmin=0.0,
        vmax=1.0,
        threshold=threshold,
        black_bg=False,
        symmetric_cbar=False,
        dim=-0.15,          # brighten the anatomical background a touch
    )

    # Row 1: 8 axial slices
    disp_axial = plotting.plot_stat_map(
        nifti_img,
        display_mode="z",
        cut_coords=8,
        colorbar=True,
        title="Axial Slices  (horizontal cuts, inferior → superior)",
        **stat_kw,
    )
    fig_axial = disp_axial.frame_axes.figure
    fig_axial.set_size_inches(18, 4.5)

    # Row 2: orthogonal views at peak
    xyz_label = f"x={cut_xyz[0]:.0f}  y={cut_xyz[1]:.0f}  z={cut_xyz[2]:.0f} mm"
    disp_ortho = plotting.plot_stat_map(
        nifti_img,
        display_mode="ortho",
        cut_coords=cut_xyz,
        colorbar=True,
        title=f"Orthogonal Cross-Sections at Peak Activation  [{xyz_label}]",
        **stat_kw,
    )
    fig_ortho = disp_ortho.frame_axes.figure
    fig_ortho.set_size_inches(18, 5)

    # Combine both rows into one figure via image buffers
    def _to_img(f, dpi=190):
        buf = io.BytesIO()
        f.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                  facecolor="white", edgecolor="none")
        plt.close(f)
        buf.seek(0)
        return mpimg.imread(buf)

    img_axial = _to_img(fig_axial)
    img_ortho = _to_img(fig_ortho)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(16, 9), facecolor="white",
        gridspec_kw={"hspace": 0.12},
    )

    ax1.imshow(img_axial, interpolation="lanczos")
    ax1.axis("off")
    ax1.set_title(
        "Axial Slices  —  horizontal cuts through the brain (top to bottom)",
        fontsize=10, fontweight="bold", pad=4,
    )

    ax2.imshow(img_ortho, interpolation="lanczos")
    ax2.axis("off")
    ax2.set_title(
        f"Orthogonal Cross-Sections at Peak Activation  [{xyz_label}]",
        fontsize=10, fontweight="bold", pad=4,
    )

    fig.suptitle(
        "Brain Region Affinity Map — Anatomical Slices",
        fontsize=14, fontweight="bold", y=1.01,
    )
    return fig


# Interactive viewers (WebGL) - return standalone HTML for embedding in Streamlit
def interactive_surface_html(nifti_img, surf_mesh="fsaverage6", threshold=0.08,
                             height=640, width=1000):
    """
    Rotatable 3-D cortical surface. The affinity map is painted onto the cortex
    and the user can drag to rotate, scroll to zoom. Returns an HTML iframe
    string suitable for streamlit.components.v1.html().
    """
    view = plotting.view_img_on_surf(
        nifti_img,
        surf_mesh=surf_mesh,
        threshold=threshold,
        cmap="YlOrRd",
        symmetric_cmap=False,
        vmax=1.0,
        colorbar=True,
        title="Region Affinity — interactive 3D surface",
    )
    return view.get_iframe(width=width, height=height)


def interactive_volume_html(nifti_img, threshold=0.08, height=540, width=1000):
    """
    Interactive volume viewer (brainsprite): three synchronized planes with a
    movable cross-hair — good for deep / subcortical structures. Returns an HTML
    iframe string suitable for streamlit.components.v1.html().
    """
    view = plotting.view_img(
        nifti_img,
        threshold=threshold,
        cmap="YlOrRd",
        symmetric_cmap=False,
        vmax=1.0,
        black_bg=False,
        colorbar=True,
        title="Region Affinity — interactive slices",
    )
    return view.get_iframe(width=width, height=height)


# Gray -> red colorscale: the cortex stays neutral gray, and activation ramps
# gray -> pale-yellow -> orange -> deep-red with intensity.
_GRAY_RED = [
    [0.000, "#9aa0a6"],   # no activation -> neutral gray
    [0.001, "#9aa0a6"],
    [0.150, "#ffe49c"],   # pale yellow
    [0.400, "#ff9d3a"],   # orange
    [0.700, "#f24420"],   # red
    [1.000, "#b40426"],   # deep red
]


def _coords_faces(mesh):
    """Return (coords, faces) from any nilearn surf-mesh form (tuple / Mesh / InMemoryMesh)."""
    import numpy as np
    if hasattr(mesh, "coordinates"):
        return np.asarray(mesh.coordinates, dtype=float), np.asarray(mesh.faces)
    return np.asarray(mesh[0], dtype=float), np.asarray(mesh[1])


def interactive_surface_plotly(nifti_img, threshold=0.08, surf_mesh="fsaverage6",
                               height=680, colorbar=True):
    """
    Fully rotatable, **anatomically folded** 3-D brain (Plotly Mesh3d) rendered on
    the *pial* surface, so the real gyri and sulci (ridges/folds) are visible —
    not the smoothed inflated balloon. The cortex is shaded gray by curvature
    (gyri light, sulci dark), and affected regions ramp gray → yellow → orange →
    red by binding intensity. Returns a Plotly Figure for st.plotly_chart().

    `surf_mesh` controls fold detail: fsaverage5 (coarse) < fsaverage6 (default) <
    fsaverage (finest, heaviest).
    """
    import numpy as np
    import plotly.graph_objects as go
    from matplotlib.colors import LinearSegmentedColormap
    from nilearn import datasets, surface

    fs = datasets.fetch_surf_fsaverage(surf_mesh)

    # DISPLAY on the folded PIAL surface (real gyri/sulci) and sample there too.
    cL, fL = _coords_faces(surface.load_surf_mesh(fs.pial_left))
    cR, fR = _coords_faces(surface.load_surf_mesh(fs.pial_right))
    tex_l = np.ravel(surface.vol_to_surf(nifti_img, fs.pial_left))
    tex_r = np.ravel(surface.vol_to_surf(nifti_img, fs.pial_right))

    # Pial hemispheres are already in true anatomical position -> no offset needed.
    coords = np.vstack([cL, cR])
    faces = np.vstack([fL, fR + len(cL)])
    inten = np.clip(np.concatenate([tex_l, tex_r]), 0.0, 1.0)

    # Curvature (sulcal depth) -> gray base: gyri light, sulci dark -> folds pop.
    try:
        sulc = np.concatenate([
            np.ravel(surface.load_surf_data(fs.sulc_left)),
            np.ravel(surface.load_surf_data(fs.sulc_right)),
        ]).astype(float)
        s = sulc - sulc.min()
        s = s / (s.max() + 1e-9)
    except Exception:
        s = np.full(len(coords), 0.5)
    # Light/white brain (like the v1 static surface): near-white gyri, light-gray
    # sulci - enough contrast to read the folds, but the cortex stays bright.
    light_gray = np.array([242.0, 243.0, 245.0])   # gyri  -> near white
    dark_gray = np.array([176.0, 180.0, 186.0])    # sulci -> light gray (not dark)
    colors = light_gray * (1.0 - s[:, None]) + dark_gray * s[:, None]   # (N,3)

    # Warm ramp for activated vertices (>= threshold), blended over the gray base.
    warm = LinearSegmentedColormap.from_list(
        "grr", ["#ffe49c", "#ff9d3a", "#f24420", "#b40426"])
    mask = inten >= threshold
    if mask.any():
        colors[mask] = np.array([warm(float(v))[:3] for v in inten[mask]]) * 255.0
    vertexcolor = np.clip(colors, 0, 255).astype(np.uint8)

    mesh3d = go.Mesh3d(
        x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        vertexcolor=vertexcolor,
        lighting=dict(ambient=0.78, diffuse=0.55, specular=0.05, roughness=1.0,
                      fresnel=0.05),
        lightposition=dict(x=100, y=150, z=320),
        flatshading=False, hoverinfo="skip", name="cortex",
    )

    data = [mesh3d]
    if colorbar:
        # Hidden marker trace purely to render the gray->red colorbar.
        data.append(go.Scatter3d(
            x=[coords[0, 0]], y=[coords[0, 1]], z=[coords[0, 2]], mode="markers",
            marker=dict(size=0.1, color=[0.0], cmin=0.0, cmax=1.0,
                        colorscale=_GRAY_RED, showscale=True,
                        colorbar=dict(title="Intensity", len=0.6, thickness=14,
                                      tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                                      ticktext=["0 %", "25 %", "50 %", "75 %", "100 %"])),
            hoverinfo="skip", showlegend=False,
        ))

    fig = go.Figure(data)
    _ax = dict(showbackground=False, showgrid=False, showticklabels=False,
               zeroline=False, visible=False)
    fig.update_layout(
        scene=dict(xaxis=_ax, yaxis=_ax, zaxis=_ax, aspectmode="data",
                   camera=dict(eye=dict(x=1.6, y=-1.5, z=0.55))),
        margin=dict(l=0, r=0, t=0, b=0), height=height,
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
    )
    return fig

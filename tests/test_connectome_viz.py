import pytest

from connectome import region_centroids
from connectome_viz import build_propagation_animation
from models import make_region_entry


def test_build_propagation_animation_returns_none_for_empty_regions():
    assert build_propagation_animation([]) is None


def test_build_propagation_animation_returns_none_for_coordinates_only():
    regions = [make_region_entry("Custom (0, 0, 0)", -9.0, coordinates=(0.0, 0.0, 0.0))]
    assert build_propagation_animation(regions) is None


def test_build_propagation_animation_has_one_frame_per_diffusion_step():
    regions = [make_region_entry("Striatum (Putamen)", -12.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    assert len(fig.frames) == 5  # step 0 (raw input) + 4 diffusion iterations
    # brain shell + edges trace + nodes trace, plus 2 more (line + cone arrow
    # traces) whenever the main region has an above-threshold connection -
    # see the dedicated arrow tests below.
    assert len(fig.data) in (3, 5)


def test_build_propagation_animation_includes_brain_shell_for_context():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    assert fig.data[0].type == "mesh3d"
    assert fig.data[0].opacity < 0.3  # translucent backdrop, not the visual focus


def test_build_propagation_animation_frames_only_touch_node_trace():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    for frame in fig.frames:
        assert frame.traces == (2,)


def test_build_propagation_animation_node_trace_covers_every_region():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    node_trace = fig.data[2]
    assert len(node_trace.x) == 28


def test_build_propagation_animation_highlights_selected_region():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    node_trace = fig.data[2]
    names = list(node_trace.text)
    thalamus_idx = names.index("Thalamus")
    assert node_trace.marker.line.color[thalamus_idx] != "rgba(0,0,0,0)"
    other_idx = 0 if thalamus_idx != 0 else 1
    assert node_trace.marker.line.color[other_idx] == "rgba(0,0,0,0)"


def test_build_propagation_animation_frame_marker_sizes_bounded():
    regions = [make_region_entry("Striatum (Putamen)", -15.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    for frame in fig.frames:
        sizes = frame.data[0].marker.size
        assert all(8.0 <= s <= 40.0 + 1e-9 for s in sizes)


def test_build_propagation_animation_draws_arrows_from_main_region():
    # Striatum (Putamen) is a real hub region - expected to clear the 0.3
    # connectivity threshold with at least one other atlas region.
    regions = [make_region_entry("Striatum (Putamen)", -12.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    assert len(fig.data) == 5
    line_trace, cone_trace = fig.data[3], fig.data[4]
    assert line_trace.type == "scatter3d"
    assert line_trace.mode == "lines"
    assert cone_trace.type == "cone"
    # The line starts at the main region's own centroid every segment.
    centroid = region_centroids()["Striatum (Putamen)"]
    assert line_trace.x[0] == pytest.approx(centroid[0])
    assert line_trace.y[0] == pytest.approx(centroid[1])
    assert line_trace.z[0] == pytest.approx(centroid[2])


def test_build_propagation_animation_arrows_pick_the_strongest_selected_region():
    # Two selected regions - the arrows must emanate from the stronger one
    # (Striatum (Putamen), -14.0) and not the weaker one (Thalamus, -2.0).
    regions = [
        make_region_entry("Thalamus", -2.0),
        make_region_entry("Striatum (Putamen)", -14.0),
    ]
    fig = build_propagation_animation(regions)
    assert fig is not None
    line_trace = fig.data[3]
    centroid = region_centroids()["Striatum (Putamen)"]
    assert line_trace.x[0] == pytest.approx(centroid[0])
    assert line_trace.y[0] == pytest.approx(centroid[1])
    assert line_trace.z[0] == pytest.approx(centroid[2])


def test_build_propagation_animation_arrow_traces_not_touched_by_frames():
    regions = [make_region_entry("Striatum (Putamen)", -12.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    for frame in fig.frames:
        assert frame.traces == (2,)

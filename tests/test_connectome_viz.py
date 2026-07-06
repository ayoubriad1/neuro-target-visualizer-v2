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
    assert len(fig.frames) == 9  # step 0 (raw input) + 8 diffusion iterations
    assert len(fig.data) == 2  # edges trace + nodes trace


def test_build_propagation_animation_node_trace_covers_every_region():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    node_trace = fig.data[1]
    assert len(node_trace.x) == 28


def test_build_propagation_animation_highlights_selected_region():
    regions = [make_region_entry("Thalamus", -9.0)]
    fig = build_propagation_animation(regions)
    assert fig is not None
    node_trace = fig.data[1]
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
        sizes = frame.data[1].marker.size
        assert all(8.0 <= s <= 40.0 + 1e-9 for s in sizes)

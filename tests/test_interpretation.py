from interpretation import build_report_markdown
from models import make_region_entry


def test_build_report_markdown_contains_key_sections():
    regions = [make_region_entry("Thalamus", -9.2), make_region_entry("Habenula", -4.0)]
    report = build_report_markdown(regions, threshold=0.08, surf_mesh="fsaverage6",
                                   mpl_cmap="YlOrRd")
    assert "# Neuro-Target Affinity Visualizer" in report
    assert "## Binding Affinity Summary" in report
    assert "## Interpretation" in report
    assert "## Methods & Provenance" in report
    assert "Thalamus" in report
    assert "Habenula" in report
    assert "-9.2" in report


def test_build_report_markdown_single_region_no_runner_up():
    regions = [make_region_entry("Hippocampus", -7.0)]
    report = build_report_markdown(regions, threshold=0.08, surf_mesh="fsaverage6")
    assert "next strongest site" not in report


def test_build_report_markdown_notes_receptor_weighting_when_active():
    regions = [make_region_entry("Thalamus", -9.2)]
    report = build_report_markdown(regions, threshold=0.08, surf_mesh="fsaverage6",
                                   receptor_weight="D2 (dopamine receptor)")
    assert "Receptor density weighting" in report
    assert "D2 (dopamine receptor)" in report
    assert "Jaworska et al. 2020" in report


def test_build_report_markdown_no_receptor_note_by_default():
    regions = [make_region_entry("Thalamus", -9.2)]
    report = build_report_markdown(regions, threshold=0.08, surf_mesh="fsaverage6")
    assert "Receptor density weighting" not in report

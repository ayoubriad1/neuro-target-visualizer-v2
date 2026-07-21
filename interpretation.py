"""Renders the result-side panels: the per-region affinity summary cards,
the plain-language interpretation, and the Methods & provenance expander.
Also builds a plain-markdown version of the same content for the
downloadable report (see build_report_markdown).
"""
import datetime
import io
import sys

import streamlit as st

from atlas_regions import ATLAS_CITATIONS, ATLAS_REGIONS, get_atlas_source
from brain_regions import get_region_names
from config import DEFAULT_SIGMA, KCAL_MAX, KCAL_MIN, SURFACE_SIGMA
from models import RegionEntry, strength_label
from receptor_atlas import HANSEN_2022_CITATION, get_receptor_citation


def render_affinity_summary(regions: list[RegionEntry]):
    st.subheader("Binding Affinity Summary")
    st.caption(
        "Normalized binding intensity per region — 0 % (weak) → 100 % (very strong)."
    )

    rows = []
    for region in regions:
        label, color, text_color = strength_label(region.normalized_intensity)
        rows.append(
            '<div class="aff-card">'
            '<div class="aff-head">'
            f'<span class="aff-name">{region.name}</span>'
            '<span class="aff-meta">'
            f'<span class="aff-kcal">{region.kcal:.1f} kcal/mol</span>'
            f'<span class="aff-tag" style="background:{color};color:{text_color}">{label}</span>'
            '</span>'
            '</div>'
            '<div class="aff-bar-row">'
            f'<div class="aff-track"><div class="aff-fill" style="width:{region.normalized_intensity:.0f}%"></div></div>'
            f'<span class="aff-pct">{region.normalized_intensity:.0f}%</span>'
            '</div>'
            '</div>'
        )
    st.markdown(f'<div class="aff-wrap">{"".join(rows)}</div>', unsafe_allow_html=True)


def _affinity_summary_markdown_table(regions: list[RegionEntry]) -> str:
    """Plain markdown table version of the affinity summary, for the
    downloadable text report (the on-screen version uses styled HTML cards
    that wouldn't render outside the app).
    """
    lines = [
        "| Region | Affinity (kcal/mol) | Normalized intensity | Strength |",
        "|---|---|---|---|",
    ]
    for r in regions:
        label, _color, _text_color = strength_label(r.normalized_intensity)
        lines.append(f"| {r.name} | {r.kcal:.1f} | {r.normalized_intensity:.0f}% | {label} |")
    return "\n".join(lines)


def _interpretation_text(regions: list[RegionEntry]) -> str:
    ranked = sorted(regions, key=lambda r: r.normalized_intensity, reverse=True)
    n = len(ranked)
    top = ranked[0]
    n_strong = sum(1 for r in ranked if r.normalized_intensity >= 50)
    n_moderate = sum(1 for r in ranked if 25 <= r.normalized_intensity < 50)
    n_weak = sum(1 for r in ranked if r.normalized_intensity < 25)
    mean_kcal = sum(r.kcal for r in ranked) / n
    region_word = "region" if n == 1 else "regions"

    if n > 1:
        runner_up = ranked[1].name
        secondary = (
            f" The next strongest site is **{runner_up}**, and the mean affinity "
            f"across the selection is **{mean_kcal:.1f} kcal/mol**."
        )
    else:
        secondary = ""

    return f"""
Across the **{n}** selected {region_word}, **{top.name}** shows the strongest
predicted binding affinity at **{top.kcal:.1f} kcal/mol** (≈ {top.normalized_intensity:.0f} %
normalized intensity) — the most likely engagement site in this map.{secondary}

**Strength distribution:** {n_strong} strong–to–very-strong (≥ 50 %),
{n_moderate} moderate (25–50 %), and {n_weak} weak (< 25 %).

**How to read these results** — affinity is reported in **kcal/mol**, where a
*more negative* value means *stronger, more favourable* binding. Values are
normalized to the −1 kcal/mol (weak) → −15 kcal/mol (very strong) range that
drives the colour scale, so the percentages and the warm colours on the maps
track the same quantity. The renderings show **where** a target is predicted to
engage across cortical and subcortical structures and their **relative**
strength — they indicate predicted localization, not measured receptor
occupancy or in-vivo concentration.
"""


def render_interpretation(regions: list[RegionEntry]):
    st.divider()
    st.subheader("Interpretation")
    st.markdown(_interpretation_text(regions))


def _renderer_versions() -> str:
    try:
        import matplotlib as _mpl
        import nilearn as _nl
        import numpy as _np
        return f"nilearn {_nl.__version__} · matplotlib {_mpl.__version__} · numpy {_np.__version__}"
    except Exception:
        return "n/a"


def _receptor_weighting_note(receptor_weight: str | None) -> str:
    if receptor_weight is None:
        return ""
    citation = get_receptor_citation(receptor_weight)
    return f"""
**Receptor density weighting** — this map is additionally weighted by the
real, published PET-derived density of **{receptor_weight}** across the
brain (not a simulation): the raw affinity volume above is multiplied
voxel-by-voxel by this density (renormalized so the peak stays at 100 %), so
regions with the same nominal affinity can appear stronger or weaker
depending on how much of the target receptor/transporter is actually there.
Source: {citation}. Compiled via {HANSEN_2022_CITATION}. This is a
**structural** density map — real receptor availability, not a guarantee of
functional effect."""


def _methods_text(threshold: float, surf_mesh: str, mpl_cmap: str = "YlOrRd",
                  receptor_weight: str | None = None) -> str:
    all_names = get_region_names()
    n_total = len(all_names)
    n_atlas = len(ATLAS_REGIONS)
    n_illustrative = n_total - n_atlas
    illustrative_names = sorted(set(all_names) - ATLAS_REGIONS)

    # Built dynamically from the actual region/source mapping (rather than a
    # hardcoded list) so this table can't silently go stale the next time a
    # region is added, renamed, or removed.
    by_source: dict[str, list[str]] = {}
    for name in sorted(ATLAS_REGIONS):
        by_source.setdefault(get_atlas_source(name), []).append(name)
    atlas_table = "\n".join(
        f"| {ATLAS_CITATIONS[source]} | {', '.join(names)} |"
        for source, names in sorted(by_source.items())
    )

    if illustrative_names:
        illustrative_note = f"""
The remaining **{n_illustrative} regions** ({", ".join(illustrative_names)})
have no standard, openly-available atlas (small brainstem nuclei, or composite
functional subdivisions spanning multiple atlas labels) and stay as
hand-curated illustrative MNI points, mirrored across the midline — the
sidebar and region picker flag which kind each selected region is."""
    else:
        illustrative_note = """
**All** regions currently offered by this tool are atlas-backed — none are
illustrative points. A small number of structures with no standard,
openly-fetchable atlas (e.g. raphe nuclei, locus coeruleus, cerebellum) were
dropped from the region list entirely rather than kept as unverified data."""

    return f"""
| Item | Value |
|------|-------|
| Tool version | **v2** (enhanced) |
| Coordinate space | MNI152, 2 mm (91×109×91) |
| Region model | {n_atlas}/{n_total} regions on real atlas masks · {n_illustrative} illustrative (MNI point → Gaussian, mirrored across the midline) |
| Activation σ (illustrative regions only) | surface = {SURFACE_SIGMA} mm · glass/stat = {DEFAULT_SIGMA} mm |
| Cortical surface | `{surf_mesh}` · pial |
| Colormap | {mpl_cmap} (0 → 1 normalized intensity) |
| Display threshold | {threshold:.2f} |
| kcal/mol → % | linear over [{KCAL_MIN:.0f}, {KCAL_MAX:.0f}] |
| Renderer | {_renderer_versions()} · Python {sys.version.split()[0]} |
| Generated | {datetime.datetime.now():%Y-%m-%d %H:%M} |

**Data provenance** — affinity values are **user-entered** (`kcal/mol`); this
tool uses **no** external database or measured PET/mRNA map. Of the
{n_total} regions, **{n_atlas} are backed by a real, cited parcellation
atlas** (masks fetched at build/run time, not redrawn by hand):

| Atlas | Regions |
|---|---|
{atlas_table}
{illustrative_note}
{_receptor_weighting_note(receptor_weight)}

See **`ENHANCEMENT_REPORT.md`** for exact citations and the remaining roadmap.
"""


def render_methods_panel(threshold: float, surf_mesh: str, mpl_cmap: str = "YlOrRd",
                         receptor_weight: str | None = None):
    st.divider()
    with st.expander("🔬 Methods & provenance (for reproducibility)", expanded=False):
        st.markdown(_methods_text(threshold, surf_mesh, mpl_cmap, receptor_weight))


def build_report_markdown(regions: list[RegionEntry], threshold: float, surf_mesh: str,
                          mpl_cmap: str = "YlOrRd", receptor_weight: str | None = None) -> str:
    """Self-contained markdown report (affinity table + interpretation +
    methods/provenance) for the "Download report" button in app.py.
    """
    generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# Neuro-Target Affinity Visualizer — Report
Generated {generated}

## Binding Affinity Summary

{_affinity_summary_markdown_table(regions)}

## Interpretation
{_interpretation_text(regions)}

## Methods & Provenance
{_methods_text(threshold, surf_mesh, mpl_cmap, receptor_weight)}
"""


def render_export_buttons(fig, regions: list[RegionEntry], threshold: float, surf_mesh: str,
                          mpl_cmap: str = "YlOrRd", receptor_weight: str | None = None):
    """Download buttons: a high-res PNG of the current static figure (only
    for the 3 matplotlib-based views - the two WebGL/HTML interactive views
    already have their own built-in camera-icon export), and a markdown
    report for every view.
    """
    st.divider()
    col1, col2 = st.columns(2)

    if fig is not None:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
        col1.download_button(
            "🖼️ Download figure (PNG)",
            data=buf.getvalue(),
            file_name="neuroviz_figure.png",
            mime="image/png",
            width="stretch",
        )
    else:
        col1.caption("This interactive view exports via its own camera-icon toolbar button.")

    report = build_report_markdown(regions, threshold, surf_mesh, mpl_cmap, receptor_weight)
    col2.download_button(
        "📄 Download report (Markdown)",
        data=report,
        file_name="neuroviz_report.md",
        mime="text/markdown",
        width="stretch",
    )

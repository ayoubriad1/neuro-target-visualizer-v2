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
from connectome import propagate_effect
from connectome_viz import build_propagation_animation
from models import RegionEntry, strength_label
from receptor_atlas import HANSEN_2022_CITATION, get_receptor_citation
from region_function import FunctionalProfile, get_functional_profile
from spatial_stats import MIN_REGIONS, compute_spatial_correlation


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


def _spatial_test_result(regions: list[RegionEntry], receptor_weight: str | None):
    if receptor_weight is None:
        return None
    return compute_spatial_correlation(tuple(regions), receptor_weight)


def _spatial_test_summary(result) -> str:
    direction = "positive" if result.r > 0 else "negative"
    strength = "strong" if abs(result.r) >= 0.5 else "moderate" if abs(result.r) >= 0.3 else "weak"
    significance = (
        f"statistically distinguishable from a random set of {result.n_regions} atlas "
        f"regions (p = {result.p_value:.3f})"
        if result.p_value < 0.05
        else f"not statistically distinguishable from a random set of {result.n_regions} "
             f"atlas regions (p = {result.p_value:.3f})"
    )
    return f"""
**Spatial correspondence with {result.receptor_name}** — across your
**{result.n_regions}** selected regions with a usable density value, the
correlation between normalized affinity and real receptor density is
**r = {result.r:.2f}** ({strength} {direction} correspondence), which is
{significance} from {result.n_permutations:,} permutations."""


def _spatial_test_methodology(result) -> str:
    return f"""This is a **region-resampling permutation test**, not a
vertex-level "spin test" — the null distribution comes from swapping in
random atlas regions (same count as your selection) for the ones you chose,
not from a spatial-autocorrelation-preserving rotation of a cortical surface
parcellation (which this app's mixed cortical/subcortical region set has no
single unified object for). It answers "is this stronger than a random
same-size set of atlas regions?" — a narrower, still meaningful question.
With only {result.n_regions} data points, treat both r and p as indicative,
not conclusive."""


def render_spatial_test(regions: list[RegionEntry], receptor_weight: str | None):
    """Only renders when receptor weighting is active AND at least
    MIN_REGIONS selected regions have a usable density value - silently
    does nothing otherwise (e.g. too few regions, or weighting disabled),
    rather than show an empty/misleading section.
    """
    result = _spatial_test_result(regions, receptor_weight)
    if result is None:
        return
    st.divider()
    st.subheader("🧪 Spatial correspondence test")
    st.caption(
        f"Only shown when receptor weighting is active and at least "
        f"{MIN_REGIONS} selected regions have a usable density value."
    )
    st.markdown(_spatial_test_summary(result))
    with st.expander("ℹ️ Methodology & caveats", expanded=False):
        st.markdown(_spatial_test_methodology(result))


def _spatial_test_text(regions: list[RegionEntry], receptor_weight: str | None) -> str:
    """Combined summary + methodology, for the downloadable report (which
    has no expander to defer detail into - see render_spatial_test for the
    on-screen split version). Empty string if there's nothing to report."""
    result = _spatial_test_result(regions, receptor_weight)
    if result is None:
        return ""
    return f"{_spatial_test_summary(result)}\n\n*Methodology*: {_spatial_test_methodology(result)}"


def _connectome_table(propagated) -> str:
    rows = "\n".join(f"| {p.name} | {p.score:.0f}% |" for p in propagated)
    return f"""
**Predicted downstream regions** (via real functional connectivity, not
direct binding):

| Region | Propagated effect |
|---|---|
{rows}"""


def _connectome_methodology() -> str:
    return """Each region above is one you did **not** select, ranked by a
connectivity-weighted sum of your selected regions' affinities - real
functional connectivity (see `docs/CONNECTOME_PROPAGATION.md`) times how
strongly you rated the region(s) it connects to, only counting positive
connections. The percentage is relative to the single strongest propagated
region here, **not** on the same scale as the directly-entered affinities
above - this is a simple linear estimate of where an effect might spread
through known circuits, **not** a measured or simulated pharmacokinetic
result. Treat it as a hypothesis-generation aid, not a prediction."""


def _connectome_animation_notes() -> str:
    return """Each node is one atlas region at its real MNI location; the
gold-ringed node(s) are what you selected. **"Step" is an abstract diffusion
iteration, not real elapsed time** - it has no defined relationship to
seconds, minutes, or a real pharmacokinetic timescale. The gold **arrows**
point from your single strongest-affinity region to every other region it
has real, above-threshold functional connectivity to — functional
connectivity is itself symmetric, so "directed" here means *drawn outward
from the main region for legibility*, not a claim about anatomical or
causal direction."""


def _connectome_text(regions: list[RegionEntry]) -> str:
    """Combined table + methodology, for the downloadable report (which has
    no expander to defer detail into - see render_connectome_propagation for
    the on-screen split version). Empty string if there's nothing to report
    (no selected region has a matrix row, or every candidate's propagated
    score is non-positive)."""
    propagated = propagate_effect(regions)
    if not propagated:
        return ""
    return f"{_connectome_table(propagated)}\n\n*Methodology*: {_connectome_methodology()}"


def render_connectome_propagation(regions: list[RegionEntry]):
    """Deliberately its own section, separate from the 3-D brain render
    above - a linear circuit-propagation estimate should never be visually
    blended into the same heatmap as directly-measured/entered affinity, to
    avoid it being mistaken for part of the same measurement.
    """
    propagated = propagate_effect(regions)
    if not propagated:
        return
    st.divider()
    st.subheader("🔗 Circuit propagation (experimental)")
    st.caption(
        "An effect rarely stays confined to where it binds - estimated here "
        "from real (not simulated) functional connectivity."
    )
    st.markdown(_connectome_table(propagated))
    with st.expander("ℹ️ Methodology & caveats", expanded=False):
        st.markdown(_connectome_methodology())

    fig = build_propagation_animation(regions)
    if fig is not None:
        st.caption("🔵 Animated network view — press **▶ Play** or drag the **Step** slider.")
        st.plotly_chart(fig, width="stretch")
        with st.expander("ℹ️ About this animation", expanded=False):
            st.markdown(_connectome_animation_notes())


def _functional_profiled(regions: list[RegionEntry]) -> list[tuple[RegionEntry, FunctionalProfile]]:
    profiled: list[tuple[RegionEntry, FunctionalProfile]] = []
    for r in regions:
        profile = get_functional_profile(r.name)
        if profile is not None:
            profiled.append((r, profile))
    return profiled


def _functional_domain_summary(profiled: list[tuple[RegionEntry, FunctionalProfile]]) -> str:
    domains_touched: dict[str, set[str]] = {}
    for r, p in profiled:
        for domain in p.domains:
            domains_touched.setdefault(domain, set()).add(r.name)
    return "\n".join(
        f"- **{domain}** — via {', '.join(sorted(names))}"
        for domain, names in sorted(domains_touched.items())
    )


def _functional_per_region(profiled: list[tuple[RegionEntry, FunctionalProfile]]) -> str:
    return "\n\n".join(
        f"""**{r.name}** ({', '.join(p.domains)})
{p.description}
- *If stimulated (increased activity)*: {p.stimulation_effect}
- *If inhibited (decreased activity)*: {p.inhibition_effect}
- Source: {p.citation}"""
        for r, p in sorted(profiled, key=lambda rp: rp[0].normalized_intensity, reverse=True)
    )


def _functional_caveat() -> str:
    return """Based on the functional domain(s) associated with your selected
region(s), here is what the literature reports for **increasing** vs.
**decreasing** activity at each site. **These are the classically-reported
associations from lesion studies, direct stimulation mapping, or DBS trials
— not a deterministic prediction of what your specific compound will do**
at that site (that additionally depends on whether it acts as an agonist or
antagonist there, and on dose/exposure). Treat every line as a hypothesis to
weigh, not a guarantee."""


def _functional_interpretation_text(regions: list[RegionEntry]) -> str:
    """Combined caveat + domain summary + per-region detail, for the
    downloadable report (which has no expander to defer detail into - see
    render_functional_interpretation for the on-screen split version).
    Empty string if none of the selected regions have a curated functional
    profile (region_function.py) - e.g. only "Custom (x, y, z)" exact-
    coordinate entries were selected, which have no region name to look up.
    """
    profiled = _functional_profiled(regions)
    if not profiled:
        return ""
    return f"""
{_functional_caveat()}

**Functional domain(s) engaged by your selection:**
{_functional_domain_summary(profiled)}

---

{_functional_per_region(profiled)}
"""


def render_functional_interpretation(regions: list[RegionEntry]):
    """Deliberately separate from render_interpretation (the affinity-based
    summary above) - this translates *which regions* into *what stimulating
    or inhibiting them is classically associated with* at the functional/
    symptomatic level (motor, spatiotemporal, emotional, reward, sensory,
    executive, autonomic), which is a different - and more speculative -
    kind of claim than the measured/entered affinity numbers, so it gets its
    own clearly-labeled section rather than being folded into that one.
    """
    profiled = _functional_profiled(regions)
    if not profiled:
        return
    st.divider()
    st.subheader("🧭 Functional & symptomatic interpretation")
    st.caption(
        "What stimulating/inhibiting each region is classically associated "
        "with. See 🔗 Circuit propagation above for indirect effects."
    )
    st.markdown(
        f"**Functional domain(s) engaged by your selection:**\n"
        f"{_functional_domain_summary(profiled)}\n\n---\n\n{_functional_per_region(profiled)}"
    )
    with st.expander("ℹ️ Methodology & caveats", expanded=False):
        st.markdown(_functional_caveat())


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
    spatial_text = _spatial_test_text(regions, receptor_weight)
    spatial_section = f"\n## Spatial Correspondence Test\n{spatial_text}\n" if spatial_text else ""
    connectome_text = _connectome_text(regions)
    connectome_section = (
        f"\n## Circuit Propagation (experimental)\n{connectome_text}\n" if connectome_text else ""
    )
    functional_text = _functional_interpretation_text(regions)
    functional_section = (
        f"\n## Functional & Symptomatic Interpretation\n{functional_text}\n" if functional_text else ""
    )
    return f"""# Neuro-Target Affinity Visualizer — Report
Generated {generated}

## Binding Affinity Summary

{_affinity_summary_markdown_table(regions)}

## Interpretation
{_interpretation_text(regions)}
{spatial_section}{connectome_section}{functional_section}
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

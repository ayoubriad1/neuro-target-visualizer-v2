"""Sidebar: region picker + active-region list + rendering options.

Long explanations live in each widget's `help=` tooltip (the small "?" icon)
rather than as permanently-visible caption paragraphs, so the sidebar reads
as a short list of controls at a glance - full detail is one hover away,
never removed.
"""
import streamlit as st

from atlas_regions import get_atlas_source, is_atlas_backed
from brain_regions import get_region_names
from config import COLOR_SCHEMES, DEFAULT_COLOR_SCHEME
from docking_import import parse_csv, parse_vina_score
from gene_region import get_gene_citation, suggest_regions
from mni_space import MNI_X_RANGE, MNI_Y_RANGE, MNI_Z_RANGE
from models import strength_label
from rcsb_lookup import fetch_pdb_metadata
from receptor_atlas import HANSEN_2022_CITATION, RECEPTOR_NAMES, get_receptor_citation
from session_io import export_session, import_session
from state import add_region, clear_regions, get_regions, remove_region
from styles import render_sidebar_brain_icon

_INPUT_MODE_NAMED = "Named region (atlas-verified)"
_INPUT_MODE_EXACT = "Exact MNI coordinates (advanced)"
_NO_RECEPTOR_WEIGHT = "None (uniform affinity, current behavior)"
_RECEPTOR_WEIGHT_KEY = "receptor_weight_select"


def _render_docking_import():
    """Optional import section: bulk-add regions from a CSV/TSV of docking
    results, or pull the best score out of a single AutoDock Vina result
    file (.pdbqt output, or its plain-text log) to save retyping it. Both
    are purely convenience/data-entry shortcuts - a Vina score has no
    inherent brain-region association, so the user still has to pick the
    region/receptor it belongs to via the normal controls below.
    """
    with st.expander("📥 Import docking results (optional)", expanded=False):
        st.caption("Bulk-add regions from a file instead of one by one.")

        csv_file = st.file_uploader(
            "CSV / TSV batch", type=["csv", "tsv", "txt"], key="csv_import",
            help=(
                "Required: `region,kcal` columns (`name`/`affinity`/`kcal_mol` "
                "also accepted). Optional: `x,y,z` for exact coordinates; "
                "`pdb_id`/`protein`/`gene`/`ligand` to keep a multi-target x "
                "multi-ligand batch traceable (see 🔎 lookup below)."
            ),
        )
        if csv_file is not None:
            result = parse_csv(csv_file.getvalue().decode("utf-8", errors="replace"))
            if result.rows:
                st.success(f"{len(result.rows)} valid row(s) ready to import.")
                has_metadata = any(r.pdb_id or r.protein or r.ligand for r in result.rows)
                preview = [{"Region": r.name, "kcal/mol": r.kcal} for r in result.rows]
                if has_metadata:
                    for row, r in zip(preview, result.rows, strict=True):
                        row["PDB ID"] = r.pdb_id or ""
                        row["Protein/Gene"] = r.protein or ""
                        row["Ligand"] = r.ligand or ""
                st.dataframe(preview, width="stretch", hide_index=True)
            for err in result.errors:
                st.warning(f"⚠️ {err}")
            if result.rows and st.button(
                f"➕ Import {len(result.rows)} region(s)", key="csv_import_btn", width="stretch"
            ):
                for r in result.rows:
                    add_region(r.name, r.kcal, r.coordinates)
                st.rerun()

        st.divider()
        st.markdown("**🔎 PDB ID → gene & suggested region** _(via RCSB)_")
        pdb_query = st.text_input(
            "PDB ID", placeholder="e.g. 6CM4", key="pdb_lookup_query",
            help=(
                "RCSB has no brain-region field at all (checked against its "
                "live API) - only structural/genetic facts. This resolves the "
                "gene/UniProt ID automatically, then suggests candidate "
                "region(s) from a small curated table (same sources as "
                "Receptor Weighting below) - a hypothesis to confirm, never "
                "an auto-pick."
            ),
        )
        if st.button("Look up", key="pdb_lookup_btn") and pdb_query.strip():
            meta = fetch_pdb_metadata(pdb_query)
            if meta is None:
                st.warning(
                    "⚠️ No metadata found - check the PDB ID, or RCSB may be "
                    "unreachable right now."
                )
            else:
                st.markdown(
                    f"**{meta.pdb_id}** — {meta.title or '_no title_'}  \n"
                    f"Organism: {meta.organism or 'n/a'} · "
                    f"Gene: {meta.gene or 'n/a'} · "
                    f"UniProt: {meta.uniprot_id or 'n/a'}"
                )
                candidates = suggest_regions(meta.gene) if meta.gene else None
                if candidates:
                    st.success(
                        f"Suggested region(s) for **{meta.gene}**: "
                        f"{', '.join(candidates)}  \n"
                        f"Source: {get_gene_citation(meta.gene)}"
                    )
                elif meta.gene:
                    st.info(
                        f"'{meta.gene}' isn't in this app's curated gene→region "
                        "table - pick the region yourself from anatomical/"
                        "pharmacological knowledge of this target."
                    )
        st.divider()

        vina_file = st.file_uploader(
            "Vina result (.pdbqt or log)", type=["pdbqt", "txt", "log"], key="vina_import",
            help=(
                "Extracts the best (top-ranked) score from a Vina `.pdbqt` pose "
                "file or its plain-text log, and prefills Binding Affinity below "
                "- a docking score has no inherent region, so you still pick "
                "the matching region yourself."
            ),
        )
        if vina_file is not None:
            file_id = f"{vina_file.name}_{vina_file.size}"
            score = parse_vina_score(vina_file.getvalue().decode("utf-8", errors="replace"))
            if score is None:
                st.warning(
                    "⚠️ No Vina score recognized in this file (expected a "
                    "`REMARK VINA RESULT:` line, or a results table with a "
                    "numbered pose row)."
                )
            else:
                # Only prefill once per uploaded file - otherwise every
                # unrelated rerun (e.g. moving the threshold slider) would
                # keep re-overwriting anything the user typed afterwards.
                if st.session_state.get("_last_vina_file_id") != file_id:
                    st.session_state["_last_vina_file_id"] = file_id
                    st.session_state["kcal_input"] = max(-15.0, min(-0.1, score))
                st.success(
                    f"Best score found: **{score:.1f} kcal/mol** - prefilled into "
                    "\"Binding Affinity\" below. Pick the matching region and click Add."
                )


def _render_session_io():
    """Save/load the current analysis (region list + receptor weighting) as
    a small JSON file, so it can be resumed or handed to a colleague without
    a screenshot.

    Reads `regions`/`receptor_weight` itself (rather than taking them as
    arguments) and must run *before* the Receptor Weighting selectbox is
    instantiated below: on load, it needs to set that widget's
    `st.session_state` entry to the loaded value, and Streamlit raises if a
    widget's session_state is written after that widget has already been
    created in the same run. Reading `_RECEPTOR_WEIGHT_KEY` from
    session_state here (rather than waiting for the selectbox's return
    value) gives the same value that selectbox is about to default to.
    """
    regions = get_regions()
    current_choice = st.session_state.get(_RECEPTOR_WEIGHT_KEY, _NO_RECEPTOR_WEIGHT)
    receptor_weight = None if current_choice == _NO_RECEPTOR_WEIGHT else current_choice

    with st.expander("💾 Session (save / load)", expanded=False):
        st.caption("Persist or resume this exact analysis as a small JSON file.")
        if regions:
            st.download_button(
                "💾 Save session", data=export_session(regions, receptor_weight),
                file_name="neuroviz_session.json", mime="application/json",
                width="stretch",
                help="Downloads the current region list and receptor "
                     "weighting choice - reloading it elsewhere reproduces "
                     "this exact analysis.",
            )
        else:
            st.caption("_Add at least one region to enable saving._")

        session_file = st.file_uploader(
            "Load session", type=["json"], key="session_upload",
            help="Loading replaces the current region list and receptor "
                 "weighting choice - previously saved from this same tool.",
        )
        if session_file is not None:
            file_id = f"{session_file.name}_{session_file.size}"
            # Same "only act once per uploaded file" guard as the CSV/Vina
            # importers above - a file_uploader's value persists across
            # reruns, so without this an unrelated widget tweak would keep
            # re-clearing and re-loading the same file over and over.
            if st.session_state.get("_last_session_file_id") != file_id:
                st.session_state["_last_session_file_id"] = file_id
                result = import_session(session_file.getvalue().decode("utf-8", errors="replace"))
                for err in result.errors:
                    st.warning(f"⚠️ {err}")
                if result.regions:
                    clear_regions()
                    for r in result.regions:
                        add_region(r.name, r.kcal, r.coordinates)
                    st.session_state[_RECEPTOR_WEIGHT_KEY] = (
                        result.receptor_weight
                        if result.receptor_weight is not None
                        else _NO_RECEPTOR_WEIGHT
                    )
                    st.success(f"Loaded {len(result.regions)} region(s).")
                    st.rerun()


def render_sidebar() -> tuple[float, str, str, str | None]:
    """Renders the full sidebar; returns (threshold, surf_mesh, mpl_cmap,
    receptor_weight) for the main view."""
    with st.sidebar:
        render_sidebar_brain_icon()
        _render_docking_import()
        st.header("Add Brain Region")

        input_mode = st.radio(
            "Input mode",
            [_INPUT_MODE_NAMED, _INPUT_MODE_EXACT],
            help="Named region: pick from the 28 atlas-verified regions below. "
                 "Exact coordinates: for researchers who already know their precise "
                 "target (e.g. a DBS contact or a paper-reported peak) - renders a "
                 "focused point exactly there instead of a whole-region mask.",
        )

        coordinates = None
        if input_mode == _INPUT_MODE_NAMED:
            region = st.selectbox("Brain Region", get_region_names())
            if is_atlas_backed(region):
                st.caption(f"✅ Atlas-backed — {get_atlas_source(region)}")
            else:
                st.caption("⚠️ Illustrative point (no standard atlas available for this region)")
        else:
            st.caption(
                "Exact point, **not** mirrored across the midline - chosen on "
                "purpose and may be intentionally one-sided (unlike named regions)."
            )
            col_x, col_y, col_z = st.columns(3)
            x = col_x.number_input("X (mm)", min_value=MNI_X_RANGE[0], max_value=MNI_X_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = left, positive = right.")
            y = col_y.number_input("Y (mm)", min_value=MNI_Y_RANGE[0], max_value=MNI_Y_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = posterior, positive = anterior.")
            z = col_z.number_input("Z (mm)", min_value=MNI_Z_RANGE[0], max_value=MNI_Z_RANGE[1],
                                   value=0.0, step=1.0, help="Negative = inferior, positive = superior.")
            coordinates = (x, y, z)
            region = f"Custom ({x:.0f}, {y:.0f}, {z:.0f})"

        kcal_score = st.number_input(
            "Binding Affinity (kcal/mol)",
            min_value=-15.0,
            max_value=-0.1,
            value=-7.0,
            step=0.1,
            format="%.1f",
            key="kcal_input",
            help="Enter a negative value. More negative = stronger binding. "
                 "Typical range: -1 (weak) to -15 (very strong). Can be "
                 "prefilled from a Vina result file via the import section above.",
        )

        if st.button("➕ Add Region", width="stretch"):
            add_region(region, kcal_score, coordinates)
            st.rerun()

        st.divider()
        st.header("Active Regions")

        regions = get_regions()
        if not regions:
            st.info("No regions added yet.")
        else:
            to_remove = None
            for i, entry in enumerate(regions):
                label, color, text_color = strength_label(entry.normalized_intensity)
                col1, col2 = st.columns([4, 1])
                col1.markdown(
                    '<div class="region-chip">'
                    f'<div class="region-chip-name">{entry.name}</div>'
                    '<div class="region-chip-meta">'
                    f'<span>{entry.kcal:.1f} kcal/mol · {entry.normalized_intensity:.0f}%</span>'
                    f'<span class="region-chip-tag" style="background:{color};color:{text_color}">{label}</span>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                if col2.button("✕", key=f"rm_{i}", help=f"Remove {entry.name}"):
                    to_remove = i

            if to_remove is not None:
                remove_region(to_remove)
                st.rerun()

            if st.button("🗑️ Clear All", width="stretch"):
                clear_regions()
                st.rerun()

        st.divider()
        _render_session_io()

        st.divider()
        st.header("Rendering")
        threshold = st.slider(
            "Display threshold (intensity)",
            min_value=0.0, max_value=0.50, value=0.08, step=0.01,
            help="Hide activation below this normalized intensity. Higher = only the "
                 "strongest voxels are shown. Applies to all three views.",
        )
        surf_res = st.selectbox(
            "Surface resolution (3D views)",
            ["fsaverage6  ·  ~41k/hemi (sharp)",
             "fsaverage5  ·  ~10k/hemi (fast)",
             "fsaverage   ·  ~164k/hemi (slow)"],
            index=0,
            help="Higher-resolution cortical mesh = finer folds, slower render.",
        )
        surf_mesh = surf_res.split()[0]   # "fsaverage6" / "fsaverage5" / "fsaverage"

        scheme_name = st.selectbox(
            "Color scheme",
            list(COLOR_SCHEMES.keys()),
            index=list(COLOR_SCHEMES.keys()).index(DEFAULT_COLOR_SCHEME),
            help="Warm (gray → red) is the original palette. Colorblind-safe "
                 "(viridis) is a perceptually-uniform alternative for red-green "
                 "color vision deficiency, applied to all five views.",
        )
        mpl_cmap = COLOR_SCHEMES[scheme_name]

        st.divider()
        st.header("Receptor Weighting (optional)")
        receptor_choice = st.selectbox(
            "Weight affinity by real receptor density",
            [_NO_RECEPTOR_WEIGHT] + RECEPTOR_NAMES,
            key=_RECEPTOR_WEIGHT_KEY,
            help="If your compound targets a specific receptor/transporter, "
                 "weight the affinity map by that target's real, published "
                 "PET-derived density across the brain instead of painting "
                 "the whole selected region uniformly - two compounds with "
                 "the same affinity on the same receptor will then light up "
                 "differently depending on where that receptor actually sits. "
                 "Structural density is not a guarantee of functional effect.",
        )
        receptor_weight = None if receptor_choice == _NO_RECEPTOR_WEIGHT else receptor_choice
        if receptor_weight is not None:
            st.caption(f"📡 {get_receptor_citation(receptor_weight)}")
            st.caption(f"Compiled via {HANSEN_2022_CITATION}")

    return threshold, surf_mesh, mpl_cmap, receptor_weight

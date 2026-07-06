"""Theme CSS and the small HTML snippets (header, sidebar mark, loader)
used to skin the default Streamlit chrome.

Design intent: a restrained, editorial look for a scientific tool - solid
neutral surfaces, one confident accent color used sparingly for emphasis
and interactive state (not a decorative gradient), real borders on every
input so it reads as editable at a glance, and no animated mascot or
glass/shimmer effects competing with the actual data.
"""
import streamlit as st

_INK = "#1B1B26"          # primary text - near-black, not a tinted gray
_INK_SOFT = "#55556B"     # secondary text
_ACCENT = "#3D3480"       # single solid accent (buttons, links, active state)
_ACCENT_DARK = "#2C2566"  # accent hover/pressed
_LINE = "#DCDCE3"         # neutral border
_LINE_SOFT = "#E9E9EF"
_SURFACE = "#FFFFFF"
_SURFACE_SUNKEN = "#F4F4F7"

_CSS = f"""
<style>
/* ---- Base palette: neutral surfaces, accent reserved for emphasis ---- */
.stApp {{
    background: {_SURFACE_SUNKEN};
}}
section[data-testid="stSidebar"] {{
    background: {_SURFACE};
    border-right: 1px solid {_LINE};
}}
h1, h2, h3, h4, .stMarkdown p, label, [data-testid="stWidgetLabel"] p {{
    color: {_INK};
}}

/* ---- Header: static wordmark, no animation, no gradient-clipped text - */
.app-header {{
    display: flex; align-items: center; gap: 0.85rem;
    padding-bottom: 1rem; margin-bottom: 1.1rem;
    border-bottom: 1px solid {_LINE};
}}
.app-header .mark {{
    font-size: 2.1rem; line-height: 1; flex-shrink: 0;
}}
.app-header h1 {{
    font-size: 1.55rem; font-weight: 700; margin: 0; color: {_INK};
    letter-spacing: -0.3px;
}}
.app-header .subtitle {{
    color: {_INK_SOFT}; font-size: 0.92rem; margin-top: 0.15rem;
}}
.app-header .byline {{
    margin-top: 0.35rem; font-size: 0.85rem; color: {_INK_SOFT};
}}
.app-header .byline b {{ color: {_INK}; font-weight: 700; }}

/* ---- Sidebar mark: small, static, top-left - not a spinning centerpiece */
.sidebar-mark {{
    display: flex; align-items: center; gap: 0.5rem;
    margin: 0.1rem 0 0.9rem 0; padding-bottom: 0.7rem;
    border-bottom: 1px solid {_LINE};
}}
.sidebar-mark .glyph {{ font-size: 1.35rem; line-height: 1; }}
.sidebar-mark .label {{
    font-size: 0.82rem; font-weight: 700; color: {_INK};
    text-transform: uppercase; letter-spacing: 0.6px;
}}

/* ---- Buttons: one filled primary style, clear hover/focus, no gradient - */
.stButton > button, .stDownloadButton > button {{
    border-radius: 7px; border: 1px solid {_LINE};
    background: {_SURFACE}; color: {_INK}; font-weight: 600;
    transition: border-color 0.12s ease, background 0.12s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: {_ACCENT}; color: {_ACCENT}; background: {_SURFACE_SUNKEN};
}}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{
    outline: 2px solid {_ACCENT}; outline-offset: 1px;
}}
/* Primary action buttons (Add Region, Import N, Save session) - filled,
   so the one button that actually commits an action stands out from
   secondary controls (Clear All, ✕) instead of every button looking alike. */
.stButton > button[kind="primary"] {{
    background: {_ACCENT}; border-color: {_ACCENT}; color: #FFFFFF;
}}
.stButton > button[kind="primary"]:hover {{
    background: {_ACCENT_DARK}; border-color: {_ACCENT_DARK}; color: #FFFFFF;
}}

/* ---- Text/number inputs: explicit border + fill so they read as ------- */
/* ---- editable at a glance - Streamlit's own default is nearly          */
/* ---- invisible against this app's surfaces (the reported issue).      */
/* BaseWeb wraps the actual visible box in its own container div (not the
   bare <input>/<textarea> itself) - styling only the inner element left
   the real border at Streamlit's near-invisible default, which was the
   reported bug (a text field with no visible edge reads as non-editable). */
div[data-baseweb="base-input"],
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] {{
    background: {_SURFACE} !important;
    border: 1.5px solid {_LINE} !important;
    border-radius: 7px !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {{
    background: transparent !important;
    color: {_INK} !important;
}}
div[data-baseweb="base-input"]:hover,
div[data-baseweb="select"]:hover > div,
div[data-baseweb="textarea"]:hover {{
    border-color: #B9B9C9 !important;
}}
div[data-baseweb="base-input"]:has(input:focus),
div[data-baseweb="select"]:has(input:focus) > div,
div[data-baseweb="textarea"]:has(textarea:focus) {{
    border-color: {_ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(61,52,128,0.15) !important;
}}
div[data-testid="stFileUploaderDropzone"] {{
    background: {_SURFACE} !important; border: 1.5px dashed {_LINE} !important;
}}

/* ---- Affinity summary: solid cards, solid progress fill, no shimmer --- */
.aff-wrap {{ margin-top: 0.4rem; }}
.aff-card {{
    background: {_SURFACE};
    border: 1px solid {_LINE}; border-radius: 10px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.7rem;
    box-shadow: 0 1px 3px rgba(27,27,38,0.05);
}}
.aff-head {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.55rem;
}}
.aff-name {{ font-weight: 700; font-size: 1.0rem; color: {_INK}; }}
.aff-meta {{ display: flex; align-items: center; gap: 0.5rem; }}
.aff-kcal {{
    font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.8rem;
    color: {_ACCENT}; background: {_SURFACE_SUNKEN};
    padding: 0.12rem 0.5rem; border-radius: 5px;
}}
.aff-tag {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.4px;
    text-transform: uppercase; color: #FFFFFF;
    padding: 0.12rem 0.55rem; border-radius: 5px;
}}
.aff-bar-row {{ display: flex; align-items: center; gap: 0.85rem; }}
.aff-track {{
    position: relative; flex: 1; height: 10px; border-radius: 999px;
    background: {_SURFACE_SUNKEN}; overflow: hidden;
    border: 1px solid {_LINE_SOFT};
}}
.aff-fill {{
    height: 100%; border-radius: 999px;
    background: {_ACCENT};
}}
.aff-pct {{
    min-width: 46px; text-align: right; font-weight: 700;
    font-size: 0.95rem; color: {_INK};
}}

/* ---- Sidebar "Active Regions" chips (mirrors .aff-card, compact) ------ */
.region-chip {{
    background: {_SURFACE};
    border: 1px solid {_LINE}; border-radius: 8px;
    padding: 0.55rem 0.75rem; margin-bottom: 0.45rem;
}}
.region-chip-name {{
    font-weight: 700; font-size: 0.87rem; color: {_INK};
    margin-bottom: 0.2rem;
}}
.region-chip-meta {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 0.4rem; font-size: 0.72rem; color: {_INK_SOFT};
}}
.region-chip-tag {{
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.3px;
    text-transform: uppercase; color: #FFFFFF;
    padding: 0.08rem 0.4rem; border-radius: 4px; white-space: nowrap;
}}
/* Nudge the "✕" remove button to align with the taller two-line chip */
div[data-testid="stSidebar"] div[data-testid="column"]:has(button[kind]) button {{
    margin-top: 0.55rem;
}}

/* ---- Loading state: a plain indeterminate bar, no mascot -------------- */
@keyframes slidebar {{
    0%   {{ margin-left: -45%; }}
    100% {{ margin-left: 100%; }}
}}
.brain-loader-wrap {{
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 2.2rem 0; gap: 0.7rem;
}}
.brain-loader-wrap .msg {{
    color: {_INK_SOFT}; font-weight: 600; letter-spacing: 0.2px; font-size: 0.9rem;
}}
.brain-loader-wrap .track {{
    width: 220px; height: 5px; border-radius: 999px;
    background: {_LINE_SOFT}; overflow: hidden;
}}
.brain-loader-wrap .track .bar {{
    height: 100%; width: 40%; border-radius: 999px;
    background: {_ACCENT};
    animation: slidebar 1.3s ease-in-out infinite;
}}

/* Replace Streamlit's built-in first-load icons with a plain neutral bar */
[data-testid="stSkeleton"],
.stApp [class*="loading"] svg,
.stApp [class*="Loading"] svg,
div[data-testid="stDecoration"] {{ display: none !important; }}

/* ---- Remove the Deploy button (not relevant for local use) ---------- */
[data-testid="stAppDeployButton"] {{ display: none !important; }}

/* ---- View Mode: segmented control, solid active state (no gradient) -- */
div[data-testid="stRadio"] > div[role="radiogroup"] {{
    display: inline-flex; flex-wrap: wrap; gap: 0.25rem;
    background: {_SURFACE_SUNKEN}; border: 1px solid {_LINE};
    border-radius: 8px; padding: 0.25rem;
}}
div[data-testid="stRadio"] label {{
    border-radius: 6px; padding: 0.3rem 0.9rem !important; margin: 0 !important;
    transition: background 0.12s ease; cursor: pointer;
}}
div[data-testid="stRadio"] label:hover {{ background: rgba(61,52,128,0.06); }}
div[data-testid="stRadio"] label:has(input:checked) {{
    background: {_ACCENT};
}}
div[data-testid="stRadio"] label:has(input:checked) p {{
    color: #FFFFFF !important; font-weight: 700;
}}

/* ---- Expanders: flat card chrome, no blur/glow -------------------- */
div[data-testid="stExpander"] {{
    border: 1px solid {_LINE} !important; border-radius: 10px !important;
    background: {_SURFACE}; box-shadow: none;
    overflow: hidden;
}}
div[data-testid="stExpander"] summary {{
    font-weight: 600; color: {_INK};
}}

/* ---- Respect prefers-reduced-motion (WCAG 2.3.3) ---------------------- */
@media (prefers-reduced-motion: reduce) {{
    .brain-loader-wrap .track .bar {{ animation: none !important; }}
}}
</style>
"""


def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero_header():
    st.markdown(
        """
        <div class="app-header">
            <span class="mark">🧠</span>
            <div>
                <h1>Neuro-Target Affinity Visualizer</h1>
                <div class="subtitle">Visualize protein / target binding affinity across brain regions</div>
                <div class="byline">Made by <b>Ayoub Riad</b> &nbsp;·&nbsp; Researcher in Bioinformatics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brain_icon():
    st.markdown(
        '<div class="sidebar-mark"><span class="glyph">🧠</span>'
        '<span class="label">NeuroViz</span></div>',
        unsafe_allow_html=True,
    )


def brain_loader_html(message):
    """A centered, indeterminate progress bar with a status message."""
    return (
        '<div class="brain-loader-wrap">'
        f'<div class="msg">{message}</div>'
        '<div class="track"><div class="bar"></div></div>'
        '</div>'
    )

"""Theme CSS and the small HTML snippets (hero header, sidebar brain, loader
spinner) used to skin the default Streamlit chrome.
"""
import streamlit as st

_CSS = """
<style>
/* ---- Base palette ---------------------------------------------------- */
.stApp {
    background: linear-gradient(160deg, #FBFBFE 0%, #F2F1F9 55%, #ECEAF6 100%);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F3F1FB 0%, #E8E5F4 100%);
    border-right: 1px solid #E0DCEF;
}

/* ---- Centered hero header -------------------------------------------- */
.brain-hero { text-align: center; margin: 0.2rem 0 1.3rem 0; }
.brain-hero .brain-icon {
    font-size: 56px; display: inline-block; line-height: 1;
    animation: brainspin 3.4s linear infinite;
    filter: drop-shadow(0 5px 12px rgba(138,111,196,0.35));
}
.brain-hero h1 {
    font-size: 2.5rem; font-weight: 800; margin: 0.35rem 0 0 0;
    background: linear-gradient(90deg, #6E5BB5 0%, #9A6FC9 45%, #C77FB4 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brain-hero .subtitle {
    color: #5C5570; font-size: 1.05rem; margin-top: 0.4rem;
}
.brain-hero .byline {
    margin-top: 0.75rem; font-size: 1.25rem; color: #5C5570; font-weight: 500;
}
.brain-hero .byline b {
    color: #6E5BB5; font-size: 1.45rem; font-weight: 800;
    letter-spacing: 0.3px;
}
.brain-hero hr {
    border: none; height: 2px; width: 130px; margin: 1rem auto 0 auto;
    background: linear-gradient(90deg, transparent, #B49BDE, transparent);
}

/* ---- Rotating brain at the top of the sidebar ------------------------ */
.sidebar-brain { text-align: center; margin: 0.1rem 0 0.5rem 0; }
.sidebar-brain .spin {
    font-size: 46px; display: inline-block; line-height: 1;
    animation: brainspin 3.4s linear infinite;
    filter: drop-shadow(0 4px 10px rgba(138,111,196,0.35));
}

/* ---- Buttons --------------------------------------------------------- */
.stButton > button {
    border-radius: 10px; border: 1px solid #CFC4EA;
    background: #FFFFFF; color: #4B4368; font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #8A6FC4; color: #6E5BB5;
    box-shadow: 0 2px 10px rgba(138,111,196,0.25);
}

/* ---- Affinity summary (professional / futuristic bars) --------------- */
.aff-wrap { margin-top: 0.4rem; }
.aff-card {
    background: rgba(255,255,255,0.66);
    border: 1px solid #E2DCF1; border-radius: 14px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.7rem;
    box-shadow: 0 2px 12px rgba(110,91,181,0.07);
    backdrop-filter: blur(4px);
}
.aff-head {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.55rem;
}
.aff-name { font-weight: 700; font-size: 1.02rem; color: #2D2A3A; }
.aff-meta { display: flex; align-items: center; gap: 0.5rem; }
.aff-kcal {
    font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.8rem;
    color: #6E5BB5; background: #EFEAF9;
    padding: 0.12rem 0.5rem; border-radius: 6px;
}
.aff-tag {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.4px;
    text-transform: uppercase; color: #FFFFFF;
    padding: 0.12rem 0.55rem; border-radius: 6px;
}
.aff-bar-row { display: flex; align-items: center; gap: 0.85rem; }
.aff-track {
    position: relative; flex: 1; height: 13px; border-radius: 999px;
    background: #E8E3F4; overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(76,67,104,0.18);
}
.aff-fill {
    position: relative; height: 100%; border-radius: 999px; overflow: hidden;
    background: linear-gradient(90deg, #6E5BB5 0%, #9A6FC9 50%, #C77FB4 100%);
    box-shadow: 0 0 10px rgba(154,111,201,0.55);
}
.aff-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
    transform: translateX(-100%);
    animation: shimmer 2.2s ease-in-out infinite;
}
@keyframes shimmer { 100% { transform: translateX(100%); } }
.aff-pct {
    min-width: 50px; text-align: right; font-weight: 800;
    font-size: 1.0rem; color: #6E5BB5;
}

/* ---- Sidebar "Active Regions" chips (mirrors .aff-card, compact) ------ */
.region-chip {
    background: rgba(255,255,255,0.66);
    border: 1px solid #E2DCF1; border-radius: 12px;
    padding: 0.55rem 0.75rem; margin-bottom: 0.45rem;
    box-shadow: 0 1px 6px rgba(110,91,181,0.06);
}
.region-chip-name {
    font-weight: 700; font-size: 0.88rem; color: #2D2A3A;
    margin-bottom: 0.2rem;
}
.region-chip-meta {
    display: flex; align-items: center; justify-content: space-between;
    gap: 0.4rem; font-size: 0.72rem; color: #6E5BB5;
}
.region-chip-tag {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.3px;
    text-transform: uppercase; color: #FFFFFF;
    padding: 0.08rem 0.4rem; border-radius: 5px; white-space: nowrap;
}
/* Nudge the "✕" remove button to align with the taller two-line chip */
div[data-testid="stSidebar"] div[data-testid="column"]:has(button[kind]) button {
    margin-top: 0.55rem;
}

/* ---- Rotating-brain loader (reusable + first-load splash) ------------ */
@keyframes brainspin {
    0%   { transform: rotateY(0deg); }
    100% { transform: rotateY(360deg); }
}
@keyframes slidebar {
    0%   { margin-left: -45%; }
    100% { margin-left: 100%; }
}
.brain-loader-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 2.6rem 0; gap: 0.9rem;
}
.brain-loader-wrap .spin {
    font-size: 74px; display: inline-block; line-height: 1;
    animation: brainspin 1.5s linear infinite;
    filter: drop-shadow(0 5px 14px rgba(138,111,196,0.40));
}
.brain-loader-wrap .msg {
    color: #6E5BB5; font-weight: 600; letter-spacing: 0.3px;
}
.brain-loader-wrap .track {
    width: 230px; height: 6px; border-radius: 999px;
    background: #E2DCF1; overflow: hidden;
}
.brain-loader-wrap .track .bar {
    height: 100%; width: 45%; border-radius: 999px;
    background: linear-gradient(90deg, #8A6FC4, #C77FB4);
    animation: slidebar 1.4s ease-in-out infinite;
}

/* Replace Streamlit's built-in first-load sport icons with a brain */
[data-testid="stSkeleton"],
.stApp [class*="loading"] svg,
.stApp [class*="Loading"] svg,
div[data-testid="stDecoration"],
div[class*="loaderContainer"] svg,
div[class*="loaderContainer"] img,
div[class*="LoadingContainer"] svg,
div[class*="LoadingContainer"] img { display: none !important; }
div[class*="loaderContainer"]::before,
div[class*="LoadingContainer"]::before {
    content: "🧠"; font-size: 72px; display: block; text-align: center;
    animation: brainspin 1.5s linear infinite;
}

/* ---- Top-right "Running…" indicator → spinning brain (was a runner) -- */
[data-testid="stStatusWidgetRunningIcon"] svg,
[data-testid="stStatusWidgetRunningManIcon"] { display: none !important; }
[data-testid="stStatusWidgetRunningIcon"]::before {
    content: "🧠"; font-size: 1.55rem; line-height: 1;
    display: inline-block; transform-origin: center;
    animation: brainspin 1.4s linear infinite;
}

/* ---- Remove the Deploy button (not relevant for local use) ---------- */
[data-testid="stAppDeployButton"] { display: none !important; }

/* ---- View Mode: dress the default radio group up as a segmented control */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: inline-flex; flex-wrap: wrap; gap: 0.3rem;
    background: #EDEAF7; border: 1px solid #E0DCEF;
    border-radius: 999px; padding: 0.3rem;
}
div[data-testid="stRadio"] label {
    border-radius: 999px; padding: 0.3rem 0.9rem !important; margin: 0 !important;
    transition: all 0.15s ease; cursor: pointer;
}
div[data-testid="stRadio"] label:hover { background: rgba(255,255,255,0.6); }
div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(90deg, #6E5BB5 0%, #9A6FC9 100%);
    box-shadow: 0 2px 8px rgba(110,91,181,0.35);
}
div[data-testid="stRadio"] label:has(input:checked) p {
    color: #FFFFFF !important; font-weight: 700;
}

/* ---- Expanders (view guide, methods panel): card-style chrome -------- */
div[data-testid="stExpander"] {
    border: 1px solid #E2DCF1 !important; border-radius: 14px !important;
    background: rgba(255,255,255,0.55); box-shadow: 0 2px 10px rgba(110,91,181,0.06);
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    font-weight: 600; color: #4B4368;
}

/* ---- Respect prefers-reduced-motion (WCAG 2.3.3): the spinning brain,   */
/* shimmer bar, and loader animations can trigger vestibular discomfort.  */
@media (prefers-reduced-motion: reduce) {
    .brain-hero .brain-icon,
    .sidebar-brain .spin,
    .brain-loader-wrap .spin,
    .brain-loader-wrap .track .bar,
    .aff-fill::after,
    div[class*="loaderContainer"]::before,
    div[class*="LoadingContainer"]::before,
    [data-testid="stStatusWidgetRunningIcon"]::before {
        animation: none !important;
    }
}
</style>
"""


def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero_header():
    st.markdown(
        """
        <div class="brain-hero">
            <span class="brain-icon">🧠</span>
            <h1>Neuro-Target Affinity Visualizer</h1>
            <div class="subtitle">Visualize protein / target binding affinity across brain regions</div>
            <div class="byline">🔬 Made by <b>Ayoub Riad</b> &nbsp;·&nbsp; Researcher in Bioinformatics</div>
            <hr/>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brain_icon():
    st.markdown(
        '<div class="sidebar-brain"><span class="spin">🧠</span></div>',
        unsafe_allow_html=True,
    )


def brain_loader_html(message):
    """A centered, rotating-brain spinner with an indeterminate progress bar."""
    return (
        '<div class="brain-loader-wrap">'
        '<span class="spin">🧠</span>'
        f'<div class="msg">{message}</div>'
        '<div class="track"><div class="bar"></div></div>'
        '</div>'
    )

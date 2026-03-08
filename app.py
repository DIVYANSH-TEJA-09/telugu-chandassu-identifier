import streamlit as st
import sys
import os

sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine
from telugu_chandas.models import Weight
from telugu_chandas.locale import GANA_NAMES_TE, UI_STRINGS, METER_NAMES_TE, YATI_CATEGORY_NAMES_TE, METER_TYPE_TE
from telugu_chandas.analyzer import ProsodyAnalyzer
from telugu_chandas.jati_registry import JatiRegistry
from telugu_chandas.jati_segmenter import segment_surya_indra, segment_kandam

st.set_page_config(
    page_title="తెలుగు ఛందస్సు విశ్లేషకం",
    page_icon="📜",
    layout="wide"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Suravaram&display=swap');

    /* ── Global ── */
    h1, h2, h3, h4, h5, h6 { font-family: 'Suravaram', serif !important; }

    /* ── Hero ── */
    .hero-wrap {
        text-align: center;
        padding: 2rem 0 1.2rem 0;
    }
    .hero-title {
        font-family: 'Suravaram', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
    }
    .hero-sub {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }
    .stat-pills {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }
    .stat-pill {
        background: linear-gradient(135deg, #667eea22, #764ba222);
        border: 1px solid #667eea44;
        border-radius: 999px;
        padding: 5px 18px;
        font-family: 'Suravaram', serif;
        font-size: 0.88rem;
        color: #4f46e5;
        font-weight: 600;
    }

    /* ── Feature Cards ── */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin: 1.5rem 0;
    }
    .feature-card {
        background: white;
        border-radius: 14px;
        padding: 22px 20px;
        box-shadow: 0 2px 16px rgba(102,126,234,0.09);
        border: 1px solid #e8eaf6;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(102,126,234,0.15);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    .feature-title {
        font-family: 'Suravaram', serif;
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 6px;
    }
    .feature-desc {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.82rem;
        color: #64748b;
        line-height: 1.6;
    }

    /* ── Meter Table ── */
    .meters-section {
        background: #f8fafc;
        border-radius: 16px;
        padding: 24px;
        margin: 1.5rem 0;
        border: 1px solid #e2e8f0;
    }
    .meters-section-title {
        font-family: 'Suravaram', serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 16px;
    }
    .meter-group {
        margin-bottom: 16px;
    }
    .meter-group-label {
        font-family: 'Suravaram', serif;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #667eea;
        margin-bottom: 8px;
    }
    .meter-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .meter-chip {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 14px;
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.85rem;
        color: #334155;
        font-weight: 500;
    }
    .meter-chip .te { font-size: 0.95rem; }
    .meter-chip .en { font-size: 0.72rem; color: #94a3b8; display: block; }

    /* ── Result: Meter Card ── */
    .meter-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .meter-name {
        font-family: 'Suravaram', serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .meter-type-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border-radius: 999px;
        padding: 3px 14px;
        font-size: 0.82rem;
        font-family: 'Suravaram', serif;
        margin-bottom: 12px;
    }
    .meter-score-row {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .score-big {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1;
    }
    .score-bar-wrap { flex: 1; min-width: 120px; }
    .score-bar-bg {
        background: rgba(255,255,255,0.25);
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
    }
    .score-bar-fill {
        background: white;
        height: 8px;
        border-radius: 999px;
        transition: width 0.6s ease;
    }
    .score-label {
        font-size: 0.78rem;
        opacity: 0.8;
        margin-top: 4px;
        font-family: 'Suravaram', serif;
    }
    .score-breakdown {
        font-size: 0.78rem;
        opacity: 0.75;
        font-family: 'Suravaram', serif;
        margin-top: 8px;
    }

    /* ── Validation Cards ── */
    .validation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 20px;
    }
    .validation-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 4px solid;
    }
    .validation-card.valid   { border-left-color: #10b981; }
    .validation-card.invalid { border-left-color: #ef4444; }
    .validation-card.neutral { border-left-color: #94a3b8; }
    .validation-title {
        font-family: 'Suravaram', serif;
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 4px;
    }
    .validation-value {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .validation-detail {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 3px;
    }

    /* ── Gana Sequence ── */
    .gana-sequence {
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .gana-sequence-title {
        font-family: 'Suravaram', serif;
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 8px;
    }
    .gana-sequence-content {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #334155;
        letter-spacing: 0.4rem;
    }

    /* ── Padyam Visualization ── */
    .padyam-container {
        background: white;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 14px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
    }
    .line-number {
        font-family: 'Suravaram', serif;
        font-size: 0.72rem;
        color: #94a3b8;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.1rem;
    }
    .padyam-line {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        align-items: flex-end;
    }
    .gana-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        background: #fafafa;
        border-radius: 8px;
        padding: 8px 6px 10px 6px;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #f0f0f0;
    }
    .gana-header {
        font-family: 'Suravaram', serif;
        font-size: 0.72rem;
        font-weight: 700;
        color: #667eea;
        padding: 2px 8px;
        background: #eef2ff;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .gana-content { display: flex; flex-direction: row; gap: 2px; }
    .akshara-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 4px 6px;
        min-width: 30px;
    }
    .weight {
        font-family: system-ui, sans-serif;
        font-size: 0.68rem;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 4px;
        margin-bottom: 4px;
    }
    .weight-U { color: #dc2626; background: #fef2f2; }
    .weight-I { color: #16a34a; background: #f0fdf4; }
    .akshara {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: #1e293b;
    }
    .word-gap {
        width: 1px; height: 24px;
        background-color: #cbd5e1;
        margin: 0 6px;
        align-self: center;
    }

    /* ── Yati Notes ── */
    .yati-section {
        background: #fffbeb;
        border-radius: 12px;
        padding: 18px 20px;
        margin-top: 20px;
        border: 1px solid #fde68a;
    }
    .yati-title {
        font-family: 'Suravaram', serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #92400e;
        margin-bottom: 10px;
    }
    .yati-item {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.88rem;
        color: #78350f;
        padding: 7px 0;
        border-bottom: 1px solid #fde68a;
    }
    .yati-item:last-child { border-bottom: none; }

    /* ── Unknown Meter ── */
    .unknown-card {
        background: #f8fafc;
        border-radius: 14px;
        padding: 32px;
        text-align: center;
        border: 2px dashed #cbd5e1;
        margin-bottom: 20px;
    }
    .unknown-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .unknown-title {
        font-family: 'Suravaram', serif;
        font-size: 1.2rem;
        color: #475569;
        margin-bottom: 6px;
    }
    .unknown-sub {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* ── Input ── */
    .stTextArea textarea {
        font-family: 'Noto Sans Telugu', sans-serif !important;
        font-size: 1.05rem !important;
        line-height: 1.85 !important;
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.12) !important;
    }

    /* ── Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 36px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        font-family: 'Suravaram', serif !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(102,126,234,0.4) !important;
    }

    /* ── Sidebar ── */
    .sidebar-section {
        background: white;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 14px;
        border: 1px solid #e8eaf6;
    }
    .sidebar-title {
        font-family: 'Suravaram', serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: #4f46e5;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .sidebar-meter-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        border-bottom: 1px solid #f1f5f9;
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.82rem;
    }
    .sidebar-meter-row:last-child { border-bottom: none; }
    .sidebar-meter-name { color: #334155; font-weight: 600; }
    .sidebar-meter-type {
        font-size: 0.7rem;
        color: #94a3b8;
        font-family: 'Suravaram', serif;
    }
    .rule-row {
        padding: 5px 0;
        border-bottom: 1px solid #f1f5f9;
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.8rem;
        color: #475569;
        line-height: 1.5;
    }
    .rule-row:last-child { border-bottom: none; }
    .rule-label {
        font-family: 'Suravaram', serif;
        font-weight: 700;
        color: #667eea;
        font-size: 0.78rem;
    }
    .divider-line {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1.5rem 0;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_line_ganas(w_str, meter_name, pada_idx):
    jati_meter = JatiRegistry.get(meter_name)
    if jati_meter is not None and pada_idx < len(jati_meter.pada_structures):
        structure = jati_meter.pada_structures[pada_idx]
        seg = (segment_surya_indra(w_str, structure)
               if jati_meter.segmentation_type == "surya_indra"
               else segment_kandam(w_str))
        if seg:
            return [(name, len(pattern)) for name, pattern in seg]
    result = []
    for g in ProsodyAnalyzer.get_ganas(w_str):
        size = 2 if g in ("GaGa", "GaLa", "LaLa", "Va") else (1 if g in ("Ga", "La") else 3)
        result.append((GANA_NAMES_TE.get(g, g), size))
    return result


@st.cache_resource
def get_engine():
    return ChandasEngine()

engine = get_engine()


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div style="text-align:center; padding: 8px 0 16px 0;">'
                '<span style="font-family:Suravaram,serif; font-size:1.4rem; '
                'font-weight:700; background:linear-gradient(135deg,#667eea,#764ba2); '
                '-webkit-background-clip:text; -webkit-text-fill-color:transparent;">'
                '📜 ఛందస్సు విశ్లేషకం</span></div>', unsafe_allow_html=True)

    app_mode = st.selectbox(
        "Mode",
        ["ఛందస్సు విశ్లేషణ (Analyzer)", "సమాచారం (Learning Resources)"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Supported meters list
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">Supported Meters</div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">ఉత్పలమాల</span>
            <span class="sidebar-meter-type">వృత్తం</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">చంపకమాల</span>
            <span class="sidebar-meter-type">వృత్తం</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">శార్దూలము</span>
            <span class="sidebar-meter-type">వృత్తం</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">మత్తేభము</span>
            <span class="sidebar-meter-type">వృత్తం</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">ద్విపద</span>
            <span class="sidebar-meter-type">జాతి</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">తరువోజ</span>
            <span class="sidebar-meter-type">జాతి</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">కందం</span>
            <span class="sidebar-meter-type">జాతి</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">ఆటవెలది</span>
            <span class="sidebar-meter-type">ఉపజాతి</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">తేటగీతి</span>
            <span class="sidebar-meter-type">ఉపజాతి</span>
        </div>
        <div class="sidebar-meter-row">
            <span class="sidebar-meter-name">సీసం</span>
            <span class="sidebar-meter-type">ఉపజాతి</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Rules quick ref
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">Key Rules</div>
        <div class="rule-row">
            <span class="rule-label">లఘువు (I) —</span> హ్రస్వ అచ్చు
        </div>
        <div class="rule-row">
            <span class="rule-label">గురువు (U) —</span> దీర్ఘ అచ్చు, సంధ్యాక్షరం, సున్న, విసర్గ, పొల్లు
        </div>
        <div class="rule-row">
            <span class="rule-label">స్థాన గురువు —</span> సంయుక్తాక్షరం ముందు లఘువు, గురువు అవుతుంది (ఒకే పదంలో)
        </div>
        <div class="rule-row">
            <span class="rule-label">యతి —</span> నిర్ణీత స్థానంలో మైత్రి
        </div>
        <div class="rule-row">
            <span class="rule-label">ప్రాస —</span> రెండవ అక్షరం హల్లు అన్ని పాదాలలో ఒకటే
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Learning Resources mode ───────────────────────────────────────────────────

if app_mode == "సమాచారం (Learning Resources)":
    from telugu_chandas.learning_materials import render_learning_section
    render_learning_section()

# ── Analyzer mode ────────────────────────────────────────────────────────────
else:

    # ── Hero ──
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-title">తెలుగు ఛందస్సు విశ్లేషకం</div>
        <div class="hero-sub">Telugu Chandas Identifier — Laghu · Guru · Ganas · Yati · Prasa</div>
        <div class="stat-pills">
            <span class="stat-pill">📜 10 Meters</span>
            <span class="stat-pill">⚖️ Laghu &amp; Guru Analysis</span>
            <span class="stat-pill">🎯 Yati &amp; Prasa Validation</span>
            <span class="stat-pill">🔍 Gana-by-Gana Breakdown</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input ──
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        text_input = st.text_area(
            "పద్యం నమోదు చేయండి (Enter Telugu Padyam):",
            value=(
                "భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-\n"
                "భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-\n"
                "రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-\n"
                "నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"
            ),
            height=165,
            label_visibility="collapsed",
            placeholder="ఇక్కడ పద్యం టైప్ చేయండి..."
        )
    with col_btn:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        analyze = st.button("విశ్లేషించు\n(Analyze)", type="primary", use_container_width=True)

    # ── Capabilities shown before first analysis ──
    if not analyze:
        st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

        st.markdown("""
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">⚖️</div>
                <div class="feature-title">Laghu · Guru Classification</div>
                <div class="feature-desc">Every akshara is classified as లఘువు (I) or గురువు (U) using textbook rules — intrinsic length, positional guru, pollu, sunna, and visarga.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📜</div>
                <div class="feature-title">10 Meters Identified</div>
                <div class="feature-desc">Covers all major meter families — 4 Vritta (వృత్తం), 3 Jati (జాతి), and 3 Upajati (ఉపజాతి) padyam — with confidence scoring.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Yati &amp; Prasa Validation</div>
                <div class="feature-desc">Checks యతి మైత్రి (vowel harmony at the yati position) and ప్రాస (matching onset consonant of 2nd akshara) across all padas.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Gana-by-Gana Breakdown</div>
                <div class="feature-desc">Each pada is visually segmented into its constituent ganas — Surya, Indra, Kandam, or Vritta — with every akshara labelled.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔗</div>
                <div class="feature-title">Wall &amp; Hyphen Rules</div>
                <div class="feature-desc">Samyukta guru effect is blocked at word boundaries (wall rule). Hyphens break the wall. A retry pass handles missing hyphens automatically.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Confidence Score</div>
                <div class="feature-desc">Every identification comes with a 0–100% confidence score broken down into Gana (60%), Yati (20%), and Prasa (20%) components.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Supported meters grid
        st.markdown("""
        <div class="meters-section">
            <div class="meters-section-title">Supported Meters</div>

            <div class="meter-group">
                <div class="meter-group-label">వృత్తం · Vritta (Syllabic — 3-akshara ganas)</div>
                <div class="meter-chips">
                    <div class="meter-chip"><span class="te">ఉత్పలమాల</span><span class="en">Utpalamala · 20ak · Yati@10</span></div>
                    <div class="meter-chip"><span class="te">చంపకమాల</span><span class="en">Champakamala · 21ak · Yati@11</span></div>
                    <div class="meter-chip"><span class="te">శార్దూలము</span><span class="en">Shardulam · 19ak · Yati@13</span></div>
                    <div class="meter-chip"><span class="te">మత్తేభము</span><span class="en">Mattebham · 20ak · Yati@14</span></div>
                </div>
            </div>

            <div class="meter-group">
                <div class="meter-group-label">జాతి · Jati (Matra-based — Surya/Indra ganas, with Prasa)</div>
                <div class="meter-chips">
                    <div class="meter-chip"><span class="te">ద్విపద</span><span class="en">Dwipada · 2 padas · 3I+1S</span></div>
                    <div class="meter-chip"><span class="te">తరువోజ</span><span class="en">Taruvoja · 4 padas · (3I+1S)×2</span></div>
                    <div class="meter-chip"><span class="te">కందం</span><span class="en">Kandam · 4 padas · K-ganas</span></div>
                </div>
            </div>

            <div class="meter-group">
                <div class="meter-group-label">ఉపజాతి · Upajati (Jati without Prasa — Prasa-Yati allowed)</div>
                <div class="meter-chips">
                    <div class="meter-chip"><span class="te">ఆటవెలది</span><span class="en">Ataveladi · 4 padas · 3I+2S / 5S</span></div>
                    <div class="meter-chip"><span class="te">తేటగీతి</span><span class="en">Tetagiti · 4 padas · 1S+2I+2S</span></div>
                    <div class="meter-chip"><span class="te">సీసం</span><span class="en">Sisam · 4 padas · 6I+2S</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Analysis Results ──
    if analyze:
        if not text_input.strip():
            st.warning("దయచేసి పద్యాన్ని నమోదు చేయండి.")
        else:
            with st.spinner("విశ్లేషిస్తున్నాము..."):
                id_result = engine.identify_meter(text_input)

            st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

            # ── Meter Result ──
            if id_result.meter_name != "Unknown":
                meter_te    = METER_NAMES_TE.get(id_result.meter_name, id_result.meter_name)
                meter_type  = METER_TYPE_TE.get(id_result.meter_name, "పద్యం")
                score       = id_result.confidence_score
                breakdown   = id_result.notes[0] if id_result.notes else ""
                bar_width   = min(int(score), 100)

                st.markdown(f"""
                <div class="meter-card">
                    <div class="meter-type-badge">{meter_type}</div>
                    <div class="meter-name">{meter_te} <span style="font-size:1.1rem;opacity:0.7">· {id_result.meter_name}</span></div>
                    <div class="meter-score-row">
                        <div class="score-big">{score:.0f}%</div>
                        <div class="score-bar-wrap">
                            <div class="score-bar-bg">
                                <div class="score-bar-fill" style="width:{bar_width}%"></div>
                            </div>
                            <div class="score-label">Confidence Score</div>
                        </div>
                    </div>
                    <div class="score-breakdown">{breakdown}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Validation row ──
                yati_status  = "valid"   if id_result.yati_valid  else "invalid"
                prasa_status = "valid"   if id_result.prasa_valid else "invalid"
                yati_text    = "✓ చెల్లింది" if id_result.yati_valid  else "✗ చెల్లలేదు"
                prasa_text   = "✓ చెల్లింది" if id_result.prasa_valid else "✗ చెల్లలేదు"
                prasa_detail = id_result.prasa_note if id_result.prasa_note and id_result.prasa_note != "వర్తించదు (ఉపజాతి)" else "—"
                prasa_label  = "ప్రాస (Prasa)" if id_result.prasa_valid or not id_result.prasa_note.startswith("వర్తించదు") else "ప్రాస — వర్తించదు"

                # extra notes (hyphen retry etc.)
                extra_notes = [n for n in id_result.notes[1:] if n]

                st.markdown(f"""
                <div class="validation-grid">
                    <div class="validation-card {yati_status}">
                        <div class="validation-title">యతి (Yati)</div>
                        <div class="validation-value">{yati_text}</div>
                        <div class="validation-detail">పాద మైత్రి తనిఖీ</div>
                    </div>
                    <div class="validation-card {prasa_status}">
                        <div class="validation-title">{prasa_label}</div>
                        <div class="validation-value">{prasa_text}</div>
                        <div class="validation-detail">హల్లు: {prasa_detail}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Extra engine notes (e.g. hyphen retry warning)
                if extra_notes:
                    for note in extra_notes:
                        st.info(note)

                # ── Gana Sequence ──
                ganas_te = [GANA_NAMES_TE.get(g, g) for g in id_result.ganas_found]
                st.markdown(f"""
                <div class="gana-sequence">
                    <div class="gana-sequence-title">గణ విభజన (Gana Sequence — first pada)</div>
                    <div class="gana-sequence-content">{' '.join(ganas_te)}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Yati Notes ──
                if id_result.yati_notes:
                    items = "".join(f'<div class="yati-item">{n}</div>' for n in id_result.yati_notes)
                    st.markdown(f"""
                    <div class="yati-section">
                        <div class="yati-title">యతి మైత్రి వివరాలు (Per-Pada Yati Detail)</div>
                        {items}
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.markdown("""
                <div class="unknown-card">
                    <div class="unknown-icon">🔎</div>
                    <div class="unknown-title">గుర్తించబడని పద్యం</div>
                    <div class="unknown-sub">No matching meter found. Check that the poem is in Telugu and follows a standard chandas.</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Line-by-Line Breakdown ──
            st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
            st.markdown("### పాద విశ్లేషణ (Line-by-Line Breakdown)")

            tokens = engine.analyze(text_input)

            lines_of_tokens, current = [], []
            for tok in tokens:
                if not tok.is_word and '\n' in tok.text:
                    if current:
                        lines_of_tokens.append(current)
                        current = []
                else:
                    current.append(tok)
            if current:
                lines_of_tokens.append(current)

            for line_idx, line_tokens in enumerate(lines_of_tokens):
                flat = []
                for tok in line_tokens:
                    if tok.is_word:
                        n = len(tok.aksharas)
                        for i, ak in enumerate(tok.aksharas):
                            flat.append({'akshara': ak, 'is_word_end': i == n - 1})

                w_str = "".join(item['akshara'].weight.value for item in flat if item['akshara'].weight)
                ganas = get_line_ganas(w_str, id_result.meter_name, line_idx)

                parts = [
                    f'<div class="padyam-container">',
                    f'<div class="line-number">పాదం {line_idx + 1} &nbsp;·&nbsp; {len(flat)} అక్షరాలు &nbsp;·&nbsp; {w_str}</div>',
                    '<div class="padyam-line">',
                ]

                ak_idx = 0
                for gana_name_te, chunk_size in ganas:
                    end = min(ak_idx + chunk_size, len(flat))
                    chunk = flat[ak_idx:end]
                    parts += [
                        '<div class="gana-block">',
                        f'<div class="gana-header">{gana_name_te}</div>',
                        '<div class="gana-content">',
                    ]
                    for item in chunk:
                        ak    = item['akshara']
                        w_val = ak.weight.value if ak.weight else "?"
                        parts += [
                            '<div class="akshara-box">',
                            f'<span class="weight weight-{w_val}">{w_val}</span>',
                            f'<span class="akshara">{ak.text}</span>',
                            '</div>',
                        ]
                        if item['is_word_end']:
                            parts.append('<div class="word-gap"></div>')
                    parts.append('</div></div>')
                    ak_idx = end
                    if ak_idx >= len(flat):
                        break

                parts.append('</div></div>')
                st.markdown("".join(parts), unsafe_allow_html=True)

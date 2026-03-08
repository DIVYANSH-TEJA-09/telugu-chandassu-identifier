import streamlit as st
import sys, os
sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine
from telugu_chandas.locale import GANA_NAMES_TE, METER_NAMES_TE, METER_TYPE_TE
from telugu_chandas.analyzer import ProsodyAnalyzer
from telugu_chandas.jati_registry import JatiRegistry
from telugu_chandas.jati_segmenter import segment_surya_indra, segment_kandam

st.set_page_config(
    page_title="తెలుగు ఛందస్సు విశ్లేషకం",
    page_icon="📜",
    layout="wide"
)

# ── colour tokens (teal + amber, no purple) ───────────────────────────────────
# primary  : #0f766e  (deep teal)
# primary2 : #0d9488  (teal)
# accent   : #d97706  (amber / gold)
# accent2  : #f59e0b
# bg light : #f0fdfa
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

/* ── reset / base ── */
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.block-container { padding-top: 0 !important; }

/* ── hide default sidebar toggle & header ── */
#MainMenu, footer, header { visibility:hidden; }
section[data-testid="stSidebar"] { display:none; }

/* ── TOP NAVBAR ── */
.navbar {
    display:flex; align-items:center; justify-content:space-between;
    background:#0f766e; padding:0 2.5rem;
    height:58px; position:sticky; top:0; z-index:999;
    box-shadow:0 2px 12px rgba(15,118,110,.25);
}
.nav-brand {
    font-size:1.15rem; font-weight:800; color:white;
    letter-spacing:.01em; display:flex; align-items:center; gap:8px;
}
.nav-brand span { color:#fde68a; }
.nav-links { display:flex; gap:4px; }
.nav-btn {
    background:transparent; border:none; color:rgba(255,255,255,.75);
    padding:8px 18px; border-radius:8px; font-size:.88rem; font-weight:600;
    cursor:pointer; transition:all .18s; white-space:nowrap;
}
.nav-btn:hover  { background:rgba(255,255,255,.12); color:white; }
.nav-btn.active { background:rgba(255,255,255,.18); color:white; }

/* ── hero ── */
.hero { text-align:center; padding:2.8rem 1rem 1.2rem; }
.hero h1 {
    font-size:2.8rem; font-weight:800; margin-bottom:.4rem;
    background:linear-gradient(135deg,#0f766e 0%,#d97706 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero p { color:#64748b; font-size:1rem; margin:0; }

/* ── stat cards ── */
.stat-card {
    background:white; border-radius:12px; padding:18px 16px;
    border:1px solid #ccfbf1; text-align:center;
    box-shadow:0 1px 8px rgba(15,118,110,.08);
}
.stat-num { font-size:2.2rem; font-weight:800; color:#0f766e; line-height:1; }
.stat-lbl { font-size:.73rem; color:#94a3b8; margin-top:5px; font-weight:600;
            text-transform:uppercase; letter-spacing:.06em; }

/* ── feature list ── */
.feat { display:flex; gap:14px; align-items:flex-start;
        padding:13px 0; border-bottom:1px solid #f1f5f9; }
.feat:last-child { border-bottom:none; }
.feat-icon { font-size:1.45rem; flex-shrink:0; margin-top:1px; }
.feat-title { font-weight:700; color:#134e4a; font-size:.93rem; margin-bottom:3px; }
.feat-desc  { color:#64748b; font-size:.81rem; line-height:1.6; }

/* ── result: meter card ── */
.r-card {
    background:linear-gradient(135deg,#0f766e 0%,#065f46 100%);
    border-radius:16px; padding:28px 32px; color:white; margin-bottom:18px;
    box-shadow:0 8px 32px rgba(15,118,110,.25);
}
.r-badge {
    display:inline-block; background:rgba(255,255,255,.18);
    border-radius:999px; padding:3px 14px; font-size:.78rem;
    font-weight:600; margin-bottom:10px; letter-spacing:.04em;
}
.r-name { font-size:2.3rem; font-weight:800; line-height:1.15; margin-bottom:4px; }
.r-eng  { font-size:.95rem; opacity:.65; }
.r-score{ font-size:3rem; font-weight:900; color:#fde68a; line-height:1; margin-top:14px; }
.r-note { font-size:.76rem; opacity:.6; margin-top:6px; }

/* ── validation cards ── */
.v-card {
    border-radius:12px; padding:18px 20px; border-left:4px solid;
    background:white; box-shadow:0 1px 8px rgba(0,0,0,.05);
}
.v-card.ok  { border-color:#0d9488; }
.v-card.no  { border-color:#ef4444; }
.v-card.na  { border-color:#d97706; }
.v-lbl { font-size:.72rem; color:#64748b; margin-bottom:4px; font-weight:700;
         text-transform:uppercase; letter-spacing:.05em; }
.v-val { font-size:1.1rem; font-weight:700; color:#1e293b; }
.v-sub { font-size:.77rem; color:#94a3b8; margin-top:3px; }

/* ── gana strip ── */
.g-strip {
    background:#f0fdfa; border-radius:10px; padding:14px 18px;
    border:1px solid #99f6e4; margin-bottom:16px;
}
.g-lbl { font-size:.72rem; color:#0f766e; font-weight:700;
         text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; }
.g-seq { font-family:'Noto Sans Telugu',sans-serif; font-size:1.4rem;
         font-weight:700; color:#134e4a; letter-spacing:.35rem; }

/* ── yati notes ── */
.y-box {
    background:#fffbeb; border-radius:10px; padding:16px 20px;
    border:1px solid #fde68a; margin-bottom:16px;
}
.y-title { font-weight:700; color:#92400e; font-size:.88rem; margin-bottom:8px; }
.y-row {
    font-family:'Noto Sans Telugu',sans-serif; font-size:.87rem;
    color:#78350f; padding:6px 0; border-bottom:1px solid #fde68a;
}
.y-row:last-child { border-bottom:none; }

/* ── pada breakdown ── */
.pada-box {
    background:white; border-radius:12px; padding:18px 22px;
    margin-bottom:12px; border:1px solid #e2e8f0;
    box-shadow:0 1px 6px rgba(0,0,0,.04);
}
.pada-hdr { font-size:.7rem; color:#94a3b8; text-transform:uppercase;
            letter-spacing:.08em; margin-bottom:12px; }
.pada-line { display:flex; flex-wrap:wrap; gap:3px; align-items:flex-end; }
.g-blk {
    display:flex; flex-direction:column; align-items:center;
    background:#f0fdfa; border-radius:7px; padding:7px 5px 9px;
    margin:0 5px 5px 0; border:1px solid #99f6e4;
}
.g-hdr {
    font-size:.67rem; font-weight:700; color:#0f766e;
    background:#ccfbf1; border-radius:4px; padding:2px 7px; margin-bottom:7px;
}
.g-body { display:flex; gap:1px; }
.ak-box { display:flex; flex-direction:column; align-items:center;
          padding:3px 5px; min-width:28px; }
.wt { font-size:.64rem; font-weight:800; border-radius:3px;
      padding:1px 5px; margin-bottom:3px; }
.wt-U { color:#b45309; background:#fef3c7; }
.wt-I { color:#0f766e; background:#ccfbf1; }
.ak-ch { font-family:'Noto Sans Telugu',sans-serif; font-size:1rem; color:#1e293b; }
.w-gap { width:1px; height:22px; background:#cbd5e1;
         margin:0 5px; align-self:center; }

/* ── unknown ── */
.unk {
    text-align:center; padding:40px 24px; background:#f0fdfa;
    border-radius:14px; border:2px dashed #99f6e4; margin-bottom:16px;
}
.unk h3 { color:#0f766e; margin-bottom:6px; }
.unk p  { color:#94a3b8; font-size:.88rem; margin:0; }

/* ── streamlit tweaks ── */
.stTextArea textarea {
    font-family:'Noto Sans Telugu',sans-serif !important;
    font-size:1.05rem !important; line-height:1.85 !important;
    border-radius:10px !important; border:1.5px solid #99f6e4 !important;
}
.stTextArea textarea:focus {
    border-color:#0f766e !important;
    box-shadow:0 0 0 3px rgba(15,118,110,.12) !important;
}
.stButton > button {
    background:linear-gradient(135deg,#0f766e,#0d9488) !important;
    color:white !important; border:none !important;
    border-radius:10px !important; padding:12px 36px !important;
    font-size:.95rem !important; font-weight:700 !important;
    transition:all .2s !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(15,118,110,.35) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:#0f766e !important; border-bottom-color:#0f766e !important;
}
div[data-testid="stProgress"] > div > div {
    background:linear-gradient(90deg,#0f766e,#d97706) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def get_line_ganas(w_str, meter_name, pada_idx):
    m = JatiRegistry.get(meter_name)
    if m and pada_idx < len(m.pada_structures):
        seg = (segment_surya_indra(w_str, m.pada_structures[pada_idx])
               if m.segmentation_type == "surya_indra"
               else segment_kandam(w_str))
        if seg:
            return [(name, len(pat)) for name, pat in seg]
    out = []
    for g in ProsodyAnalyzer.get_ganas(w_str):
        sz = 2 if g in ("GaGa","GaLa","LaLa","Va") else (1 if g in ("Ga","La") else 3)
        out.append((GANA_NAMES_TE.get(g, g), sz))
    return out


@st.cache_resource
def get_engine():
    return ChandasEngine()

engine = get_engine()


# ── session state ─────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "analyzer"


# ── navbar ────────────────────────────────────────────────────────────────────

a_cls = "nav-btn active" if st.session_state.page == "analyzer" else "nav-btn"
l_cls = "nav-btn active" if st.session_state.page == "learning" else "nav-btn"

st.markdown(f"""
<div class="navbar">
    <div class="nav-brand">📜 తెలుగు <span>ఛందస్సు విశ్లేషకం</span></div>
    <div class="nav-links" id="navlinks"></div>
</div>
""", unsafe_allow_html=True)

# real clickable nav using columns (overlay on top of visual navbar)
_, nc1, nc2, _ = st.columns([6, 1.2, 1.6, 0.5])
with nc1:
    if st.button("Analyzer", key="nav_a",
                 type="primary" if st.session_state.page == "analyzer" else "secondary",
                 use_container_width=True):
        st.session_state.page = "analyzer"
        st.rerun()
with nc2:
    if st.button("Learning Resources", key="nav_l",
                 type="primary" if st.session_state.page == "learning" else "secondary",
                 use_container_width=True):
        st.session_state.page = "learning"
        st.rerun()

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ── learning page ─────────────────────────────────────────────────────────────

if st.session_state.page == "learning":
    from telugu_chandas.learning_materials import render_learning_section
    render_learning_section()
    st.stop()


# ── analyzer page ─────────────────────────────────────────────────────────────

# hero
st.markdown("""
<div class="hero">
    <h1>తెలుగు ఛందస్సు విశ్లేషకం</h1>
    <p>Rule-based Telugu prosody engine — identify Vritta, Jati &amp; Upajati padyam with full gana breakdown</p>
</div>
""", unsafe_allow_html=True)

# stat row
for col, num, lbl in zip(
    st.columns(4),
    ["10",  "4",       "3",     "3"],
    ["Meters", "Vritta", "Jati", "Upajati"],
):
    col.markdown(
        f'<div class="stat-card"><div class="stat-num">{num}</div>'
        f'<div class="stat-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

# input
text_input = st.text_area(
    "పద్యం నమోదు చేయండి",
    value=(
        "భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-\n"
        "భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-\n"
        "రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-\n"
        "నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"
    ),
    height=160,
    placeholder="ఇక్కడ పద్యం నమోదు చేయండి...",
    label_visibility="collapsed",
)
analyze = st.button("విశ్లేషించు (Analyze)", type="primary")

st.divider()

# ── capabilities (before analysis) ───────────────────────────────────────────
if not analyze:

    st.markdown("### What this tool does")
    fa, fb = st.columns(2)

    with fa:
        st.markdown("""
<div class="feat"><div class="feat-icon">⚖️</div><div>
<div class="feat-title">Laghu · Guru Classification</div>
<div class="feat-desc">Every akshara classified as లఘువు (I) or గురువు (U) — intrinsic length, positional guru, pollu, sunna, visarga, wall &amp; hyphen rules all applied.</div>
</div></div>

<div class="feat"><div class="feat-icon">📜</div><div>
<div class="feat-title">10 Meters Identified</div>
<div class="feat-desc">Covers Vritta (syllabic), Jati (matra-based), and Upajati padyam. Auto retry handles missing hyphens at line ends.</div>
</div></div>

<div class="feat"><div class="feat-icon">📊</div><div>
<div class="feat-title">Confidence Score</div>
<div class="feat-desc">0–100% score split into Gana (60%), Yati (20%), Prasa (20%). Both Vritta and Jati identifiers run — higher score wins.</div>
</div></div>
        """, unsafe_allow_html=True)

    with fb:
        st.markdown("""
<div class="feat"><div class="feat-icon">🔍</div><div>
<div class="feat-title">Gana-by-Gana Breakdown</div>
<div class="feat-desc">Every pada visualised akshara-by-akshara, grouped into ganas with U/I labels and word boundaries marked.</div>
</div></div>

<div class="feat"><div class="feat-icon">🎯</div><div>
<div class="feat-title">Yati &amp; Prasa Validation</div>
<div class="feat-desc">Checks యతి మైత్రి and ప్రాస with per-pada detail. Prasa-Yati alternative checked for Upajati meters.</div>
</div></div>

<div class="feat"><div class="feat-icon">🔗</div><div>
<div class="feat-title">Wall &amp; Hyphen Rules</div>
<div class="feat-desc">Samyukta guru blocked at word boundaries. Hyphens break the wall. Missing-hyphen retry runs automatically when confidence is low.</div>
</div></div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### Supported Meters")

    t1, t2, t3 = st.tabs(["📜 వృత్తం · Vritta", "🎵 జాతి · Jati", "🎶 ఉపజాతి · Upajati"])

    with t1:
        st.caption("Syllabic meters — 3-akshara ganas (Ma Ya Ra Sa Ta Ja Bha Na)")
        st.markdown("---")
        for name_te, name_en, ganas, yati in [
            ("ఉత్పలమాల", "Utpalamala",   "Bha · Ra · Na · Bha · Bha · Ra · Va", "10th akshara"),
            ("చంపకమాల",  "Champakamala", "Na · Ja · Bha · Ja · Ja · Ja · Ra",  "11th akshara"),
            ("శార్దూలము", "Shardulam",    "Ma · Sa · Ja · Sa · Ta · Ta · Ga",   "13th akshara"),
            ("మత్తేభము",  "Mattebham",    "Sa · Bha · Ra · Na · Ma · Ya · Va",  "14th akshara"),
        ]:
            c1, c2, c3 = st.columns([1.5, 3, 1.2])
            c1.markdown(f"**{name_te}**  \n`{name_en}`")
            c2.markdown(f"<small style='color:#64748b'>{ganas}</small>", unsafe_allow_html=True)
            c3.markdown(f"<small style='color:#0f766e'>Yati @ {yati}</small>", unsafe_allow_html=True)

    with t2:
        st.caption("Matra-based — Surya (S) / Indra (I) ganas · **Prasa required**")
        st.markdown("---")
        for name_te, name_en, struct, note in [
            ("ద్విపద", "Dwipada",  "3 Indra + 1 Surya per pada",         "2 padas · Yati @ G3"),
            ("తరువోజ", "Taruvoja", "(3 Indra + 1 Surya) × 2 per pada",   "4 padas · Yati @ G3, G5, G7"),
            ("కందం",   "Kandam",   "Odd: 3 K-ganas · Even: 5 K-ganas",  "4 padas · Cross-pada Yati"),
        ]:
            c1, c2, c3 = st.columns([1.5, 2.5, 1.8])
            c1.markdown(f"**{name_te}**  \n`{name_en}`")
            c2.markdown(f"<small style='color:#64748b'>{struct}</small>", unsafe_allow_html=True)
            c3.markdown(f"<small style='color:#0f766e'>{note}</small>", unsafe_allow_html=True)

    with t3:
        st.caption("Matra-based — **no Prasa** · Prasa-Yati (ప్రాసయతి) allowed")
        st.markdown("---")
        for name_te, name_en, struct, note in [
            ("ఆటవెలది", "Ataveladi", "Odd: 3I+2S · Even: 5S",  "4 padas · Yati @ G4"),
            ("తేటగీతి",  "Tetagiti",  "1S + 2I + 2S per pada", "4 padas · Yati @ G4"),
            ("సీసం",     "Sisam",     "6I + 2S per pada",       "4 padas · Yati @ G3, G5, G7"),
        ]:
            c1, c2, c3 = st.columns([1.5, 2.5, 1.8])
            c1.markdown(f"**{name_te}**  \n`{name_en}`")
            c2.markdown(f"<small style='color:#64748b'>{struct}</small>", unsafe_allow_html=True)
            c3.markdown(f"<small style='color:#0f766e'>{note}</small>", unsafe_allow_html=True)


# ── results ───────────────────────────────────────────────────────────────────
if analyze:
    if not text_input.strip():
        st.warning("దయచేసి పద్యాన్ని నమోదు చేయండి.")
        st.stop()

    with st.spinner("విశ్లేషిస్తున్నాము..."):
        result = engine.identify_meter(text_input)

    if result.meter_name != "Unknown":
        meter_te   = METER_NAMES_TE.get(result.meter_name, result.meter_name)
        meter_type = METER_TYPE_TE.get(result.meter_name, "పద్యం")
        score      = result.confidence_score
        breakdown  = result.notes[0] if result.notes else ""

        st.markdown(f"""
<div class="r-card">
    <div class="r-badge">{meter_type}</div>
    <div class="r-name">{meter_te}</div>
    <div class="r-eng">{result.meter_name}</div>
    <div class="r-score">{score:.0f}%</div>
    <div class="r-note">{breakdown}</div>
</div>""", unsafe_allow_html=True)

        st.progress(int(score) / 100)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # validation
        v1, v2 = st.columns(2)
        yati_cls  = "ok" if result.yati_valid else "no"
        prasa_na  = "వర్తించదు" in result.prasa_note
        prasa_cls = "ok" if result.prasa_valid else ("na" if prasa_na else "no")
        yati_val  = "✓ చెల్లింది" if result.yati_valid else "✗ చెల్లలేదు"
        prasa_val = "✓ చెల్లింది" if result.prasa_valid else ("— వర్తించదు" if prasa_na else "✗ చెల్లలేదు")

        v1.markdown(f"""<div class="v-card {yati_cls}">
<div class="v-lbl">యతి · Yati</div>
<div class="v-val">{yati_val}</div>
<div class="v-sub">పాద మైత్రి తనిఖీ</div>
</div>""", unsafe_allow_html=True)

        v2.markdown(f"""<div class="v-card {prasa_cls}">
<div class="v-lbl">ప్రాస · Prasa</div>
<div class="v-val">{prasa_val}</div>
<div class="v-sub">హల్లు: {result.prasa_note or '—'}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        for note in result.notes[1:]:
            if note:
                st.info(note)

        # gana sequence
        ganas_te = [GANA_NAMES_TE.get(g, g) for g in result.ganas_found]
        st.markdown(f"""<div class="g-strip">
<div class="g-lbl">గణ విభజన · Gana Sequence (first pada)</div>
<div class="g-seq">{' '.join(ganas_te)}</div>
</div>""", unsafe_allow_html=True)

        # yati detail
        if result.yati_notes:
            rows = "".join(f'<div class="y-row">{n}</div>' for n in result.yati_notes)
            st.markdown(f"""<div class="y-box">
<div class="y-title">యతి మైత్రి వివరాలు · Per-Pada Yati Detail</div>
{rows}
</div>""", unsafe_allow_html=True)

    else:
        st.markdown("""<div class="unk">
<h3>🔎 గుర్తించబడని పద్యం</h3>
<p>No matching meter found. Ensure the poem is in Telugu and follows a standard chandas.</p>
</div>""", unsafe_allow_html=True)

    # line breakdown
    st.divider()
    st.markdown("### పాద విశ్లేషణ · Line-by-Line Breakdown")

    tokens = engine.analyze(text_input)
    lines_of_tokens, cur = [], []
    for tok in tokens:
        if not tok.is_word and '\n' in tok.text:
            if cur:
                lines_of_tokens.append(cur)
                cur = []
        else:
            cur.append(tok)
    if cur:
        lines_of_tokens.append(cur)

    for li, line_tokens in enumerate(lines_of_tokens):
        flat = []
        for tok in line_tokens:
            if tok.is_word:
                n = len(tok.aksharas)
                for i, ak in enumerate(tok.aksharas):
                    flat.append({"ak": ak, "we": i == n - 1})

        w_str = "".join(f["ak"].weight.value for f in flat if f["ak"].weight)
        ganas = get_line_ganas(w_str, result.meter_name, li)

        parts = [
            '<div class="pada-box">',
            f'<div class="pada-hdr">పాదం {li+1} &nbsp;·&nbsp; {len(flat)} అక్షరాలు &nbsp;·&nbsp; <code>{w_str}</code></div>',
            '<div class="pada-line">',
        ]
        ai = 0
        for gname, gsz in ganas:
            chunk = flat[ai: ai + gsz]
            parts += ['<div class="g-blk">',
                      f'<div class="g-hdr">{gname}</div>',
                      '<div class="g-body">']
            for f in chunk:
                ak = f["ak"]
                wv = ak.weight.value if ak.weight else "?"
                parts += [
                    '<div class="ak-box">',
                    f'<span class="wt wt-{wv}">{wv}</span>',
                    f'<span class="ak-ch">{ak.text}</span>',
                    '</div>',
                ]
                if f["we"]:
                    parts.append('<div class="w-gap"></div>')
            parts.append('</div></div>')
            ai += gsz
            if ai >= len(flat):
                break
        parts.append('</div></div>')
        st.markdown("".join(parts), unsafe_allow_html=True)

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

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&family=Inter:wght@400;600;700&display=swap');

/* base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* hero */
.hero { text-align:center; padding: 2.5rem 0 1rem; }
.hero h1 {
    font-size: 3rem; font-weight: 800; margin-bottom: .3rem;
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero p { color:#64748b; font-size:1.05rem; margin:0; }

/* stat cards */
.stat-card {
    background:white; border-radius:12px; padding:16px 20px;
    border:1px solid #e2e8f0; text-align:center;
    box-shadow:0 1px 8px rgba(79,70,229,.07);
}
.stat-num { font-size:2rem; font-weight:800; color:#4f46e5; line-height:1; }
.stat-lbl { font-size:.78rem; color:#94a3b8; margin-top:4px; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }

/* feature rows */
.feat { display:flex; gap:14px; align-items:flex-start; padding:12px 0; border-bottom:1px solid #f1f5f9; }
.feat:last-child { border-bottom:none; }
.feat-icon { font-size:1.5rem; flex-shrink:0; }
.feat-title { font-weight:700; color:#1e293b; font-size:.95rem; margin-bottom:2px; }
.feat-desc  { color:#64748b; font-size:.82rem; line-height:1.55; }

/* meter chip */
.m-chip {
    display:inline-block; background:#f8fafc; border:1px solid #e2e8f0;
    border-radius:8px; padding:7px 14px; margin:4px;
    font-family:'Noto Sans Telugu',sans-serif; font-size:.9rem; color:#334155;
}
.m-chip small { display:block; font-size:.7rem; color:#94a3b8; font-family:Inter,sans-serif; }

/* result: meter card */
.r-card {
    background:linear-gradient(135deg,#4f46e5,#7c3aed);
    border-radius:16px; padding:28px 32px; color:white; margin-bottom:18px;
}
.r-badge {
    display:inline-block; background:rgba(255,255,255,.2);
    border-radius:999px; padding:3px 14px; font-size:.8rem; margin-bottom:10px;
}
.r-name { font-size:2.4rem; font-weight:800; line-height:1.1; margin-bottom:6px; }
.r-eng  { font-size:1rem; opacity:.7; }
.r-score{ font-size:3rem; font-weight:900; line-height:1; margin-top:12px; }
.r-note { font-size:.78rem; opacity:.65; margin-top:6px; }

/* val card */
.v-card {
    border-radius:12px; padding:16px 20px;
    border-left:4px solid; background:white;
    box-shadow:0 1px 8px rgba(0,0,0,.06);
}
.v-card.ok  { border-color:#10b981; }
.v-card.no  { border-color:#ef4444; }
.v-card.na  { border-color:#94a3b8; }
.v-lbl { font-size:.75rem; color:#64748b; margin-bottom:3px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
.v-val { font-size:1.1rem; font-weight:700; color:#1e293b; }
.v-sub { font-size:.78rem; color:#94a3b8; margin-top:2px; }

/* gana strip */
.g-strip {
    background:#f8fafc; border-radius:10px; padding:14px 18px;
    border:1px solid #e2e8f0; margin-bottom:16px;
}
.g-lbl { font-size:.75rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; }
.g-seq { font-family:'Noto Sans Telugu',sans-serif; font-size:1.4rem; font-weight:700; color:#1e293b; letter-spacing:.35rem; }

/* yati section */
.y-box {
    background:#fffbeb; border-radius:10px; padding:16px 20px;
    border:1px solid #fde68a; margin-bottom:16px;
}
.y-title { font-weight:700; color:#92400e; font-size:.9rem; margin-bottom:8px; }
.y-row {
    font-family:'Noto Sans Telugu',sans-serif; font-size:.88rem;
    color:#78350f; padding:6px 0; border-bottom:1px solid #fde68a;
}
.y-row:last-child { border-bottom:none; }

/* pada breakdown */
.pada-box {
    background:white; border-radius:12px; padding:18px 22px;
    margin-bottom:12px; border:1px solid #f1f5f9;
    box-shadow:0 1px 8px rgba(0,0,0,.04);
}
.pada-hdr { font-size:.72rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.08em; margin-bottom:12px; }
.pada-line { display:flex; flex-wrap:wrap; gap:3px; align-items:flex-end; }
.g-blk {
    display:flex; flex-direction:column; align-items:center;
    background:#fafafa; border-radius:7px; padding:7px 5px 9px;
    margin:0 5px 5px 0; border:1px solid #f0f0f0;
}
.g-hdr {
    font-size:.68rem; font-weight:700; color:#4f46e5;
    background:#eef2ff; border-radius:4px; padding:2px 7px; margin-bottom:7px;
}
.g-body { display:flex; gap:1px; }
.ak-box { display:flex; flex-direction:column; align-items:center; padding:3px 5px; min-width:28px; }
.wt {
    font-size:.65rem; font-weight:800; border-radius:3px;
    padding:1px 5px; margin-bottom:3px;
}
.wt-U { color:#dc2626; background:#fef2f2; }
.wt-I { color:#16a34a; background:#f0fdf4; }
.ak-ch { font-family:'Noto Sans Telugu',sans-serif; font-size:1rem; color:#1e293b; }
.w-gap { width:1px; height:22px; background:#cbd5e1; margin:0 5px; align-self:center; }

/* unknown */
.unk {
    text-align:center; padding:40px 24px; background:#f8fafc;
    border-radius:14px; border:2px dashed #cbd5e1; margin-bottom:16px;
}
.unk h3 { color:#475569; margin-bottom:6px; }
.unk p  { color:#94a3b8; font-size:.88rem; margin:0; }

/* sidebar */
section[data-testid="stSidebar"] { background:#fafbff; }
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


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📜 ఛందస్సు విశ్లేషకం")
    st.caption("Telugu Chandas Identifier")
    st.divider()

    app_mode = st.radio(
        "Mode", ["Analyzer", "Learning Resources"], label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**Supported Meters**")

    st.markdown("*వృత్తం (Vritta)*")
    for m in ["ఉత్పలమాల","చంపకమాల","శార్దూలము","మత్తేభము"]:
        st.markdown(f"&nbsp;&nbsp;· {m}")

    st.markdown("*జాతి (Jati)*")
    for m in ["ద్విపద","తరువోజ","కందం"]:
        st.markdown(f"&nbsp;&nbsp;· {m}")

    st.markdown("*ఉపజాతి (Upajati)*")
    for m in ["ఆటవెలది","తేటగీతి","సీసం"]:
        st.markdown(f"&nbsp;&nbsp;· {m}")

    st.divider()
    with st.expander("Key Rules"):
        st.markdown("""
**లఘువు (I)** — short vowel
**గురువు (U)** — long vowel, diphthong, sunna, visarga, pollu
**Positional Guru** — laghu before a conjunct (same word) → guru
**Wall rule** — samyukta effect blocked at word boundaries
**యతి** — vowel harmony at fixed gana position
**ప్రాస** — 2nd akshara onset consonant matches across all padas
        """)


# ── learning mode ─────────────────────────────────────────────────────────────

if app_mode == "Learning Resources":
    from telugu_chandas.learning_materials import render_learning_section
    render_learning_section()

# ── analyzer mode ─────────────────────────────────────────────────────────────
else:

    # hero
    st.markdown("""
    <div class="hero">
        <h1>తెలుగు ఛందస్సు విశ్లేషకం</h1>
        <p>Rule-based Telugu prosody engine — identify Vritta, Jati &amp; Upajati padyam with full gana breakdown</p>
    </div>
    """, unsafe_allow_html=True)

    # stat row
    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl in [
        (c1, "10", "Meters Supported"),
        (c2, "4",  "Vritta"),
        (c3, "3",  "Jati"),
        (c4, "3",  "Upajati"),
    ]:
        col.markdown(
            f'<div class="stat-card"><div class="stat-num">{num}</div>'
            f'<div class="stat-lbl">{lbl}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

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
    )
    analyze = st.button("విశ్లేషించు (Analyze)", type="primary")

    st.divider()

    # ── capabilities (shown before analysis) ──────────────────────────────────
    if not analyze:

        # features
        st.markdown("### What this tool does")
        fa, fb = st.columns(2)

        with fa:
            st.markdown("""
<div class="feat"><div class="feat-icon">⚖️</div><div>
<div class="feat-title">Laghu · Guru Classification</div>
<div class="feat-desc">Every akshara classified as లఘువు (I) or గురువు (U) using full textbook rules — intrinsic length, positional guru, pollu, sunna, visarga, wall &amp; hyphen rules.</div>
</div></div>

<div class="feat"><div class="feat-icon">📜</div><div>
<div class="feat-title">10 Meters Identified</div>
<div class="feat-desc">Covers Vritta (syllabic), Jati (matra-based), and Upajati padyam. Automatic retry pass handles missing hyphens at line ends.</div>
</div></div>

<div class="feat"><div class="feat-icon">📊</div><div>
<div class="feat-title">Confidence Score</div>
<div class="feat-desc">0–100% score split into Gana (60%), Yati (20%), and Prasa (20%). Both Vritta and Jati identifiers run; the higher score wins.</div>
</div></div>
            """, unsafe_allow_html=True)

        with fb:
            st.markdown("""
<div class="feat"><div class="feat-icon">🔍</div><div>
<div class="feat-title">Gana-by-Gana Breakdown</div>
<div class="feat-desc">Every pada visualised akshara-by-akshara, grouped into ganas (Vritta / Surya-Indra / Kandam) with U/I labels and word boundaries marked.</div>
</div></div>

<div class="feat"><div class="feat-icon">🎯</div><div>
<div class="feat-title">Yati &amp; Prasa Validation</div>
<div class="feat-desc">Checks యతి మైత్రి (vowel harmony) and ప్రాస (matching onset consonant) with per-pada detail. Prasa-Yati alternative checked for Upajati meters.</div>
</div></div>

<div class="feat"><div class="feat-icon">🔗</div><div>
<div class="feat-title">Wall &amp; Hyphen Rules</div>
<div class="feat-desc">Samyukta guru is blocked at word boundaries (wall rule). Hyphens break the wall. Missing-hyphen retry runs automatically when confidence is low.</div>
</div></div>
            """, unsafe_allow_html=True)

        st.divider()

        # meters reference
        st.markdown("### Supported Meters")
        t1, t2, t3 = st.tabs(["వృత్తం · Vritta", "జాతి · Jati", "ఉపజాతి · Upajati"])

        with t1:
            st.markdown("Syllabic meters — 3-akshara ganas (Ma Ya Ra Sa Ta Ja Bha Na)")
            for name_te, name_en, ganas, yati in [
                ("ఉత్పలమాల", "Utpalamala",  "Bha Ra Na Bha Bha Ra Va", "10"),
                ("చంపకమాల",  "Champakamala","Na Ja Bha Ja Ja Ja Ra",   "11"),
                ("శార్దూలము", "Shardulam",   "Ma Sa Ja Sa Ta Ta Ga",    "13"),
                ("మత్తేభము",  "Mattebham",   "Sa Bha Ra Na Ma Ya Va",   "14"),
            ]:
                a, b, c = st.columns([1.2, 2, 1])
                a.markdown(f"**{name_te}**  \n*{name_en}*")
                b.markdown(f"`{ganas}`")
                c.markdown(f"Yati @ {yati}")

        with t2:
            st.markdown("Matra-based meters with Surya/Indra ganas — **Prasa required**")
            for name_te, name_en, struct in [
                ("ద్విపద",  "Dwipada",  "2 padas · 3 Indra + 1 Surya each"),
                ("తరువోజ",  "Taruvoja", "4 padas · (3 Indra + 1 Surya) × 2 each"),
                ("కందం",    "Kandam",   "4 padas · Odd: 3 K-ganas · Even: 5 K-ganas"),
            ]:
                a, b = st.columns([1.2, 3])
                a.markdown(f"**{name_te}**  \n*{name_en}*")
                b.markdown(struct)

        with t3:
            st.markdown("Matra-based meters — **no Prasa** (Prasa-Yati allowed)")
            for name_te, name_en, struct in [
                ("ఆటవెలది", "Ataveladi", "4 padas · Odd: 3I+2S · Even: 5S"),
                ("తేటగీతి",  "Tetagiti",  "4 padas · 1S+2I+2S each"),
                ("సీసం",     "Sisam",     "4 padas · 6I+2S each"),
            ]:
                a, b = st.columns([1.2, 3])
                a.markdown(f"**{name_te}**  \n*{name_en}*")
                b.markdown(struct)

    # ── analysis results ──────────────────────────────────────────────────────
    if analyze:
        if not text_input.strip():
            st.warning("దయచేసి పద్యాన్ని నమోదు చేయండి.")
        else:
            with st.spinner("విశ్లేషిస్తున్నాము..."):
                result = engine.identify_meter(text_input)

            if result.meter_name != "Unknown":
                meter_te   = METER_NAMES_TE.get(result.meter_name, result.meter_name)
                meter_type = METER_TYPE_TE.get(result.meter_name, "పద్యం")
                score      = result.confidence_score
                breakdown  = result.notes[0] if result.notes else ""

                # meter card
                st.markdown(f"""
<div class="r-card">
    <div class="r-badge">{meter_type}</div>
    <div class="r-name">{meter_te}</div>
    <div class="r-eng">{result.meter_name}</div>
    <div class="r-score">{score:.0f}%</div>
    <div class="r-note">{breakdown}</div>
</div>""", unsafe_allow_html=True)

                # confidence bar
                st.progress(int(score) / 100)

                # validation
                v1, v2 = st.columns(2)
                yati_cls  = "ok" if result.yati_valid  else "no"
                prasa_cls = "ok" if result.prasa_valid else ("na" if "వర్తించదు" in result.prasa_note else "no")
                yati_val  = "✓ చెల్లింది" if result.yati_valid  else "✗ చెల్లలేదు"
                prasa_val = "✓ చెల్లింది" if result.prasa_valid else ("— వర్తించదు" if "వర్తించదు" in result.prasa_note else "✗ చెల్లలేదు")
                prasa_sub = result.prasa_note if result.prasa_note else "—"

                v1.markdown(f"""<div class="v-card {yati_cls}">
<div class="v-lbl">యతి · Yati</div>
<div class="v-val">{yati_val}</div>
<div class="v-sub">పాద మైత్రి తనిఖీ</div>
</div>""", unsafe_allow_html=True)

                v2.markdown(f"""<div class="v-card {prasa_cls}">
<div class="v-lbl">ప్రాస · Prasa</div>
<div class="v-val">{prasa_val}</div>
<div class="v-sub">హల్లు: {prasa_sub}</div>
</div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                # extra engine notes (hyphen retry etc.)
                for note in result.notes[1:]:
                    if note:
                        st.info(note)

                # gana sequence
                ganas_te = [GANA_NAMES_TE.get(g, g) for g in result.ganas_found]
                st.markdown(f"""<div class="g-strip">
<div class="g-lbl">గణ విభజన · Gana Sequence (first pada)</div>
<div class="g-seq">{' '.join(ganas_te)}</div>
</div>""", unsafe_allow_html=True)

                # yati notes
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

            # ── line-by-line breakdown ─────────────────────────────────────
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
                        ak   = f["ak"]
                        wv   = ak.weight.value if ak.weight else "?"
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

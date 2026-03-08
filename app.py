import streamlit as st
import sys
import os

# Add current directory to path so we can import our package
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

# Premium CSS Design
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Suravaram&display=swap');
    
    /* Global Typography */
    .main-title {
        font-family: 'Suravaram', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Suravaram', serif !important;
    }
    
    .subtitle {
        font-family: 'Suravaram', serif;
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Meter Result Card */
    .meter-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .meter-name {
        font-family: 'Suravaram', serif;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .meter-type {
        font-family: 'Suravaram', serif;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Validation Badges */
    .validation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .validation-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid;
    }
    
    .validation-card.valid { border-left-color: #10b981; }
    .validation-card.invalid { border-left-color: #ef4444; }
    
    .validation-title {
        font-family: 'Suravaram', serif;
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 4px;
    }
    
    .validation-value {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    .validation-detail {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.8rem;
        color: #888;
        margin-top: 4px;
    }
    
    /* Gana Sequence Display */
    .gana-sequence {
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
    }
    
    .gana-sequence-title {
        font-family: 'Suravaram', serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 8px;
    }
    
    .gana-sequence-content {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #334155;
        letter-spacing: 0.5rem;
    }
    
    /* Padyam Line Visualization */
    .padyam-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #f1f5f9;
    }
    
    .line-number {
        font-family: 'Suravaram', serif;
        font-size: 0.75rem;
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
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid #f0f0f0;
    }
    
    .gana-header {
        font-family: 'Suravaram', serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: #667eea;
        padding: 2px 8px;
        background: #eef2ff;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    
    .gana-content {
        display: flex;
        flex-direction: row;
        gap: 2px;
    }
    
    .akshara-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 4px 6px;
        min-width: 32px;
    }
    
    .weight {
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        margin-bottom: 4px;
    }
    
    .weight-U {
        color: #dc2626;
        background: #fef2f2;
    }
    
    .weight-I {
        color: #16a34a;
        background: #f0fdf4;
    }
    
    .akshara {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: #1e293b;
    }
    
    .word-gap {
        width: 1px;
        height: 24px;
        background-color: #cbd5e1;
        margin: 0 8px;
        align-self: center;
    }
    
    /* Yati Notes Section */
    .yati-section {
        background: #fffbeb;
        border-radius: 12px;
        padding: 20px;
        margin-top: 24px;
        border: 1px solid #fde68a;
    }
    
    .yati-title {
        font-family: 'Suravaram', serif;
        font-size: 1rem;
        font-weight: 600;
        color: #92400e;
        margin-bottom: 12px;
    }
    
    .yati-item {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-size: 0.9rem;
        color: #78350f;
        padding: 8px 0;
        border-bottom: 1px solid #fde68a;
    }
    
    .yati-item:last-child {
        border-bottom: none;
    }
    
    /* Input Area Styling */
    .stTextArea textarea {
        font-family: 'Noto Sans Telugu', sans-serif !important;
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 16px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 32px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def get_line_ganas(w_str: str, meter_name: str, pada_idx: int):
    """
    Returns a list of (gana_name_te, chunk_size) for rendering the line breakdown.
    Uses Jati segmentation for Jati/Upajati meters, Vritta for everything else.
    Falls back to Vritta if Jati segmentation fails.
    """
    jati_meter = JatiRegistry.get(meter_name)
    if jati_meter is not None and pada_idx < len(jati_meter.pada_structures):
        structure = jati_meter.pada_structures[pada_idx]
        if jati_meter.segmentation_type == "surya_indra":
            seg = segment_surya_indra(w_str, structure)
        else:
            seg = segment_kandam(w_str)
        if seg:
            return [(name, len(pattern)) for name, pattern in seg]

    # Vritta fallback
    result = []
    for g in ProsodyAnalyzer.get_ganas(w_str):
        if g in ("GaGa", "GaLa", "LaLa", "Va"):
            size = 2
        elif g in ("Ga", "La"):
            size = 1
        else:
            size = 3
        result.append((GANA_NAMES_TE.get(g, g), size))
    return result


# Initialize Engine
@st.cache_resource
def get_engine():
    return ChandasEngine()

engine = get_engine()

# Navigation
st.sidebar.markdown('### Navigation')
app_mode = st.sidebar.selectbox("ఎంచుకోండి (Select Mode):", ["ఛందస్సు విశ్లేషణ (Analyzer)", "సమాచారం (Learning Resources)"])

if app_mode == "సమాచారం (Learning Resources)":
    from telugu_chandas.learning_materials import render_learning_section
    render_learning_section()
    
else:
    # Title
    st.markdown('<h1 class="main-title">📜 తెలుగు ఛందస్సు విశ్లేషకం</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Telugu Chandas Identifier - Analyze Laghu, Guru weights and identify Vritta meters</p>', unsafe_allow_html=True)

    # Input
    # Input
    text_input = st.text_area(
        "పద్యం నమోదు చేయండి (Enter Telugu Padyam):", 
        value="భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-\nభవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-\nరవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-\nనివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!", 
        height=180
    )

    if st.button("విశ్లేషించు (Analyze)", type="primary"):
        if not text_input.strip():
            st.warning("దయచేసి పద్యాన్ని నమోదు చేయండి.")
        else:
            # 1. Meter Identification
            id_result = engine.identify_meter(text_input)
            
            if id_result.meter_name != "Unknown":
                meter_te = METER_NAMES_TE.get(id_result.meter_name, id_result.meter_name)
                
                # Breakdown
                breakdown = id_result.notes[0] if id_result.notes else ""

                # Meter Card
                meter_type_te = METER_TYPE_TE.get(id_result.meter_name, "పద్యం")
                st.markdown(f'''
                <div class="meter-card">
                    <div class="meter-name">{meter_te}</div>
                    <div class="meter-type">{meter_type_te} • {id_result.meter_name} • Confidence: {id_result.confidence}</div>
                    <div style="font-size: 0.8rem; margin-top: 8px; color: rgba(255,255,255,0.8); font-family: 'Suravaram', serif;">{breakdown}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Validation Cards
                yati_status = "valid" if id_result.yati_valid else "invalid"
                prasa_status = "valid" if id_result.prasa_valid else "invalid"
                yati_text = "చెల్లింది ✓" if id_result.yati_valid else "చెల్లలేదు ✗"
                prasa_text = "చెల్లింది ✓" if id_result.prasa_valid else "చెల్లలేదు ✗"
                
                st.markdown(f'''
                <div class="validation-grid">
                    <div class="validation-card {yati_status}">
                        <div class="validation-title">యతి (Yati)</div>
                        <div class="validation-value">{yati_text}</div>
                    </div>
                    <div class="validation-card {prasa_status}">
                        <div class="validation-title">ప్రాస (Prasa)</div>
                        <div class="validation-value">{prasa_text}</div>
                        <div class="validation-detail">హల్లు: {id_result.prasa_note}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Gana Sequence
                ganas_te = [GANA_NAMES_TE.get(g, g) for g in id_result.ganas_found]
                st.markdown(f'''
                <div class="gana-sequence">
                    <div class="gana-sequence-title">గణ విభజన (Gana Sequence)</div>
                    <div class="gana-sequence-content">{' '.join(ganas_te)}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Yati Notes
                if id_result.yati_notes:
                    yati_items = "".join([f'<div class="yati-item">{note}</div>' for note in id_result.yati_notes])
                    st.markdown(f'''
                    <div class="yati-section">
                        <div class="yati-title">యతి మైత్రి వివరాలు</div>
                        {yati_items}
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info(f"గుర్తించబడని వృత్తం (Unknown Meter)")
            
            st.divider()
            st.markdown("### పాద విశ్లేషణ (Line-by-Line Breakdown)")
            
            # Analyze FULL text
            tokens = engine.analyze(text_input)
            
            # Group tokens by line
            lines_of_tokens = []
            current_line_tokens = []
            
            for token in tokens:
                if not token.is_word and '\n' in token.text:
                    if current_line_tokens:
                        lines_of_tokens.append(current_line_tokens)
                        current_line_tokens = []
                else:
                    current_line_tokens.append(token)
            
            if current_line_tokens:
                lines_of_tokens.append(current_line_tokens)
            
            # Display each line
            for line_idx, line_tokens in enumerate(lines_of_tokens):

                # Flatten aksharas
                flattened_aksharas = []
                for token in line_tokens:
                    if token.is_word:
                        n_ak = len(token.aksharas)
                        for idx, ak in enumerate(token.aksharas):
                            is_word_end = (idx == n_ak - 1)
                            flattened_aksharas.append({
                                'akshara': ak,
                                'is_word_end': is_word_end
                            })

                # Get Ganas (Jati-aware)
                full_w_str = "".join([item['akshara'].weight.value for item in flattened_aksharas if item['akshara'].weight])
                ganas_in_line = get_line_ganas(full_w_str, id_result.meter_name, line_idx)

                # Build HTML
                html_parts = []
                html_parts.append(f'<div class="padyam-container">')
                html_parts.append(f'<div class="line-number">పాదం {line_idx + 1}</div>')
                html_parts.append('<div class="padyam-line">')

                current_ak_idx = 0

                for gana_name_te, chunk_size in ganas_in_line:
                    end_idx = min(current_ak_idx + chunk_size, len(flattened_aksharas))
                    chunk_items = flattened_aksharas[current_ak_idx:end_idx]
                    
                    html_parts.append(f'<div class="gana-block">')
                    html_parts.append(f'<div class="gana-header">{gana_name_te}</div>')
                    html_parts.append('<div class="gana-content">')
                    
                    for item in chunk_items:
                        ak = item['akshara']
                        w_val = ak.weight.value if ak.weight else "?"
                        w_class = f"weight-{w_val}"
                        
                        html_parts.append(f'<div class="akshara-box">')
                        html_parts.append(f'<span class="weight {w_class}">{w_val}</span>')
                        html_parts.append(f'<span class="akshara">{ak.text}</span>')
                        html_parts.append('</div>')
                        
                        if item['is_word_end']:
                            html_parts.append('<div class="word-gap"></div>')
                    
                    html_parts.append('</div></div>')
                    
                    current_ak_idx = end_idx
                    if current_ak_idx >= len(flattened_aksharas):
                        break
                
                html_parts.append('</div></div>')
                
                st.markdown("".join(html_parts), unsafe_allow_html=True)

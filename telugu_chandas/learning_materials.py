
import streamlit as st
import pandas as pd

def render_learning_section():
    # Local CSS for Learning Section
    st.markdown("""
    <style>
        .topic-card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border-left: 5px solid #667eea;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .topic-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }
        .topic-header {
            font-family: 'Suravaram', serif;
            color: #2c3e50;
            font-size: 1.4rem;
            margin-bottom: 16px;
            font-weight: bold;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }
        .sub-header {
            font-family: 'Suravaram', serif;
            color: #555;
            font-size: 1.1rem;
            margin-top: 12px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .info-list {
            list-style-type: none;
            padding-left: 0;
        }
        .info-list li {
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }
        .info-list li:before {
            content: "•";
            color: #667eea;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        .rule-box {
            background-color: #f8fbff;
            border: 1px solid #cce5ff;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="main-title">తెలుగు ఛందస్సు - సమగ్ర సమాచారం</h2>', unsafe_allow_html=True)
    
    # Use tabs for structured learning
    tab1, tab2, tab3 = st.tabs(["1. ప్రాథమిక అంశాలు (Basics)", "2. గణ & యతి ప్రాస (Rules)", "3. పద్య లక్షణాలు (Poems)"])
    
    with tab1:
        st.markdown("### తెలుగు వర్ణక్రమం - 57 అక్షరాలు")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #e74c3c;">
                <div class="topic-header" style="color:#c0392b;">అచ్చులు (Vowels) - 16</div>
                <p>స్వతంత్రంగా పలికే వర్ణములు (ప్రాణములు). అ నుండి ఔ వరకు.</p>
                <div class="sub-header">విభాగములు:</div>
                <ul class="info-list">
                    <li><b>హ్రస్వములు (Short):</b> 6 - అ, ఇ, ఉ, ఋ, ఎ, ఒ (ఏక మాత్రా కాలం)</li>
                    <li><b>దీర్ఘములు (Long):</b> 6 - ఆ, ఈ, ఊ, ౠ, ఏ, ఓ (ద్వి మాత్రా కాలం)</li>
                    <li><b>వక్రములు:</b> 4 - ఎ, ఏ, ఒ, ఓ</li>
                    <li><b>వక్రతమములు:</b> 2 - ఐ, ఔ</li>
                </ul>
                <div class="sub-header">ఉభయాక్షరములు (3):</div>
                <p>అచ్చులు, హల్లుల సహాయంతో పలికేవి.</p>
                <ul class="info-list">
                    <li>సున్న (Anusvara) - o</li>
                    <li>అరసున్న (Arasunna) - c</li>
                    <li>విసర్గ (Visarga) - :</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #2980b9;">
                <div class="topic-header" style="color:#2980b9;">హల్లులు (Consonants) - 38</div>
                <p>అచ్చుల సహాయంతో పలికేవి (వ్యంజనములు/ప్రాణులు).</p>
                <div class="sub-header">వర్గ విభజన:</div>
                <ul class="info-list">
                    <li><b>క వర్గం:</b> క ఖ గ ఘ ఙ</li>
                    <li><b>చ వర్గం:</b> చ ఛ జ ఝ ఞ</li>
                    <li><b>ట వర్గం:</b> ట ఠ డ ఢ ణ</li>
                    <li><b>త వర్గం:</b> త థ ద ధ న</li>
                    <li><b>ప వర్గం:</b> ప ఫ బ భ మ</li>
                </ul>
                <div class="sub-header">గుణ విభజన:</div>
                <ul class="info-list">
                    <li><b>పరుషములు (Hard):</b> క, చ, ట, త, ప</li>
                    <li><b>సరళములు (Soft):</b> గ, జ, డ, ద, బ</li>
                    <li><b>స్థిరములు:</b> పరుష, సరళాలు కాక మిగిలినవి (ఖ, ఘ, ఙ...)</li>
                    <li><b>అనునాసికములు (Nasal):</b> ఙ, ఞ, ణ, న, మ</li>
                    <li><b>అంతస్థములు:</b> య, ర, ఱ, ల, ళ, వ</li>
                    <li><b>ఊష్మములు (Sibilants):</b> శ, ష, స, హ</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.info("మాత్ర అనగా కనురెప్ప పాటు కాలం (లేదా చిటికె వేయు కాలం).")

    with tab2:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #2ecc71;">
                <div class="topic-header">లఘువు (Laghu) - 'l'</div>
                <div class="rule-box">గుర్తు: <b>l</b> | మాత్ర: <b>1</b></div>
                <div class="sub-header">లఘువులయ్యే అక్షరాలు:</div>
                <ul class="info-list">
                    <li>హ్రస్వ అచ్చులు (అ, ఇ, ఉ, ఋ...)</li>
                    <li>హ్రస్వ అచ్చులతో గూడిన హల్లులు (క, కి, కు...)</li>
                    <li>వక్రములు (ఎ, ఒ)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_r2:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #f39c12;">
                <div class="topic-header">గురువు (Guru) - 'U'</div>
                <div class="rule-box">గుర్తు: <b>U</b> | మాత్ర: <b>2</b></div>
                <div class="sub-header">గురువులయ్యే అక్షరాలు:</div>
                <ul class="info-list">
                    <li>దీర్ఘ అచ్చులు (ఆ, ఈ, ఊ...) & దీర్ఘ హల్లులు</li>
                    <li>సున్న (o), విసర్గ (:), పొల్లు (క్, న్) తో కూడినవి</li>
                    <li>ఐ, ఔ కారాలు కలిగినవి (కై, కౌ...)</li>
                    <li>ద్విత్వ అక్షరాలకు <b>ముందున్న</b> అక్షరం</li>
                    <li>సంయుక్త అక్షరాలకు <b>ముందున్న</b> అక్షరం</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### గణ విభజన పట్టిక")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**ఏకాక్షర గణాలు**")
            st.write("* **గ** (Guru) - U")
            st.write("* **ల** (Laghu) - l")
            
            st.markdown("**రెండక్షరాల గణాలు**")
            st.write("* **గగ** (UU)")
            st.write("* **గల** (Ul) - హ గణం")
            st.write("* **వ** (lU) - వ గణం")
            st.write("* **లల** (ll)")
            
        with c2:
            st.markdown("**సూర్య గణాలు (2)**")
            st.success("1. **న** గణం (lll)\n2. **గల** (లేదా **హ**) గణం (Ul)")
            
            st.markdown("**ఇంద్ర గణాలు (6)**")
            st.info("1. **నల** (llll)\n2. **నగ** (lllU)\n3. **సల** (llUl)\n4. **భ** (Ull)\n5. **ర** (UlU)\n6. **త** (UUl)")
            
        with c3:
            st.markdown("**మూడక్షరాల గణాలు (8)**")
            st.markdown("""
            | గణం | స్వరూపం | వివరణ |
            |---|---|---|
            | **య** | lUU | ఆది లఘువు |
            | **ర** | UlU | మధ్య లఘువు |
            | **త** | UUl | అంత్య లఘువు |
            | **భ** | Ull | ఆది గురువు |
            | **జ** | lUl | మధ్య గురువు |
            | **స** | llU | అంత్య గురువు |
            | **మ** | UUU | సర్వ గురువు |
            | **న** | lll | సర్వ లఘువు |
            """)

        st.divider()
        st.markdown("### యతి - ప్రాస నియమాలు")
        y1, y2 = st.columns(2)
        with y1:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #8e44ad;">
                <div class="topic-header">యతి (Yati)</div>
                <p>పద్య పాదంలో <b>మొదటి అక్షరాన్ని</b> 'యతి' అంటారు.</p>
                <ul class="info-list">
                    <li>నిర్ణీత స్థానంలో యతి మైత్రి అక్షరం ఉండాలి.</li>
                    <li>సాధారణంగా సవర్ణ అక్షరాలు లేదా వర్గ మైత్రి అక్షరాలు చెల్లుతాయి.</li>
                    <li><b>ప్రాస యతి:</b> ఉపజాతి పద్యాలలో యతి కుదరకపోతే, ప్రాస అక్షరాన్ని యతిగా వాడవచ్చు.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with y2:
            st.markdown("""
            <div class="topic-card" style="border-left-color: #d35400;">
                <div class="topic-header">ప్రాస (Prasa)</div>
                <p>పద్య పాదంలో <b>రెండవ అక్షరాన్ని</b> 'ప్రాస' అంటారు.</p>
                <ul class="info-list">
                    <li><b>ప్రాస నియమం:</b> పద్యవాదంలోని అన్ని పాదాలలోనూ రెండవ అక్షరం ఒకే హల్లు (gunintham doesn't matter, only consonant) అయి ఉండాలి.</li>
                    <li>ద్విత్వ, సంయుక్త అక్షరాలకు కఠిన నియమాలు ఉంటాయి.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 1. వృత్త పద్యాలు (Vritta Padyalu)")
        st.write("అక్షర గణాలతో ఏర్పడేవి. ప్రతి పాదానికి ఈ లక్షణాలు సమానంగా ఉంటాయి.")
        
        vritta_df = pd.DataFrame({
            "వృత్తం": ["ఉత్పలమాల", "చంపకమాల", "శార్దూలం", "మత్తేభం"],
            "గణ వరుస": ["భ-ర-న-భ-భ-ర-వ", "న-జ-భ-జ-జ-జ-ర", "మ-స-జ-స-త-త-గ", "స-భ-ర-న-మ-య-వ"],
            "యతి స్థానం": ["10వ అక్షరం", "11వ అక్షరం", "13వ అక్షరం", "14వ అక్షరం"],
            "మొత్తం అక్షరాలు": ["20", "21", "19", "20"],
            "ప్రాస": ["ఉంది", "ఉంది", "ఉంది", "ఉంది"]
        })
        st.table(vritta_df)

        st.markdown("### 2. జాతి పద్యాలు (Jati Padyalu)")
        st.write("మాత్రా గణాలతో (సూర్య, ఇంద్ర) ఏర్పడేవి.")
        
        jati_df = pd.DataFrame({
            "పద్యం": ["కందం", "ద్విపద", "తరువోజ"],
            "పాదాలు": ["4", "2", "2 (దీర్ఘ పాదాలు)"],
            "గణ విభజన (Structure)": [
                "1,3 పాదాలు: 3 గణాలు (12 మాత్రలు)\n2,4 పాదాలు: 5 గణాలు (20 మాత్రలు)\nవాడే గణాలు: గగ, భ, జ, స, నల",
                "ప్రతి పాదంలో: 3 ఇంద్ర + 1 సూర్య గణాలు",
                "ప్రతి పాదంలో: 3 ఇంద్ర + 1 సూర్య + 3 ఇంద్ర + 1 సూర్య"
            ],
            "యతి స్థానం": [
                "4వ గణం మొదటి అక్షరం",
                "3వ గణం మొదటి అక్షరం",
                "1, 3, 5, 7 గణాల తొలి అక్షరాల మధ్య"
            ],
            "ముఖ్య నియమాలు": [
                "1. బేసి గణంలో 'జ' రాకూడదు (1,3,5,7).\n2. 6వ గణం తప్పక 'నలం' లేదా 'జ' అవ్వాలి.\n3. చివర గురువు ఉండాలి.",
                "ప్రాస నియమం ఉంది.",
                "ప్రాస నియమం ఉంది."
            ]
        })
        st.table(jati_df)

        st.markdown("### 3. ఉపజాతి పద్యాలు (Upajati Padyalu)")
        st.write("మాత్రా గణాలతో ఏర్పడేవి. **ప్రాస నియమం లేదు**. యతి బదులు ప్రాస యతి చెల్లుతుంది.")
        
        upajati_df = pd.DataFrame({
            "పద్యం": ["ఆటవెలది", "తేటగీతి", "సీసం"],
            "గణాలు": [
                "1, 3 పాదాలు: 3 సూర్య + 2 ఇంద్ర\n2, 4 పాదాలు: 5 సూర్య గణాలు",
                "1 సూర్య + 2 ఇంద్ర + 2 సూర్య గణాలు",
                "ప్రతి పాదంలో: 6 ఇంద్ర + 2 సూర్య గణాలు\n(సాధారణంగా 4 పాదాలు, పైన సీసం, కింద ఆటవెలది/తేటగీతి)"
            ],
            "యతి": [
                "1వ గణం - 4వ గణం మధ్య",
                "1వ గణం - 4వ గణం మధ్య",
                "1-3 గణాల మధ్య, 5-7 గణాల మధ్య"
            ]
        })
        st.table(upajati_df)

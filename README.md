# Telugu Chandas Identifier

A rule-based engine for identifying Telugu prosodic meters (Chandassu). Classifies Laghu/Guru weights and matches **Vritta**, **Jati**, and **Upajati** padyam.

## Supported Meters

**Vritta** (syllabic — 3-akshara ganas):

| Meter | Gana Sequence | Yati Position |
|---|---|---|
| Utpalamala | Bha Ra Na Bha Bha Ra Va | 10 |
| Champakamala | Na Ja Bha Ja Ja Ja Ra | 11 |
| Shardulam | Ma Sa Ja Sa Ta Ta Ga | 13 |
| Mattebham | Sa Bha Ra Na Ma Ya Va | 14 |

**Jati** (matra-based — Surya/Indra ganas, with Prasa):

| Meter | Padas | Structure |
|---|---|---|
| Dwipada | 2 | 3 Indra + 1 Surya per pada |
| Taruvoja | 4 | (3 Indra + 1 Surya) × 2 per pada |
| Kandam | 4 | Odd: 3 K-ganas, Even: 5 K-ganas |

**Upajati** (Jati without Prasa — Prasa-Yati allowed):

| Meter | Padas | Structure |
|---|---|---|
| Ataveladi | 4 | Odd: 3 Indra + 2 Surya, Even: 5 Surya |
| Tetagiti | 4 | 1 Surya + 2 Indra + 2 Surya per pada |
| Sisam | 4 | 6 Indra + 2 Surya per pada |

## Usage

```python
from telugu_chandas.engine import ChandasEngine

engine = ChandasEngine()

# Identify meter
result = engine.identify_meter(poem_text)
print(result.meter_name)       # e.g. "Mattebham"
print(result.confidence)       # e.g. "95.0%"
print(result.yati_valid)       # True / False
print(result.prasa_valid)      # True / False
print(result.ganas_found)      # ["Sa", "Bha", "Ra", ...]
print(result.yati_notes)       # per-line yati detail strings
print(result.prasa_note)       # prasa consonant string

# Analyze weights only
tokens = engine.analyze(poem_text)
for token in tokens:
    if token.is_word:
        for ak in token.aksharas:
            print(ak.text, ak.weight.value)  # e.g. "భ" "I"

# Debug weight breakdown
print(engine.debug_output(poem_text))
```

## Run the App

```bash
streamlit run app.py
```

## Run Tests

```bash
pip install pytest
pytest tests/ -v
```

# Telugu Chandassu Identifier (`telugu-chandassu`)

[![PyPI version](https://img.shields.io/pypi/v/telugu-chandassu.svg)](https://pypi.org/project/telugu-chandassu/)
[![Python versions](https://img.shields.io/pypi/pyversions/telugu-chandassu.svg)](https://pypi.org/project/telugu-chandassu/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A rule-based Python engine for identifying and analyzing Telugu prosodic meters (ఛందస్సు). It classifies Laghu (లఘువు) and Guru (గురువు) weights and matches **Vritta** (వృత్తం), **Jati** (జాతి), and **Upajati** (ఉపజాతి) padyam with detailed Gana, Yati, and Prasa breakdowns.

---

## Installation

### Core Library (Zero External Dependencies)
```bash
pip install telugu-chandassu
```

### For Development & Testing
```bash
pip install "telugu-chandassu[dev]"
```

---

## Supported Meters

### **Vritta** (వృత్తం — Syllabic / 3-akshara ganas)

| Meter (తెలుగు) | Meter (English) | Gana Sequence | Yati Position |
|---|---|---|---|
| ఉత్పలమాల | Utpalamala | Bha Ra Na Bha Bha Ra Va | 10 |
| చంపకమాల | Champakamala | Na Ja Bha Ja Ja Ja Ra | 11 |
| శార్దూలము | Shardulam | Ma Sa Ja Sa Ta Ta Ga | 13 |
| మత్తేభము | Mattebham | Sa Bha Ra Na Ma Ya Va | 14 |

### **Jati** (జాతి — Matra-based with Surya/Indra ganas, Prasa required)

| Meter (తెలుగు) | Meter (English) | Padas | Structure |
|---|---|---|---|
| ద్విపద | Dwipada | 2 | 3 Indra + 1 Surya per pada |
| తరువోజ | Taruvoja | 4 | (3 Indra + 1 Surya) × 2 per pada |
| కందం | Kandam | 4 | Odd: 3 K-ganas, Even: 5 K-ganas |

### **Upajati** (ఉపజాతి — Matra-based, Prasa not required, Prasa-Yati allowed)

| Meter (తెలుగు) | Meter (English) | Padas | Structure |
|---|---|---|---|
| ఆటవెలది | Ataveladi | 4 | Odd: 3 Indra + 2 Surya, Even: 5 Surya |
| తేటగీతి | Tetagiti | 4 | 1 Surya + 2 Indra + 2 Surya per pada |
| సీసం | Sisam | 4 | 6 Indra + 2 Surya per pada |

---

## Usage

```python
from telugu_chandassu import ChandassuEngine

engine = ChandassuEngine()

poem_text = """భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-
భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-
రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-
నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"""

# 1. Identify Meter
result = engine.identify_meter(poem_text)
print("Meter Name     :", result.meter_name)       # "Mattebham"
print("Confidence     :", result.confidence)       # "95.0%"
print("Yati Valid     :", result.yati_valid)       # True
print("Prasa Valid    :", result.prasa_valid)      # True
print("Ganas Found    :", result.ganas_found)      # ['Sa', 'Bha', 'Ra', 'Na', 'Ma', 'Ya', 'Va']
print("Prasa Consonant:", result.prasa_note)       # Main Prasa: వ

# 2. Analyze Individual Aksharas & Weights
tokens = engine.analyze(poem_text)
for token in tokens:
    if token.is_word:
        for ak in token.aksharas:
            print(f"{ak.text}: {ak.weight.value}")  # e.g. "భ": "I", "వ": "I", "దు": "U"

# 3. Debug Output
print(engine.debug_output(poem_text))
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## License

This project is licensed under the [GNU Affero General Public License v3 (AGPL-3.0)](LICENSE).

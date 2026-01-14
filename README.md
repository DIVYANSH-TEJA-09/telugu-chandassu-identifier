# Telugu Chandas Identifier

A strict, rule-based engine for identifying Laghu/Guru weights in Telugu poetry (Chandassu).

## Features
- **Deterministic Rule Base**: Follows standard Telugu Chandas textbook rules.
- **Akshara Segmentation**: Correctly splits text into Aksharas, handling:
    - Vowels (Achchulu)
    - Consonants (Hallulu) + Vowel Signs (Guninthalu)
    - Conjuncts (Samyuktaksharalu, Dvitvaksharalu)
    - Pollu (Word-final Consonant + Virama treated as Guru coda)
    - Modifiers (Sunna, Visarga)
- **Weight Classification**:
    - **Laghu (I)**: Short vowels.
    - **Guru (U)**: Long vowels, Diphthongs, Modifiers (Sunna/Visarga), Pollu-ending syllables.
    - **Positional Guru**: A Laghu akshara becomes Guru if followed by a conjunct consonant (double consonant or composite) **in the same word**. This rule **does not cross word boundaries**.

## Usage

```python
from telugu_chandas.engine import ChandasEngine

engine = ChandasEngine()
text = "ఆదిత్య"

# Analyze
tokens = engine.analyze(text)

# Get Sequence
search_pattern = engine.get_laghu_guru_sequence(text)
print(search_pattern) 
# Output: U U I (Aa=U, Di=U(Positional), Tya=I)

# Detailed Debug
print(engine.debug_output(text))
```
"# telugu-chandassu-identifier" 

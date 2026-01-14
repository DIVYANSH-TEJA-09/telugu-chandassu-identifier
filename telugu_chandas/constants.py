# telugu_chandas/constants.py

"""
Telugu Character Sets for Chandas Analysis.
Based on the project requirements:
A (Achchulu), H (Hallulu), G (Guninthapu Gurthulu), U (Modifiers), V (Virama), P (Pollu).
"""

# 🅰️ Set A — Achchulu (Independent Vowels)
ACHCHULU = {
    'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ౠ', 
    'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ'
}

A_HRASVA = {'అ', 'ఇ', 'ఉ', 'ఋ', 'ఎ', 'ఒ'}  # Short vowels (1 matra)
A_DIRGHA = {'ఆ', 'ఈ', 'ఊ', 'ౠ', 'ఏ', 'ఓ'}  # Long vowels (2 matras)
A_VAKRA = {'ఐ', 'ఔ'}                       # Diphthongs (2 matras)

# 🅱️ Set H — Hallulu (Consonants)
# Standard Telugu consonants
HALLULU = {
    'క', 'ఖ', 'గ', 'ఘ', 'ఙ',
    'చ', 'ఛ', 'జ', 'ఝ', 'ఞ',
    'ట', 'ఠ', 'డ', 'ఢ', 'ణ',
    'త', 'థ', 'ద', 'ధ', 'న',
    'ప', 'ఫ', 'బ', 'భ', 'మ',
    'య', 'ర', 'ల', 'వ', 'శ', 'ష', 'స', 'హ', 'ళ', 'క్ష', 'ఱ'
} 
# Note: 'క్ష' is strictly speaking k+sh+a, but often treated as a unit. 
# However, for Chandas strict rules, we should handle it as composite if decomposable.
# Standard unicode range often includes it. 
# We will treat standard Unicode code points.
# Let's ensure strict set definition.

# 🅲 Set G — Guninthapu Gurthulu (Vowel Signs)
# Matras corresponding to vowels
GUNINTHALU = {
    'ా', 'ి', 'ీ', 'ు', 'ూ', 'ృ', 'ౄ', 
    'ె', 'ే', 'ై', 'ొ', 'ో', 'ౌ'
}

G_HRASVA = {'ి', 'ు', 'ృ', 'ె', 'ొ'}
G_DIRGHA = {'ా', 'ీ', 'ూ', 'ౄ', 'ే', 'ో', 'ై', 'ౌ'}

# 🅳 Set U — Modifiers
# U1 (Heavy/Guru)
U_GURU_MODIFIERS = {'ం', 'ః'}  # Sunna (Anusvara), Visarga

# U2 (Light/Laghu)
U_LAGHU_MODIFIERS = {'ఁ'}      # Arasunna (Candrabindu) - rare in heavy usage, always Laghu

MODIFIERS = U_GURU_MODIFIERS.union(U_LAGHU_MODIFIERS)

# 🅴 Set V — Virāma
VIRAMA = {'్'}

# Helper Sets
ALL_VOWELS = ACHCHULU.union(GUNINTHALU)
ALL_CONSONANTS = HALLULU

def is_achchu(char: str) -> bool:
    return char in ACHCHULU

def is_hallu(char: str) -> bool:
    return char in HALLULU

def is_gunintham(char: str) -> bool:
    return char in GUNINTHALU

def is_virama(char: str) -> bool:
    return char in VIRAMA

def is_modifier(char: str) -> bool:
    return char in U_GURU_MODIFIERS or char in U_LAGHU_MODIFIERS

def is_guru_vowel(char: str) -> bool:
    """Check if a vowel (Achchu or Gunintham) is inherently Guru."""
    if char in A_DIRGHA or char in A_VAKRA:
        return True
    if char in G_DIRGHA:
        return True
    return False

def is_hrasva_vowel(char: str) -> bool:
    """Check if a vowel is Short (Laghu)."""
    if char in A_HRASVA:
        return True
    if char in G_HRASVA:
        return True
    return False

# -----------------------------------------------------------------------------
# YATI & PRASA GROUPS
# -----------------------------------------------------------------------------

# Mapping Gunintham signs back to primary vowels for comparison
GUNINTHAM_TO_ACHCHU_MAP = {
    'ా': 'ఆ',
    'ి': 'ఇ',
    'ీ': 'ఈ',
    'ు': 'ఉ',
    'ూ': 'ఊ',
    'ృ': 'ఋ',
    'ౄ': 'ౠ',
    'ె': 'ఎ',
    'ే': 'ఏ',
    'ై': 'ఐ',
    'ొ': 'ఒ',
    'ో': 'ఓ',
    'ౌ': 'ఔ'
}

# Special Yati Friendships (Abheda) where strict articulation differs but Yati allows
YATI_ABHEDA_PAIRS = {
    frozenset({'న', 'ణ'}), # Na - Ana
    frozenset({'ల', 'ళ'}), # La - Ala
    frozenset({'ర', 'ఱ'}), # Ra - Bandira
    frozenset({'అ', 'హ'}), # Sometimes Ha is treated as A? (Wait, K-Group handles Ha+A)
}

# -----------------------------------------------------------------------------
# YATI & PRASA GROUPS (STRICT ARTICULATION)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# YATI MAITRI GROUPS (ADVANCED)
# -----------------------------------------------------------------------------

# RULE A: SWARA MAITRI (Vowel Friendship)
# Vowels must belong to the same Phonetic Family.
SWARA_MAITRI_GROUPS = [
    # A-Group: Kanthya based
    {'name': 'A-Group', 'vowels': {'అ', 'ఆ', 'ఐ', 'ఔ'}},
    
    # I-Group: Talavya based
    {'name': 'I-Group', 'vowels': {'ఇ', 'ఈ', 'ఎ', 'ఏ'}},
    
    # U-Group: Oshthya based
    {'name': 'U-Group', 'vowels': {'ఉ', 'ఊ', 'ఒ', 'ఓ'}},
    
    # Ru-Group: Murdhanya
    {'name': 'Ru-Group', 'vowels': {'ఋ', 'ౠ'}}
]

# RULE B: VYANJANA MAITRI (Consonant Friendship)
# Consonants must belong to same articulation place (Mouth Position).
# Consonants must belong to same articulation place (Mouth Position).
VYANJANA_MAITRI_GROUPS = [
    # K-Group (Kanthya): Ka Varga + Ha
    {'name': 'Ka-Group', 'consonants': {'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'హ', 'అ', 'ఆ'}}, # Including A, AA
    
    # Ch-Group (Talavya): Cha Varga + Ya, Sha
    {'name': 'Cha-Group', 'consonants': {'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'య', 'శ', 'ఇ', 'ఈ', 'ఎ', 'ఏ'}}, # Including I, E
    
    # T-Group (Murdhanya): Ta Varga + Ra, Rra, Sha
    {'name': 'Ta-Group', 'consonants': {'ట', 'ఠ', 'డ', 'ఢ', 'ణ', 'ర', 'ఱ', 'ష', 'ఋ', 'ౠ'}}, # Including Ru
    
    # Th-Group (Dantya): Tha Varga + La, Sa
    {'name': 'Tha-Group', 'consonants': {'త', 'థ', 'ద', 'ధ', 'న', 'ల', 'స', 'ళ'}},
    
    # P-Group (Oshthya): Pa Varga
    {'name': 'Pa-Group', 'consonants': {'ప', 'ఫ', 'బ', 'భ', 'మ', 'ఉ', 'ఊ', 'ఒ', 'ఓ'}} # Including U, O
]

# DETAILED CONSONANT CLASSIFICATIONS (For Advanced Yati)
CONSONANT_CLASSES = [
    {'name': 'Parushalu', 'consonants': {'క', 'చ', 'ట', 'త', 'ప'}},
    {'name': 'Saralalu', 'consonants': {'గ', 'జ', 'డ', 'ద', 'బ'}},
    {'name': 'Drutamu', 'consonants': {'న'}},
    {'name': 'Sthiralu', 'consonants': {'ఖ', 'ఘ', 'ఙ', 'ఛ', 'ఝ', 'ఞ', 'ఠ', 'ఢ', 'ణ', 'థ', 'ధ', 'న', 'ఫ', 'భ', 'మ', 'య', 'ర', 'ఱ', 'ల', 'ళ', 'వ', 'శ', 'ష', 'స', 'హ'}},
    {'name': 'Anunasikalu', 'consonants': {'ఙ', 'ఞ', 'ణ', 'న', 'మ'}},
    {'name': 'Antasthalu', 'consonants': {'య', 'ర', 'ఱ', 'ల', 'ళ', 'వ'}},
    {'name': 'Ushmamulu', 'consonants': {'శ', 'ష', 'స', 'హ'}},
    
    # Varga Groups
    {'name': 'Varga-1', 'consonants': {'క', 'చ', 'ట', 'త', 'ప'}},
    {'name': 'Varga-2', 'consonants': {'ఖ', 'ఛ', 'ఠ', 'థ', 'ఫ'}},
    {'name': 'Varga-3', 'consonants': {'గ', 'జ', 'డ', 'ద', 'బ'}},
    {'name': 'Varga-4', 'consonants': {'ఘ', 'ఝ', 'ఢ', 'ధ', 'భ'}},
    {'name': 'Varga-5', 'consonants': {'ఙ', 'ఞ', 'ణ', 'న', 'మ'}}
]

def get_swara_maitri_group(char: str) -> dict:
    """Returns the Swara Maitri group for a Vowel."""
    base_vowel = GUNINTHAM_TO_ACHCHU_MAP.get(char, char)
    for group in SWARA_MAITRI_GROUPS:
        if base_vowel in group['vowels']:
            return group
    return None

def get_vyanjana_maitri_group(cons: str) -> dict:
    """Returns the Vyanjana Maitri group for a Consonant."""
    for group in VYANJANA_MAITRI_GROUPS:
        if cons in group['consonants']:
            return group
    return None

# Mapping Gunintham signs back to primary vowels for comparison


from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass

class GanaType(Enum):
    VRITTA = "Vr̥tta"      # 3 aksharas (standard)
    SURYA = "Surya"      # Matra based
    INDRA = "Indra"      # Matra based
    CHANDRA = "Chandra"  # (If needed)

@dataclass
class GanaPattern:
    name: str
    pattern: str  # e.g., "Ull"
    types: List[GanaType]

# --- Standard Gana Definitions ---
# 1. Ekakshara
G_GURU = "U"
G_LAGHU = "I" # Using 'I' for Laghu consistently

# 2. Dvikakshara
G_GAGA = "UU"
G_GALA = "UI"
G_VA   = "IU" # Vaganam
G_LALA = "II"

# 3. Trikakshara (Vritta Ganas)
# BHAJASAYARATANA (Mnemonics)
# Bha = U I I
# Ja  = I U I
# Sa  = I I U
# Ya  = I U U
# Ra  = U I U
# Ta  = U U I
# Na  = I I I
# Ma  = U U U

VRITTA_GANAS: Dict[str, str] = {
    "UUU": "Ma",
    "IUU": "Ya",
    "UIU": "Ra",
    "IIU": "Sa",
    "UUI": "Ta",
    "IUI": "Ja",
    "UII": "Bha",
    "III": "Na"
}

# --- Utility to get Gana from Pattern ---

# --- Jati Gana Definitions ---
# Weight encoding: U = Guru (2 matras), I = Laghu (1 matra)

# Surya Ganas (2 types, 3 matras each)
SURYA_GANAS: Dict[str, str] = {
    "III": "న",   # na gana  - I I I (3 aksharas, 3 matras)
    "UI":  "గల",  # ga-la    - U I   (2 aksharas, 3 matras)
}

# Indra Ganas (6 types, 3-4 aksharas each)
INDRA_GANAS: Dict[str, str] = {
    "UII":  "భ",   # bha gana - U I I   (3 aksharas)
    "UIU":  "ర",   # ra gana  - U I U   (3 aksharas)
    "UUI":  "త",   # ta gana  - U U I   (3 aksharas)
    "IIII": "నల",  # nal gana - I I I I (4 aksharas)
    "IIIU": "నగ",  # nag gana - I I I U (4 aksharas)
    "IIUI": "సల",  # sal gana - I I U I (4 aksharas)
}

# Kandam Ganas (5 types, all exactly 4 matras, variable akshara count)
KANDAM_GANAS: Dict[str, str] = {
    "UU":   "గగన", # ga-ga-na - U U     (2 aksharas, 4 matras)
    "UII":  "భ",   # bha gana - U I I   (3 aksharas, 4 matras)
    "IUI":  "జ",   # ja gana  - I U I   (3 aksharas, 4 matras)
    "IIU":  "స",   # sa gana  - I I U   (3 aksharas, 4 matras)
    "IIII": "నల",  # nal gana - I I I I (4 aksharas, 4 matras)
}

def get_ganas_for_vritta(weight_string: str) -> List[str]:
    """
    Splits the weight string into chunks of 3 and maps to Vritta Ganas.
    Leftovers are mapped to Ga/La.
    
    Ex: "UIIUIIU" -> "UII", "UII", "U" -> [Bha, Bha, Ga]
    """
    ganas = []
    n = len(weight_string)
    
    for i in range(0, n, 3):
        chunk = weight_string[i : i+3]
        
        if len(chunk) == 3:
            if chunk in VRITTA_GANAS:
                ganas.append(VRITTA_GANAS[chunk])
            else:
                ganas.append(f"?({chunk})") # Should not happen if strictly I/U
        elif len(chunk) == 2:
            # Handle leftovers
            if chunk == "UU": ganas.append("GaGa")
            elif chunk == "UI": ganas.append("GaLa")
            elif chunk == "IU": ganas.append("Va")
            elif chunk == "II": ganas.append("LaLa")
        elif len(chunk) == 1:
            if chunk == "U": ganas.append("Ga")
            elif chunk == "I": ganas.append("La")
            
    return ganas

from typing import List, Set, Tuple, Optional
from .models import Akshara
from . import constants
from .locale import YATI_CATEGORY_NAMES_TE, MAITRI_GROUP_NAMES_TE


def get_akshara_vowel(akshara: Akshara) -> str:
    """Extracts the vowel part (Achchu or Gunintham mapped to Achchu) from an Akshara."""
    has_vowel_sign = False
    has_hallu = False
    for char in akshara.components:
        if constants.is_achchu(char):
            return char
        if constants.is_gunintham(char):
            return constants.GUNINTHAM_TO_ACHCHU_MAP.get(char, char)
        if constants.is_hallu(char):
            has_hallu = True
            
    if has_hallu and not akshara.has_pollu:
        return 'అ' # Inherent A
        
    return ""

def get_akshara_consonants(akshara: Akshara) -> List[str]:
    """
    Extracts the onset consonants (for Prasa validation).
    
    For aksharas with pollu (coda), we should NOT include the pollu consonant.
    Example: 'పన్' has components ['ప', 'న', '్']
    - 'ప' is the nucleus consonant (with implicit 'a')
    - 'న్' is the coda (pollu)
    We should return only ['ప'], not ['ప', 'న']
    """
    consonants = []
    components = akshara.components
    n = len(components)
    
    i = 0
    while i < n:
        char = components[i]
        
        if constants.is_hallu(char):
            # Check if this is part of pollu (coda) or onset
            next_char = components[i+1] if i+1 < n else None
            
            if next_char and constants.is_virama(next_char):
                # H + V pattern
                after_virama = components[i+2] if i+2 < n else None
                
                if after_virama and constants.is_hallu(after_virama):
                    # H + V + H -> This H is part of onset cluster
                    consonants.append(char)
                    i += 2  # Skip virama
                    continue
                else:
                    # H + V at end -> This is pollu (coda), STOP
                    break
            else:
                # H not followed by virama -> this is the nucleus consonant
                consonants.append(char)
                break
                
        elif constants.is_achchu(char) or constants.is_gunintham(char):
            # Found vowel, done with onset
            break
            
        i += 1
        
    return consonants

def check_yati_match(akshara1: Akshara, akshara2: Akshara) -> Tuple[bool, str]:
    """
    Checks if two aksharas match according to Advanced Yati Rules.
    
    Rules (in order of precedence):
    1. SWARA MAITRI - If vowels from same group, valid Yati (regardless of consonant)
    2. VYANJANA MAITRI - If consonants from same vargam, valid Yati (can override vowel mismatch)
    3. ABHEDA pairs - Special consonant equivalences (న-ణ, ల-ళ, etc.)
    
    For aksharas with multiple consonants (samyukta), check ALL consonants.
    """
    # 1. Extract Vowels
    v1 = get_akshara_vowel(akshara1)
    v2 = get_akshara_vowel(akshara2)
    
    if not v1: v1 = "అ"  # Implicit 'a' if no vowel found
    if not v2: v2 = "అ"
    
    # 2. Extract ALL Consonants (for samyukta aksharas)
    c1_list = get_akshara_consonants(akshara1)
    c2_list = get_akshara_consonants(akshara2)
    
    # Also get the second consonant in case of conjuncts (for checking alternate matches)
    all_c1 = [c for c in akshara1.components if constants.is_hallu(c)]
    all_c2 = [c for c in akshara2.components if constants.is_hallu(c)]
    
    # Helper to translate group names
    def _te(name):
        return MAITRI_GROUP_NAMES_TE.get(name, name)
    
    # 3. Check SWARA MAITRI
    swara_match = False
    swara_info = ""
    
    s1_group = constants.get_swara_maitri_group(v1)
    s2_group = constants.get_swara_maitri_group(v2)
    
    if s1_group and s2_group and s1_group['name'] == s2_group['name']:
        swara_match = True
        swara_info = s1_group['name']
    elif v1 == v2:
        swara_match = True
        swara_info = "Savarna"
    
    # 4. Check VYANJANA MAITRI (using ALL consonants in both aksharas)
    def get_consonant_groups(c_list):
        groups = set()
        for c in c_list:
            # Check standard Vyanjana groups
            g = constants.get_vyanjana_maitri_group(c)
            if g: groups.add(g['name'])
            
            # Check detailed classes (Parushalu, Vargas, etc.)
            for cls in constants.CONSONANT_CLASSES:
                if c in cls['consonants']:
                    groups.add(cls['name'])
        return groups
    
    c1_groups = get_consonant_groups(all_c1)
    c2_groups = get_consonant_groups(all_c2)
    
    vyanjana_match = False
    vyanjana_info = "Mismatch"
    
    if not all_c1 and not all_c2:
        # Both pure vowels
        vyanjana_match = True
        vyanjana_info = "PureVowels"
    elif all_c1 and all_c2:
        # Check for group intersection
        common = c1_groups.intersection(c2_groups)
        if common:
            vyanjana_match = True
            vyanjana_info = list(common)[0]
        else:
            # Check Abheda Pairs
            for x in all_c1:
                for y in all_c2:
                    if frozenset({x, y}) in constants.YATI_ABHEDA_PAIRS:
                        vyanjana_match = True
                        vyanjana_info = f"Abheda({x}-{y})"
                        break
                if vyanjana_match: break
    
    # 5. Decision Logic
    # Legacy shorthand for logs
    c1 = all_c1[0] if all_c1 else None
    c2 = all_c2[0] if all_c2 else None
    
    # Case 1: Swara match (Yati valid regardless of consonant)
    if swara_match:
        if c1 and c2:
            if vyanjana_match:
                return True, f"'{v1}'-'{v2}' ({_te(swara_info)}) + '{c1}'-'{c2}' ({_te(vyanjana_info)})"
            else:
                return True, f"'{v1}'-'{v2}' ({_te(swara_info)}) [హల్లు: {c1}-{c2}]"
        else:
            return True, f"'{v1}'-'{v2}' ({_te(swara_info)})"
    
    # Case 2: Vyanjana match only (Yati can be valid if consonants match even with vowel mismatch)
    # This is a more lenient interpretation allowing consonant-based Yati
    if vyanjana_match and c1 and c2:
        return True, f"'{c1}'-'{c2}' ({_te(vyanjana_info)}) [స్వర: {v1}-{v2}]"
    
    # Case 3: Neither matches
    return False, f"స్వర అసంగతం ({v1} vs {v2})"
    return False, f"స్వర అసంగతం ({v1} vs {v2})"

def check_prasa_match(akshara1: Akshara, akshara2: Akshara) -> Tuple[bool, str]:
    """
    Returns (Valid?, ConsonantString).
    """
    c1 = get_akshara_consonants(akshara1)
    c2 = get_akshara_consonants(akshara2)
    
    if c1 == c2:
        c_str = "+".join(c1) if c1 else "Achchu"
        return True, c_str
    
    return False, f"{c1} vs {c2}"

def validate_line_prasa(lines_2nd_aksharas: List[Akshara]) -> Tuple[bool, str]:
    """
    Validates Prasa across lines.
    Returns (Valid?, CommonConsonant).
    """
    if not lines_2nd_aksharas:
        return True, "None"
        
    start_point = lines_2nd_aksharas[0]
    master_cons = get_akshara_consonants(start_point)
    master_cons_str = "+".join(master_cons) if master_cons else "Vowel"
    
    for i in range(1, len(lines_2nd_aksharas)):
        valid, info = check_prasa_match(start_point, lines_2nd_aksharas[i])
        if not valid:
            return False, f"Line {i+1} mismatch: {info}"
            
    return True, master_cons_str

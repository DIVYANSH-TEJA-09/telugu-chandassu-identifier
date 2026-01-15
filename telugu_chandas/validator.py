# telugu_chandas/validator.py

from typing import List, Tuple, Optional
from .models import Akshara
from . import constants
from .locale import YATI_CATEGORY_NAMES_TE, MAITRI_GROUP_NAMES_TE

class RuleValidator:
    """
    Validates various rules of Telugu Chandas (Yati, Prasa, etc.).
    """

    @staticmethod
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

    @staticmethod
    def get_akshara_consonants(akshara: Akshara) -> List[str]:
        """
        Extracts the onset consonants (for Prasa validation).
        Excludes Coda (pollu) consonants.
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

    @classmethod
    def check_yati_match(cls, akshara1: Akshara, akshara2: Akshara) -> Tuple[bool, str]:
        """
        Checks if two aksharas match according to Advanced Yati Rules.
        """
        # 1. Extract Vowels
        v1 = cls.get_akshara_vowel(akshara1)
        v2 = cls.get_akshara_vowel(akshara2)
        
        if not v1: v1 = "అ"
        if not v2: v2 = "అ"
        
        # 2. Extract Consonants
        c1_list = cls.get_akshara_consonants(akshara1)
        c2_list = cls.get_akshara_consonants(akshara2)
        
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
        
        # 4. Check VYANJANA MAITRI
        all_c1 = [c for c in akshara1.components if constants.is_hallu(c)]
        all_c2 = [c for c in akshara2.components if constants.is_hallu(c)]

        def get_consonant_groups(c_list):
            groups = set()
            for c in c_list:
                g = constants.get_vyanjana_maitri_group(c)
                if g: groups.add(g['name'])
                for cl in constants.CONSONANT_CLASSES:
                    if c in cl['consonants']:
                        groups.add(cl['name'])
            return groups
        
        c1_groups = get_consonant_groups(all_c1)
        c2_groups = get_consonant_groups(all_c2)
        
        vyanjana_match = False
        vyanjana_info = "Mismatch"
        
        if not all_c1 and not all_c2:
            vyanjana_match = True
            vyanjana_info = "PureVowels"
        elif all_c1 and all_c2:
            common = c1_groups.intersection(c2_groups)
            if common:
                vyanjana_match = True
                vyanjana_info = list(common)[0]
            else:
                for x in all_c1:
                    for y in all_c2:
                        if frozenset({x, y}) in constants.YATI_ABHEDA_PAIRS:
                            vyanjana_match = True
                            vyanjana_info = f"Abheda({x}-{y})"
                            break
                        if vyanjana_match: break
        
        # 5. Decision
        c1_s = all_c1[0] if all_c1 else None
        c2_s = all_c2[0] if all_c2 else None
        
        if swara_match:
            if c1_s and c2_s:
                if vyanjana_match:
                    return True, f"'{v1}'-'{v2}' ({_te(swara_info)}) + '{c1_s}'-'{c2_s}' ({_te(vyanjana_info)})"
                else:
                    return True, f"'{v1}'-'{v2}' ({_te(swara_info)}) [హల్లు: {c1_s}-{c2_s}]"
            else:
                return True, f"'{v1}'-'{v2}' ({_te(swara_info)})"
        
        if vyanjana_match and c1_s and c2_s:
            return True, f"'{c1_s}'-'{c2_s}' ({_te(vyanjana_info)}) [స్వర: {v1}-{v2}]"
        
        return False, f"స్వర అసంగతం ({v1} vs {v2})"

    @classmethod
    def check_prasa_match(cls, akshara1: Akshara, akshara2: Akshara) -> Tuple[bool, str]:
        """
        Returns (Valid?, ConsonantString).
        """
        c1 = cls.get_akshara_consonants(akshara1)
        c2 = cls.get_akshara_consonants(akshara2)
        
        if c1 == c2:
            c_str = "+".join(c1) if c1 else "Achchu"
            return True, c_str
        
        return False, f"{c1} vs {c2}"
    
    @classmethod
    def validate_line_prasa(cls, lines_2nd_aksharas: List[Akshara]) -> Tuple[bool, str]:
        """
        Validates Prasa across lines.
        """
        if not lines_2nd_aksharas:
            return True, "None"
            
        start_point = lines_2nd_aksharas[0]
        master_cons = cls.get_akshara_consonants(start_point)
        master_cons_str = "+".join(master_cons) if master_cons else "Vowel"
        
        for i in range(1, len(lines_2nd_aksharas)):
            valid, info = cls.check_prasa_match(start_point, lines_2nd_aksharas[i])
            if not valid:
                return False, f"Line {i+1} mismatch: {info}"
                
        return True, master_cons_str

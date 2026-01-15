# telugu_chandas/analyzer.py

from typing import List
from .models import Akshara, Weight

class ProsodyAnalyzer:
    """
    Analyzes the metric weight (Laghu/Guru) of patterns.
    """

    @staticmethod
    def get_weight(akshara: Akshara, next_akshara: Akshara = None) -> Weight:
        """
        Determines weight of a single Akshara.
        1. Intrinsic Guru -> GURU
        2. Next is Samyukta (Onset count >= 1) -> GURU (Positional)
        3. Else -> LAGHU
        
        Side-effect: Sets akshara.weight
        """
        weight = Weight.LAGHU # Default
        
        if akshara.is_intrinsic_guru:
            weight = Weight.GURU
        elif next_akshara and next_akshara.onset_hallulu_count >= 1:
            weight = Weight.GURU
            
        akshara.weight = weight
        return weight

    @staticmethod
    def scan_line(aksharas: List[Akshara]) -> str:
        """
        Generates the Laghu-Guru string for a line of Aksharas.
        """
        weights = []
        for i, ak in enumerate(aksharas):
            nxt = aksharas[i+1] if i + 1 < len(aksharas) else None
            # Scan also sets weight on object
            w = ProsodyAnalyzer.get_weight(ak, nxt)
            weights.append(w.value)
        return "".join(weights)

    @staticmethod
    def get_ganas(weight_string: str) -> List[str]:
        """
        Groups the weight string into 3-letter Ganas (standard Vritta grouping).
        Leftovers mapped to Ga/La.
        
        Ex: "UIIUIIU" -> ["Bha", "Bha", "Ga"]
        """
        VRITTA_GANAS = {
            "UUU": "Ma", "IUU": "Ya", "UIU": "Ra", "IIU": "Sa",
            "UUI": "Ta", "IUI": "Ja", "UII": "Bha", "III": "Na"
        }
        
        ganas = []
        n = len(weight_string)
        
        for i in range(0, n, 3):
            chunk = weight_string[i : i+3]
            if len(chunk) == 3:
                ganas.append(VRITTA_GANAS.get(chunk, f"?({chunk})"))
            elif len(chunk) == 2:
                if chunk == "UU": ganas.append("GaGa")
                elif chunk == "UI": ganas.append("GaLa")
                elif chunk == "IU": ganas.append("Va") # or Laghu-Guru
                elif chunk == "II": ganas.append("LaLa")
            elif len(chunk) == 1:
                ganas.append("Ga" if chunk == "U" else "La")
                
        return ganas

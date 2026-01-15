# telugu_chandas/models.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

class Weight(Enum):
    LAGHU = "I"
    GURU = "U"

from .constants import ACHCHULU, HALLULU, GUNINTHALU, is_achchu, is_hallu, is_gunintham, is_guru_vowel, is_virama

@dataclass
class Akshara:
    """
    Represents a single Telugu syllable unit (Akshara).
    Components:
    - onset: List of consonants (Hallulu) before the vowel.
    - nucleus: The vowel (Achchu) or Consonant+VowelSign.
    - coda: Modifiers (Sunna, Visarga) or Pollu (Consonant+Virama) that ends the syllable.
    """
    text: str  # Full string representation
    components: List[str]  # Individual characters
    weight: Optional[Weight] = None
    
    # Metadata for classification logic
    has_pollu: bool = False  # If it ends with Pollu (H+V)
    has_modifier: bool = False # If it has Sunna/Visarga (U)

    def __str__(self):
        return f"{self.text} ({self.weight.value if self.weight else '?'})"

    @property
    def onset_hallulu_count(self) -> int:
        """
        Counts the number of Hallulu in the onset CLUSTER (samyuktakshara/dvitvakshara).
        
        This is used for positional guru: if the NEXT akshara starts with 2+ consonants
        (conjunct), the current akshara becomes Guru.
        
        Structure of akshara: [Onset Cluster] + [Nucleus] + [Coda]
        - Onset Cluster: 0 or more (H+V)+ sequences (e.g., 'స్వ' = స + ్ + వ = 2 onset)
        - Nucleus: The vowel-bearing unit (Achchu, or Hallu with Gunintham/implicit 'a')
        - Coda: Optional pollu or modifier
        
        Examples:
        - 'క' (ka): onset=0 (no cluster, 'క' is nucleus with implicit 'a')
        - 'క్త' (kta): onset=1 ('క్' is onset, 'త' is nucleus)
        - 'స్త్ర' (stra): onset=2 ('స్త్' is onset, 'ర' is nucleus)
        - 'రన్' (ran): onset=0 ('ర' is nucleus, 'న్' is coda)
        - 'భ' (bha): onset=0 (single consonant with implicit vowel = nucleus)
        """
        components = self.components
        n = len(components)
        
        # If starts with Achchu, no onset
        if n > 0 and is_achchu(components[0]):
            return 0
        
        # Count H+V patterns at the start
        # These form the onset cluster
        onset_count = 0
        i = 0
        
        while i < n:
            char = components[i]
            
            if not is_hallu(char):
                # Not a hallu, done with onset
                break
                
            # Check if this hallu is followed by virama
            next_char = components[i+1] if i+1 < n else None
            
            if next_char and is_virama(next_char):
                # H + V pattern
                # Check what comes after virama
                after_virama = components[i+2] if i+2 < n else None
                
                if after_virama and is_hallu(after_virama):
                    # H + V + H -> This H is part of onset cluster
                    onset_count += 1
                    i += 2  # Move past the virama
                    continue
                else:
                    # H + V at end (no more H after) -> This is coda/pollu
                    # We've reached the end of onset (which was the previous hallu as nucleus)
                    break
            else:
                # H not followed by virama
                # This H is the nucleus (with implicit 'a' or explicit gunintham)
                break
            
            i += 1
        
        return onset_count

    @property
    def is_intrinsic_guru(self) -> bool:
        """Checks if the Akshara is Guru by its own composition (Long Vowel, Modifier, Pollu)."""
        if self.has_pollu:
            return True
        
        # Check Modifier (U_GURU)
        # We need to distinguish Light vs Heavy modifier.
        # has_modifier flag is generic? 'has_modifier' in tokenizer checked is_modifier().
        # Tokenizer Logic: if peeks and is_modifier...
        # We need to know WHICH modifier.
        # Check components for Guru Modifiers.
        from .constants import U_GURU_MODIFIERS
        for char in self.components:
            if char in U_GURU_MODIFIERS:
                return True
        
        # Check Nucleus Length
        for char in self.components:
            if is_guru_vowel(char):
                return True
                
        return False

@dataclass
class Token:
    """A higher level unit: Word or Whitespace."""
    text: str
    is_word: bool
    aksharas: List[Akshara]

@dataclass
class IdentificationResult:
    meter_name: str
    confidence: str # "High", "Medium", "Low" or percentage string
    confidence_score: float # 0-100
    ganas_found: List[str] # Ganas of the *first* line or best matching line
    yati_valid: bool
    prasa_valid: bool
    notes: List[str] # General notes (e.g. score breakdown)
    yati_notes: List[str] = None # Detailed reasons
    prasa_note: str = ""       # "Main Prasa: X"

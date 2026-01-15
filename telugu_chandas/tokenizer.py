# telugu_chandas/tokenizer.py

import re
from typing import List, Optional
from .models import Akshara, Token
from .constants import (
    ACHCHULU, HALLULU, GUNINTHALU, MODIFIERS, VIRAMA,
    is_achchu, is_hallu, is_gunintham, is_modifier, is_virama
)

class TeluguTokenizer:
    """
    Robust tokenizer for Telugu text, splitting content into Words and Aksharas (Syllables).
    """

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text:
        - Unicode normalization (TODO: Add NFD/NFC checks if needed)
        - Whitespace cleanup
        """
        return text.strip()

    @staticmethod
    def split_into_tokens(text: str) -> List[Token]:
        """
        Splits text into Tokens (Words and Whitespace boundaries).
        """
        # Split by whitespace, keeping delimiters
        parts = re.split(r'(\s+)', text)
        tokens = []
        
        for part in parts:
            if not part:
                continue
            if re.match(r'\s+', part):
                tokens.append(Token(text=part, is_word=False, aksharas=[]))
            else:
                # It's a word, separate into Aksharas
                # Remove hyphens for segmentation analysis if necessary
                clean_part = part.replace('-', '')
                aksharas = TeluguTokenizer.syllabify(clean_part)
                tokens.append(Token(text=part, is_word=True, aksharas=aksharas))
                
        return tokens

    @staticmethod
    def syllabify(word: str) -> List[Akshara]:
        """
        Core Standard Algorithm to segment a Telugu word into Aksharas.
        
        An 'Akshara' in Telugu Prosody is a syllable unit that allows weight calculation.
        """
        chars = list(word)
        aksharas = []
        current_chars = []
        
        i = 0
        while i < len(chars):
            char = chars[i]
            
            # Skip non-Telugu characters (punctuation, numbers, etc.)
            if not (is_achchu(char) or is_hallu(char) or is_gunintham(char) or is_modifier(char) or is_virama(char)):
                i += 1
                continue
                
            current_chars.append(char)
            
            # An Akshara nucleus is determined by a Vowel principle.
            # Types of completion:
            # 1. Independent Vowel (Achchu)
            # 2. Consonant (Hallu) + Vowel Sign (Gunintham)
            # 3. Consonant (Hallu) + Implicit 'a' (if no virama/gunintham follows)
            
            # Look ahead
            peeks = chars[i+1:]
            is_complete = False
            
            if is_achchu(char):
                # Vowel Core
                if peeks and is_modifier(peeks[0]):
                    current_chars.append(peeks[0])
                    i += 1
                    peeks = peeks[1:]
                
                # Check for Pollu (Final Consonant) only if word-final or special case
                is_complete = True
                
            elif is_hallu(char):
                # Consonant Core
                if peeks and is_gunintham(peeks[0]):
                    # Attach vowel sign
                    current_chars.append(peeks[0])
                    i += 1
                    peeks = peeks[1:]
                    
                    if peeks and is_modifier(peeks[0]):
                        current_chars.append(peeks[0])
                        i += 1
                        peeks = peeks[1:]
                    is_complete = True
                    
                elif peeks and is_virama(peeks[0]):
                    # It's a Consonant Cluster component?
                    # Generally, H+V belongs to the NEXT Akshara as onset.
                    # UNLESS it is Word-Final (Pollu).
                    # We continue accumulating (is_complete=False) so it attaches to next.
                    pass
                    
                else: # Implicit 'a'
                    # It is a complete Akshara 'Ka'
                    if peeks and is_modifier(peeks[0]): 
                        current_chars.append(peeks[0])
                        i += 1
                    is_complete = True
            
            elif is_modifier(char):
                # Should have been eaten. If here, it's start of string or broken.
                is_complete = True
            
            # --- Pollu (Coda) Handling ---
            # If we formed a complete syllable [Onset + Nucleus], we define the boundary.
            # But if a word-final consonant follows (N+Virama at EOS), it is Coda.
            
            if is_complete:
                # Check lookahead for Word-Final Pollu
                p_idx = i + 1
                if p_idx < len(chars) and is_hallu(chars[p_idx]):
                    if p_idx + 1 < len(chars) and is_virama(chars[p_idx+1]):
                        # Found H + V sequence.
                        after_pol_idx = p_idx + 2
                        is_word_end = (after_pol_idx >= len(chars))
                        
                        # Only eat if word end. If middle, it's onset of next.
                        if is_word_end:
                            current_chars.append(chars[p_idx])
                            current_chars.append(chars[p_idx+1])
                            i += 2
                
                akshara_text = "".join(current_chars)
                aksharas.append(Akshara(
                    text=akshara_text, 
                    components=list(current_chars), # Copy
                    has_pollu=akshara_text.endswith(tuple(VIRAMA))
                ))
                current_chars = []
                
            i += 1
            
        # Handle trailing junk
        if current_chars:
             akshara_text = "".join(current_chars)
             aksharas.append(Akshara(text=akshara_text, components=list(current_chars), has_pollu=False))

        return aksharas

# Alias for backwards compatibility functions (if needed internally)
split_word_into_aksharas = TeluguTokenizer.syllabify
split_into_tokens = TeluguTokenizer.split_into_tokens
normalize_text = TeluguTokenizer.normalize


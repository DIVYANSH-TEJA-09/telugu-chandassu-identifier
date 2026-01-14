# telugu_chandas/classifier.py

from typing import List
from .models import Akshara, Token, Weight

def classify_token_weights(tokens: List[Token]):
    """
    Classifies the weight of aksharas in the given tokens.
    Modifies the tokens in-place.
    
    Logic:
    - Builds a continuous chain of Aksharas from word tokens.
    - Breaks the chain ONLY at Newlines that are NOT preceded by a hyphen.
    - Applies classification (Intrinsic + Positional) on each chain.
    """
    current_chain: List[Akshara] = []
    
    last_word_ended_with_hyphen = False
    
    for token in tokens:
        if token.is_word:
            # Add aksharas to current chain
            current_chain.extend(token.aksharas)
            
            # Check if this word ends with hyphen (for next line continuity)
            if token.text.strip().endswith('-'):
                last_word_ended_with_hyphen = True
            else:
                last_word_ended_with_hyphen = False
                
        else:
            # Whitespace token
            if '\n' in token.text:
                # It's a line break
                if last_word_ended_with_hyphen:
                    # Hyphenated line break: Continue chain
                    pass
                else:
                    # Real line break: End chain, Process, Start new
                    if current_chain:
                        classify_chain(current_chain)
                        current_chain = []
            else:
                # Just spaces/tabs: Continue chain
                pass
                
    # Process any remaining chain
    if current_chain:
        classify_chain(current_chain)

def classify_chain(aksharas: List[Akshara]):
    """
    Applies Laghu/Guru rules to a list of Aksharas (representing a line or connected phrase).
    """
    
    # Step 1: Intrinsic Classification
    for akshara in aksharas:
        # Reset first? Or assume None?
        if akshara.is_intrinsic_guru:
            akshara.weight = Weight.GURU
        else:
            akshara.weight = Weight.LAGHU
            
    # Step 2: Positional Classification (Lookahead)
    # Applied across the entire chain.
    for i in range(len(aksharas) - 1):
        current = aksharas[i]
        next_akshara = aksharas[i+1]
        
        # If current is already Guru, no change needed.
        if current.weight == Weight.GURU:
            continue
            
        # Check next akshara's onset count (Samyukta/Dvitva)
        # onset_hallulu_count returns the number of H+V patterns (pure consonants)
        # before the nucleus consonant. If >= 1, there's a conjunct (2+ total consonants).
        if next_akshara.onset_hallulu_count >= 1:
            current.weight = Weight.GURU

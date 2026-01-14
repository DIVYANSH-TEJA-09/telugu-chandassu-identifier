# telugu_chandas/tokenizer.py

import re
from typing import List
from .models import Akshara, Token
from .constants import (
    ACHCHULU, HALLULU, GUNINTHALU, MODIFIERS, VIRAMA,
    is_achchu, is_hallu, is_gunintham, is_modifier, is_virama
)

def normalize_text(text: str) -> str:
    """
    Normalize text:
    - Standard whitespace cleanup.
    """
    return text.strip()

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
            # Remove hyphens for segmentation analysis (phonetically irrelevant)
            # but keep them in the Token.text for display/logic
            clean_part = part.replace('-', '')
            aksharas = split_word_into_aksharas(clean_part)
            tokens.append(Token(text=part, is_word=True, aksharas=aksharas))
            
    return tokens

def split_word_into_aksharas(word: str) -> List[Akshara]:
    """
    Core logic to segment a Telugu word into Aksharas.
    
    Rules for valid Akshara:
    1. A (Achchu)
    2. H + (G)? + (U)?
    3. (H + V + H)+ + (G)? + (U)?
    
    The tricky part is keeping (H+V) attached to PREVIOUS if it's a Pollu at end of word/syllable?
    Prompt: "Word-final pollu makes previous Akshara Guru".
    User Update: "Syllable ending in Pollu is Guru... merge Pollu with the preceding Akshara".
    
    Algorithm:
    1. Scan characters.
    2. Group into 'Syllabic Units' based on Vowel Nucleus.
       - A Vowel (A or G) ends the core of an Akshara.
       - Modifiers (U) attach to the preceding Vowel.
    3. Handle Virama (V):
       - H + V + H... -> This is a cluster (Samyukta/Dvitva) STARTING an Akshara.
       - H + V (at end of unit or followed by non-H?) -> Pollu.
       
    Let's iterate and build.
    """
    chars = list(word)
    aksharas = []
    current_chars = []
    
    i = 0
    while i < len(chars):
        char = chars[i]
        current_chars.append(char)
        
        # Check if we have formed a complete Akshara core
        # Valid endings for a core:
        # 1. Independent Vowel (A)
        # 2. Hallu + Gunintham (H + G)
        # 3. Hallu (if we assume 'implicit schwa' - but definitions say A is explict.
        #    Wait, in Telugu script, 'Ka' is K+a. 'K' is K+Virama.
        #    So 'Ka' (single char) is an Akshara.
        #    If chars[i] is Hallu, does it have implicit vowel? Yes.
        #    Unless followed by Virama or Gunintham.
        
        # Let's peek ahead to decide boundaries.
        peeks = chars[i+1:]
        
        is_complete = False
        
        if is_achchu(char):
            # Independent vowel.
            # Can be followed by Modifier (U)
            if peeks and is_modifier(peeks[0]):
                current_chars.append(peeks[0])
                i += 1
                peeks = peeks[1:] # update peek
            
            # Now, check for Pollu (H + V) merging.
            # If the NEXT thing is H, and the thing AFTER is V, and the thing AFTER that is NOT H (or EOS).
            # Then that H+V is a Pollu and should attach here.
            # BUT, wait. If next is H+V+H, that's a Samyukta/Dvitva for the NEXT akshara.
            # So Pollu only happens if H+V is NOT followed by H?
            # Or if strictly word-final?
            # Prompt: "Word-final pollu makes previous Akshara Guru".
            # User: "Syllable ending in Pollu... merge locally".
            
            # Logic: If we see Hallu + Virama, check what follows.
            # If (H + V) is followed by another Hallu, it's usually part of the NEXT Akshara (Samyukta).
            # UNLESS it is an explict Pollu usage in the middle of a word (rare in modern, common in Chandas).
            # Actually, in generic Telugu text processing: 
            # 'K' + 'V' + 'Y' + 'A' -> 'K' is part of 'kya'. 'KV' is not an akshara on its own.
            # 'N' + 'V' -> 'n' (Pollu).
            
            # Revised Logic:
            # An Akshara logic is driven by VOWELS.
            # Every Vowel (Achchu or Implicit in Hallu or Explicit Gunintham) creates an Akshara nucleus.
            # Consonants before it are the Onset.
            # Modifiers/Pollu after it are the Coda.
            
            # Special case: Hallu is implicitly H + a.
            # So 'K' is an Akshara.
            # 'K' + 'V' is NOT an Akshara (it's part of onset of next, or coda of current).
            
            is_complete = True
            
        elif is_hallu(char):
            # It's a consonant.
            # Check next:
            if peeks and is_gunintham(peeks[0]):
                # Needs to attach.
                current_chars.append(peeks[0])
                i += 1
                peeks = peeks[1:]
                
                # Check modifier
                if peeks and is_modifier(peeks[0]):
                    current_chars.append(peeks[0])
                    i += 1
                    peeks = peeks[1:]
                
                is_complete = True
                
            elif peeks and is_virama(peeks[0]):
                # It has a virama. It is Pure Consonant.
                # It usually belongs to the NEXT Akshara as onset, OR PREVIOUS as coda.
                # Wait, this loop is "accumulating current Akshara".
                # If we just finished a Valid Akshara (is_complete=True), we stop.
                # BUT, what if this Hallu is actually the start of THIS Akshara?
                # Case: "Sva" -> S + V + V + A.
                # Loop step 1: S. Next is V.
                # So S+V is not complete. Continue accumulating.
                
                # So we only set is_complete if we hit a VOWEL nucleus.
                pass
                
            elif peeks and is_achchu(peeks[0]):
                # K + A ? No, Achchu follows Hallu only if separate word or broken.
                # Assume separate. Current 'K' (implicit 'a') is complete.
                is_complete = True
                
            else:
                # Value is just 'K' (plus implicit 'a').
                # Followed by another Hallu or EOS.
                # It is a complete Akshara 'Ka'.
                
                # Check modifier for implicit vowel 'Ka' + 'sunna'
                if peeks and is_modifier(peeks[0]):
                    current_chars.append(peeks[0])
                    i += 1
                    
                is_complete = True
        
        elif is_modifier(char):
            # Modifier shouldn't start an akshara (unless malformed text).
            # Attach to previous if possible?
            # For now treat as standalone if found at start (error case).
            is_complete = True
            
        # If we think we are done, we must check for "Pollu" coda.
        # Pollu = Hallu + Virama that does NOT lead into another vowel.
        # Effectively, if we have a "Complete Akshara", we look ahead.
        # If we see H + V (and NOT followed by H?), we might eat it.
        # BUT: "K + V + Y + A". "K+V" is onset of "YA".
        # "K + A + N + V". "N+V" is Pollu.
        
        # How to distinguish?
        # A Pollu (Coda) is H+V that is NOT the start of the next akshara's onset.
        # The next akshara MUST have a nucleus.
        # If H+V is followed by H+V+...Nucleus, it is likely the Onset of that Nucleus.
        # Standard Syllabification: Onset Maximization used?
        # NO. Telugu Chandas is specific.
        # "N + V" at end of word is Pollu. -> GURU.
        # "N + V" inside word "Bo-N-Dha"? -> usually "Bon-Dha". N is part of first syllable?
        # Actually, "Bo-N-Dha" is usually written with Sunna or specific conjunct.
        # If written B+o+N+V+Dh+a.
        # B+o is Akshara 1.
        # Dh+a is Akshara 2.
        # N+V is in between.
        # Does it belong to 1 or 2?
        # If 1: [Bon] [Dha]. [Bon] is Guru.
        # If 2: [Bo] [Ndha]. [Bo] is Guru (Positional Samyukta).
        # Outcome is similar for Weight of 1.
        # BUT, the segmentation matters. 
        # Textbook rule: Samyuktakshara (Conjunct) makes PREVIOUS Guru.
        # Meaning the Conjunct itself (N+dh) is the ONSET of the NEXT syllable.
        # So "Bo" is one akshara. "Ndha" is the next.
        # "Bo" becomes Guru because of "Ndha".
        
        # SO: H+V sequences usually belong to the NEXT akshara as Onset.
        # EXCEPTION: Word-Final Pollu.
        # OR: Explicit Pollu that is NOT followed by a Hallu? (e.g. followed by punctuation or nothing).
        
        # Refined Logic:
        # 1. Accumulate Onset (sequence of H+V...H+V).
        # 2. Identify Nucleus (H with implicit, or H+G, or A).
        # 3. Absorb Modifiers (U).
        # 4. STOP. The Akshara is done.
        # 5. UNLESS: Next is H+V + (End of Word or Non-Hallu?).
        #    If Next is H+V and it's the END of the word, we consume it as Coda.
        
        if is_complete:
            # We formed a core [Onset + Nucleus + Coda_U].
            
            # Check for generic Pollu tail.
            # Look ahead for H + V pattern.
            p_idx = i + 1
            if p_idx < len(chars) and is_hallu(chars[p_idx]):
                if p_idx + 1 < len(chars) and is_virama(chars[p_idx+1]):
                    # Found H + V.
                    # Check what is AFTER.
                    after_pol_idx = p_idx + 2
                    is_word_end = (after_pol_idx >= len(chars))
                    
                    if is_word_end:
                        # Yes, it is word-final Pollu. Eat it.
                        current_chars.append(chars[p_idx])
                        current_chars.append(chars[p_idx+1])
                        i += 2
                    else:
                        # Not word end.
                        # Do we eat it?
                        # If followed by another Hallu -> "Ka-R-Ma". K+a R+V M+a.
                        # R+V is likely start of "Ma" (Samyukta).
                        # So we leave it for the next Akshara.
                        pass
                        
            # Finalize this Akshara
            akshara_text = "".join(current_chars)
            # Create object
            # (Simplification: We don't fill detailed components yet, just text)
            aksharas.append(Akshara(text=akshara_text, components=current_chars, has_pollu=akshara_text.endswith('\u0c4d'))) # check virama
            
            # Reset
            current_chars = []
            
        i += 1
        
    return aksharas

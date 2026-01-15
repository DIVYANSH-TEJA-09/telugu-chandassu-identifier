# telugu_chandas/engine.py

from typing import List
from .models import Token, Akshara, IdentificationResult
from .tokenizer import TeluguTokenizer
from .analyzer import ProsodyAnalyzer
from .identifier import ChandasIdentifier

class ChandasEngine:
    """
    Main entry point for Telugu Chandas analysis.
    Acts as a Facade over Tokenizer, Analyzer, and Identifier.
    """
    
    def analyze(self, text: str) -> List[Token]:
        """
        Analyzes the input text and returns a list of Tokens with Aksharas classified (Laghu/Guru).
        """
        # 1. Normalize & Tokenize
        norm_text = TeluguTokenizer.normalize(text)
        tokens = TeluguTokenizer.split_into_tokens(norm_text)
        
        # 2. Classify Weights (Context-aware, with Wall and Hyphen rules)
        # WALL RULE: Whitespace = true boundary. Samyukta in Word B does NOT affect Word A.
        # HYPHEN RULE: Hyphen at end of word = continuation. Samyukta in next word DOES affect this word's last akshara.
        
        # First, build a list of (word_token, ends_with_hyphen) pairs
        word_tokens = [(t, t.text.endswith('-')) for t in tokens if t.is_word]
        
        for idx, (t, ends_with_hyphen) in enumerate(word_tokens):
            aksharas = t.aksharas
            n_ak = len(aksharas)
            
            for i, ak in enumerate(aksharas):
                is_last_akshara = (i + 1 == n_ak)
                
                if is_last_akshara:
                    # Special handling for word-final akshara
                    if ends_with_hyphen:
                        # Hyphen continuation: look at next word's first akshara
                        next_word_idx = idx + 1
                        if next_word_idx < len(word_tokens):
                            next_word_aksharas = word_tokens[next_word_idx][0].aksharas
                            nxt = next_word_aksharas[0] if next_word_aksharas else None
                        else:
                            nxt = None
                    else:
                        # Normal word end (wall): no cross-word effect
                        nxt = None
                else:
                    # Not last akshara: look at next akshara in same word
                    nxt = aksharas[i + 1]
                
                ProsodyAnalyzer.get_weight(ak, nxt)
            
        return tokens

    def identify_meter(self, text: str) -> IdentificationResult:
        """
        Identifies the meter of the given text using the robust registry.
        """
        tokens = self.analyze(text)
        lines = self.split_tokens_into_lines(tokens)
        
        identifier = ChandasIdentifier()
        return identifier.identify(lines)

    def split_tokens_into_lines(self, tokens: List[Token]) -> List[List[Akshara]]:
        """
        Groups aksharas by line based on newline tokens.
        """
        lines = []
        current_line_aksharas = []
        
        for token in tokens:
            if '\n' in token.text:
                if current_line_aksharas:
                    lines.append(current_line_aksharas)
                    current_line_aksharas = []
            elif token.is_word:
                current_line_aksharas.extend(token.aksharas)
                
        if current_line_aksharas:
            lines.append(current_line_aksharas)
            
        return lines

    def debug_output(self, text: str) -> str:
        """
        Returns a detailed string representation of the analysis for debugging.
        """
        tokens = self.analyze(text)
        output = []
        
        for token in tokens:
            if token.is_word:
                word_str = f"Word: '{token.text}'\n"
                for akshara in token.aksharas:
                    w = akshara.weight
                    val = w.value if w else "?"
                    name = w.name if w else "Unknown"
                    word_str += f"  - {akshara.text}: {name} ({val})\n"
                output.append(word_str)
                
        return "\n".join(output)


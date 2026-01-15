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
        
        # 2. Classify Weights (Context-aware)
        # We need to flatten to a list of aksharas to handle cross-word context (e.g., Samyukta at start of next word)
        # But our current get_weight handles local context. 
        # Ideally, we should iterate all aksharas in sequence.
        
        all_aksharas = []
        for t in tokens:
            if t.is_word:
                all_aksharas.extend(t.aksharas)
                
        # Calculate weights
        for i, ak in enumerate(all_aksharas):
            nxt = all_aksharas[i+1] if i + 1 < len(all_aksharas) else None
            # This updates the 'weight' attribute on the Akshara object in-place
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


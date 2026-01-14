# telugu_chandas/engine.py

from typing import List, Tuple
from .models import Token, Akshara
from .tokenizer import normalize_text, split_into_tokens
from .classifier import classify_token_weights

class ChandasEngine:
    """
    Main entry point for Telugu Chandas analysis.
    """
    
    def analyze(self, text: str) -> List[Token]:
        """
        Analyzes the input text and returns a list of Tokens with Aksharas classified.
        """
        # 1. Normalize
        norm_text = normalize_text(text)
        
        # 2. Tokenize
        tokens = split_into_tokens(norm_text)
        
        # 3. Classify
        classify_token_weights(tokens)
        
        return tokens

    def get_laghu_guru_sequence(self, text: str) -> str:
        """
        Returns a simple string string of I/U weights for the text.
        Ignores whitespace in output string? 
        Usually Chandas strings are block based.
        We'll return a space-separated string per word.
        """
        tokens = self.analyze(text)
        result_parts = []
        
        for token in tokens:
            if token.is_word:
                weights = "".join([a.weight.value for a in token.aksharas if a.weight])
                result_parts.append(weights)
            # else: whitespace, ignore or preserve?
            # Usually we want the pattern.
        
        return " ".join(result_parts)

    def debug_output(self, text: str) -> str:
        """
        Returns a detailed string representation of the analysis.
        """
        tokens = self.analyze(text)
        output = []
        
        for token in tokens:
            if token.is_word:
                word_str = f"Word: '{token.text}'\n"
                for akshara in token.aksharas:
                    word_str += f"  - {akshara.text}: {akshara.weight.name} ({akshara.weight.value})\n"
                    # Add explanation
                    reasons = []
                    if akshara.is_intrinsic_guru:
                        reasons.append("Intrinsic Guru")
                    if akshara.weight.value == "U" and not akshara.is_intrinsic_guru:
                        reasons.append("Positional Guru")
                    
                    word_str += f"    Reason: {', '.join(reasons) if reasons else 'Laghu'}\n"
                output.append(word_str)
                
        return "\n".join(output)
    def split_tokens_into_lines(self, tokens: List[Token]) -> List[List[Akshara]]:
        """
        Groups aksharas by line based on newline tokens.
        Returns a list of lists of Aksharas.
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

    def identify_meter(self, text: str):
        """
        Identifies the meter of the given text.
        """
        tokens = self.analyze(text)
        lines = self.split_tokens_into_lines(tokens)
        
        from .identifier import ChandasIdentifier
        identifier = ChandasIdentifier()
        return identifier.identify(lines)

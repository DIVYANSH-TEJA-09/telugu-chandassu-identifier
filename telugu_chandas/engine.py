# telugu_chandas/engine.py

from typing import List
from .models import Token, Akshara, IdentificationResult
from .tokenizer import TeluguTokenizer
from .analyzer import ProsodyAnalyzer
from .identifier import ChandasIdentifier
from .jati_identifier import JatiIdentifier

class ChandasEngine:
    """
    Main entry point for Telugu Chandas analysis.
    Acts as a Facade over Tokenizer, Analyzer, and Identifier.
    """
    
    def analyze(self, text: str, force_hyphen_at_line_ends: bool = False) -> List[Token]:
        """
        Analyzes the input text and returns a list of Tokens with Aksharas
        classified (Laghu/Guru).

        force_hyphen_at_line_ends:
            When True, the last word of every line is treated as if it ends
            with a hyphen — i.e., the samyukta/dwitwa onset of the first word
            on the next line is allowed to make the line-final akshara Guru.
            Used as a retry pass when the poet may have omitted the hyphen.
        """
        # 1. Normalize & Tokenize
        norm_text = TeluguTokenizer.normalize(text)
        tokens = TeluguTokenizer.split_into_tokens(norm_text)

        # 2. Classify Weights (Context-aware, with Wall and Hyphen rules)
        # WALL RULE:   Space boundary → samyukta in next word does NOT affect
        #              the current word's last akshara.
        # HYPHEN RULE: Word ends with '-' → the wall is broken; samyukta in the
        #              very next word CAN make this word's last akshara Guru.

        # Identify which word-token indices are the last word before a newline
        line_end_word_indices: set = (
            self._find_line_end_word_indices(tokens)
            if force_hyphen_at_line_ends
            else set()
        )

        # Build (token, ends_with_hyphen) pairs for all word tokens
        word_tokens = []
        word_idx = 0
        for t in tokens:
            if t.is_word:
                has_hyphen = (
                    t.text.endswith('-')
                    or word_idx in line_end_word_indices
                )
                word_tokens.append((t, has_hyphen))
                word_idx += 1

        for idx, (t, ends_with_hyphen) in enumerate(word_tokens):
            aksharas = t.aksharas
            n_ak = len(aksharas)

            for i, ak in enumerate(aksharas):
                is_last_akshara = (i + 1 == n_ak)

                if is_last_akshara:
                    if ends_with_hyphen:
                        # Hyphen / relaxed line-end: look at next word's onset
                        next_word_idx = idx + 1
                        if next_word_idx < len(word_tokens):
                            next_word_aksharas = word_tokens[next_word_idx][0].aksharas
                            nxt = next_word_aksharas[0] if next_word_aksharas else None
                        else:
                            nxt = None
                    else:
                        # Strict wall: no cross-word positional effect
                        nxt = None
                else:
                    # Within the same word: normal lookahead
                    nxt = aksharas[i + 1]

                ProsodyAnalyzer.get_weight(ak, nxt)

        return tokens

    @staticmethod
    def _find_line_end_word_indices(tokens: List[Token]) -> set:
        """
        Returns the 0-based indices (in word-token order) of words that are
        immediately followed by a newline token — i.e., the last word of
        each line.

        Example for tokens [word1, ' ', word2, '\\n', word3]:
            word1 → index 0, word2 → index 1 (last before \\n), word3 → index 2
            Returns {1}
        """
        result: set = set()
        word_idx = 0
        last_seen_word_idx = None

        for tok in tokens:
            if tok.is_word:
                last_seen_word_idx = word_idx
                word_idx += 1
            elif '\n' in tok.text:
                if last_seen_word_idx is not None:
                    result.add(last_seen_word_idx)
                last_seen_word_idx = None   # reset — next word starts a new line

        return result

    # Confidence below this level triggers the missing-hyphen retry pass.
    _HYPHEN_RETRY_THRESHOLD = 80.0

    def identify_meter(self, text: str) -> IdentificationResult:
        """
        Identifies the meter of the given text.

        Pass 1 — strict wall rule (explicit hyphens only).
        Pass 2 — if Pass 1 confidence < threshold, retry treating every
                 line-final word as hyphenated (author may have omitted '-').
                 If Pass 2 scores higher, its result is returned with a note.
        """
        best = self._identify_pass(text, force_hyphen_at_line_ends=False)

        if best.confidence_score < self._HYPHEN_RETRY_THRESHOLD:
            relaxed = self._identify_pass(text, force_hyphen_at_line_ends=True)

            if relaxed.confidence_score > best.confidence_score:
                relaxed.notes.append(
                    "గమనిక: పాద చివరి పదంలో హైఫన్ (-) వదిలిపెట్టబడి ఉండవచ్చు; "
                    "సంయుక్తాక్షర నియమం సడలించి పునఃపరీక్ష చేయబడింది."
                )
                return relaxed

        return best

    def _identify_pass(
        self, text: str, force_hyphen_at_line_ends: bool
    ) -> IdentificationResult:
        """Single identification pass with the given wall-rule setting."""
        tokens = self.analyze(text, force_hyphen_at_line_ends=force_hyphen_at_line_ends)
        lines  = self.split_tokens_into_lines(tokens)

        vritta = ChandasIdentifier().identify(lines)
        jati   = JatiIdentifier().identify(lines)

        return vritta if vritta.confidence_score >= jati.confidence_score else jati

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


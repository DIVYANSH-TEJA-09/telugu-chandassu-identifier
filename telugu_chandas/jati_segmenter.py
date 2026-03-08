# telugu_chandas/jati_segmenter.py

from typing import List, Optional, Tuple
from .gana import SURYA_GANAS, INDRA_GANAS, KANDAM_GANAS


def segment_surya_indra(
    weight_str: str,
    type_sequence: List[str]
) -> Optional[List[Tuple[str, str]]]:
    """
    Segments a weight string into Surya (S) / Indra (I) ganas following
    the given type_sequence.  Uses backtracking so ambiguous lengths are
    handled correctly.

    Returns a list of (gana_name, pattern) tuples on success, or None if
    no valid segmentation exists.
    """
    def backtrack(pos: int, seq_idx: int, result: list) -> Optional[list]:
        if seq_idx == len(type_sequence):
            # All slots consumed — valid only if we used the whole string
            return result if pos == len(weight_str) else None

        gana_type = type_sequence[seq_idx]
        candidates = SURYA_GANAS if gana_type == "S" else INDRA_GANAS

        for pattern, name in candidates.items():
            end = pos + len(pattern)
            if weight_str[pos:end] == pattern:
                r = backtrack(end, seq_idx + 1, result + [(name, pattern)])
                if r is not None:
                    return r
        return None

    return backtrack(0, 0, [])


def segment_kandam(weight_str: str) -> Optional[List[Tuple[str, str]]]:
    """
    Segments a weight string into Kandam ganas.
    Every Kandam gana is exactly 4 matras (U=2, I=1).
    Accumulates aksharas until we reach exactly 4 matras; if we ever
    overshoot, the string is not valid Kandam.

    Returns a list of (gana_name, pattern) tuples, or None if invalid.
    """
    ganas = []
    chunk_chars: List[str] = []
    accumulated = 0

    for char in weight_str:
        matra = 2 if char == 'U' else 1

        if accumulated + matra > 4:
            return None  # Overshoot — not segmentable into 4-matra chunks

        chunk_chars.append(char)
        accumulated += matra

        if accumulated == 4:
            pattern = "".join(chunk_chars)
            if pattern not in KANDAM_GANAS:
                return None  # 4-matra chunk but not an allowed Kandam gana
            ganas.append((KANDAM_GANAS[pattern], pattern))
            chunk_chars = []
            accumulated = 0

    if accumulated != 0:
        return None  # Leftover matras at end

    return ganas


def gana_start_indices(ganas: List[Tuple[str, str]]) -> List[int]:
    """
    Returns the starting akshara index (0-based) for each gana in the list.

    E.g., for [("భ","UII"), ("నల","IIII"), ("గల","UI")] → [0, 3, 7]
    """
    indices = []
    pos = 0
    for _name, pattern in ganas:
        indices.append(pos)
        pos += len(pattern)
    return indices

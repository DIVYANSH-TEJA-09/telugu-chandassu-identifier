# telugu_chandas/identifier.py

from typing import List, Dict
from collections import Counter
from .models import Akshara, IdentificationResult, Weight
from .registry import MeterRegistry, MeterDefinition
from .validator import RuleValidator
from .analyzer import ProsodyAnalyzer

class ChandasIdentifier:
    """
    Identifies the meter of a given set of aksharas lines.
    """
    
    def identify(self, lines_of_aksharas: List[List[Akshara]]) -> IdentificationResult:
        """
        Main identification logic.
        """
        if not lines_of_aksharas:
            return IdentificationResult("Unknown", "0%", 0.0, [], False, False, ["No text provided"])

        total_lines = len(lines_of_aksharas)
        
        # 1. Vote for Candidate Meter
        candidate_counts: Dict[str, int] = {} 
        candidate_map: Dict[str, MeterDefinition] = {}
        lines_ganas = []
        
        for line in lines_of_aksharas:
            # Use pre-calculated weights if available (from Engine), else fallback to local scan
            weights = []
            for i, ak in enumerate(line):
                if ak.weight:
                    weights.append(ak.weight.value)
                else:
                    # Fallback logic (without cross-line context)
                    nxt = line[i+1] if i+1 < len(line) else None
                    weights.append(ProsodyAnalyzer.get_weight(ak, nxt).value)
            
            w_str = "".join(weights)
            ganas = ProsodyAnalyzer.get_ganas(w_str)
            lines_ganas.append(ganas)
            
            meters = MeterRegistry.find_by_ganas(ganas)
            for m in meters:
                candidate_counts[m.name] = candidate_counts.get(m.name, 0) + 1
                candidate_map[m.name] = m
                
        if not candidate_counts:
            return IdentificationResult("Unknown", "0.0%", 0.0, lines_ganas[0], False, False, ["No matching Vritta pattern found in any line"])
            
        best_meter_name = max(candidate_counts, key=candidate_counts.get)
        target_meter = candidate_map[best_meter_name]
        
        # 2. Calculate Confidence
        
        # A. Gana Score (60%)
        gana_matches = 0
        notes = []
        for idx, ganas in enumerate(lines_ganas):
            if ganas == target_meter.gana_sequence:
                gana_matches += 1
            else:
                # Check for Optional Samyukta Rule (Ra-vatthu) - Localized Fix
                line = lines_of_aksharas[idx]
                corrected_weights = []
                
                # Get base weights
                base_weights = []
                relaxable_indices = set()
                
                for i, ak in enumerate(line):
                    w_val = ak.weight.value if ak.weight else "I"
                    base_weights.append(w_val)
                    
                    # Check relaxability
                    if w_val == "U" and not ak.is_intrinsic_guru:
                        nxt = line[i+1] if i+1 < len(line) else None
                        if nxt:
                            has_ra = False
                            from .constants import is_hallu, VIRAMA
                            for c in nxt.components:
                                if not is_hallu(c) and c not in VIRAMA: break
                                if c == 'ర' or c == 'ఱ':
                                    has_ra = True
                                    break
                            if has_ra:
                                relaxable_indices.add(i)

                # Process chunk by chunk
                final_ganas = []
                current_w_str = list(base_weights)
                
                target_seq = target_meter.gana_sequence
                
                # Chunk size 3
                for chunk_idx in range(len(target_seq)):
                    start = chunk_idx * 3
                    end = start + 3
                    if start >= len(current_w_str): break
                    
                    chunk_weights = current_w_str[start:end]
                    chunk_str = "".join(chunk_weights)
                    
                    # Get current gana
                    curr_gana = ProsodyAnalyzer.get_ganas(chunk_str)[0]
                    target_gana = target_seq[chunk_idx]
                    
                    if curr_gana == target_gana:
                        final_ganas.append(curr_gana)
                    else:
                        # Try relaxing indices in this chunk
                        chunk_relaxables = [ix for ix in range(start, min(end, len(current_w_str))) if ix in relaxable_indices]
                        
                        found_fix = False
                        if chunk_relaxables:
                            # Try all combinations (max 3 indices = 8 combos, usually 1)
                            import itertools
                            for r_count in range(1, len(chunk_relaxables) + 1):
                                for comb in itertools.combinations(chunk_relaxables, r_count):
                                    # Create temp chunk
                                    temp_chunk = list(chunk_weights)
                                    for r_idx in comb:
                                        local_r = r_idx - start
                                        temp_chunk[local_r] = "I"
                                    
                                    if ProsodyAnalyzer.get_ganas("".join(temp_chunk))[0] == target_gana:
                                        # Success! Apply to current_w_str
                                        for r_idx in comb:
                                            current_w_str[r_idx] = "I"
                                        final_ganas.append(target_gana)
                                        found_fix = True
                                        break
                                if found_fix: break
                        
                        if not found_fix:
                             final_ganas.append(curr_gana)

                # Remaining (partial gana at end)
                if len(final_ganas) < len(target_seq):
                    # Handle leftovers? Usually assumed covered
                    pass
                
                # Re-verify full sequence match
                if final_ganas == target_seq:
                    gana_matches += 1
                    notes.append(f"Line {idx+1}: Matched using Optional Rule (Ra-vatthu) ✅")
                else:
                    notes.append(f"Line {idx+1} Gana Mismatch: Found {ganas}") # Keep original mismatch in notes or partial?
                    # Maybe updated one?
                    # notes.append(f"Line {idx+1} Gana Mismatch: Found {final_ganas}")
        gana_score = (gana_matches / total_lines) * 60.0
        
        # B. Yati Score (20%)
        yati_matches = 0
        yati_notes = []
        yati_pos = target_meter.yati_position
        
        for idx, line in enumerate(lines_of_aksharas):
            if len(line) >= yati_pos:
                ak_start = line[0]
                ak_yati = line[yati_pos - 1]
                
                is_match, reason = RuleValidator.check_yati_match(ak_start, ak_yati)
                if is_match:
                    yati_matches += 1
                    yati_notes.append(f"L{idx+1}: {reason}✅")
                else:
                    yati_notes.append(f"L{idx+1}: {reason}❌")
            else:
                yati_notes.append(f"L{idx+1}: Short❌")
        yati_score = (yati_matches / total_lines) * 20.0
        
        # C. Prasa Score (20%)
        # Identify dominant prasa
        prasa_cons_list = []
        for line in lines_of_aksharas:
            if len(line) >= 2:
                # We need ONLY the ONSET consonants for Prasa (excluding coda)
                cons = RuleValidator.get_akshara_consonants(line[1])
                prasa_cons_list.append(tuple(cons))
            else:
                prasa_cons_list.append(None)
                
        valid_prasas = [p for p in prasa_cons_list if p is not None]
        prasa_matches = 0
        prasa_info_str = "None"
        
        if valid_prasas:
            most_common = Counter(valid_prasas).most_common(1)[0][0]
            for p in prasa_cons_list:
                if p == most_common:
                    prasa_matches += 1
            prasa_info_str = "+".join(most_common) if most_common else "Achchu"
            
        prasa_score = (prasa_matches / total_lines) * 20.0
        
        # 3. Final Result
        total_score = gana_score + yati_score + prasa_score
        score_breakdown = f"Score: {total_score:.1f}% (Gana: {gana_score:.1f} + Yati: {yati_score:.1f} + Prasa: {prasa_score:.1f})"
        notes.insert(0, score_breakdown)
        
        final_yati_valid = (yati_matches / total_lines) >= 0.5
        final_prasa_valid = (prasa_matches / total_lines) >= 0.5
        
        return IdentificationResult(
            meter_name=target_meter.name,
            confidence=f"{total_score:.1f}%",
            confidence_score=total_score,
            ganas_found=target_meter.gana_sequence,
            yati_valid=final_yati_valid,
            prasa_valid=final_prasa_valid,
            notes=notes,
            yati_notes=yati_notes,
            prasa_note=prasa_info_str
        )

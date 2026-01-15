from typing import List, Optional, Dict
from dataclasses import dataclass
from .models import Akshara, Token, Weight
from .gana import get_ganas_for_vritta
from .registry import find_meter_by_ganas, MeterDefinition
from .chandas_rules import check_yati_match, validate_line_prasa, get_akshara_consonants

@dataclass
class IdentificationResult:
    meter_name: str
    confidence: str # "High", "Medium", "Low" or percentage string
    confidence_score: float # 0-100
    ganas_found: List[str] # Ganas of the *first* line or best matching line? Let's keep first line for display, or maybe list of lists? Existing UI expects a list. Let's return the ganas of the best matching line or the first line if none.
    yati_valid: bool
    prasa_valid: bool
    notes: List[str] # General notes (e.g. score breakdown)
    yati_notes: List[str] = None # Detailed reasons
    prasa_note: str = ""       # "Main Prasa: X"

class ChandasIdentifier:
    def identify(self, lines_of_aksharas: List[List[Akshara]]) -> IdentificationResult:
        if not lines_of_aksharas:
            return IdentificationResult("Unknown", "0%", 0.0, [], False, False, ["No text provided"])

        total_lines = len(lines_of_aksharas)
        
        # 1. Vote for Candidate Meter
        # Scan all lines to find potential meters
        candidate_counts: Dict[str, int] = {} 
        candidate_map: Dict[str, MeterDefinition] = {}
        
        # Keep track of ganas for each line to avoid re-computing
        lines_ganas = []
        
        for line in lines_of_aksharas:
            w_str = "".join([a.weight.value for a in line if a.weight])
            ganas = get_ganas_for_vritta(w_str)
            lines_ganas.append(ganas)
            
            meters = find_meter_by_ganas(ganas)
            for m in meters:
                candidate_counts[m.name] = candidate_counts.get(m.name, 0) + 1
                candidate_map[m.name] = m
                
        if not candidate_counts:
            # No recognized meter found in ANY line
            # Default to first line's analysis for display
            return IdentificationResult("Unknown", "0.0%", 0.0, lines_ganas[0], False, False, ["No matching Vritta pattern found in any line"])
            
        # Pick best candidate
        best_meter_name = max(candidate_counts, key=candidate_counts.get)
        target_meter = candidate_map[best_meter_name]
        
        # 2. Calculate Confidence Scores
        
        # A. Gana Score (60%)
        # How many lines match the target meter's gana sequence?
        gana_matches = 0
        notes = []
        
        for idx, ganas in enumerate(lines_ganas):
            if ganas == target_meter.gana_sequence:
                gana_matches += 1
            else:
                notes.append(f"Line {idx+1} Gana Mismatch: Found {ganas}")
                
        gana_score = (gana_matches / total_lines) * 60.0
        
        # B. Yati Score (20%)
        yati_matches = 0
        yati_notes = []
        yati_pos = target_meter.yati_position
        
        for idx, line in enumerate(lines_of_aksharas):
            if len(line) >= yati_pos:
                ak_start = line[0]
                ak_yati = line[yati_pos - 1]
                
                is_match, reason = check_yati_match(ak_start, ak_yati)
                if is_match:
                    yati_matches += 1
                    yati_notes.append(f"L{idx+1}: {reason}✅")
                else:
                    yati_notes.append(f"L{idx+1}: {reason}❌")
            else:
                yati_notes.append(f"L{idx+1}: Short❌")
                
        yati_score = (yati_matches / total_lines) * 20.0
        
        # C. Prasa Score (20%)
        # Identify dominant prasa consonant
        from collections import Counter
        prasa_cons_list = []
        
        for line in lines_of_aksharas:
            if len(line) >= 2:
                # Get onset consonants of 2nd akshara
                cons = get_akshara_consonants(line[1])
                # We use a tuple to make it hashable for Counter
                prasa_cons_list.append(tuple(cons))
            else:
                prasa_cons_list.append(None)
                
        # Filter None and count
        valid_prasas = [p for p in prasa_cons_list if p is not None]
        
        prasa_matches = 0
        prasa_info_str = "None"
        
        if valid_prasas:
            # Find most common prasa pattern
            most_common = Counter(valid_prasas).most_common(1)[0][0]
            
            # Count matches
            for p in prasa_cons_list:
                if p == most_common:
                    prasa_matches += 1
            
            prasa_info_str = "+".join(most_common) if most_common else "Achchu"
        
        prasa_score = (prasa_matches / total_lines) * 20.0
        
        # 3. Final Aggregation
        total_score = gana_score + yati_score + prasa_score
        
        score_breakdown = f"Score: {total_score:.1f}% (Gana: {gana_score:.1f} + Yati: {yati_score:.1f} + Prasa: {prasa_score:.1f})"
        notes.insert(0, score_breakdown)
        
        # Determine strict validity booleans for UI badges (using > 50% threshold or strict?)
        # For UI badges "Valid/Invalid", let's use a reasonable threshold
        # Yati is valid if score > 15 (approx 75% lines valid)? Or strict 100%?
        # User defined "20% yati", so if score is 20, it's perfect.
        # Let's say valid if > 50% of lines are valid?
        
        final_yati_valid = (yati_matches / total_lines) >= 0.5
        final_prasa_valid = (prasa_matches / total_lines) >= 0.5
        
        return IdentificationResult(
            meter_name=target_meter.name,
            confidence=f"{total_score:.1f}%",
            confidence_score=total_score,
            ganas_found=target_meter.gana_sequence, # Return the EXPECTED ganas for the identified meter
            yati_valid=final_yati_valid,
            prasa_valid=final_prasa_valid,
            notes=notes,
            yati_notes=yati_notes,
            prasa_note=prasa_info_str
        )

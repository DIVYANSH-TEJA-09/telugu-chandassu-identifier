from typing import List, Optional, Dict
from dataclasses import dataclass
from .models import Akshara, Token, Weight
from .gana import get_ganas_for_vritta
from .registry import find_meter_by_ganas, MeterDefinition
from .chandas_rules import check_yati_match, validate_line_prasa

@dataclass
class IdentificationResult:
    meter_name: str
    confidence: str # "High", "Low", "None"
    ganas_found: List[str]
    yati_valid: bool
    prasa_valid: bool
    notes: List[str]
    yati_notes: List[str] = None # Detailed reasons
    prasa_note: str = ""       # "Main Prasa: X"

class ChandasIdentifier:
    def identify(self, lines_of_aksharas: List[List[Akshara]]) -> IdentificationResult:
        if not lines_of_aksharas:
            return IdentificationResult("Unknown", "None", [], False, False, ["No text provided"])

        # 1. Analyze First Line to find candidate meters (Vritta)
        line1 = lines_of_aksharas[0]
        weight_str = "".join([a.weight.value for a in line1 if a.weight])
        
        # Strategy: Try splitting valid Vritta Ganas
        ganas = get_ganas_for_vritta(weight_str)
        candidates = find_meter_by_ganas(ganas)
        
        if not candidates:
            return IdentificationResult("Unknown", "None", ganas, False, False, ["No matching Vritta pattern found"])
            
        # 2. Pick the best candidate (usually only 1 matches exactly)
        meter = candidates[0] # Take first match
        
        # 3. Validation - Check all lines match the Gana pattern
        ganas_match_all = True
        notes = []
        
        for idx, line in enumerate(lines_of_aksharas):
            w_str = "".join([a.weight.value for a in line if a.weight])
            line_ganas = get_ganas_for_vritta(w_str)
            if line_ganas != meter.gana_sequence:
                ganas_match_all = False
                notes.append(f"Line {idx+1} Gana Mismatch: Found {line_ganas}")
        
        # 4. Yati Validation
        yati_valid = True
        yati_notes = []
        yati_pos = meter.yati_position
        
        for idx, line in enumerate(lines_of_aksharas):
            # Yati is typically 1st letter vs Yati-th letter
            if len(line) >= yati_pos:
                ak_start = line[0]
                ak_yati = line[yati_pos - 1] # 0-indexed
                
                is_match, reason = check_yati_match(ak_start, ak_yati)
                if not is_match:
                    yati_valid = False
                    notes.append(f"Line {idx+1} Yati Fail: {reason}")
                    yati_notes.append(f"L{idx+1}: {reason}❌")
                else:
                    yati_notes.append(f"L{idx+1}: {reason}✅")

            else:
                yati_valid = False
                notes.append(f"Line {idx+1} too short for Yati check")
                yati_notes.append(f"L{idx+1}: Short❌")

        # 5. Prasa Validation
        # Collect 2nd akshara of each line
        second_aksharas = []
        for line in lines_of_aksharas:
            if len(line) >= 2:
                second_aksharas.append(line[1])
        
        prasa_valid, prasa_info = validate_line_prasa(second_aksharas)
        if not prasa_valid:
            notes.append(f"Prasa Fail: {prasa_info}")
            
        return IdentificationResult(
            meter_name=meter.name,
            confidence="High" if ganas_match_all else "Partial",
            ganas_found=ganas,
            yati_valid=yati_valid,
            prasa_valid=prasa_valid,
            notes=notes,
            yati_notes=yati_notes,
            prasa_note=prasa_info
        )

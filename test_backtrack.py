
import sys
import os
sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine
from telugu_chandas.analyzer import ProsodyAnalyzer

engine = ChandasEngine()

poem = """అపరిమిత ప్రీతినా భగీరథుని
తపమిచ్చమెచ్చనే కందర్ప సంహరుని"""

# Test backtracking parser directly
tokens = engine.analyze(poem)
lines = engine.split_tokens_into_lines(tokens)

for idx, line_aksharas in enumerate(lines):
    weights = "".join([ak.weight.value if ak.weight else "?" for ak in line_aksharas])
    print(f"\n=== Line {idx+1} ===")
    print(f"Weights: {weights}")
    
    # Try backtracking with 3I+1S
    ganas, valid = ProsodyAnalyzer.parse_for_structure(weights, "3I+1S")
    print(f"Backtrack 3I+1S: valid={valid}")
    if valid:
        print(f"Ganas: {[g['name'] for g in ganas]}")

# Full identification
print("\n=== Full Identification ===")
result = engine.identify_meter(poem)
print(f"Meter: {result.meter_name} ({result.meter_type})")
print(f"Confidence: {result.confidence}")
if hasattr(result, 'matra_ganas') and result.matra_ganas:
    for i, lg in enumerate(result.matra_ganas):
        print(f"Line {i+1} ganas: {[g['name'] for g in lg]}")

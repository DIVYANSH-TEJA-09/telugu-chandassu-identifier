
import sys
import os
sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine

engine = ChandasEngine()

# Kandam poem from user
kandam = """ఇచ్చున దెవిద్యన రణములనఁ
జొచ్చున దేమగతనంబు సుకవీశ్వరులు
మెచ్చున దెనేర్పు వాదుకు
వచ్చున దేకీడు సుమ్ము వసుధను సుమతీ"""

print("=== Test: Kandam ===")
result = engine.identify_meter(kandam)
print(f"Meter: {result.meter_name} ({result.meter_type})")
print(f"Confidence: {result.confidence}")
print(f"Notes:")
for n in result.notes[:5]:
    print(f"  {n}")

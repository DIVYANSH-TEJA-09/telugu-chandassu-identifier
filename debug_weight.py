from telugu_chandas.engine import ChandasEngine
engine = ChandasEngine()

# Previous clean text had: "భక్తి కంగంబు ప్రా-"
# New hypothesis: "భక్తి కంగంబుగ ప్రా-"
text_fixed = """లింగారాధన జంగమార్చనము లోలిన్ భక్తి కంగంబుగ ప్రా-
ణాంగవ్యాప్తియునై స్ఫురించు నిది తత్త్వార్థంబగుం గాన నా
యంగాభ్యర్చన జంగమాహితకరుండై చేసినం దా శవ-
శృంగారంబగు వాని భక్తి మదిఁ జర్చింపంగ సర్వేశ్వరా!"""

res = engine.identify_meter(text_fixed)

with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write(f"Meter: {res.meter_name}\n")
    f.write(f"Confidence: {res.confidence}\n")
    f.write(f"Ganas: {res.ganas_found}\n")

print("Done")

from telugu_chandas.engine import ChandasEngine
from telugu_chandas.chandas_rules import get_akshara_vowel

def test_meter_identification():
    engine = ChandasEngine()
    
    # User provided poem (Mattebham)
    text = """భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-
భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-
రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-
నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"""
    
    res = engine.identify_meter(text)
    
    with open("test_result.txt", "w", encoding="utf-8") as f:
        f.write("Analyzing User Poem...\n")
        f.write(f"Meter: {res.meter_name} ({res.confidence})\n")
        f.write(f"Yati Valid: {res.yati_valid}\n")
        f.write(f"Prasa Valid: {res.prasa_valid}\n")
        f.write(f"Ganas: {res.ganas_found}\n")
        f.write("Yati Notes:\n")
        if res.yati_notes:
            for n in res.yati_notes:
                f.write(f"- {n}\n")
            
        if not res.yati_valid:
             f.write("\n--- Yati Debug ---\n")
             lines = engine.split_tokens_into_lines(engine.analyze(text))
             for idx, line in enumerate(lines):
                if len(line) >= 14:
                    ak1 = line[0]
                    ak2 = line[13] # 14th
                    v1 = get_akshara_vowel(ak1)
                    v2 = get_akshara_vowel(ak2)
                    f.write(f"Line {idx+1}: '{ak1.text}'({v1}) vs '{ak2.text}'({v2})\n")

    assert res.meter_name == "Mattebham"
    # assert res.yati_valid == True # Let it run to inspect file
    print("Run completed. Check test_result.txt")

if __name__ == "__main__":
    test_meter_identification()

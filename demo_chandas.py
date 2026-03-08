import sys
import os

sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine

MATTEBHAM = (
    "భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-\n"
    "భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-\n"
    "రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-\n"
    "నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"
)

POEMS = [
    ("Mattebham (Vritta)", MATTEBHAM),
]


def main():
    engine = ChandasEngine()

    print("Telugu Chandas Demo")
    print("=" * 50)

    for title, text in POEMS:
        print(f"\n{title}")
        print("-" * 50)
        result = engine.identify_meter(text)
        print(f"Meter     : {result.meter_name}")
        print(f"Confidence: {result.confidence}")
        print(f"Yati      : {'✓' if result.yati_valid else '✗'}")
        print(f"Prasa     : {'✓' if result.prasa_valid else '✗'} ({result.prasa_note})")
        print(f"Ganas     : {' '.join(result.ganas_found)}")
        if result.yati_notes:
            print("Yati Notes:")
            for note in result.yati_notes:
                print(f"  {note}")
        print("\nWeight Breakdown:")
        print(engine.debug_output(text))


if __name__ == "__main__":
    main()

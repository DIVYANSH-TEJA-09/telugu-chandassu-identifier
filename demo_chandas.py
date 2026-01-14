# demo_chandas.py
import sys
import os

sys.path.insert(0, os.getcwd())

from telugu_chandas.engine import ChandasEngine

def main():
    engine = ChandasEngine()
    
    examples = [
        "రమ",          # Ra (L), Ma (L)
        "కాకి",        # Kaa (G), Ki (L)
        "ఆదిత్య",      # Aa (G), Di (G - Positional), Tya (L)
        "నమస్కా",      # Na (G), Ma (G), Kaa (G) ?
                       # Na (L). Next 'ma'.
                       # Ma (L). Next 'ska'. S+K+A. 2 Hallus.
                       # So Ma -> Guru.
                       # Ska -> Guru (Long A). 
                       # Na is Laghu? Na followed by Ma. Ma starts with M. 1 Hallu.
                       # So Na -> Laghu.
                       # Result: I U U.
        "కన్",         # Kan (G) - Pollu
        "ర మ్య",       # Ra (L) - boundary - Mya (L)
    ]
    
    print("Telugu Chandas Demo\n" + "="*20)
    
    for text in examples:
        print(f"\nScanning: '{text}'")
        seq = engine.get_laghu_guru_sequence(text)
        print(f"Sequence: {seq}")
        print("Details:")
        print(engine.debug_output(text))
        print("-" * 20)

if __name__ == "__main__":
    main()

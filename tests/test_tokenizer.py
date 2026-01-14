# tests/test_tokenizer.py

import unittest
import sys
import os

# Put src on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telugu_chandas.tokenizer import split_into_tokens
from telugu_chandas.constants import VIRAMA

class TestTokenizer(unittest.TestCase):
    
    def test_simple_aksharas(self):
        # 'రమ' -> 'ర', 'మ'
        text = "రమ" 
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens), 1)
        word = tokens[0]
        self.assertEqual(len(word.aksharas), 2)
        self.assertEqual(word.aksharas[0].text, "ర")
        self.assertEqual(word.aksharas[1].text, "మ")

    def test_vowel_aksharas(self):
        # 'అల' -> 'అ', 'ల'
        text = "అల"
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens[0].aksharas), 2)
        self.assertEqual(tokens[0].aksharas[0].text, "అ")
        
    def test_gunintham(self):
        # 'కి' -> 'కి' (Ka + i)
        text = "కి"
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens[0].aksharas), 1)
        self.assertEqual(tokens[0].aksharas[0].text, "కి")
        
    def test_samyuktakshara(self):
        # 'స్వ' -> 'స్వ' (Sa + Virama + Va)
        text = "స్వ"
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens[0].aksharas), 1)
        self.assertEqual(tokens[0].aksharas[0].text, "స్వ")
    
    def test_complex_word(self):
        # 'అమ్మ' -> 'అ', 'మ్మ'
        text = "అమ్మ"
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens[0].aksharas), 2)
        # Assuming splitting A + mma
        self.assertEqual(tokens[0].aksharas[0].text, "అ")
        self.assertEqual(tokens[0].aksharas[1].text, "మ్మ")

    def test_kan(self):
        # 'కన్' -> 'కన్' (Pollu merge)
        # Ka + Na + Virama
        text = "కన్"
        tokens = split_into_tokens(text)
        # Should be 1 word, 1 akshara
        self.assertEqual(len(tokens), 1)
        self.assertEqual(len(tokens[0].aksharas), 1)
        self.assertEqual(tokens[0].aksharas[0].text, "కన్")
        self.assertTrue(tokens[0].aksharas[0].has_pollu)

    def test_hyphenation_tokens(self):
        # "రాము- \nడు" -> Should be 2 word tokens with hyphen preserved in text
        text = "రాము-\nడు"
        from telugu_chandas.tokenizer import normalize_text
        norm = normalize_text(text)
        # Normalization should NOT merge now
        self.assertEqual(norm, "రాము-\nడు")
        
        tokens = split_into_tokens(norm)
        # Token 1: రాము-
        # Token 2: \n (Whitespace)
        # Token 3: డు
        self.assertTrue(len(tokens) >= 3)
        self.assertTrue("రాము-" in tokens[0].text)
        self.assertTrue(tokens[2].text == "డు")  # Assuming index 2 is the next word

    def test_modifiers(self):
        # 'అం' -> 'అం'
        text = "అం"
        tokens = split_into_tokens(text)
        self.assertEqual(len(tokens[0].aksharas), 1)
        self.assertEqual(tokens[0].aksharas[0].text, "అం")

if __name__ == '__main__':
    unittest.main()

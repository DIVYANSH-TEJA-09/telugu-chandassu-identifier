# tests/test_classifier.py

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telugu_chandas.tokenizer import split_into_tokens
from telugu_chandas.classifier import classify_token_weights
from telugu_chandas.models import Weight

class TestClassifier(unittest.TestCase):
    
    def test_intrinsic_laghu(self):
        text = "రమ" # Ra, Ma -> L, L
        tokens = split_into_tokens(text)
        classify_token_weights(tokens)
        
        aksharas = tokens[0].aksharas
        self.assertEqual(aksharas[0].weight, Weight.LAGHU, "Ra should be Laghu")
        self.assertEqual(aksharas[1].weight, Weight.LAGHU, "Ma should be Laghu")

    def test_intrinsic_guru(self):
        text = "కాకి" # Kaa, Ki -> G, L
        tokens = split_into_tokens(text)
        classify_token_weights(tokens)
        
        aksharas = tokens[0].aksharas
        self.assertEqual(aksharas[0].weight, Weight.GURU, "Kaa should be Guru")
        self.assertEqual(aksharas[1].weight, Weight.LAGHU, "Ki should be Laghu")
        
        text2 = "కం" # Kam -> G
        tokens2 = split_into_tokens(text2)
        classify_token_weights(tokens2)
        self.assertEqual(tokens2[0].aksharas[0].weight, Weight.GURU, "Kam should be Guru")

    def test_positional_guru(self):
        # "ఆదిత్య" -> Aa (G), Di (L->G?), Tya (L)
        # Aa is already Guru.
        # Di: Next is Tya. Onset T+Y (2 halls). So Di becomes Guru.
        # Tya: Laghu (ends in short a).
        text = "ఆదిత్య"
        tokens = split_into_tokens(text)
        classify_token_weights(tokens)
        
        aksharas = tokens[0].aksharas
        self.assertEqual(aksharas[0].weight, Weight.GURU, "Aa is Guru")
        self.assertEqual(aksharas[1].weight, Weight.GURU, "Di becomes Guru due to Tya")
        self.assertEqual(aksharas[2].weight, Weight.LAGHU, "Tya is Laghu")

        # "రమ్య" -> Ra (L->G), Mya (L)
        text2 = "రమ్య"
        tokens = split_into_tokens(text2)
        classify_token_weights(tokens)
        
        self.assertEqual(tokens[0].aksharas[0].weight, Weight.GURU, "Ra becomes Guru due to Mya")
        self.assertEqual(tokens[0].aksharas[1].weight, Weight.LAGHU, "Mya is Laghu")

    def test_boundary_rule(self):
        # "ర మ్య" -> Ra (L), Mya (L). Space separates.
        text = "ర మ్య"
        tokens = split_into_tokens(text)
        classify_token_weights(tokens)
        
        # Token 0: Ra
        word1 = tokens[0]
        self.assertEqual(word1.aksharas[0].weight, Weight.LAGHU, "Ra stays Laghu because of boundary")
        
        # Token 1: Space
        
        # Token 2: Mya
        word2 = tokens[2]
        self.assertEqual(word2.aksharas[0].weight, Weight.LAGHU, "Mya is Laghu")

    def test_pollu_weight(self):
        # "కన్" -> Guru.
        text = "కన్"
        tokens = split_into_tokens(text)
        classify_token_weights(tokens)
        
        self.assertEqual(tokens[0].aksharas[0].weight, Weight.GURU, "Kan should be Guru")

if __name__ == '__main__':
    unittest.main()

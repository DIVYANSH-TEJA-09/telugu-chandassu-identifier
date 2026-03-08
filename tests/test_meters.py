import pytest
from telugu_chandas.engine import ChandasEngine

engine = ChandasEngine()

MATTEBHAM = (
    "భవదున్మేషవిజృంభణంబు పరికింపంగా సరోజాతసం-\n"
    "భవు జన్మంబు భవన్నిమేష మమితబ్రహ్మాండకల్పాంత భై-\n"
    "రవసంక్షోభిత మన్నఁ దక్కిన భవత్ప్రారంభభూరిక్రియా-\n"
    "నివహం బెవ్వరు నేర్తు రిట్టిదని వర్ణింపంగ సర్వేశ్వరా!"
)


def test_mattebham_identified():
    result = engine.identify_meter(MATTEBHAM)
    assert result.meter_name == "Mattebham"


def test_mattebham_confidence():
    result = engine.identify_meter(MATTEBHAM)
    assert result.confidence_score >= 80.0


def test_mattebham_yati():
    result = engine.identify_meter(MATTEBHAM)
    assert result.yati_valid is True


def test_mattebham_prasa():
    result = engine.identify_meter(MATTEBHAM)
    assert result.prasa_valid is True


def test_mattebham_gana_count():
    result = engine.identify_meter(MATTEBHAM)
    # Mattebham = Sa Bha Ra Na Ma Ya Va (7 ganas)
    assert len(result.ganas_found) == 7


def test_unknown_meter():
    result = engine.identify_meter("hello world test")
    assert result.meter_name == "Unknown"


def test_empty_input():
    result = engine.identify_meter("")
    assert result.meter_name == "Unknown"


def test_result_has_yati_notes():
    result = engine.identify_meter(MATTEBHAM)
    assert isinstance(result.yati_notes, list)


def test_result_has_prasa_note():
    result = engine.identify_meter(MATTEBHAM)
    assert isinstance(result.prasa_note, str)

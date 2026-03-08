import pytest
from telugu_chandas.jati_segmenter import segment_surya_indra, segment_kandam, gana_start_indices
from telugu_chandas.jati_registry import JatiRegistry


# ---------------------------------------------------------------------------
# segment_surya_indra
# ---------------------------------------------------------------------------

class TestSegmentSuryaIndra:

    def test_dwipada_pada_bha_ganas(self):
        # 3 Indra(UII=భ) + 1 Surya(UI=గల)
        result = segment_surya_indra("UIIUIIUIIUI", ["I", "I", "I", "S"])
        assert result == [("భ", "UII"), ("భ", "UII"), ("భ", "UII"), ("గల", "UI")]

    def test_returns_none_on_weight_mismatch(self):
        # "UUUUUU" cannot be segmented as 3 Indra + 1 Surya
        assert segment_surya_indra("UUUUUU", ["I", "I", "I", "S"]) is None

    def test_returns_none_on_leftover_chars(self):
        # Valid for 3I+1S but has one extra char
        assert segment_surya_indra("UIIUIIUIIUII", ["I", "I", "I", "S"]) is None

    def test_mixed_surya_indra(self):
        # Surya(III=న) + Indra(IIII=నల) + Indra(UII=భ)
        result = segment_surya_indra("IIIIIIIUII", ["S", "I", "I"])
        assert result is not None
        assert result[0] == ("న", "III")
        assert result[1] == ("నల", "IIII")
        assert result[2] == ("భ", "UII")

    def test_taruvoja_pada_8_ganas(self):
        # (3 Indra + 1 Surya) * 2  =  8 ganas
        w = "UII" * 3 + "UI" + "UII" * 3 + "UI"
        structure = ["I", "I", "I", "S", "I", "I", "I", "S"]
        result = segment_surya_indra(w, structure)
        assert result is not None
        assert len(result) == 8
        assert result[3] == ("గల", "UI")
        assert result[7] == ("గల", "UI")

    def test_surya_gala_pattern(self):
        # Single Surya gana గల (UI)
        result = segment_surya_indra("UI", ["S"])
        assert result == [("గల", "UI")]

    def test_surya_na_pattern(self):
        # Single Surya gana న (III)
        result = segment_surya_indra("III", ["S"])
        assert result == [("న", "III")]

    def test_empty_structure_empty_string(self):
        result = segment_surya_indra("", [])
        assert result == []

    def test_empty_structure_nonempty_string(self):
        # Non-empty string with no structure slots → leftover → None
        assert segment_surya_indra("UI", []) is None


# ---------------------------------------------------------------------------
# segment_kandam
# ---------------------------------------------------------------------------

class TestSegmentKandam:

    def test_gagana_bha_nal(self):
        # గగన(UU=4m) + భ(UII=4m) + నల(IIII=4m)
        result = segment_kandam("UUUIIIIII")
        assert result == [("గగన", "UU"), ("భ", "UII"), ("నల", "IIII")]

    def test_ja_gana(self):
        # జ(IUI) = I(1)+U(2)+I(1) = 4 matras
        result = segment_kandam("IUI")
        assert result == [("జ", "IUI")]

    def test_sa_gana(self):
        # స(IIU) = I(1)+I(1)+U(2) = 4 matras
        result = segment_kandam("IIU")
        assert result == [("స", "IIU")]

    def test_nal_gana(self):
        result = segment_kandam("IIII")
        assert result == [("నల", "IIII")]

    def test_multiple_ganas(self):
        # జ(IUI) + స(IIU) + గగన(UU) = "IUI"+"IIU"+"UU"
        result = segment_kandam("IUIIIUUU")
        assert result == [("జ", "IUI"), ("స", "IIU"), ("గగన", "UU")]

    def test_overshoot_returns_none(self):
        # UUU: after "UU" chunk, remaining U(2) forms incomplete chunk
        assert segment_kandam("UUU") is None

    def test_leftover_returns_none(self):
        # Single I can never reach 4 matras
        assert segment_kandam("I") is None

    def test_iiui_leftover_returns_none(self):
        # "IIU"(స) valid, then "I" leftover → None
        assert segment_kandam("IIUI") is None

    def test_empty_string(self):
        assert segment_kandam("") == []


# ---------------------------------------------------------------------------
# gana_start_indices
# ---------------------------------------------------------------------------

class TestGanaStartIndices:

    def test_three_ganas(self):
        ganas = [("భ", "UII"), ("నల", "IIII"), ("గగన", "UU")]
        assert gana_start_indices(ganas) == [0, 3, 7]

    def test_single_gana(self):
        assert gana_start_indices([("గల", "UI")]) == [0]

    def test_empty(self):
        assert gana_start_indices([]) == []

    def test_uniform_ganas(self):
        ganas = [("భ", "UII")] * 4
        assert gana_start_indices(ganas) == [0, 3, 6, 9]


# ---------------------------------------------------------------------------
# JatiRegistry
# ---------------------------------------------------------------------------

class TestJatiRegistry:

    def test_all_six_meters_registered(self):
        names = {m.name for m in JatiRegistry.all()}
        for expected in ("Dwipada", "Taruvoja", "Kandam", "Ataveladi", "Tetagiti", "Sisam"):
            assert expected in names

    def test_dwipada_properties(self):
        m = JatiRegistry.get("Dwipada")
        assert m is not None
        assert m.pada_count == 2
        assert m.segmentation_type == "surya_indra"
        assert m.has_prasa is True
        assert m.has_prasa_yati is False
        assert len(m.pada_structures) == 2

    def test_taruvoja_properties(self):
        m = JatiRegistry.get("Taruvoja")
        assert m is not None
        assert m.pada_count == 4
        assert m.yati_gana_positions == [3, 5, 7]

    def test_kandam_properties(self):
        m = JatiRegistry.get("Kandam")
        assert m is not None
        assert m.pada_count == 4
        assert m.segmentation_type == "kandam"
        assert m.yati_type == "cross_pada"
        assert m.yati_cross_pada_pairs == [(0, 1), (2, 3)]
        assert m.has_prasa is True

    def test_upajati_meters_no_prasa(self):
        for name in ("Ataveladi", "Tetagiti", "Sisam"):
            m = JatiRegistry.get(name)
            assert m is not None
            assert m.has_prasa is False, f"{name} should have no prasa"
            assert m.has_prasa_yati is True, f"{name} should allow prasa-yati"

    def test_ataveladi_alternating_structure(self):
        m = JatiRegistry.get("Ataveladi")
        # Odd padas: 3I+2S, Even padas: 5S
        assert m.pada_structures[0] == ["I", "I", "I", "S", "S"]
        assert m.pada_structures[1] == ["S", "S", "S", "S", "S"]
        assert m.pada_structures[2] == ["I", "I", "I", "S", "S"]
        assert m.pada_structures[3] == ["S", "S", "S", "S", "S"]

    def test_case_insensitive_lookup(self):
        assert JatiRegistry.get("dwipada") is not None
        assert JatiRegistry.get("KANDAM") is not None

    def test_unknown_meter_returns_none(self):
        assert JatiRegistry.get("NonExistent") is None

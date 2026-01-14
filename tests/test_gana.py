from telugu_chandas.gana import get_ganas_for_vritta

def test_vritta_gana_mapping():
    # Test all 8 basic ganas
    assert get_ganas_for_vritta("UUU") == ["Ma"]
    assert get_ganas_for_vritta("IUU") == ["Ya"]
    assert get_ganas_for_vritta("UIU") == ["Ra"]
    assert get_ganas_for_vritta("IIU") == ["Sa"]
    assert get_ganas_for_vritta("UUI") == ["Ta"]
    assert get_ganas_for_vritta("IUI") == ["Ja"]
    assert get_ganas_for_vritta("UII") == ["Bha"]
    assert get_ganas_for_vritta("III") == ["Na"]
    
    # Test Sequence (Utpalamala start: Bha Ra Na Bha...)
    # Bha=UII, Ra=UIU, Na=III
    # "UIIUIUIII"
    seq = "UIIUIUIII"
    assert get_ganas_for_vritta(seq) == ["Bha", "Ra", "Na"]
    
    # Test Leftovers
    # "UII U" -> ["Bha", "Ga"]
    assert get_ganas_for_vritta("UIIU") == ["Bha", "Ga"]
    
    print("All Vritta Gana tests passed!")

if __name__ == "__main__":
    test_vritta_gana_mapping()

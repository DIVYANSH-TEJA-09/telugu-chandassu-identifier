from dataclasses import dataclass
from typing import List

@dataclass
class MeterDefinition:
    name: str
    gana_sequence: List[str]
    yati_position: int  # 1-based index
    has_prasa: bool = True

# Common Vritta Meters
VRITTA_METERS = [
    MeterDefinition(
        name="Utpalamala",
        # Bha, Ra, Na, Bha, Bha, Ra, Va
        gana_sequence=["Bha", "Ra", "Na", "Bha", "Bha", "Ra", "Va"],
        yati_position=10
    ),
    MeterDefinition(
        name="Champakamala",
        # Na, Ja, Bha, Ja, Ja, Ja, Ra
        gana_sequence=["Na", "Ja", "Bha", "Ja", "Ja", "Ja", "Ra"],
        yati_position=11
    ),
    MeterDefinition(
        name="Shardulam",
        # Ma, Sa, Ja, Sa, Ta, Ta, Ga
        gana_sequence=["Ma", "Sa", "Ja", "Sa", "Ta", "Ta", "Ga"],
        yati_position=13
    ),
    MeterDefinition(
        name="Mattebham",
        # Sa, Bha, Ra, Na, Ma, Ya, Va
        gana_sequence=["Sa", "Bha", "Ra", "Na", "Ma", "Ya", "Va"],
        yati_position=14
    )
]

def find_meter_by_ganas(ganas: List[str]) -> List[MeterDefinition]:
    """
    Finds meters that match the given gana sequence.
    """
    matches = []
    for meter in VRITTA_METERS:
        # Comparison logic: Exact match of list
        # Note: Input ganas might have extra '?' or be incomplete?
        # Assuming we pass full line analysis.
        
        if len(ganas) != len(meter.gana_sequence):
            continue
            
        if ganas == meter.gana_sequence:
            matches.append(meter)
            
    return matches

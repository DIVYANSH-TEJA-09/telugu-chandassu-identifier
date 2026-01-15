# telugu_chandas/registry.py

from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class MeterDefinition:
    name: str
    gana_sequence: List[str] # Standard Vritta sequence (e.g. ["Bha", "Ra"...])
    yati_position: int  # 1-based index
    has_prasa: bool = True
    # Future: type (Vritta, Jati, Upajati), total_aksharas etc.

class MeterRegistry:
    """
    Registry of known Telugu Meters.
    """
    _meters: Dict[str, MeterDefinition] = {}

    @classmethod
    def register(cls, meter: MeterDefinition):
        cls._meters[meter.name.lower()] = meter

    @classmethod
    def get(cls, name: str) -> Optional[MeterDefinition]:
        return cls._meters.get(name.lower())

    @classmethod
    def find_by_ganas(cls, ganas: List[str]) -> List[MeterDefinition]:
        """
        Finds meters that match the given gana sequence.
        """
        matches = []
        for meter in cls._meters.values():
            if len(ganas) != len(meter.gana_sequence):
                continue
            if ganas == meter.gana_sequence:
                matches.append(meter)
        return matches
    
    @classmethod
    def all(cls) -> List[MeterDefinition]:
        return list(cls._meters.values())

# --- Initialize Standard Meters ---
# Utpalamala: Bha-Ra-Na-Bha-Bha-Ra-Va (20 chars, Yati 10)
MeterRegistry.register(MeterDefinition("Utpalamala", ["Bha", "Ra", "Na", "Bha", "Bha", "Ra", "Va"], 10))

# Champakamala: Na-Ja-Bha-Ja-Ja-Ja-Ra (21 chars, Yati 11)
MeterRegistry.register(MeterDefinition("Champakamala", ["Na", "Ja", "Bha", "Ja", "Ja", "Ja", "Ra"], 11))

# Shardulam: Ma-Sa-Ja-Sa-Ta-Ta-Ga (19 chars, Yati 13)
MeterRegistry.register(MeterDefinition("Shardulam", ["Ma", "Sa", "Ja", "Sa", "Ta", "Ta", "Ga"], 13))

# Mattebham: Sa-Bha-Ra-Na-Ma-Ya-Va (20 chars, Yati 14)
MeterRegistry.register(MeterDefinition("Mattebham", ["Sa", "Bha", "Ra", "Na", "Ma", "Ya", "Va"], 14))

# Backwards Compatibility
VRITTA_METERS = MeterRegistry.all()
find_meter_by_ganas = MeterRegistry.find_by_ganas


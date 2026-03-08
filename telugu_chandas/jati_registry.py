# telugu_chandas/jati_registry.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


@dataclass
class JatiMeterDefinition:
    """
    Describes a Jati (matra-based) or Upajati padyam.

    pada_structures:       One list per pada.  "S" = Surya, "I" = Indra,
                           "K" = Kandam (4-matra chunk).
    yati_gana_positions:   1-based gana indices *within* each pada whose first
                           akshara is compared against the pada's first akshara.
                           Used when yati_type == "standard".
    yati_type:             "standard"   — within-pada gana comparison (default)
                           "cross_pada" — first akshara of even pada vs. first
                                          akshara of paired odd pada.
    yati_cross_pada_pairs: List of (odd_pada_index, even_pada_index) pairs used
                           when yati_type == "cross_pada".
    has_prasa:             2nd-akshara consonant must match across all padas.
    has_prasa_yati:        Upajati option: yati position uses prasa letter
                           instead of the line-start letter.
    """
    name: str
    segmentation_type: str              # "surya_indra" | "kandam"
    pada_count: int
    pada_structures: List[List[str]]    # length == pada_count
    yati_gana_positions: List[int]
    has_prasa: bool
    has_prasa_yati: bool
    yati_type: str = "standard"                                  # new
    yati_cross_pada_pairs: Optional[List[Tuple[int,int]]] = None # new
    notes: str = ""


class JatiRegistry:
    _meters: Dict[str, JatiMeterDefinition] = {}

    @classmethod
    def register(cls, meter: JatiMeterDefinition):
        cls._meters[meter.name.lower()] = meter

    @classmethod
    def get(cls, name: str) -> Optional[JatiMeterDefinition]:
        return cls._meters.get(name.lower())

    @classmethod
    def all(cls) -> List[JatiMeterDefinition]:
        return list(cls._meters.values())


# ---------------------------------------------------------------------------
# Dwipada — the first Jati meter
# 2 padas, each: 3 Indra + 1 Surya gana
# Yati: 3rd gana's first akshara vs. pada's 1st akshara
# Prasa: yes
# ---------------------------------------------------------------------------
JatiRegistry.register(JatiMeterDefinition(
    name="Dwipada",
    segmentation_type="surya_indra",
    pada_count=2,
    pada_structures=[
        ["I", "I", "I", "S"],   # pada 1
        ["I", "I", "I", "S"],   # pada 2
    ],
    yati_gana_positions=[3],    # 3rd gana's 1st akshara vs. pada start
    has_prasa=True,
    has_prasa_yati=False,
    notes="3 ఇంద్ర గణాలు + 1 సూర్య గణం, 2 పాదాలు"
))

# ---------------------------------------------------------------------------
# Taruvoja — 4 padas, each: 3 Indra + 1 Surya + 3 Indra + 1 Surya (8 ganas)
# Yati: ganas 3, 5, 7 each check their 1st akshara against the pada's 1st akshara
# Prasa: yes
# ---------------------------------------------------------------------------
_TARUVOJA_PADA = ["I", "I", "I", "S", "I", "I", "I", "S"]

JatiRegistry.register(JatiMeterDefinition(
    name="Taruvoja",
    segmentation_type="surya_indra",
    pada_count=4,
    pada_structures=[_TARUVOJA_PADA] * 4,
    yati_gana_positions=[3, 5, 7],  # ganas 3, 5, 7 vs. pada start
    has_prasa=True,
    has_prasa_yati=False,
    notes="(3 ఇంద్ర + 1 సూర్య) × 2, 4 పాదాలు, యతి గణాలు 3-5-7"
))

# ---------------------------------------------------------------------------
# Tetagiti — 4 padas, each: 1 Surya + 2 Indra + 2 Surya (5 ganas)
# Yati: 4th gana's first akshara vs. pada's first akshara
# No prasa; prasa-yati allowed as alternative to regular yati
# ---------------------------------------------------------------------------
JatiRegistry.register(JatiMeterDefinition(
    name="Tetagiti",
    segmentation_type="surya_indra",
    pada_count=4,
    pada_structures=[["S", "I", "I", "S", "S"]] * 4,
    yati_gana_positions=[4],     # gana 4's first akshara vs. pada start
    has_prasa=False,
    has_prasa_yati=True,
    notes="1 సూర్య + 2 ఇంద్ర + 2 సూర్య, 4 పాదాలు, ప్రాసయతి అనుమతి"
))

# ---------------------------------------------------------------------------
# Ataveladi — 4 padas
#   Odd padas  (1, 3): 3 Indra + 2 Surya  →  [I, I, I, S, S]
#   Even padas (2, 4): 5 Surya             →  [S, S, S, S, S]
# Yati: gana 4's first akshara vs. pada's first akshara
# No prasa; prasa-yati allowed
# ---------------------------------------------------------------------------
JatiRegistry.register(JatiMeterDefinition(
    name="Ataveladi",
    segmentation_type="surya_indra",
    pada_count=4,
    pada_structures=[
        ["I", "I", "I", "S", "S"],  # pada 1 (odd)
        ["S", "S", "S", "S", "S"],  # pada 2 (even)
        ["I", "I", "I", "S", "S"],  # pada 3 (odd)
        ["S", "S", "S", "S", "S"],  # pada 4 (even)
    ],
    yati_gana_positions=[4],
    has_prasa=False,
    has_prasa_yati=True,
    notes="ఆటవెలది: బేసి పాదాలు 3I+2S, సరి పాదాలు 5S, ప్రాసయతి అనుమతి"
))

# ---------------------------------------------------------------------------
# Sisam — 4 padas, each: 6 Indra + 2 Surya  →  [I,I,I,I,I,I,S,S]
# Yati: ganas 3, 5, 7 vs. pada's first akshara
# No prasa; prasa-yati allowed
# ---------------------------------------------------------------------------
JatiRegistry.register(JatiMeterDefinition(
    name="Sisam",
    segmentation_type="surya_indra",
    pada_count=4,
    pada_structures=[["I", "I", "I", "I", "I", "I", "S", "S"]] * 4,
    yati_gana_positions=[3, 5, 7],
    has_prasa=False,
    has_prasa_yati=True,
    notes="సీసం: 6 ఇంద్ర + 2 సూర్య, యతి గణాలు 3-5-7, ప్రాసయతి అనుమతి"
))

# ---------------------------------------------------------------------------
# Kandam — 4 padas, odd padas 3 ganas, even padas 5 ganas
# All ganas are 4-matra chunks: గగన(UU) భ(UII) జ(IUI) స(IIU) నల(IIII)
#
# Extra structural rules (checked per half-verse: padas 1+2 and padas 3+4):
#   1. Jagana (IUI) must NOT appear at global odd positions 1,3,5,7
#   2. 3rd gana of each even pada (global position 6) must be నల or జ
#   3. Last akshara of each even pada must be Guru
#
# Yati: cross-pada — 1st akshara of each even pada vs. 1st akshara of
#        the paired odd pada  (pada1↔pada2, pada3↔pada4)
# Prasa: yes
# ---------------------------------------------------------------------------
JatiRegistry.register(JatiMeterDefinition(
    name="Kandam",
    segmentation_type="kandam",
    pada_count=4,
    pada_structures=[
        ["K", "K", "K"],           # pada 1 (odd):  3 kandam ganas
        ["K", "K", "K", "K", "K"], # pada 2 (even): 5 kandam ganas
        ["K", "K", "K"],           # pada 3 (odd):  3 kandam ganas
        ["K", "K", "K", "K", "K"], # pada 4 (even): 5 kandam ganas
    ],
    yati_gana_positions=[],          # unused — handled by cross_pada logic
    yati_type="cross_pada",
    yati_cross_pada_pairs=[(0, 1), (2, 3)],
    has_prasa=True,
    has_prasa_yati=False,
    notes="కందం: బేసి పాదాలు 3 గణాలు, సరి పాదాలు 5 గణాలు"
))

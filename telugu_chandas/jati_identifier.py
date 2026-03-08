# telugu_chandas/jati_identifier.py

from collections import Counter
from typing import List, Optional, Tuple

from .models import Akshara, IdentificationResult, Weight
from .analyzer import ProsodyAnalyzer
from .validator import RuleValidator
from .jati_registry import JatiRegistry, JatiMeterDefinition
from .jati_segmenter import segment_surya_indra, segment_kandam, gana_start_indices


class JatiIdentifier:
    """
    Identifies Jati (matra-based) meters — Dwipada, Taruvoja, Kandam,
    Ataveladi, Tetagiti, Sisam.
    """

    def identify(self, lines_of_aksharas: List[List[Akshara]]) -> IdentificationResult:
        """
        Tries every registered Jati meter and returns the best match.
        """
        best_result: Optional[IdentificationResult] = None
        best_score = -1.0

        for meter in JatiRegistry.all():
            result = self._try_meter(lines_of_aksharas, meter)
            if result is not None and result.confidence_score > best_score:
                best_score = result.confidence_score
                best_result = result

        if best_result is None:
            return IdentificationResult(
                "Unknown", "0.0%", 0.0, [], False, False,
                ["No matching Jati pattern found"],
                yati_notes=[],
            )
        return best_result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _try_meter(
        self,
        lines: List[List[Akshara]],
        meter: JatiMeterDefinition,
    ) -> Optional[IdentificationResult]:
        """Attempt to match *lines* against *meter*. Returns None if completely
        incompatible (e.g., wrong pada count)."""

        if len(lines) != meter.pada_count:
            return None

        # 1. Segment each pada ------------------------------------------------
        pada_ganas: List[Optional[List[Tuple[str, str]]]] = []

        for pada_idx, line in enumerate(lines):
            w_str = "".join(
                ak.weight.value for ak in line if ak.weight is not None
            )
            structure = meter.pada_structures[pada_idx]

            if meter.segmentation_type == "surya_indra":
                ganas = segment_surya_indra(w_str, structure)
            else:  # kandam
                ganas = segment_kandam(w_str)
                # Validate expected gana count for this pada
                if ganas is not None and len(ganas) != len(structure):
                    ganas = None

            pada_ganas.append(ganas)

        # 2. Gana score (60%) ------------------------------------------------
        valid_count = sum(1 for g in pada_ganas if g is not None)
        if valid_count == 0:
            return None  # Not this meter at all

        gana_score = (valid_count / meter.pada_count) * 60.0

        # 3. Kandam extra structural rules (penalty deducted from gana_score) --
        rule_penalty = 0.0
        rule_notes: List[str] = []
        if meter.name.lower() == "kandam" and valid_count > 0:
            rule_penalty, rule_notes = self._validate_kandam_rules(
                lines, pada_ganas
            )

        # 4. Yati score (20%) ------------------------------------------------
        yati_score, yati_notes = self._score_yati(lines, pada_ganas, meter)

        # 5. Prasa score (20%) -----------------------------------------------
        prasa_score, prasa_note = self._score_prasa(lines, meter)

        total_score = max(0.0, gana_score - rule_penalty) + yati_score + prasa_score

        # Build ganas_found from first successfully segmented pada
        first_valid = next((g for g in pada_ganas if g is not None), [])
        ganas_found = [name for name, _pat in first_valid]

        breakdown = (
            f"Score: {total_score:.1f}% "
            f"(Gణ: {gana_score:.1f} + యతి: {yati_score:.1f} + ప్రాస: {prasa_score:.1f})"
        )

        return IdentificationResult(
            meter_name=meter.name,
            confidence=f"{total_score:.1f}%",
            confidence_score=total_score,
            ganas_found=ganas_found,
            yati_valid=(yati_score >= 10.0),
            prasa_valid=(prasa_score >= 10.0),
            notes=[breakdown] + rule_notes,
            yati_notes=yati_notes,
            prasa_note=prasa_note,
        )

    def _score_yati(
        self,
        lines: List[List[Akshara]],
        pada_ganas: List[Optional[List[Tuple[str, str]]]],
        meter: JatiMeterDefinition,
    ) -> Tuple[float, List[str]]:
        """Dispatch to the correct yati-scoring strategy."""
        if meter.yati_type == "cross_pada":
            return self._score_yati_cross_pada(lines, meter)
        return self._score_yati_standard(lines, pada_ganas, meter)

    def _score_yati_standard(
        self,
        lines: List[List[Akshara]],
        pada_ganas: List[Optional[List[Tuple[str, str]]]],
        meter: JatiMeterDefinition,
    ) -> Tuple[float, List[str]]:
        """
        Standard within-pada yati: each listed gana position's first akshara
        is compared against the pada's first akshara.

        When meter.has_prasa_yati is True and regular yati fails, prasa-yati
        is attempted: pada's 2nd akshara is compared with the 2nd akshara of
        the yati gana (and pada's 1st must NOT match yati gana's 1st to avoid
        Yati-Prasa-Sankara).

        Score = (passing padas / total padas) × 20.
        """
        notes: List[str] = []
        passing = 0

        for pada_idx, (line, ganas) in enumerate(zip(lines, pada_ganas)):
            if ganas is None:
                notes.append(f"P{pada_idx+1}: గణ విభజన లేదు ❌")
                continue

            starts = gana_start_indices(ganas)
            pada_ok = True
            pada_reasons: List[str] = []

            for yati_pos in meter.yati_gana_positions:  # 1-based
                gana_idx = yati_pos - 1
                if gana_idx >= len(starts):
                    pada_ok = False
                    pada_reasons.append(f"G{yati_pos}: లేదు ❌")
                    continue

                ak_start = line[0]
                ak_yati  = line[starts[gana_idx]]

                matched, reason = RuleValidator.check_yati_match(ak_start, ak_yati)

                if matched:
                    pada_reasons.append(f"G{yati_pos}: {reason}✅")
                elif meter.has_prasa_yati:
                    # Try prasa-yati: pada[1] ↔ gana[1]
                    py_ok, py_reason = self._check_prasa_yati(
                        line, starts[gana_idx]
                    )
                    if py_ok:
                        pada_reasons.append(
                            f"G{yati_pos}: ప్రాసయతి — {py_reason}✅"
                        )
                    else:
                        pada_ok = False
                        pada_reasons.append(
                            f"G{yati_pos}: యతి({reason})❌ ప్రాసయతి({py_reason})❌"
                        )
                else:
                    pada_ok = False
                    pada_reasons.append(f"G{yati_pos}: {reason}❌")

            if pada_ok:
                passing += 1
            notes.append(f"P{pada_idx+1}: {' | '.join(pada_reasons)}")

        score = (passing / meter.pada_count) * 20.0
        return score, notes

    @staticmethod
    def _check_prasa_yati(
        line: List[Akshara],
        yati_gana_start: int,
    ) -> Tuple[bool, str]:
        """
        Prasa-Yati check:
          • pada[1]  ↔  line[yati_gana_start + 1]  must have Maitri.
          • pada[0]  ↔  line[yati_gana_start]       must NOT match
            (avoid Yati-Prasa-Sankara — mixing of yati and prasa).

        Returns (valid, reason_string).
        """
        # Need at least 2 aksharas in pada and 2 in yati gana
        if len(line) < 2 or yati_gana_start + 1 >= len(line):
            return False, "అక్షరాలు చాలవు"

        ak_prasa      = line[1]
        ak_yati_prasa = line[yati_gana_start + 1]

        prasa_match, prasa_reason = RuleValidator.check_yati_match(
            ak_prasa, ak_yati_prasa
        )
        if not prasa_match:
            return False, f"ప్రాస అక్షర అసంగతం ({prasa_reason})"

        # Sankara check: line[0] must NOT match line[yati_gana_start]
        ak_start     = line[0]
        ak_yati_start = line[yati_gana_start]
        sankara, _ = RuleValidator.check_yati_match(ak_start, ak_yati_start)
        if sankara:
            return False, "యతి-ప్రాస-సంకరం (1వ అక్షరాలు కూడా సరిపోతున్నాయి)"

        return True, prasa_reason

    def _score_yati_cross_pada(
        self,
        lines: List[List[Akshara]],
        meter: JatiMeterDefinition,
    ) -> Tuple[float, List[str]]:
        """
        Cross-pada yati (Kandam): the first akshara of each even pada is
        compared against the first akshara of its paired odd pada.

        E.g. pairs = [(0,1),(2,3)] means:
            pada1[0] ↔ pada2[0]   and   pada3[0] ↔ pada4[0]
        Score = (matching pairs / total pairs) × 20.
        """
        notes: List[str] = []
        passing = 0
        pairs = meter.yati_cross_pada_pairs or []

        for odd_idx, even_idx in pairs:
            if odd_idx >= len(lines) or even_idx >= len(lines):
                notes.append(f"P{odd_idx+1}↔P{even_idx+1}: పాదం లేదు ❌")
                continue
            if not lines[odd_idx] or not lines[even_idx]:
                notes.append(f"P{odd_idx+1}↔P{even_idx+1}: ఖాళీ పాదం ❌")
                continue

            ak_ref  = lines[odd_idx][0]
            ak_yati = lines[even_idx][0]

            matched, reason = RuleValidator.check_yati_match(ak_ref, ak_yati)
            symbol = "✅" if matched else "❌"
            notes.append(f"P{odd_idx+1}↔P{even_idx+1}: {reason}{symbol}")
            if matched:
                passing += 1

        total = len(pairs) if pairs else 1
        score = (passing / total) * 20.0
        return score, notes

    # ------------------------------------------------------------------
    # Kandam extra structural rules
    # ------------------------------------------------------------------

    def _validate_kandam_rules(
        self,
        lines: List[List[Akshara]],
        pada_ganas: List[Optional[List[Tuple[str, str]]]],
    ) -> Tuple[float, List[str]]:
        """
        Checks the three Kandam-specific structural rules per half-verse
        (padas 1+2  and  padas 3+4):

          Rule 1 — Jagana (IUI) must NOT appear at global odd positions
                   1, 3 (odd pada's gana slots 0,2)
                   5, 7 (even pada's gana slots 1,3)

          Rule 2 — 3rd gana of the even pada (global position 6, even-pada
                   slot index 2) must be నల (IIII) or జ (IUI).

          Rule 3 — Last akshara of each even pada must be Guru (U).

        Returns (score_penalty, notes).
        The penalty is subtracted from gana_score (max 20 points total).
        """
        notes: List[str] = []
        violations = 0
        total_checks = 0

        for half_idx, (odd_idx, even_idx) in enumerate([(0, 1), (2, 3)]):
            label = f"H{half_idx + 1}"
            odd_g  = pada_ganas[odd_idx]
            even_g = pada_ganas[even_idx]

            if odd_g is None or even_g is None:
                continue

            # Rule 1a: odd-pada gana slots 0,2 (global 1,3) → no Jagana
            for slot, gpos in [(0, 1), (2, 3)]:
                total_checks += 1
                if slot < len(odd_g):
                    name, pat = odd_g[slot]
                    if pat == "IUI":
                        violations += 1
                        notes.append(
                            f"{label}: G{gpos}(బేసి)లో జగణం నిషేధం ❌"
                        )

            # Rule 1b: even-pada gana slots 1,3 (global 5,7) → no Jagana
            for slot, gpos in [(1, 5), (3, 7)]:
                total_checks += 1
                if slot < len(even_g):
                    name, pat = even_g[slot]
                    if pat == "IUI":
                        violations += 1
                        notes.append(
                            f"{label}: G{gpos}(బేసి)లో జగణం నిషేధం ❌"
                        )

            # Rule 2: even-pada slot 2 (global 6) must be నల or జ
            total_checks += 1
            if len(even_g) > 2:
                name, pat = even_g[2]
                if pat in ("IIII", "IUI"):
                    notes.append(f"{label}: G6 {name}({pat}) ✅")
                else:
                    violations += 1
                    notes.append(
                        f"{label}: G6 నల/జగణం కావాలి, {name}({pat}) వచ్చింది ❌"
                    )

            # Rule 3: last akshara of even pada must be Guru
            total_checks += 1
            even_line = lines[even_idx]
            if even_line and even_line[-1].weight:
                if even_line[-1].weight.value == "U":
                    notes.append(f"{label}: సరి పాద చివరి అక్షరం గురువు ✅")
                else:
                    violations += 1
                    notes.append(
                        f"{label}: సరి పాద చివరి అక్షరం లఘువు ❌"
                    )

        # Max penalty = 20 points; scale by violation ratio
        ratio   = violations / total_checks if total_checks else 0
        penalty = ratio * 20.0
        return penalty, notes

    def _score_prasa(
        self,
        lines: List[List[Akshara]],
        meter: JatiMeterDefinition,
    ) -> Tuple[float, str]:
        """
        Checks the Prasa rule: the onset consonant(s) of the 2nd akshara
        must be the same across all padas.

        For upajati meters (has_prasa=False) full marks are awarded
        automatically since prasa is not required.
        """
        if not meter.has_prasa:
            return 20.0, "వర్తించదు (ఉపజాతి)"

        prasa_cons: List[Optional[tuple]] = []
        for line in lines:
            if len(line) >= 2:
                cons = RuleValidator.get_akshara_consonants(line[1])
                prasa_cons.append(tuple(cons))
            else:
                prasa_cons.append(None)

        valid = [p for p in prasa_cons if p is not None]
        if not valid:
            return 0.0, "లేదు"

        most_common = Counter(valid).most_common(1)[0][0]
        matches = sum(1 for p in prasa_cons if p == most_common)
        score = (matches / meter.pada_count) * 20.0
        prasa_str = "+".join(most_common) if most_common else "అచ్చు"
        return score, prasa_str

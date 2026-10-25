import re
from typing import Any, Dict, List, Optional
from app.core.logging import get_logger

logger = get_logger("prescription_parser")

# Standard dosage forms
DOSAGE_FORMS = [
    "tablet", "tab", "capsule", "cap", "syrup", "syr", "injection", "inj",
    "ointment", "cream", "suspension", "drops", "inhaler", "solution"
]

# Standard frequency abbreviations
FREQUENCY_PATTERNS = {
    r"\b(once\s+daily|qd|od|q\.d\.)\b": "Once daily (OD)",
    r"\b(twice\s+daily|bid|b\.i\.d\.)\b": "Twice daily (BID)",
    r"\b(three\s+times\s+daily|thrice\s+daily|tid|t\.i\.d\.)\b": "Three times daily (TID)",
    r"\b(four\s+times\s+daily|qid|q\.i\.d\.)\b": "Four times daily (QID)",
    r"\b(at\s+bedtime|hs|h\.s\.)\b": "At bedtime (HS)",
    r"\b(as\s+needed|prn|p\.r\.n\.|sos)\b": "As needed (PRN / SOS)",
    r"\b(every\s+(\d+)\s+hours|q(\d+)h)\b": "Every specified interval",
}

# Standard routes
ROUTES = {
    r"\b(po|oral|by\s+mouth)\b": "Oral (PO)",
    r"\b(iv|intravenous)\b": "Intravenous (IV)",
    r"\b(im|intramuscular)\b": "Intramuscular (IM)",
    r"\b(topical|apply\s+externally)\b": "Topical",
    r"\b(sublingual|sl)\b": "Sublingual",
    r"\b(inhalation|inh)\b": "Inhalation",
}


class PrescriptionParserService:
    def parse_prescription_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse prescription text into structured candidate records.
        FLAGS any uncertain medicine names or dosages for mandatory human confirmation.
        Preserves original raw lines.
        """
        lines = text.splitlines()
        extracted_items: List[Dict[str, Any]] = []

        prescriber = self._extract_prescriber(text)
        presc_date = self._extract_date(text)

        for line_idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue

            # Skip header, separator, or disclaimer lines
            if line.startswith(("-", "=", "*", "_", "~")) or len(line) < 3:
                continue
            if any(h in line.lower() for h in ["prescription", "doctor", "clinic", "hospital", "patient", "rx #", "date:", "dr.", "signature"]):
                continue
            if line.strip().lower() in ("rx:", "rx", "medicines:", "medication:", "medicines"):
                continue

            parsed_item = self._parse_prescription_line(line, prescriber, presc_date, line_idx + 1)
            if parsed_item:
                extracted_items.append(parsed_item)

        return extracted_items

    def _extract_prescriber(self, text: str) -> Optional[str]:
        doc_match = re.search(r"\b(Dr\.?\s+[A-Za-z\.\s]{2,40}|Doctor\s+[A-Za-z\.\s]{2,40})\b", text)
        if doc_match:
            return doc_match.group(1).strip()
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b", text)
        if date_match:
            return date_match.group(1).strip()
        return None

    def _parse_prescription_line(
        self,
        line: str,
        prescriber: Optional[str],
        presc_date: Optional[str],
        line_num: int,
    ) -> Optional[Dict[str, Any]]:
        # Remove list numbers like "1.", "2)", etc.
        clean_line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()

        # Check for strength pattern
        strength_match = re.search(r"(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu|units|%|meq))\b", clean_line, re.IGNORECASE)

        # Check for dosage form
        form_match = None
        for form in DOSAGE_FORMS:
            f_pat = rf"\b{form}\b"
            if re.search(f_pat, clean_line, re.IGNORECASE):
                form_match = form
                break

        # A prescription item typically has at least a drug candidate name or strength or dosage form
        if not strength_match and not form_match and not clean_line.lower().startswith("rx"):
            # Check if line looks like a medicine name (single or two words followed by instructions)
            words = clean_line.split()
            if len(words) < 2 or len(words) > 15:
                return None

        # Extract medicine name candidate
        # Typically the text before the strength or first form keyword
        medicine_name = ""
        if strength_match:
            medicine_name = clean_line[:strength_match.start()].strip()
        elif form_match:
            f_idx = clean_line.lower().find(form_match)
            # could be "Tab Amoxicillin" or "Amoxicillin Tab"
            parts = clean_line.split(maxsplit=2)
            medicine_name = " ".join(parts[:2])
        else:
            words = clean_line.split()
            medicine_name = words[0] if words else "Unknown"

        # Clean medicine name
        medicine_name = re.sub(r"^(tab|cap|syr|inj|rx)\s+", "", medicine_name, flags=re.IGNORECASE).strip()
        if not medicine_name or len(medicine_name) < 2:
            return None

        extracted_strength = strength_match.group(1) if strength_match else None

        # Extract frequency
        extracted_frequency = None
        for pat, standard_freq in FREQUENCY_PATTERNS.items():
            if re.search(pat, clean_line, re.IGNORECASE):
                extracted_frequency = standard_freq
                break

        # Extract route
        extracted_route = None
        for pat, standard_route in ROUTES.items():
            if re.search(pat, clean_line, re.IGNORECASE):
                extracted_route = standard_route
                break

        # Extract duration
        duration_match = re.search(r"\b(?:for|x)\s*(\d+\s*(?:days|weeks|months|d|w))\b", clean_line, re.IGNORECASE)
        extracted_duration = duration_match.group(1) if duration_match else None

        # Build extracted instructions
        instructions_parts = []
        if extracted_frequency:
            instructions_parts.append(extracted_frequency)
        if extracted_duration:
            instructions_parts.append(f"for {extracted_duration}")
        if extracted_route:
            instructions_parts.append(extracted_route)

        extracted_instructions = ", ".join(instructions_parts) if instructions_parts else clean_line

        # Confidence calculation & safety flagging
        confidence = 0.95
        confidence_flags: List[str] = []

        # If no strength found: uncertainty flag
        if not extracted_strength:
            confidence -= 0.25
            confidence_flags.append("Missing explicit strength or concentration.")

        # If medicine name contains special symbols or numbers in name
        if re.search(r"[0-9\?\!\@\#\$\%\^\&\*]", medicine_name):
            confidence -= 0.3
            confidence_flags.append("Medicine name contains ambiguous characters or numbers.")

        # If line was very short or missing frequency
        if not extracted_frequency:
            confidence -= 0.15
            confidence_flags.append("No explicit administration frequency detected.")

        confidence = max(round(confidence, 2), 0.2)
        needs_human_confirmation = confidence < 0.85 or bool(confidence_flags)

        return {
            "extracted_medicine_name": medicine_name,
            "extracted_strength": extracted_strength,
            "extracted_instructions": extracted_instructions,
            "frequency": extracted_frequency,
            "duration": extracted_duration,
            "route": extracted_route,
            "prescriber": prescriber,
            "prescription_date": presc_date,
            "confidence_metadata": {
                "confidence_score": confidence,
                "needs_human_confirmation": needs_human_confirmation,
                "uncertainty_reasons": confidence_flags,
                "raw_line": line,
                "line_number": line_num,
            },
            "verification_status": "pending_confirmation",
        }


prescription_parser = PrescriptionParserService()

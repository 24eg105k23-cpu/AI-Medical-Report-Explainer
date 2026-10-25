import re
from typing import Any, Dict, List, Optional, Tuple
from app.core.logging import get_logger
from app.schemas.analysis import LaboratoryValueSchema, ReferenceRangeSchema, SourceLocationSchema

logger = get_logger("parser")

# Standard known units in laboratory reports
COMMON_UNITS = [
    "g/dL", "mg/dL", "ug/dL", "mcg/dL", "10^3/uL", "10^6/uL", "x10^3/uL",
    "x10^6/uL", "/uL", "K/uL", "M/uL", "fl", "fL", "pg", "%", "mmol/L",
    "umol/L", "mEq/L", "IU/L", "U/L", "uIU/mL", "ng/mL", "ng/dL", "pg/mL",
    "cells/mcL", "sec", "seconds", "ratio", "Index", "mg/L", "g/L"
]

# Common test aliases / patterns
KNOWN_TEST_NAMES = [
    "Hemoglobin", "Hb", "Hematocrit", "HCT", "RBC Count", "Red Blood Cell Count",
    "WBC Count", "White Blood Cell Count", "WBC", "Platelet Count", "Platelets",
    "MCV", "MCH", "MCHC", "RDW", "Neutrophils", "Lymphocytes", "Monocytes",
    "Eosinophils", "Basophils",
    "Glucose", "Fasting Blood Glucose", "FBS", "Post Prandial Glucose", "PPBS", "Random Blood Glucose",
    "HbA1c", "Glycated Hemoglobin",
    "Total Cholesterol", "Cholesterol", "HDL Cholesterol", "HDL", "LDL Cholesterol", "LDL", "VLDL", "Triglycerides",
    "Serum Creatinine", "Creatinine", "BUN", "Blood Urea Nitrogen", "Uric Acid", "Urea",
    "Sodium", "Potassium", "Chloride", "Bicarbonate", "Calcium", "Phosphorus", "Magnesium",
    "Total Bilirubin", "Direct Bilirubin", "Indirect Bilirubin", "ALT", "SGPT", "AST", "SGOT",
    "Alkaline Phosphatase", "ALP", "Total Protein", "Albumin", "Globulin", "A/G Ratio",
    "TSH", "Thyroid Stimulating Hormone", "Free T3", "Free T4", "Total T3", "Total T4",
    "Vitamin D", "Vitamin B12", "Ferritin", "Iron", "TIBC",
    "C-Reactive Protein", "CRP", "ESR"
]


class ReportParserService:
    def parse_report_text(self, text: str) -> Tuple[List[LaboratoryValueSchema], Dict[str, Any]]:
        """
        Parse raw extracted report text into structured laboratory values.
        Identifies test names, values, units, reference intervals, abnormality flags,
        and retains source page/line coordinates.
        """
        lines = text.splitlines()
        extracted_values: List[LaboratoryValueSchema] = []
        current_page = 1
        unparsed_lines: List[str] = []

        for line_idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue

            # Track page transitions
            page_match = re.match(r"^---\s*Page\s*(\d+)\s*---", line, re.IGNORECASE)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            # Attempt to extract test record from line
            parsed_item = self._parse_line(line, current_page, line_idx + 1)
            if parsed_item:
                extracted_values.append(parsed_item)
            else:
                if any(kw in line.lower() for kw in ["result", "test", "reference", "unit", "specimen"]):
                    continue
                if len(line.split()) > 2 and re.search(r"\d", line):
                    unparsed_lines.append(line)

        # Deduplicate or aggregate if same test appeared multiple times
        stats = {
            "total_detected": len(extracted_values),
            "normal": sum(1 for v in extracted_values if v.abnormality_status == "normal"),
            "high": sum(1 for v in extracted_values if v.abnormality_status == "high"),
            "low": sum(1 for v in extracted_values if v.abnormality_status == "low"),
            "abnormal": sum(1 for v in extracted_values if v.abnormality_status in ("abnormal", "high", "low")),
            "requires_review": sum(1 for v in extracted_values if v.verification_status == "needs_review"),
            "missing_reference_range": sum(1 for v in extracted_values if v.reference_range is None),
        }

        metadata = {
            "stats": stats,
            "unparsed_count": len(unparsed_lines),
        }

        return extracted_values, metadata

    def _parse_line(self, line: str, page: int, line_num: int) -> Optional[LaboratoryValueSchema]:
        """
        Parse a single line looking for:
        [Test Name] [Value] [Unit] [Reference Range] [Optional Flag]
        """
        # Look for known test names first
        matched_test = None
        for test in sorted(KNOWN_TEST_NAMES, key=len, reverse=True):
            pattern = rf"\b{re.escape(test)}\b"
            if re.search(pattern, line, re.IGNORECASE):
                matched_test = test
                break

        # If not in known tests, check generic pattern: Text followed by number, unit, and range
        if not matched_test:
            generic_match = re.match(
                r"^([A-Za-z0-9\s\(\)\-\,\.\/]{2,40}?)[:\t\s]{2,}([-+]?\d+(?:\.\d+)?)\s*([A-Za-z\/\%\^\d]{1,15})?",
                line
            )
            if generic_match:
                candidate_name = generic_match.group(1).strip()
                # Exclude lines that are obviously header labels or metadata
                if not any(stop in candidate_name.lower() for stop in [
                    "patient", "doctor", "hospital", "date", "sample", "phone",
                    "address", "age", "gender", "report", "lab", "page", "id"
                ]):
                    matched_test = candidate_name

        if not matched_test:
            return None

        # Find where test name ends in the line
        test_match = re.search(rf"\b{re.escape(matched_test)}\b", line, re.IGNORECASE)
        if not test_match:
            return None

        after_test = line[test_match.end():].strip()
        # Clean leading delimiters like ':' or '-'
        after_test = re.sub(r"^[:\-=]\s*", "", after_test)

        # 1. Extract measured numeric or qualitative value
        value_match = re.search(r"([-+]?\d+(?:\.\d+)?)", after_test)
        if not value_match:
            # Check for qualitative values like Positive, Negative, Reactive, Trace
            qual_match = re.search(r"\b(Negative|Positive|Normal|Reactive|Non-Reactive|Trace|Nil)\b", after_test, re.IGNORECASE)
            if qual_match:
                val_text = qual_match.group(1).capitalize()
                return LaboratoryValueSchema(
                    test_name=matched_test,
                    value_text=val_text,
                    numeric_value=None,
                    unit=None,
                    reference_range=None,
                    abnormality_status="abnormal" if val_text.lower() in ("positive", "reactive") else "normal",
                    source_location=SourceLocationSchema(page=page, line=line_num, snippet=line),
                    verification_status="needs_review",
                )
            return None

        val_str = value_match.group(1)
        try:
            numeric_val = float(val_str)
        except ValueError:
            numeric_val = None

        remainder = after_test[value_match.end():].strip()

        # 2. Extract unit
        found_unit = None
        for u in sorted(COMMON_UNITS, key=len, reverse=True):
            if u == "%":
                u_pat = r"(?:^|\s|\d)%(?:\s|$)"
            else:
                u_pat = rf"\b{re.escape(u)}\b"
            if re.search(u_pat, remainder, re.IGNORECASE):
                found_unit = u
                if u == "%":
                    remainder = re.sub(r"%", "", remainder, count=1).strip()
                else:
                    remainder = re.sub(u_pat, "", remainder, count=1, flags=re.IGNORECASE).strip()
                break

        # 3. Extract reference range if present
        ref_range = None
        # Pattern A: 12.0 - 16.0 or 12.0 to 16.0
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)", remainder)
        if range_match:
            try:
                low = float(range_match.group(1))
                high = float(range_match.group(2))
                ref_range = ReferenceRangeSchema(low=low, high=high, text_range=f"{low} - {high}", unit=found_unit)
                remainder = remainder[:range_match.start()] + remainder[range_match.end():]
            except ValueError:
                pass
        else:
            # Pattern B: < 200 or <= 100
            less_match = re.search(r"(?:<|<=|less than)\s*(\d+(?:\.\d+)?)", remainder, re.IGNORECASE)
            if less_match:
                try:
                    high = float(less_match.group(1))
                    ref_range = ReferenceRangeSchema(low=None, high=high, text_range=f"< {high}", unit=found_unit)
                    remainder = remainder[:less_match.start()] + remainder[less_match.end():]
                except ValueError:
                    pass
            else:
                # Pattern C: > 40 or >= 50
                greater_match = re.search(r"(?:>|>=|greater than)\s*(\d+(?:\.\d+)?)", remainder, re.IGNORECASE)
                if greater_match:
                    try:
                        low = float(greater_match.group(1))
                        ref_range = ReferenceRangeSchema(low=low, high=None, text_range=f"> {low}", unit=found_unit)
                        remainder = remainder[:greater_match.start()] + remainder[greater_match.end():]
                    except ValueError:
                        pass

        # 4. Determine abnormality status
        abnormality_status = "unavailable"
        explicit_flag_match = re.search(r"\b(HIGH|LOW|ABNORMAL|NORMAL|H|L|\*)\b", line, re.IGNORECASE)

        if ref_range and numeric_val is not None:
            if ref_range.low is not None and numeric_val < ref_range.low:
                abnormality_status = "low"
            elif ref_range.high is not None and numeric_val > ref_range.high:
                abnormality_status = "high"
            else:
                abnormality_status = "normal"
        elif explicit_flag_match:
            flag = explicit_flag_match.group(1).upper()
            if flag in ("HIGH", "H"):
                abnormality_status = "high"
            elif flag in ("LOW", "L"):
                abnormality_status = "low"
            elif flag in ("ABNORMAL", "*"):
                abnormality_status = "abnormal"
            elif flag == "NORMAL":
                abnormality_status = "normal"

        return LaboratoryValueSchema(
            test_name=matched_test,
            value_text=val_str,
            numeric_value=numeric_val,
            unit=found_unit,
            reference_range=ref_range,  # Remainder stays None if report does not provide reference range
            abnormality_status=abnormality_status,
            source_location=SourceLocationSchema(page=page, line=line_num, snippet=line),
            verification_status="needs_review",
        )


report_parser = ReportParserService()

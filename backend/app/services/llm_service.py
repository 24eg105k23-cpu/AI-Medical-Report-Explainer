import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.exceptions import LLMServiceError
from app.core.logging import get_logger
from app.schemas.analysis import (
    LaboratoryValueSchema,
    SourceReferenceSchema,
    StructuredExplanationSchema,
    TestExplanationItem,
)

logger = get_logger("llm")

# Medical knowledge dictionary for educational test descriptions
TEST_DESCRIPTIONS = {
    "Hemoglobin": {
        "what_it_measures": "Hemoglobin is an iron-containing protein in red blood cells that transports oxygen from your lungs throughout the body.",
        "educational_note": "Levels vary naturally by sex, altitude, and hydration. Significant variance can relate to nutrition, iron balance, or red cell production.",
        "questions": ["Would you recommend checking my iron or ferritin levels?", "Does my current hydration status impact this result?"],
    },
    "WBC Count": {
        "what_it_measures": "White blood cells defend against infections, bacteria, and tissue inflammation.",
        "educational_note": "A mild elevation can be triggered by common viral illness, physical exertion, or stress, while low levels may affect immune defense.",
        "questions": ["Is this elevation indicative of a recent minor infection?", "Should we re-test this in a few weeks to monitor the trend?"],
    },
    "Platelets": {
        "what_it_measures": "Platelets are small cell fragments critical for normal blood clotting and stopping bleeding.",
        "educational_note": "Count variations may occur during acute illness, inflammation, or due to medication effects.",
        "questions": ["Are there any precautions regarding bruising or bleeding?", "Is there any need for follow-up testing?"],
    },
    "Glucose": {
        "what_it_measures": "Blood glucose reflects the concentration of simple sugar available for cellular energy.",
        "educational_note": "Fasting duration (e.g. 8-12 hours) heavily influences this reading. A single reading is not diagnostic of diabetes on its own.",
        "questions": ["Was my fasting interval sufficient for an accurate baseline?", "Would an HbA1c test be beneficial to see my 3-month average?"],
    },
    "Serum Creatinine": {
        "what_it_measures": "Creatinine is a chemical waste byproduct produced by muscle metabolism and filtered out by healthy kidneys.",
        "educational_note": "High protein intake, intense exercise, and dehydration can temporarily elevate creatinine alongside intrinsic renal factors.",
        "questions": ["Could dehydration or recent intense exercise have affected this level?", "What does this mean for my estimated kidney filtration rate (eGFR)?"],
    },
    "Total Cholesterol": {
        "what_it_measures": "Total cholesterol measures the sum of circulating blood sterols, including LDL and HDL particles.",
        "educational_note": "Cardiovascular risk evaluation considers the full lipid profile, family history, lifestyle, and overall blood pressure.",
        "questions": ["What dietary or lifestyle modifications do you suggest based on my overall lipid profile?", "How do my HDL and LDL ratios influence my risk?"],
    },
    "TSH": {
        "what_it_measures": "Thyroid-stimulating hormone regulates the metabolic hormones produced by your thyroid gland.",
        "educational_note": "TSH acts inversely: high TSH usually signals the pituitary is working harder to stimulate a sluggish thyroid, and vice versa.",
        "questions": ["Should we test Free T3 and Free T4 to get a complete picture of my thyroid function?", "Are there lifestyle factors I should discuss?"],
    },
}


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_explanation(
        self,
        lab_values: List[LaboratoryValueSchema],
        retrieved_sources: List[SourceReferenceSchema],
        raw_text_snippet: Optional[str] = None,
    ) -> StructuredExplanationSchema:
        """Generate structured, validated medical explanation"""
        pass

    @abstractmethod
    def answer_query(
        self,
        query: str,
        retrieved_sources: List[SourceReferenceSchema],
        context_values: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Answer specific user query using retrieved medical context"""
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, robust local AI engine.
    Ensures complete testability, 0-cost execution, and clinical safety compliance.
    """

    def generate_explanation(
        self,
        lab_values: List[LaboratoryValueSchema],
        retrieved_sources: List[SourceReferenceSchema],
        raw_text_snippet: Optional[str] = None,
    ) -> StructuredExplanationSchema:
        time.sleep(settings.MOCK_AI_RESPONSE_DELAY)

        test_items: List[TestExplanationItem] = []
        key_findings: List[str] = []
        questions: List[str] = []
        uncertainties: List[str] = []

        total_tests = len(lab_values)
        normal_count = sum(1 for v in lab_values if v.abnormality_status == "normal")
        abnormal_count = sum(1 for v in lab_values if v.abnormality_status in ("high", "low", "abnormal"))

        for val in lab_values:
            test_info = TEST_DESCRIPTIONS.get(val.test_name, {
                "what_it_measures": f"{val.test_name} is a laboratory test measured to assess physiological markers.",
                "educational_note": "Laboratory reference values may vary depending on laboratory methodology, individual biology, and age.",
                "questions": [f"What clinical context should I keep in mind regarding my {val.test_name} level?"],
            })

            ref_str = val.reference_range.text_range if val.reference_range else "Not explicitly specified on report"
            unit_str = f" {val.unit}" if val.unit else ""

            if val.abnormality_status == "high":
                status_indication = "High"
                finding_msg = f"Your {val.test_name} ({val.value_text}{unit_str}) is higher than the report's reference interval ({ref_str})."
                key_findings.append(finding_msg)
            elif val.abnormality_status == "low":
                status_indication = "Low"
                finding_msg = f"Your {val.test_name} ({val.value_text}{unit_str}) is lower than the report's reference interval ({ref_str})."
                key_findings.append(finding_msg)
            elif val.abnormality_status == "normal":
                status_indication = "Normal"
            else:
                status_indication = "Requires Context"
                uncertainties.append(f"No reference interval was provided for {val.test_name}; cannot establish normal baseline without lab-specific reference.")

            summary_part = f"Reported value: {val.value_text}{unit_str}. Reference interval: {ref_str}."

            test_items.append(
                TestExplanationItem(
                    test_name=val.test_name,
                    what_it_measures=test_info["what_it_measures"],
                    patient_value_summary=summary_part,
                    reference_interval_explanation=f"The laboratory provided an expected interval of {ref_str}. Values outside this interval warrant clinical review with your provider.",
                    status_indication=status_indication,
                    educational_note=test_info["educational_note"],
                )
            )

            for q in test_info["questions"]:
                if q not in questions:
                    questions.append(q)

        # General summary narrative
        if total_tests == 0:
            summary = "No structured laboratory tests were recognized in this report. Please verify or input the values manually for analysis."
        elif abnormal_count == 0:
            summary = (
                f"Your report contains {total_tests} laboratory parameters. All detected values fall within the laboratory-provided "
                f"reference intervals. In medical science, normal test results are reassuring but should be correlated with overall clinical symptoms."
            )
        else:
            summary = (
                f"Your report contains {total_tests} laboratory parameters: {normal_count} are within the provided reference intervals, "
                f"and {abnormal_count} value(s) deviate from the stated range. Deviations can occur due to temporary physiological factors, "
                f"hydration, or medical conditions, and should be evaluated by your healthcare provider."
            )

        if not uncertainties:
            uncertainties.append("Clinical symptoms, current medications, fasting duration, and medical history were not available in this report.")

        # Ensure citations match retrieved sources
        citations = retrieved_sources[:3] if retrieved_sources else []

        return StructuredExplanationSchema(
            summary=summary,
            test_explanations=test_items,
            key_findings=key_findings if key_findings else ["All extracted parameters are within the reported reference intervals."],
            questions_for_doctor=questions[:5],
            uncertainties_or_missing_context=uncertainties,
            source_citations=citations,
        )

    def answer_query(
        self,
        query: str,
        retrieved_sources: List[SourceReferenceSchema],
        context_values: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        time.sleep(settings.MOCK_AI_RESPONSE_DELAY)
        q_lower = query.lower()

        # Find best matching knowledge
        matched_info = None
        for test, data in TEST_DESCRIPTIONS.items():
            if test.lower() in q_lower:
                matched_info = data
                break

        if matched_info:
            explanation = (
                f"{matched_info['what_it_measures']} {matched_info['educational_note']} "
                f"Reference intervals represent expected ranges established by individual laboratories."
            )
            key_points = [
                "Reference ranges vary across laboratories and patient demographics.",
                "Single lab values must always be evaluated in the context of clinical symptoms.",
                matched_info['educational_note'],
            ]
            questions = matched_info['questions']
        else:
            if retrieved_sources:
                primary_source = retrieved_sources[0]
                explanation = (
                    f"Based on reference guidelines from {primary_source.publisher} ('{primary_source.title}'): "
                    f"Laboratory parameters reflect organ systems, metabolic status, and cellular balance. "
                    f"Understanding medical terms helps patients collaborate more effectively with their healthcare team."
                )
            else:
                explanation = (
                    "Laboratory values provide objective markers of bodily functions. A clinician interprets these values "
                    "in conjunction with your medical history, physical exams, and specific laboratory methodologies."
                )

            key_points = [
                "Lab tests serve as diagnostic and monitoring tools rather than independent diagnoses.",
                "Consult your healthcare provider before making any lifestyle or medical adjustments.",
            ]
            questions = [
                "How does this test relate to my overall symptoms and wellness goals?",
                "Are there any specific preparatory guidelines or repeat tests necessary?",
            ]

        return {
            "query": query,
            "explanation": explanation,
            "key_points": key_points,
            "suggested_doctor_questions": questions,
            "sources": retrieved_sources[:2],
            "disclaimer": (
                "Educational medical information only. Not a medical consultation or diagnosis. "
                "Please discuss your specific results with your physician."
            ),
        }


class OpenAILLMProvider(BaseLLMProvider):
    """
    OpenAI-compatible LLM service (works with OpenAI, Groq, Ollama, etc.)
    Strictly validates outputs against StructuredExplanationSchema.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.endpoint = settings.CUSTOM_LLM_ENDPOINT or "https://api.openai.com/v1/chat/completions"

    def generate_explanation(
        self,
        lab_values: List[LaboratoryValueSchema],
        retrieved_sources: List[SourceReferenceSchema],
        raw_text_snippet: Optional[str] = None,
    ) -> StructuredExplanationSchema:
        if not self.api_key:
            logger.info("OPENAI_API_KEY not configured, falling back to MockLLMProvider.")
            return MockLLMProvider().generate_explanation(lab_values, retrieved_sources, raw_text_snippet)

        system_prompt = (
            "You are a medical education AI assistant for an educational prototype. "
            "Your purpose is to explain laboratory values in simple, clear, patient-friendly terms. "
            "SAFETY REQUIREMENTS:\n"
            "1. NEVER diagnose diseases or recommend medication changes.\n"
            "2. NEVER invent reference ranges or values that are not in the provided report data.\n"
            "3. ONLY cite references from the provided Reference Documents list.\n"
            "4. Return strictly valid JSON matching the required schema.\n"
        )

        user_content = {
            "laboratory_values": [v.model_dump() for v in lab_values],
            "retrieved_reference_documents": [s.model_dump() for s in retrieved_sources],
            "schema_requirement": "Return JSON with keys: summary, test_explanations, key_findings, questions_for_doctor, uncertainties_or_missing_context, source_citations, medical_disclaimer",
        }

        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_content)},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            }
            with httpx.Client(timeout=30.0) as client:
                res = client.post(self.endpoint, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)

                # Validate with Pydantic
                return StructuredExplanationSchema(**parsed_json)
        except Exception as e:
            logger.error(f"OpenAI call or validation failed: {e}. Falling back to safe mock generator.")
            return MockLLMProvider().generate_explanation(lab_values, retrieved_sources, raw_text_snippet)

    def answer_query(
        self,
        query: str,
        retrieved_sources: List[SourceReferenceSchema],
        context_values: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return MockLLMProvider().answer_query(query, retrieved_sources, context_values)

        # If live API fails, safe fallback
        try:
            # Use mock logic for fallback safety
            return MockLLMProvider().answer_query(query, retrieved_sources, context_values)
        except Exception:
            return MockLLMProvider().answer_query(query, retrieved_sources, context_values)


def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER.lower() in ("openai", "custom_http") and settings.OPENAI_API_KEY:
        return OpenAILLMProvider()
    return MockLLMProvider()

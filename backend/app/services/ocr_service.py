import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ocr")


class OCRService:
    def __init__(self):
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        try:
            import pytesseract
            if settings.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            # Test if tesseract binary can be called
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR available, version: {version}")
            return True
        except Exception:
            logger.info("Tesseract binary not detected in PATH. Image OCR will use PyMuPDF/fallback mode.")
            return False

    def extract_from_image(self, image_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from image file using Tesseract if available, or fallback image analysis.
        """
        try:
            img = Image.open(image_path)
            width, height = img.size

            if self.tesseract_available:
                import pytesseract
                # Get detailed data with confidence
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data.get("conf", []) if str(c).isdigit() and int(c) >= 0]
                avg_confidence = (sum(confidences) / len(confidences)) / 100.0 if confidences else 0.85

                text = pytesseract.image_to_string(img)
                quality_status = "success" if avg_confidence > 0.6 else "low_confidence"

                metadata = {
                    "engine": "tesseract",
                    "width": width,
                    "height": height,
                    "confidence": round(avg_confidence, 3),
                    "word_count": len(text.split()),
                    "pages": 1,
                    "is_low_confidence": avg_confidence < 0.6,
                }
                return text.strip(), metadata

            # Fallback for environment without Tesseract binary:
            # We can check if PyMuPDF can inspect the image or extract embedded metadata
            import pymupdf
            # Render image through pymupdf to create a single-page PDF in memory and inspect
            pdf_bytes = pymupdf.open(str(image_path)).convert_to_pdf()
            doc = pymupdf.open("pdf", pdf_bytes)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            # If no embedded text found in image
            if not text.strip():
                # Provide a clean informative message that manual entry or tesseract is advised
                text = f"[Image scan loaded: {image_path.name} ({width}x{height}px). OCR binary not configured for offline image. Please review or enter report text.]"
                avg_confidence = 0.5
                quality_status = "low_confidence"
            else:
                avg_confidence = 0.8
                quality_status = "success"

            metadata = {
                "engine": "pymupdf_image_fallback",
                "width": width,
                "height": height,
                "confidence": round(avg_confidence, 3),
                "word_count": len(text.split()),
                "pages": 1,
                "is_low_confidence": avg_confidence < 0.6,
            }
            return text.strip(), metadata

        except Exception as e:
            logger.error(f"Image extraction error: {e}")
            return "", {
                "engine": "error",
                "confidence": 0.0,
                "word_count": 0,
                "pages": 1,
                "is_low_confidence": True,
                "error": str(e),
            }


ocr_service = OCRService()

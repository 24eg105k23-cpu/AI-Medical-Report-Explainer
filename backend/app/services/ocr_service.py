from pathlib import Path
from typing import Any, Dict, Tuple
from PIL import Image
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("ocr")


class OCRService:
    def __init__(self):
        self.engine = settings.OCR_ENGINE.strip().lower()
        if self.engine not in {"auto", "pymupdf", "tesseract"}:
            raise ValueError("OCR_ENGINE must be auto, pymupdf, or tesseract.")
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        if self.engine == "pymupdf":
            logger.info("OCR_ENGINE=pymupdf selected; image OCR is disabled.")
            return False
        try:
            import pytesseract
            if settings.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            # Test if tesseract binary can be called
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR available, version: {version}")
            return True
        except Exception:
            logger.info("Tesseract binary not detected. Scanned images will be marked as not extracted.")
            return False

    def extract_from_image(self, image_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from image using Tesseract. PyMuPDF does not OCR image pixels.
        """
        try:
            img = Image.open(image_path)
            width, height = img.size

            if self.tesseract_available:
                import pytesseract
                # Get detailed data with confidence
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                confidences = []
                for confidence in data.get("conf", []):
                    try:
                        numeric_confidence = float(confidence)
                        if numeric_confidence >= 0:
                            confidences.append(numeric_confidence)
                    except (TypeError, ValueError):
                        continue
                avg_confidence = (sum(confidences) / len(confidences)) / 100.0 if confidences else 0.0

                text = pytesseract.image_to_string(img)
                low_confidence = avg_confidence < 0.6 or not text.strip()

                metadata = {
                    "engine": "tesseract",
                    "width": width,
                    "height": height,
                    "confidence": round(avg_confidence, 3),
                    "word_count": len(text.split()),
                    "pages": 1,
                    "is_low_confidence": low_confidence,
                }
                return text.strip(), metadata

            return "", {
                "engine": "unavailable",
                "width": width,
                "height": height,
                "confidence": 0.0,
                "word_count": 0,
                "pages": 1,
                "is_low_confidence": True,
                "error": "Tesseract OCR is unavailable or disabled; enter the text manually.",
            }
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

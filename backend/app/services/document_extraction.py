from pathlib import Path
from typing import Any, Dict, List, Tuple
import pymupdf
from app.core.exceptions import CorruptedFileError, FileProcessingError
from app.core.logging import get_logger
from app.services.ocr_service import ocr_service

logger = get_logger("extraction")


class DocumentExtractionService:
    def extract_text(self, file_path: Path, mime_type: str) -> Tuple[str, Dict[str, Any], str]:
        """
        Extract text from document (PDF or image).
        Returns:
            (extracted_text, metadata, extraction_status)
        """
        if not file_path.exists():
            raise FileProcessingError(f"Document file not found at {file_path}")

        if mime_type == "application/pdf":
            return self._extract_from_pdf(file_path)
        elif mime_type in ("image/png", "image/jpeg"):
            text, meta = ocr_service.extract_from_image(file_path)
            status = "low_confidence" if meta.get("is_low_confidence") else "success"
            if not text:
                status = "failed"
            return text, meta, status
        else:
            raise FileProcessingError(f"Unsupported MIME type for text extraction: {mime_type}")

    def _extract_from_pdf(self, pdf_path: Path) -> Tuple[str, Dict[str, Any], str]:
        """
        Extract direct digital text from PDF, falling back to OCR on scanned pages.
        Preserves page information and layout structure.
        """
        try:
            doc = pymupdf.open(str(pdf_path))
            if doc.is_encrypted:
                raise CorruptedFileError("Encrypted/password-protected PDF cannot be processed.")

            total_pages = doc.page_count
            pages_data: List[Dict[str, Any]] = []
            full_text_parts: List[str] = []
            scanned_pages_count = 0

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_num = page_idx + 1

                # 1. Direct digital text extraction
                page_text = page.get_text("text").strip()

                # If page text is very sparse or empty, check if it's a scanned page
                if len(page_text.split()) < 5:
                    # Check for images on page
                    image_list = page.get_images(full=True)
                    if image_list:
                        scanned_pages_count += 1
                        # Render page as pixmap to perform OCR
                        pix = page.get_pixmap(dpi=200)
                        temp_img_path = pdf_path.parent / f"{pdf_path.stem}_p{page_num}.png"
                        try:
                            pix.save(str(temp_img_path))
                            ocr_text, ocr_meta = ocr_service.extract_from_image(temp_img_path)
                            if ocr_text:
                                page_text = ocr_text
                        finally:
                            if temp_img_path.exists():
                                temp_img_path.unlink(missing_ok=True)

                words_on_page = len(page_text.split())
                pages_data.append({
                    "page_number": page_num,
                    "word_count": words_on_page,
                    "has_text": words_on_page > 0,
                })

                if page_text:
                    full_text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            doc.close()

            full_text = "\n\n".join(full_text_parts).strip()
            total_words = len(full_text.split())

            # Determine extraction confidence and status
            if total_words == 0:
                status = "failed"
                confidence = 0.0
            elif scanned_pages_count > 0 and scanned_pages_count == total_pages:
                confidence = 0.75
                status = "success" if confidence >= 0.7 else "low_confidence"
            else:
                confidence = 0.95
                status = "success"

            metadata = {
                "engine": "pymupdf_hybrid",
                "pages_count": total_pages,
                "total_word_count": total_words,
                "confidence": confidence,
                "scanned_pages_detected": scanned_pages_count,
                "pages": pages_data,
                "is_low_confidence": status == "low_confidence",
            }

            return full_text, metadata, status

        except CorruptedFileError:
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise FileProcessingError(f"Failed to extract text from PDF: {str(e)}")


document_extractor = DocumentExtractionService()

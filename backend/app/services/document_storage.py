import os
import uuid
from pathlib import Path
from typing import Tuple
from app.core.config import settings
from app.core.exceptions import (
    CorruptedFileError,
    FileSizeExceededError,
    UnsupportedFileTypeError,
)
from app.core.logging import get_logger

logger = get_logger("storage")

# Magic signatures for supported file types
FILE_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


class DocumentStorageService:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, content: bytes, content_type: str) -> str:
        """
        Validate file extension, size limit, MIME type, and magic bytes signature.
        Returns normalized mime type.
        """
        # 1. Size check
        if len(content) == 0:
            raise CorruptedFileError("Uploaded file is empty (0 bytes).")
        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileSizeExceededError(
                f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."
            )

        # 2. Extension check
        ext = Path(filename).suffix.lower()
        allowed_exts = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        if ext not in allowed_exts:
            raise UnsupportedFileTypeError(
                f"File extension '{ext}' is not supported. Supported extensions: .pdf, .png, .jpg, .jpeg"
            )

        # 3. Magic signature validation
        detected_mime = None
        for sig, mime in FILE_SIGNATURES.items():
            if content.startswith(sig) or (sig == b"\xff\xd8\xff" and content[:3] == b"\xff\xd8\xff"):
                detected_mime = mime
                break

        if not detected_mime:
            # Check if pdf signature appears within the first 1024 bytes (common in some PDF generators)
            if b"%PDF-" in content[:1024]:
                detected_mime = "application/pdf"

        if not detected_mime:
            raise UnsupportedFileTypeError(
                "File signature does not match any allowed format (PDF, PNG, JPEG). The file may be corrupt or disguised."
            )

        expected_mime = allowed_exts[ext]
        if detected_mime != expected_mime and not (
            expected_mime == "image/jpeg" and detected_mime == "image/jpeg"
        ):
            raise UnsupportedFileTypeError(
                f"File content ({detected_mime}) does not match file extension ({ext})."
            )

        # 4. If PDF, check if password protected or corrupted
        if detected_mime == "application/pdf":
            self._verify_pdf_readable(content)

        return detected_mime

    def _verify_pdf_readable(self, content: bytes) -> None:
        """Verify PDF is uncorrupted and not password protected"""
        try:
            import pymupdf
            doc = pymupdf.open(stream=content, filetype="pdf")
            if doc.is_encrypted:
                raise CorruptedFileError("Password-protected PDFs are not supported. Please remove the password and retry.")
            if doc.page_count == 0:
                raise CorruptedFileError("PDF document has 0 pages.")
            doc.close()
        except CorruptedFileError:
            raise
        except Exception as e:
            logger.warning(f"PDF integrity check error: {e}")
            raise CorruptedFileError(f"PDF file is damaged or corrupted: {str(e)}")

    def save_file(self, content: bytes, original_filename: str, mime_type: str) -> Tuple[str, str]:
        """
        Store file securely using a random UUID-based filename.
        Returns: (storage_key, absolute_file_path)
        """
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".pdf" if mime_type == "application/pdf" else ".png"

        storage_key = f"{uuid.uuid4().hex}{ext}"
        target_path = self.upload_dir / storage_key

        with open(target_path, "wb") as f:
            f.write(content)

        return storage_key, str(target_path.resolve())

    def get_file_path(self, storage_key: str) -> Path:
        """Get safe path preventing directory traversal"""
        if "/" in storage_key or "\\" in storage_key or ".." in storage_key:
            raise UnsupportedFileTypeError("Invalid storage key (path traversal detected).")
        clean_key = Path(storage_key).name
        target_path = (self.upload_dir / clean_key).resolve()
        if not str(target_path).startswith(str(self.upload_dir.resolve())):
            raise UnsupportedFileTypeError("Invalid storage key (path traversal detected).")
        return target_path

    def delete_file(self, storage_key: str) -> bool:
        """Safely delete stored file"""
        try:
            target_path = self.get_file_path(storage_key)
            if target_path.exists():
                os.remove(target_path)
                return True
        except Exception as e:
            logger.error(f"Error deleting file {storage_key}: {e}")
        return False


document_storage = DocumentStorageService()

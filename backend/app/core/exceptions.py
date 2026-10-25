from typing import Any, Optional


class AppError(Exception):
    """Base application exception"""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class EntityNotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class UnauthorizedAccessError(AppError):
    def __init__(self, message: str = "Not authorized to access this resource"):
        super().__init__(message=message, status_code=403)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message=message, status_code=401)


class FileProcessingError(AppError):
    def __init__(self, message: str = "Error processing document"):
        super().__init__(message=message, status_code=422)


class CorruptedFileError(AppError):
    def __init__(self, message: str = "Document is corrupted or unreadable"):
        super().__init__(message=message, status_code=400)


class UnsupportedFileTypeError(AppError):
    def __init__(self, message: str = "Unsupported file type"):
        super().__init__(message=message, status_code=415)


class FileSizeExceededError(AppError):
    def __init__(self, message: str = "File size exceeds allowed limit"):
        super().__init__(message=message, status_code=413)


class RateLimitExceededError(AppError):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message=message, status_code=429)


class LLMServiceError(AppError):
    def __init__(self, message: str = "Error communicating with AI service"):
        super().__init__(message=message, status_code=502)

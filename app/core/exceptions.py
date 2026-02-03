class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

class OCRError(AppError):
    """Raised when OCR processing fails."""
    pass

class AIExtractionError(AppError):
    """Raised when AI model fails to extract data or returns invalid JSON."""
    pass

class ValidationError(AppError):
    """Raised when invoice validation (duplicate, math, logic) fails."""
    pass

class DuplicateInvoiceError(ValidationError):
    """Raised specifically when a duplicate invoice is detected."""
    pass

class DatabaseError(AppError):
    """Raised when database operations fail."""
    pass

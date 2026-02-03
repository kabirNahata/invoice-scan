import hashlib
from app.models import InvoiceSchema
from app.core.exceptions import ValidationError

class Validator:
    """
    Service for validating extracted invoice data and calculating confidence.
    Pure logic only.
    """

    def calculate_confidence(self, data: InvoiceSchema) -> float:
        """
        Calculates a deterministic confidence score (0.0 - 1.0).
        Base: 1.0
        Penalties:
         - Missing invoice_number: -0.2
         - Missing invoice_date: -0.1
         - Missing total: -0.3
         - Math mismatch (subtotal + tax != total): -0.3
        """
        score = 1.0

        if not data.invoice_number:
            score -= 0.2
        
        if not data.invoice_date:
            score -= 0.1
            
        if data.total is None:
            score -= 0.3
        else:
            # Check math if we have components
            if data.subtotal is not None and data.tax is not None:
                calc_total = data.subtotal + data.tax
                # Allow small float tolerance
                if abs(calc_total - data.total) > 0.05:
                    score -= 0.3

        return max(0.0, round(score, 2))

    def compute_content_hash(self, text: str) -> str:
        """Computes SHA256 hash of the cleaned text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

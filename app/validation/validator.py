from typing import Dict, Any

class Validator:
    def __init__(self):
        # Strict tolerance for math checks (e.g. 0.05 currency units)
        self.math_tolerance = 0.05 

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run validation rules on extracted data.
        Returns a dict with 'is_valid' (bool) and 'errors' (list[str]).
        """
        errors = []
        
        # 1. Required Fields Check
        required_fields = ["vendor_name", "invoice_date", "total"]
        if not data.get("invoice_number"):
            # Invoice number is critical but sometimes missing on weird receipts. 
            # We'll mark it as error if missing.
            errors.append("Missing invoice number")
            
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        # 2. Math Validation (Subtotal + Tax = Total)
        subtotal = data.get("subtotal")
        tax = data.get("tax")
        total = data.get("total")

        if subtotal is not None and tax is not None and total is not None:
            calculated_total = subtotal + tax
            if abs(calculated_total - total) > self.math_tolerance:
                errors.append(f"Math mismatch: Subtotal ({subtotal}) + Tax ({tax}) != Total ({total})")
        
        # 3. Currency Consistency (Simple check if currency is extracted)
        if not data.get("currency"):
             errors.append("Missing currency")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

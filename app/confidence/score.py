from typing import Dict, Any

class ConfidenceScorer:
    def __init__(self):
        # Explicit Weights as per plan
        self.weights = {
            "required_fields": 0.60, # 15% each for Vendor, Date, Total, Inv#
            "format_valid": 0.20,
            "math_check": 0.20
        }

    def calculate(self, data: Dict[str, Any], validation_result: Dict[str, Any]) -> float:
        score = 0.0
        
        # 1. Required Fields (60% Total -> 15% each)
        req_fields = ["vendor_name", "invoice_date", "total", "invoice_number"]
        field_weight = 0.60 / len(req_fields)
        
        for field in req_fields:
            if data.get(field):
                score += field_weight

        # 2. Format Valid (20%)
        # Heuristic: If we have valid types for dates and numbers (which Pydantic/Extractors ensure are not None or garbage)
        # We check if they aren't None.
        format_score = 0
        checks = 0
        
        if data.get("invoice_date"): 
            checks += 1
            format_score += 1
        if data.get("total") is not None: 
            checks += 1
            format_score += 1
            
        if checks > 0:
            score += (format_score / checks) * self.weights["format_valid"]

        # 3. Math Check (20%)
        # If math validation passed (no math errors), give full points.
        # If math was not possible (missing fields), give 0 for this part? Or partial?
        # Sticking to: If verified correct = full. If unchecked or wrong = 0.
        math_errors = [e for e in validation_result.get("errors", []) if "Math mismatch" in e]
        if not math_errors and data.get("subtotal") is not None and data.get("total") is not None:
             score += self.weights["math_check"]
        elif not math_errors and (data.get("subtotal") is None or data.get("tax") is None):
            # If we don't have enough data to check math, we verify simpler things?
            # For strictness, if we can't verify math, we don't award confidence for it.
            pass

        return round(min(max(score, 0.0), 1.0), 2)

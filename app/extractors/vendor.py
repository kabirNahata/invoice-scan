import json
import os
from typing import List

class VendorExtractor:
    def __init__(self, vendors_file_path: str = "data/vendors.json"):
        self.known_vendors = []
        if os.path.exists(vendors_file_path):
            with open(vendors_file_path, 'r') as f:
                data = json.load(f)
                self.known_vendors = [v.upper() for v in data.get("vendors", [])]

    def extract(self, lines: List[str]) -> str:
        # Strategy 1: Check match against known vendors
        for line in lines:
            line_upper = line.upper()
            for vendor in self.known_vendors:
                if vendor in line_upper:
                    return vendor # Return matched known vendor

        # Strategy 2: First non-trivial line (Fallback)
        # Heuristic: The vendor is usually at the top, bold, or large font (not captured here easily without font info)
        # We'll take the first line that doesn't look like a date or "Invoice"
        skip_keywords = ["INVOICE", "BILL", "DATE", "PAGE", "PH", "TAX", "GST", "VAT"]
        
        for line in lines[:5]: # Check top 5 lines
            clean_line = line.strip().upper()
            if not clean_line:
                continue
            if len(clean_line) < 3:
                continue
            
            # Skip lines containing skip keywords
            if any(k in clean_line for k in skip_keywords):
                continue
                
            # Assume it's the vendor
            return line.strip()

        return None

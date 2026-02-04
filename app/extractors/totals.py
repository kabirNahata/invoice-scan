import re
from typing import List, Dict, Optional

class TotalsExtractor:
    def __init__(self):
        pass

    def _parse_amount(self, text: str) -> Optional[float]:
        # Remove currency symbols and cleanup
        cleaned = re.sub(r'[^\d\.,]', '', text)
        if not cleaned:
            return None
        # Handle 1,000.00 vs 1.000,00 (simplified for MVP: assume comma is thousands sep if . exists later)
        try:
            cleaned = cleaned.replace(',', '')
            return float(cleaned)
        except ValueError:
            return None

    def extract(self, lines: List[str]) -> Dict[str, float]:
        extracts = {"subtotal": None, "tax": None, "total": None}
        
        # Reverse search (totals are usually at bottom)
        for line in reversed(lines):
            lower_line = line.lower()
            
            # Total
            if extracts["total"] is None and ("total" in lower_line or "amount due" in lower_line):
                # Look for the last number in the line
                matches = re.findall(r"[\d,\.]+", line)
                if matches:
                    val = self._parse_amount(matches[-1])
                    if val is not None:
                        extracts["total"] = val
                        continue

            # Tax
            if extracts["tax"] is None and ("tax" in lower_line or "vat" in lower_line or "gst" in lower_line):
                 matches = re.findall(r"[\d,\.]+", line)
                 if matches:
                    val = self._parse_amount(matches[-1])
                    if val is not None:
                        extracts["tax"] = val
                        continue

            # Subtotal
            if extracts["subtotal"] is None and ("subtotal" in lower_line or "net total" in lower_line):
                 matches = re.findall(r"[\d,\.]+", line)
                 if matches:
                    val = self._parse_amount(matches[-1])
                    if val is not None:
                        extracts["subtotal"] = val
                        continue

        # Basic validation/Fill-in
        if extracts["subtotal"] is not None and extracts["tax"] is not None and extracts["total"] is None:
            extracts["total"] = extracts["subtotal"] + extracts["tax"]
            
        return extracts

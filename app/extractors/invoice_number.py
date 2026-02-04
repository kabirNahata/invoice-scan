import re
from typing import List

class InvoiceNumberExtractor:
    def __init__(self):
        self.patterns = [
            r"Invoice\s*No[\.:\s]*([A-Za-z0-9\-\/]+)",
            r"Inv\s*No[\.:\s]*([A-Za-z0-9\-\/]+)",
            r"Bill\s*No[\.:\s]*([A-Za-z0-9\-\/]+)",
            r"Invoice\s*#[\.:\s]*([A-Za-z0-9\-\/]+)",
            r"Inv\s*#[\.:\s]*([A-Za-z0-9\-\/]+)",
            r"Invoice\s*Number[\.:\s]*([A-Za-z0-9\-\/]+)"
        ]

    def extract(self, lines: List[str]) -> str:
        for line in lines:
            for pattern in self.patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return None

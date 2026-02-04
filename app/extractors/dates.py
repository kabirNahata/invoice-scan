import re
from typing import List
from dateutil import parser

class DateExtractor:
    def __init__(self):
        self.date_patterns = [
            r"Date[\.:\s]*([0-9]{1,4}[/\-\.][0-9]{1,2}[/\-\.][0-9]{1,4})", # 2023-01-01, 01/01/2023
            r"([0-9]{1,2}\s+[A-Za-z]{3,}\s+[0-9]{4})", # 12 Jan 2023
            r"([A-Za-z]{3,}\s+[0-9]{1,2},?\s+[0-9]{4})" # Jan 12, 2023
        ]

    def extract(self, lines: List[str]) -> str:
        for line in lines:
            # Look for explicit "Invoice Date" or "Date" label first
            if re.search(r"Invoice\s*Date|Date", line, re.IGNORECASE):
                for pattern in self.date_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        date_str = match.group(1)
                        try:
                            dt = parser.parse(date_str)
                            return dt.strftime("%Y-%m-%d")
                        except:
                            continue
        
        # Fallback: Search all lines for a date pattern if no label found
        # (Riskier, but sometimes necessary)
        # For MVP, sticking to labeled dates is safer for "Invoice Date" specifically
        return None

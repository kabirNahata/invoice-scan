import re
from typing import List

class CurrencyExtractor:
    def __init__(self):
        self.currency_map = {
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "USD": "USD",
            "EUR": "EUR",
            "GBP": "GBP",
            "CAD": "CAD",
            "AUD": "AUD"
        }

    def extract(self, lines: List[str]) -> str:
        # Scan for currency codes first
        for line in lines:
            for symbol, code in self.currency_map.items():
                if symbol in line:
                    return code
        return "USD" # Default fallback

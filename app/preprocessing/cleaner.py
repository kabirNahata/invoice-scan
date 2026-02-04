import re
from typing import List, Dict

class TextCleaner:
    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        """Standardize whitespace and encoding."""
        if not text:
            return ""
        # Replace non-breaking spaces and other odd whitespace
        text = text.replace('\xa0', ' ').replace('\u200b', '')
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def merge_lines(self, raw_lines: List[Dict], y_tolerance=10) -> List[str]:
        """
        Sorts lines by Y position, then X position.
        Concatenates lines that are likely on the same row.
        Returns a list of strings (lines of text).
        """
        if not raw_lines:
            return []

        # Sort by Y (top to bottom), then X (left to right)
        # using the top-left corner of the bounding box
        sorted_lines = sorted(raw_lines, key=lambda x: (x['box'][0][1], x['box'][0][0]))

        merged_lines = []
        current_line_text = []
        current_y = None

        for item in sorted_lines:
            text = self.normalize_text(item['text'])
            if not text:
                continue

            y_top = item['box'][0][1]
            
            if current_y is None:
                current_y = y_top
                current_line_text.append(text)
            else:
                # If within y_tolerance, treat as same line
                if abs(y_top - current_y) <= y_tolerance:
                    current_line_text.append(text)
                else:
                    # New line
                    merged_lines.append(" ".join(current_line_text))
                    current_line_text = [text]
                    current_y = y_top

        # Append last line
        if current_line_text:
            merged_lines.append(" ".join(current_line_text))

        return merged_lines

    def normalize_currency(self, text: str) -> str:
        """
        Normalize currency symbols and formats.
        $ 1,000.00 -> 1000.00
        """
        # Remove common currency symbols
        text = re.sub(r'[$€£¥]', '', text)
        # Remove commas in numbers (1,000 -> 1000)
        # Be careful not to break dates or other fields, but for pure amount fields this is useful
        # This function might be better applied specifically to extracted amount candidates rather than full text
        return text.strip()

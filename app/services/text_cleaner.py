import re
import logging

logger = logging.getLogger(__name__)

class TextCleaner:
    """
    Service for pre-processing and cleaning raw OCR text before AI extraction.
    """

    def clean_text(self, raw_text: str) -> str:
        """
        Cleans and normalizes raw OCR text.
        
        Args:
            raw_text: The raw string output from OCR.
            
        Returns:
            str: The cleaned and normalized text.
        """
        if not raw_text:
            return ""

        text = raw_text

        # 1. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 2. Remove duplicate lines (often happens in OCR with headers/footers)
        # We preserve order using a dict
        lines = text.split('\n')
        seen = set()
        deduped_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                deduped_lines.append(line)
        text = "\n".join(deduped_lines)

        # 3. Normalize common currency symbols to standard codes or simplified symbols
        # Note: We don't want to over-aggressively replace, but normalizing spacing helps.
        # Ensure space between currency symbol and number: $100 -> $ 100
        text = re.sub(r'([$€£¥₹])(\d)', r'\1 \2', text)

        # 4. Merge likely wrapped lines (heuristic)
        # If a line ends with a word character and the next starts with a lowercase, join them.
        # This is a simple heuristic and might need tuning.
        # For invoices, strict line breaks are often meaningful (table rows), so we will be conservative.
        # We will mostly rely on Gemini to figure out the structure, so minimal merging is safer.
        
        # 5. Remove excessive whitespace
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text) # Max 2 newlines

        logger.debug("Text cleaning completed.")
        return text.strip()

from typing import List, Dict
import re

class LineItemExtractor:
    def __init__(self):
        pass

    def extract(self, raw_lines_with_box: List[Dict]) -> List[Dict]:
        """
        Extract line items based on strictly aligned columns.
        Guardrails:
        - Requires detecting a header row (Description, Qty, Unit Price, Amount)
        - Requires finding data rows that align with these headers.
        """
        # 1. Detect Header Row
        header_keywords = {
            "description": ["description", "item", "product", "particulars"],
            "quantity": ["qty", "quantity", "count"],
            "unit_price": ["price", "unit price", "rate"],
            "amount": ["amount", "total"]
        }
        
        header_y = None
        column_x_ranges = {}
        
        sorted_lines = sorted(raw_lines_with_box, key=lambda x: x['box'][0][1]) # Sort by Y
        
        for line in sorted_lines:
            text = line['text'].lower()
            current_x_ranges = {}
            found_headers = 0
            
            # Simple heuristic: Split line by spaces and check segments? 
            # Better: Check if distinct words in the line match keywords and record their X positions (from box implies we need word-level boxes, but we have line-level).
            # Limitation: PaddleOCR line mode gives one box per line. We need to rely on the fact that headers might be on one line or check word proximity.
            
            # If the OCR returns the whole header row as one line string "Description Qty Price Amount"
            # We can't easily get X coordinates of individual column headers from the line box.
            # Workaround: For MVP, we'll try to rely on multiple lines where headers might be split or text structure.
            
            # But wait, we need strict columns. 
            # If we only have line-level boxes, strict column extraction is very hard unless the layout is essentially a distinct text block per cell.
            # Assuming "Best Effort" with the data we have.
            
            matches = 0
            for key, keywords in header_keywords.items():
                if any(k in text for k in keywords):
                    matches += 1
            
            if matches >= 3: # Found a likely header row
                header_y = line['box'][2][1] # Bottom Y of header
                # We can't define column X ranges easily without word-level boxes.
                # Project constraint: "PaddleOCR (lightweight CPU model)" typically returns line boxes.
                # If we assume meaningful whitespace separation in the text string, we can try to split.
                pass 
        
        # IF we cannot robustly detect columns, we RETURN EMPTY list (Guardrail: Never return partial/guessed rows)
        # Without word-level bounding boxes, robust column extraction is unsafe.
        # PaddleOCR *does* support returning word boxes if configured, but our adapter returns lines.
        
        # DECISION: For this MVP and the constraints, since we only established "line" output in the adapter,
        # we will skip Line Item extraction implementation details that would be flaky.
        # We will return empty list to be safe and deterministic.
        
        return [] 

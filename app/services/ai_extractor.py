import json
import logging
import google.generativeai as genai
from typing import Dict, Any
from app.core.config import settings
from app.core.exceptions import AIExtractionError

logger = logging.getLogger(__name__)

class AIExtractor:
    """
    Service to interact with Gemini API for extracting structured invoice data.
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in configuration")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use a model that supports JSON mode if available, or just standard efficient model
        self.model = genai.GenerativeModel('gemini-2.0-flash') 
        
        self.extraction_prompt = """
        You are a financial document parser.
        Extract invoice data from the text below.
        
        STRICTLY return ONLY valid JSON matching this schema:
        {
          "vendor_name": string | null,
          "invoice_number": string | null,
          "invoice_date": string | null (YYYY-MM-DD format preferred),
          "currency": string | null,
          "subtotal": number | null,
          "tax": number | null,
          "total": number | null,
          "line_items": [
            {
              "description": string,
              "quantity": number | null,
              "unit_price": number | null,
              "amount": number | null
            }
          ]
        }
        
        Rules:
        1. return ONLY valid JSON. No Markdown formatting (no ```json ... ```).
        2. If a value is missing or unclear, use null.
        3. Do not guess or hallucinate values.
        4. "amount" in line_items should be unit_price * quantity if explicit value is missing.
        5. "confidence_score" is NOT required in your output, it will be calculated externally.

        INVOICE TEXT:
        """

    def _strip_markdown(self, text: str) -> str:
        """Removes markdown code block formatting if present."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Sends text to Gemini to extract invoice data.
        
        Args:
            text: The pre-processed OCR text.
            
        Returns:
            dict: The extracted data matching the schema.
            
        Raises:
            AIExtractionError: If extraction fails or JSON is invalid.
        """
        if not text:
            raise AIExtractionError("Input text is empty")

        prompt = f"{self.extraction_prompt}\n{text}"
        
        retries = 1
        for attempt in range(retries + 1):
            try:
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    raise AIExtractionError("Gemini returned empty response")

                clean_json_text = self._strip_markdown(response.text)
                
                data = json.loads(clean_json_text)
                return data

            except json.JSONDecodeError as e:
                logger.warning(f"JSON Decode Error on attempt {attempt + 1}: {e}. Response: {response.text[:100]}...")
                if attempt == retries:
                    raise AIExtractionError("Failed to parse JSON from AI response after retries") from e
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                raise AIExtractionError("Gemini API request failed", e)
        
        raise AIExtractionError("Unknown error in extraction loop")

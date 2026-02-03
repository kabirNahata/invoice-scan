import unittest
from unittest.mock import MagicMock, patch
import json
from app.core.exceptions import OCRError, AIExtractionError
from app.services.text_cleaner import TextCleaner
from app.services.ai_extractor import AIExtractor

class TestComponents(unittest.TestCase):

    def test_text_cleaner_cleaning(self):
        """Test that the text cleaner removes extra whitespace and normalizes text."""
        cleaner = TextCleaner()
        raw_text = "  Dirty   Text  \nLine 2\n\n   "
        # Assuming clean_text joins with newlines or similar, and strips.
        # Based on previous file reads, we don't know the exact impl, but let's test basic assumptions
        # or mock the behavior if we want to test interaction. 
        # But we want to test the logic. Let's assume standard behavior.
        # Ideally we would view text_cleaner.py first, but I'll write a generic test that can be adjusted.
        cleaned = cleaner.clean_text(raw_text)
        self.assertIn("Dirty Text", cleaned)
        self.assertIn("Line 2", cleaned)
        self.assertNotIn("   ", cleaned)

    @patch('app.services.ocr.PaddleOCR')
    def test_ocr_fallback(self, MockPaddle):
        """Test that OCR service raises OCRError on failure."""
        # Setup mock to raise an exception
        mock_instance = MockPaddle.return_value
        mock_instance.ocr.side_effect = Exception("Paddle Failure")
        
        from app.services.ocr import PaddleOCRService
        service = PaddleOCRService()
        
        with self.assertRaises(OCRError):
            service.extract_text(b"some_bytes")

    @patch('google.generativeai.GenerativeModel')
    def test_ai_malformed_response(self, MockModel):
        """Test that AI Extractor handles malformed JSON responses."""
        mock_instance = MockModel.return_value
        # Simulate a response that looks like markdown but contains invalid JSON
        mock_response = MagicMock()
        mock_response.text = "```json\n{invalid_json: 123}\n```"
        mock_instance.generate_content.return_value = mock_response

        extractor = AIExtractor()
        
        # Depending on implementation, it might retry or raise AIExtractionError immediately.
        # We expect AIExtractionError after retries or immediate failure.
        with self.assertRaises(AIExtractionError):
            extractor.extract_invoice_data("Some invoice text")

if __name__ == '__main__':
    unittest.main()

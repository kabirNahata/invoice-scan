import sys
import os
# Add project root to path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import json

# MOCK PaddleOCR modules BEFORE importing app.main
# This prevents the ImportError from scipy/paddlex in this environment
sys.modules["paddleocr"] = MagicMock()
sys.modules["paddlepaddle"] = MagicMock()
sys.modules["pdf2image"] = MagicMock()

from app.main import app, ocr_engine


client = TestClient(app)

# Mock Data representing a clear invoice
MOCK_OCR_RESULT = [
    # Header
    {"text": "ACME CORP", "box": [[10, 10], [100, 10], [100, 30], [10, 30]], "confidence": 0.99, "page": 1},
    {"text": "123 Business Rd", "box": [[10, 40], [100, 40], [100, 50], [10, 50]], "confidence": 0.98, "page": 1},
    
    # Invoice Details
    {"text": "INVOICE", "box": [[200, 10], [280, 10], [280, 30], [200, 30]], "confidence": 0.99, "page": 1},
    {"text": "Invoice No: INV-2023-001", "box": [[200, 40], [350, 40], [350, 60], [200, 60]], "confidence": 0.95, "page": 1},
    {"text": "Date: 2023-10-25", "box": [[200, 70], [350, 70], [350, 90], [200, 90]], "confidence": 0.95, "page": 1},
    
    # Line Items (Mocking layout roughly)
    {"text": "Description", "box": [[10, 200], [100, 200], [100, 220], [10, 220]], "confidence": 0.9, "page": 1},
    {"text": "Qty", "box": [[150, 200], [100, 200], [100, 220], [10, 220]], "confidence": 0.9, "page": 1}, # Box coords approx
    {"text": "Amount", "box": [[300, 200], [350, 200], [350, 220], [300, 220]], "confidence": 0.9, "page": 1},
    
    {"text": "Widget A", "box": [[10, 230], [100, 230], [100, 250], [10, 250]], "confidence": 0.9, "page": 1},
    {"text": "100.00", "box": [[300, 230], [350, 230], [350, 250], [300, 250]], "confidence": 0.9, "page": 1},
    
    # Totals
    {"text": "Subtotal: $100.00", "box": [[250, 400], [350, 400], [350, 420], [250, 420]], "confidence": 0.9, "page": 1},
    {"text": "Tax (10%): $10.00", "box": [[250, 430], [350, 430], [350, 450], [250, 450]], "confidence": 0.9, "page": 1},
    {"text": "Total: $110.00", "box": [[250, 460], [350, 460], [350, 480], [250, 480]], "confidence": 0.9, "page": 1},
]

def test_scan_endpoint():
    # Patch OCR engine
    ocr_engine.process_file = MagicMock(return_value=MOCK_OCR_RESULT)
    
    # Create dummy file
    dummy_file = {"file": ("test_invoice.pdf", b"dummy pdf content", "application/pdf")}
    
    response = client.post("/scan", files=dummy_file)
    
    if response.status_code != 200:
        print(f"FAILED: {response.json()}")
        return

    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
    
    # Assertions
    assert data["vendor_name"] is not None, "Vendor name should be found (Strategy 2)" # "ACME CORP" likely found
    assert data["invoice_number"] == "INV-2023-001"
    assert data["invoice_date"] == "2023-10-25"
    assert data["currency"] == "USD"
    assert data["subtotal"] == 100.0
    assert data["tax"] == 10.0
    assert data["total"] == 110.0
    assert data["validation_status"] == "VALID"
    print("SUCCESS: All assertions passed.")

if __name__ == "__main__":
    test_scan_endpoint()

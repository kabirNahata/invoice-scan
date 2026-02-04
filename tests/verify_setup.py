import sys
import os
import json
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.getcwd())

# CONFIG: Set Poppler Path for Windows
POPPLER_BIN = r"C:\Program Files\Release-25.12.0-0\poppler-25.12.0\Library\bin"
os.environ["PATH"] += os.pathsep + POPPLER_BIN

# Import app normally - NO MOCKS
# This will trigger the real PaddleOCR initialization
try:
    from app.main import app
except ImportError as e:
    print(f"CRITICAL: Failed to import app/dependencies: {e}")
    sys.exit(1)

client = TestClient(app)

def test_real_scan():
    file_path = "invoice.jpg"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print("Initializing Real OCR Engine... (this may take a moment)")
    
    # We don't need to mock anything. The app.main import already initialized ocr_engine.
    
    try:
        with open(file_path, "rb") as f:
            response = client.post("/scan", files={"file": ("invoice.jpg", f, "image/jpeg")})
            
        if response.status_code == 200:
            print("\nSUCCESS: Real OCR Scan Completed!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nFAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\nCRITICAL ERROR during scan: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_scan()

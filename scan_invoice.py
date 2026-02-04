import sys
import os
import requests
import json
import time

SERVER_URL = "http://localhost:8000/scan"

def scan_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    print(f"Scanning: {file_path}...")
    print(f"Target: {SERVER_URL}")

    try:
        with open(file_path, 'rb') as f:
            # Determine mime type roughly
            mime_type = "application/pdf" if file_path.lower().endswith(".pdf") else "image/jpeg"
            files = {'file': (os.path.basename(file_path), f, mime_type)}
            
            start_time = time.time()
            response = requests.post(SERVER_URL, files=files)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"\n✅ Success! ({duration:.2f}s)")
                print("-" * 50)
                print(json.dumps(response.json(), indent=2))
                print("-" * 50)
            else:
                print(f"\n❌ Error {response.status_code}:")
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server.")
        print("Make sure the server is running! (Double-click run_server.bat)")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan_invoice.py <path_to_invoice>")
        print("Or drop a file onto scan.bat")
    else:
        target_file = sys.argv[1]
        scan_file(target_file)

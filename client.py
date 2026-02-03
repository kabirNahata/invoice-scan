import requests
import argparse
import sys
import os
import json

API_URL = "http://localhost:8005"

def scan_invoice(file_path):
    print(f"Scanning: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        mime_type = 'application/pdf' if file_path.lower().endswith('.pdf') else 'image/jpeg'
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, mime_type)}
            response = requests.post(f"{API_URL}/scan", files=files)
            
        if response.status_code == 200:
            print("\n--- Extraction Success ---")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n--- Extraction Failed ({response.status_code}) ---")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running on port 8005?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Scan Invoice Client")
    parser.add_argument("file_path", help="Path to the invoice file (PDF/Image)")
    args = parser.parse_args()
    
    scan_invoice(args.file_path)

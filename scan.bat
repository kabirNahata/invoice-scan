@echo off
if "%~1"=="" (
    echo Drag and drop an invoice file onto this script to scan it.
    echo Or run: scan.bat filename.pdf
    pause
    exit /b
)

echo Using Python environment...
.venv\Scripts\python.exe scan_invoice.py "%~1"
pause

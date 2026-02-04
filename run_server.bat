@echo off
echo Starting Smart Scan Server...
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
pause

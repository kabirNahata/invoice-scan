@echo off
echo Starting Smart Scan Server...
.venv\Scripts\uvicorn app.main:app --reload
pause

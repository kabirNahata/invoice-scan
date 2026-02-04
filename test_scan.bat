@echo off
echo Running verification test...
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
.venv\Scripts\python tests/verify_setup.py
pause

@echo off
REM Start server script
cd /d "%~dp0"
echo Current directory: %cd%
python -m uvicorn app:app --host 0.0.0.0 --port 7860 --reload

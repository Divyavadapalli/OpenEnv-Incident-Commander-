 @echo off
REM Quick start script for IncidentCommander (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         IncidentCommander OpenEnv Environment             ║
echo ║                Quick Start Script (Windows)               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Python %python_version% found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed
echo.

REM Run validation
echo 🧪 Running validation checks...
python validate.py
echo.

REM Start server
echo 🚀 Starting IncidentCommander server...
echo    Server will be available at: http://localhost:7860
echo    Health check: curl http://localhost:7860/health
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 0.0.0.0 --port 7860 --reload

pause

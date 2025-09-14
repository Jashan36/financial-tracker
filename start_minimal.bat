@echo off
echo Starting Financial Tracker (Minimal Version)...
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "streamlit_app_minimal.py" (
    echo Error: streamlit_app_minimal.py not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

REM Install minimal dependencies
echo Installing minimal dependencies...
pip install streamlit pandas

REM Start the minimal application
echo Starting minimal Streamlit server...
echo The app will open in your default web browser
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ================================================

streamlit run streamlit_app_minimal.py --server.port 8501

pause


@echo off
echo Starting Financial Tracker (Streamlit Version)...
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
if not exist "streamlit_app.py" (
    echo Error: streamlit_app.py not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

REM Install/upgrade requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Start the application
echo Starting Streamlit server...
echo The app will open in your default web browser
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ================================================

python run_streamlit.py

pause

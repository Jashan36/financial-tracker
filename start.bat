@echo off
echo Starting Financial Tracker Application...
echo.
echo Please ensure you have Python installed and dependencies are installed.
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the application...
python app.py
echo.
echo Application started! Open your browser and go to: http://localhost:5000
echo.
pause 
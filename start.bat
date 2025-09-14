@echo off
echo Starting Financial Tracker Application (Streamlit)...
echo.
echo Please ensure you have Python installed and dependencies are installed.
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the application...
streamlit run streamlit_app.py
echo.
echo Application started! Open your browser and go to: http://localhost:8501
echo.
pause 
@echo off
chcp 65001 >nul
echo ============================================
echo   RLI Systems - Local Server
echo ============================================
echo.

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Checking dependencies...
pip install -q -r requirements.txt

echo.
echo ============================================
echo   Starting server...
echo ============================================
echo.
echo Server starting on http://localhost:8088
echo For network access use: http://192.168.1.110:8088
echo.
echo Press Ctrl+C to stop
echo.

python main.py

pause


@echo off
title Starting MockMate AI...
echo ===================================================
echo   Starting MockMate AI Server...
echo ===================================================

cd /d "%~dp0"

IF NOT EXIST "venv" (
    echo Creating Python environment...
    python -m venv venv
)

echo Activating environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt --quiet

echo Launching browser...
start http://127.0.0.1:8000

echo Launching server...
python run_app.py

pause

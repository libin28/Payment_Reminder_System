@echo off
echo 💰 Payment Reminder System
echo ========================
echo.
echo Starting the Payment Reminder System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Run the startup script
python start_app.py

echo.
echo Press any key to exit...
pause >nul

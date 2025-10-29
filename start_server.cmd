@echo off
REM Autonomous Diligence Cloud - Startup Script for Windows
REM This script sets up and starts the server

echo ============================================
echo   Autonomous Diligence Cloud
echo   AI-Powered Document Intelligence
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
pip install -r backend\requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "backend\uploads" mkdir backend\uploads
if not exist "data\vector_db" mkdir data\vector_db

REM Check for .env file
if not exist ".env" (
    echo.
    echo ================================================
    echo   WARNING: .env file not found!
    echo ================================================
    echo.
    echo Please follow these steps:
    echo 1. Rename 'env_template.txt' to '.env'
    echo 2. Open .env and add your OPENAI_API_KEY
    echo 3. Run this script again
    echo.
    echo Get your API key from: https://platform.openai.com/api-keys
    echo.
    pause
    exit /b 1
)

REM Start the server
echo.
echo ============================================
echo   Starting server...
echo   Access at: http://localhost:8002
echo   API Docs: http://localhost:8002/docs
echo ============================================
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Server exited with an error
    pause
)


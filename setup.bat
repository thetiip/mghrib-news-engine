@echo off
REM Maghrib News Aggregator - Quick Start Script for Windows

echo ===================================
echo Maghrib News Aggregator Setup
echo ===================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.10 or higher.
    exit /b 1
)

python --version
echo OK Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo X Failed to create virtual environment
    exit /b 1
)

echo OK Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo X Failed to install dependencies
    exit /b 1
)

echo OK Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo OK .env file created
) else (
    echo i .env file already exists
)
echo.

REM Create necessary directories
if not exist data mkdir data
if not exist logs mkdir logs

echo ===================================
echo OK Setup Complete!
echo ===================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Run the scraper:
echo    python main.py
echo.
echo 3. Start the API server:
echo    python api.py
echo.
echo 4. Access the API documentation:
echo    http://localhost:8000/docs
echo.
echo Happy scraping! (Moroccan flag)
pause

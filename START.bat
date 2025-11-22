@echo off
REM Production Ready AI Flashcard Generator Launcher
REM This script starts the complete system

echo.
echo ====================================================================
echo   AI FLASHCARD GENERATOR - PRODUCTION LAUNCHER
echo ====================================================================
echo.

cd /d "%~dp0"

echo [Step 1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11 or higher.
    pause
    exit /b 1
)
echo DONE: Python found

echo.
echo [Step 2/3] Verifying all dependencies...
python -c "import streamlit, transformers, torch, datasets, PyPDF2; print('SUCCESS: All packages installed')" >nul 2>&1
if errorlevel 1 (
    echo INFO: Installing/updating packages...
    pip install -q streamlit transformers torch numpy pandas datasets PyPDF2 tqdm sentencepiece sacremoses
)
echo DONE: Dependencies ready

echo.
echo [Step 3/3] Starting AI Flashcard Generator on localhost:8501...
echo.
echo ====================================================================
echo   WEB UI: http://localhost:8501
echo ====================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

timeout /t 2 >nul

python -m streamlit run app.py --server.port=8501 --logger.level=warning --client.showErrorDetails=false

pause

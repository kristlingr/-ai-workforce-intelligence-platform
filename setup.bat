@echo off
REM ============================================
REM  AI Workforce Intelligence Platform — Setup
REM ============================================
echo.
echo === AI Workforce Intelligence Platform ===
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+.
    pause
    exit /b 1
)
echo [OK] Python found.

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

REM Generate datasets
echo.
echo Generating sample datasets...
python -m data_layer.run_pipeline
if %errorlevel% neq 0 (
    echo [WARNING] Data pipeline had issues — check output above.
) else (
    echo [OK] Datasets generated.
)

REM Launch app
echo.
echo Starting Streamlit app...
echo.
streamlit run app.py

pause

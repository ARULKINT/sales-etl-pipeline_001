@echo off
REM ==============================================================================
REM Sales ETL Pipeline Runner (Batch)
REM ==============================================================================
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else (
    set "PYTHON_CMD=python"
)

echo [INFO] Running Sales ETL Pipeline via %PYTHON_CMD%...
%PYTHON_CMD% src/main.py --generate-report

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pipeline execution finished successfully!
) else (
    echo [ERROR] Pipeline failed with error code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

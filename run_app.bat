@echo off
title Laser Cut Metal Stencil OCR Scanner
echo ============================================================
echo Starting Laser Cut Metal Stencil OCR Streamlit App...
echo ============================================================

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
) else if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
)

if "%PYTHON_EXE%"=="" (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
    ) else (
        where python >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_EXE=python"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python executable not found. Please verify Python installation.
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
"%PYTHON_EXE%" -m streamlit run app.py
pause

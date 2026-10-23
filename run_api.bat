@echo off
title Laser Cut Metal Stencil OCR - REST API Server
echo ============================================================
echo Starting Laser Cut Metal Stencil OCR API Server...
echo ============================================================

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
) else if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
)

if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_EXE=py"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python executable not found. Please install Python or add it to PATH.
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo API Server running at: http://localhost:5000
echo Endpoints:
echo   - Health Check: GET  http://localhost:5000/api/health
echo   - OCR Upload:   POST http://localhost:5000/api/ocr
echo   - Catalog:      GET  http://localhost:5000/api/catalog
echo ============================================================
"%PYTHON_EXE%" api/index.py
pause

@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MiniQuiz - Backend Only
color 0A

echo.
echo =========================================
echo       MiniQuiz - Backend Server
echo =========================================
echo.

REM ===== SETUP =====
set "PROJECT_ROOT=%~dp0"
REM Remove trailing backslash if present
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "API_DIR=%PROJECT_ROOT%\api"
set "WORKING_DIR=%PROJECT_ROOT%"

echo [CONFIG] PROJECT_ROOT: %PROJECT_ROOT%
echo [CONFIG] API_DIR: %API_DIR%
echo [CONFIG] WORKING_DIR: %WORKING_DIR%
echo.

REM ===== CHECK PYTHON =====
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo [ERROR] Install Python 3.8+ from python.org
    pause
    exit /b 1
)

python --version
echo.

REM ===== CHECK REQUIREMENTS =====
if exist "%API_DIR%\requirements.txt" (
    echo [INFO] Installing Python dependencies from requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r "%API_DIR%\requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        echo [ERROR] Check network connection and pip version
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo.
) else (
    echo [WARN] requirements.txt not found at "%API_DIR%"
    echo [WARN] Skipping pip install
    echo.
)

REM ===== ENSURE UVICORN =====
python -m pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo [INFO] uvicorn not found, installing...
    python -m pip install uvicorn
    if errorlevel 1 (
        echo [ERROR] Failed to install uvicorn
        pause
        exit /b 1
    )
    echo [OK] uvicorn installed
    echo.
) else (
    echo [INFO] uvicorn is already installed
)

REM ===== START BACKEND =====
echo [INFO] Starting FastAPI backend...
echo [INFO] Entry point: backend.app:app
echo [INFO] Host: 127.0.0.1, Port: 8000
echo [INFO] Working directory: %WORKING_DIR%
echo [INFO] Press Ctrl+C to stop
echo.

cd /d "%WORKING_DIR%"
if errorlevel 1 (
    echo [ERROR] Failed to change to directory: %WORKING_DIR%
    pause
    exit /b 1
)

echo [INFO] Current directory: %CD%
echo.

REM Launch uvicorn directly (this window becomes the server)
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000

REM If we get here, uvicorn exited
echo.
echo [ERROR] Backend stopped unexpectedly (exit code: %ERRORLEVEL%)
pause
endlocal

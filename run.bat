@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MiniQuiz - Running Full Project
color 0A

echo.
echo ========================================
echo       MiniQuiz - Starting Project
echo ========================================
echo.

REM ===== SETUP =====
set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "BACKEND_SCRIPT=%PROJECT_ROOT%\run_backend.bat"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"
set "FRONTEND_OK=0"

echo [CONFIG] PROJECT_ROOT: %PROJECT_ROOT%
echo [CONFIG] BACKEND_SCRIPT: %BACKEND_SCRIPT%
echo [CONFIG] FRONTEND_DIR: %FRONTEND_DIR%
echo [CONFIG] BACKEND_PORT: %BACKEND_PORT%
echo [CONFIG] FRONTEND_PORT: %FRONTEND_PORT%
echo.

REM ===== CHECK PYTHON =====
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo [ERROR] Install Python 3.8+ from python.org
    goto :fail
)
python --version
echo.

REM ===== CHECK NODE.JS + NPM =====
echo [INFO] Checking Node.js and npm...
echo.

set "NODE_PATH="
set "NPM_PATH="

for /f "delims=" %%P in ('where node 2^>nul') do (
    if not defined NODE_PATH set "NODE_PATH=%%P"
)

if not defined NODE_PATH (
    echo [WARN] Node.js ^(node^) not found in PATH
    echo [WARN] Frontend will not start, but backend will run
    echo [WARN] Install Node.js from nodejs.org and restart terminal
    echo.
    goto :skip_frontend
)

for /f "delims=" %%P in ('where npm 2^>nul') do (
    if not defined NPM_PATH set "NPM_PATH=%%P"
)

if not defined NPM_PATH (
    echo [WARN] npm not found in PATH
    echo [WARN] Frontend will not start, but backend will run
    echo [WARN] Reinstall Node.js and enable "Add to PATH"
    echo.
    goto :skip_frontend
)

echo [INFO] node path: !NODE_PATH!
echo [INFO] npm path: !NPM_PATH!

node --version
if errorlevel 1 (
    echo [ERROR] node command failed
    goto :skip_frontend
)

call npm --version
if errorlevel 1 (
    echo [ERROR] npm command failed
    goto :skip_frontend
)

echo.

REM ===== START BACKEND =====
echo [1/3] Starting Backend ^(FastAPI^)...
if exist "%BACKEND_SCRIPT%" (
    echo [INFO] Launching backend server...
    start "MiniQuiz Backend" cmd /k ""%BACKEND_SCRIPT%""
) else (
    echo [ERROR] Backend script not found: "%BACKEND_SCRIPT%"
    goto :fail
)

echo [INFO] Waiting for backend on port %BACKEND_PORT%...

set "MAX_WAIT=30"
set "WAITED=0"

:wait_loop_backend
if !WAITED! geq %MAX_WAIT% (
    echo [WARN] Backend timeout after %MAX_WAIT%s
    echo [WARN] Continuing anyway...
    goto :backend_ready
)

powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', %BACKEND_PORT%); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Backend running on port %BACKEND_PORT%
    goto :backend_ready
)

timeout /t 1 /nobreak >nul
set /a WAITED+=1
goto :wait_loop_backend

:skip_frontend
echo [INFO] Skipping frontend ^(Node.js/npm unavailable or failed^)
echo.
goto :browser_anyway

:backend_ready
echo.

REM ===== START FRONTEND =====
echo [2/3] Starting Frontend ^(Vite^)...
echo [INFO] Frontend directory: "%FRONTEND_DIR%"
echo [INFO] Checking frontend...

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found: "%FRONTEND_DIR%"
    echo [ERROR] Skipping frontend, backend is running
    goto :browser_anyway
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo [ERROR] package.json not found in "%FRONTEND_DIR%"
    echo [ERROR] Skipping frontend, backend is running
    goto :browser_anyway
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not available - cannot start frontend
    goto :browser_anyway
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not available - cannot start frontend
    goto :browser_anyway
)

echo [INFO] Changing to: "%FRONTEND_DIR%"
cd /d "%FRONTEND_DIR%"
if errorlevel 1 (
    echo [ERROR] Failed to change to directory: "%FRONTEND_DIR%"
    goto :browser_anyway
)

echo [INFO] Current directory: %CD%
echo.

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed ^(exit code: !ERRORLEVEL!^)
        echo [ERROR] Frontend will not start
        goto :browser_anyway
    )
    echo [OK] Dependencies installed
) else (
    echo [INFO] Dependencies already installed
)

echo [INFO] Starting Vite dev server...
echo [INFO] Command: npm run dev
echo.

start "MiniQuiz Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && call npm run dev"

echo [INFO] Waiting for frontend to start...
timeout /t 12 /nobreak >nul

powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', %FRONTEND_PORT%); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Frontend not responding on port %FRONTEND_PORT%
    echo [WARN] Check the frontend terminal for errors
) else (
    echo [OK] Frontend running on port %FRONTEND_PORT%
    set "FRONTEND_OK=1"
)

:browser_anyway
echo.

REM ===== OPEN BROWSER =====
echo [3/3] Opening browser...
echo [INFO] Opening: http://localhost:%FRONTEND_PORT%/auth
start "" "http://localhost:%FRONTEND_PORT%/auth"

echo.
echo ========================================
echo       Services status
echo ========================================
echo.
echo  Backend:  http://localhost:%BACKEND_PORT%
echo  Frontend: http://localhost:%FRONTEND_PORT%
echo  Auth:     http://localhost:%FRONTEND_PORT%/auth
echo.
if "%FRONTEND_OK%"=="0" (
    echo  [WARN] Frontend may not be running
    echo  [WARN] Check frontend terminal for error messages
)
echo ========================================
echo.
echo  Press any key to exit...
pause >nul
endlocal
exit /b 0

:fail
echo.
echo [FAIL] Startup aborted.
pause
endlocal
exit /b 1\



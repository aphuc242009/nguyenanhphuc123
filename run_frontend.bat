@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MiniQuiz - Frontend Only
color 0A

REM ===== SETUP =====
set "PROJECT_ROOT=%~dp0"
REM Remove trailing backslash for clean path joining
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

echo.
echo ========================================
echo       MiniQuiz - Frontend Server
echo ========================================
echo.

echo [CONFIG] PROJECT_ROOT: %PROJECT_ROOT%
echo [CONFIG] FRONTEND_DIR: %FRONTEND_DIR%
echo.

REM ===== CHECK DIRECTORY =====
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found: "%FRONTEND_DIR%"
    pause
    exit /b 1
)

REM ===== CHECK PACKAGE.JSON =====
if exist "%FRONTEND_DIR%\package.json" (
    echo [INFO] Found package.json
) else (
    echo [ERROR] package.json not found in "%FRONTEND_DIR%"
    pause
    exit /b 1
)

REM ===== CHECK NODE.JS =====
echo [INFO] Checking Node.js installation...
echo.

set "NODE_PATH="
set "NPM_PATH="

REM Find node.exe
for %%I in (node) do (
    where %%I >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('where %%I 2^>nul') do (
            set "NODE_PATH=%%P"
            goto :found_node
        )
    )
)

:found_node
if not defined NODE_PATH (
    echo [ERROR] Node.js (node) not found in PATH
    echo.
    echo [ROOT-CAUSE] Node.js is not installed or not in system PATH
    echo.
    echo [FIX] Step 1: Install Node.js LTS from https://nodejs.org
    echo [FIX] Step 2: During installation, check "Add to PATH" option
    echo [FIX] Step 3: Close and reopen Cursor / terminal
    echo [FIX] Step 4: Run this script again
    echo.
    echo [VERIFY] After installing, run: node --version
    pause
    exit /b 1
)

echo [INFO] Node.js found: %NODE_PATH%

REM Find npm.cmd / npm.exe
for %%I in (npm) do (
    where %%I >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('where %%I 2^>nul') do (
            set "NPM_PATH=%%P"
            goto :found_npm
        )
    )
)

:found_npm
if not defined NPM_PATH (
    echo [ERROR] npm not found in PATH
    echo.
    echo [ROOT-CAUSE] npm is not available even though node exists
    echo.
    echo [FIX] Step 1: Reinstall Node.js (npm comes with Node.js)
    echo [FIX] Step 2: Ensure "npm" is selected during installation
    echo [FIX] Step 3: Check PATH contains Node.js directory
    echo [FIX] Step 4: Restart Cursor / terminal
    echo.
    echo [DEBUG] Common Node.js PATH locations:
    echo   - C:\Program Files\nodejs\
    echo   - C:\Program Files (x86)\nodejs\
    echo   - %%USERPROFILE%%\AppData\Roaming\npm\
    pause
    exit /b 1
)

echo [INFO] npm found: %NPM_PATH%
echo.

REM Verify versions
node --version
if errorlevel 1 (
    echo [ERROR] node command failed
    pause
    exit /b 1
)

npm --version
if errorlevel 1 (
    echo [ERROR] npm command failed
    pause
    exit /b 1
)
echo.

REM ===== INSTALL DEPENDENCIES =====
echo [INFO] Changing to frontend directory: "%FRONTEND_DIR%"
cd /d "%FRONTEND_DIR%"
if errorlevel 1 (
    echo [ERROR] Failed to change to directory: "%FRONTEND_DIR%"
    pause
    exit /b 1
)

echo [INFO] Current directory: %CD%
echo.

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Installing dependencies (this may take a minute)...
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed with exit code: %ERRORLEVEL%
        echo [ERROR] Check the error messages above for details
        echo [ERROR] Common issues: network problems, package.json syntax error
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo.
) else (
    echo [INFO] Dependencies already installed (node_modules exists)
    echo.
)

REM ===== START FRONTEND =====
echo [INFO] Starting Vite dev server...
echo [INFO] Command: npm run dev
echo [INFO] Press Ctrl+C to stop
echo.

call npm run dev

echo.
echo [ERROR] Frontend server stopped (exit code: %ERRORLEVEL%)
pause
endlocal

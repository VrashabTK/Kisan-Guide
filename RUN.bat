@echo off
setlocal EnableDelayedExpansion

title KISSAN GUIDE - One-Click Launcher

echo ===================================================================
echo     KISSAN GUIDE (ಕಿಸಾನ್ ಗೈಡ್) - FULL-STACK LAUNCHER
echo     Agricultural Assistance Platform for Dakshina Kannada
echo ===================================================================
echo.

:: 1. Detect project root directory
cd /d "%~dp0"
set "ROOT_DIR=%~dp0"
echo [1/6] Project Root: %ROOT_DIR%

:: 2. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [2/6] Detected %PY_VER%

:: 3. Check Node.js and npm installation
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm is not found in PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node -v 2^>^&1') do set "NODE_VER=%%v"
echo [3/6] Detected Node.js %NODE_VER%

:: Check for occupied ports (8000 and 5173)
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>nul
if %errorlevel% equ 0 (
    echo [WARNING] Port 8000 is currently occupied by another process.
    echo If another instance of KISSAN GUIDE Backend is running, please close it first.
    echo.
)

netstat -ano | findstr /R /C:":5173 .*LISTENING" >nul 2>nul
if %errorlevel% equ 0 (
    echo [WARNING] Port 5173 is currently occupied by another process.
    echo If another instance of KISSAN GUIDE Frontend is running, please close it first.
    echo.
)

:: 4. Setup Python Virtual Environment
if not exist "venv\Scripts\python.exe" (
    echo [4/6] Creating Python virtual environment in .\venv ...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo       Virtual environment created successfully.
) else (
    echo [4/6] Virtual environment found at .\venv
)

:: 5. Install Backend Dependencies if needed
if not exist "venv\.deps_installed" (
    echo [5/6] Installing backend dependencies from backend\requirements.txt ...
    call "venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>nul
    call "venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>nul
    call "venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
    echo installed > "venv\.deps_installed"
    echo       Backend dependencies installed successfully.
) else (
    echo [5/6] Backend dependencies verified.
)

:: 6. Install Frontend Dependencies if node_modules is missing
if not exist "frontend\node_modules" (
    echo [6/6] Installing frontend packages in .\frontend ...
    pushd frontend
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend packages via npm.
        popd
        pause
        exit /b 1
    )
    popd
    echo       Frontend dependencies installed successfully.
) else (
    echo [6/6] Frontend dependencies verified.
)

echo.
echo ===================================================================
echo   STARTING SERVICES WITH AUTOMATIC RELOAD (HMR)
echo ===================================================================
echo.

:: Launch FastAPI Backend with uvicorn --reload in its own persistent terminal
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "KISSAN GUIDE - Backend Server (Port 8000)" cmd /k "title KISSAN GUIDE - Backend & cd /d "%ROOT_DIR%" & call venv\Scripts\activate.bat & python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Launch React Vite Frontend with HMR in its own persistent terminal
echo Starting Vite Frontend on http://localhost:5173 ...
start "KISSAN GUIDE - Frontend Server (Port 5173)" cmd /k "title KISSAN GUIDE - Frontend & cd /d "%ROOT_DIR%frontend" & npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo Waiting for servers to initialize...
:: Poll until frontend port 5173 is responding (up to 30 seconds)
powershell -NoProfile -Command "$ready = $false; for ($i = 0; $i -lt 30; $i++) { Start-Sleep -Seconds 1; try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 1; if ($res.StatusCode -eq 200) { $ready = $true; break } } catch {} }; if (-not $ready) { Write-Host 'Server taking longer than expected to start.' }"

:: Open the default browser to the web application
echo Opening application in default browser...
start http://localhost:5173

echo.
echo ===================================================================
echo   KISSAN GUIDE IS NOW RUNNING!
echo ===================================================================
echo.
echo   - Frontend Web App:     http://localhost:5173
echo   - Backend API:          http://127.0.0.1:8000
echo   - Interactive API Docs: http://127.0.0.1:8000/docs
echo   - API Health Check:     http://127.0.0.1:8000/api/health
echo.
echo   * Changes to Python files will auto-reload the backend.
echo   * Changes to React/TS/CSS files will live-update via Vite HMR.
echo   * Keep the two server terminal windows open while working.
echo.
echo Press any key to exit this launcher window (servers remain running).
pause >nul

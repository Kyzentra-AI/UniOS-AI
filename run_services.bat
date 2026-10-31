@echo off
setlocal enabledelayedexpansion

:: Kyzentra AI - All Services Launcher (Windows Batch)
:: Usage:
::   run_services.bat          (launches all 4 services in separate terminals)
::   run_services.bat frontend (runs frontend only)
::   run_services.bat backend  (runs backend only)
::   run_services.bat kie      (runs Kie service only)
::   run_services.bat kie-2    (runs Kie-2 service only)

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

if "%~1"=="frontend" goto :run_frontend
if "%~1"=="backend"  goto :run_backend
if "%~1"=="kie"      goto :run_kie
if "%~1"=="kie-2"    goto :run_kie2

:: ====================================================================
:: Master Launcher: Spawns 4 separate terminal windows
:: ====================================================================
echo ======================================================================
echo                Kyzentra AI - Starting All Services
echo ======================================================================
echo.
echo [1/4] Spawning Frontend   (Next.js)      -^> http://localhost:3000
start "Kyzentra - Frontend (Port 3000)" cmd /k call "%~f0" frontend

echo [2/4] Spawning Backend    (FastAPI)      -^> http://localhost:8000
start "Kyzentra - Backend (Port 8000)" cmd /k call "%~f0" backend

echo [3/4] Spawning Kie        (FastAPI)      -^> http://localhost:8001
start "Kyzentra - Kie (Port 8001)" cmd /k call "%~f0" kie

echo [4/4] Spawning Kie-2      (FastAPI)      -^> http://localhost:8002
start "Kyzentra - Kie-2 (Port 8002)" cmd /k call "%~f0" kie-2

echo.
echo ======================================================================
echo All 4 service terminals have been launched!
echo You can safely minimize or close this launcher window.
echo ======================================================================
ping -n 3 127.0.0.1 >nul
exit /b 0


:: ====================================================================
:: 1. Frontend Service
:: ====================================================================
:run_frontend
title Kyzentra - Frontend (Port 3000)
cd /d "%ROOT_DIR%\frontend"
echo ======================================================================
echo  Frontend Service (Next.js - Port 3000)
echo ======================================================================

if not exist "node_modules\" (
    echo [Frontend] 'node_modules' not found. Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [Frontend] Error: npm install failed!
        pause
        exit /b 1
    )
)

echo [Frontend] Running 'npm run build'...
call npm run build
if errorlevel 1 (
    echo [Frontend] Error: Build failed! Check the error log above.
    pause
    exit /b 1
)

echo [Frontend] Starting production server on http://localhost:3000...
call npm run start
pause
exit /b 0


:: ====================================================================
:: 2. Backend Service
:: ====================================================================
:run_backend
title Kyzentra - Backend (Port 8000)
cd /d "%ROOT_DIR%\backend"
echo ======================================================================
echo  Backend Service (FastAPI - Port 8000)
echo ======================================================================

set "VENV_NAME="
if exist "venv\Scripts\activate.bat" (
    set "VENV_NAME=venv"
) else if exist ".venv\Scripts\activate.bat" (
    set "VENV_NAME=.venv"
) else (
    echo [Backend] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [Backend] Error: Failed to create virtual environment 'venv'.
        pause
        exit /b 1
    )
    set "VENV_NAME=venv"
    if exist "requirements.txt" (
        echo [Backend] Installing requirements.txt...
        call venv\Scripts\activate.bat
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [Backend] Error: Failed to install requirements.txt.
            pause
            exit /b 1
        )
    )
)

echo [Backend] Activating virtual environment '!VENV_NAME!'...
call !VENV_NAME!\Scripts\activate.bat
echo [Backend] Starting uvicorn on http://localhost:8000...
uvicorn app.main:app --reload --port=8000
pause
exit /b 0


:: ====================================================================
:: 3. Kie Service
:: ====================================================================
:run_kie
title Kyzentra - Kie (Port 8001)
cd /d "%ROOT_DIR%\Kie"
echo ======================================================================
echo  Kie Service (FastAPI - Port 8001)
echo ======================================================================

set "VENV_NAME="
if exist ".venv\Scripts\activate.bat" (
    set "VENV_NAME=.venv"
) else if exist "venv\Scripts\activate.bat" (
    set "VENV_NAME=venv"
) else (
    echo [Kie] Virtual environment not found. Creating '.venv'...
    python -m venv .venv
    if errorlevel 1 (
        echo [Kie] Error: Failed to create virtual environment '.venv'.
        pause
        exit /b 1
    )
    set "VENV_NAME=.venv"
    if exist "requirements.txt" (
        echo [Kie] Installing requirements.txt...
        call .venv\Scripts\activate.bat
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [Kie] Error: Failed to install requirements.txt.
            pause
            exit /b 1
        )
    )
)

echo [Kie] Activating virtual environment '!VENV_NAME!'...
call !VENV_NAME!\Scripts\activate.bat
echo [Kie] Starting uvicorn on http://localhost:8001...
uvicorn app.main:app --reload --port=8001
pause
exit /b 0


:: ====================================================================
:: 4. Kie-2 Service
:: ====================================================================
:run_kie2
title Kyzentra - Kie-2 (Port 8002)
cd /d "%ROOT_DIR%\kie-2"
echo ======================================================================
echo  Kie-2 Service (FastAPI - Port 8002)
echo ======================================================================

set "VENV_NAME="
if exist ".venv\Scripts\activate.bat" (
    set "VENV_NAME=.venv"
) else if exist "venv\Scripts\activate.bat" (
    set "VENV_NAME=venv"
) else (
    echo [kie-2] Virtual environment not found. Creating '.venv'...
    python -m venv .venv
    if errorlevel 1 (
        echo [kie-2] Error: Failed to create virtual environment '.venv'.
        pause
        exit /b 1
    )
    set "VENV_NAME=.venv"
    if exist "requirements.txt" (
        echo [kie-2] Installing requirements.txt...
        call .venv\Scripts\activate.bat
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [kie-2] Error: Failed to install requirements.txt.
            pause
            exit /b 1
        )
    )
)

echo [kie-2] Activating virtual environment '!VENV_NAME!'...
call !VENV_NAME!\Scripts\activate.bat
echo [kie-2] Starting uvicorn on http://localhost:8002...
uvicorn app.main:app --reload --port=8002
pause
exit /b 0

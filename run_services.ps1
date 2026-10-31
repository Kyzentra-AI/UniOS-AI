<#
.SYNOPSIS
    Kyzentra AI - All Services Launcher (PowerShell)

.DESCRIPTION
    Launches Frontend, Backend, Kie, and Kie-2 services in separate terminal windows.
    Automatically checks and installs node_modules and builds frontend.
    Automatically creates Python virtual environments (.venv/venv) and installs requirements.txt if missing.

.EXAMPLE
    .\run_services.ps1
    .\run_services.ps1 -Service frontend
    .\run_services.ps1 -Service backend
    .\run_services.ps1 -Service kie
    .\run_services.ps1 -Service kie-2
#>

[CmdletBinding()]
param(
    [ValidateSet("all", "frontend", "backend", "kie", "kie-2")]
    [string]$Service = "all"
)

$RootDir = $PSScriptRoot

function Start-PythonService {
    param(
        [string]$ServiceName,
        [string]$SubDir,
        [int]$Port,
        [string]$PreferredVenvName = ".venv"
    )

    $ServicePath = Join-Path $RootDir $SubDir
    Set-Location $ServicePath
    $host.UI.RawUI.WindowTitle = "Kyzentra - $ServiceName (Port $Port)"

    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host " $ServiceName (FastAPI - Port $Port)" -ForegroundColor Cyan
    Write-Host " Path: $ServicePath" -ForegroundColor DarkGray
    Write-Host "==============================================================" -ForegroundColor Cyan

    # Check for existing venv (.venv or venv)
    $venvDir = $null
    $activateScript = $null

    if (Test-Path (Join-Path $ServicePath "$PreferredVenvName\Scripts\Activate.ps1")) {
        $venvDir = $PreferredVenvName
    } elseif ($PreferredVenvName -eq ".venv" -and (Test-Path (Join-Path $ServicePath "venv\Scripts\Activate.ps1"))) {
        $venvDir = "venv"
    } elseif ($PreferredVenvName -eq "venv" -and (Test-Path (Join-Path $ServicePath ".venv\Scripts\Activate.ps1"))) {
        $venvDir = ".venv"
    } else {
        Write-Host "[$ServiceName] No virtual environment found. Creating '$PreferredVenvName'..." -ForegroundColor Yellow
        python -m venv $PreferredVenvName
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[$ServiceName] Error: Failed to create virtual environment '$PreferredVenvName'." -ForegroundColor Red
            return
        }
        $venvDir = $PreferredVenvName

        $reqFile = Join-Path $ServicePath "requirements.txt"
        if (Test-Path $reqFile) {
            Write-Host "[$ServiceName] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
            $pipExe = Join-Path $ServicePath "$venvDir\Scripts\pip.exe"
            $pyExe = Join-Path $ServicePath "$venvDir\Scripts\python.exe"
            & $pyExe -m pip install --upgrade pip
            & $pipExe install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[$ServiceName] Error: Failed to install requirements." -ForegroundColor Red
                return
            }
        }
    }

    $activateScript = Join-Path $ServicePath "$venvDir\Scripts\Activate.ps1"
    Write-Host "[$ServiceName] Activating virtual environment '$venvDir'..." -ForegroundColor Green
    & $activateScript

    Write-Host "[$ServiceName] Starting uvicorn on http://localhost:$Port (Reload enabled)..." -ForegroundColor Green
    
    # Try running uvicorn directly; fallback to python -m uvicorn
    if (Get-Command uvicorn -ErrorAction SilentlyContinue) {
        uvicorn app.main:app --reload --port=$Port
    } else {
        python -m uvicorn app.main:app --reload --port=$Port
    }
}

switch ($Service.ToLower()) {
    "all" {
        Write-Host "==============================================================" -ForegroundColor Cyan
        Write-Host "                Kyzentra AI - Starting All Services           " -ForegroundColor Cyan
        Write-Host "==============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host " [1/4] Spawning Frontend   (Next.js)      -> http://localhost:3000" -ForegroundColor Green
        Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Service", "frontend"

        Write-Host " [2/4] Spawning Backend    (FastAPI)      -> http://localhost:8000" -ForegroundColor Green
        Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Service", "backend"

        Write-Host " [3/4] Spawning Kie        (FastAPI)      -> http://localhost:8001" -ForegroundColor Green
        Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Service", "kie"

        Write-Host " [4/4] Spawning Kie-2      (FastAPI)      -> http://localhost:8002" -ForegroundColor Green
        Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Service", "kie-2"

        Write-Host ""
        Write-Host "==============================================================" -ForegroundColor Cyan
        Write-Host "All 4 service terminals have been launched!" -ForegroundColor Green
        Write-Host "You can safely close this launcher window." -ForegroundColor DarkGray
        Write-Host "==============================================================" -ForegroundColor Cyan
    }

    "frontend" {
        $host.UI.RawUI.WindowTitle = "Kyzentra - Frontend (Port 3000)"
        $FrontendPath = Join-Path $RootDir "frontend"
        Set-Location $FrontendPath

        Write-Host "==============================================================" -ForegroundColor Cyan
        Write-Host " Frontend Service (Next.js - Port 3000)" -ForegroundColor Cyan
        Write-Host " Path: $FrontendPath" -ForegroundColor DarkGray
        Write-Host "==============================================================" -ForegroundColor Cyan

        if (-not (Test-Path (Join-Path $FrontendPath "node_modules"))) {
            Write-Host "[Frontend] 'node_modules' not found. Running 'npm install'..." -ForegroundColor Yellow
            npm install
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[Frontend] Error: 'npm install' failed." -ForegroundColor Red
                return
            }
        }

        Write-Host "[Frontend] Running 'npm run build'..." -ForegroundColor Green
        npm run build
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[Frontend] Error: Build failed! Check the error log above." -ForegroundColor Red
            return
        }

        Write-Host "[Frontend] Starting production server on http://localhost:3000..." -ForegroundColor Green
        npm run start
    }

    "backend" {
        Start-PythonService -ServiceName "Backend" -SubDir "backend" -Port 8000 -PreferredVenvName "venv"
    }

    "kie" {
        Start-PythonService -ServiceName "Kie" -SubDir "Kie" -Port 8001 -PreferredVenvName ".venv"
    }

    "kie-2" {
        Start-PythonService -ServiceName "Kie-2" -SubDir "kie-2" -Port 8002 -PreferredVenvName ".venv"
    }
}

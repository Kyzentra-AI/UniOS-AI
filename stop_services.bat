@echo off
setlocal enabledelayedexpansion

:: Kyzentra AI - Stop All Services (Windows Batch)
:: Cleans up active processes on ports 3000, 8000, 8001, and 8002

echo ======================================================================
echo  Kyzentra AI - Stopping Services on Ports 3000, 8000, 8001, 8002
echo ======================================================================

for %%P in (3000 8000 8001 8002) do (
    set "FOUND="
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr /r /c:":%%P *LISTENING"') do (
        set "PID=%%A"
        if defined PID (
            set "FOUND=1"
            echo Killing process with PID !PID! on port %%P...
            taskkill /f /pid !PID! >nul 2>&1
            if !errorlevel! equ 0 (
                echo Port %%P freed successfully.
            ) else (
                echo Could not terminate PID !PID!. May already be closed.
            )
        )
    )
    if not defined FOUND (
        echo Port %%P is clean.
    )
)

echo.
echo ======================================================================
echo Done.
echo ======================================================================
ping -n 3 127.0.0.1 >nul
exit /b 0

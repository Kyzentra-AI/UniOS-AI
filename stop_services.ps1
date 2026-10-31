<#
.SYNOPSIS
    Kyzentra AI - Stop All Services (PowerShell)

.DESCRIPTION
    Checks and stops any active processes listening on ports 3000, 8000, 8001, and 8002.
#>

param(
    [int[]]$Ports = @(3000, 8000, 8001, 8002)
)

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " Kyzentra AI - Stopping Services on Ports: $($Ports -join ', ')" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

foreach ($port in $Ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $pidsKilled = @()
        foreach ($conn in $conns) {
            $targetPid = $conn.OwningProcess
            if ($targetPid -and ($pidsKilled -notcontains $targetPid)) {
                $pidsKilled += $targetPid
                try {
                    $proc = Get-Process -Id $targetPid -ErrorAction Stop
                    Write-Host "Killing process '$($proc.ProcessName)' (PID $targetPid) on port $port..." -ForegroundColor Yellow
                    Stop-Process -Id $targetPid -Force
                    Write-Host "Port $port freed successfully." -ForegroundColor Green
                } catch {
                    Write-Host "Failed to stop PID $($targetPid) on port $($port): $_" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "Port $port is clean (no listening processes)." -ForegroundColor DarkGray
    }
}

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Done." -ForegroundColor Cyan

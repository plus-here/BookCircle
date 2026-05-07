$ErrorActionPreference = "Stop"

$Ports = @(8000, 8001, 5173, 5174)
$ProcessIds = @()

foreach ($Port in $Ports) {
    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        if ($connection.OwningProcess -and -not ($ProcessIds -contains $connection.OwningProcess)) {
            $ProcessIds += $connection.OwningProcess
        }
    }
}

if ($ProcessIds.Count -eq 0) {
    Write-Host "No BookCircle services are listening on ports: $($Ports -join ', ')"
    exit 0
}

foreach ($ProcessId in $ProcessIds) {
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        continue
    }

    Write-Host "Stopping PID $ProcessId ($($process.ProcessName))"
    Stop-Process -Id $ProcessId
}

Start-Sleep -Seconds 1

$stillListening = @()
foreach ($Port in $Ports) {
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
        $stillListening += $Port
    }
}

if ($stillListening.Count -gt 0) {
    Write-Host "Some ports are still listening: $($stillListening -join ', ')"
    exit 1
}

Write-Host "BookCircle services stopped."

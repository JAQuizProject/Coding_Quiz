[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$StateDir = Join-Path $RootDir ".demo"

foreach ($name in @("frontend", "backend")) {
    $pidPath = Join-Path $StateDir "$name.pid"
    if (-not (Test-Path $pidPath)) {
        continue
    }

    $processId = [int](Get-Content -Raw $pidPath)
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        & taskkill.exe /PID $processId /T /F | Out-Null
        Write-Host "Stopped $name process tree ($processId)."
    }
    Remove-Item -LiteralPath $pidPath -Force
}

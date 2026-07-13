[CmdletBinding()]
param(
    [switch]$SkipDataPreparation,
    [switch]$RestartBackend
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $RootDir "frontend"
$StateDir = Join-Path $RootDir ".demo"
$Python = Join-Path $RootDir ".venv\Scripts\python.exe"
$Node = "C:\Program Files\nodejs\node.exe"
$NextCli = Join-Path $FrontendDir "node_modules\next\dist\bin\next"

if (-not (Test-Path $Python)) {
    throw "Missing .venv. Run scripts\setup_live_demo.ps1 first."
}
if (-not (Test-Path $Node)) {
    throw "node.exe was not found at $Node."
}
if (-not (Test-Path $NextCli)) {
    throw "Next.js CLI was not found. Run scripts\setup_live_demo.ps1 first."
}

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

if (-not $SkipDataPreparation) {
    Set-Location $RootDir
    & $Python scripts\prepare_live_demo.py
}

function Test-DemoUrl {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

function Wait-DemoUrl {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ErrorLog
    )
    for ($attempt = 1; $attempt -le 60; $attempt += 1) {
        if (Test-DemoUrl $Url) {
            Write-Host "$Name is ready: $Url"
            return
        }
        Start-Sleep -Seconds 1
    }

    $details = if (Test-Path $ErrorLog) { Get-Content -Raw $ErrorLog } else { "No error log was created." }
    throw "$Name did not start within 60 seconds.`n$details"
}

function Stop-StateProcessTree {
    param([string]$Name)

    $pidPath = Join-Path $StateDir "$Name.pid"
    if (-not (Test-Path $pidPath)) {
        return
    }

    $processId = [int](Get-Content -Raw $pidPath)
    if ($null -ne (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
        & taskkill.exe /PID $processId /T /F | Out-Null
        Write-Host "Stopped $Name process tree ($processId)."
    }
    Remove-Item -LiteralPath $pidPath -Force
}

$BackendUrl = "http://127.0.0.1:8000/"
$BackendErrorLog = Join-Path $StateDir "backend.error.log"
if ($RestartBackend) {
    Stop-StateProcessTree -Name "backend"
}
if (-not (Test-DemoUrl $BackendUrl)) {
    $env:CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
    $backendOptions = @{
        FilePath               = $Python
        ArgumentList           = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000")
        WorkingDirectory       = $RootDir
        RedirectStandardOutput = Join-Path $StateDir "backend.log"
        RedirectStandardError  = $BackendErrorLog
        WindowStyle            = "Hidden"
        PassThru               = $true
    }
    $backend = Start-Process @backendOptions
    Set-Content -Path (Join-Path $StateDir "backend.pid") -Value $backend.Id
}
else {
    Write-Host "Backend is already running: $BackendUrl"
}

$FrontendUrl = "http://127.0.0.1:3000/login"
$FrontendErrorLog = Join-Path $StateDir "frontend.error.log"
if (-not (Test-DemoUrl $FrontendUrl)) {
    $frontendOptions = @{
        FilePath               = $Node
        ArgumentList           = @($NextCli, "dev", "--hostname", "127.0.0.1", "--port", "3000")
        WorkingDirectory       = $FrontendDir
        RedirectStandardOutput = Join-Path $StateDir "frontend.log"
        RedirectStandardError  = $FrontendErrorLog
        WindowStyle            = "Hidden"
        PassThru               = $true
    }
    $frontend = Start-Process @frontendOptions
    Set-Content -Path (Join-Path $StateDir "frontend.pid") -Value $frontend.Id
}
else {
    Write-Host "Frontend is already running: $FrontendUrl"
}

Wait-DemoUrl -Name "Backend" -Url $BackendUrl -ErrorLog $BackendErrorLog
Wait-DemoUrl -Name "Frontend" -Url $FrontendUrl -ErrorLog $FrontendErrorLog

Write-Host ""
Write-Host "Live demo is ready."
Write-Host "URL:      $FrontendUrl"
Write-Host "Login:    live-demo@example.com"
Write-Host "Password: Demo1234!"
Write-Host "Category: LiveDemo"
Write-Host "Practice: demo\AI_DEBUGGING_PRACTICE.md"
Write-Host "Prompts:  demo\LIVE_DEMO_PROMPTS.md"

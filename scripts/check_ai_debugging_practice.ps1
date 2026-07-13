[CmdletBinding()]
param(
    [ValidateSet("Buggy", "Fixed", "Either")]
    [string]$ExpectedState = "Buggy",
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RootDir ".venv\Scripts\python.exe"
$FrontendDir = Join-Path $RootDir "frontend"

Set-Location $RootDir

function Assert-UrlReady {
    param(
        [string]$Name,
        [string]$Url
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
    }
    catch {
        throw "$Name is not ready at $Url. Run scripts\start_live_demo.ps1 first."
    }

    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 400) {
        throw "$Name returned HTTP $($response.StatusCode) at $Url."
    }

    Write-Host "[PASS] ${Name}: HTTP $($response.StatusCode)"
}

if (-not (Test-Path $Python)) {
    throw "Missing .venv. Run scripts\setup_live_demo.ps1 first."
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    throw "Missing frontend dependencies. Run scripts\setup_live_demo.ps1 first."
}

Write-Host "Checking AI debugging practice environment..."

$mcpInfo = codex mcp get chrome-devtools 2>&1 | Out-String
if ($LASTEXITCODE -ne 0 -or $mcpInfo -notmatch "enabled:\s+true") {
    throw "The chrome-devtools MCP server is not enabled for this project."
}
Write-Host "[PASS] Chrome DevTools MCP: enabled"

Assert-UrlReady -Name "Backend" -Url "http://127.0.0.1:8000/openapi.json"
Assert-UrlReady -Name "Frontend" -Url "http://127.0.0.1:3000/login"

$stateScript = @'
import json
from app.modules.quiz.grading import is_answer_accepted

print(json.dumps([
    is_answer_accepted('10.00', '10'),
    is_answer_accepted('java3', 'python3'),
    is_answer_accepted('user 404', 'order 404'),
]))
'@
$stateJson = & $Python -c $stateScript
if ($LASTEXITCODE -ne 0) {
    throw "Unable to evaluate the backend grading state."
}

$stateLine = ($stateJson | Select-Object -Last 1).Trim()
$state = switch ($stateLine) {
    "[false, true, true]" { "Buggy" }
    "[true, false, false]" { "Fixed" }
    default { "Unknown" }
}

if ($state -eq "Unknown") {
    throw "Unknown grading state detected ($stateLine). Review the implementation before continuing."
}
if ($ExpectedState -ne "Either" -and $state -ne $ExpectedState) {
    throw "Expected grading state '$ExpectedState', but detected '$state' ($stateLine)."
}
Write-Host "[PASS] Grading state: $state $stateLine"

if ($state -eq "Fixed") {
    $backendPidPath = Join-Path $RootDir ".demo\backend.pid"
    $gradingPath = Join-Path $RootDir "app\modules\quiz\grading.py"
    if (Test-Path $backendPidPath) {
        $backendProcessId = [int](Get-Content -Raw $backendPidPath)
        $backendProcess = Get-Process -Id $backendProcessId -ErrorAction SilentlyContinue
        if ($null -ne $backendProcess) {
            $gradingUpdatedAt = (Get-Item $gradingPath).LastWriteTime
            if ($backendProcess.StartTime -lt $gradingUpdatedAt) {
                throw "Backend started before grading.py was updated. Restart it with scripts\start_live_demo.ps1 -RestartBackend -SkipDataPreparation."
            }
            Write-Host "[PASS] Backend process is newer than the grading change"
        }
    }
}

if ($RunTests) {
    Write-Host "Running backend baseline tests..."
    & $Python -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        throw "Backend tests failed."
    }

    Write-Host "Running frontend baseline tests..."
    Push-Location $FrontendDir
    try {
        npm test
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend tests failed."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Practice environment is ready."
Write-Host "Guide:    demo\AI_DEBUGGING_PRACTICE.md"
Write-Host "URL:      http://127.0.0.1:3000/login"
Write-Host "Login:    live-demo@example.com"
Write-Host "Password: Demo1234!"
Write-Host "Category: LiveDemo"

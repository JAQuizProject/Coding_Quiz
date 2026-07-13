[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$VenvDir = Join-Path $RootDir ".venv"
$Python = Join-Path $VenvDir "Scripts\python.exe"
$FrontendDir = Join-Path $RootDir "frontend"

Set-Location $RootDir

if (-not (Test-Path $Python)) {
    Write-Host "[1/6] Creating Python virtual environment..."
    python -m venv $VenvDir
}
else {
    Write-Host "[1/6] Python virtual environment already exists."
}

Write-Host "[2/6] Installing backend dependencies..."
$env:POETRY_VIRTUALENVS_IN_PROJECT = "true"
poetry install --with dev
if ($LASTEXITCODE -ne 0) {
    throw "poetry install failed."
}

Write-Host "[3/6] Installing frontend dependencies from package-lock.json..."
Push-Location $FrontendDir
try {
    npm ci
    if ($LASTEXITCODE -ne 0) {
        throw "npm ci failed."
    }
}
finally {
    Pop-Location
}

Write-Host "[4/6] Preparing local demo account and quiz data..."
& $Python scripts\prepare_live_demo.py
if ($LASTEXITCODE -ne 0) {
    throw "Demo data preparation failed."
}

Write-Host "[5/6] Verifying the Chrome DevTools MCP configuration..."
$McpInfo = codex mcp get chrome-devtools 2>&1 | Out-String
if ($LASTEXITCODE -ne 0 -or $McpInfo -notmatch "enabled") {
    throw "Codex did not load .codex/config.toml. Trust this project and restart Codex."
}
Write-Host $McpInfo.Trim()

Write-Host "[6/6] Running baseline checks..."
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    throw "Backend tests failed."
}
& $Python -m ruff check app tests scripts\prepare_live_demo.py
if ($LASTEXITCODE -ne 0) {
    throw "Backend lint failed."
}
Push-Location $FrontendDir
try {
    npm test
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend tests failed."
    }
    npm run lint
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend lint failed."
    }
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed."
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete. Start the demo with:"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1"

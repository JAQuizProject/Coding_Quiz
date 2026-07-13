[CmdletBinding()]
param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$PatchPath = Join-Path $RootDir "demo\grading-fix.patch"

Set-Location $RootDir
git apply --check $PatchPath
if ($LASTEXITCODE -ne 0) {
    throw "The fallback patch does not apply cleanly. Inspect the current diff before continuing."
}

if ($CheckOnly) {
    Write-Host "Fallback patch applies cleanly."
    exit 0
}

git apply $PatchPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to apply the fallback patch."
}

Write-Host "Fallback grading fix applied. Run the verification commands from demo\LIVE_DEMO_PROMPTS.md."

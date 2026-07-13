[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot

Set-Location $RootDir

$configOverrides = @(
    "mcp_servers.context7.enabled=false",
    "mcp_servers.figma.enabled=false",
    "mcp_servers.openaiDeveloperDocs.enabled=false",
    "mcp_servers.postman_oauth_full.enabled=false"
)

$arguments = @()
foreach ($override in $configOverrides) {
    $arguments += @("-c", $override)
}

Write-Host "Practice guide: demo\AI_DEBUGGING_PRACTICE.md"
Write-Host "Opening Codex with unrelated remote MCPs disabled for this session."
& codex @arguments

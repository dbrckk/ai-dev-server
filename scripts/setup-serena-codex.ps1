$ErrorActionPreference = "Stop"

if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    Write-Error @"
uv/uvx is required.

Windows PowerShell:
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Then open a new PowerShell window and run this script again.
"@
    exit 1
}

Write-Host "Configuring Serena MCP for Codex..."
& uvx --from git+https://github.com/oraios/serena serena setup codex
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$config = Join-Path $HOME ".codex\config.toml"
if ((Test-Path $config) -and (Select-String -Path $config -Pattern '^\[mcp_servers\.serena\]$' -Quiet)) {
    Write-Host "OK: Serena is registered in $config"
} else {
    Write-Error "Serena setup completed but $config does not contain [mcp_servers.serena]."
    exit 2
}

Write-Host @"

Serena/Codex setup complete.

For a configured repository:
  1. cd C:\path\to\repository
  2. codex
  3. verify Serena with /mcp

The repository AGENTS.md instructs Codex to prefer Serena symbol navigation.
If activation is not automatic, tell Codex:
  Activate the current dir as project using serena
"@

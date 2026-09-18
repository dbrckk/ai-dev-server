# Serena + Codex

The active repositories use Serena for symbol-oriented code navigation through `.serena/project.yml`.

## One-time Codex setup

### Linux, macOS or Termux

```bash
bash scripts/setup-serena-codex.sh
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-serena-codex.ps1
```

The scripts use Serena's official Codex setup command through `uvx` and verify that `~/.codex/config.toml` contains the Serena MCP registration.

## Per repository

Start Codex from the repository root:

```bash
codex
```

Then use `/mcp` to verify that Serena is connected. If project activation is not automatic, ask Codex:

```text
Activate the current dir as project using serena
```

Each configured repository also contains an `AGENTS.md` file telling Codex to prefer Serena's symbol/reference tools over whole-file scans.

## Optional pre-index

From a repository root:

```bash
uvx --from git+https://github.com/oraios/serena serena project index
```

This builds the local symbol cache ahead of the first substantial task. The cache is ignored by Git.

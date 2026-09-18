This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
existing-projects/
  jumpy.json
mobile-requests/
  example.json
  jumpy.json
ci.json
promoted_capabilities.json
provider-probe.json
release.json
request.json
```

# Files

## File: existing-projects/jumpy.json
```json
{
  "repository": "dbrckk/Jumpy",
  "baseline_commit": "b9a8df120dc5da807f68b610e7bfcd0422f8cff5",
  "engine": "godot",
  "engine_version": "4.7.2",
  "engine_sha256": "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4",
  "mode": "baseline_only"
}
```

## File: mobile-requests/example.json
```json
{
  "id": "focus-mobile-v1",
  "target_repo": "dbrckk/my-new-mobile-app",
  "app_name": "focus_mobile",
  "brief": "Créer une application Android de concentration en français avec minuteur fonctionnel, pause/reprise/reset, choix de durée, statistiques de la session et thème sombre. Direction artistique sobre et professionnelle, accent bleu, typographie très lisible et grandes cibles tactiles. Aucune publicité, aucun compte ni backend. Les statistiques concernent la session courante ; aucune persistance promise. Livrer les sources, les tests et un APK de démonstration.",
  "enabled": false,
  "max_rounds": 3,
  "max_calls": 12,
  "max_cycles": 5,
  "play_publish": {
    "enabled": false,
    "track": "internal",
    "commit": false
  }
}
```

## File: mobile-requests/jumpy.json
```json
{
  "id": "jumpy",
  "target_repo": "dbrckk/Jumpy",
  "app_name": "jumpy",
  "brief": "Finish the existing Jumpy Godot game to a production-ready Android release candidate. Preserve its one-touch jump, airborne correction, perfect-landing/FLOW core loop and existing progression systems. Autonomously inspect the repository, fix defects, complete missing product polish, UX, gameplay balance, accessibility, performance, tests, runtime journeys, visual QA, privacy/security, store-ready metadata/assets, and Android build readiness. Prefer safe incremental changes backed by real Godot and Android evidence. Do not depend on optional external SDKs or credentials; when release signing or store-side credentials are the only remaining blocker, report the exact human action required instead of claiming completion.",
  "enabled": true,
  "priority": 100,
  "play_publish": {
    "enabled": false,
    "commit": false,
    "track": "internal"
  }
}
```

## File: ci.json
```json
{"provider":"github"}
```

## File: promoted_capabilities.json
```json
{
  "version": 1,
  "capabilities": {
    "asset_artwork": {
      "provider": "studio.capabilities.asset_artwork",
      "candidate_id": "capability-candidate:asset_artwork:176e24c4325c3bb5",
      "baseline_sha": "0c9f44167f5b312b944027791e87fabfab44864b",
      "candidate_sha": "c6b1cfcb0551a59415b2277031ff318b0cfbdd54"
    }
  }
}
```

## File: provider-probe.json
```json
{"enabled":false,"revision":5}
```

## File: release.json
```json
{
  "schema": 1,
  "version": "1.3.0",
  "channel": "stable",
  "branch": "main",
  "required_gates": [
    "CI",
    "Validate AI Dev Server",
    "Fault Injection Gate",
    "Resilience Soak",
    "Mobile Studio Real Build",
    "Multi-Engine E2E Benchmark"
  ],
  "operational_commands": [
    "python studio/v1_gate.py",
    "python -m studio.project_status --project-out studio-output/<project-id>",
    "python studio/fleet_dashboard.py --root studio-output",
    "python studio/fleet_metrics.py --root studio-output",
    "python studio/fleet_regression.py --history studio-output/fleet-metrics.json",
    "python studio/fleet_supervisor.py --root studio-output",
    "python studio/fleet_supervisor_apply.py --root studio-output",
    "python studio/fleet_maintenance.py --root studio-output",
    "python studio/fleet_daemon.py --root studio-output --once"
  ],
  "safety": {
    "supervisor_default": "dry-run",
    "restart_budget_default": 2,
    "regression_blocks_restart": true,
    "quarantine_on_state_integrity_failure": true,
    "canary_schedule": "every 6 hours"
  }
}
```

## File: request.json
```json
{
  "operation": "agent_test",
  "requested_by": "chatgpt",
  "reason": "Direct FCC release-blocker audit of the current Jumpy HEAD",
  "request_id": 34
}
```

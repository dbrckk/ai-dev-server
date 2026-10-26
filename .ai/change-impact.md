# Change impact

Base: 8dabcd9aa80d2c50f8dbc37f8acf3a4739ab6a93
Head: 04c155252930b13669b4f9352bec8f48c85a40a3

## Changed files
- A docs/managed-generic-delivery.md
- M studio/autonomous_project.py
- M studio/generic_delivery.py
- M studio/generic_project.py
- M studio/generic_repository.py
- M studio/generic_smoke.py
- A studio/generic_target_ci.py
- M studio/production_os_worker.py
- M tests/test_generic_published_checkpoint.py
- M tests/test_generic_repository_pull_request.py
- M tests/test_generic_worker_canary_resume.py
- M tests/test_multi_engine_orchestrator.py
- M tests/test_production_os_worker_runtime.py

## Affected areas
- docs
- studio
- tests

## Related test candidates
- tests/test_autonomous_project.py
- tests/test_production_os_worker.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.

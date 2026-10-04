# Change impact

Base: 0f2db36742f5b7e733c4de463be66e378920ec12
Head: 6caaeebdc3bcae8ae9f31fe413ff75270201b19b

## Changed files
- M .github/workflows/production-os-actions-worker.yml
- A .github/workflows/production-os-live-diagnostics.yml
- M .github/workflows/production-os-worker-integration.yml
- A control/production-os-diagnostics-kick.json
- M docs/PRODUCTION_OS_WORKER.md
- M integration_tests/test_production_os_server_integration.py
- M studio/core.py
- A studio/production_os_live_diagnostics.py
- A studio/production_os_provider_config.py
- M studio/production_os_worker.py
- M tests/test_production_os_actions_worker_workflow.py
- A tests/test_production_os_live_diagnostics.py
- M tests/test_production_os_worker_recovery.py
- M tests/test_request_contract.py

## Affected areas
- .github
- control
- docs
- integration_tests
- studio
- tests

## Related test candidates
- tests/test_production_os_live_diagnostics.py
- tests/test_production_os_worker.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.

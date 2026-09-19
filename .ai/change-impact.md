# Change impact

Base: 6dd708d3e10a4710896e3c165bf9427b057830c2
Head: 0fdc770db3b1fcb24aecf31d8ef631180ed6082c

## Changed files
- A studio/agents/codex.py
- M studio/agents/orchestrator.py
- M studio/capacity_scheduler.py
- M studio/core.py
- M studio/generic_project.py
- M studio/github_runner.py
- A studio/omniroute_capacity.py
- A studio/production_os_worker.py
- M tests/test_agent_router.py
- A tests/test_capacity_scheduler_omniroute.py
- A tests/test_codex_adapter.py
- A tests/test_github_runner_usage.py
- A tests/test_omniroute_capacity.py
- A tests/test_production_os_result_contract.py
- A tests/test_production_os_worker.py
- A tests/test_production_os_worker_cli.py
- A tests/test_production_os_worker_runtime.py

## Affected areas
- studio
- tests

## Related test candidates
- tests/test_orchestrator.py
- tests/test_capacity_scheduler.py
- tests/test_omniroute_capacity.py
- tests/test_production_os_worker.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.

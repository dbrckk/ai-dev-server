# Change impact

Base: 3a60de96210e1bfb00e29c7425a7d984df0924f6
Head: 6ad645b95be26f2865dc541dcdc0d189b86cd31a

## Changed files
- M .github/workflows/mobile-studio.yml
- M .github/workflows/production-os-actions-worker.yml
- M .github/workflows/production-os-live-diagnostics.yml
- M control/production-os-diagnostics-kick.json
- M studio/production_os_provider_config.py
- M studio/provider_router.py
- M tests/test_production_os_live_diagnostics.py

## Affected areas
- .github
- control
- studio
- tests

## Related test candidates
- tests/test_provider_router.py

## Agent guidance
- Read this file before broad repository exploration.
- Inspect only the affected areas first.
- Use .ai/commands.json to choose validation commands.
- Expand scope only if the change crosses module boundaries or tests fail.

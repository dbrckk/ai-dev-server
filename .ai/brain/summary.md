# Repo Brain

- Index mode: incremental
- Files indexed: 619
- Files reparsed this run: 1
- Symbols: 4319
- Internal import edges: 1252
- Impacted files: 1
- Selected tests: 1

## Languages
- python: 616 files
- gdscript: 3 files

## Highest-density symbol files
- tests/test_release_candidate_search.py: 95 symbols
- tests/test_replacement_ci_policy.py: 62 symbols
- tests/test_studio.py: 60 symbols
- tests/test_architecture_reputation_policy_migration.py: 44 symbols
- tests/test_architecture_replacement_planner.py: 42 symbols
- tests/test_journeys.py: 41 symbols
- tests/test_production_os_worker_runtime.py: 41 symbols
- studio/core.py: 32 symbols
- tests/test_architecture_reputation_policy_approval.py: 32 symbols
- tests/test_orchestrator.py: 30 symbols
- studio/production_os_worker.py: 29 symbols
- tests/test_architecture_replacement_reputation.py: 26 symbols
- tests/test_capacity_scheduler.py: 26 symbols
- tests/test_ci.py: 26 symbols
- studio/replacement_ci_policy_v11.py: 24 symbols
- tests/test_architecture_feedback.py: 23 symbols
- tests/test_architecture_reputation_policy_github_collect.py: 23 symbols
- tests/test_asset_forge_bridge.py: 23 symbols
- studio/evolution_research.py: 22 symbols
- studio/architecture_reputation_policy_migration.py: 20 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 1
- outline files retained: 615
- top-level items retained: 6395
- direct members retained: 2117
- symbol shards: 26
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard


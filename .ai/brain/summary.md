# Repo Brain

- Index mode: incremental
- Files indexed: 658
- Files reparsed this run: 7
- Symbols: 4867
- Internal import edges: 1429
- Impacted files: 15
- Selected tests: 10

## Languages
- python: 655 files
- gdscript: 3 files

## Highest-density symbol files
- tests/test_release_candidate_search.py: 95 symbols
- tests/test_production_os_worker_runtime.py: 94 symbols
- tests/test_replacement_ci_policy.py: 62 symbols
- tests/test_studio.py: 60 symbols
- tests/test_production_os_actions_worker_workflow.py: 45 symbols
- studio/production_os_worker.py: 44 symbols
- tests/test_architecture_reputation_policy_migration.py: 44 symbols
- tests/test_architecture_replacement_planner.py: 42 symbols
- tests/test_journeys.py: 41 symbols
- tests/test_multi_engine_orchestrator.py: 38 symbols
- tests/test_production_os_worker_canary.py: 34 symbols
- studio/core.py: 32 symbols
- tests/test_architecture_reputation_policy_approval.py: 32 symbols
- tests/test_orchestrator.py: 30 symbols
- tests/test_architecture_replacement_reputation.py: 26 symbols
- tests/test_capacity_scheduler.py: 26 symbols
- tests/test_ci.py: 26 symbols
- tests/test_autonomous_project.py: 25 symbols
- studio/replacement_ci_policy_v11.py: 24 symbols
- tests/test_goal_loop.py: 24 symbols

## Agent routing
- Read impact.json first after project/change context.
- Use selected-tests.json before broad validation.
- Search lookup.json for symbol routing; ast-grep enrichment may provide exact ranges.
- Verify source before editing.

## ast-grep enrichment
- ast-grep outline: available
- AST index mode: incremental
- AST files reparsed this run: 7
- outline files retained: 654
- top-level items retained: 6972
- direct members retained: 2338
- symbol shards: 26
- route named symbols via ast-routing.json, then fetch one ast-symbols/<initial>.json shard


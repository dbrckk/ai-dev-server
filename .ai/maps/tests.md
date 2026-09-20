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
test_adaptation_research.py
test_adaptation.py
test_adaptive_phase_policy.py
test_adaptive_planning_runtime.py
test_adaptive_review_telemetry.py
test_adaptive_role_allocator.py
test_adaptive_scoring.py
test_agent_performance_store.py
test_agent_performance.py
test_agent_router.py
test_agent_workspace.py
test_android_ci_resilience.py
test_android_signing.py
test_api_transport_retry.py
test_architecture_benchmark.py
test_architecture_change_guard.py
test_architecture_contract.py
test_architecture_evaluator.py
test_architecture_feedback.py
test_architecture_learning.py
test_architecture_obsolescence.py
test_architecture_outcome.py
test_architecture_planner.py
test_architecture_preflight.py
test_architecture_replacement_candidate.py
test_architecture_replacement_executor.py
test_architecture_replacement_learning.py
test_architecture_replacement_merge_gate.py
test_architecture_replacement_merge.py
test_architecture_replacement_outcome.py
test_architecture_replacement_persist.py
test_architecture_replacement_pipeline.py
test_architecture_replacement_planner.py
test_architecture_replacement_postmerge_pipeline.py
test_architecture_replacement_postmerge.py
test_architecture_replacement_pr_package.py
test_architecture_replacement_pr_validator.py
test_architecture_replacement_promotion.py
test_architecture_replacement_reputation_state_machine.py
test_architecture_replacement_reputation.py
test_architecture_replacement_rollback_gate.py
test_architecture_replacement_rollback.py
test_architecture_replacement_work_order.py
test_architecture_reputation_policy_approval.py
test_architecture_reputation_policy_github_attestation.py
test_architecture_reputation_policy_github_collect.py
test_architecture_reputation_policy_migration_cli.py
test_architecture_reputation_policy_migration_review.py
test_architecture_reputation_policy_migration.py
test_architecture_safe_rewrite.py
test_artifact_cas_audit.py
test_artifact_cas_namespace.py
test_artifact_cas_promotion.py
test_artifact_cas_stats.py
test_artifact_cas.py
test_artifact_handoff.py
test_artwork_candidate_bridge.py
test_artwork_capability.py
test_artwork_stage.py
test_artwork_validation.py
test_asset_artwork_capability.py
test_asset_artwork_promotion.py
test_asset_forge_installer.py
test_atomic_file.py
test_autonomous_project.py
test_autonomous_research.py
test_billing_qa.py
test_candidate_portfolio_learning.py
test_capability_adaptation_state.py
test_capability_candidate_review_state.py
test_capability_candidate_validator.py
test_capability_memory.py
test_capability_promotion.py
test_capability_qa.py
test_capability_registry_promotion_persist.py
test_capability_registry_review.py
test_capability_registry.py
test_capability_review.py
test_capability_runtime.py
test_capability_synthesis.py
test_capacity_budget.py
test_capacity_efficiency.py
test_capacity_ledger.py
test_capacity_runtime.py
test_capacity_scheduler_omniroute.py
test_capacity_scheduler_work_conserving.py
test_capacity_scheduler.py
test_checkout_credentials_policy.py
test_ci_adaptation.py
test_ci_runner_admission.py
test_ci.py
test_codex_adapter.py
test_codex_output_retention.py
test_completion.py
test_concurrent_state.py
test_contextual_routing_memory.py
test_contextual_strategy_efficiency.py
test_contextual_utility.py
test_continuous_improvement.py
test_cost_drift.py
test_diagnostics.py
test_diff_quick_gates.py
test_durable_state.py
test_engine_entry.py
test_engine_patch.py
test_evolution_automerge_orchestration.py
test_evolution_automerge.py
test_evolution_benchmark.py
test_evolution_candidate.py
test_evolution_differential.py
test_evolution_evidence.py
test_evolution_executor.py
test_evolution_isolated_runner.py
test_evolution_pending.py
test_evolution_persist.py
test_evolution_promotion.py
test_evolution_research.py
test_evolution_rollback.py
test_evolution_stage_runner.py
test_evolution_synthesis.py
test_execution_budget.py
test_execution_checkpoint.py
test_existing_project.py
test_file_lock.py
test_fleet_capacity.py
test_fleet_daemon.py
test_fleet_maintenance.py
test_fleet_metrics.py
test_fleet_operations.py
test_fleet_supervisor_apply.py
test_free_capacity_recommendations.py
test_full_gate_cache.py
test_generic_adaptive_review_wiring.py
test_generic_architecture.py
test_generic_capability_candidate_persistence.py
test_generic_capability_isolated_validation.py
test_generic_capability_persist.py
test_generic_capability_synthesis_state.py
test_generic_capability_validation_report.py
test_generic_model_capacity.py
test_generic_policy.py
test_generic_toolchain.py
test_generic_verifier_adaptation.py
test_github_artifact_cas_audit_store.py
test_github_artifact_cas_stats_store.py
test_github_full_gate_cache_store.py
test_github_goal_store.py
test_github_memory_store.py
test_github_quick_gate_cache_store.py
test_github_runner_persistent.py
test_github_runner_usage.py
test_global_admission.py
test_goal_capability_runtime.py
test_goal_engine.py
test_goal_learning.py
test_goal_loop.py
test_godot_android_export.py
test_godot_android_stage.py
test_godot_baseline.py
test_godot_device_qa.py
test_godot_device_stage.py
test_godot_final_review_qa.py
test_godot_model.py
test_godot_play_stage.py
test_godot_preview.py
test_godot_privacy_security_qa.py
test_godot_release_artifact_stage.py
test_godot_release_artifact.py
test_godot_release_qa.py
test_godot_release_stage.py
test_godot_repository_probe.py
test_godot_runtime_journey_stage.py
test_godot_runtime_journeys.py
test_godot_runtime.py
test_godot_session.py
test_godot_store_metadata_qa.py
test_godot_visual_qa.py
test_godot_visual_stage.py
test_human_handoff_status_v3.py
test_human_input_request.py
test_idempotent_model.py
test_imagen_codex_installer.py
test_immutable_artifact_cache.py
test_improvement_backlog.py
test_improvement_dispatch.py
test_improvement_executor.py
test_improvement_verifier.py
test_journeys.py
test_jumpy_v13_migration.py
test_learning_context.py
test_lease_guard.py
test_lease_keepalive.py
test_local_api_security.py
test_local_capacity.py
test_local_model_leaderboard.py
test_local_model_reputation.py
test_local_model_specialization.py
test_memory_bridge.py
test_memory_lifecycle.py
test_meta_router.py
test_mobile_studio_provider_fallbacks.py
test_mobile_studio_runtime_triggers.py
test_model_portfolio_audit.py
test_model_portfolio_learning.py
test_model_portfolio.py
test_multi_engine_orchestrator.py
test_multi_project_canary.py
test_native_qa.py
test_notification_qa.py
test_omniroute_capacity.py
test_orchestrator_automerge.py
test_orchestrator.py
test_patch_safety_rebuild.py
test_performance_qa.py
test_persistent_improvement_runner.py
test_persistent_quick_gate_cache.py
test_phase_budget.py
test_phase_cost_baseline.py
test_platform_view_qa.py
test_play_publisher.py
test_play_stage.py
test_portfolio_candidate_scheduler.py
test_predictive_budget.py
test_preemption_apply.py
test_preemption_controller.py
test_privacy_stage.py
test_privacy.py
test_production_os_local_e2e.py
test_production_os_result_contract.py
test_production_os_worker_cli.py
test_production_os_worker_preflight.py
test_production_os_worker_runtime.py
test_production_os_worker.py
test_project_budget.py
test_project_context.py
test_project_engine_generic.py
test_project_engine.py
test_project_memory.py
test_promoted_capabilities.py
test_provider_cost.py
test_provider_health.py
test_provider_metrics.py
test_provider_monthly_quota.py
test_provider_router.py
test_provider_runtime_reliability.py
test_provider_scoped_health.py
test_provider_verified_feedback.py
test_queue_terminal_state.py
test_quick_gate_cache.py
test_readiness.py
test_recovery_controller.py
test_registry_promotion_review_state.py
test_release_candidate_search.py
test_release_contract.py
test_release_readiness.py
test_release_repair.py
test_release_stage_engine.py
test_release_v130.py
test_release.py
test_repair_planner.py
test_repair_queue.py
test_repair_search_policy.py
test_repair_strategy.py
test_replacement_ci_policy.py
test_repo_maintenance.py
test_repo_version_probe.py
test_repository_research_provider.py
test_request_budget.py
test_request_contract.py
test_request_priority.py
test_resilience_soak.py
test_routing_audit.py
test_routing_calibration.py
test_routing_history.py
test_run_cost_controller.py
test_runtime_health.py
test_runtime_journeys.py
test_runtime_soak.py
test_safe_rewrite_learning.py
test_security_agent.py
test_security_remediation.py
test_security_stage.py
test_security.py
test_stage_registry.py
test_stagnation_controller.py
test_star_recommendations.py
test_store.py
test_strategy_efficiency.py
test_strict_task_claim_store.py
test_studio.py
test_task_claim_store.py
test_task_context.py
test_task_lease.py
test_task_scheduler.py
test_telemetry_maintenance.py
test_telemetry.py
test_transport.py
test_unified_routing_score.py
test_v1_gate.py
test_verification_cost.py
test_worker_heartbeat.py
test_worker_reaper.py
test_worker_reliability.py
test_workflow_checkpoint.py
```

# Files

## File: test_adaptation_research.py
```python
class AdaptationResearchTests(unittest.TestCase)
⋮----
def search(self, query)
⋮----
def fetch(self, url)
⋮----
def test_complete_research_never_registers_capability(self)
⋮----
registry=new_registry()
⋮----
entries=query(memory,project_id="project-a",kind="research")
⋮----
def test_insufficient_research_stays_in_research(self)
⋮----
def test_research_cannot_override_existing_registry(self)
⋮----
before=registry["registry_sha256"]
```

## File: test_adaptation.py
```python
class AdaptationTests(unittest.TestCase)
⋮----
def test_missing_billing_stage_requests_research_and_safe_promotion(self)
⋮----
report = {
result = build_adaptation_request(report, frozenset({'real_device', 'capability_qa'}))
⋮----
kinds = {item['kind'] for item in result['resource_research']}
⋮----
def test_registered_capability_needs_no_adaptation(self)
⋮----
result = build_adaptation_request(report, frozenset({'notification_qa'}))
⋮----
def test_unfinished_without_next_stage_fails_closed(self)
⋮----
result = build_adaptation_request({'completion': {'finished': False, 'blockers': []}}, frozenset())
⋮----
def test_unclassified_android_permission_requests_adaptation(self)
⋮----
result = build_adaptation_request(report, frozenset({'store_metadata'}))
⋮----
def test_writes_machine_readable_evolution_request_only_when_needed(self)
⋮----
out = Path(tmp)
report = {'completion': {'finished': False, 'next_stage': 'platform_view_qa', 'blockers': []}}
result = write_adaptation_request(report, out, frozenset())
path = out / 'evolution-request.json'
⋮----
complete = {'completion': {'finished': True, 'next_stage': None, 'blockers': []}}
result = write_adaptation_request(complete, out, frozenset())
⋮----
def test_validated_cross_project_memory_is_attached_as_hint_only(self)
⋮----
memory = add_entry(
⋮----
report = {'completion': {'finished': False, 'next_stage': 'billing_qa', 'blockers': ['billing_qa_missing']}}
```

## File: test_adaptive_phase_policy.py
```python
class AdaptivePhasePolicyTests(unittest.TestCase)
⋮----
def test_low_risk_round_skips_model_review_after_trusted_verification(self)
⋮----
decision = review_phase_decision(
⋮----
def test_failed_verification_never_becomes_complete_when_review_is_skipped(self)
⋮----
def test_ambiguous_verification_fails_closed_when_review_is_skipped(self)
⋮----
def test_required_review_launches_model_when_budget_allows(self)
⋮----
def test_quota_exhaustion_fails_closed_even_when_review_is_required(self)
⋮----
def test_invalid_review_quota_fails_closed_when_review_is_required(self)
```

## File: test_adaptive_planning_runtime.py
```python
ROOT = Path(__file__).resolve().parents[1]
⋮----
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"
⋮----
class AdaptivePlanningRuntimeTests(unittest.TestCase)
⋮----
def test_planning_requirement_is_shared_with_role_allocator(self)
⋮----
allocator = importlib.import_module("adaptive_role_allocator")
⋮----
planning_required = allocator.planning_required
⋮----
def test_planning_budget_pressure_is_exposed_for_telemetry(self)
⋮----
budget_pressure = allocator.budget_pressure
⋮----
def test_planning_policy_reports_stable_reason(self)
⋮----
policy = importlib.import_module("adaptive_phase_policy")
planning_phase_decision = policy.planning_phase_decision
⋮----
skipped = planning_phase_decision(
⋮----
required = planning_phase_decision(
⋮----
invalid = planning_phase_decision(
⋮----
def test_planning_policy_skips_only_when_safe_and_has_deterministic_plan(self)
⋮----
def test_generic_runtime_wires_preplanning_decision_before_plan_model(self)
⋮----
source = GENERIC_PROJECT.read_text(encoding="utf-8")
tree = ast.parse(source)
⋮----
allocator_import = any(
policy_import = any(
⋮----
def test_round_state_persists_planning_decision_telemetry(self)
```

## File: test_adaptive_review_telemetry.py
```python
ROOT = Path(__file__).resolve().parents[1]
⋮----
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"
⋮----
class AdaptiveReviewTelemetryTests(unittest.TestCase)
⋮----
def test_review_policy_reports_stable_reason_for_each_decision(self)
⋮----
policy = importlib.import_module("adaptive_phase_policy")
review_phase_decision = policy.review_phase_decision
⋮----
required = review_phase_decision(
⋮----
quota_exhausted = review_phase_decision(
⋮----
skipped = review_phase_decision(
⋮----
failed_verification = review_phase_decision(
⋮----
def test_round_state_persists_review_decision_telemetry(self)
⋮----
source = GENERIC_PROJECT.read_text(encoding="utf-8")
```

## File: test_adaptive_role_allocator.py
```python
class AdaptiveRoleAllocatorTests(unittest.TestCase)
⋮----
def test_simple_confident_task_uses_one_model_without_extra_roles(self)
⋮----
result = choose_role_allocation(
⋮----
def test_difficult_uncertain_task_adds_independent_implementation(self)
⋮----
def test_extreme_task_can_use_three_models(self)
⋮----
def test_budget_pressure_prevents_wide_orchestration(self)
⋮----
def test_paid_or_scarce_capacity_does_not_expand_models(self)
```

## File: test_adaptive_scoring.py
```python
class AdaptiveScoringTests(unittest.TestCase)
⋮----
def test_provider_trace_sums_components(self)
⋮----
trace = score_provider(
⋮----
def test_agent_trace_is_explainable(self)
⋮----
trace = score_agent(
data = trace.as_dict()
```

## File: test_agent_performance_store.py
```python
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
⋮----
class T(unittest.TestCase)
⋮----
def test_valid(self): self.assertEqual(_validate({"opencode:implementation":{"runs":2,"successes":1,"duration_total":3.5}})["opencode:implementation"]["runs"],2)
def test_invalid_counts(self)
```

## File: test_agent_performance.py
```python
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
⋮----
class T(unittest.TestCase)
⋮----
def test_success_history_changes_bounded_bonus(self)
⋮----
p=Path(td)/"p.json"
⋮----
def test_repeated_failures_trigger_cooldown(self)
⋮----
data=__import__("json").loads(p.read_text())
```

## File: test_agent_router.py
```python
ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
⋮----
class AgentRouterTests(unittest.TestCase)
⋮----
def setUp(self)
⋮----
def test_free_preference_changes_ranking(self)
⋮----
ranked = rank_agents({"code_editing", "tests"}, registry=self.registry, prefer_free=True)
⋮----
def test_paid_can_win_when_free_preference_disabled(self)
⋮----
ranked = rank_agents({"code_editing", "tests"}, registry=self.registry, prefer_free=False)
⋮----
def test_unavailable_agent_is_not_selected(self)
⋮----
def which(name)
⋮----
decision = choose_agent({"research"}, registry=self.registry)
⋮----
def test_learned_agent_weights_affect_ranking_and_trace(self)
⋮----
ranked = rank_agents(
⋮----
def test_architecture_discipline_penalizes_repeatedly_risky_agent(self)
⋮----
summary = {
⋮----
risky = next(item for item in ranked if item.agent.name == "paid-code")
⋮----
def test_contextual_memory_changes_agent_score(self)
⋮----
contextual = {
⋮----
free_code = next(item for item in ranked if item.agent.name == "free-code")
paid_code = next(item for item in ranked if item.agent.name == "paid-code")
⋮----
def test_cost_aware_utility_prefers_faster_agent_when_context_quality_is_equal(self)
⋮----
def test_opencode_invocation_uses_secret_alias(self)
⋮----
env={
⋮----
def test_codex_invocation_uses_verified_headless_contract(self)
⋮----
def test_codex_execute_named_exposes_token_usage(self)
⋮----
run = AgentRun(
⋮----
result = execute_named("codex", "do work", cwd=ROOT)
⋮----
def test_codex_execute_named_prefers_isolated_omniroute_profile_when_healthy(self)
⋮----
seen = {}
⋮----
def fake_run(_adapter, argv, *, cwd, timeout, extra_env)
⋮----
def test_codex_execute_named_uses_chatgpt_profile_when_omniroute_is_unavailable(self)
⋮----
def test_codex_execute_named_stops_when_project_token_envelope_is_exhausted(self)
⋮----
root = Path(td)
plan = root / "capacity-plan.json"
ledger = root / "capacity-ledger.json"
⋮----
reservation = capacity_ledger.reserve(
⋮----
env = {
⋮----
def test_codex_execute_named_settles_reported_usage_in_project_ledger(self)
⋮----
run_result = AgentRun(
```

## File: test_agent_workspace.py
```python
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
⋮----
class AgentWorkspaceTests(unittest.TestCase)
⋮----
def test_valid_change_is_reported(self)
⋮----
root=Path(td); (root/"a.py").write_text("x=1\n")
before=snapshot(root); (root/"a.py").write_text("x=2\n")
⋮----
def test_deletion_is_rejected_and_restored(self)
⋮----
before=snapshot(root); (root/"a.py").unlink()
```

## File: test_android_ci_resilience.py
```python
ROOT = Path(__file__).resolve().parents[1]
⋮----
class AndroidCIResilienceTests(unittest.TestCase)
⋮----
def test_transient_android_archive_failures_are_recognized_conservatively(self)
⋮----
def test_android_bootstrap_retries_sdkmanager_then_succeeds(self)
⋮----
script = ROOT / "scripts" / "bootstrap-android-ci.sh"
⋮----
root = Path(td)
sdk = root / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
⋮----
counter = root / "install-attempts"
⋮----
env = dict(os.environ)
⋮----
result = subprocess.run(
⋮----
def test_android_bootstrap_fails_after_three_install_attempts(self)
⋮----
def test_all_android_workflows_use_shared_resilient_bootstrap(self)
⋮----
text = (ROOT / rel).read_text(encoding="utf-8")
```

## File: test_android_signing.py
```python
def make_aab(path: Path, *, signed=False)
⋮----
class AndroidSigningTests(unittest.TestCase)
⋮----
def test_signature_metadata_is_removed_from_copy(self)
⋮----
root = Path(td)
source = root / "source.aab"
clean = root / "clean.aab"
⋮----
evidence = strip_existing_signatures(source, clean)
⋮----
def test_credentials_reject_keystore_inside_project_workspace(self)
⋮----
key = root / "upload.jks"
⋮----
env = {
⋮----
def test_missing_credentials_are_explicit_but_not_exceptional(self)
⋮----
result = signing_credentials({})
⋮----
def test_signer_never_places_password_on_command_line(self)
⋮----
unsigned = root / "u.aab"
signed = root / "s.aab"
⋮----
calls = []
⋮----
def runner(cmd, **kwargs)
⋮----
result = sign_aab(
```

## File: test_api_transport_retry.py
```python
class APITransportRetryTests(unittest.TestCase)
⋮----
def test_call_retries_transient_url_error_then_succeeds(self)
⋮----
api = API('https://example.test', 'key')
responses = [urllib.error.URLError('temporary network failure'), {'ok': True}]
⋮----
def fake_response(_req, timeout_seconds=300)
⋮----
value = responses.pop(0)
⋮----
result = api.call('GET', '/resource', timeout_seconds=30)
```

## File: test_architecture_benchmark.py
```python
class ArchitectureBenchmarkTests(unittest.TestCase)
⋮----
def decision(self)
⋮----
def recommendations(self)
⋮----
def test_review_can_surface_migration_candidate(self)
⋮----
evaluation={"verdict":"review","blockers":["testing failed","browser failed"]}
result=benchmark(self.decision(),evaluation,self.recommendations())
row=result["comparisons"][0]
⋮----
def test_benchmark_carries_project_context(self)
⋮----
result=benchmark(self.decision(),{"verdict":"review","blockers":["x"]},self.recommendations())
⋮----
def test_clean_evidence_does_not_propose_migration(self)
⋮----
evaluation={"verdict":"retain","blockers":[]}
⋮----
def test_missing_alternative_metadata_is_explicit(self)
⋮----
alt=[x for x in result["comparisons"][0]["alternatives"] if x["repo"]=="a/unknown"][0]
⋮----
def test_write_persists_benchmark(self)
⋮----
out=Path(tmp)
result=write(self.decision(),{"verdict":"retain","blockers":[]},self.recommendations(),out)
saved=json.loads((out/"architecture-benchmark.json").read_text())
```

## File: test_architecture_change_guard.py
```python
class ArchitectureChangeGuardTests(unittest.TestCase)
⋮----
def test_source_only_patch_is_allowed_on_hold(self)
⋮----
result = guard.enforce(
⋮----
def test_flutter_dependency_manifest_is_blocked_on_hold(self)
⋮----
def test_generic_infrastructure_file_is_blocked_on_hold(self)
⋮----
def test_godot_project_file_is_blocked_on_hold(self)
⋮----
def test_architecture_patch_is_allowed_after_preflight_pass(self)
⋮----
def test_semantic_router_change_is_blocked_on_hold(self)
⋮----
root = Path(td)
target = root / "lib/router.dart"
⋮----
def test_semantic_import_churn_is_reported_when_allowed(self)
⋮----
target = root / "src/main.py"
⋮----
def test_small_source_edit_does_not_trigger_semantic_guard(self)
⋮----
target = root / "src/util.py"
```

## File: test_architecture_contract.py
```python
class ArchitectureContractTests(unittest.TestCase)
⋮----
def test_contract_is_valid(self)
⋮----
report = architecture_contract.validate()
```

## File: test_architecture_evaluator.py
```python
class ArchitectureEvaluatorTests(unittest.TestCase)
⋮----
def decision(self)
⋮----
def test_retain_when_validation_is_clean(self)
⋮----
result=evaluate(self.decision(),{"status":"validated_preview","blockers":[]})
⋮----
def test_review_when_blockers_exist(self)
⋮----
result=evaluate(self.decision(),{"status":"repair_needed","blockers":["browser testing failed"]})
⋮----
def test_failed_release_evidence_triggers_review(self)
⋮----
report={"status":"validated_preview","release_evidence":{"release_build":{"passed":False}}}
result=evaluate(self.decision(),report)
⋮----
def test_write_persists_sidecar(self)
⋮----
out=Path(tmp)
result=write(self.decision(),{"status":"validated_preview"},out)
saved=json.loads((out/"architecture-evaluation.json").read_text())
⋮----
def test_godot_preview_validation_is_retain(self)
⋮----
result=evaluate(self.decision(),{"status":"godot_preview_validated","blockers":[]})
```

## File: test_architecture_feedback.py
```python
class ArchitectureFeedbackTests(unittest.TestCase)
⋮----
def test_insufficient_history_does_not_bias(self)
⋮----
recs = {"matches": [{"repo": "a/core", "score": 90.0, "quality_score": 9.0}]}
learning = {"rankings": [{"repo": "a/core", "samples": 4, "success_rate": 1.0}]}
⋮----
result = af.apply(recs, learning)
⋮----
def test_success_history_applies_bounded_bonus(self)
⋮----
recs = {
learning = {
⋮----
by_repo = {row["repo"]: row for row in result["matches"]}
⋮----
def test_poor_history_can_only_apply_small_penalty(self)
⋮----
recs = {"matches": [{"repo": "a/core", "score": 90.0}]}
learning = {"rankings": [{"repo": "a/core", "samples": 10, "success_rate": 0.0}]}
⋮----
def test_unrelated_history_does_not_claim_feedback_applied(self)
⋮----
learning = {"rankings": [{"repo": "other/repo", "samples": 10, "success_rate": 1.0}]}
⋮----
def test_domain_mismatch_does_not_bias_current_recommendation(self)
⋮----
def test_matching_domain_can_apply_feedback(self)
⋮----
def test_stale_evidence_is_ignored(self)
⋮----
now = 10_000_000.0
recs = {"matches": [{"repo": "a/core", "domain": "mobile", "score": 90.0}]}
⋮----
result = af.apply(recs, learning, now=now)
⋮----
def test_fresh_evidence_is_allowed(self)
⋮----
def test_framework_mismatch_does_not_bias(self)
⋮----
result = af.apply(recs, learning, framework="godot")
⋮----
def test_matching_framework_can_bias(self)
⋮----
def test_stack_synergy_is_framework_scoped(self)
⋮----
mismatch = af.stack_adjustment("b/ui", ["a/core"], learning, framework="godot")
matching = af.stack_adjustment("b/ui", ["a/core"], learning, framework="flutter")
⋮----
def test_project_type_mismatch_does_not_bias(self)
⋮----
learning = {"rankings": [{
result = af.apply(
⋮----
def test_full_context_gets_full_bonus(self)
⋮----
def test_stack_synergy_is_project_type_scoped(self)
⋮----
learning = {"stack_rankings": [{
mismatch = af.stack_adjustment(
matching = af.stack_adjustment(
⋮----
def test_quality_score_changes_feedback_with_same_success_rate(self)
⋮----
recs = {"matches": [
learning = {"rankings": [
⋮----
by_repo = {x["repo"]: x for x in result["matches"]}
⋮----
def test_large_sample_can_outweigh_perfect_small_sample(self)
⋮----
def test_uncertainty_never_authorizes_dependencies(self)
⋮----
def test_repo_feedback_attenuates_low_confidence_evidence(self)
⋮----
common = {
⋮----
def test_stack_synergy_attenuates_low_confidence_evidence(self)
⋮----
base = {
low = af.stack_adjustment(
high = af.stack_adjustment(
⋮----
def test_degraded_drift_removes_positive_historical_bonus(self)
⋮----
recs = {"matches": [{
⋮----
row = result["matches"][0]
⋮----
def test_stable_drift_keeps_positive_history_bonus(self)
⋮----
def test_degraded_stack_history_becomes_negative_synergy(self)
⋮----
result = af.stack_adjustment(
```

## File: test_architecture_learning.py
```python
class ArchitectureLearningTests(unittest.TestCase)
⋮----
def _write(self, root, project, repos, successful, calls, cycles, blockers)
⋮----
out = root / project
⋮----
payload = {
⋮----
def test_requires_multiple_samples_before_advisory_bias(self)
⋮----
root = Path(td)
⋮----
result = al.summarize(root)
row = result["rankings"][0]
⋮----
def test_aggregates_success_and_cost_metrics(self)
⋮----
def test_better_evidence_ranks_higher(self)
⋮----
rankings = al.summarize(root)["rankings"]
⋮----
def test_write_persists_bounded_learning_summary(self)
⋮----
result = al.write(root)
saved = json.loads((root / "architecture-learning.json").read_text(encoding="utf-8"))
⋮----
def test_same_repo_is_separated_by_domain(self)
⋮----
mobile = root / "mobile"
⋮----
backend = root / "backend"
⋮----
by_domain = {row["domain"]: row for row in rankings}
⋮----
def test_stack_rankings_aggregate_joint_outcomes(self)
⋮----
def test_learning_root_does_not_escape_arbitrary_output_directory(self)
⋮----
def test_same_repo_and_domain_are_separated_by_framework(self)
⋮----
out = root / name
⋮----
keyed = {(row["framework"], row["domain"]): row for row in rankings}
⋮----
def test_stack_learning_is_separated_by_project_type_and_domain(self)
⋮----
out = root / f"p{i}"
⋮----
stacks = al.summarize(root)["stack_rankings"]
by_context = {(x["project_type"], x["primary_domain"]): x for x in stacks}
⋮----
def test_repo_learning_is_separated_by_project_type(self)
⋮----
by_type = {x["project_type"]: x for x in rankings}
⋮----
def test_continuous_quality_distinguishes_successful_stacks(self)
⋮----
out = root / f"good-{i}"
⋮----
out = root / f"weak-{i}"
⋮----
def test_uncertainty_metrics_favor_large_samples(self)
⋮----
rows = {x["repo"]: x for x in al.summarize(root)["rankings"]}
⋮----
def test_detects_recent_quality_degradation(self)
⋮----
qualities = [95, 94, 93, 92, 91, 60, 58, 55, 52, 50]
⋮----
row = al.summarize(root)["rankings"][0]
⋮----
def test_detects_recent_success_degradation(self)
⋮----
successes = [True] * 5 + [True, False, False, False, False]
⋮----
stack = al.summarize(root)["stack_rankings"][0]
⋮----
def test_drift_requires_recent_and_baseline_windows(self)
⋮----
observations = [
result = al._drift(observations)
⋮----
def test_stable_history_is_not_marked_degraded(self)
def test_degraded_history_is_exposed_as_drift_alert(self)
⋮----
qualities = [95, 95, 95, 95, 95, 50, 50, 50, 50, 50]
⋮----
alerts = [x for x in result["drift_alerts"] if x.get("type") == "repository"]
```

## File: test_architecture_obsolescence.py
```python
class ArchitectureObsolescenceTests(unittest.TestCase)
⋮----
def learning(self)
⋮----
def benchmark(self)
⋮----
def recommendations(self)
⋮----
def test_requires_drift_and_benchmark_evidence(self)
⋮----
result=evaluate(self.learning(),self.benchmark(),self.recommendations())
⋮----
row=result["deprecation_candidates"][0]
⋮----
def test_weak_drift_is_not_candidate(self)
⋮----
learning=self.learning()
⋮----
result=evaluate(learning,self.benchmark(),self.recommendations())
⋮----
def test_no_benchmark_migration_means_no_candidate(self)
⋮----
benchmark=self.benchmark()
⋮----
result=evaluate(self.learning(),benchmark,self.recommendations())
⋮----
def test_unknown_maintenance_is_explicit(self)
⋮----
def test_write_persists_sidecar(self)
⋮----
out=Path(td)
result=write(self.learning(),self.benchmark(),self.recommendations(),out)
saved=json.loads((out/"architecture-obsolescence.json").read_text())
⋮----
def test_stale_maintenance_strengthens_candidate(self)
⋮----
maintenance={"a/current":{
result=evaluate(
⋮----
def test_active_maintenance_does_not_auto_deprecate(self)
⋮----
maintenance={"a/current":{"repo":"a/current","status":"active","age_days":10.0}}
⋮----
def test_version_probe_context_is_propagated(self)
⋮----
versions={
```

## File: test_architecture_outcome.py
```python
class ArchitectureOutcomeTests(unittest.TestCase)
⋮----
def test_build_links_decision_to_verified_outcome(self)
⋮----
state = {
result = build(state)
⋮----
def test_finished_outcome_is_successful(self)
⋮----
result = build({
⋮----
def test_blocked_outcome_is_not_successful(self)
⋮----
def test_write_is_machine_readable(self)
⋮----
out = Path(td)
result = write(
saved = json.loads((out / "architecture-outcome.json").read_text(encoding="utf-8"))
⋮----
def test_verified_godot_preview_counts_as_success(self)
⋮----
def test_contextual_constraints_are_preserved(self)
def test_quality_score_rewards_cleaner_success(self)
⋮----
clean = build({
expensive = build({
```

## File: test_architecture_planner.py
```python
class ArchitecturePlannerTests(unittest.TestCase)
⋮----
def test_selects_ranked_candidates_without_authorizing_dependencies(self)
⋮----
recs={"matches":[
result=plan({"target_repo":"o/r","app_name":"demo"},recs)
⋮----
def test_write_persists_machine_readable_decision(self)
⋮----
out=Path(tmp)
result=write({"target_repo":"o/r","app_name":"demo"},{"matches":[]},out)
saved=json.loads((out/"architecture-decision.json").read_text())
⋮----
def test_learning_below_threshold_does_not_change_selection_score(self)
⋮----
learning={"rankings":[{"repo":"a/core","samples":4,"success_rate":1.0}]}
result=plan({"target_repo":"o/r","app_name":"demo"},recs,learning=learning)
⋮----
def test_verified_history_can_reorder_with_small_bounded_bonus(self)
⋮----
learning={"rankings":[
⋮----
def test_verified_stack_history_can_break_close_tie(self)
⋮----
learning={"stack_rankings":[
⋮----
def test_stack_history_below_threshold_is_ignored(self)
⋮----
def test_negative_stack_history_can_demote_combination(self)
def test_stack_history_does_not_cross_project_type(self)
⋮----
result=plan(
⋮----
def test_matching_project_type_can_apply_stack_history(self)
⋮----
def test_primary_domain_is_recorded_in_constraints(self)
⋮----
result=plan({"target_repo":"o/r","app_name":"demo","brief":"Vector animation app"},recs)
⋮----
def test_selection_margin_exposes_near_tie_confidence(self)
⋮----
def test_selection_margin_marks_clear_winner_high_confidence(self)
⋮----
def test_low_confidence_requires_independent_architecture_review(self)
⋮----
policy=result["autonomy_policy"]
⋮----
def test_clear_architecture_choice_allows_normal_autonomous_flow(self)
```

## File: test_architecture_preflight.py
```python
class ArchitecturePreflightTests(unittest.TestCase)
⋮----
def test_low_confidence_convergent_baseline_passes(self)
⋮----
decision = {
recommendations = {"matches": [
result = ap.validate(decision, recommendations)
⋮----
def test_low_confidence_divergent_baseline_holds_architecture_changes(self)
⋮----
def test_high_confidence_is_not_blocked_by_preflight_disagreement(self)
⋮----
def test_write_persists_machine_readable_result(self)
⋮----
result = ap.write(
saved = json.loads((Path(td) / "architecture-preflight.json").read_text())
```

## File: test_architecture_replacement_candidate.py
```python
class ReplacementCandidateTests(unittest.TestCase)
⋮----
def order(self)
⋮----
def candidate(self)
⋮----
def test_valid_candidate_is_normalized(self)
⋮----
result=validate(self.order(),self.candidate())
⋮----
def test_shell_command_is_rejected(self)
⋮----
candidate=self.candidate()
⋮----
def test_protected_path_is_rejected(self)
⋮----
def test_context_collection_is_bounded_and_finds_manifest(self)
⋮----
root=Path(td)
⋮----
rows=_collect_context(root,"a/current","a/better")
paths={x["path"] for x in rows}
```

## File: test_architecture_replacement_executor.py
```python
class ReplacementExecutorTests(unittest.TestCase)
⋮----
def order(self)
⋮----
def candidate(self)
⋮----
def test_candidate_identity_and_files_are_validated(self)
⋮----
files=_validate_candidate(self.order(),self.candidate())
⋮----
def test_protected_studio_path_is_rejected(self)
⋮----
c=self.candidate()
⋮----
def test_workflow_path_is_rejected(self)
⋮----
def test_parent_traversal_is_rejected(self)
⋮----
def test_default_validation_commands_are_bounded(self)
⋮----
commands=_commands(self.candidate())
⋮----
def test_candidate_cannot_change_identity(self)
```

## File: test_architecture_replacement_learning.py
```python
class ReplacementLearningTests(unittest.TestCase)
⋮----
def test_successful_replacement_pair_is_aggregated(self)
⋮----
root=Path(td)
⋮----
out=root/f"p{i}"; out.mkdir()
⋮----
row=arl.summarize(root)["rankings"][0]
⋮----
def test_same_pair_is_separated_by_context(self)
⋮----
rows=[
⋮----
rows=arl.summarize(root)["rankings"]
⋮----
by_framework={x["framework"]:x for x in rows}
⋮----
def test_observation_window_is_preserved(self)
⋮----
def test_detects_recent_regime_shift(self)
⋮----
root=Path(td); now=2_000_000_000.0
outcomes=[]
⋮----
row=arl.summarize(root,now=now)["rankings"][0]
⋮----
def test_small_recent_sample_does_not_trigger_regime_shift(self)
⋮----
outcomes=[(now-200*86400-i,True,False) for i in range(10)]
⋮----
def test_sequential_drift_detects_gradual_degradation(self)
⋮----
rows=[]
now=2_000_000_000.0
sequence=[True,True,True,True,True,True,True,False,True,False,False,False]
⋮----
result=arl._sequential_drift(rows)
⋮----
def test_sequential_drift_stable_sequence_remains_stable(self)
⋮----
rows=[{"observed_at":float(i),"successful":True} for i in range(12)]
⋮----
def test_sequential_drift_requires_minimum_samples(self)
⋮----
rows=[{"observed_at":float(i),"successful":False} for i in range(4)]
⋮----
def test_sequential_recovery_detects_sustained_improvement(self)
⋮----
sequence=[False,False,False,True,False,True,True,True,True,True]
⋮----
def test_recovery_requires_weak_baseline(self)
⋮----
rows=[{"observed_at":float(i),"successful":success} for i,success in enumerate(
⋮----
def test_short_improvement_is_not_recovery(self)
```

## File: test_architecture_replacement_merge_gate.py
```python
class ReplacementMergeGateTests(unittest.TestCase)
⋮----
def inputs(self)
⋮----
validation={
review={
package={
persisted={
⋮----
def test_gate_requires_explicit_authorization(self)
⋮----
result=build(*self.inputs())
⋮----
def test_head_mismatch_is_blocked(self)
⋮----
def test_not_ready_pr_is_blocked(self)
⋮----
def test_write_persists_gate(self)
⋮----
result=write(*self.inputs(),Path(td))
```

## File: test_architecture_replacement_merge.py
```python
class ReplacementMergeTests(unittest.TestCase)
⋮----
def fixtures(self)
⋮----
content=b"hello\n"
review={
package={
persisted={
gate={
authorization={
⋮----
def requester(self,content,merged=True)
⋮----
calls={"merge":0}
def request(url,token,method="GET",payload=None,*args,**kwargs)
⋮----
def test_explicit_authorization_allows_single_merge_write(self)
⋮----
requester=self.requester(content)
result=merge(
⋮----
def test_missing_authorization_blocks_before_merge(self)
```

## File: test_architecture_replacement_outcome.py
```python
class ReplacementOutcomeTests(unittest.TestCase)
⋮----
def fixtures(self)
⋮----
work={"id":"r1","current_repo":"a/current","replacement_repo":"a/better","risk":"low","scope":"narrow","framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android","current_major_version":1,"replacement_major_version":2}
merged={"status":"replacement_merged","work_order_id":"r1","merge_sha":"3"*40}
⋮----
def test_healthy_merge_is_success(self)
⋮----
result=build(work,merged,{"status":"post_merge_healthy","work_order_id":"r1","post_merge_healthy":True})
⋮----
def test_regression_is_failure(self)
⋮----
result=build(work,merged,{"status":"post_merge_regression","work_order_id":"r1","rollback_required":True,"failed_checks":["validate"]})
⋮----
def test_context_is_preserved(self)
```

## File: test_architecture_replacement_persist.py
```python
class ReplacementPersistTests(unittest.TestCase)
⋮----
def test_repository_identity_validation(self)
⋮----
def test_sha_validation(self)
```

## File: test_architecture_replacement_pipeline.py
```python
class ReplacementPipelineTests(unittest.TestCase)
⋮----
def test_pipeline_never_auto_promotes(self)
⋮----
root=Path(td)
order=root/"order.json"
⋮----
fake_candidate={
fake_execution={
fake_review={"status":"promotion_review_ready"}
fake_package={"status":"pr_package_ready"}
⋮----
result=arp.run(order,root,root/"out")
```

## File: test_architecture_replacement_planner.py
```python
class ArchitectureReplacementPlannerTests(unittest.TestCase)
⋮----
def obsolescence(self)
⋮----
def recommendations(self)
⋮----
def test_low_risk_when_capabilities_are_preserved(self)
⋮----
result=plan(self.obsolescence(),self.recommendations())
row=result["replacement_plans"][0]
⋮----
def test_missing_capability_is_high_risk(self)
⋮----
recs=self.recommendations()
⋮----
result=plan(self.obsolescence(),recs)
⋮----
def test_missing_maintenance_requires_gate(self)
⋮----
obs=self.obsolescence()
⋮----
result=plan(obs,self.recommendations())
⋮----
def test_bad_historical_replacement_raises_risk(self)
⋮----
learning={"rankings":[{
result=plan(self.obsolescence(),self.recommendations(),learning=learning)
⋮----
def test_strong_historical_replacement_is_recorded_but_does_not_skip_gates(self)
⋮----
def test_historical_evidence_does_not_cross_framework_context(self)
⋮----
learning={"rankings":[
result=plan(obs,self.recommendations(),learning=learning)
⋮----
def test_matching_context_can_apply_history(self)
⋮----
def test_generic_history_is_downweighted_for_specific_context(self)
⋮----
def test_nearby_major_versions_are_partially_transferable(self)
⋮----
row=plan(obs,self.recommendations(),learning=learning)["replacement_plans"][0]
⋮----
def test_large_version_distance_is_strongly_downweighted(self)
⋮----
def test_closest_history_is_selected_instead_of_largest_sample(self)
⋮----
def test_framework_mismatch_caps_transferability(self)
⋮----
def test_version_jump_similarity_handles_downgrades(self)
⋮----
def test_multiple_nearby_histories_are_fused(self)
⋮----
fused=row["fused_historical_evidence"]
⋮----
def test_distant_framework_history_has_small_fusion_weight(self)
⋮----
contributors=row["fused_historical_evidence"]["contributors"]
exact=next(x for x in contributors if x["framework"]=="flutter")
distant=next(x for x in contributors if x["framework"]=="python")
⋮----
def test_low_sample_histories_can_accumulate_effective_evidence(self)
⋮----
rows=[]
⋮----
row=plan(obs,self.recommendations(),learning={"rankings":rows})["replacement_plans"][0]
⋮----
def test_conflicting_fused_history_blocks_positive_bias(self)
⋮----
common={
good={**common,"current_major_version":3,"replacement_major_version":4,
bad={**common,"current_major_version":2,"replacement_major_version":3,
row=plan(obs,self.recommendations(),learning={"rankings":[good,bad]})["replacement_plans"][0]
⋮----
def test_recent_history_outweighs_equivalent_old_history(self)
⋮----
now=time.time()
⋮----
recent={**common,"current_major_version":3,"replacement_major_version":4,"latest_observed_at":now}
old={**common,"current_major_version":2,"replacement_major_version":3,"latest_observed_at":now-720*86400}
row=plan(obs,self.recommendations(),learning={"rankings":[recent,old]})["replacement_plans"][0]
⋮----
recent_row=next(x for x in contributors if x["current_major_version"]==3)
old_row=next(x for x in contributors if x["current_major_version"]==2)
⋮----
def test_temporal_decay_has_nonzero_floor(self)
⋮----
history={
row=plan(obs,self.recommendations(),learning={"rankings":[history]})["replacement_plans"][0]
contributor=row["fused_historical_evidence"]["contributors"][0]
⋮----
def test_missing_timestamp_is_neutral_conservative(self)
⋮----
def test_stale_fused_evidence_requires_revalidation(self)
⋮----
def test_regime_shift_forces_high_risk_and_revalidation(self)
⋮----
def test_minor_regime_signal_does_not_dominate_fusion(self)
⋮----
stable={**common,"current_major_version":1,"replacement_major_version":2,"regime_shift":False}
shifted={**common,"framework":"python","current_major_version":1,"replacement_major_version":2,
row=plan(obs,self.recommendations(),learning={"rankings":[stable,shifted]})["replacement_plans"][0]
⋮----
def test_sequential_drift_forces_high_risk_and_gate(self)
⋮----
def test_low_weight_sequential_drift_does_not_dominate_fusion(self)
⋮----
stable={
shifted={
⋮----
def test_recovery_candidate_reduces_old_negative_bias_but_requires_gate(self)
⋮----
def test_low_weight_recovery_does_not_override_bad_fusion(self)
⋮----
bad={
recovering={
row=plan(obs,self.recommendations(),learning={"rankings":[bad,recovering]})["replacement_plans"][0]
⋮----
def test_recovery_never_skips_isolated_benchmark_gate(self)
⋮----
def test_reputation_state_machine(self)
⋮----
cases=[
⋮----
def test_quarantined_reputation_adds_explicit_gate(self)
⋮----
def test_trusted_reputation_is_explainable_and_promotion_eligible(self)
⋮----
reputation=row["replacement_reputation"]
⋮----
def test_recovering_reputation_never_becomes_trusted_directly(self)
⋮----
evidence={
reputation_state=arp.reputation_desired_state(evidence)
reputation={
⋮----
def test_persistent_reputation_overrides_current_derived_state(self)
⋮----
context={
⋮----
row=plan(
⋮----
def test_persisted_recovering_state_clamps_bias_and_adds_transition_gate(self)
⋮----
def test_persisted_degraded_state_blocks_positive_bias(self)
⋮----
strong={
weak={**strong,"regression_rate":0.40,"wilson_lower_95":0.30}
⋮----
def test_planner_uses_canonical_reputation_engine(self)
⋮----
canonical=arp.reputation_desired_state(row["fused_historical_evidence"])
⋮----
def test_stale_persisted_policy_requires_revalidation(self)
⋮----
entry=next(iter(registry["entries"].values()))
⋮----
rep=row["replacement_reputation"]
⋮----
def test_current_persisted_policy_does_not_require_revalidation(self)
⋮----
def test_write_persists_plan(self)
⋮----
out=Path(td)
result=write(self.obsolescence(),self.recommendations(),out)
saved=json.loads((out/"architecture-replacement-plan.json").read_text())
```

## File: test_architecture_replacement_postmerge_pipeline.py
```python
class ReplacementPostMergePipelineTests(unittest.TestCase)
⋮----
def test_healthy_result_records_learning_without_rollback_gate(self)
⋮----
root=Path(td)
work=root/"work.json"; merged=root/"merged.json"; package=root/"package.json"
⋮----
post={"status":"post_merge_healthy","work_order_id":"r1","post_merge_healthy":True,"rollback_required":False}
⋮----
result=pipeline.run(work,merged,package,root/"studio-output"/"p1","token","owner/repo")
⋮----
def test_regression_emits_rollback_gate(self)
⋮----
post={"status":"post_merge_regression","work_order_id":"r1","post_merge_healthy":False,"rollback_required":True,"failed_checks":["validate"],"content_mismatches":[]}
gate={"status":"rollback_authorization_required"}
⋮----
def test_nonterminal_postmerge_does_not_pollute_learning(self)
⋮----
post={"status":"awaiting_post_merge_checks","work_order_id":"r1","post_merge_healthy":False,"rollback_required":False}
out=root/"studio-output"/"p1"
⋮----
result=pipeline.run(work,merged,package,out,"token","owner/repo")
⋮----
learning=json.loads((root/"studio-output"/"architecture-replacement-learning.json").read_text())
⋮----
def test_terminal_outcome_persists_reputation_registry(self)
⋮----
registry_path=root/"studio-output"/"architecture-replacement-reputation.json"
⋮----
registry=json.loads(registry_path.read_text())
⋮----
entry=next(iter(registry["entries"].values()))
⋮----
def test_nonterminal_state_does_not_write_reputation(self)
```

## File: test_architecture_replacement_postmerge.py
```python
class ReplacementPostMergeTests(unittest.TestCase)
⋮----
def fixtures(self)
⋮----
content=b"hello\n"
merged={
package={
⋮----
def requester(self,content,failed=False,main=True)
⋮----
def request(url,token,*args,**kwargs)
⋮----
def test_clean_merge_is_healthy(self)
⋮----
result=verify(merged,package,"token","owner/repo",requester=self.requester(content))
⋮----
def test_failed_main_check_requires_rollback(self)
⋮----
result=verify(merged,package,"token","owner/repo",requester=self.requester(content,failed=True))
⋮----
def test_main_not_yet_at_merge_waits(self)
⋮----
result=verify(merged,package,"token","owner/repo",requester=self.requester(content,main=False))
```

## File: test_architecture_replacement_pr_package.py
```python
class ReplacementPRPackageTests(unittest.TestCase)
⋮----
def review(self)
⋮----
def candidate(self)
⋮----
def test_package_is_non_networking(self)
⋮----
result=build(self.review(),self.candidate())
⋮----
def test_identity_mismatch_is_blocked(self)
⋮----
c=self.candidate()
⋮----
def test_write_persists_package(self)
⋮----
result=write(self.review(),self.candidate(),Path(td))
```

## File: test_architecture_replacement_pr_validator.py
```python
class ReplacementPRValidatorTests(unittest.TestCase)
⋮----
def review(self)
⋮----
def package(self)
⋮----
data=b"hello\n"
⋮----
def persisted(self)
⋮----
def requester(self,draft=False,mergeable=True,checks=True,content=b"hello\n")
⋮----
def request(url,token,*args,**kwargs)
⋮----
runs=[]
⋮----
def test_clean_non_draft_pr_is_ready(self)
⋮----
result=validate(
⋮----
def test_draft_is_validated_but_not_merge_ready(self)
⋮----
def test_missing_checks_waits(self)
⋮----
def test_content_change_is_blocked(self)
```

## File: test_architecture_replacement_promotion.py
```python
class ReplacementPromotionTests(unittest.TestCase)
⋮----
def order(self)
⋮----
def candidate(self)
⋮----
def execution(self)
⋮----
def test_clean_evidence_is_review_ready(self)
⋮----
result=review(self.order(),self.candidate(),self.execution())
⋮----
def test_network_not_disabled_is_blocked(self)
⋮----
execution=self.execution()
⋮----
def test_candidate_validation_failure_is_blocked(self)
⋮----
def test_identity_mismatch_is_blocked(self)
⋮----
candidate=self.candidate()
⋮----
def test_write_persists_review_package(self)
⋮----
result=write(self.order(),self.candidate(),self.execution(),Path(td))
```

## File: test_architecture_replacement_reputation_state_machine.py
```python
class ReplacementReputationStateMachineExhaustiveTests(unittest.TestCase)
⋮----
def setUp(self)
⋮----
def test_no_two_step_path_from_quarantine_to_trusted_bypasses_recovering(self)
⋮----
states=sorted(arr.REPUTATION_STATES)
⋮----
first=arr.transition_policy("QUARANTINED",middle)
second=arr.transition_policy(middle,"TRUSTED")
⋮----
def test_all_allowed_dangerous_targets_have_required_gate(self)
⋮----
required=arr.DANGEROUS_STATE_GATES.get(target)
⋮----
def test_exhaustive_desired_state_sequences_never_jump_quarantine_to_trusted(self)
⋮----
desired_states=["TRUSTED","DEGRADED","QUARANTINED","RECOVERING","EXPERIMENTAL"]
⋮----
registry=None
now=100.0
previous=None
saw_quarantine=False
⋮----
evidence=self.evidence[desired]
⋮----
saw_quarantine=True
⋮----
previous=entry["state"]
⋮----
def test_recovery_to_trusted_requires_elapsed_time_and_new_samples(self)
⋮----
e={**self.evidence["TRUSTED"],"effective_samples":samples}
⋮----
e={**self.evidence["TRUSTED"],"effective_samples":22}
```

## File: test_architecture_replacement_reputation.py
```python
class ReplacementReputationTests(unittest.TestCase)
⋮----
def context(self)
⋮----
def strong(self)
⋮----
def test_unobserved_can_become_trusted_with_strong_evidence(self)
⋮----
def test_trusted_quarantines_immediately_on_drift(self)
⋮----
evidence={**self.strong(),"sequential_drift":True}
⋮----
def test_quarantine_cannot_jump_directly_to_trusted(self)
⋮----
def test_recovery_requires_time_new_evidence_and_confirmations(self)
⋮----
# Time alone is insufficient because no new effective evidence arrived.
later=300.0+arr.RECOVERY_MIN_DWELL_SECONDS+1
⋮----
stronger={**self.strong(),"effective_samples":22}
⋮----
def test_recovery_dwell_blocks_fast_repromotion(self)
⋮----
richer={**self.strong(),"effective_samples":25}
⋮----
def test_degradation_from_trusted_is_immediate(self)
⋮----
weak={
⋮----
def test_policy_is_exported_in_registry(self)
⋮----
policy=registry["policy"]
⋮----
def test_transition_matrix_is_fail_closed(self)
⋮----
rule=arr.transition_policy("TRUSTED","RECOVERING")
⋮----
def test_recovery_policy_declares_all_upward_requirements(self)
⋮----
rule=arr.transition_policy("RECOVERING","TRUSTED")
⋮----
def test_entry_exposes_versioned_transition_rule(self)
⋮----
def test_quarantine_rule_is_critical(self)
⋮----
def test_policy_graph_is_valid(self)
⋮----
validation=arr.validate_transition_policy()
⋮----
def test_validator_rejects_direct_quarantine_to_trusted(self)
⋮----
policy={state:dict(row) for state,row in arr.TRANSITION_POLICY.items()}
⋮----
validation=arr.validate_transition_policy(policy)
⋮----
def test_validator_rejects_dangerous_transition_without_gate(self)
⋮----
def test_validator_rejects_recovery_without_hysteresis(self)
⋮----
def test_validator_rejects_unknown_and_unreachable_states(self)
⋮----
def test_apply_fail_closed_on_invalid_global_policy(self)
⋮----
original=arr.TRANSITION_POLICY
⋮----
def test_policy_digest_is_stable_and_exported(self)
⋮----
first=arr.transition_policy_digest()
second=arr.transition_policy_digest()
⋮----
def test_policy_digest_changes_when_policy_changes(self)
⋮----
modified={state:dict(row) for state,row in arr.TRANSITION_POLICY.items()}
⋮----
def test_audit_records_every_transition(self)
⋮----
def test_update_persists_registry(self)
⋮----
path=Path(td)/"architecture-replacement-reputation.json"
entry=arr.update(path,self.context(),self.strong(),now=100.0)
⋮----
loaded=arr.load(path)
⋮----
def test_learning_style_sequential_dict_drives_quarantine(self)
⋮----
evidence={**self.strong(),"sequential_drift":{"drift_detected":True,"status":"drift"}}
state=arr.desired_state(evidence)
⋮----
def test_learning_style_recovery_dict_drives_recovering(self)
⋮----
evidence={
```

## File: test_architecture_replacement_rollback_gate.py
```python
class ReplacementRollbackGateTests(unittest.TestCase)
⋮----
def fixtures(self)
def test_regression_creates_explicit_gate(self)
⋮----
result=build(*self.fixtures())
⋮----
def test_healthy_state_cannot_create_rollback_gate(self)
```

## File: test_architecture_replacement_rollback.py
```python
class ReplacementRollbackTests(unittest.TestCase)
⋮----
def fixtures(self)
⋮----
gate={"status":"rollback_authorization_required","authorization_id":"2"*64,"work_order_id":"r1","merge_sha":"3"*40,"baseline_sha":"0"*40,"reason":{"failed_checks":["validate"]}}
auth={"status":"explicit_rollback_authorization","authorization_id":"2"*64,"work_order_id":"r1","merge_sha":"3"*40,"authorized":True}
⋮----
def requester(self)
⋮----
calls={"prs":0}
def request(url,token,method="GET",payload=None,*args,**kwargs)
⋮----
def test_authorized_regression_creates_draft_rollback_pr(self)
⋮----
gate,auth=self.fixtures(); requester=self.requester()
result=execute(gate,auth,"token","owner/repo",requester=requester)
⋮----
def test_main_advance_blocks_rollback_preparation(self)
⋮----
def request(url,token,*args,**kwargs)
```

## File: test_architecture_replacement_work_order.py
```python
class ReplacementWorkOrderTests(unittest.TestCase)
⋮----
def plan(self)
⋮----
def test_build_is_fail_closed(self)
⋮----
result=build(self.plan())
⋮----
order=result["work_orders"][0]
⋮----
def test_context_is_carried_into_work_order(self)
⋮----
order=build(self.plan())["work_orders"][0]
⋮----
def test_id_is_deterministic(self)
⋮----
first=build(self.plan())["work_orders"][0]["id"]
second=build(self.plan())["work_orders"][0]["id"]
⋮----
def test_write_persists(self)
⋮----
out=Path(td)
result=write(self.plan(),out)
saved=json.loads((out/"architecture-replacement-work-orders.json").read_text())
```

## File: test_architecture_reputation_policy_approval.py
```python
def _canonical(value)
⋮----
class ApprovalProvenanceTests(unittest.TestCase)
⋮----
def approval(self,reinforced=False)
⋮----
a={"migration_id":"m1","review_digest":"r1","reviewer":{"id":"alice","roles":["reviewer"]}}
⋮----
def test_standard_approval(self)
def test_reinforced_requires_separation(self)
⋮----
a=self.approval(True);a["second_reviewer"]["id"]="alice";a["approval_digest"]=approval_digest(a)
⋮----
def test_reinforced_accepts_distinct_risk_owner(self)
def test_ledger_is_append_only_and_replay_safe(self)
⋮----
a=self.approval();ledger=consume(None,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=1)
⋮----
def test_tampered_ledger_fails(self)
⋮----
ledger=copy.deepcopy(ledger);ledger["events"][0]["applied_at"]=99
⋮----
def canonical_workflow_file(self)
⋮----
raw=(Path(__file__).resolve().parents[1]/".github/workflows/ci.yml").read_bytes()
validation=validate_workflow_text(raw.decode("utf-8"))
⋮----
def github_attestation(self,reinforced=False)
⋮----
a={
⋮----
payload={k:v for k,v in a.items() if k!="attestation_digest"}
⋮----
def test_github_attestation_binds_commit_review_permission_and_workflow(self)
⋮----
got=validate_github_attestation(self.github_attestation(),{"migration_id":"m1","review_digest":"r1"},reinforced=False)
⋮----
def test_github_attestation_rejects_stale_commit(self)
⋮----
a=self.github_attestation();a["reviewed_commit_sha"]="old";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
⋮----
def test_github_attestation_rejects_read_only_reviewer(self)
⋮----
a=self.github_attestation();a["reviewer"]["permission"]="read";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
⋮----
def test_github_reinforced_requires_distinct_approver(self)
⋮----
a=self.github_attestation(True);a["second_reviewer"]["login"]="alice";a["attestation_digest"]=hashlib.sha256(_canonical({k:v for k,v in a.items() if k!="attestation_digest"}).encode()).hexdigest()
⋮----
def test_github_attestation_rejects_review_before_head_commit(self)
⋮----
a=self.github_attestation()
⋮----
def test_github_attestation_rejects_draft_pr(self)
⋮----
def test_github_attestation_rejects_mixed_workflow_runs(self)
⋮----
def test_github_attestation_rejects_attested_workflow_id_mismatch(self)
⋮----
def test_github_attestation_rejects_workflow_content_with_mutable_action(self)
⋮----
raw=(b"name: CI\n" b"jobs:\n" b"  validate:\n" b"    steps:\n" b"      - uses: actions/checkout@v4\n" b"  python-tests:\n")
⋮----
def test_github_attestation_rejects_wrong_workflow_file_digest(self)
⋮----
a=self.github_attestation();a["workflow_file"]["sha256"]="bad";self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_untrusted_workflow_path(self)
⋮----
a=self.github_attestation();a["workflow"]["path"]=".github/workflows/other.yml";self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_untrusted_workflow_name(self)
⋮----
a=self.github_attestation();a["workflow"]["name"]="Other";self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_stale_workflow(self)
⋮----
a=self.github_attestation();a["workflow"]["timestamp"]=1767225599.0;self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_stale_required_check(self)
⋮----
a=self.github_attestation();a["required_checks"]["valid"]=False;a["required_checks"]["stale_checks"]=["validate"];self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_forged_pass_without_check_evidence(self)
⋮----
a=self.github_attestation();a["required_checks"]["check_evidence"].pop("validate");self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_check_evidence_for_wrong_sha(self)
⋮----
a=self.github_attestation();a["required_checks"]["check_evidence"]["validate"]["head_sha"]="old";self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_check_evidence_before_head_commit(self)
⋮----
a=self.github_attestation();a["required_checks"]["check_evidence"]["validate"]["timestamp"]=1767225599.0;self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_failed_required_check(self)
⋮----
a=self.github_attestation();a["required_checks"]["valid"]=False;a["required_checks"]["failed_checks"]=["validate"];self._redigest_attestation(a)
⋮----
def _redigest_attestation(self,a)
def test_github_attestation_rejects_missing_semantic_digest(self)
⋮----
a=self.github_attestation();a["workflow_file"].pop("semantic_digest",None);self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_forged_semantic_digest(self)
⋮----
a=self.github_attestation();a["workflow_file"]["semantic_digest"]="0"*64;self._redigest_attestation(a)
⋮----
def test_github_attestation_rejects_invalid_semantic_digest_length(self)
⋮----
a=self.github_attestation();a["workflow_file"]["semantic_digest"]="bad";self._redigest_attestation(a)
```

## File: test_architecture_reputation_policy_github_attestation.py
```python
def canonical_ci_file()
⋮----
raw=(Path(__file__).resolve().parents[1]/".github/workflows/ci.yml").read_bytes()
validation=validate_workflow_text(raw.decode("utf-8"))
⋮----
class GitHubAttestationBuilderTests(unittest.TestCase)
⋮----
plan={"migration_id":"m","review_digest":"r"}
⋮----
def check_runs(self)
⋮----
def pr_identity(self)
⋮----
def workflow_file(self)
def test_build_standard(self)
⋮----
a=build(self.plan,repository="o/r",pull_request=7,commit_sha="abc",
⋮----
def test_latest_review_wins(self)
⋮----
rows=latest_approvals([
⋮----
def test_latest_review_order_is_timestamp_driven(self)
⋮----
def test_reinforced_requires_two_eligible(self)
def test_missing_required_check_rejected(self)
⋮----
def test_draft_pr_rejected(self)
⋮----
identity=self.pr_identity()
⋮----
def test_approval_before_head_commit_is_rejected(self)
⋮----
def test_wrong_workflow_name_rejected(self)
⋮----
def test_wrong_workflow_path_rejected(self)
⋮----
def test_stale_workflow_time_rejected(self)
⋮----
def test_stale_check_time_rejected(self)
⋮----
checks=self.check_runs()
⋮----
def test_required_checks_from_different_workflow_runs_rejected(self)
⋮----
def test_stale_workflow_rejected(self)
```

## File: test_architecture_reputation_policy_github_collect.py
```python
def canonical_ci_bytes()
⋮----
class GitHubAttestationCollectorTests(unittest.TestCase)
⋮----
def plan(self,reinforced=False)
⋮----
def responses(self,reinforced=False)
⋮----
reviews=[
⋮----
def fake_request(self,reinforced=False)
⋮----
reviews=self.responses(reinforced)
def _request(url,token,method="GET",payload=None,allow_404=False)
⋮----
raw=canonical_ci_bytes()
⋮----
def test_collects_standard_attestation(self)
⋮----
result=collector.collect(self.plan(False),token="t",repository="o/r",pull_request=7)
⋮----
def test_collects_reinforced_attestation(self)
⋮----
result=collector.collect(self.plan(True),token="t",repository="o/r",pull_request=7)
⋮----
def test_collect_rejects_write_permissions(self)
⋮----
base=self.fake_request(False)
def req(url,token,method="GET",payload=None,allow_404=False)
⋮----
raw=b"name: CI\npermissions:\n  contents: write\njobs:\n  validate:\n  python-tests:\n"
⋮----
def test_collect_rejects_mutable_action_reference(self)
⋮----
raw=(
⋮----
def test_collect_rejects_workflow_file_without_required_job(self)
⋮----
raw=b"name: CI\njobs:\n  python-tests:\n"
⋮----
def test_collect_rejects_stale_required_check(self)
⋮----
def test_collect_rejects_stale_workflow(self)
⋮----
def test_collect_rejects_review_older_than_head_commit(self)
⋮----
def test_collect_rejects_draft_pr(self)
⋮----
value=base(url,token,method,payload,allow_404)
⋮----
def test_missing_token_is_fail_closed(self)
```

## File: test_architecture_reputation_policy_migration_cli.py
```python
class ReputationPolicyMigrationCLITests(unittest.TestCase)
⋮----
def registry(self)
⋮----
context={"current_repo":"a/current","replacement_repo":"a/better","framework":"flutter","project_type":"game","primary_domain":"mobile","platform":"android","current_major_version":1,"replacement_major_version":2}
evidence={"effective_samples":20,"evidence_confidence":1.0,"wilson_lower_95":0.82,"regression_rate":0.02}
⋮----
entry=next(iter(registry["entries"].values()))
⋮----
def canonical_workflow_file(self)
⋮----
raw=(Path(__file__).resolve().parents[1]/".github/workflows/ci.yml").read_bytes()
validation=validate_workflow_text(raw.decode("utf-8"))
⋮----
def target_for(self,workflow_file)
⋮----
def test_review_writes_plan(self)
⋮----
root=Path(td);registry=root/"registry.json";registry.write_text(json.dumps(self.registry()))
rc=cli.main(["review",str(registry),"--out",str(root/"out")])
⋮----
plan=root/"out"/"architecture-reputation-policy-migration-review.json"
⋮----
def test_apply_requires_authorized_record(self)
⋮----
root=Path(td);registry_value=self.registry();registry=root/"registry.json";registry.write_text(json.dumps(registry_value))
plan_value=dry_run(registry_value,None,now=200.0);plan=root/"plan.json";plan.write_text(json.dumps(plan_value))
auth=root/"auth.json";auth.write_text(json.dumps(plan_value["authorization_template"]))
⋮----
def test_apply_can_auto_collect_github_attestation(self)
⋮----
workflow_file=self.canonical_workflow_file()
now=time.time()
plan_value=dry_run(registry_value,None,now=now)
plan_value=bind_github_review_target(plan_value,self.target_for(workflow_file),now=now)
plan=root/"plan.json";plan.write_text(json.dumps(plan_value))
auth_value=dict(plan_value["authorization_template"]);auth_value["authorized"]=True
⋮----
auth=root/"auth.json";auth.write_text(json.dumps(auth_value))
reinforced=plan_value.get("risk",{}).get("reinforced_review_required") is True
reviews=[{"user":{"login":"alice"},"state":"APPROVED","commit_id":"a"*40,"submitted_at":"2026-01-01T00:00:10Z"}];permissions={"alice":"write"}
⋮----
attestation=build(
⋮----
rc=cli.main(["apply",str(registry),str(plan),str(auth),"--repository","dbrckk/ai-dev-server","--pull-request","7"])
⋮----
def test_bind_target_reissues_content_bound_plan(self)
⋮----
root=Path(td);registry_value=self.registry();plan_value=dry_run(registry_value,None,now=200.0);original_id=plan_value["migration_id"]
plan=root/"plan.json";plan.write_text(json.dumps(plan_value));workflow_file=self.canonical_workflow_file();target=self.target_for(workflow_file);out=root/"bound.json"
⋮----
rc=cli.main(["bind-target",str(plan),"--repository","dbrckk/ai-dev-server","--pull-request","7","--out",str(out)])
self.assertEqual(rc,0);bound=json.loads(out.read_text());self.assertNotEqual(bound["migration_id"],original_id)
```

## File: test_architecture_reputation_policy_migration_review.py
```python
class ReputationPolicyMigrationReviewTests(unittest.TestCase)
⋮----
def test_render_contains_human_review_information(self)
⋮----
plan={
text=render(plan)
```

## File: test_architecture_reputation_policy_migration.py
```python
class ReputationPolicyMigrationTests(unittest.TestCase)
⋮----
def context(self)
⋮----
def registry(self)
⋮----
strong={
⋮----
# Simulate a registry created under an older policy.
⋮----
entry=next(iter(registry["entries"].values()))
⋮----
def learning(self,strong=True)
⋮----
def canonical_workflow_file(self)
⋮----
raw=(Path(__file__).resolve().parents[1]/".github/workflows/ci.yml").read_bytes()
validation=validate_workflow_text(raw.decode("utf-8"))
⋮----
def authorize(self,plan)
⋮----
bound=bind_github_review_target(plan,{
⋮----
auth=dict(plan["authorization_template"])
⋮----
def approval(self,plan,reinforced=False)
⋮----
value={
⋮----
def github_attestation(self,plan,reinforced=False)
⋮----
reviews=[
permissions={"reviewer-a":"write"}
⋮----
def apply(self,registry,plan,auth,now=300.0,approval=None,ledger=None,github_attestation=None)
⋮----
reinforced=plan.get("risk",{}).get("reinforced_review_required") is True
⋮----
def test_dry_run_is_content_bound_and_non_mutating(self)
⋮----
registry=self.registry()
original=copy.deepcopy(registry)
plan=dry_run(registry,self.learning(),now=200.0)
⋮----
def test_policy_migration_can_downgrade_trusted(self)
⋮----
plan=dry_run(self.registry(),self.learning(strong=False),now=200.0)
row=plan["changes"][0]
⋮----
def test_policy_migration_never_promotes_nontrusted_directly(self)
⋮----
plan=dry_run(registry,self.learning(strong=True),now=200.0)
⋮----
def test_apply_requires_explicit_authorization(self)
⋮----
def test_bind_target_rejects_untrusted_workflow_path(self)
⋮----
plan=dry_run(self.registry(),self.learning(),now=200.0)
⋮----
def test_bind_target_rejects_invalid_workflow_digest(self)
⋮----
def test_apply_rejects_unbound_github_review_target(self)
⋮----
auth=dict(plan["authorization_template"]); auth["authorized"]=True
⋮----
def test_apply_is_bound_to_exact_registry(self)
⋮----
changed=copy.deepcopy(registry)
⋮----
def test_authorized_apply_updates_policy_and_audit(self)
⋮----
migrated=self.apply(registry,plan,self.authorize(plan),now=300.0)
⋮----
entry=next(iter(migrated["entries"].values()))
⋮----
def test_preserved_quarantine_keeps_revalidation_gate(self)
⋮----
migrated_entry=next(iter(migrated["entries"].values()))
⋮----
def test_policy_migration_does_not_mutate_source_registry(self)
⋮----
def test_trust_downgrade_risk_classification(self)
⋮----
plan=dry_run(registry,self.learning(strong=False),now=200.0)
⋮----
def test_promotion_path_change_requires_reinforced_review(self)
⋮----
# Simulate an older policy whose RECOVERING -> TRUSTED rule differs.
⋮----
def test_reinforced_review_is_required_for_promotion_path_change(self)
⋮----
auth=self.authorize(plan)
⋮----
migrated=self.apply(registry,plan,auth,now=300.0)
⋮----
def test_no_impact_when_registry_already_matches_current_policy(self)
⋮----
def test_source_invalid_policy_is_critical(self)
⋮----
def test_explainer_describes_policy_edge_and_state_impact(self)
⋮----
explanation=plan["explanation"]
⋮----
edge=next(x for x in explanation["policy_changes"] if x["transition"]=="RECOVERING -> TRUSTED")
fields={x["field"] for x in edge["changes"]}
⋮----
def test_explainer_no_impact_is_compact(self)
⋮----
def test_authorization_is_bound_to_review_digest(self)
⋮----
tampered=copy.deepcopy(plan)
⋮----
def test_authorization_expires(self)
⋮----
def test_authorization_rejects_future_issue_time(self)
⋮----
def test_authorization_rejects_extended_expiry(self)
⋮----
def test_review_digest_is_persisted_in_migration_audit(self)
⋮----
def test_apply_requires_reviewer_provenance(self)
⋮----
registry=self.registry();plan=dry_run(registry,self.learning(),now=200.0)
⋮----
def test_apply_records_reviewer_and_ledger(self)
⋮----
last=migrated["last_policy_migration"]
⋮----
def test_replay_ledger_rejects_same_migration(self)
⋮----
ledger=migrated["policy_migration_approval_ledger"]
⋮----
def test_apply_requires_github_attestation(self)
⋮----
def test_applied_migration_audits_github_attestation(self)
⋮----
def test_github_attestation_can_derive_approval_provenance(self)
⋮----
migrated=apply_migration(
⋮----
def test_manual_approval_identity_must_match_github(self)
⋮----
approval=self.approval(plan,reinforced=reinforced)
⋮----
def test_bind_target_rejects_missing_semantic_digest(self)
⋮----
wf=self.canonical_workflow_file()
target={"repository":"dbrckk/ai-dev-server","pull_request":42,"commit_sha":"a"*40,"head_ref":"policy/migration","base_ref":"main","author":"reviewer-a","workflow_path":".github/workflows/ci.yml","workflow_blob_sha":"blob123","workflow_sha256":wf["sha256"],"ci_trust_policy_version":CI_TRUST_POLICY_VERSION,"ci_trust_policy_digest":ci_trust_policy_digest()}
⋮----
def test_bind_target_rejects_invalid_semantic_digest(self)
⋮----
target={"repository":"dbrckk/ai-dev-server","pull_request":42,"commit_sha":"a"*40,"head_ref":"policy/migration","base_ref":"main","author":"reviewer-a","workflow_path":".github/workflows/ci.yml","workflow_blob_sha":"blob123","workflow_sha256":wf["sha256"],"workflow_semantic_digest":"bad","ci_trust_policy_version":CI_TRUST_POLICY_VERSION,"ci_trust_policy_digest":ci_trust_policy_digest()}
⋮----
def test_audit_persists_semantic_digest(self)
⋮----
def test_apply_rejects_semantic_digest_mismatch_between_target_and_attestation(self)
⋮----
attestation=self.github_attestation(plan)
⋮----
def test_apply_rejects_review_target_semantic_digest_tamper(self)
```

## File: test_architecture_safe_rewrite.py
```python
class ArchitectureSafeRewriteTests(unittest.TestCase)
⋮----
def test_context_contains_bounded_rewrite_contract(self)
⋮----
patch = {"files": [
context = safe.build_context(
⋮----
def test_patch_summary_is_file_count_bounded(self)
⋮----
patch = {
context = safe.build_context("BASE", patch, "blocked", engine="generic")
payload = json.loads(context.split("ARCHITECTURE_SAFE_REWRITE:\n", 1)[1])
rows = payload["architecture_safe_rewrite"]["rejected_patch_summary"]
```

## File: test_artifact_cas_audit.py
```python
class ArtifactCasAuditTests(unittest.TestCase)
⋮----
def test_records_monotonic_sequence(self)
⋮----
path = Path(td) / "audit.json"
⋮----
first = audit.record(
second = audit.record(
rows = audit.load()
⋮----
def test_audit_is_bounded(self)
```

## File: test_artifact_cas_namespace.py
```python
class ArtifactCasNamespaceTests(unittest.TestCase)
⋮----
def test_repository_id_becomes_safe_namespace(self)
⋮----
def test_unsafe_project_id_is_hashed(self)
⋮----
value = project_namespace("Private App / customer α")
⋮----
def test_same_blob_is_scoped_differently_per_project(self)
⋮----
digest = "a" * 64
⋮----
def test_invalid_content_digest_is_rejected(self)
```

## File: test_artifact_cas_promotion.py
```python
class ArtifactCasPromotionTests(unittest.TestCase)
⋮----
def _env(self, td)
⋮----
def test_promotes_explicit_safe_text_fixture(self)
⋮----
private = artifact_cas.put(b'{"fixture":"public"}')
result = promote_private(
shared = artifact_cas.get(
⋮----
def test_requires_exact_public_attestation(self)
⋮----
private = artifact_cas.put(b"public text")
⋮----
def test_rejects_binary_payload(self)
⋮----
private = artifact_cas.put(b"\x00\xff\x00\xff")
⋮----
def test_rejects_secret_marker(self)
⋮----
private = artifact_cas.put(b"token=ghp_example_secret")
```

## File: test_artifact_cas_stats.py
```python
class ArtifactCasStatsTests(unittest.TestCase)
⋮----
def test_hits_and_rebuild_cost_raise_retention_score(self)
⋮----
path = Path(td) / "stats.json"
env = {
⋮----
cold = "a" * 64
hot = "b" * 64
⋮----
def test_value_trim_keeps_more_valuable_blob_under_quota(self)
⋮----
low = "1" * 64
high = "2" * 64
⋮----
entries = {
⋮----
trimmed = cache._trim_by_value(entries)
⋮----
def test_recency_is_deterministic_logical_clock(self)
⋮----
older = "c" * 64
newer = "d" * 64
⋮----
def test_summary_reports_hits_bytes_and_protected_cost(self)
⋮----
digest = "e" * 64
⋮----
result = stats.summary()
```

## File: test_artifact_cas.py
```python
class ArtifactCasTests(unittest.TestCase)
⋮----
def test_put_get_and_deduplicate(self)
⋮----
env = {
⋮----
first = artifact_cas.put(b"payload")
second = artifact_cas.put(b"payload")
⋮----
blobs = [
⋮----
def test_corrupt_blob_is_rejected(self)
⋮----
meta = artifact_cas.put(b"payload")
⋮----
def test_physical_quota_rejects_new_blob_atomically(self)
⋮----
def test_private_same_blob_is_physically_isolated_per_project(self)
⋮----
base = {
⋮----
first = artifact_cas.put(b"same")
first_path = artifact_cas.blob_path(first["sha256"])
⋮----
second = artifact_cas.put(b"same")
second_path = artifact_cas.blob_path(second["sha256"])
⋮----
def test_shareable_blob_uses_common_scope_only_when_explicit(self)
⋮----
first = artifact_cas.put(
first_path = artifact_cas.blob_path(
⋮----
second = artifact_cas.put(
second_path = artifact_cas.blob_path(
⋮----
def test_shareable_requires_approved_class(self)
⋮----
def test_direct_shared_write_rejects_binary_payload(self)
⋮----
def test_shared_classes_are_physically_separated(self)
⋮----
fixture = artifact_cas.put(
toolchain = artifact_cas.put(
fixture_path = artifact_cas.blob_path(
toolchain_path = artifact_cas.blob_path(
⋮----
def test_private_metrics_do_not_collide_across_projects(self)
⋮----
digest = "a" * 64
⋮----
a = artifact_cas.stats_digest(digest)
⋮----
b = artifact_cas.stats_digest(digest)
⋮----
def test_explicit_shared_root_is_reused_across_project_roots(self)
⋮----
shared_root = Path(td) / "global-shared-cas"
first_env = {
second_env = {
⋮----
def test_gc_keeps_only_referenced_digest(self)
⋮----
keep = artifact_cas.put(b"keep")
drop = artifact_cas.put(b"drop")
result = artifact_cas.gc({keep["sha256"]})
```

## File: test_artifact_handoff.py
```python
class ArtifactHandoffTests(unittest.TestCase)
⋮----
def test_selects_latest_exact_project_artifact(self)
⋮----
payload={"artifacts":[
selected=select_latest_project_artifact(payload,"demo-v1")
⋮----
def test_expired_and_forged_names_are_ignored(self)
⋮----
def test_invalid_project_id_fails_closed(self)
⋮----
def test_invalid_listing_fails_closed(self)
⋮----
def test_same_timestamp_uses_artifact_id_deterministically(self)
```

## File: test_artwork_candidate_bridge.py
```python
class ArtworkCandidateBridgeTests(unittest.TestCase)
⋮----
def paths(self)
⋮----
root=Path(__file__).resolve().parents[1]
⋮----
def test_builds_generic_candidate_and_eligible_validation(self)
⋮----
def test_candidate_digest_covers_provider_and_tests(self)
⋮----
def test_missing_sources_fail_closed(self)
```

## File: test_artwork_capability.py
```python
class ArtworkCapabilityTests(unittest.TestCase)
⋮----
def png(self,path,w,h)
⋮----
def test_fallback_provider_is_safe_default(self)
⋮----
selected=select_provider(new_registry())
⋮----
def test_registered_provider_is_selected_but_still_requires_validation(self)
⋮----
registry=register(
selected=select_provider(registry)
⋮----
def test_valid_artwork_requires_visual_qa(self)
⋮----
root=Path(td)
icon=root/"icon.png"; feature=root/"feature.png"
⋮----
evidence=validate_artwork_set(
⋮----
def test_promoted_official_provider_has_studio_generated_provenance(self)
⋮----
root=Path(td); icon=root/"icon.png"; feature=root/"feature.png"
pixels=lambda w,h: b"".join(
⋮----
def test_third_party_provider_without_provenance_fails_closed(self)
⋮----
def test_verified_external_provider_requires_permissive_digest_provenance(self)
⋮----
def test_wrong_dimensions_fail_closed(self)
```

## File: test_artwork_stage.py
```python
class FakeGitHub
⋮----
def __init__(self,*args,**kwargs)
def publish(self,branch,parent,root,state)
⋮----
class ArtworkStageTests(unittest.TestCase)
⋮----
def state(self)
⋮----
def request(self,path)
⋮----
def test_valid_artwork_advances_to_privacy(self)
⋮----
root=Path(td); out=root/"out"; work=root/"work"
⋮----
req=root/"request.json"; self.request(req)
⋮----
store=out/"play-store"; store.mkdir()
⋮----
state=advance(req,work,out)
⋮----
def test_flat_artwork_fails_closed(self)
```

## File: test_artwork_validation.py
```python
class ArtworkValidationTests(unittest.TestCase)
⋮----
def provider(self)
⋮----
def test_produces_three_sealed_passed_proofs_without_promotion(self)
⋮----
result=validate_artwork_provider(self.provider())
⋮----
def test_benchmark_has_explicit_baseline(self)
⋮----
def test_missing_or_symlink_provider_fails_closed(self)
⋮----
missing=Path(td)/"missing.py"
```

## File: test_asset_artwork_capability.py
```python
class ArtworkCapabilityTests(unittest.TestCase)
⋮----
def test_generates_deterministic_icon_and_feature_graphic(self)
⋮----
context={
first=run(context)
second=run(context)
⋮----
def test_escapes_user_visible_label(self)
⋮----
result=run({"label":"<script>alert(1)</script>","assets":["feature_graphic"]})
svg=result["assets"]["feature_graphic"]["content"]
⋮----
def test_invalid_color_falls_back_deterministically(self)
⋮----
result=run({"label":"Demo","design":{"primary":"red"},"assets":["icon"]})
⋮----
def test_unsupported_or_duplicate_assets_fail_closed(self)
⋮----
def test_provider_has_no_side_effect_contract(self)
⋮----
result=run({"objective":"Create artwork"})
```

## File: test_asset_artwork_promotion.py
```python
class AssetArtworkPromotionTests(unittest.TestCase)
⋮----
BASELINE_SHA="0c9f44167f5b312b944027791e87fabfab44864b"
CANDIDATE_SHA="c6b1cfcb0551a59415b2277031ff318b0cfbdd54"
⋮----
def paths(self)
⋮----
root=Path(__file__).resolve().parents[1]
⋮----
def test_static_registry_matches_generic_promotion_gate(self)
⋮----
def test_promoted_artwork_syncs_only_through_registry_gate(self)
⋮----
registry=sync_into_registry(new_registry(),registry_path,repo_root=root)
item=registry["capabilities"]["asset_artwork"]
```

## File: test_asset_forge_installer.py
```python
ROOT = Path(__file__).resolve().parents[1]
⋮----
def test_asset_forge_installer_expands_environment_configuration()
⋮----
script = (ROOT / "scripts" / "install-asset-forge.sh").read_text(
⋮----
def test_asset_forge_installer_uses_pyproject_editable_install()
⋮----
def test_asset_forge_default_ref_is_immutable_commit()
```

## File: test_atomic_file.py
```python
class AtomicFileTests(unittest.TestCase)
⋮----
def test_write_bytes_replaces_existing_file_without_temp_leak(self)
⋮----
root = Path(td)
path = root / "state.json"
⋮----
def test_replace_failure_preserves_previous_file_and_cleans_temp(self)
⋮----
def test_write_text_uses_utf8(self)
⋮----
path = Path(td) / "unicode.txt"
```

## File: test_autonomous_project.py
```python
class AutonomousProjectTests(unittest.TestCase)
⋮----
def test_complete_requires_machine_completion_evidence(self)
⋮----
translated = translate_orchestrator_result({
⋮----
def test_false_complete_fails_closed(self)
⋮----
def test_human_action_is_preserved(self)
⋮----
def test_adaptation_yields_without_claiming_completion(self)
⋮----
def test_status_detail_that_requires_external_secret_becomes_human_action(self)
⋮----
def test_ordinary_failure_remains_autonomous_failure(self)
⋮----
def test_promoted_stage_syncs_into_capability_registry(self)
⋮----
root=Path(td); out=root/"out"
⋮----
control=root/"control"; control.mkdir()
⋮----
registry=load_registry(registry_path)
⋮----
def test_persistent_wrapper_relaunches_until_proved_complete(self)
⋮----
root = Path(td)
calls = {"n": 0}
⋮----
def run_once(*args)
⋮----
state = run_persistent_project(
⋮----
def test_persistent_godot_failure_counts_once_then_yields_for_fresh_workspace(self)
⋮----
def test_human_action_persists_terminal_state(self)
⋮----
def test_existing_project_registry_syncs_new_promoted_capability(self)
⋮----
root = Path(td) / "out"
⋮----
before = load_registry(registry_path)
⋮----
def sync(registry)
⋮----
after = load_registry(registry_path)
⋮----
def test_runtime_environment_is_restored_after_project_run(self)
⋮----
previous = os.environ.get("STUDIO_CHECKPOINT_PATH")
```

## File: test_autonomous_research.py
```python
class AutonomousResearchTests(unittest.TestCase)
⋮----
def search(self, query)
⋮----
def fetch(self, url)
⋮----
def test_research_seals_exact_content_and_provenance(self)
⋮----
result=run_research("cap-1","Implement safe capability",self.search,self.fetch)
⋮----
expected=hashlib.sha256(self.fetch(item["source"])).hexdigest()
⋮----
def test_research_memory_is_non_reusable(self)
⋮----
items=query(memory,project_id="project-a",kind="research")
⋮----
def test_insufficient_sources_never_claims_complete(self)
⋮----
result=run_research(
⋮----
def test_http_credentials_and_bad_provider_results_fail_closed(self)
⋮----
def test_source_deduplication_is_deterministic(self)
⋮----
def search(query)
result=run_research("cap-5","Need evidence",search,self.fetch)
```

## File: test_billing_qa.py
```python
class BillingQATests(unittest.TestCase)
⋮----
def make_app(self, root: Path)
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
def evidence(self, apk: Path)
⋮----
def test_billing_stage_is_registered(self)
⋮----
def test_without_play_sandbox_evidence_fails_closed(self)
⋮----
root = Path(tmp) / 'app'
out = Path(tmp) / 'out'
apk = self.make_app(root)
result = validate_billing(root, out)
⋮----
def test_matching_play_sandbox_evidence_passes(self)
⋮----
def test_wrong_apk_hash_is_rejected(self)
⋮----
value = self.evidence(apk)
⋮----
def test_incomplete_purchase_lifecycle_is_rejected(self)
```

## File: test_candidate_portfolio_learning.py
```python
class CandidatePortfolioLearningTests(unittest.TestCase)
⋮----
def test_recommendation_requires_minimum_samples(self)
⋮----
path = Path(td) / "candidate-width.json"
⋮----
result = learning.recommendation(learning.load(path))
⋮----
def test_verified_success_dominates_cost(self)
⋮----
def test_cost_breaks_close_success_outcomes(self)
⋮----
data = {
result = learning.recommendation(data)
⋮----
def test_history_can_reduce_but_not_expand_safe_width(self)
⋮----
reduced = choose_schedule(
⋮----
not_expanded = choose_schedule(
```

## File: test_capability_adaptation_state.py
```python
class CapabilityAdaptationStateTests(unittest.TestCase)
⋮----
def test_state_is_deterministic_and_sealed(self)
⋮----
one=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
two=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
⋮----
def test_tampering_fails_closed(self)
⋮----
state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
⋮----
def test_research_completion_advances_to_synthesis(self)
⋮----
state=record_research(state,"research_complete")
⋮----
def test_validated_candidate_advances_to_promotion_required(self)
⋮----
state=record_synthesis(state,"a"*64)
state=record_validation(state,"candidate_validated")
⋮----
def test_rejected_candidate_blocks_adaptation(self)
⋮----
state=record_validation(state,"candidate_rejected")
⋮----
def test_invalid_capability_rejected(self)
```

## File: test_capability_candidate_review_state.py
```python
def eligible()
⋮----
state=new_state("project","image_assets","improvement:1")
state=record_research(state,"research_complete")
state=record_synthesis(state,"a"*64)
⋮----
class CapabilityCandidateReviewStateTests(unittest.TestCase)
⋮----
def test_persisted_candidate_transitions_to_awaiting_merge(self)
⋮----
state=record_candidate_persistence(eligible(),"candidate_persisted")
⋮----
def test_idempotent_persistence_result_transitions_to_awaiting_merge(self)
⋮----
state=record_candidate_persistence(eligible(),"candidate_already_persisted")
⋮----
def test_unproved_persistence_status_fails_closed(self)
⋮----
def test_transition_requires_eligible_promotion_state(self)
```

## File: test_capability_candidate_validator.py
```python
def digest(value)
⋮----
def envelope()
⋮----
candidate={
⋮----
def proof(candidate_sha, *, passed=True, score=None, baseline_score=None, marker="e")
⋮----
out={"candidate_sha256":candidate_sha,"passed":passed,"evidence_sha256":marker*64}
⋮----
class CapabilityCandidateValidatorTests(unittest.TestCase)
⋮----
def test_all_gates_make_candidate_only_eligible(self)
⋮----
env=envelope(); sha=env["candidate_sha256"]
result=validate_candidate(
⋮----
def test_targeted_test_failure_rejects_candidate(self)
⋮----
def test_benchmark_regression_rejects_candidate(self)
⋮----
def test_tampered_candidate_fails_closed(self)
⋮----
env=envelope()
⋮----
sha=env["candidate_sha256"]
⋮----
def test_cross_candidate_proof_is_rejected(self)
```

## File: test_capability_memory.py
```python
def memory()
⋮----
value=new_memory()
⋮----
class CapabilityMemoryTests(unittest.TestCase)
⋮----
def test_returns_cross_project_validated_hint(self)
⋮----
hints=capability_hints(memory(),"app-b","billing_qa")
⋮----
def test_same_project_is_not_reused(self)
⋮----
def test_unrelated_capability_has_no_hint(self)
⋮----
def test_attached_hints_are_explicitly_non_authoritative(self)
⋮----
request={
enriched=attach_capability_hints(request,memory(),"app-b")
⋮----
policy=enriched["memory_policy"]
```

## File: test_capability_promotion.py
```python
def envelope()
⋮----
def validation()
⋮----
class CapabilityPromotionTests(unittest.TestCase)
⋮----
def test_validated_candidate_prepares_promoted_registry_only(self)
⋮----
registry={"version":1,"capabilities":{}}
⋮----
def test_unvalidated_candidate_fails_closed(self)
⋮----
bad=validation(); bad["promotion_status"]="not_ready"
⋮----
def test_cross_candidate_validation_is_rejected(self)
⋮----
bad=validation(); bad["candidate_sha256"]="f"*64
⋮----
def test_provider_must_be_deterministic(self)
⋮----
env=envelope()
⋮----
bad=validation(); bad["provider"]="studio.capabilities.custom_redirect"
⋮----
def test_conflicting_existing_promotion_is_rejected(self)
⋮----
registry={
```

## File: test_capability_qa.py
```python
class CapabilityQATests(unittest.TestCase)
⋮----
def make_app(self, root: Path, *, pubspec_extra: str = '', manifest_permissions=(), source='void main() {}')
⋮----
target = root / 'android/app/src/main'
⋮----
permissions = ''.join(
⋮----
def base_state(self)
⋮----
def test_standard_app_requires_no_specialized_qa(self)
⋮----
root = Path(tmp)
⋮----
evidence = classify(root)
⋮----
def test_game_dependency_requires_performance_qa(self)
⋮----
def test_native_and_notification_permissions_require_distinct_qa(self)
⋮----
def test_capability_requirements_block_finished_until_evidence_exists(self)
⋮----
state = self.base_state()
⋮----
def test_untrusted_dynamic_stage_name_is_ignored(self)
⋮----
stages = required_release_stages(state)
```

## File: test_capability_registry_promotion_persist.py
```python
class FakeGitHub
⋮----
def __init__(self)
⋮----
def get(self,path)
⋮----
raw=json.dumps({"version":1,"capabilities":{}}).encode()
⋮----
prefix="refs/heads/"+path.split("/git/matching-refs/heads/",1)[1]
⋮----
sha=path.rsplit("/",1)[-1]
⋮----
def call(self,method,path,payload=None)
⋮----
pr={"number":23,"head":{"ref":payload["head"],"sha":"2"*40}}
⋮----
def candidate()
⋮----
def validation_report()
⋮----
def review(gh)
⋮----
def merged()
⋮----
class RegistryPromotionPersistTests(unittest.TestCase)
⋮----
@patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_registry_only_pr_is_created_after_verified_merge(self,_vr,_vc)
⋮----
gh=FakeGitHub()
result=persist(gh,candidate(),validation_report(),review(gh),merged(),gh.main)
⋮----
tree_call=next(x for x in gh.calls if x[1].endswith("/git/trees"))
paths=[x["path"] for x in tree_call[2]["tree"]]
⋮----
@patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_provider_content_mismatch_fails_closed(self,_vr,_vc)
⋮----
original=gh.get
def bad(path)
⋮----
@patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_unmerged_candidate_cannot_prepare_registry_pr(self,_vr,_vc)
⋮----
@patch("studio.capability_registry_promotion_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.capability_registry_promotion_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_review_identity_mismatch_fails_closed(self,_vr,_vc)
⋮----
gh=FakeGitHub(); r=review(gh); r["candidate_id"]="other"
```

## File: test_capability_registry_review.py
```python
REVIEW={
⋮----
class GitHub
⋮----
def __init__(self,pr): self.pr=pr
def get(self,path)
⋮----
def pr(state="open",merged=False)
⋮----
class CapabilityRegistryReviewTests(unittest.TestCase)
⋮----
def test_open_exact_pr_remains_pending(self)
⋮----
def test_merged_exact_pr_reports_merge_without_activation(self)
⋮----
result=inspect(GitHub(pr(state="closed",merged=True)),REVIEW)
⋮----
def test_closed_unmerged_pr_is_rejected(self)
⋮----
def test_changed_head_fails_closed(self)
⋮----
value=pr(); value["head"]["sha"]="e"*40
⋮----
def test_changed_base_fails_closed(self)
⋮----
value=pr(); value["base"]["ref"]="release"
```

## File: test_capability_registry.py
```python
class CapabilityRegistryTests(unittest.TestCase)
⋮----
def test_register_requires_evidence(self)
⋮----
r=new_registry()
⋮----
def test_register_and_lookup(self)
⋮----
r=register(new_registry(),"godot.android.export","studio.godot_android_stage",{"tests":"passed"})
⋮----
def test_persistence_detects_tampering(self)
⋮----
p=Path(td)/"capabilities.json"
r=register(new_registry(),"godot.visual.qa","studio.godot_visual_stage",{"ci":"green"})
⋮----
value=json.loads(p.read_text())
```

## File: test_capability_review.py
```python
REVIEW={
⋮----
class GitHub
⋮----
def __init__(self,pr): self.pr=pr
def get(self,path)
⋮----
def pr(state="open",merged=False)
⋮----
class CapabilityReviewTests(unittest.TestCase)
⋮----
def test_open_exact_pr_remains_pending(self)
⋮----
def test_merged_exact_pr_reports_merge_commit_without_promoting(self)
⋮----
result=inspect(GitHub(pr(state="closed",merged=True)),REVIEW)
⋮----
def test_closed_unmerged_pr_is_rejected(self)
⋮----
def test_changed_head_fails_closed(self)
⋮----
value=pr(); value["head"]["sha"]="d"*40
⋮----
def test_changed_base_fails_closed(self)
⋮----
value=pr(); value["base"]["ref"]="release"
```

## File: test_capability_runtime.py
```python
class CapabilityRuntimeTests(unittest.TestCase)
⋮----
def make_provider(self, root, name, source)
⋮----
path=Path(root)/"studio/capabilities"/(name+".py")
⋮----
def registry(self, provider)
⋮----
def test_executes_registered_provider(self)
⋮----
result=execute_capability(
⋮----
def test_missing_or_symlink_provider_fails_closed(self)
⋮----
def test_provider_must_expose_run(self)
⋮----
def test_timeout_fails_closed(self)
⋮----
def test_non_json_result_is_rejected(self)
⋮----
def test_unregistered_capability_cannot_execute(self)
```

## File: test_capability_synthesis.py
```python
def memory_with_research()
⋮----
research={
⋮----
class CapabilitySynthesisTests(unittest.TestCase)
⋮----
def synth(self, context)
⋮----
def test_candidate_is_synthesized_but_never_promoted(self)
⋮----
result=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
⋮----
def test_same_inputs_are_deterministically_sealed(self)
⋮----
one=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
two=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
⋮----
def test_missing_research_fails_closed(self)
⋮----
def test_arbitrary_provider_redirect_is_rejected(self)
⋮----
def bad(context)
⋮----
value=self.synth(context)
⋮----
def test_candidate_cannot_smuggle_extra_control_fields(self)
```

## File: test_capacity_budget.py
```python
class CapacityBudgetTests(unittest.TestCase)
⋮----
def test_unmetered_capacity_expands_budget_most(self)
⋮----
plan = cb.expanded_call_limit(
⋮----
def test_large_pooled_quota_expands_budget(self)
⋮----
def test_low_remaining_pool_does_not_expand_budget(self)
⋮----
def test_explicit_user_limit_is_never_expanded(self)
⋮----
def test_automatic_limit_is_absolutely_capped(self)
```

## File: test_capacity_efficiency.py
```python
class CapacityEfficiencyTests(unittest.TestCase)
⋮----
def test_verified_progress_per_token_rewards_efficient_model(self)
⋮----
path = Path(td) / "efficiency.json"
⋮----
summary = efficiency.summarize(path)
⋮----
def test_failures_reduce_efficiency(self)
⋮----
row = efficiency.summarize(path)["rows"][0]
⋮----
def test_routing_bonus_prefers_verified_efficient_model(self)
⋮----
fast = efficiency.routing_bonus(
slow = efficiency.routing_bonus(
⋮----
def test_routing_bonus_requires_mature_comparison(self)
⋮----
summary = {
⋮----
def test_failure_streak_resets_after_verified_success(self)
⋮----
row = efficiency.record(
⋮----
def test_stagnation_routing_penalty_escalates_with_failure_streak(self)
⋮----
def test_stagnation_routing_penalty_is_neutral_without_streak(self)
⋮----
def test_sparse_projects_remain_neutral(self)
```

## File: test_capacity_ledger.py
```python
reserve = ledger.reserve
load = ledger.load
reserved_tokens = ledger.reserved_tokens
⋮----
class CapacityLedgerTests(unittest.TestCase)
⋮----
def test_provider_capacity_cannot_be_double_reserved(self)
⋮----
path = Path(td) / "ledger.json"
first = ledger.reserve(
second = ledger.reserve(
⋮----
def test_project_envelope_is_enforced_across_providers(self)
⋮----
def test_settle_releases_unused_reservation_and_records_actual_usage(self)
⋮----
reservation = ledger.reserve(
result = ledger.settle(
data = ledger.load(path)
⋮----
def test_release_on_failed_call_returns_full_reservation(self)
⋮----
result = ledger.release(path, reservation["reservation_id"], now=11)
⋮----
def test_expired_reservations_are_reaped_before_new_claim(self)
⋮----
def test_release_project_releases_only_owned_reservations(self)
⋮----
result = release_project(path, "a", now=101)
⋮----
remaining = load(path)["reservations"]
⋮----
def test_atomic_preemption_transfer_releases_victim_and_leases_contender(self)
⋮----
result = transfer_project_reservations(
⋮----
data = load(path)
⋮----
lease = next(iter(data["reservations"].values()))
⋮----
def test_claim_preemption_lease_converts_lease_to_worker_reservation(self)
⋮----
transfer = transfer_project_reservations(
claim = claim_preemption_lease(path, "high", now=102, ttl_seconds=600)
⋮----
row = load(path)["reservations"][claim["reservation_id"]]
⋮----
def test_expired_preemption_lease_cannot_be_claimed(self)
⋮----
claim = claim_preemption_lease(path, "high", now=131)
⋮----
def test_worker_heartbeat_renews_only_on_progress(self)
⋮----
claim = claim_preemption_lease(path, "high", now=101, ttl_seconds=100)
first = heartbeat(
⋮----
stalled = heartbeat(
⋮----
advanced = heartbeat(
```

## File: test_capacity_runtime.py
```python
class CapacityRuntimeTests(unittest.TestCase)
⋮----
def test_reads_project_envelope(self)
⋮----
path = Path(td) / "plan.json"
⋮----
def test_missing_or_invalid_plan_returns_none(self)
⋮----
path = Path(td) / "missing.json"
⋮----
def test_reads_full_project_state_for_recovery(self)
⋮----
row = project_state(path, "a")
```

## File: test_capacity_scheduler_omniroute.py
```python
class CapacitySchedulerOmniRouteTests(unittest.TestCase)
⋮----
def test_cli_replaces_static_omniroute_capacity_with_live_remaining(self)
⋮----
snapshot = OmniRouteCapacitySnapshot(
⋮----
root = Path(tmp)
projects = root / "projects.json"
providers = root / "providers.json"
output = root / "capacity.json"
⋮----
rc = main([
⋮----
report = json.loads(output.read_text(encoding="utf-8"))
```

## File: test_capacity_scheduler_work_conserving.py
```python
class WorkConservingCapacityTests(unittest.TestCase)
⋮----
def test_finite_capacity_is_redistributed_when_peer_hits_cap(self)
⋮----
providers = [ProviderCapacity("free", 1000, unmetered=False)]
report = allocate([
by_id = {row["id"]: row for row in report["projects"]}
⋮----
def test_reserved_capacity_is_not_spent_by_ordinary_projects(self)
⋮----
def test_critical_project_can_consume_unused_ordinary_pool(self)
⋮----
def test_redistribution_respects_pause_stagnation_caps_and_total_capacity(self)
```

## File: test_capacity_scheduler.py
```python
class CapacitySchedulerTests(unittest.TestCase)
⋮----
def test_unmetered_capacity_removes_token_constraint(self)
⋮----
providers = [
report = allocate([
⋮----
def test_critical_project_can_use_reserved_capacity(self)
⋮----
providers = [ProviderCapacity("omniroute", 1_000, unmetered=False)]
⋮----
by_id = {row["id"]: row for row in report["projects"]}
⋮----
def test_provider_order_prefers_unmetered_then_free_then_paid(self)
⋮----
report = allocate([{"id": "p", "requested_tokens": 100}], providers)
order = [row["name"] for row in report["projects"][0]["provider_order"]]
⋮----
def test_provider_peers_rank_by_runtime_evidence(self)
⋮----
def test_adaptive_score_does_not_override_free_first_policy(self)
⋮----
def test_parser_normalizes_adaptive_provider_metrics(self)
⋮----
rows = provider_capacities([{
⋮----
def test_health_history_supplies_smoothed_reliability(self)
⋮----
rows = provider_capacities(
⋮----
def test_explicit_reliability_overrides_health_history(self)
⋮----
def test_sparse_health_history_is_bayesian_smoothed(self)
⋮----
def test_health_history_supplies_observed_latency(self)
⋮----
def test_explicit_latency_overrides_health_history(self)
⋮----
def test_open_circuit_provider_is_excluded(self)
⋮----
report = allocate([{"id": "p", "requested_tokens": 100}], rows)
⋮----
def test_provider_returns_after_circuit_cooldown(self)
⋮----
def test_open_circuit_capacity_is_not_counted(self)
⋮----
report = allocate(
⋮----
def test_under_observed_peer_gets_bounded_exploration_bonus(self)
⋮----
order = report["projects"][0]["provider_order"]
⋮----
def test_exploration_never_bypasses_provider_tier(self)
⋮----
def test_zero_exploration_preserves_adaptive_ranking(self)
⋮----
def test_capacity_pressure_increases_scarce_capacity_share(self)
⋮----
providers = [ProviderCapacity("omniroute", 1000, unmetered=False)]
⋮----
def test_verified_efficiency_changes_scarce_capacity_share(self)
⋮----
def test_stagnation_throttle_reduces_capacity_share(self)
⋮----
def test_paused_stagnant_project_gets_zero_envelope(self)
⋮----
def test_recovery_project_receives_bounded_nonzero_envelope(self)
⋮----
providers = [ProviderCapacity("omniroute", 10000, unmetered=False)]
⋮----
def test_recovery_cap_applies_even_with_unmetered_provider(self)
⋮----
providers = [ProviderCapacity("local", None, unmetered=True)]
⋮----
row = report["projects"][0]
⋮----
def test_terminal_projects_are_excluded(self)
⋮----
providers = [ProviderCapacity("free", 10_000)]
⋮----
def test_parser_normalizes_provider_capacity_rows(self)
⋮----
rows = provider_capacities([
```

## File: test_checkout_credentials_policy.py
```python
class CheckoutCredentialsPolicyTests(unittest.TestCase)
⋮----
def test_checkout_persist_credentials_false_is_accepted(self)
⋮----
text=(
result=validate_step_inputs_env_text(text)
⋮----
def test_checkout_missing_persist_credentials_is_rejected(self)
⋮----
def test_checkout_persist_credentials_true_is_rejected(self)
⋮----
def test_checkout_extra_input_is_rejected(self)
```

## File: test_ci_adaptation.py
```python
class QueueAdaptationTests(unittest.TestCase)
⋮----
def test_unknown_future_stage_becomes_adaptation_request_not_success(self)
⋮----
root = Path(tmp)
queue = root / 'requests'
⋮----
request = queue / 'future.json'
⋮----
out = root / 'out'
⋮----
def payload(args)
⋮----
calls = []
def runner(args, timeout)
⋮----
project_out = Path(args[-1])
⋮----
capacity = {"projects": [{"id": "future", "admission": {"admitted": True, "action": "admit"}}]}
⋮----
queue_report = json.loads((out / 'queue.json').read_text())
project = queue_report['projects'][0]
⋮----
evolution = json.loads((out / 'future/evolution-request.json').read_text())
```

## File: test_ci_runner_admission.py
```python
class CiRunnerAdmissionTests(unittest.TestCase)
⋮----
def test_denied_project_never_creates_worker(self)
⋮----
projects = [
capacity_plan = {
⋮----
def fake_run(*args, **kwargs)
⋮----
code = ci_runner.run_queue(
report = __import__("json").loads(
⋮----
by_id = {row["id"]: row for row in report["projects"]}
⋮----
def test_missing_admission_decision_fails_open(self)
⋮----
projects = [{"id": "a", "file": "a.json"}]
⋮----
def test_preemption_lease_is_claimed_before_worker_and_released_after(self)
⋮----
projects = [{"id": "high", "file": "high.json"}]
⋮----
events = []
⋮----
def claim(*args, **kwargs)
⋮----
def run(*args, **kwargs)
⋮----
def release(*args, **kwargs)
⋮----
def test_failed_preemption_lease_claim_blocks_worker(self)
```

## File: test_ci.py
```python
def neutral_capacity_plan(projects)
⋮----
class ProviderTests(unittest.TestCase)
⋮----
def test_exactly_one_owner(self)
⋮----
p = Path(tmp) / 'ci.json'
⋮----
def test_invalid_policy_fails_closed(self)
⋮----
def test_non_main_rejected_before_provider_or_model_access(self)
⋮----
class QueueRunnerTests(unittest.TestCase)
⋮----
def setUp(self)
⋮----
def make_requests(self, root, count=2)
⋮----
queue = root / 'requests'
⋮----
def payload_for(self, args)
⋮----
def test_separate_artifacts_and_continue_after_one_preview_failure(self)
⋮----
root = Path(tmp)
queue = self.make_requests(root)
out = root / 'out'
calls = []
def runner(args, timeout)
⋮----
project_out = Path(args[-1])
⋮----
report = json.loads((out / 'queue.json').read_text())
⋮----
def test_preview_success_chains_every_stage_to_finished(self)
⋮----
queue = self.make_requests(root, 1)
⋮----
expected = ['studio/run.py', 'studio/post_preview.py', 'studio/device_stage.py',
⋮----
def test_security_failure_is_not_reported_as_complete(self)
⋮----
def test_entire_queue_validated_before_generation(self)
⋮----
def test_empty_queue_requires_no_credentials(self)
⋮----
def test_persistent_mode_uses_goal_wrapper(self)
⋮----
class RecoveryTests(unittest.TestCase)
⋮----
def make_queue(self, root)
⋮----
def test_timeout_preserves_progress_and_defers_remaining_work(self)
⋮----
queue = self.make_queue(root)
⋮----
def test_worker_launch_failure_is_reported(self)
⋮----
def runner(*args, **kwargs)
⋮----
text = (out / 'queue.json').read_text()
⋮----
def test_timeout_kills_group_and_only_removes_labeled_containers(self)
⋮----
process = Mock(pid=12345)
⋮----
run_id = popen.call_args.kwargs['env']['STUDIO_RUN_ID']
```

## File: test_codex_adapter.py
```python
ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
⋮----
class CodexAdapterTests(unittest.TestCase)
⋮----
def test_invocation_uses_headless_json_ephemeral_workspace_write_exec(self)
⋮----
def test_parse_usage_from_completed_turn(self)
⋮----
stdout = "\n".join(
⋮----
def test_parse_usage_is_backward_compatible_with_older_streams(self)
⋮----
stdout = '{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":4,"output_tokens":3}}'
⋮----
def test_parse_usage_ignores_malformed_and_unrelated_lines(self)
⋮----
def test_parse_usage_returns_none_without_completed_turn(self)
⋮----
def test_omniroute_invocation_uses_isolated_home_and_custom_responses_provider(self)
⋮----
provider_override = next(
⋮----
def test_omniroute_invocation_rejects_insecure_remote_http(self)
```

## File: test_codex_output_retention.py
```python
ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
⋮----
class CodexAdapterOutputRetentionTests(unittest.TestCase)
⋮----
def test_codex_terminal_usage_event_survives_large_trailing_output(self)
⋮----
completed = (
stdout = completed + "\n" + ("x" * 40000)
result = subprocess.CompletedProcess(
spec = AgentSpec(
⋮----
run = AgentAdapter(spec).run(
⋮----
usage = parse_codex_usage(run.stdout_tail)
```

## File: test_completion.py
```python
def preview_state()
⋮----
class CompletionTests(unittest.TestCase)
⋮----
def test_preview_is_not_misrepresented_as_finished(self)
⋮----
report = completion_report(preview_state())
⋮----
def test_scheduler_advances_in_strict_order(self)
⋮----
state = preview_state()
⋮----
def test_failed_stage_is_retried_not_skipped(self)
⋮----
def test_all_release_evidence_can_finish(self)
⋮----
report = apply_completion(state)
⋮----
def test_play_publish_is_required_only_when_explicitly_enabled(self)
⋮----
def test_missing_review_stays_blocked_even_with_release_evidence(self)
⋮----
def test_human_action_preserves_post_preview_next_stage(self)
⋮----
def test_unvalidated_app_returns_to_preview_stage(self)
```

## File: test_concurrent_state.py
```python
def _write_quick_cache(path, prefix, count)
⋮----
def _write_checkpoints(path, prefix, count)
⋮----
key = wc.operation_key("stress", {"prefix": prefix, "i": i})
⋮----
class ConcurrentStateTests(unittest.TestCase)
⋮----
def test_two_processes_do_not_lose_quick_cache_updates(self)
⋮----
path = Path(td) / "quick.json"
workers = [
⋮----
loaded = pqc.load()
⋮----
def test_two_processes_do_not_corrupt_checkpoint_store(self)
⋮----
path = Path(td) / "checkpoints.json"
⋮----
loaded = wc.load()
```

## File: test_contextual_routing_memory.py
```python
class ContextualRoutingMemoryTests(unittest.TestCase)
⋮----
def test_contextual_adjustment_requires_evidence(self)
⋮----
data = {"backend": {"provider:p": {"samples": 2, "successes": 2, "ema_success_rate": 1.0}}}
⋮----
def test_positive_context_history_adds_bonus(self)
⋮----
data = {"backend": {"provider:p": {"samples": 8, "successes": 7, "ema_success_rate": 0.9}}}
bonus = crm.contextual_adjustment(
⋮----
def test_negative_context_history_applies_larger_bounded_penalty(self)
⋮----
data = {"stack:rust": {"agent:a": {"samples": 8, "successes": 1, "ema_success_rate": 0.1}}}
penalty = crm.contextual_adjustment(
⋮----
def test_record_uses_ema(self)
⋮----
path = Path(td) / "memory.json"
⋮----
row = crm.load(path)["bugfix"]["provider:p"]
⋮----
def test_bandit_bonus_is_higher_with_less_evidence(self)
⋮----
sparse = {
dense = {
sparse_score = crm.contextual_bandit_score(
dense_score = crm.contextual_bandit_score(
⋮----
def test_architecture_hold_reduces_exploration(self)
⋮----
data = {
normal = crm.contextual_bandit_score(
risky = crm.contextual_bandit_score(
```

## File: test_contextual_strategy_efficiency.py
```python
class ContextualStrategyEfficiencyTests(unittest.TestCase)
⋮----
def test_contexts_learn_independently(self)
⋮----
path=Path(td)/"contextual.json"
⋮----
data=load(path)
⋮----
def test_weighted_blend_can_combine_bugfix_backend_and_tests(self)
⋮----
blended=blend_rows(data,[("bugfix",0.5),("backend",0.3),("tests",0.2)])
⋮----
def test_unknown_context_returns_empty_rows(self)
⋮----
def test_recent_success_is_tracked_per_context(self)
⋮----
row=rows_for(data,"bugfix")["model_only"]
```

## File: test_contextual_utility.py
```python
class ContextualUtilityTests(unittest.TestCase)
⋮----
def test_high_success_fast_free_is_positive(self)
⋮----
result = utility_score(
⋮----
def test_slow_low_success_is_penalized(self)
⋮----
def test_architecture_hold_reduces_utility(self)
⋮----
normal = utility_score(
hold = utility_score(
⋮----
def test_paid_provider_has_small_extra_cost(self)
⋮----
free = utility_score(
paid = utility_score(
```

## File: test_continuous_improvement.py
```python
def complete_goal(*,failures=None,history=None)
⋮----
state=new_goal("primary","Ship project",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
state=record_cycle(state,evidence={"project_completion":{"finished":True}})
state=finalize(state)
⋮----
# Rebuild through real cycles so integrity remains valid.
⋮----
state=record_cycle(state,failure=failure)
⋮----
state=record_cycle(state,missing_capability=capability)
# keep later cycles possible by resolving via a fresh state event contract is not required
# for assessment; repeated missing-capability evidence itself is what matters.
⋮----
# missing capabilities prevent completion, so history-only tests use direct sealed goal below.
⋮----
class ContinuousImprovementTests(unittest.TestCase)
⋮----
def test_active_primary_goal_defers_improvement(self)
⋮----
goal=new_goal("g","Work",[{"name":"done","required_evidence":["x"]}])
result=assess(goal,{})
⋮----
def test_repeated_failure_creates_high_priority_proof_gated_candidate(self)
⋮----
state=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
state=record_cycle(state,failure="flaky emulator")
⋮----
result=assess(state,{})
candidate=next_candidate(result)
⋮----
goal=improvement_goal(candidate)
⋮----
goal=record_cycle(goal,evidence={
⋮----
def test_single_failure_does_not_create_noise(self)
⋮----
state=record_cycle(state,failure="one-off")
state=record_cycle(state,evidence={"project_completion":True})
⋮----
def test_passed_stage_warning_creates_candidate(self)
⋮----
state=complete_goal()
project={
result=assess(state,project)
⋮----
def test_capability_churn_is_detected_from_history(self)
⋮----
state=record_cycle(state,missing_capability="billing_qa")
# resolve to permit another missing event and final completion
⋮----
state=resolve_capability(state,"billing_qa",{"validated":True})
⋮----
def test_candidate_id_is_deterministic(self)
⋮----
state=record_cycle(state,failure="repeat")
⋮----
a=next_candidate(assess(state,{}))
b=next_candidate(assess(state,{}))
```

## File: test_cost_drift.py
```python
class CostDriftDetectorTests(unittest.TestCase)
⋮----
def test_normal_phase_cost_keeps_execution(self)
⋮----
d = CostDriftDetector()
sample = d.record(phase="planning", expected_seconds=100, observed_seconds=120)
⋮----
def test_elevated_drift_reduces_exploration(self)
⋮----
sample = d.record(phase="implementation", expected_seconds=100, observed_seconds=160)
⋮----
def test_single_severe_drift_requests_replan(self)
⋮----
def test_multiple_severe_drifts_request_stop(self)
⋮----
def test_historical_baseline_overrides_fixed_ratio_threshold(self)
⋮----
baseline = {"samples": 10, "ema_seconds": 100.0, "ema_abs_deviation": 5.0}
sample = d.record(
⋮----
def test_historical_normal_range_is_not_flagged(self)
⋮----
baseline = {"samples": 10, "ema_seconds": 100.0, "ema_abs_deviation": 20.0}
⋮----
def test_snapshot_is_bounded(self)
```

## File: test_diagnostics.py
```python
class DiagnosticsTests(unittest.TestCase)
⋮----
def test_separates_code_environment_external_and_prerequisite(self)
⋮----
evidence = {
result = classify("performance_qa", evidence)
⋮----
def test_prefixed_runtime_failure_is_code_repairable(self)
```

## File: test_diff_quick_gates.py
```python
class DiffQuickGateTests(unittest.TestCase)
⋮----
def test_lib_change_skips_dependency_gate_and_targets_matching_test(self)
⋮----
root = Path(td)
test = root / "test/services/api_test.dart"
⋮----
result = plan(root, ["lib/services/api.dart"])
⋮----
def test_import_impact_selects_non_matching_test_name(self)
⋮----
test = root / "test/integration/network_flow_test.dart"
⋮----
def test_pubspec_change_requires_dependency_and_analyze_but_not_quick_tests(self)
⋮----
result = plan(Path(td), ["pubspec.yaml"])
⋮----
def test_asset_only_change_skips_all_quick_gates(self)
⋮----
result = plan(Path(td), ["assets/icon.svg"])
⋮----
def test_changed_test_targets_itself(self)
⋮----
test = root / "test/widget/foo_test.dart"
⋮----
result = plan(root, ["test/widget/foo_test.dart"])
```

## File: test_durable_state.py
```python
class DurableStateTests(unittest.TestCase)
⋮----
def test_roundtrip_and_checksum(self)
⋮----
path = Path(td) / "state.json"
value = {"status": "running", "counter": 2}
⋮----
def test_corruption_is_detected(self)
⋮----
payload = json.loads(path.read_text())
⋮----
def test_schema_one_is_migrated(self)
⋮----
value = {"status": "old"}
envelope = {
⋮----
loaded = ds.load(path)
⋮----
def test_backup_can_restore_corrupt_primary(self)
⋮----
root = Path(td)
primary = root / "state.json"
backup = root / "backup.json"
⋮----
restored = ds.repair_from_backup(primary, backup)
⋮----
def test_load_recovering_restores_last_verified_backup(self)
⋮----
loaded = ds.load_recovering(path)
```

## File: test_engine_entry.py
```python
SHA = 'a' * 40
CHECKPOINT = 'b' * 40
⋮----
class FakeGitHub
⋮----
def __init__(self, size=1, default_paths=None, checkpoint_paths=None)
def get(self, path)
⋮----
REQ = {'id':'demo-v1'}
⋮----
class EngineEntryTests(unittest.TestCase)
⋮----
def test_empty_repository_keeps_flutter_bootstrap(self)
⋮----
gh = FakeGitHub(size=0)
⋮----
def test_docs_only_repository_keeps_flutter_bootstrap(self)
⋮----
gh = FakeGitHub(default_paths=['README.md', '.gitignore'])
⋮----
def test_existing_flutter_marker(self)
⋮----
def test_existing_godot_marker(self)
⋮----
def test_ambiguous_markers_fail_closed(self)
⋮----
def test_checkpoint_branch_is_authoritative_for_resume(self)
⋮----
gh = FakeGitHub(default_paths=['pubspec.yaml'], checkpoint_paths=['project.godot','scripts/main.gd'])
⋮----
def test_existing_non_specialized_repository_uses_generic_engine(self)
```

## File: test_engine_patch.py
```python
class EnginePatchTests(unittest.TestCase)
⋮----
def test_flutter_scope_remains_compatible(self)
⋮----
result = validate({'files': [{'path': 'lib/app.dart', 'content': 'void main() {}'}]}, 'flutter')
⋮----
def test_godot_implementation_accepts_project_text_scope(self)
⋮----
result = validate({'files': [
⋮----
def test_godot_rejects_workflow_binary_and_traversal(self)
⋮----
def test_engine_specific_test_roles_are_enforced(self)
⋮----
def test_duplicate_empty_and_secret_content_fail_closed(self)
⋮----
def test_unknown_engine_and_role_fail_closed(self)
```

## File: test_evolution_automerge_orchestration.py
```python
class EvolutionAutoMergeOrchestrationTests(unittest.TestCase)
⋮----
def test_restarted_runner_merges_pending_promotion_without_regeneration(self)
⋮----
report={'completion':{'finished':False,'next_stage':'future_capability_qa'}}
⋮----
out=Path(tmp)
⋮----
result=run_registered_stages('request.json',out,tmp,report,100,lambda *a,**k:None,lambda:0,'a'*40)
⋮----
def test_restarted_runner_waits_without_regenerating_when_checks_are_running(self)
⋮----
result=run_registered_stages('request.json',Path(tmp),tmp,report,100,lambda *a,**k:None,lambda:0,'a'*40)
⋮----
def test_blocked_pending_proof_fails_closed_without_regeneration(self)
```

## File: test_evolution_automerge.py
```python
CANDIDATE='future-capability-qa-123456789abc'; GAP='future_capability_qa'; HEAD='b'*40
BRANCH=_branch_prefix(GAP,CANDIDATE)+HEAD
⋮----
def order(): return {'status':'candidate_planned','candidate_id':CANDIDATE,'primary_gap':{'value':GAP},'baseline_sha':'a'*40}
def persisted(): return {'status':'promotion_persisted','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12}
def pending(): return {'status':'promotion_pending_merge','candidate_id':CANDIDATE,'gap':GAP,'branch':BRANCH,'commit_sha':HEAD,'pull_request':12,'proof':'branch_name_sha_v1'}
def files(extra=None)
⋮----
names=set(expected_paths(GAP).values())|{'control/promoted_stages.json','control/evolution_rollbacks/'+CANDIDATE+'.json'}
⋮----
def check(name,status='completed',conclusion='success',slug='github-actions',details='https://github.com/owner/repo/actions/runs/123/job/4')
⋮----
def request_for(checks=None,head=HEAD,extra=None)
⋮----
def req(url,token,method='GET',payload=None,allow_404=False)
⋮----
class EvolutionAutoMergeTests(unittest.TestCase)
⋮----
def test_restarted_runner_can_merge_from_durable_proof_without_local_file(self)
⋮----
result=attempt(order(),None,'token','owner/repo')
⋮----
def test_local_proof_must_match_durable_proof(self)
⋮----
bad=dict(persisted(),commit_sha='c'*40)
⋮----
def test_changed_head_is_rejected(self)
⋮----
def test_spoofed_check_names_are_not_trusted(self)
⋮----
spoofed=[check('validate',slug='other-app'),check('mobile-smoke',slug='other-app')]
⋮----
def test_wrong_actions_repository_is_not_trusted(self)
⋮----
wrong=[check('validate',details='https://github.com/attacker/repo/actions/runs/1'),check('mobile-smoke',details='https://github.com/attacker/repo/actions/runs/2')]
⋮----
def test_extra_file_blocks_merge(self)
⋮----
def test_failed_trusted_check_blocks_merge(self)
⋮----
checks=[check('validate'),check('mobile-smoke',conclusion='failure')]
⋮----
def test_green_checks_merge_exact_encoded_sha(self)
⋮----
calls=[]
⋮----
result=attempt(order(),persisted(),'token','owner/repo')
⋮----
merge=[item for item in calls if item[0].endswith('/pulls/12/merge')][0]
```

## File: test_evolution_benchmark.py
```python
class EvolutionBenchmarkTests(unittest.TestCase)
⋮----
def order(self)
⋮----
def result(self, sha, count=140)
⋮----
def test_approves_only_non_regressing_candidate(self)
⋮----
decision = evaluate(self.order(), self.result('a' * 40, 140), self.result('b' * 40, 145))
⋮----
def test_protected_contract_drift_rejects_promotion(self)
⋮----
baseline = self.result('a' * 40); candidate = self.result('b' * 40); candidate['protected_hashes']['studio/completion.py'] = '9' * 64
decision = evaluate(self.order(), baseline, candidate)
⋮----
def test_losing_existing_tests_is_a_regression(self)
⋮----
decision = evaluate(self.order(), self.result('a' * 40, 150), self.result('b' * 40, 149))
⋮----
def test_capability_benchmark_is_mandatory(self)
⋮----
baseline = self.result('a' * 40); candidate = self.result('b' * 40); candidate['capability_benchmark']['passed'] = False; candidate['capability_benchmark']['assertions_passed'] = 3
⋮----
def test_baseline_and_unknown_gate_fail_closed(self)
⋮----
order = self.order(); order['promotion_gates'].append('skip_security_for_speed')
```

## File: test_evolution_candidate.py
```python
class EvolutionCandidateTests(unittest.TestCase)
⋮----
def work_order(self): return {'status':'candidate_planned','candidate_id':'billing-qa-abc123def456','candidate_branch':'evolution/billing-qa-abc123def456','baseline_sha':'a'*40,'primary_gap':{'kind':'missing_stage_executor','value':'billing_qa','reason':'missing trusted billing QA'}}
def research(self): return {'status':'research_complete','candidate_id':'billing-qa-abc123def456','items':[]}
def candidate(self)
⋮----
benchmark=json.dumps({'version':1,'id':'billing-qa-core','gap':'billing_qa','purpose':'Prove the new billing QA fails closed without verified purchase evidence.','assertions':['stage requires trusted billing evidence','unavailable Play test environment cannot be reported as success']})
⋮----
def test_accepts_only_complete_scoped_candidate(self)
⋮----
result=validate_candidate(self.work_order(),self.research(),self.candidate()); self.assertEqual(result['status'],'candidate_validated'); self.assertEqual(result['benchmark_assertions'],2); self.assertEqual(result['differential_tests'],2); self.assertEqual(set(expected_paths('billing_qa').values()),{f['path'] for f in result['files']})
def test_completion_registry_smoke_and_evolution_judges_are_protected(self)
⋮----
candidate=self.candidate(); candidate['files'][0]['path']='studio/completion.py'
⋮----
def test_missing_test_or_benchmark_is_rejected(self)
⋮----
candidate=self.candidate(); candidate['files']=[item for item in candidate['files'] if item['path']!=path]
⋮----
def test_test_count_must_match_benchmark_assertions(self)
⋮----
candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nclass BillingCandidateTests(unittest.TestCase):\n    def test_only_one(self):\n        self.assertTrue(True)\n'
⋮----
def test_skipped_tests_are_rejected(self)
⋮----
candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nclass BillingCandidateTests(unittest.TestCase):\n    @unittest.skip("no")\n    def test_one(self):\n        pass\n    def test_two(self):\n        pass\n'
⋮----
def test_candidate_module_cannot_be_imported_at_collection_time(self)
⋮----
candidate=self.candidate(); candidate['files'][2]['content']='import unittest\nfrom billing_qa import validate_billing\nclass BillingCandidateTests(unittest.TestCase):\n    def test_one(self): self.assertTrue(True)\n    def test_two(self): self.assertTrue(True)\n'
⋮----
def test_shell_true_eval_and_secret_are_rejected(self)
⋮----
candidate=self.candidate(); candidate['files'][0]['content']=bad
```

## File: test_evolution_differential.py
```python
class EvolutionDifferentialTests(unittest.TestCase)
⋮----
def order(self): return {'status':'candidate_planned','candidate_id':'future-capability-abc123','baseline_sha':'a'*40,'primary_gap':{'value':'future_capability_qa'},'promotion_gates':list(PROMOTION_GATES)}
def validated(self): return {'status':'candidate_validated','candidate_id':'future-capability-abc123','files':[{'path':'studio/future_capability_qa.py','content':'pass\n'},{'path':'studio/future_capability_stage.py','content':'pass\n'},{'path':'tests/test_future_capability_qa.py','content':'pass\n'},{'path':'tests/benchmarks/future_capability_qa.json','content':'{}'}]}
def diff_result(self,sha,failures=0,errors=0,passed=True): return {'commit_sha':sha,'test_file':'tests/test_future_capability_qa.py','tests_collected':3,'failures':failures,'errors':errors,'passed':passed}
def benchmark_result(self,sha): return {'version':1,'commit_sha':sha,'compile_passed':True,'unit_tests':{'passed':True,'count':170,'failures':0,'errors':0},'flutter_smoke_passed':True,'protected_hashes':{'studio/core.py':'1'*64,'studio/completion.py':'2'*64},'capability_benchmark':{'gap':'future_capability_qa','passed':True,'assertions_total':3,'assertions_passed':3},'reversible':True}
def test_promotion_contract_requires_every_candidate_test_red_then_green(self)
⋮----
self.assertIn('differential_improvement_proved',PROMOTION_GATES); proof=evaluate(self.order(),self.validated(),self.diff_result('a'*40,failures=3,passed=False),self.diff_result('b'*40)); decision=evaluate_promotion(self.order(),self.benchmark_result('a'*40),self.benchmark_result('b'*40),proof); self.assertEqual(decision['promotion_decision'],'approve'); self.assertTrue(decision['gates']['differential_improvement_proved'])
def test_partially_red_baseline_blocks_promotion(self)
⋮----
proof=evaluate(self.order(),self.validated(),self.diff_result('a'*40,failures=1,passed=False),self.diff_result('b'*40)); self.assertFalse(proof['improvement_proved']); self.assertIn('not_every_candidate_test_failed_on_baseline',proof['blockers']); decision=evaluate_promotion(self.order(),self.benchmark_result('a'*40),self.benchmark_result('b'*40),proof); self.assertEqual(decision['promotion_decision'],'reject')
def test_trivial_baseline_green_test_blocks_promotion(self)
⋮----
proof=evaluate(self.order(),self.validated(),self.diff_result('a'*40),self.diff_result('b'*40)); decision=evaluate_promotion(self.order(),self.benchmark_result('a'*40),self.benchmark_result('b'*40),proof); self.assertEqual(decision['promotion_decision'],'reject'); self.assertIn('differential_improvement_not_proved',decision['blockers'])
def test_missing_differential_proof_blocks_promotion(self)
⋮----
decision=evaluate_promotion(self.order(),self.benchmark_result('a'*40),self.benchmark_result('b'*40)); self.assertEqual(decision['promotion_decision'],'reject'); self.assertFalse(decision['gates']['differential_improvement_proved'])
def test_pinned_baseline_is_required(self)
```

## File: test_evolution_evidence.py
```python
class EvolutionEvidenceTests(unittest.TestCase)
⋮----
def work_order(self)
⋮----
def evidence(self)
⋮----
def test_accepts_complete_allowlisted_evidence(self)
⋮----
result = validate_evidence(self.work_order(), self.evidence())
⋮----
def test_rejects_non_official_docs_domain(self)
⋮----
evidence = self.evidence()
⋮----
def test_rejects_missing_task(self)
⋮----
def test_rejects_candidate_mismatch(self)
⋮----
def test_rejects_arbitrary_device_identifier(self)
```

## File: test_evolution_executor.py
```python
class EvolutionExecutorTests(unittest.TestCase)
⋮----
def request(self)
⋮----
def test_builds_deterministic_isolated_candidate(self)
⋮----
order = build_work_order(self.request(), 'a' * 40)
⋮----
def test_rejects_weakened_promotion_gate(self)
⋮----
request = self.request()
⋮----
def test_rejects_unreviewed_external_execution_policy(self)
⋮----
def test_rejects_unknown_resource_kind(self)
⋮----
def test_consume_writes_machine_readable_work_order(self)
⋮----
root = Path(tmp)
source = root / 'evolution-request.json'
⋮----
result = consume(source, root / 'out', 'b' * 40)
written = json.loads((root / 'out/evolution-work-order.json').read_text())
```

## File: test_evolution_isolated_runner.py
```python
class IsolatedEvolutionRunnerTests(unittest.TestCase)
⋮----
def test_unittest_parser_requires_real_collected_tests(self)
⋮----
passed = _parse_unittest('Ran 3 tests in 0.01s\n\nOK\n', 0)
⋮----
empty = _parse_unittest('OK\n', 0)
⋮----
failed = _parse_unittest('Ran 3 tests in 0.01s\nFAILED (failures=1, errors=1)\n', 1)
⋮----
@patch('evolution_isolated_runner.shutil.which', return_value='/usr/bin/docker')
@patch('evolution_isolated_runner._run')
    def test_candidate_python_runs_without_network_or_writable_repo(self, run, which)
⋮----
root = Path('/tmp/candidate')
⋮----
command = run.call_args.args[0]
⋮----
mount = command[command.index('-v') + 1]
⋮----
joined = ' '.join(command)
⋮----
@patch('evolution_isolated_runner._run')
    def test_trusted_smoke_uses_unique_scrubbed_root(self, run)
⋮----
smoke_root = Path('/tmp/evolution-smoke-never-created')
⋮----
env = run.call_args.kwargs['env']
⋮----
def test_capability_evidence_is_counted_not_invented(self)
⋮----
failed = _capability_result('future_qa', 4, False)
⋮----
passed = _capability_result('future_qa', 4, True)
⋮----
@patch('evolution_isolated_runner.shutil.which', return_value=None)
    def test_missing_docker_fails_closed(self, which)
```

## File: test_evolution_pending.py
```python
CANDIDATE='future-capability-qa-123456789abc'; GAP='future_capability_qa'; BASELINE='a'*40; COMMIT='b'*40
⋮----
def order(): return {'status':'candidate_planned','candidate_id':CANDIDATE,'baseline_sha':BASELINE,'primary_gap':{'value':GAP}}
def branch(): return _branch_prefix(GAP,CANDIDATE)+COMMIT
def pr(state='open',merged_at=None,sha=COMMIT,ref=None,number=9)
⋮----
class EvolutionPendingTests(unittest.TestCase)
⋮----
def test_no_pr_and_no_branch_allows_new_evolution(self)
⋮----
def request(url,token,method='GET',payload=None,allow_404=False)
with patch('evolution_pending._request',side_effect=request): result=check(order(),'token','owner/repo')
⋮----
def test_open_pr_recovers_branch_name_sha_proof(self)
⋮----
def test_force_moved_branch_is_orphaned(self)
⋮----
def test_pr_head_not_equal_encoded_sha_is_orphaned(self)
⋮----
result=check(order(),'token','owner/repo')
⋮----
def test_multiple_candidate_prs_fail_closed(self)
⋮----
def test_merged_pr_survives_deleted_branch(self)
⋮----
def test_orchestrator_maps_open_pr_to_pending_merge(self)
⋮----
out=Path(tmp); (out/'evolution-work-order.json').write_text(json.dumps(order()))
def runner(args,timeout)
with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'github'},clear=True): status=_run_adaptation_pending(out,100,runner,lambda:0)
```

## File: test_evolution_persist.py
```python
BASELINE='a'*40; CANDIDATE_SHA='b'*40; COMMIT='c'*40; CANDIDATE='candidate-12345678'; GAP='future_capability_qa'
⋮----
class EvolutionPersistTests(unittest.TestCase)
⋮----
def fixture(self,root)
⋮----
candidate_files={'studio/future_capability_stage.py':'stage-fixture','studio/future_capability_qa.py':'implementation-fixture','tests/test_future_capability_qa.py':'tests-fixture','tests/benchmarks/future_capability_qa.json':'benchmark-fixture'}
⋮----
path=root/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content)
registry=root/'control/promoted_stages.json'; registry.parent.mkdir(parents=True,exist_ok=True)
⋮----
rollback=root/'control/evolution_rollbacks'/(CANDIDATE+'.json'); rollback.parent.mkdir(parents=True,exist_ok=True)
⋮----
def api(self,existing=False,moved=False,different_tree=False)
⋮----
blobs={'n':0}; branch=_branch_prefix(GAP,CANDIDATE)+COMMIT
def request(url,token,method='GET',payload=None,allow_404=False)
⋮----
def test_new_branch_encodes_exact_approved_commit_sha(self)
⋮----
root=Path(tmp); applied=self.fixture(root); request,branch=self.api()
with patch('evolution_persist._request',side_effect=request): result=persist(root,applied,'token','owner/repo',BASELINE)
⋮----
def test_existing_identical_content_bound_branch_is_idempotent(self)
⋮----
root=Path(tmp); applied=self.fixture(root); request,branch=self.api(existing=True)
⋮----
def test_force_moved_existing_branch_is_rejected(self)
⋮----
root=Path(tmp); applied=self.fixture(root); request,_=self.api(existing=True,moved=True)
⋮----
def test_existing_branch_with_different_tree_is_rejected(self)
⋮----
root=Path(tmp); applied=self.fixture(root); request,_=self.api(existing=True,different_tree=True)
⋮----
def test_modified_promoted_file_is_rejected_before_network(self)
⋮----
root=Path(tmp); applied=self.fixture(root); (root/'studio/future_capability_qa.py').write_text('tampered')
⋮----
def test_github_orchestrator_requires_persistence_evidence(self)
⋮----
out=Path(tmp); (out/'evolution-applied.json').write_text(json.dumps({'status':'promoted','candidate_id':CANDIDATE,'gap':GAP,'candidate_sha':CANDIDATE_SHA}))
calls=[]
def runner(args,timeout)
with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'github'},clear=True): status=_run_adaptation_persistence(out,100,runner,lambda:0)
⋮----
def test_non_github_provider_does_not_attempt_github_persistence(self)
⋮----
with patch.dict('os.environ',{'STUDIO_CI_PROVIDER':'circleci'},clear=True): status=_run_adaptation_persistence(Path(tmp),100,lambda args,timeout:calls.append(args),lambda:0)
```

## File: test_evolution_promotion.py
```python
class EvolutionPromotionTests(unittest.TestCase)
⋮----
def test_fake_approval_cannot_install_files(self)
⋮----
root = Path(tmp)
order = {'status': 'candidate_planned', 'candidate_id': 'candidate-1', 'baseline_sha': 'a' * 40,
candidate = {'status': 'candidate_validated', 'candidate_id': 'candidate-1', 'gap': 'future_capability_qa',
benchmark = {'status': 'isolated_benchmark_complete', 'candidate_id': 'candidate-1', 'baseline_sha': 'a' * 40}
promotion = {'status': 'promotion_approved', 'promotion_decision': 'approve', 'candidate_id': 'candidate-1'}
⋮----
def test_promoted_registry_is_strict_and_dynamic(self)
⋮----
registry = Path(tmp) / 'promoted_stages.json'
⋮----
stage = get_stage('future_capability_qa')
⋮----
def test_registry_script_cannot_redirect_execution(self)
```

## File: test_evolution_research.py
```python
class FakeFetch
⋮----
def __init__(self)
⋮----
def __call__(self, url, **kwargs)
⋮----
headers = {'date': 'Mon, 08 Sep 2026 20:00:00 GMT', 'etag': '"rev-1"'}
⋮----
payload = {'latest': {'version': '4.0.0', 'published': '2026-08-20T10:00:00Z',
⋮----
payload = {'html_url': 'https://github.com/flutter/packages', 'pushed_at': '2026-09-01T12:00:00Z',
⋮----
payload = {'items': [{'html_url': 'https://github.com/flutter/packages',
⋮----
class EvolutionResearchTests(unittest.TestCase)
⋮----
def work_order(self)
⋮----
def test_executes_known_research_without_external_code_execution(self)
⋮----
fetch = FakeFetch()
⋮----
out = Path(tmp)
result = execute(self.work_order(), out, fetch)
⋮----
package = result['items'][1]
⋮----
provenance = json.loads((out / 'evolution-research-provenance.json').read_text())
⋮----
def test_unknown_official_mapping_fails_closed(self)
⋮----
task = {'id': 'research-1', 'kind': 'official_docs', 'query': 'unknown quantum sensor SDK'}
⋮----
def test_network_url_rejects_non_allowlisted_host_and_nonstandard_port(self)
⋮----
def test_v2_evidence_requires_content_hash(self)
⋮----
order = {'candidate_id': 'x', 'research_tasks': [{'id': 'research-1', 'kind': 'official_docs'}]}
evidence = {'version': 2, 'candidate_id': 'x', 'items': [{
```

## File: test_evolution_rollback.py
```python
class EvolutionRollbackTests(unittest.TestCase)
⋮----
def make_promoted(self, root)
⋮----
candidate_id = 'candidate-1'
gap = 'future_capability_qa'
baseline = 'a' * 40
candidate = 'b' * 40
paths = [
contents = {path: 'content:' + path for path in paths}
⋮----
target = root / path
⋮----
previous = {'version': 1, 'stages': {'existing_qa': {
registry = {'version': 1, 'stages': dict(previous['stages'])}
⋮----
registry_path = root / 'control/promoted_stages.json'
⋮----
previous_text = canonical(previous) + '\n'
record = {
record_path = root / 'control/evolution_rollbacks' / (candidate_id + '.json')
⋮----
def test_rollback_restores_registry_and_removes_only_promoted_files(self)
⋮----
root = Path(tmp)
⋮----
unrelated = root / 'studio/unrelated.py'
⋮----
result = rollback(root, candidate_id)
⋮----
def test_changed_promoted_file_blocks_entire_rollback(self)
⋮----
registry_before = (root / 'control/promoted_stages.json').read_text()
⋮----
def test_registry_identity_mismatch_blocks_rollback(self)
⋮----
registry = json.loads(registry_path.read_text())
```

## File: test_evolution_stage_runner.py
```python
class PromotedStageRunnerTests(unittest.TestCase)
⋮----
def test_scrubs_tokens_keys_and_secrets(self)
⋮----
env = scrubbed_env({
⋮----
def test_rejects_paths_outside_stage_scope(self)
```

## File: test_evolution_synthesis.py
```python
class FakeAPI
⋮----
base='https://example.invalid/v1'
def __init__(self,payload): self.payload=payload; self.calls=[]
def call(self,method,path,data=None): self.calls.append((method,path,data)); return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.payload)}}]}
class EvolutionSynthesisTests(unittest.TestCase)
⋮----
def order(self): return {'status':'candidate_planned','candidate_id':'future-qa-abc123def456','candidate_branch':'evolution/future-qa-abc123def456','baseline_sha':'a'*40,'primary_gap':{'kind':'missing_stage_executor','value':'future_qa','reason':'missing trusted stage'}}
def research(self): return {'status':'research_complete','candidate_id':'future-qa-abc123def456','items':[]}
def candidate(self)
⋮----
benchmark=json.dumps({'version':1,'id':'future-qa-core','gap':'future_qa','purpose':'Prove fail-closed evidence validation.','assertions':['missing evidence fails','valid evidence passes']})
⋮----
def test_validated_model_output_is_persisted(self)
⋮----
root=Path(tmp); order=root/'order.json'; order.write_text(json.dumps(self.order())); research=root/'research.json'; research.write_text(json.dumps(self.research())); api=FakeAPI(self.candidate()); result=consume(order,research,root/'out',api=api,model='test-model'); self.assertEqual(result['status'],'candidate_validated'); self.assertEqual(result['benchmark_assertions'],2); self.assertEqual(result['differential_tests'],2); self.assertTrue((root/'out/evolution-candidate.json').is_file()); self.assertEqual(api.calls[0][0:2],('POST','/chat/completions'))
def test_model_cannot_escape_candidate_scope(self)
⋮----
candidate=self.candidate(); candidate['files'][0]['path']='studio/core.py'
⋮----
def test_research_is_required_before_model_call(self)
⋮----
api=FakeAPI(self.candidate())
```

## File: test_execution_budget.py
```python
class ExecutionBudgetTests(unittest.TestCase)
⋮----
def test_normal_budget_allows_two_passes_and_two_agents(self)
⋮----
budget = choose_budget(
⋮----
def test_deadline_guard_collapses_exploration(self)
⋮----
def test_recent_success_reduces_new_work(self)
⋮----
def test_predictive_inputs_bound_normal_budget(self)
⋮----
def test_bootstrap_failure_prioritizes_recovery(self)
```

## File: test_execution_checkpoint.py
```python
class ExecutionCheckpointTests(unittest.TestCase)
⋮----
def test_round_and_verification_resume_from_published_commit(self)
⋮----
path = Path(td) / "checkpoint.json"
checkpoint = new("demo", "generic", "a" * 40)
checkpoint = advance(
⋮----
restored = load(path)
⋮----
def test_tampering_is_rejected(self)
⋮----
value = json.loads(path.read_text())
⋮----
def test_round_cannot_regress(self)
⋮----
checkpoint = advance(checkpoint, round_index=4, phase="published")
```

## File: test_existing_project.py
```python
SHA='a'*40
⋮----
def item(path,size=3,mode='100644',kind='blob',sha=SHA): return {'path':path,'size':size,'mode':mode,'type':kind,'sha':sha}
⋮----
class ExistingProjectTests(unittest.TestCase)
⋮----
def test_plans_existing_godot_project_without_workflow_or_binary_assets(self)
⋮----
tree={'truncated':False,'tree':[item('project.godot'),item('scripts/player.gd'),item('scenes/Main.tscn'),item('README.md'),item('SETUP_REQUIRED.txt'),item('.github/workflows/validate.yml'),item('assets/sprite.png',size=100)]}
result=plan(tree,'godot'); paths={entry['path'] for entry in result['files']}
⋮----
def test_engine_mismatch_and_ambiguous_markers_fail_closed(self)
def test_rejects_symlink_mode_large_file_and_truncated_tree(self)
def test_materialize_validates_all_blobs_before_writing(self)
⋮----
import_plan={'engine':'godot','files':[{'path':'project.godot','sha':'a'*40,'size':3},{'path':'scripts/player.gd','sha':'b'*40,'size':4}]}
def fetch(sha)
⋮----
raw=b'abc' if sha.startswith('a') else b'xx'; return {'encoding':'base64','content':base64.b64encode(raw).decode()}
⋮----
root=Path(tmp)
⋮----
def test_materialize_writes_valid_utf8_snapshot(self)
⋮----
payloads={'a'*40:b'[application]\n','b'*40:b'extends Node\n'}
import_plan={'engine':'godot','files':[{'path':'project.godot','sha':'a'*40,'size':len(payloads['a'*40])},{'path':'scripts/player.gd','sha':'b'*40,'size':len(payloads['b'*40])}]}
def fetch(sha): return {'encoding':'base64','content':base64.b64encode(payloads[sha]).decode()}
⋮----
root=Path(tmp); materialize(root,import_plan,fetch); self.assertEqual((root/'project.godot').read_text(),'[application]\n'); self.assertEqual((root/'scripts/player.gd').read_text(),'extends Node\n')
```

## File: test_file_lock.py
```python
def _hold_lock(path)
⋮----
class FileLockTests(unittest.TestCase)
⋮----
def test_lock_timeout_prevents_indefinite_deadlock(self)
⋮----
path = Path(td) / "state.json"
holder = multiprocessing.Process(target=_hold_lock, args=(str(path),))
⋮----
def test_lock_releases_after_owner_exits(self)
```

## File: test_fleet_capacity.py
```python
class FleetCapacityTests(unittest.TestCase)
⋮----
def test_project_demand_uses_explicit_capacity_request(self)
⋮----
rows = fleet_capacity._project_rows(Path("out"), Path("requests"))
⋮----
def test_project_demand_uses_configured_call_upper_bound(self)
⋮----
def test_known_monthly_quota_is_reported_as_remaining_capacity(self)
⋮----
provider = ProviderSpec(
quota_data = {
⋮----
providers = fleet_capacity._provider_rows()
⋮----
def test_provider_capacity_subtracts_inflight_reservations(self)
⋮----
providers = fleet_capacity._provider_rows(
⋮----
def test_project_pressure_uses_committed_tokens_against_previous_envelope(self)
⋮----
previous = {
usage = {
⋮----
rows = fleet_capacity._project_rows(
⋮----
def test_explicit_fleet_quota_path_is_used_for_provider_capacity(self)
⋮----
quota_path = Path(td) / "provider-monthly-quota.json"
⋮----
providers = fleet_capacity._provider_rows(quota_path=quota_path)
⋮----
def test_project_rows_include_verified_efficiency_multiplier(self)
⋮----
efficiency = {
⋮----
by_id = {row["id"]: row for row in rows}
⋮----
def test_project_rows_apply_stagnation_pause_and_throttle(self)
⋮----
stagnation = {
⋮----
def test_paused_project_gets_bounded_recovery_after_context_change(self)
⋮----
recovery_path = Path(td) / "recovery.json"
first = fleet_capacity._project_rows(
⋮----
second = fleet_capacity._project_rows(
⋮----
def test_capacity_band_ignores_small_quota_drift(self)
⋮----
def test_persist_writes_machine_readable_plan(self)
⋮----
report = {
⋮----
root = Path(td)
result = fleet_capacity.persist(root, "requests")
target = root / "capacity-plan.json"
```

## File: test_fleet_daemon.py
```python
class FleetDaemonTests(unittest.TestCase)
⋮----
def test_tick_suppresses_restarts_when_regression_detected(self)
⋮----
report = fleet_daemon.tick("out", "requests", apply_restarts=True, max_restarts=2)
⋮----
def test_tick_allows_bounded_restarts_without_regression(self)
⋮----
report = fleet_daemon.tick("out", "requests", apply_restarts=True, max_restarts=1)
⋮----
def test_tick_persists_capacity_plan(self)
⋮----
report = fleet_daemon.tick("out", "requests")
⋮----
def test_tick_applies_preemption_then_replans_capacity(self)
⋮----
plans = [
⋮----
report = fleet_daemon.tick("out", "requests", apply_preemptions=True)
⋮----
def test_run_loop_enforces_minimum_interval(self)
⋮----
sleeps = []
⋮----
rows = fleet_daemon.run_loop(
```

## File: test_fleet_maintenance.py
```python
class FleetMaintenanceTests(unittest.TestCase)
⋮----
def test_removes_only_known_temporary_files(self)
⋮----
project = Path(td) / "demo"
autonomy = project / ".autonomy"
⋮----
report = fleet_maintenance.maintain_project(project)
⋮----
def test_run_ignores_non_project_directories(self)
⋮----
root = Path(td)
⋮----
report = fleet_maintenance.run(root)
```

## File: test_fleet_metrics.py
```python
class FleetMetricsTests(unittest.TestCase)
⋮----
def test_snapshot_aggregates_operational_totals(self)
⋮----
dashboard = {
⋮----
row = fleet_metrics.snapshot("ignored", ts=100.0)
⋮----
def test_history_is_bounded(self)
⋮----
path = Path(td) / "metrics.json"
⋮----
rows = fleet_metrics.load(path)
⋮----
def test_regression_detects_health_drop_and_lease_spike(self)
⋮----
result = fleet_regression.compare(
⋮----
def test_insufficient_history_is_not_a_regression(self)
⋮----
result = fleet_regression.evaluate(path)
```

## File: test_fleet_operations.py
```python
class FleetOperationsTests(unittest.TestCase)
⋮----
def test_dashboard_aggregates_projects(self)
⋮----
root = Path(td)
⋮----
reports = {
⋮----
report = fleet_dashboard.collect(root)
⋮----
def test_supervisor_quarantines_state_integrity_failures(self)
⋮----
dashboard = {
⋮----
report = fleet_supervisor.plan("ignored")
⋮----
actions = {row["id"]: row["action"] for row in report["actions"]}
```

## File: test_fleet_supervisor_apply.py
```python
class FleetSupervisorApplyTests(unittest.TestCase)
⋮----
def _projects(self)
⋮----
def test_dry_run_never_executes_restart(self)
⋮----
decisions = {
⋮----
report = fsa.execute("out", "requests", apply=False)
⋮----
statuses = {row["id"]: row["status"] for row in report["results"]}
⋮----
def test_apply_executes_only_restartable_projects_with_budget(self)
⋮----
def fake_run(project, project_out, work, runner, deadline, clock, baseline_sha)
⋮----
report = fsa.execute(
⋮----
def test_admission_denial_blocks_supervisor_restart(self)
⋮----
decisions = {"actions": [{"id": "a", "action": "restart"}]}
denied = {
⋮----
report = fsa.execute("out", "requests", apply=True)
⋮----
def test_missing_request_is_not_executed(self)
⋮----
decisions = {"actions": [{"id": "missing", "action": "restart"}]}
```

## File: test_free_capacity_recommendations.py
```python
class FreeCapacityRecommendationsTests(unittest.TestCase)
⋮----
def test_preferred_self_hosted_capacity_sources_rank_first(self)
⋮----
fake = {
⋮----
result = fcr.discover(Path(td))
⋮----
def test_policy_does_not_assume_external_unlimited_quota(self)
```

## File: test_full_gate_cache.py
```python
class FullGateCacheTests(unittest.TestCase)
⋮----
def _root(self, td)
⋮----
root = Path(td)
⋮----
def test_identical_inputs_produce_identical_key(self)
⋮----
root = self._root(td)
journeys = [{
first = validation_key(root, app_name="demo_app", journeys=journeys)
second = validation_key(root, app_name="demo_app", journeys=journeys)
⋮----
def test_journey_change_invalidates_key(self)
⋮----
first = validation_key(
second = validation_key(
⋮----
def test_native_change_invalidates_key(self)
⋮----
def test_editable_source_change_invalidates_key(self)
```

## File: test_generic_adaptive_review_wiring.py
```python
ROOT = Path(__file__).resolve().parents[1]
GENERIC_PROJECT = ROOT / "studio" / "generic_project.py"
⋮----
class GenericAdaptiveReviewWiringTests(unittest.TestCase)
⋮----
def test_generic_runtime_wires_allocator_review_requirement_into_phase_policy(self)
⋮----
source = GENERIC_PROJECT.read_text(encoding="utf-8")
tree = ast.parse(source)
⋮----
imported = any(
⋮----
fail_closed_default = any(
⋮----
allocator_override = any(
⋮----
policy_calls = [
⋮----
keywords = {item.arg: item.value for item in policy_calls[0].keywords if item.arg}
```

## File: test_generic_architecture.py
```python
class GenericArchitectureTests(unittest.TestCase)
⋮----
def test_prepare_architecture_is_generic_and_advisory(self)
⋮----
state = {"engine": "generic", "toolchain": "python"}
req = {
recommendations = {"matches": [{"repo": "a/core", "score": 90.0}]}
decision = {
⋮----
root = gp._prepare_architecture(req, Path(td) / "project", state)
⋮----
def test_record_architecture_writes_full_evidence_chain(self)
⋮----
state = {
evaluation = {"status": "evaluated", "verdict": "retain"}
benchmark = {"status": "benchmarked", "migration_candidates": []}
learning = {"schema": 1, "rankings": []}
⋮----
out = Path(td) / "project"
⋮----
def test_learning_failure_is_non_fatal_after_verified_round(self)
```

## File: test_generic_capability_candidate_persistence.py
```python
class GenericCapabilityCandidatePersistenceTests(unittest.TestCase)
⋮----
def envelope(self)
⋮----
candidate={
digest=hashlib.sha256(json.dumps(candidate,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
⋮----
def test_candidate_envelope_integrity(self)
⋮----
value=self.envelope()
⋮----
def test_tampering_is_rejected(self)
```

## File: test_generic_capability_isolated_validation.py
```python
def envelope()
⋮----
candidate={
digest=hashlib.sha256(json.dumps(candidate,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
⋮----
class GenericCapabilityIsolatedValidationTests(unittest.TestCase)
⋮----
@patch("studio.generic_capability_isolated_validation._docker")
    def test_passed_isolation_makes_candidate_eligible_only(self,docker)
⋮----
result=validate_in_isolation(envelope())
⋮----
def test_forbidden_import_fails_before_execution(self)
⋮----
value=envelope()
```

## File: test_generic_capability_persist.py
```python
class FakeGitHub
⋮----
def __init__(self)
⋮----
def get(self,path)
⋮----
prefix="refs/heads/"+path.split("/git/matching-refs/heads/",1)[1]
⋮----
def call(self,method,path,payload=None)
⋮----
sha="3"*40
⋮----
sha="4"*40
⋮----
pr={"number":7,"head":{"ref":payload["head"],"sha":"4"*40}}
⋮----
def candidate()
⋮----
def validation()
⋮----
def handoff()
⋮----
class GenericCapabilityPersistTests(unittest.TestCase)
⋮----
@patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_persists_only_candidate_provider_test_and_evidence(self,_validation,_candidate)
⋮----
gh=FakeGitHub()
result=persist(gh,candidate(),validation(),handoff(),"1"*40)
⋮----
tree_call=next(x for x in gh.calls if x[1].endswith("/git/trees"))
paths={x["path"] for x in tree_call[2]["tree"]}
⋮----
@patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_cross_candidate_validation_fails_closed(self,_validation,_candidate)
⋮----
gh=FakeGitHub(); bad=validation(); bad["candidate_id"]="other"
⋮----
@patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_existing_target_path_fails_closed(self,_validation,_candidate)
⋮----
@patch("studio.generic_capability_persist.validate_candidate_envelope",side_effect=lambda x:x)
@patch("studio.generic_capability_persist.validate_isolated_validation_result",side_effect=lambda x:x)
    def test_existing_branch_must_match_content_and_parent(self,_validation,_candidate)
⋮----
prefix=_prefix("image_assets","capability-candidate:image_assets:abc")
```

## File: test_generic_capability_synthesis_state.py
```python
class GenericCapabilitySynthesisStateTests(unittest.TestCase)
⋮----
def test_synthesis_advances_only_after_research(self)
⋮----
state=new_state("project-a","improvement.apply.repeated_failure","improvement:abc")
state=record_research(state,"research_complete")
state=record_synthesis(state,"a"*64)
⋮----
def test_synthesis_before_research_fails_closed(self)
```

## File: test_generic_capability_validation_report.py
```python
def seal(value)
⋮----
def report()
⋮----
sha="a"*64
candidate_id="capability-candidate:test:1234"
⋮----
def proof(kind, **extra)
⋮----
value={"kind":kind,"candidate_sha256":sha,"passed":True,**extra}
⋮----
targeted=proof("targeted_test",tests_collected=1,compile_passed=True)
benchmark=proof("benchmark",score=1,baseline_score=0,differential_improvement=True)
regression=proof("regression",tests_collected=100)
validation={
value={
⋮----
def reseal(value)
⋮----
unsigned=dict(value)
⋮----
class GenericCapabilityValidationReportTests(unittest.TestCase)
⋮----
def test_report_validates(self)
⋮----
value=report()
⋮----
def test_tampered_proof_fails_closed(self)
⋮----
def test_report_digest_tampering_fails_closed(self)
⋮----
def test_validation_evidence_must_match_proofs(self)
⋮----
def test_candidate_identity_must_match_decision(self)
⋮----
def test_validated_decision_requires_all_proofs_passed(self)
⋮----
proof=value["regression"]
⋮----
def test_validated_decision_requires_non_regressing_benchmark(self)
⋮----
proof=value["benchmark"]
⋮----
def test_non_boolean_proof_result_fails_closed(self)
⋮----
proof=value["targeted_test"]
⋮----
def test_trust_boundary_claim_fails_closed(self)
```

## File: test_generic_model_capacity.py
```python
class _FakeAPI
⋮----
response = None
error = None
⋮----
def __init__(self, base, key)
⋮----
def call(self, method, path, params, timeout_seconds=None)
⋮----
class GenericModelCapacityTests(unittest.TestCase)
⋮----
def _provider(self)
⋮----
def _env(self)
⋮----
def test_success_settles_transactional_reservation_with_actual_usage(self)
⋮----
reservation = {
⋮----
def test_protocol_failure_settles_consumed_tokens_without_double_release(self)
⋮----
def test_transport_failure_releases_open_reservation(self)
⋮----
def test_denied_reservation_skips_provider_call(self)
⋮----
denied = {
```

## File: test_generic_policy.py
```python
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
⋮----
class GenericPolicyTests(unittest.TestCase)
⋮----
def test_common_source_is_editable(self)
⋮----
def test_sensitive_and_ci_paths_are_blocked(self)
⋮----
def test_patch_rejects_secret_pattern(self)
```

## File: test_generic_toolchain.py
```python
ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
⋮----
class GenericToolchainTests(unittest.TestCase)
⋮----
def test_detects_node_and_python(self)
⋮----
root=Path(td); (root/"package.json").write_text("{}"); (root/"pyproject.toml").write_text("[project]\nname='x'\n")
⋮----
def test_npm_bootstrap_is_lockfile_bound_and_ignores_scripts(self)
⋮----
root=Path(td); (root/"package.json").write_text("{}"); (root/"package-lock.json").write_text("{}")
cmd=bootstrap_commands(root)[0]
⋮----
def test_safe_env_drops_studio_and_github_secrets(self)
⋮----
env=safe_env()
```

## File: test_generic_verifier_adaptation.py
```python
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
⋮----
class GenericVerifierAdaptationTests(unittest.TestCase)
⋮----
def test_accepts_safe_available_tool(self)
⋮----
recipe=validate_recipe({"commands":[["python","-m","unittest","discover"]],"reason":"run unit tests"},Path(td))
⋮----
def test_rejects_shell_command_string(self)
⋮----
def test_rejects_install_operation(self)
```

## File: test_github_artifact_cas_audit_store.py
```python
class GitHubArtifactCasAuditStoreTests(unittest.TestCase)
⋮----
def test_accepts_monotonic_rows(self)
⋮----
rows = [
⋮----
def test_rejects_non_monotonic_sequence(self)
⋮----
def test_rejects_oversized_audit(self)
```

## File: test_github_artifact_cas_stats_store.py
```python
class GitHubArtifactCasStatsStoreTests(unittest.TestCase)
⋮----
def test_accepts_valid_stats(self)
⋮----
payload = {
⋮----
def test_rejects_invalid_digest(self)
⋮----
def test_rejects_negative_hits(self)
⋮----
def test_rejects_oversized_stats(self)
```

## File: test_github_full_gate_cache_store.py
```python
class GitHubFullGateCacheStoreTests(unittest.TestCase)
⋮----
def test_accepts_valid_success_only_cache(self)
⋮----
payload = {
⋮----
def test_rejects_toolchain_mismatch(self)
⋮----
def test_rejects_failed_entry(self)
⋮----
def test_rejects_oversized_cache(self)
```

## File: test_github_goal_store.py
```python
class FakeGitHub
⋮----
def __init__(self)
⋮----
def get(self,path)
⋮----
sha=path.rsplit("/",1)[-1]
⋮----
sha=path.split("/git/trees/",1)[1].split("?",1)[0]
⋮----
def call(self,method,path,payload=None)
⋮----
sha=("1"*39)+str(len(self.calls)%10)
base=payload["base_tree"]
entries=[]
⋮----
content=entry["content"].encode()
bsha=("2"*39)+str(len(self.blobs)%10)
⋮----
sha=("3"*39)+str(len(self.calls)%10)
⋮----
def goal()
⋮----
class GitHubGoalStoreTests(unittest.TestCase)
⋮----
def test_save_and_load_round_trip(self)
⋮----
gh=FakeGitHub()
sha=save(gh,"demo",goal(),new_registry(),new_backlog())
⋮----
restored=load(gh,"demo")
⋮----
def test_missing_remote_state_returns_none(self)
⋮----
def test_invalid_project_id_rejected(self)
⋮----
def test_validation_requires_persisted_candidate(self)
⋮----
validation={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
⋮----
def test_validation_must_match_persisted_candidate(self)
⋮----
candidate={"candidate_id":"candidate:a","candidate_sha256":"a"*64}
validation={"candidate_id":"candidate:b","candidate_sha256":"a"*64}
⋮----
def test_validation_link_accepts_exact_candidate_identity(self)
⋮----
def test_awaiting_merge_requires_review_identity(self)
⋮----
adaptation={"status":"awaiting_merge","capability":"image_assets"}
candidate={"candidate_id":"candidate:a","candidate_sha256":"a"*64,"candidate":{"capability":"image_assets"}}
⋮----
def test_review_must_match_candidate_and_capability(self)
⋮----
review={
⋮----
def test_review_without_awaiting_merge_state_fails_closed(self)
⋮----
adaptation={"status":"promotion_required","capability":"image_assets"}
⋮----
def test_awaiting_registry_merge_requires_registry_review(self)
⋮----
adaptation={"status":"awaiting_registry_merge","capability":"image_assets"}
⋮----
review={"candidate_id":"candidate:a"}
⋮----
def test_registry_review_identity_must_match_candidate(self)
⋮----
registry_review={
⋮----
def test_local_restore_and_persist(self)
⋮----
gh=FakeGitHub(); save(gh,"demo",goal(),new_registry(),new_backlog())
⋮----
out=Path(td)
⋮----
def test_improvement_goal_round_trip_and_restore(self)
⋮----
improvement=new_goal(
⋮----
path=out/".autonomy/improvement-goal.json"
```

## File: test_github_memory_store.py
```python
class FakeGitHub
⋮----
def __init__(self)
⋮----
def get(self,path)
⋮----
sha=path.split("/git/trees/",1)[1].split("?",1)[0]
⋮----
def call(self,method,path,payload=None)
⋮----
sha=("c"*39)+str(len(self.calls)%10)
content=payload["tree"][0]["content"].encode()
bsha=("d"*39)+str(len(self.blobs)%10)
⋮----
sha=("e"*39)+str(len(self.calls)%10)
⋮----
def populated()
⋮----
class GitHubMemoryStoreTests(unittest.TestCase)
⋮----
def test_empty_store_returns_new_memory(self)
⋮----
def test_save_and_load_round_trip(self)
⋮----
gh=FakeGitHub(); memory=populated()
sha=save(gh,memory)
⋮----
def test_unchanged_memory_does_not_create_new_commit(self)
⋮----
gh=FakeGitHub(); memory=populated(); save(gh,memory)
calls=len(gh.calls); head=gh.ref
⋮----
def test_restore_and_persist_local(self)
⋮----
gh=FakeGitHub(); save(gh,populated())
⋮----
p=Path(td)/"memory.json"
```

## File: test_github_quick_gate_cache_store.py
```python
class GitHubQuickGateCacheStoreTests(unittest.TestCase)
⋮----
def test_accepts_valid_cache_payload(self)
⋮----
payload = {
result = _validate(payload)
⋮----
def test_rejects_invalid_cache_key(self)
⋮----
def test_rejects_oversized_cache(self)
⋮----
def test_rejects_unbounded_log_output(self)
```

## File: test_github_runner_persistent.py
```python
class GithubRunnerPersistentTests(unittest.TestCase)
⋮----
def request(self, root)
⋮----
path=root/"request.json"
⋮----
def test_run_uses_persistent_goal_engine(self)
⋮----
root=Path(td); request=self.request(root); out=root/"out"
⋮----
goal=new_goal("demo","Complete demo",[{"name":"done","required_evidence":["project_completion"]}])
goal=record_cycle(goal,evidence={"project_completion":{"finished":True}})
⋮----
result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="a"*40)
⋮----
def test_human_action_is_not_reported_complete(self)
⋮----
result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="b"*40)
⋮----
def test_blocked_state_preserves_reason(self)
⋮----
result=run(request,out,runner=lambda *a,**k:None,clock=lambda:0,budget_seconds=100,baseline_sha="c"*40)
⋮----
def test_remote_checkpoint_ingests_memory_before_state_persistence(self)
⋮----
order=[]
state={"status":"blocked","human_action":None,"blocked_reason":"test-stop"}
⋮----
def test_invalid_memory_ingestion_blocks_state_checkpoint(self)
⋮----
persist_state=stack.enter_context(patch("github_runner.persist_local"))
⋮----
def test_promotion_required_handoff_is_sealed_and_non_promoting(self)
⋮----
out=Path(td)
root=out/".autonomy"; root.mkdir(parents=True)
⋮----
state={
candidate={
validation={
⋮----
handoff=_prepare_capability_promotion_handoff(out,state,"c"*40)
⋮----
def test_promotion_handoff_rejects_cross_candidate_validation(self)
```

## File: test_github_runner_usage.py
```python
class GitHubRunnerUsageTests(unittest.TestCase)
⋮----
def test_collect_agent_usage_sums_codex_attempts_across_rounds(self)
⋮----
report = {
⋮----
def test_collect_agent_usage_ignores_duplicate_non_attempt_usage_and_bad_values(self)
⋮----
def test_collect_agent_usage_empty_report_is_zeroed(self)
```

## File: test_global_admission.py
```python
class GlobalAdmissionTests(unittest.TestCase)
⋮----
def test_zero_capacity_is_deferred(self)
⋮----
report = decide([{"id": "a", "requested_tokens": 10000, "token_envelope": 0}])
row = decision_for(report, "a")
⋮----
def test_recovery_probe_is_admitted_with_small_bounded_budget(self)
⋮----
report = decide([{
⋮----
def test_critical_project_bypasses_standard_slot_saturation(self)
⋮----
projects = [
report = decide(projects, max_standard_admissions=1)
⋮----
admitted_standard = [
⋮----
def test_ranking_prefers_priority_success_and_efficiency(self)
⋮----
def test_tiny_ordinary_envelope_is_deferred(self)
⋮----
def test_worker_reliability_changes_close_admission_ranking(self)
⋮----
admitted = next(row for row in report["decisions"] if row["admitted"])
```

## File: test_goal_capability_runtime.py
```python
class GoalCapabilityRuntimeTests(unittest.TestCase)
⋮----
def state(self, root)
⋮----
goal=new_goal("g","finish",[{"name":"done","required_evidence":["done"]}],max_attempts=4)
goal=record_cycle(goal,missing_capability="image_assets")
gp=root/"goal.json"; rp=root/"capabilities.json"
⋮----
registry=register(new_registry(),"image_assets","studio.capabilities.image_assets",{"source":"promoted_factory_capability"})
⋮----
def test_registered_capability_requires_runtime(self)
⋮----
state=run_goal(gp,rp,lambda s: {},max_cycles=1)
⋮----
def test_runtime_must_return_verified_evidence(self)
⋮----
state=run_goal(
⋮----
def test_verified_runtime_resolves_capability(self)
⋮----
calls=[]
def runtime(registry,name,state)
state=run_goal(gp,rp,lambda s: {},max_cycles=1,execute_registered_capability=runtime)
```

## File: test_goal_engine.py
```python
def goal(max_attempts=3)
⋮----
class GoalEngineTests(unittest.TestCase)
⋮----
def test_relaunch_until_required_evidence_exists(self)
⋮----
s=goal()
⋮----
s=record_cycle(s,evidence={"build_sha":"abc"})
⋮----
def test_complete_requires_all_evidence(self)
⋮----
s=record_cycle(goal(),evidence={"build_sha":"abc","qa_report":{"passed":True}})
⋮----
def test_failure_never_counts_as_completion(self)
⋮----
s=record_cycle(goal(),failure="tests failed")
⋮----
def test_missing_capability_requests_adaptation(self)
⋮----
s=record_cycle(goal(),missing_capability="unity_android_qa")
⋮----
def test_human_action_is_explicit_terminal_state(self)
⋮----
s=record_cycle(goal(),human_action="accept store declarations")
⋮----
def test_attempt_budget_blocks_infinite_loop(self)
⋮----
s=record_cycle(goal(max_attempts=1),failure="still failing")
⋮----
def test_persistence_detects_tampering(self)
⋮----
p=Path(td)/"goal.json"
⋮----
value=json.loads(p.read_text())
⋮----
def test_terminal_state_is_immutable(self)
⋮----
s=finalize(record_cycle(goal(),evidence={"build_sha":"abc","qa_report":"ok"}))
⋮----
def test_false_evidence_rejected(self)
⋮----
def test_attempt_budget_cannot_be_overrun(self)
⋮----
s=record_cycle(goal(max_attempts=1),failure="failed")
⋮----
def test_resolve_capability_removes_pending_requirement(self)
⋮----
s=record_cycle(goal(),missing_capability="unity.qa")
s=resolve_capability(s,"unity.qa",{"registry":"verified"})
```

## File: test_goal_learning.py
```python
class GoalLearningTests(unittest.TestCase)
⋮----
def test_context_combines_local_and_reusable_cross_project(self)
⋮----
m=new_memory()
m=add_entry(m,entry_id="a",kind="project",project_id="p1",summary="local",tags=["godot"],evidence={"x":1},provenance={"source":"test"})
m=add_entry(m,entry_id="b",kind="experience",project_id="p2",summary="reusable",tags=["godot"],evidence={"x":2},provenance={"source":"test"},reusable=True,confidence=100)
got=context_for_goal(m,"p1",["godot"])
⋮----
def test_learning_requires_tests_and_regression_for_reuse(self)
⋮----
m=new_memory(); state={"goal_id":"g","attempt":2}; commit="a"*40
unchanged=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"learning_summary":"x"},commit)
⋮----
unchanged=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"tests_passed":True,"learning_summary":"x","reusable_learning":True},commit)
⋮----
learned=learn_from_cycle(m,"p",state,{"evidence":{"x":1},"tests_passed":True,"regression_suite_passed":True,"learning_summary":"proved","learning_tags":["godot"],"reusable_learning":True},commit)
```

## File: test_goal_loop.py
```python
class GoalLoopTests(unittest.TestCase)
⋮----
def make_paths(self, root)
⋮----
goal_path = root / "goal.json"
registry_path = root / "registry.json"
⋮----
def test_relaunch_until_required_evidence_exists(self)
⋮----
root = Path(td)
⋮----
calls = {"n": 0}
def execute(state)
state = run_goal(goal_path, registry_path, execute, max_cycles=5)
⋮----
def test_worker_exception_is_recorded_and_retried(self)
⋮----
state = run_goal(goal_path, registry_path, execute, max_cycles=3)
⋮----
def test_programming_error_blocks_without_repeating_broken_cycle(self)
⋮----
def test_missing_capability_is_adapted_registered_and_goal_resumes(self)
⋮----
calls = {"execute": 0, "adapt": 0}
⋮----
def adapt(name, state)
state = run_goal(goal_path, registry_path, execute, adapt, max_cycles=6)
⋮----
registry = load_registry(registry_path)
⋮----
def test_unverified_adaptation_never_registers_capability(self)
⋮----
state = run_goal(goal_path, registry_path, execute, adapt, max_cycles=3)
⋮----
def test_yield_run_preserves_attempt_budget_and_returns_active(self)
⋮----
root=Path(td)
⋮----
state=run_goal(goal_path,registry_path,lambda state: {"yield_run":True,"evidence":{"adaptation_progress":{"phase":"pending_merge"}}},max_cycles=3)
⋮----
def test_human_action_stops_and_persists_terminal_state(self)
⋮----
state = run_goal(goal_path, registry_path, lambda state: {"human_action": "approve_release"}, max_cycles=3)
⋮----
def test_absent_adapter_leads_to_blocked_terminal_state(self)
⋮----
state = run_goal(goal_path, registry_path, lambda state: {"missing_capability": "missing_tool"}, max_cycles=4)
⋮----
def test_local_cycle_budget_does_not_fake_completion(self)
⋮----
state = run_goal(goal_path, registry_path, lambda state: {"failure": "still incomplete"}, max_cycles=2)
```

## File: test_godot_android_export.py
```python
def archive_bytes()
⋮----
buf=io.BytesIO()
⋮----
class Response(io.BytesIO)
⋮----
def __enter__(self): return self
def __exit__(self,*args): return False
⋮----
class GodotAndroidExportTests(unittest.TestCase)
⋮----
def test_installs_only_verified_android_templates(self)
⋮----
data=archive_bytes()
⋮----
target=gae.install_android_templates(Path(td), opener=lambda *a,**k:Response(data))
⋮----
def test_wrong_template_digest_fails_closed(self)
def test_requires_exactly_one_android_preset(self)
def test_export_is_offline_and_source_is_not_mounted(self)
⋮----
root=Path(td); project=root/'src'; project.mkdir(); (project/'project.godot').write_text('[application]\n'); (project/'export_presets.cfg').write_text('[preset.0]\nname="Android"\nplatform="Android"\n')
binary=root/'godot'; binary.write_bytes(b'godot'); (root/'godot.sha256').write_text(hashlib.sha256(b'godot').hexdigest()); binary.chmod(0o755)
templates=root/'templates'; templates.mkdir(); (templates/'android_debug.apk').write_bytes(b'd'); (templates/'android_release.apk').write_bytes(b'r')
seen={}
def runner(cmd,**kwargs)
⋮----
out=Path(cmd[cmd.index('-v')+1]) if False else None
host_out=next(x.split(':/out:rw')[0] for x in cmd if x.endswith(':/out:rw'))
⋮----
result=gae.export_debug_apk(project,binary,templates,runner=runner)
```

## File: test_godot_android_stage.py
```python
REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
⋮----
class FakeGitHub: pass
⋮----
class GodotAndroidStageTests(unittest.TestCase)
⋮----
@patch('godot_android_stage._publish', return_value='b'*40)
@patch('godot_android_stage._restore')
    def test_success_advances_only_to_device_qa(self, restore, publish)
⋮----
state={'engine':'godot','status':'godot_preview_validated','completion':{'finished':False,'next_stage':'godot_android_export_qa'},'coverage':{}}
⋮----
root=Path(td)/'work'; out=Path(td)/'out'
def runtime(_): return Path(td)/'godot'
def templates(_): return Path(td)/'templates'
def exporter(project,binary,tpls,artifact_path=None)
result=execute(REQ,root,out,FakeGitHub(),runtime,templates,exporter)
⋮----
@patch('godot_android_stage._restore')
    def test_requires_validated_preview_checkpoint(self, restore)
```

## File: test_godot_baseline.py
```python
class GodotBaselineTests(unittest.TestCase)
⋮----
def setUp(self)
⋮----
def test_reviewed_pinned_manifest(self)
⋮----
def test_mutable_or_unreviewed_target_rejected(self)
⋮----
c = copy.deepcopy(self.config)
⋮----
def test_download_integrity(self)
⋮----
data = b'fixture'
⋮----
def test_engine_errors_fail_even_with_zero_exit(self)
⋮----
def test_gameplay_requires_marker_and_success(self)
```

## File: test_godot_device_qa.py
```python
class GodotDeviceQATests(unittest.TestCase)
⋮----
def project(self, root: Path)
⋮----
def test_package_id_must_be_exact_and_unambiguous(self)
⋮----
root=Path(td); self.project(root)
⋮----
def test_apk_hash_mismatch_fails_before_adb(self)
⋮----
root=Path(td); self.project(root); apk=root/'app.apk'; apk.write_bytes(b'x'*2000)
⋮----
@patch('godot_device_qa.shutil.which', return_value='/usr/bin/tool')
@patch('godot_device_qa.subprocess.run')
    def test_success_keeps_app_offline_and_claims_no_journeys(self, run, which)
⋮----
root=Path(td); self.project(root); apk=root/'app.apk'; apk.write_bytes(b'a'*2000)
⋮----
digest=hashlib.sha256(apk.read_bytes()).hexdigest(); calls=[]
def fake(args, **kwargs)
⋮----
handle=kwargs['stdout']; handle.write(b'p'*2000); handle.flush()
⋮----
result=qa.validate_debug_apk(root,apk,digest,root/'out',sleeper=lambda _:None)
⋮----
def test_safe_env_drops_ci_credentials(self)
⋮----
env=qa._safe_env()
```

## File: test_godot_device_stage.py
```python
REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
⋮----
class FakeGitHub: pass
⋮----
def state(apk_sha)
⋮----
class GodotDeviceStageTests(unittest.TestCase)
⋮----
@patch('godot_device_stage._publish',return_value='b'*40)
@patch('godot_device_stage._restore')
    def test_matching_local_apk_advances_only_to_journey_qa(self,restore,publish)
⋮----
payload=b'a'*2000; digest=hashlib.sha256(payload).hexdigest(); restore.return_value=(state(digest),'a'*40,True)
⋮----
root=Path(td)/'work'; out=Path(td)/'out'; out.mkdir(); (out/'app-debug.apk').write_bytes(payload)
def validator(project,apk,expected,target)
result=execute(REQ,root,out,FakeGitHub(),device_validator=validator)
⋮----
@patch('godot_device_stage._publish',return_value='b'*40)
@patch('godot_device_stage._restore')
    def test_missing_local_apk_is_reexported_and_rebound(self,restore,publish)
⋮----
restore.return_value=(state('a'*64),'a'*40,True); payload=b'z'*2000; digest=hashlib.sha256(payload).hexdigest()
⋮----
root=Path(td)/'work'; out=Path(td)/'out'
def runtime(_): return Path(td)/'godot'
def templates(_): return Path(td)/'templates'
def exporter(project,binary,tpls,artifact_path=None)
⋮----
result=execute(REQ,root,out,FakeGitHub(),validator,runtime,templates,exporter)
⋮----
@patch('godot_device_stage._restore')
    def test_requires_android_export_checkpoint(self,restore)
⋮----
@patch('godot_device_stage._publish',return_value='b'*40)
@patch('godot_device_stage._restore')
    def test_device_cannot_spoof_journey_or_visual_evidence(self,restore,publish)
⋮----
def validator(*args): return {'passed':True,'apk_sha256':digest,'journeys_executed':True,'visual_reviewed':False}
```

## File: test_godot_final_review_qa.py
```python
def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
⋮----
class GodotFinalReviewTests(unittest.TestCase)
⋮----
def fixture(self,root)
⋮----
out=root/'out'; out.mkdir()
aab=b'aab'; manifest=b'{}'; policy=b'policy'; safety=b'{}'
⋮----
store=out/'play-store-godot'; store.mkdir(); (store/'manifest.json').write_bytes(manifest)
privacy=out/'privacy-godot'; privacy.mkdir(); (privacy/'privacy-policy.md').write_bytes(policy); (privacy/'data-safety.json').write_bytes(safety)
state={
⋮----
def test_full_bound_evidence_becomes_technical_store_ready_only(self)
⋮----
root=Path(td); out,state=self.fixture(root)
result=gfr.review(root,out,state)
⋮----
def test_changed_artifact_fails_closed(self)
⋮----
root=Path(td); out,state=self.fixture(root); (out/'app-release.aab').write_bytes(b'tampered')
⋮----
def test_cross_stage_hash_mismatch_fails_closed(self)
⋮----
root=Path(td); out,state=self.fixture(root); state['privacy_security']['release_aab_sha256']='0'*64
⋮----
def test_missing_coverage_or_attestation_blocks(self)
⋮----
root=Path(td); out,state=self.fixture(root); state['coverage']['security_qa']=False
⋮----
root=Path(td); out,state=self.fixture(root); state['privacy_security']['data_safety']['requires_human_legal_attestation']=False
```

## File: test_godot_model.py
```python
class FakeAPI
⋮----
base = 'https://example.test/v1'
def __init__(self, responses): self.responses = list(responses); self.calls = []
def call(self, method, path, data=None)
⋮----
value = self.responses.pop(0)
⋮----
def completion(value)
⋮----
def model(responses, limit=4)
⋮----
obj = GodotModel.__new__(GodotModel)
⋮----
def product_value()
⋮----
class GodotModelTests(unittest.TestCase)
⋮----
def test_product_uses_godot_planning_contract_not_flutter_execution_claims(self)
⋮----
subject = model([completion(product_value())])
result = subject.ask('product', 'plan game')
⋮----
system = subject.api.calls[0][2]['messages'][0]['content']
⋮----
def test_product_prompt_requires_literal_json_step_objects(self)
⋮----
def test_implementation_uses_godot_prompt_and_scope(self)
⋮----
subject = model([completion({'files':[{'path':'scripts/main.gd','content':'extends Node\n'}]})])
result = subject.ask('implementation', 'improve game')
⋮----
params = subject.api.calls[0][2]
system = params['messages'][0]['content']
⋮----
def test_test_role_rejects_non_test_path_then_repairs_once(self)
⋮----
subject = model([
result = subject.ask('tests', 'write regression')
⋮----
def test_structured_godot_call_falls_back_to_secondary_provider(self)
⋮----
subject = model([StudioError('API unavailable or timed out')])
fallback_api = FakeAPI([completion(product_value())])
⋮----
def test_ranked_fallback_uses_its_own_api_client_when_it_beats_primary(self)
⋮----
def test_budget_is_shared_and_fail_closed(self)
⋮----
subject = model([], limit=0)
```

## File: test_godot_play_stage.py
```python
REQ={
STATE={
⋮----
class FakeGitHub: pass
⋮----
def make_aab(path:Path)
⋮----
class GodotPlayStageTests(unittest.TestCase)
⋮----
@patch("godot_play_stage._publish",return_value="d"*40)
@patch("godot_play_stage._restore")
    def test_validate_only_finishes_requested_pipeline(self,restore,publish)
⋮----
root=Path(td); work=root/"work"; out=root/"out"; out.mkdir()
artifact=out/"app-release.aab"; make_aab(artifact)
state=dict(STATE); state["release_artifact"]=dict(STATE["release_artifact"])
⋮----
seen={}
def publisher(**kwargs)
result=execute(REQ,work,out,FakeGitHub(),env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=publisher)
⋮----
@patch("godot_play_stage._publish",return_value="d"*40)
@patch("godot_play_stage._restore")
    def test_missing_token_is_human_action(self,restore,publish)
⋮----
result=execute(REQ,work,out,FakeGitHub(),env={},publisher=lambda **k:self.fail("network"))
⋮----
@patch("godot_play_stage._publish",return_value="d"*40)
@patch("godot_play_stage._restore")
    def test_missing_exact_artifact_is_human_action(self,restore,publish)
⋮----
root=Path(td)
result=execute(REQ,root/"work",root/"out",FakeGitHub(),env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40})
```

## File: test_godot_preview.py
```python
def blob(text)
⋮----
raw=text.encode(); return {'encoding':'base64','content':base64.b64encode(raw).decode()}, len(raw)
⋮----
class FakeGitHub
⋮----
def __init__(self)
def get(self,path)
def call(self,method,path,data=None)
⋮----
state_entries=[e for e in data['tree'] if e['path']=='.studio/state.json']
⋮----
class FakeModel
⋮----
def __init__(self,limit): self.calls=0; self.models_used={}
def ask(self,role,context,screenshots=())
⋮----
class FakeSandbox
⋮----
def __init__(self,root): self.root=root
def create(self,name)
def gates(self,name,journeys)
⋮----
class GodotPreviewTests(unittest.TestCase)
⋮----
def request(self)
⋮----
def test_existing_godot_project_checkpoints_without_claiming_completion(self)
⋮----
github=FakeGitHub()
⋮----
base=Path(td); state=godot_preview.execute(self.request(),base/'work',base/'out',github,FakeModel,FakeSandbox)
⋮----
def test_publication_refuses_branch_movement(self)
⋮----
github=FakeGitHub(); github.branch_head='e'*40
⋮----
root=Path(td); (root/'project.godot').write_text('[application]\n')
```

## File: test_godot_privacy_security_qa.py
```python
class GodotPrivacySecurityTests(unittest.TestCase)
⋮----
def _state(self,aab_hash,manifest_hash)
def test_hash_mismatch_fails_before_audit(self)
⋮----
root=Path(td); out=root/'out'; out.mkdir(); (root/'project.godot').write_text('[application]\n')
⋮----
def test_cleartext_and_runtime_bridge_block(self)
⋮----
aab=out/'app-release.aab'; aab.write_bytes(b'a'); store=out/'play-store-godot'; store.mkdir(); mf=store/'manifest.json'; mf.write_text('{}')
result=gps.audit(root,out,self._state(hashlib.sha256(b'a').hexdigest(),hashlib.sha256(b'{}').hexdigest()))
```

## File: test_godot_release_artifact_stage.py
```python
REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
STATE={'engine':'godot','status':'godot_release_preflight_validated','release_preflight':{'format':'aab','target_api':36,'package':'com.example.demo','version_code':1,'version_name':'1.0'},'coverage':{'visual_qa':True},'completion':{'finished':False,'next_stage':'godot_release_artifact_qa'}}
ENV={'GODOT_ANDROID_KEYSTORE_RELEASE_PATH':'/tmp/key','GODOT_ANDROID_KEYSTORE_RELEASE_USER':'upload','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD':'secret'}
class FakeGitHub: pass
⋮----
class GodotReleaseArtifactStageTests(unittest.TestCase)
⋮----
@patch('godot_release_artifact_stage._publish',return_value='b'*40)
@patch('godot_release_artifact_stage._restore')
@patch('godot_release_artifact_stage.signing_credentials',return_value={'available':True})
    def test_success_advances_only_to_store_metadata(self,creds,restore,publish)
⋮----
root=Path(td); key=root/'key'; key.write_bytes(b'k'); env=dict(ENV); env['GODOT_ANDROID_KEYSTORE_RELEASE_PATH']=str(key)
def runtime(path): return path/'godot'
def source(path): return path/'android_source.zip'
def builder(project,binary,tpl,artifact): artifact.write_bytes(b'u'*2000); return {'passed':True,'unsigned_aab_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'network':'none','source_project':'not_mounted','signing_material_exposed':False}
def signer(unsigned,signed,keystore,alias,password): signed.write_bytes(b's'*2000); return {'passed':True,'signed_aab_sha256':hashlib.sha256(signed.read_bytes()).hexdigest(),'certificate_sha256':'c'*64,'signing_scope':'artifact_only','project_code_had_signing_material':False}
result=execute(REQ,root/'work',root/'out',FakeGitHub(),runtime,source,builder,signer,env)
⋮----
@patch('godot_release_artifact_stage._publish',return_value='b'*40)
@patch('godot_release_artifact_stage._restore')
@patch('godot_release_artifact_stage.signing_credentials',return_value={'available':False,'blocker':'release_keystore_required'})
    def test_lost_credentials_returns_to_human_action(self,creds,restore,publish)
⋮----
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),env={})
⋮----
@patch('godot_release_artifact_stage._publish',return_value='b'*40)
@patch('godot_release_artifact_stage._restore')
@patch('godot_release_artifact_stage.signing_credentials',return_value={'available':True})
    def test_project_build_cannot_claim_signing_isolation_if_exposed(self,creds,restore,publish)
⋮----
def builder(project,binary,tpl,artifact): artifact.write_bytes(b'u'*2000); return {'passed':True,'unsigned_aab_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'network':'none','source_project':'not_mounted','signing_material_exposed':True}
```

## File: test_godot_release_artifact.py
```python
def valid_aab(path:Path)
⋮----
class Response(io.BytesIO)
⋮----
def __enter__(self): return self
def __exit__(self,*args): return False
⋮----
class GodotReleaseArtifactTests(unittest.TestCase)
⋮----
def project(self,root)
⋮----
def test_source_template_requires_verified_official_archive(self)
⋮----
buf=io.BytesIO()
⋮----
data=buf.getvalue()
⋮----
target=gra.install_source_template(Path(td),opener=lambda *a,**k:Response(data))
⋮----
def test_unsigned_build_is_offline_and_receives_no_signing_material(self)
⋮----
root=Path(td); project=self.project(root/'project'); binary=root/'godot'; binary.write_bytes(b'godot'); binary.chmod(0o755)
(root/'godot.sha256').write_text(hashlib.sha256(b'godot').hexdigest()); source=root/'android_source.zip'; source.write_bytes(b'source'); artifact=root/'out.aab'; seen={}
def runner(cmd,**kwargs)
⋮----
host_out=next(x.split(':/out:rw')[0] for x in cmd if isinstance(x,str) and x.endswith(':/out:rw'))
⋮----
result=gra.build_unsigned_aab(project,binary,source,artifact,runner=runner)
⋮----
def test_signer_uses_password_environment_not_argv_and_only_artifact(self)
⋮----
root=Path(td); unsigned=root/'u.aab'; signed=root/'s.aab'; key=root/'upload.keystore'; key.write_bytes(b'key'); valid_aab(unsigned); calls=[]
⋮----
shutil_copy=__import__('shutil').copyfile; shutil_copy(unsigned,signed); return subprocess.CompletedProcess(cmd,0,stdout=b'signed')
⋮----
result=gra.sign_aab(unsigned,signed,key,'upload','SecretPassword',runner=runner)
⋮----
sign_call=calls[0]; self.assertIn('-storepass:env',sign_call[0]); self.assertEqual(sign_call[1]['STUDIO_AAB_STOREPASS'],'SecretPassword')
```

## File: test_godot_release_qa.py
```python
PRESET='''[preset.0]\nplatform="Android"\n[preset.0.options]\ngradle_build/use_gradle_build=false\ngradle_build/export_format=0\ngradle_build/target_sdk=""\narchitectures/arm64-v8a=false\nversion/code=1\nversion/name="0.1.0"\npackage/unique_name="com.example.demo"\npackage/signed=false\n'''
⋮----
class GodotReleaseQATests(unittest.TestCase)
⋮----
def project(self,root)
⋮----
def test_prepare_normalizes_play_requirements(self)
⋮----
root=self.project(Path(td)); result=qa.prepare_store_preset(root); audit=qa.audit_store_preset(root)
⋮----
def test_missing_release_keystore_is_human_action(self)
⋮----
root=self.project(Path(td)); result=qa.preflight(root,{})
⋮----
def test_existing_keystore_allows_only_preflight_not_aab_claim(self)
⋮----
root=Path(td); project=self.project(root/'project'); key=root/'upload.keystore'; key.write_bytes(b'key')
env={'GODOT_ANDROID_KEYSTORE_RELEASE_PATH':str(key),'GODOT_ANDROID_KEYSTORE_RELEASE_USER':'upload','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD':'secret'}
result=qa.preflight(project,env)
⋮----
def test_invalid_identity_stays_blocked(self)
⋮----
root=self.project(Path(td)); p=root/'export_presets.cfg'; p.write_text(PRESET.replace('com.example.demo','bad'))
qa.prepare_store_preset(root); audit=qa.audit_store_preset(root)
```

## File: test_godot_release_stage.py
```python
REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
STATE={'engine':'godot','status':'godot_visual_validated','coverage':{'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':True},'completion':{'finished':False,'next_stage':'godot_release_qa'}}
AUDIT={'passed':True,'blockers':[],'package':'com.example.demo','version_code':1,'version_name':'0.1.0','target_api':36,'format':'aab','gradle':True,'arm64':True}
class FakeGitHub: pass
⋮----
class GodotReleaseStageTests(unittest.TestCase)
⋮----
@patch('godot_release_stage._publish',return_value='b'*40)
@patch('godot_release_stage._restore')
    def test_missing_signing_is_human_action_not_success(self,restore,publish)
⋮----
evidence={'passed':False,'preset_normalized':True,'audit':dict(AUDIT),'signing':{'available':False,'human_action_required':True,'blocker':'release_keystore_required'},'blockers':['release_keystore_required'],'aab_built':False}
⋮----
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda root:evidence)
⋮----
@patch('godot_release_stage._publish',return_value='b'*40)
@patch('godot_release_stage._restore')
    def test_signing_inputs_advance_only_to_aab_artifact(self,restore,publish)
⋮----
evidence={'passed':True,'preset_normalized':True,'audit':dict(AUDIT),'signing':{'available':True,'human_action_required':False,'blocker':None},'blockers':[],'aab_built':False}
⋮----
@patch('godot_release_stage._publish',return_value='b'*40)
@patch('godot_release_stage._restore')
    def test_invalid_preset_stays_on_release_qa(self,restore,publish)
⋮----
evidence={'passed':False,'audit':{'passed':False},'signing':{'available':False},'blockers':['target_api_36_required'],'aab_built':False}
```

## File: test_godot_repository_probe.py
```python
class FakeSandbox
⋮----
def __init__(self, root): self.root = root
def create(self, name): self.created = name
def gates(self, name, journeys)
⋮----
def blob(text)
⋮----
raw = text.encode()
⋮----
class GodotRepositoryProbeTests(unittest.TestCase)
⋮----
def test_requires_pinned_commit(self)
⋮----
def test_imports_pinned_godot_tree_before_runtime(self)
⋮----
tree = {'truncated':False,'tree':[
def fetch(url)
⋮----
result = godot_repository_probe.probe('dbrckk/Jumpy', 'f'*40, fetch_json=fetch)
```

## File: test_godot_runtime_journey_stage.py
```python
REQ={'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Build a polished mobile game.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
JOURNEYS=[{'id':'settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]
⋮----
class FakeGitHub: pass
⋮----
class GodotRuntimeJourneyStageTests(unittest.TestCase)
⋮----
@patch('godot_runtime_journey_stage._publish',return_value='b'*40)
@patch('godot_runtime_journey_stage._restore')
    def test_all_journeys_advance_only_to_visual_qa(self,restore,publish)
⋮----
def installer(_): return Path(td)/'godot'
def runner(root,binary,journeys): return {'passed':True,'journeys_executed':True,'journey_count':1,'passed_ids':['settings'],'network':'none','source_project':'not_mounted','binary_sha256':'c'*64,'harness':'trusted_ephemeral_v1'}
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),installer,runner)
⋮----
@patch('godot_runtime_journey_stage._publish',return_value='b'*40)
@patch('godot_runtime_journey_stage._restore')
    def test_partial_success_stays_on_journey_stage(self,restore,publish)
⋮----
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda _:Path(td)/'godot',lambda *args:{'passed':False,'journeys_executed':False,'journey_count':1})
⋮----
@patch('godot_runtime_journey_stage._restore')
    def test_requires_device_validated_checkpoint(self,restore)
```

## File: test_godot_runtime_journeys.py
```python
JOURNEYS=[{'id':'open_settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]
⋮----
class GodotRuntimeJourneyTests(unittest.TestCase)
⋮----
def setup(self,root)
⋮----
project=root/'project'; project.mkdir(); (project/'project.godot').write_text('[application]\nrun/main_scene="res://Main.tscn"\n'); (project/'Main.tscn').write_text('x')
binary=root/'godot'; binary.write_bytes(b'godot'); digest=hashlib.sha256(binary.read_bytes()).hexdigest(); (root/'godot.sha256').write_text(digest); binary.chmod(0o755)
⋮----
def test_harness_uses_json_data_and_unique_node_names(self)
⋮----
def test_success_requires_every_exact_journey_marker(self)
⋮----
root=Path(td); project,binary=self.setup(root); seen={}
def runner(command,**kwargs)
result=run_journeys(project,binary,JOURNEYS,runner=runner)
⋮----
def test_missing_or_failed_marker_fails_closed(self)
⋮----
outputs=[b'STUDIO_JOURNEYS_COMPLETE:1\n',b'STUDIO_JOURNEY_FAIL:open_settings:expected_text_missing\n']
⋮----
root=Path(td); project,binary=self.setup(root)
def runner(command,**kwargs): return subprocess.CompletedProcess(command,1 if b'FAIL' in output else 0,output)
⋮----
def test_host_credentials_are_not_forwarded(self)
⋮----
root=Path(td); project,binary=self.setup(root); captured={}
```

## File: test_godot_runtime.py
```python
class Response(io.BytesIO)
⋮----
def __enter__(self): return self
def __exit__(self, *args): self.close()
⋮----
def archive_bytes(payload=b'godot-binary')
⋮----
buf = io.BytesIO()
⋮----
def project(root: Path) -> Path
⋮----
p = root / 'project'; p.mkdir(); (p / 'project.godot').write_text('[application]\n')
scripts = p / 'scripts'; scripts.mkdir(); (scripts / 'smoke.gd').write_text('extends Node\n')
⋮----
class GodotRuntimeTests(unittest.TestCase)
⋮----
def test_verified_archive_is_extracted_and_binary_gets_bound_digest(self)
⋮----
raw = archive_bytes(); expected = hashlib.sha256(raw).hexdigest()
⋮----
binary = godot_runtime.install(Path(tmp), opener=lambda request, timeout: Response(raw))
⋮----
def test_wrong_release_digest_is_rejected(self)
⋮----
raw = archive_bytes()
⋮----
def test_binary_tampering_after_extraction_is_rejected(self)
⋮----
def test_docker_validation_is_offline_and_uses_only_ephemeral_copy(self)
⋮----
base = Path(tmp); source = project(base); staged = base / 'staged'; staged.mkdir(); godot_runtime._copy_project(source, staged)
binary = godot_runtime.install(base / 'cache', opener=lambda request, timeout: Response(raw))
command = godot_runtime.docker_command(staged, binary)
⋮----
def test_source_project_is_not_mounted_or_mutated(self)
⋮----
base = Path(tmp); source = project(base); binary = godot_runtime.install(base / 'cache', opener=lambda request, timeout: Response(raw))
before = (source / 'scripts/smoke.gd').read_bytes(); captured = {}
def runner(command, **kwargs)
result = godot_runtime.validate(source, binary, runner=runner)
⋮----
def test_symlink_in_source_project_is_rejected(self)
⋮----
base = Path(tmp); source = project(base); outside = base / 'outside'; outside.write_text('x')
⋮----
staged = base / 'staged'; staged.mkdir()
⋮----
def test_host_environment_does_not_forward_credentials(self)
⋮----
def test_blocking_godot_marker_fails_even_with_zero_exit_code(self)
⋮----
base=Path(tmp); source=project(base); binary=godot_runtime.install(base/'cache', opener=lambda request, timeout: Response(raw))
def runner(command, **kwargs): return subprocess.CompletedProcess(command, 0, stdout=b'Parse Error: broken')
result=godot_runtime.validate(source,binary,runner=runner)
```

## File: test_godot_session.py
```python
class GodotSessionTests(unittest.TestCase)
⋮----
def test_requires_existing_godot_project(self)
⋮----
def test_gate_preserves_non_claimed_journey_evidence(self)
⋮----
root = Path(td); (root / 'project.godot').write_text('[application]\n')
fake = {'passed': True, 'exit_code': 0, 'output': 'ok', 'engine_version': '4.7.2-stable',
```

## File: test_godot_store_metadata_qa.py
```python
class GodotStoreMetadataTests(unittest.TestCase)
⋮----
def test_privacy_fails_closed_on_network_marker(self)
⋮----
root=Path(td); (root/'project.godot').write_text('[application]\n')
⋮----
result=gsm.privacy_classification(root)
⋮----
def test_validated_screens_require_exact_hashes(self)
⋮----
out=Path(td); shot=out/'godot-visual-a.png'; shot.write_bytes(b'x'*2000)
digest=hashlib.sha256(shot.read_bytes()).hexdigest()
state={'visual_qa':{'screenshot_sha256':[digest]},'device_qa':{}}
⋮----
def test_generated_store_assets_include_provenance(self)
⋮----
req={'app_name':'demo_app','brief':'Build a complete polished mobile productivity application with a focused and accessible workflow.'}
⋮----
root=Path(td); out=root/'out'; out.mkdir()
⋮----
pixels1=bytes((20,40,80,255))*(320*640)
pixels2=bytes((80,40,20,255))*(320*640)
shot1=out/'godot-visual-a.png'; shot2=out/'godot-visual-b.png'
⋮----
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (shot1,shot2)]
state={
result=gsm.build(req,root,out,state)
⋮----
def test_store_build_requires_signed_aab_evidence(self)
⋮----
req={'app_name':'demo_app','brief':'Build a complete polished mobile application.'}
```

## File: test_godot_visual_qa.py
```python
class FakeModel
⋮----
def __init__(self,limit): self.models_used={}
def ask(self,role,context,screenshots=())
⋮----
class GodotVisualQATests(unittest.TestCase)
⋮----
def project(self,root)
⋮----
def journeys(self)
⋮----
def test_instrumentation_changes_only_ephemeral_copy(self)
⋮----
source=self.project(Path(td)/'source'); before=(source/'project.godot').read_text(); target=Path(td)/'copy'; target.mkdir()
⋮----
def test_safe_env_drops_ci_credentials(self)
⋮----
env=qa._safe_env()
⋮----
@patch('godot_visual_qa._pull_png')
@patch('godot_visual_qa.shutil.which',return_value='/usr/bin/adb')
    def test_success_requires_every_android_frame_and_vision_review(self,which,pull)
⋮----
root=Path(td); source=self.project(root/'source'); out=root/'out'; calls=[]
def runtime(path): path.mkdir(parents=True,exist_ok=True); p=path/'godot'; p.write_bytes(b'x'); return p
def templates(path): path.mkdir(parents=True,exist_ok=True); return path
def exporter(project,binary,tpls,artifact_path=None): artifact_path.write_bytes(b'a'*2000); return {'passed':True}
def runner(args,timeout=120,**kwargs)
⋮----
text='STUDIO_VISUAL_PASS:home\nSTUDIO_VISUAL_PASS:settings\nSTUDIO_VISUAL_COMPLETE:2\n'
⋮----
def write_png(adb,serial,package,jid,target)
⋮----
result=qa.capture_and_review(source,self.journeys(),{'direction':'clean'},out,FakeModel,runtime,templates,exporter,runner,lambda _:None)
⋮----
@patch('godot_visual_qa._pull_png')
@patch('godot_visual_qa.shutil.which',return_value='/usr/bin/adb')
    def test_missing_visual_marker_fails_closed(self,which,pull)
⋮----
root=Path(td); source=self.project(root/'source')
```

## File: test_godot_visual_stage.py
```python
REQ={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
JOURNEYS=[{'id':'home','steps':[{'action':'tap','key':'start_button'},{'action':'expect_text','value':'Ready'}]},
STATE={'engine':'godot','status':'godot_runtime_journeys_validated','product':{'journeys':JOURNEYS},'design':{'direction':'clean'},
⋮----
class FakeGitHub: pass
⋮----
class GodotVisualStageTests(unittest.TestCase)
⋮----
@patch('godot_visual_stage._publish',return_value='b'*40)
@patch('godot_visual_stage._restore')
    def test_success_advances_only_to_release_qa(self,restore,publish)
⋮----
evidence={'passed':True,'visual_reviewed':True,'blockers':[],'journey_ids':['home','settings'],
⋮----
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda *args:evidence)
⋮----
@patch('godot_visual_stage._publish',return_value='b'*40)
@patch('godot_visual_stage._restore')
    def test_rejected_visual_stays_on_visual_qa(self,restore,publish)
⋮----
result=execute(REQ,Path(td)/'work',Path(td)/'out',FakeGitHub(),lambda *args:{'passed':False,'blockers':['clipping']})
⋮----
@patch('godot_visual_stage._restore')
    def test_requires_real_journey_coverage(self,restore)
⋮----
bad=dict(STATE); bad['coverage']=dict(STATE['coverage']); bad['coverage']['journeys_executed']=False
```

## File: test_human_handoff_status_v3.py
```python
class HumanHandoffStatusV3Tests(unittest.TestCase)
⋮----
def test_handoff_never_persists_secret_value_and_records_exact_name(self)
⋮----
root = Path(td)
secret_value = "canary-super-secret-value"
text_path = write_request(
text = text_path.read_text(encoding="utf-8")
machine_text = (root / "user-input-required.json").read_text(encoding="utf-8")
machine = json.loads(machine_text)
⋮----
def test_named_secret_resumes_terminal_goal_before_worker_runs(self)
⋮----
out = root / "out"
first_calls = {"n": 0}
⋮----
def require_secret(*args)
⋮----
first = run_persistent_project(
⋮----
resumed_calls = {"n": 0}
⋮----
def complete(*args)
⋮----
second = run_persistent_project(
⋮----
def test_missing_named_secret_does_not_reinvoke_worker(self)
⋮----
calls = {"n": 0}
⋮----
def should_not_run(*args)
⋮----
def test_project_status_reads_sealed_goal_without_running_work(self)
⋮----
out = Path(td) / "out"
⋮----
status = read_status(out)
```

## File: test_human_input_request.py
```python
ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
⋮----
class HumanInputRequestTests(unittest.TestCase)
⋮----
def test_detects_credentials(self)
⋮----
def test_secret_is_requested_by_name_but_never_embedded(self)
⋮----
p = write_request(Path(td), "demo", "Missing STUDIO_API_KEY", target_repo="owner/repo")
text = p.read_text()
⋮----
def test_prerequisite_satisfied_when_named_secret_exists(self)
```

## File: test_idempotent_model.py
```python
class FakeModel
⋮----
def __init__(self)
⋮----
def ask(self, role, context, screenshots=())
⋮----
class IdempotentModelTests(unittest.TestCase)
⋮----
def test_replay_after_crash_does_not_call_model_twice(self)
⋮----
checkpoint = Path(td) / "checkpoints.json"
⋮----
first_model = FakeModel()
⋮----
restarted_model = FakeModel()
⋮----
def test_changed_context_causes_new_call(self)
⋮----
model = FakeModel()
```

## File: test_imagen_codex_installer.py
```python
ROOT = Path(__file__).resolve().parents[1]
⋮----
def test_imagen_installer_is_version_pinned_and_checksum_verified()
⋮----
script = (ROOT / "scripts" / "install-imagen-codex.sh").read_text(
⋮----
def test_bootstrap_installs_imagen_without_making_it_mandatory()
⋮----
script = (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")
```

## File: test_immutable_artifact_cache.py
```python
class ImmutableArtifactCacheTests(unittest.TestCase)
⋮----
def _cas_env(self, root)
def _root(self, td)
⋮----
root = Path(td)
apk = root / APK_REL
⋮----
goldens = root / "test/goldens"
⋮----
def test_capture_and_verified_restore(self)
⋮----
root = self._root(td)
key = "a" * 64
⋮----
entry = capture(root, key)
⋮----
result = restore(root, entry, key)
⋮----
def test_corrupted_payload_is_rejected(self)
⋮----
key = "b" * 64
⋮----
apk_meta = entry["files"][APK_REL]
⋮----
blob = blob_path(apk_meta["sha256"])
payload = bytearray(blob.read_bytes())
⋮----
def test_validation_key_mismatch_is_rejected(self)
⋮----
entry = capture(root, "c" * 64)
⋮----
def test_identical_blobs_are_deduplicated(self)
⋮----
first = capture(root, "e" * 64)
second = capture(root, "f" * 64)
first_apk = first["files"][APK_REL]["sha256"]
second_apk = second["files"][APK_REL]["sha256"]
⋮----
blobs = [p for p in (root / "cas").rglob("*") if p.is_file()]
unique_digests = {
⋮----
def test_gc_removes_unreferenced_blobs(self)
⋮----
first = capture(root, "1" * 64)
⋮----
second = capture(root, "2" * 64)
stale = first["files"][APK_REL]["sha256"]
⋮----
stale_path = blob_path(stale)
⋮----
def test_high_value_artifact_can_evict_low_value_entry_before_admission(self)
⋮----
entries = {}
⋮----
first_key = "7" * 64
first = capture(
⋮----
old_apk_digest = first["files"][APK_REL]["sha256"]
⋮----
second_key = "8" * 64
second = capture(
⋮----
old_blob = blob_path(old_apk_digest)
⋮----
def test_touch_moves_entry_to_most_recent_position(self)
⋮----
entries = {
```

## File: test_improvement_backlog.py
```python
def assessment()
⋮----
goal=new_goal("g","ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
goal=record_cycle(goal,failure="repeat")
⋮----
goal=record_cycle(goal,evidence={"project_completion":True})
goal=finalize(goal)
⋮----
class ImprovementBacklogTests(unittest.TestCase)
⋮----
def test_assessment_is_deduplicated(self)
⋮----
backlog=merge_assessment(new_backlog(),assessment())
again=merge_assessment(backlog,assessment())
⋮----
def test_only_one_item_activates(self)
⋮----
result=assessment()
second=dict(result["candidates"][0])
⋮----
result={"version":1,"status":"improvement_required","candidates":[result["candidates"][0],second]}
backlog=activate_next(merge_assessment(new_backlog(),result))
⋮----
def test_proof_must_cover_candidate_requirements(self)
⋮----
backlog=activate_next(merge_assessment(new_backlog(),assessment()))
cid=backlog["items"][0]["candidate"]["id"]
⋮----
proved=prove(backlog,cid,{
⋮----
def test_persistence_detects_tampering(self)
⋮----
path=Path(td)/"backlog.json"
⋮----
value=json.loads(path.read_text())
```

## File: test_improvement_dispatch.py
```python
def add(registry,name,provider)
⋮----
class ImprovementDispatchTests(unittest.TestCase)
⋮----
def test_warning_requires_applicator_even_with_builtin_verifier(self)
⋮----
candidate={"kind":"persistent_warning"}
result=dispatch(candidate,new_registry())
⋮----
def test_warning_executes_with_registered_applicator_and_builtin_verifier(self)
⋮----
registry=add(new_registry(),"improvement.apply.persistent_warning","studio.warning_improver")
result=dispatch({"kind":"persistent_warning"},registry)
⋮----
def test_repeated_failure_requires_applicator_before_verifier(self)
⋮----
candidate={"kind":"repeated_failure"}
⋮----
def test_repeated_failure_then_requires_verifier(self)
⋮----
registry=add(new_registry(),"improvement.apply.repeated_failure","studio.failure_improver")
result=dispatch({"kind":"repeated_failure"},registry)
⋮----
def test_registered_applicator_and_verifier_allow_execution(self)
⋮----
registry=add(registry,"improvement.verify.repeated_failure","studio.repeated_failure_verifier")
⋮----
def test_capability_churn_has_distinct_verifier(self)
```

## File: test_improvement_executor.py
```python
def candidate_assessment()
⋮----
goal=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=10)
goal=record_cycle(goal,failure="repeat")
⋮----
goal=record_cycle(goal,evidence={"project_completion":True})
goal=finalize(goal)
⋮----
class ImprovementExecutorTests(unittest.TestCase)
⋮----
def setup_paths(self,root)
⋮----
backlog_path=root/"backlog.json"
goal_path=root/"improvement-goal.json"
registry_path=root/"capabilities.json"
backlog=activate_next(merge_assessment(new_backlog(),candidate_assessment()))
⋮----
registry=register(
⋮----
def test_no_active_improvement_is_idle(self)
⋮----
root=Path(td)
backlog=root/"backlog.json"; registry=root/"capabilities.json"
⋮----
result=run_active_improvement(backlog,root/"goal.json",registry,lambda state:{},max_cycles=1)
⋮----
def test_missing_verifier_requests_adaptation_without_running_cycles(self)
⋮----
calls={"n":0}
def execute(state)
result=run_active_improvement(backlog_path,goal_path,registry_path,execute,max_cycles=2)
⋮----
def test_active_improvement_relaunches_until_proved(self)
⋮----
result=run_active_improvement(backlog,goal,registry,execute,max_cycles=3)
⋮----
def test_incomplete_improvement_does_not_mutate_primary_success(self)
⋮----
result=run_active_improvement(
⋮----
def test_existing_goal_must_match_active_candidate(self)
⋮----
wrong=new_goal("wrong","Wrong",[{"name":"x","required_evidence":["x"]}])
⋮----
def test_verified_project_cycle_only_emits_trusted_evidence(self)
⋮----
candidate={
wrapped=verified_project_cycle(
result=wrapped({})
⋮----
def test_verified_project_cycle_does_not_invent_targeted_proof(self)
```

## File: test_improvement_verifier.py
```python
class ImprovementVerifierTests(unittest.TestCase)
⋮----
def complete(self,extra=None)
⋮----
result={
⋮----
def test_full_regression_requires_machine_completion(self)
⋮----
candidate={
⋮----
def test_repeated_failure_needs_matching_targeted_verification(self)
⋮----
candidate={"kind":"repeated_failure","source":{"failure":"flaky emulator"}}
result=self.complete({
evidence=verify_improvement_result(candidate,result)
⋮----
def test_capability_churn_needs_matching_preflight(self)
⋮----
candidate={"kind":"capability_churn","source":{"capability":"billing_qa"}}
⋮----
def test_warning_removed_is_derived_from_revalidated_stage(self)
⋮----
result=self.complete()
⋮----
def test_warning_still_present_is_not_proved(self)
⋮----
def test_unknown_kind_rejected(self)
```

## File: test_journeys.py
```python
VALID = [{'id': 'settings', 'steps': [{'action': 'tap', 'key': 'settings_button'}, {'action': 'expect_text', 'value': 'Durée'}]}]
⋮----
class JourneyTests(unittest.TestCase)
⋮----
def test_roundtrip_unicode_and_dart_injection_is_data(self)
⋮----
val = copy.deepcopy(VALID)
⋮----
def test_rejects_no_interaction(self)
def test_rejects_no_assertion(self)
def test_rejects_unknown_action(self)
def test_action_must_be_a_string(self)
def test_rejects_duplicate_or_reserved_path(self)
def test_bounded_steps_and_journeys(self)
def test_invalid_scrolls(self)
def test_typed_input_and_assertion(self)
⋮----
class ProtocolRepairTests(unittest.TestCase)
⋮----
def test_underscore_slug_is_valid(self)
def test_one_repair_preserves_budget(self)
⋮----
class InvalidThenValid(Model)
⋮----
def __init__(self)
def _ask(self, role, context, screenshots=())
model = InvalidThenValid()
⋮----
def test_bad_schema_does_not_loop_forever(self)
⋮----
class AlwaysInvalid(Model)
⋮----
def __init__(self): self.calls, self.limit = 0, 9
def _ask(self, *args)
model = AlwaysInvalid()
⋮----
def test_no_protocol_retry_when_budget_exhausted(self)
⋮----
class Limited(Model)
⋮----
def __init__(self): self.calls, self.limit = 0, 1
⋮----
model = Limited()
⋮----
class VisionDefaultsTests(unittest.TestCase)
⋮----
def test_nvidia_default(self)
def test_other_provider_never_receives_nvidia_model_implicitly(self)
def test_explicit_disable(self)
⋮----
class TruncationTests(unittest.TestCase)
⋮----
def test_truncated_output_gets_one_budgeted_retry(self)
⋮----
class Truncated(Model)
⋮----
def __init__(self): self.calls, self.limit = 0, 2
⋮----
model = Truncated()
⋮----
def test_auth_errors_are_not_protocol_retried(self)
⋮----
class AuthError(Model)
⋮----
def __init__(self): self.calls, self.limit = 0, 10
⋮----
model = AuthError()
⋮----
class CodingModelTests(unittest.TestCase)
⋮----
def test_code_defaults_to_configured_general_model(self)
def test_code_model_override(self)
def test_other_provider_keeps_configured_general_model(self)
```

## File: test_jumpy_v13_migration.py
```python
class JumpyV13MigrationTests(unittest.TestCase)
⋮----
def test_jumpy_is_an_enabled_v13_mobile_studio_request(self)
⋮----
request_path = Path("control/mobile-requests/jumpy.json")
⋮----
request = request_check(json.loads(request_path.read_text(encoding="utf-8")))
⋮----
def test_legacy_jumpy_scheduler_is_removed(self)
⋮----
legacy = Path(".github/workflows/jumpy-autocycle.yml")
```

## File: test_learning_context.py
```python
class LearningContextTests(unittest.TestCase)
⋮----
def test_bounded_valid_context_is_injected(self)
⋮----
path=Path(td)/"ctx.json"
⋮----
old=os.environ.get("STUDIO_LEARNED_CONTEXT_PATH"); os.environ["STUDIO_LEARNED_CONTEXT_PATH"]=str(path)
⋮----
items=load_context(); self.assertEqual(len(items),1)
text=augment("task")
⋮----
def test_invalid_or_oversized_context_is_ignored(self)
⋮----
path=Path(td)/"ctx.json"; path.write_text("x"*70000)
```

## File: test_lease_guard.py
```python
class LeaseGuardTests(unittest.TestCase)
⋮----
def test_guard_refreshes_active_lease(self)
⋮----
task = {"status": "running"}
⋮----
before = task["lease_heartbeat_at"]
```

## File: test_lease_keepalive.py
```python
class LeaseKeepaliveTests(unittest.TestCase)
⋮----
def test_long_operation_renews_active_lease(self)
⋮----
task = {
calls = []
⋮----
def fake_heartbeat(task, *, owner, token, lease_seconds)
⋮----
def test_unleased_task_is_noop(self)
```

## File: test_local_api_security.py
```python
class LocalAPISecurityTests(unittest.TestCase)
⋮----
def test_loopback_http_is_allowed(self)
⋮----
api = API("http://127.0.0.1:11434/v1", "")
⋮----
def test_localhost_http_is_allowed(self)
⋮----
api = API("http://localhost:8000/v1", "")
⋮----
def test_remote_http_is_rejected(self)
⋮----
def test_https_remote_remains_allowed(self)
⋮----
api = API("https://example.invalid/v1", "secret")
```

## File: test_local_capacity.py
```python
class LocalCapacityTests(unittest.TestCase)
⋮----
def _response(self, payload)
⋮----
response = MagicMock()
⋮----
def test_probe_selects_code_and_vision_models(self)
⋮----
payload = {
⋮----
result = local_capacity.probe_gateway(
⋮----
def test_omniroute_is_pooled_free_not_unmetered(self)
⋮----
payload = {"data": [{"id": "auto"}]}
⋮----
def test_invalid_model_envelope_is_ignored(self)
⋮----
def test_autodiscovery_can_be_disabled(self)
```

## File: test_local_model_leaderboard.py
```python
class LocalModelLeaderboardTests(unittest.TestCase)
⋮----
def test_best_specialist_ranks_first(self)
⋮----
data = {
result = leaderboards(data)
rows = result["contexts"]["stack:python"]
⋮----
def test_low_sample_rows_are_hidden(self)
⋮----
result = leaderboards(data, min_samples=3)
⋮----
def test_contexts_are_independent(self)
```

## File: test_local_model_reputation.py
```python
class LocalModelReputationTests(unittest.TestCase)
⋮----
def test_reputation_requires_minimum_samples(self)
⋮----
path = Path(td) / "rep.json"
⋮----
data = rep.load(path)
⋮----
def test_good_model_gets_positive_reputation(self)
⋮----
score = rep.score(
⋮----
def test_protocol_failures_reduce_reputation(self)
⋮----
def test_verified_success_dominates_after_minimum_samples(self)
⋮----
def test_verified_success_can_rehabilitate_model(self)
⋮----
def test_repeated_verified_failures_trigger_quarantine(self)
⋮----
status = rep.quarantine_status(
⋮----
def test_good_verified_runs_do_not_quarantine(self)
⋮----
def test_quarantine_penalty_dominates_normal_provider_priority(self)
⋮----
def test_benchmark_bonus_is_bounded(self)
⋮----
data = {
```

## File: test_local_model_specialization.py
```python
class LocalModelSpecializationTests(unittest.TestCase)
⋮----
def test_context_requires_minimum_evidence(self)
⋮----
path = Path(td) / "specialization.json"
⋮----
result = spec.specialization_score(
⋮----
def test_same_model_can_be_good_in_python_and_bad_in_flutter(self)
⋮----
data = spec.load(path)
python_score = spec.specialization_score(
flutter_score = spec.specialization_score(
⋮----
def test_weighted_contexts_blend_specialization(self)
⋮----
data = {
backend_heavy = spec.specialization_score(
rust_heavy = spec.specialization_score(
⋮----
def test_score_is_bounded(self)
⋮----
score = spec.specialization_score(
```

## File: test_memory_bridge.py
```python
class MemoryBridgeTests(unittest.TestCase)
⋮----
def research(self)
⋮----
def test_validated_research_is_recorded_but_not_cross_project_reusable(self)
⋮----
memory = remember_research(new_memory(), "app-a", self.research())
items = query(memory, project_id="app-a", kind="research")
⋮----
def test_unvalidated_research_is_rejected(self)
⋮----
def test_experience_can_be_reused_only_with_regression_proof(self)
⋮----
proof = {
memory = remember_experience(
⋮----
def test_reusable_experience_without_regression_proof_is_rejected(self)
⋮----
def test_experience_requires_valid_commit_identity(self)
```

## File: test_memory_lifecycle.py
```python
class MemoryLifecycleTests(unittest.TestCase)
⋮----
def test_research_is_ingested(self)
⋮----
out=Path(td)
⋮----
memory=ingest_run(new_memory(),"app-a",out)
⋮----
def test_approved_persisted_promotion_becomes_reusable_experience(self)
⋮----
items=reusable_for_project(memory,"app-b")
⋮----
def test_unapproved_or_unpersisted_candidate_is_not_learned(self)
⋮----
def test_duplicate_experience_is_idempotent(self)
⋮----
memory=ingest_run(memory,"app-a",out)
```

## File: test_meta_router.py
```python
class MetaRouterTests(unittest.TestCase)
⋮----
def test_no_agent_forces_model_only(self)
⋮----
decision = choose_execution_mode([], role="implementation", agent_available=False)
⋮----
def test_insufficient_history_keeps_dual_mode(self)
⋮----
events = [
decision = choose_execution_mode(events, role="implementation", agent_available=True)
⋮----
def test_model_advantage_reduces_agent_exploration(self)
⋮----
events = []
⋮----
def test_strategy_efficiency_can_override_rate_only_policy(self)
⋮----
events=[]
⋮----
strategy_data={
decision=choose_execution_mode(
⋮----
def test_meta_router_surfaces_exploration_strategy(self)
⋮----
def test_strategy_uncertainty_reduces_meta_route_confidence(self)
⋮----
def test_architecture_discipline_can_reduce_agent_focus(self)
⋮----
summary = {
decision = choose_execution_mode(
⋮----
def test_agent_advantage_keeps_agent_focus(self)
⋮----
def test_force_diversify_overrides_learned_single_strategy(self)
⋮----
route = choose_execution_mode(
```

## File: test_mobile_studio_provider_fallbacks.py
```python
WORKFLOW = Path('.github/workflows/mobile-studio.yml')
⋮----
class MobileStudioProviderFallbackTests(unittest.TestCase)
⋮----
def test_autonomous_runner_exports_free_nim_fallbacks_using_existing_key(self)
⋮----
text = WORKFLOW.read_text(encoding='utf-8')
```

## File: test_mobile_studio_runtime_triggers.py
```python
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/mobile-studio.yml"
⋮----
class MobileStudioRuntimeTriggerTests(unittest.TestCase)
⋮----
def test_runtime_changes_retrigger_autonomous_mobile_studio(self)
⋮----
text = WORKFLOW.read_text(encoding="utf-8")
```

## File: test_model_portfolio_audit.py
```python
class ModelPortfolioAuditTests(unittest.TestCase)
⋮----
def test_independent_review_is_detected(self)
⋮----
result = audit({
⋮----
def test_same_review_identity_is_detected(self)
⋮----
def test_empty_portfolio_is_safe(self)
⋮----
result = audit({})
```

## File: test_model_portfolio_learning.py
```python
class ModelPortfolioLearningTests(unittest.TestCase)
⋮----
def test_learning_requires_minimum_samples(self)
⋮----
path = Path(td) / "portfolio.json"
audit = {"review_independent": True, "diversity_ratio": 1.0}
⋮----
result = learning.recommendation(learning.load(path))
⋮----
def test_best_verified_portfolio_class_is_recommended(self)
⋮----
independent = {"review_independent": True, "diversity_ratio": 0.8}
same = {"review_independent": False, "diversity_ratio": 0.2}
⋮----
def test_classes_are_separate(self)
⋮----
data = learning.load(path)
⋮----
def test_diversity_bias_is_zero_without_enough_evidence(self)
⋮----
data = {
⋮----
def test_diversity_bias_is_bounded_by_portfolio_class(self)
⋮----
high = {
medium = {
```

## File: test_model_portfolio.py
```python
class ModelPortfolioTests(unittest.TestCase)
⋮----
def test_review_avoids_implementation_identity_when_possible(self)
⋮----
ranked = {
portfolio = choose(
⋮----
def test_review_falls_back_if_no_independent_candidate_exists(self)
⋮----
def test_non_review_role_keeps_top_candidate(self)
⋮----
portfolio = choose(ranked)
⋮----
def test_visual_also_prefers_independent_identity(self)
```

## File: test_multi_engine_orchestrator.py
```python
REQUEST={'id':'demo-v1','target_repo':'owner/app','app_name':'demo_app','brief':'Build a complete polished mobile application.','enabled':True,'max_rounds':2,'max_calls':8,'max_cycles':3}
⋮----
class MultiEngineOrchestratorTests(unittest.TestCase)
⋮----
def request(self,root)
⋮----
path=root/'request.json'; path.write_text(json.dumps(REQUEST)); return path
⋮----
@patch('multi_engine_orchestrator.run_flutter_project')
    def test_flutter_delegates_unchanged(self,legacy)
⋮----
root=Path(td); out=root/'out'; req=self.request(root)
def runner(args,timeout)
result=run_project(str(req),out,str(root/'work'),runner,100,lambda:0,'a'*40)
⋮----
def _runner(self,out,fail_stage=None,bad_journey=False,bad_visual=False,release_ready=False,artifact_credentials=True)
⋮----
calls=[]
⋮----
script=next((x for x in args if isinstance(x,str) and x.startswith('studio/')),None)
⋮----
coverage={'android_export':True,'device_qa':True,'journeys_executed':not bad_journey,'visual_qa':False}
⋮----
coverage={'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':not bad_visual}
⋮----
coverage={'android_export':True,'device_qa':True,'journeys_executed':True,'visual_qa':True}
⋮----
report={'engine':'godot','status':'godot_release_preflight_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_release_artifact_qa'},'coverage':coverage}
⋮----
report={'engine':'godot','status':'godot_release_credentials_required','release_status':'human_action_required','completion':{'finished':False,'next_stage':'godot_release_qa'},'coverage':coverage}
⋮----
report={'engine':'godot','status':'godot_release_credentials_required','release_status':'human_action_required','completion':{'finished':False,'next_stage':'godot_release_qa'},'coverage':{'visual_qa':True}}
⋮----
report={'engine':'godot','status':'godot_release_artifact_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_store_metadata_qa'},'coverage':{'visual_qa':True,'release_artifact':True,'release_signed':True},'release_artifact':{'project_code_had_signing_material':False}}
⋮----
report={'engine':'godot','status':'godot_store_metadata_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_privacy_security_qa'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True}}
⋮----
report={'engine':'godot','status':'godot_privacy_security_validated','release_status':'not_store_ready','completion':{'finished':False,'next_stage':'godot_final_review_qa'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True}}
⋮----
report={'engine':'godot','status':'godot_technical_store_ready','release_status':'technical_store_ready','completion':{'finished':False,'next_stage':'godot_play_submission'},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True,'final_review':True}}
⋮----
report={'engine':'godot','status':'godot_play_validated','release_status':'play_validated','completion':{'finished':True,'next_stage':None},'coverage':{'release_artifact':True,'release_signed':True,'store_metadata':True,'privacy_qa':True,'security_qa':True,'final_review':True,'play_publish':True}}
⋮----
def test_godot_stops_cleanly_when_release_keystore_is_missing(self)
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out)
⋮----
def test_release_chain_reaches_human_play_submission_only(self)
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,calls=self._runner(out,release_ready=True)
⋮----
def test_opt_in_play_validation_can_complete_godot_pipeline(self)
⋮----
root=Path(td); out=root/'out'
request=dict(REQUEST)
⋮----
req=root/'request.json'; req.write_text(json.dumps(request))
⋮----
def test_credentials_lost_between_preflight_and_signing_return_to_human_action(self)
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,release_ready=True,artifact_credentials=False)
⋮----
def test_each_failed_godot_stage_stays_on_itself(self)
⋮----
expected={'android':'godot_android_export_qa','device':'godot_device_qa','journey':'godot_runtime_journey_qa','visual':'godot_visual_qa','release':'godot_release_qa','artifact':'godot_release_artifact_qa','store':'godot_store_metadata_qa','privacy':'godot_privacy_security_qa','final':'godot_final_review_qa'}
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,fail_stage=failed,release_ready=failed in {'artifact','store','privacy','final'})
⋮----
def test_journey_stage_cannot_fake_execution_coverage(self)
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,bad_journey=True)
⋮----
def test_visual_stage_cannot_fake_visual_coverage(self)
⋮----
root=Path(td); out=root/'out'; req=self.request(root); runner,_=self._runner(out,bad_visual=True)
⋮----
def test_missing_detection_evidence_fails_closed(self)
⋮----
root=Path(td); req=self.request(root)
def runner(args,timeout): return subprocess.CompletedProcess(args,0)
```

## File: test_multi_project_canary.py
```python
class MultiProjectCanaryTests(unittest.TestCase)
⋮----
def _request(self, root: Path, index: int) -> None
⋮----
payload = {
⋮----
def test_three_projects_complete_without_state_cross_talk(self)
⋮----
root = Path(td)
requests = root / "requests"
⋮----
out = root / "out"
⋮----
seen = []
⋮----
def fake_project(project, project_out, work, runner, deadline, clock, baseline_sha)
⋮----
capacity = {"projects": [
⋮----
code = ci_runner.run_queue(
⋮----
report = json.loads((out / "queue.json").read_text(encoding="utf-8"))
⋮----
marker = json.loads(
```

## File: test_native_qa.py
```python
class NativeQATests(unittest.TestCase)
⋮----
def test_declared_runtime_permissions_are_detected(self)
⋮----
root = Path(tmp)
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
permissions = _declared_permissions(root)
⋮----
def test_release_permission_output_is_parsed_from_multiple_tool_formats(self)
⋮----
output = """android.permission.CAMERA\nuses-permission: name='android.permission.ACCESS_FINE_LOCATION'\nuses-permission: name='android.permission.CAMERA'\n"""
⋮----
def test_native_stage_is_registered(self)
⋮----
stage = get_stage('native_qa')
```

## File: test_notification_qa.py
```python
class NotificationQATests(unittest.TestCase)
⋮----
def test_counts_only_target_package_notification_records(self)
⋮----
sample = '''NotificationRecord(0x1: pkg=com.example.demo user=UserHandle{0})\nNotificationRecord(0x2: pkg=com.other.app user=UserHandle{0})\nNotificationRecord(0x3: pkg=com.example.demo user=UserHandle{0})\n'''
⋮----
def test_detects_notification_dependency_and_permission(self)
⋮----
root = Path(tmp)
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
def test_notification_stage_is_registered(self)
⋮----
stage = get_stage('notification_qa')
```

## File: test_omniroute_capacity.py
```python
class _FakeResponse
⋮----
def __init__(self, payload)
⋮----
def __enter__(self)
⋮----
def __exit__(self, exc_type, exc, tb)
⋮----
def read(self)
⋮----
class OmniRouteCapacityTests(unittest.TestCase)
⋮----
def test_authenticated_summary_exposes_live_remaining_capacity(self)
⋮----
snapshot = parse_summary({
⋮----
def test_unauthenticated_summary_fails_closed_for_scheduler_capacity(self)
⋮----
def test_invalid_summary_is_rejected(self)
⋮----
def test_fetch_summary_uses_bearer_token_and_canonical_endpoint(self)
⋮----
seen = {}
⋮----
def opener(request, timeout)
⋮----
snapshot = fetch_summary(
⋮----
def test_fetch_summary_accepts_openai_v1_base_url(self)
```

## File: test_orchestrator_automerge.py
```python
class OrchestratorAutoMergeTests(unittest.TestCase)
⋮----
def test_github_automerge_uses_local_persistence_proof(self)
⋮----
out=Path(tmp)
⋮----
calls=[]
def runner(args,timeout)
⋮----
status=_run_adaptation_automerge(out,1000,runner,lambda:0)
⋮----
args=calls[0][0]
⋮----
def test_non_github_provider_never_attempts_automerge(self)
⋮----
status=_run_adaptation_automerge(Path(tmp),100,lambda args,timeout:calls.append(args),lambda:0)
```

## File: test_orchestrator.py
```python
BASELINE = 'a' * 40
MISSING_STAGE = 'future_capability_qa'
⋮----
class OrchestratorTests(unittest.TestCase)
⋮----
def payload_for(self, args)
⋮----
def missing_report(self)
⋮----
def test_full_pipeline_reaches_finished(self)
⋮----
root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}')
calls = []
def runner(args, timeout)
result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)
⋮----
expected = ['studio/run.py', 'studio/post_preview.py', 'studio/device_stage.py', 'studio/capability_stage.py',
⋮----
def test_unregistered_stage_research_then_synthesis(self)
⋮----
root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}'); calls = []
⋮----
order = json.loads((out / 'evolution-work-order.json').read_text())
⋮----
report = {'status': 'validated_preview'} if 'studio/run.py' in args else self.missing_report()
⋮----
def test_research_failure_prevents_synthesis(self)
⋮----
root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}'); calls=[]
⋮----
def test_adaptation_without_baseline_has_no_promotable_work_order(self)
⋮----
result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, None)
⋮----
def test_stage_return_code_two_is_human_action_not_failure(self)
⋮----
report = {'status': 'validated_preview'}
rc = 0
⋮----
report = {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'play_publish'}}
⋮----
report = {
rc = 2
⋮----
def test_scheduler_rewind_can_revisit_release_build_boundedly(self)
⋮----
root = Path(tmp)
out = root / 'out'
request = root / 'request.json'
⋮----
release_build_calls = 0
⋮----
initial = {
result = run_registered_stages(
⋮----
def test_successful_stage_must_advance(self)
⋮----
report = {'status': 'validated_preview'} if 'studio/run.py' in args else {'status': 'validated_preview',
⋮----
class GitHubRunnerTests(unittest.TestCase)
⋮----
def request(self, root)
⋮----
path = root / 'request.json'
⋮----
def test_non_main_is_rejected_before_generation(self)
⋮----
def test_adapter_reports_complete_only_after_machine_completion(self)
⋮----
root = Path(tmp); request = self.request(root); out = root / 'out'
⋮----
report = {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}} if 'studio/post_preview.py' in args else {'status': 'validated_preview'}
⋮----
result = github_run(request, out, runner=runner, clock=lambda: 0, budget_seconds=1000, baseline_sha=BASELINE)
```

## File: test_patch_safety_rebuild.py
```python
class PatchSafetyRebuildTests(unittest.TestCase)
⋮----
def test_write_failure_restores_original(self)
⋮----
root=Path(td)
⋮----
target=root/"lib/app.dart"
⋮----
real_replace=os.replace
calls={"n":0}
def fail(src,dst)
⋮----
def test_duplicate_model_keys_are_rejected_with_bounded_repair(self)
⋮----
model=Model(2)
envelope=lambda text:{"choices":[{"finish_reason":"stop","message":{"content":text}}]}
⋮----
def test_nonfinite_model_number_is_repaired(self)
⋮----
def test_checkpoint_metadata_rejects_secret_before_remote_access(self)
⋮----
gh=GitHub.__new__(GitHub)
⋮----
def test_unresolved_recovery_blocks_publication(self)
```

## File: test_performance_qa.py
```python
class PerformanceQATests(unittest.TestCase)
⋮----
def test_parse_gfxinfo_computes_frame_metrics(self)
⋮----
sample = '''Profile data in ms:\n\nDraw,Prepare,Process,Execute\n1,1,1,1\n2,2,2,2\n10,10,10,10\n20,20,20,20\n'''
metrics = _parse_gfxinfo(sample)
⋮----
def test_empty_gfxinfo_fails_closed_upstream(self)
⋮----
metrics = _parse_gfxinfo('no profile data')
⋮----
def test_performance_stage_is_registered(self)
⋮----
stage = get_stage('performance_qa')
```

## File: test_persistent_improvement_runner.py
```python
class PersistentImprovementRunnerTests(unittest.TestCase)
⋮----
def test_completed_project_with_active_improvement_requests_adaptation(self)
⋮----
root=Path(td)
goal=new_goal("primary","Ship",[{"name":"done","required_evidence":["project_completion"]}],max_attempts=8)
goal=record_cycle(goal,failure="repeat")
⋮----
goal=record_cycle(goal,evidence={"project_completion":True})
goal=finalize(goal)
backlog=activate_next(merge_assessment(new_backlog(),assess(goal,{})))
⋮----
result=run_active_improvement(
```

## File: test_persistent_quick_gate_cache.py
```python
class PersistentQuickGateCacheTests(unittest.TestCase)
⋮----
def test_roundtrip_with_matching_toolchain(self)
⋮----
path = Path(td) / "cache.json"
⋮----
entries = {
⋮----
def test_toolchain_mismatch_invalidates_cache(self)
⋮----
payload = {
⋮----
def test_cache_is_bounded(self)
⋮----
loaded = pqc.load()
⋮----
def test_stale_writer_merges_existing_entries_instead_of_overwriting(self)
⋮----
first = {"first": {"passed": True, "logs": []}}
⋮----
stale_second = {"second": {"passed": True, "logs": []}}
```

## File: test_phase_budget.py
```python
class PhaseBudgetTests(unittest.TestCase)
⋮----
def test_allocation_reserves_verification(self)
⋮----
quotas = allocate(
⋮----
def test_high_difficulty_keeps_more_fallback_capacity(self)
⋮----
low = allocate(
high = allocate(
⋮----
def test_unused_planning_is_reallocated_without_changing_total(self)
⋮----
updated = reallocate_unused(quotas, phase="planning", unused_seconds=30)
⋮----
def test_phase_remaining_never_goes_negative(self)
⋮----
def test_bounded_timeout_respects_remaining_quota(self)
⋮----
def test_unknown_phase_is_rejected(self)
```

## File: test_phase_cost_baseline.py
```python
class PhaseCostBaselineTests(unittest.TestCase)
⋮----
def test_baseline_requires_four_samples(self)
⋮----
path=Path(td)/"phase-cost-baselines.json"
toolchain={"stacks":["python"]}
⋮----
b=baseline(load(path),toolchain,"verification")
⋮----
def test_baselines_are_separated_by_toolchain_and_phase(self)
⋮----
data=load(path)
```

## File: test_platform_view_qa.py
```python
class PlatformViewQATests(unittest.TestCase)
⋮----
def test_platform_view_stage_is_registered(self)
⋮----
def test_detects_supported_platform_view_dependencies(self)
⋮----
root = Path(tmp)
⋮----
def test_native_ui_classes_are_parsed(self)
⋮----
xml = '<hierarchy><node class="android.webkit.WebView"/><node class="android.view.TextureView"/></hierarchy>'
⋮----
def test_unrelated_dependency_does_not_require_platform_view(self)
```

## File: test_play_publisher.py
```python
class Response(io.BytesIO)
⋮----
def __enter__(self): return self
def __exit__(self, *args): return False
⋮----
def make_aab(path: Path)
⋮----
class PlayPublisherTests(unittest.TestCase)
⋮----
def test_validate_only_flow_does_not_commit(self)
⋮----
root = Path(td)
bundle = root / "app.aab"
⋮----
calls = []
⋮----
def opener(req, timeout=0)
⋮----
result = publish_bundle(
⋮----
def test_commit_requires_explicit_true(self)
⋮----
bundle = Path(td)/"app.aab"
⋮----
calls=[]
⋮----
result=publish_bundle(
⋮----
def test_token_is_only_in_authorization_header(self)
⋮----
token="SECRET_ACCESS_TOKEN_1234567890"
⋮----
bundle=Path(td)/"app.aab"; make_aab(bundle); calls=[]
⋮----
def test_missing_publication_credentials_are_explicit(self)
⋮----
def test_invalid_track_is_rejected_before_network(self)
⋮----
bundle=Path(td)/"app.aab"; make_aab(bundle)
```

## File: test_play_stage.py
```python
REQ={
⋮----
def valid_aab(path: Path)
⋮----
def base_state()
⋮----
class FakeGitHub
⋮----
def __init__(self,*a,**k): pass
def publish(self,*a,**k): return "c"*40
⋮----
class PlayStageTests(unittest.TestCase)
⋮----
def test_detects_gradle_kts_application_id(self)
⋮----
root=Path(td)
p=root/"android/app/build.gradle.kts"
⋮----
@patch("play_stage.GitHub",FakeGitHub)
    def test_validate_only_completes_without_commit(self)
⋮----
root=Path(td); out=root/"out"; work=root/"work"; out.mkdir(); work.mkdir()
req_path=root/"request.json"; req_path.write_text(json.dumps(REQ))
gradle=work/"android/app/build.gradle.kts"; gradle.parent.mkdir(parents=True)
⋮----
artifact=out/"app-release.aab"; valid_aab(artifact)
state=base_state()
digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
⋮----
seen={}
def publisher(**kwargs)
result=advance(req_path,work,out,env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=publisher)
⋮----
@patch("play_stage.GitHub",FakeGitHub)
    def test_missing_play_token_becomes_human_action(self)
⋮----
state=base_state(); digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
⋮----
result=advance(req_path,work,out,env={},publisher=lambda **k: self.fail("network"))
⋮----
@patch("play_stage.GitHub",FakeGitHub)
    def test_commit_requires_trusted_approval(self)
⋮----
req=dict(REQ); req["play_publish"]={"enabled":True,"track":"internal","commit":True}
req_path=root/"request.json"; req_path.write_text(json.dumps(req))
⋮----
state=base_state(); state["publication_request"]=dict(req["play_publish"])
⋮----
result=advance(req_path,work,out,env={"STUDIO_PLAY_ACCESS_TOKEN":"x"*40},publisher=lambda **k:self.fail("network"))
```

## File: test_portfolio_candidate_scheduler.py
```python
class PortfolioCandidateSchedulerTests(unittest.TestCase)
⋮----
def test_single_candidate_when_route_is_confident(self)
⋮----
schedule = choose_schedule(
⋮----
def test_two_candidates_when_uncertain_and_free_capacity_exists(self)
⋮----
def test_three_candidates_require_high_uncertainty_and_cheap_verification(self)
⋮----
def test_three_candidate_portfolio_prefers_two_models_and_one_agent(self)
⋮----
def test_two_candidate_portfolio_prefers_model_agent_diversity(self)
⋮----
def test_expensive_verification_prevents_wide_portfolio(self)
⋮----
def test_model_only_never_spawns_agents(self)
⋮----
def test_model_only_can_compare_multiple_direct_models(self)
⋮----
def test_three_local_models_can_fill_wide_portfolio_without_agents(self)
⋮----
def test_agent_only_does_not_require_model_candidate(self)
⋮----
def test_high_quality_verified_candidate_stops_further_exploration(self)
⋮----
def test_uncertain_cheap_round_can_keep_exploring(self)
```

## File: test_predictive_budget.py
```python
class PredictiveBudgetTests(unittest.TestCase)
⋮----
def test_small_clean_repo_is_low_difficulty(self)
⋮----
result = estimate(
⋮----
def test_failure_history_and_slow_verification_raise_difficulty(self)
⋮----
def test_generation_is_refused_when_it_would_consume_verification_reserve(self)
```

## File: test_preemption_apply.py
```python
class PreemptionApplyTests(unittest.TestCase)
⋮----
def _fixture(self, root: Path, phase="verified")
⋮----
victim = root / "low" / ".autonomy"
⋮----
checkpoint = new("low", "generic", "a" * 40)
checkpoint = advance(checkpoint, round_index=2, phase=phase)
⋮----
plan = {
⋮----
def test_dry_run_preserves_reservations(self)
⋮----
root = Path(td)
⋮----
report = execute(root, apply=False, now=1000.0)
⋮----
def test_apply_releases_reservations_and_records_checkpoint(self)
⋮----
report = execute(root, apply=True, now=1000.0)
⋮----
ledger = load(root / "capacity-ledger.json")
⋮----
lease = next(iter(ledger["reservations"].values()))
⋮----
state = json.loads(
⋮----
def test_unsafe_checkpoint_blocks_apply(self)
⋮----
def test_cooldown_blocks_immediate_reverse_or_repeat_preemption(self)
⋮----
first = execute(root, apply=True, now=1000.0, cooldown_seconds=300)
⋮----
second = execute(root, apply=True, now=1100.0, cooldown_seconds=300)
```

## File: test_preemption_controller.py
```python
class PreemptionControllerTests(unittest.TestCase)
⋮----
def _plan(self, victim_priority=20, contender_priority=95)
⋮----
def test_high_value_contender_preempts_safe_checkpointed_victim(self)
⋮----
report = plan(self._plan(), {
⋮----
def test_missing_checkpoint_blocks_preemption(self)
⋮----
def test_unverified_checkpoint_phase_blocks_preemption(self)
⋮----
def test_small_priority_delta_blocks_preemption(self)
⋮----
report = plan(self._plan(victim_priority=70, contender_priority=80), {
⋮----
def test_critical_victim_is_never_preempted(self)
⋮----
value = self._plan()
⋮----
report = plan(value, {
```

## File: test_privacy_stage.py
```python
REQ={
⋮----
def state_before_privacy()
⋮----
class FakeGitHub
⋮----
def __init__(self,*a,**k): pass
def publish(self,*a,**k): return "c"*40
⋮----
class PrivacyStageTests(unittest.TestCase)
⋮----
@patch("privacy_stage.GitHub",FakeGitHub)
@patch("privacy_stage.build_privacy_package")
    def test_unresolved_data_safety_becomes_human_action(self,build)
⋮----
root=Path(td); out=root/"out"; out.mkdir()
req=root/"request.json"; req.write_text(json.dumps(REQ))
⋮----
result=advance(req,root/"work",out)
⋮----
@patch("privacy_stage.GitHub",FakeGitHub)
@patch("privacy_stage.build_privacy_package")
    def test_derived_privacy_evidence_advances_to_security(self,build)
```

## File: test_privacy.py
```python
class PrivacyAuditTests(unittest.TestCase)
⋮----
def make_app(self, root: Path, manifest: str, dart: str = 'void main() {}', pubspec: str = 'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n')
⋮----
target = root / 'android/app/src/main'
⋮----
lib = root / 'lib'
⋮----
def test_offline_app_can_derive_no_external_collection(self)
⋮----
root = Path(tmp)
⋮----
audit = analyze(root)
⋮----
safety = build_data_safety(audit)
⋮----
def test_internet_capability_fails_closed(self)
⋮----
def test_sensitive_permission_fails_closed(self)
⋮----
def test_local_storage_is_not_misclassified_as_network_collection(self)
⋮----
def test_analytics_dependency_requires_verified_classification(self)
⋮----
pubspec = '''name: demo
⋮----
def test_auth_and_payments_surface_specific_data_classes(self)
⋮----
def test_push_sdk_is_not_mistaken_for_offline_app(self)
⋮----
def test_package_writes_policy_and_data_safety_evidence(self)
⋮----
root = Path(tmp) / 'app'
out = Path(tmp) / 'out'
⋮----
state = {'release_evidence': {'store_metadata': {'listing': {'title': 'Demo'}}}}
evidence = build_privacy_package(root, out, state)
⋮----
payload = json.loads((out / 'privacy/data-safety.json').read_text())
```

## File: test_production_os_local_e2e.py
```python
class _ControlPlane
⋮----
def __init__(self)
⋮----
outer = self
⋮----
class Handler(BaseHTTPRequestHandler)
⋮----
def log_message(self, format, *args)
⋮----
def do_POST(self)
⋮----
length = int(self.headers.get("Content-Length", "0"))
payload = json.loads(self.rfile.read(length) or b"{}")
⋮----
body = {"worker": {"worker_id": payload["worker_id"]}}
⋮----
def _send(self, status, body)
⋮----
encoded = json.dumps(body).encode("utf-8")
⋮----
@property
    def url(self)
⋮----
def __enter__(self)
⋮----
def __exit__(self, exc_type, exc, tb)
⋮----
class ProductionOSLocalE2ETests(unittest.TestCase)
⋮----
def test_worker_completes_real_http_control_plane_cycle(self)
⋮----
output_root = Path(td)
⋮----
def runner(request_path, project_out, **kwargs)
⋮----
request = json.loads(
envelope = {
⋮----
def execute_once(client, **kwargs)
⋮----
rc = main(
⋮----
request_files = list(
result_files = list(
⋮----
result = json.loads(
⋮----
paths = [call["path"] for call in control_plane.calls]
⋮----
register = control_plane.calls[0]
⋮----
complete = next(
```

## File: test_production_os_result_contract.py
```python
BASE = {
⋮----
class ProductionOSResultContractTests(unittest.TestCase)
⋮----
def test_request_accepts_optional_production_os_correlation(self)
⋮----
value = copy.deepcopy(BASE)
⋮----
checked = request_check(value)
⋮----
def test_request_rejects_invalid_production_os_correlation(self)
⋮----
def test_result_envelope_correlates_usage_and_completion(self)
⋮----
request = copy.deepcopy(BASE)
⋮----
summary = {
⋮----
out = Path(td)
envelope = write_production_os_result(out, request, summary)
persisted = json.loads(
⋮----
def test_no_result_envelope_without_correlation(self)
⋮----
envelope = write_production_os_result(
```

## File: test_production_os_worker_cli.py
```python
class _Client
⋮----
def __init__(self, base_url, token)
⋮----
def register(self, worker_id, capabilities, operator_token)
⋮----
class ProductionOSWorkerCLITests(unittest.TestCase)
⋮----
def test_main_registers_worker_and_runs_once(self)
⋮----
clients = []
runs = []
⋮----
def factory(base_url, token)
⋮----
client = _Client(base_url, token)
⋮----
def run_once_fn(client, **kwargs)
⋮----
env = {
⋮----
rc = main(
⋮----
def test_main_runs_bounded_cycles_until_queue_is_idle(self)
⋮----
calls = []
outcomes = iter([
⋮----
def test_main_requires_all_control_plane_credentials(self)
⋮----
def test_main_forwards_capacity_snapshot_to_worker_cycle(self)
⋮----
expected = {
⋮----
def test_continuous_mode_polls_idle_queue_and_refreshes_capacity(self)
⋮----
capacities = []
⋮----
def capacity_provider(env)
⋮----
value = {"remaining_tokens": len(capacities) + 1}
⋮----
def sleeper(seconds)
```

## File: test_production_os_worker_preflight.py
```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
⋮----
SPEC = importlib.util.spec_from_file_location(
MODULE = importlib.util.module_from_spec(SPEC)
⋮----
class ProductionOSWorkerPreflightTests(unittest.TestCase)
⋮----
def base_env(self, output_root)
⋮----
def test_ready_configuration_passes(self)
⋮----
def test_visual_assets_are_non_blocking_when_pollinations_is_unavailable(self)
⋮----
def test_visual_assets_are_reported_ready_when_pollinations_is_ready(self)
⋮----
def test_visual_probe_uses_asset_forge_operational_status(self)
⋮----
class Result
⋮----
returncode = 0
stdout = (
stderr = ""
⋮----
def test_missing_required_secret_fails_without_echoing_secret_values(self)
⋮----
env = self.base_env(Path(td) / "out")
⋮----
rendered = "\n".join(lines)
⋮----
def test_remote_http_control_plane_is_rejected(self)
⋮----
def test_loopback_http_is_allowed(self)
⋮----
def test_partial_omniroute_configuration_fails(self)
⋮----
def test_non_positive_poll_interval_fails(self)
```

## File: test_production_os_worker_runtime.py
```python
def sample_job()
⋮----
class _FakeClient
⋮----
def __init__(self, job)
⋮----
def claim(self, worker_id, capabilities)
⋮----
def ack(self, key, worker_id)
⋮----
def complete(self, payload)
⋮----
def fail(self, payload)
⋮----
def heartbeat(self, worker_id, *, active_job_keys=(), capacity=None)
⋮----
class _Response
⋮----
def __init__(self, status, payload=None)
⋮----
def __enter__(self)
⋮----
def __exit__(self, exc_type, exc, tb)
⋮----
def read(self, limit=-1)
⋮----
class ProductionOSWorkerRuntimeTests(unittest.TestCase)
⋮----
def test_worker_capabilities_require_ready_visual_backend(self)
⋮----
caps = worker_capabilities(
⋮----
class Result
⋮----
returncode = 0
stdout = json.dumps(
stderr = ""
⋮----
def test_client_rejects_insecure_remote_control_plane(self)
⋮----
def test_client_allows_loopback_http(self)
⋮----
client = ProductionOSClient(
⋮----
def test_client_claim_posts_bearer_json_and_handles_no_content(self)
⋮----
seen = []
⋮----
def opener(request, timeout)
⋮----
job = client.claim(
⋮----
def test_run_once_returns_idle_when_no_job_is_available(self)
⋮----
client = _FakeClient(None)
⋮----
result = run_once(
⋮----
def test_run_once_acks_executes_and_completes_with_usage(self)
⋮----
client = _FakeClient(sample_job())
⋮----
def runner(request_path, out, **kwargs)
⋮----
request = json.loads(Path(request_path).read_text(encoding="utf-8"))
⋮----
completed = client.calls[3][1]
⋮----
def test_run_once_reports_failed_pipeline_to_control_plane(self)
⋮----
failed = client.calls[3][1]
⋮----
def test_run_once_refreshes_heartbeat_during_long_runner_execution(self)
⋮----
refreshed = threading.Event()
original_heartbeat = client.heartbeat
active_heartbeats = {"count": 0}
⋮----
def heartbeat(worker_id, *, active_job_keys=(), capacity=None)
⋮----
def test_run_once_reports_runner_exception_and_clears_active_job(self)
⋮----
def test_capacity_snapshot_prefers_authenticated_omniroute(self)
⋮----
class Snapshot
⋮----
authenticated_usage = True
steady_recurring_tokens = 1_500_000_000
used_this_month = 125_000_000
remaining_tokens = 1_375_000_000
catalog_updated_at = "2026-09-18"
catalog_source = "free-tier-catalog"
⋮----
seen = {}
⋮----
def fetch(url, *, api_key=None, timeout=5.0)
⋮----
result = production_capacity_snapshot(
⋮----
def test_capacity_snapshot_fails_closed_without_authenticated_usage(self)
⋮----
authenticated_usage = False
⋮----
used_this_month = None
remaining_tokens = None
⋮----
def test_client_heartbeat_posts_capacity_snapshot(self)
⋮----
capacity = {
⋮----
def test_run_once_writes_project_token_envelope_before_execution(self)
⋮----
plan = json.loads(
row = next(
⋮----
def test_project_token_envelope_is_capped_by_live_global_remaining_capacity(self)
```

## File: test_production_os_worker.py
```python
class ProductionOSWorkerTests(unittest.TestCase)
⋮----
def job(self)
⋮----
def test_build_studio_request_preserves_goal_and_workflow_correlation(self)
⋮----
request = build_studio_request(self.job())
⋮----
checked = request_check(request)
⋮----
def test_visual_reuse_adds_asset_forge_guidance(self)
⋮----
job = self.job()
⋮----
request = build_studio_request(job)
⋮----
def test_explicit_visual_task_adds_asset_forge_guidance_without_reuse_metadata(self)
⋮----
def test_french_visual_task_adds_asset_forge_guidance(self)
⋮----
def test_structured_asset_forge_contract_enables_guidance_without_keywords(self)
⋮----
def test_short_task_is_expanded_to_valid_studio_brief(self)
⋮----
def test_completion_payload_forwards_usage_and_evidence(self)
⋮----
result = {
⋮----
payload = completion_payload(
⋮----
def test_failure_payload_is_bounded_and_preserves_usage(self)
⋮----
payload = failure_payload(
```

## File: test_project_budget.py
```python
class ProjectBudgetTests(unittest.TestCase)
⋮----
def test_default_budget_is_derived_from_existing_limits(self)
⋮----
state = {}
budget = configure(state, {"max_calls": 12, "max_cycles": 5})
⋮----
def test_repair_budget_is_independently_enforced(self)
⋮----
def test_repair_outcome_tracks_gain_and_cost(self)
⋮----
status = budget_status(state)
⋮----
def test_low_yield_branch_is_stopped_after_enough_calls(self)
⋮----
task = {
⋮----
def test_small_branch_is_not_stopped_too_early(self)
```

## File: test_project_context.py
```python
class ProjectContextTests(unittest.TestCase)
⋮----
def request(self)
⋮----
def state(self)
⋮----
def test_render_uses_trusted_state_and_next_stage(self)
⋮----
text = render(self.request(), self.state())
⋮----
def test_write_creates_root_handoff_file(self)
⋮----
root = Path(tmp)
path = write(root, self.request(), self.state())
⋮----
def test_model_patch_scope_cannot_edit_trusted_context(self)
⋮----
def test_no_evidence_is_not_presented_as_success(self)
⋮----
state = {'status': 'pending', 'blockers': []}
text = render(self.request(), state)
```

## File: test_project_engine_generic.py
```python
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
⋮----
class GenericEngineTests(unittest.TestCase)
⋮----
def test_node_project_is_generic(self)
⋮----
def test_python_project_is_generic(self)
⋮----
def test_flutter_stays_specialized(self)
⋮----
def test_godot_stays_specialized(self)
⋮----
def test_ambiguous_specialized_markers_fail(self)
```

## File: test_project_engine.py
```python
class ProjectEngineTests(unittest.TestCase)
⋮----
def test_infers_flutter_from_pubspec(self)
⋮----
def test_infers_godot_from_project_file(self)
⋮----
def test_ambiguous_specialized_markers_fail_and_other_stacks_use_generic(self)
⋮----
def test_godot_edit_scope_is_bounded_to_text_project_files(self)
⋮----
def test_godot_restore_can_read_production_docs_without_making_them_model_editable(self)
⋮----
def test_flutter_policy_remains_compatible(self)
⋮----
def test_unknown_engine_is_rejected(self)
```

## File: test_project_memory.py
```python
class ProjectMemoryTests(unittest.TestCase)
⋮----
def make_entry(self, memory, **overrides)
⋮----
data = {
⋮----
def test_reusable_memory_requires_evidence_provenance_and_high_confidence(self)
⋮----
def test_query_scopes_project_kind_and_tags(self)
⋮----
memory = self.make_entry(new_memory())
memory = add_entry(
⋮----
def test_cross_project_reuse_excludes_same_project(self)
⋮----
memory = self.make_entry(memory, entry_id="e2", project_id="app-b", summary="Reusable second lesson.")
items = reusable_for_project(memory, "app-b", tags=["godot"])
⋮----
def test_non_reusable_research_never_crosses_projects(self)
⋮----
def test_duplicate_id_rejected(self)
⋮----
def test_persistence_detects_tampering(self)
⋮----
path = Path(td) / "memory.json"
⋮----
value = json.loads(path.read_text())
```

## File: test_promoted_capabilities.py
```python
class PromotedCapabilitiesTests(unittest.TestCase)
⋮----
def write(self, root, capabilities)
⋮----
path = root / "promoted_capabilities.json"
⋮----
def entry(self, name)
⋮----
def test_missing_registry_is_empty(self)
⋮----
def test_provider_path_is_deterministic(self)
⋮----
def test_promoted_capability_bootstraps_project_registry(self)
⋮----
root=Path(td); name="improvement.apply.repeated_failure"
provider_file=root/"studio/capabilities/improvement_apply_repeated_failure.py"
⋮----
registry=sync_into_registry(
⋮----
def test_provider_redirect_is_rejected(self)
⋮----
root=Path(td); name="improvement.apply.repeated_failure"; entry=self.entry(name)
⋮----
def test_project_provider_conflict_fails_closed(self)
⋮----
root=Path(td); name="improvement.verify.repeated_failure"
provider_file=root/"studio/capabilities/improvement_verify_repeated_failure.py"
⋮----
registry=register(new_registry(),name,"studio.other_provider",{"tests":"passed"})
⋮----
def test_missing_provider_implementation_fails_closed(self)
⋮----
def test_symlink_provider_implementation_is_rejected(self)
⋮----
outside=root/"outside.py"; outside.write_text("def provide(): return True\n")
```

## File: test_provider_cost.py
```python
class ProviderCostTests(unittest.TestCase)
⋮----
def test_estimate_call_cost(self)
⋮----
cost = provider_cost.estimate_call_cost(
⋮----
def test_record_maintains_ema_and_total(self)
⋮----
path = Path(td) / "cost.json"
⋮----
row = provider_cost.load(path)["p:implementation"]
⋮----
def test_verified_value_per_unit_cost_drops_with_money_and_retry(self)
⋮----
cheap = utility_score(
expensive = utility_score(
```

## File: test_provider_health.py
```python
class ProviderHealthTests(unittest.TestCase)
⋮----
def test_three_failures_open_circuit_and_success_resets_it(self)
⋮----
path = Path(td) / "provider-health.json"
⋮----
row = load(path)["p1"]
⋮----
def test_corrupt_state_fails_open_without_crashing(self)
⋮----
data = record_failure(path, "p1", threshold=1, cooldown_seconds=10, now=100.0)
⋮----
def test_backoff_grows_exponentially_after_threshold(self)
⋮----
def test_reliability_bonus_is_bounded_and_prefers_success(self)
⋮----
good = {"p": {"successes": 9, "failures": 1, "consecutive_failures": 0, "opened_until": 0.0}}
bad = {"p": {"successes": 1, "failures": 9, "consecutive_failures": 2, "opened_until": 0.0}}
⋮----
def test_provider_rows_never_persist_sensitive_details(self)
⋮----
raw = path.read_text()
```

## File: test_provider_metrics.py
```python
class ProviderMetricsTests(unittest.TestCase)
⋮----
def test_latency_ema_is_role_scoped(self)
⋮----
path = Path(td) / "metrics.json"
⋮----
data = load(path)
⋮----
def test_latency_bonus_rewards_fast_and_penalizes_slow(self)
⋮----
fast = {"p:product": {"calls": 3, "ema_latency_seconds": 1.5}}
slow = {"p:product": {"calls": 3, "ema_latency_seconds": 80.0}}
```

## File: test_provider_monthly_quota.py
```python
class ProviderMonthlyQuotaTests(unittest.TestCase)
⋮----
def test_records_tokens_in_current_month(self)
⋮----
path = Path(td) / "quota.json"
now = datetime(2026, 9, 14, tzinfo=timezone.utc)
⋮----
status = quota.quota_status(path, "omniroute", 1000, now=now)
⋮----
def test_month_rollover_resets_usage_view(self)
⋮----
september = datetime(2026, 9, 30, tzinfo=timezone.utc)
october = datetime(2026, 10, 1, tzinfo=timezone.utc)
⋮----
def test_exhaustion_is_enforced(self)
⋮----
def test_noncritical_work_preserves_reserve(self)
⋮----
data = {"schema": 1, "months": {"2026-09": {
decision = quota.quota_admission(
⋮----
def test_critical_work_can_use_reserve_but_not_exceed_quota(self)
⋮----
allowed = quota.quota_admission(
denied = quota.quota_admission(
```

## File: test_provider_router.py
```python
ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio"
⋮----
class ProviderRouterTests(unittest.TestCase)
⋮----
def test_discovered_local_capacity_becomes_provider_specs(self)
⋮----
discovered = [{
⋮----
providers = load_providers()
⋮----
coder = next(p for p in providers if p.model == "qwen-coder")
⋮----
def test_autodiscovers_omniroute_only_when_no_explicit_provider_exists(self)
⋮----
auto = ProviderSpec(
⋮----
def test_explicit_primary_skips_omniroute_autodiscovery(self)
⋮----
env = {
⋮----
def test_primary_provider_is_loaded(self)
⋮----
def test_missing_fallback_secret_skips_provider(self)
⋮----
config = [{
⋮----
def test_free_fallback_can_rank_before_primary(self)
⋮----
providers = load_providers(prefer_free=True)
⋮----
def test_local_endpoint_is_unmetered_by_default(self)
⋮----
def test_local_primary_can_be_keyless(self)
⋮----
def test_local_json_provider_can_be_keyless(self)
⋮----
def test_remote_endpoint_is_metered_by_default(self)
⋮----
def test_unmetered_can_be_explicit_for_remote_self_hosted_gateway(self)
⋮----
def test_omniroute_endpoint_gets_current_recurring_quota_by_default(self)
⋮----
def test_paid_budget_exhaustion_keeps_pooled_free_quota_provider(self)
⋮----
providers = (
eligible = budget_eligible(
⋮----
def test_paid_budget_exhaustion_keeps_only_unmetered(self)
⋮----
def test_paid_budget_not_exhausted_keeps_all(self)
⋮----
def test_role_specific_model_overrides_default(self)
⋮----
provider = ProviderSpec(
⋮----
def test_json_provider_accepts_role_models(self)
⋮----
provider = providers[0]
⋮----
def test_vision_candidates_exclude_text_only_provider(self)
⋮----
vision = candidates_for("visual", screenshots=True, providers=providers)
```

## File: test_provider_runtime_reliability.py
```python
class ProviderRuntimeReliabilityTests(unittest.TestCase)
⋮----
def test_reliable_route_gets_positive_bonus(self)
⋮----
report = summarize({"workers": [
⋮----
def test_unstable_route_gets_negative_bonus(self)
⋮----
def test_sparse_evidence_has_bounded_influence(self)
⋮----
def test_admission_slot_events_do_not_pollute_provider_reputation(self)
```

## File: test_provider_scoped_health.py
```python
class ProviderScopedHealthTests(unittest.TestCase)
⋮----
def test_scoped_result_updates_global_and_specialized_health(self)
⋮----
path = Path(tmp) / "health.json"
⋮----
data = provider_health.load(path)
⋮----
def test_scoped_reliability_prefers_specialization(self)
⋮----
data = {
⋮----
def test_scoped_evidence_decays_after_one_half_life(self)
⋮----
fresh = provider_health.scoped_evidence(
stale = provider_health.scoped_evidence(
⋮----
def test_legacy_health_without_timestamp_keeps_full_freshness(self)
⋮----
evidence = provider_health.scoped_evidence(
⋮----
def test_recent_recovery_accelerates_reputation(self)
⋮----
def test_short_recovery_streak_does_not_trigger_acceleration(self)
⋮----
evidence = provider_health.scoped_evidence(data, "p", now=1000.0)
⋮----
def test_scoped_reliability_falls_back_to_provider(self)
⋮----
data = {"p": {"successes": 3, "failures": 1}}
```

## File: test_provider_verified_feedback.py
```python
class ProviderVerifiedFeedbackTests(unittest.TestCase)
⋮----
def test_verified_success_updates_reliability_and_latency(self)
⋮----
path = Path(tmp) / "health.json"
⋮----
snapshot = provider_health.health_snapshot(path, now=0)
⋮----
def test_verified_failures_open_circuit(self)
⋮----
snapshot = provider_health.health_snapshot(path, now=100)
⋮----
def test_unverified_non_boolean_outcome_is_rejected(self)
```

## File: test_queue_terminal_state.py
```python
class QueueTerminalStateTests(unittest.TestCase)
⋮----
def request(self, root, project_id, target)
⋮----
value={
path=Path(root)/(project_id+".json")
⋮----
def test_terminal_goal_is_not_requeued(self)
⋮----
rows=matrix(td,{"done"})
⋮----
def test_validated_priority_and_budgets_are_propagated(self)
⋮----
row=matrix(td)[0]
⋮----
def test_unknown_terminal_id_is_harmless(self)
```

## File: test_quick_gate_cache.py
```python
class QuickGateCacheTests(unittest.TestCase)
⋮----
def test_same_delta_and_workspace_produce_same_key(self)
⋮----
files = [{"path": "lib/app.dart", "content": "a"}]
snapshot = {"lib/app.dart": "a", "pubspec.yaml": "name: demo\n"}
d1 = delta_hash(files)
d2 = delta_hash(list(reversed(files)))
w1 = workspace_hash(snapshot)
w2 = workspace_hash(dict(reversed(list(snapshot.items()))))
⋮----
def test_same_delta_on_different_workspace_does_not_collide(self)
⋮----
digest = delta_hash(files)
w1 = workspace_hash({
w2 = workspace_hash({
⋮----
def test_test_targets_are_part_of_cache_key(self)
⋮----
digest = delta_hash([{"path": "lib/app.dart", "content": "a"}])
workspace = workspace_hash({"lib/app.dart": "a"})
```

## File: test_readiness.py
```python
class ReadinessTests(unittest.TestCase)
⋮----
def _root(self, td)
⋮----
root = Path(td)
⋮----
def test_missing_runtime_state_paths_prevent_readiness(self)
⋮----
root = self._root(td)
⋮----
result = readiness.check(root)
⋮----
def test_all_runtime_prerequisites_can_pass(self)
⋮----
env = {
```

## File: test_recovery_controller.py
```python
class RecoveryControllerTests(unittest.TestCase)
⋮----
def test_first_pause_registers_context_without_immediate_retry(self)
⋮----
result = evaluate(
⋮----
def test_material_context_change_grants_single_bounded_recovery(self)
⋮----
path = Path(td) / "recovery.json"
⋮----
first = evaluate(path, project_id="a", paused=True, context={"sha": "2"})
repeated = evaluate(path, project_id="a", paused=True, context={"sha": "2"})
⋮----
def test_successful_unpause_resets_recovery_memory(self)
⋮----
reset = evaluate(path, project_id="a", paused=False, context={"sha": "2"})
⋮----
again = evaluate(path, project_id="a", paused=True, context={"sha": "3"})
```

## File: test_registry_promotion_review_state.py
```python
def awaiting_candidate_review()
⋮----
state=new_state("project","image_assets","improvement:1")
state=record_research(state,"research_complete")
state=record_synthesis(state,"a"*64)
state=record_validation(state,"candidate_validated")
⋮----
class RegistryPromotionReviewStateTests(unittest.TestCase)
⋮----
def test_registry_pr_transitions_to_awaiting_registry_merge(self)
⋮----
state=record_registry_promotion_persistence(
⋮----
def test_idempotent_registry_pr_result_is_accepted(self)
⋮----
def test_unproved_registry_persistence_fails_closed(self)
⋮----
def test_wrong_source_state_fails_closed(self)
```

## File: test_release_candidate_search.py
```python
STATE = {
⋮----
class PassingSandbox
⋮----
def __init__(self, root)
⋮----
def quick_gates(self)
⋮----
def gates(self, name, journeys)
⋮----
class FailingSandbox
⋮----
class ReleaseCandidateSearchTests(unittest.TestCase)
⋮----
def test_candidate_isolation_restores_workspace(self)
⋮----
root = Path(td)
source = root / "lib/app.dart"
⋮----
def mutate()
⋮----
candidate = run_candidate(
⋮----
def test_generated_flutter_artifacts_are_purged_between_candidates(self)
⋮----
goldens = root / "test/goldens"
⋮----
def test_failed_candidate_cannot_contaminate_next_candidate(self)
⋮----
def bad()
⋮----
first = run_candidate(
⋮----
def good()
⋮----
second = run_candidate(
⋮----
def test_failed_first_gate_gets_one_local_refinement(self)
⋮----
gate_calls = {"count": 0}
⋮----
class FlakySandbox
⋮----
def first_step(intermediate_failure=None)
⋮----
def refine(failure)
⋮----
candidate = run_branch(
⋮----
def test_multi_step_branch_preserves_step_order(self)
⋮----
order = []
⋮----
def agent_step(intermediate_failure=None)
⋮----
def model_step(intermediate_failure=None)
⋮----
def test_diff_aware_quick_gates_skip_pub_get_and_target_matching_test(self)
⋮----
source = root / "lib/services/api.dart"
⋮----
test = root / "test/services/api_test.dart"
⋮----
calls = []
⋮----
class DiffAwareSandbox
⋮----
def quick_dependency_gate(self)
⋮----
def quick_analyze_gate(self)
⋮----
def quick_test_gate(self, targets=())
⋮----
def second_step(intermediate_failure=None)
⋮----
def test_progressive_quick_gates_stop_before_tests_when_analyze_fails(self)
⋮----
class ProgressiveSandbox
⋮----
def quick_test_gate(self)
⋮----
def test_progressive_quick_gates_reach_tests_only_after_analyze_passes(self)
⋮----
def test_failed_quick_gate_prunes_unpromising_branch_before_full_gates(self)
⋮----
full_gate_calls = {"count": 0}
⋮----
class PruningSandbox
⋮----
def test_quick_gate_failure_is_passed_to_next_step_when_continuing(self)
⋮----
received = []
⋮----
class RecoverableSandbox
⋮----
def test_identical_delta_reuses_quick_gate_cache_across_branches(self)
⋮----
calls = {"analyze": 0, "test": 0}
shared_cache = {}
⋮----
class CacheSandbox
⋮----
def test_different_delta_content_does_not_reuse_quick_gate_cache(self)
⋮----
calls = {"analyze": 0}
⋮----
def run_with(value)
⋮----
def test_identical_full_candidate_validation_is_reused(self)
⋮----
full_calls = {"count": 0}
shared_full_cache = {}
shared_artifact_cache = {}
cache_env = {
⋮----
class FullCacheSandbox
⋮----
apk = self.root / "build/app/outputs/flutter-apk/app-debug.apk"
⋮----
goldens = self.root / "test/goldens"
⋮----
def mutate(intermediate_failure=None)
⋮----
first = run_branch(
second = run_branch(
⋮----
def test_missing_cas_blob_falls_back_to_full_validation(self)
⋮----
key = first["full_validation_key"]
apk_meta = shared_artifact_cache[key]["files"]["build/app/outputs/flutter-apk/app-debug.apk"]
⋮----
def test_verified_candidate_with_better_score_wins(self)
⋮----
candidates = [
winner = select_winner(candidates)
⋮----
def test_apply_winner_materializes_only_selected_patch(self)
```

## File: test_release_contract.py
```python
class ReleaseContractTests(unittest.TestCase)
⋮----
def _root(self, td, version="1.2.0", gates=None)
⋮----
root = Path(td)
⋮----
gates = gates or list(release_contract.WORKFLOW_NAMES)
manifest = {
⋮----
path = root / rel
⋮----
def test_valid_release_contract_passes(self)
⋮----
root = self._root(td)
report = release_contract.validate(root)
⋮----
def test_version_mismatch_fails(self)
⋮----
path = root / "control/release.json"
manifest = json.loads(path.read_text(encoding="utf-8"))
⋮----
def test_missing_required_workflow_fails(self)
⋮----
missing = root / release_contract.WORKFLOW_NAMES["CI"]
⋮----
def test_missing_gate_from_manifest_fails(self)
⋮----
gates = [
root = self._root(td, gates=gates)
```

## File: test_release_readiness.py
```python
class ReleaseReadinessTests(unittest.TestCase)
⋮----
def test_complete_project_is_ready(self)
⋮----
root = Path(td)
autonomy = root / ".autonomy"
⋮----
checkpoint_path = autonomy / "workflow-checkpoints.json"
⋮----
key = operation_key("test", {"x": 1})
⋮----
result = assess(root)
⋮----
def test_incomplete_project_is_rejected(self)
```

## File: test_release_repair.py
```python
STATE = {
⋮----
class NeverModel
⋮----
def __init__(self, limit)
⋮----
class ReleaseRepairTests(unittest.TestCase)
⋮----
def test_credentials_abort_before_model_call(self)
⋮----
root = Path(td)
source = root / "lib/app.dart"
⋮----
@patch("release_repair._agent_candidates", return_value=["fake-agent"])
@patch("release_repair._run_agent")
    def test_credentials_abort_before_agent_access(self, run_agent, candidates)
⋮----
@patch("release_repair._agent_candidates", return_value=["fake-agent"])
@patch("release_repair.choose_strategy")
@patch("release_repair._run_agent")
    def test_agent_only_strategy_uses_no_model_call(self, run_agent, choose_strategy, candidates)
⋮----
def edit(root, blockers, stage, failure=None)
⋮----
class PassingSandbox
⋮----
def __init__(self, root)
⋮----
def gates(self, name, journeys)
⋮----
class CandidateModel
⋮----
def ask(self, role, context, screenshots=())
⋮----
result = attempt(
⋮----
agent_candidate = next(
⋮----
@patch("release_repair.save_artifact_cache", side_effect=StudioError("artifact cache unavailable"))
@patch("release_repair.save_full_gate_cache", side_effect=OSError("full cache disk error"))
@patch("release_repair.save_persistent_quick_cache", side_effect=OSError("quick cache disk error"))
    def test_cache_persistence_failures_are_non_fatal(self, quick_save, full_save, artifact_save)
⋮----
result = _persist_caches({"q": {}}, {"f": {}}, {"a": {}})
⋮----
def test_release_fix_checkpoint_replay_does_not_spend_model_budget(self)
⋮----
class ReplayModel
⋮----
checkpoint = root / "checkpoints.json"
⋮----
first = _model_mutation(
⋮----
second = _model_mutation(
```

## File: test_release_stage_engine.py
```python
class ReleaseStageEngineTests(unittest.TestCase)
⋮----
def test_environment_failure_is_not_sent_to_repair_agent(self)
⋮----
calls = []
⋮----
def validator(root, out)
⋮----
evidence = evaluate_and_repair(
⋮----
def test_transient_environment_failure_retries_without_model(self)
⋮----
responses = iter([
⋮----
def test_code_failure_repairs_then_requires_fresh_release_artifact(self)
⋮----
def test_source_change_invalidates_all_old_release_evidence(self)
⋮----
state = {
changed = invalidate_for_source_change(
⋮----
def test_external_evidence_becomes_human_action(self)
⋮----
state = {"status": "validated_preview", "release_status": "not_store_ready"}
evidence = {
changed = apply_external_gate(state, "billing_qa", evidence)
```

## File: test_release_v130.py
```python
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GATES = [
⋮----
class ReleaseV130Tests(unittest.TestCase)
⋮----
def test_version_and_manifest_are_final_stable_v130(self)
⋮----
manifest = json.loads((ROOT / "control" / "release.json").read_text(encoding="utf-8"))
⋮----
def test_final_release_notes_document_stability_contract(self)
⋮----
notes = (ROOT / "docs" / "RELEASE_V1.3.0.md").read_text(encoding="utf-8")
⋮----
def test_readme_exposes_safe_handoff_and_read_only_status(self)
⋮----
readme = (ROOT / "README.md").read_text(encoding="utf-8")
```

## File: test_release.py
```python
class FakeSandbox
⋮----
def __init__(self, root, fail_at=None)
⋮----
def run(self, args, network=False, timeout=0)
⋮----
p = self.root / "build/app/outputs/bundle/release/app-release.aab"
⋮----
p = self.root / "build/app/outputs/flutter-apk/app-release.apk"
⋮----
class ReleaseBuildTests(unittest.TestCase)
⋮----
def test_release_build_collects_store_and_installable_evidence(self)
⋮----
root = Path(td)
result = build_release(root, FakeSandbox(root))
⋮----
def test_release_build_stops_on_first_failure(self)
⋮----
sandbox = FakeSandbox(root, fail_at=2)
result = build_release(root, sandbox)
```

## File: test_repair_planner.py
```python
class RepairPlannerTests(unittest.TestCase)
⋮----
def test_human_action_has_priority_over_code(self)
⋮----
result = plan(
⋮----
def test_environment_prevents_blind_code_repair(self)
⋮----
def test_preview_failure_becomes_code_repair_task(self)
⋮----
result = preview_plan("code_review", ["Missing persistence"])
⋮----
def test_empty_diagnostics_are_complete(self)
⋮----
result = preview_plan("preview", [])
```

## File: test_repair_queue.py
```python
class RepairQueueTests(unittest.TestCase)
⋮----
def test_task_is_persistent_scored_and_selected(self)
⋮----
state = {}
task = enqueue(
⋮----
def test_completed_recurring_task_reactivates_and_rotates_strategy(self)
⋮----
plan = {
task = enqueue(state, plan, estimated_model_calls=1)
⋮----
def test_attempt_budget_exhausts_task(self)
⋮----
def test_begin_attempt_claims_worker_lease_and_finish_releases_it(self)
⋮----
def test_expired_running_task_is_recovered_and_selected(self)
⋮----
recovered = recover_expired_leases(state, now=131.0)
```

## File: test_repair_search_policy.py
```python
class RepairSearchPolicyTests(unittest.TestCase)
⋮----
def test_does_not_expand_when_budget_is_insufficient(self)
⋮----
row = {
⋮----
def test_expands_promising_branch_without_verified_winner(self)
⋮----
def test_strong_verified_winner_stops_further_expansion(self)
⋮----
def test_refinement_requires_value_and_budget(self)
```

## File: test_repair_strategy.py
```python
class RepairStrategyTests(unittest.TestCase)
⋮----
def test_stage_context_can_select_different_mature_strategy(self)
⋮----
root = Path(td)
global_path = root / "global.json"
contextual_path = root / "contextual.json"
env = {
⋮----
result = choose(
⋮----
def test_stagnation_rotates_away_from_last_strategy(self)
⋮----
def test_agent_to_model_is_available_when_agent_exists(self)
⋮----
def test_without_agent_bootstraps_model_only(self)
```

## File: test_replacement_ci_policy.py
```python
class ReplacementCIPolicyTests(unittest.TestCase)
⋮----
def test_repository_ci_exposes_required_check_ids(self)
⋮----
root=Path(__file__).resolve().parents[1]
result=validate_workflow(root/".github/workflows/ci.yml")
⋮----
def test_missing_required_check_is_detected(self)
⋮----
path=Path(td)/"ci.yml"
⋮----
result=validate_workflow(path)
⋮----
def test_required_check_runs_must_be_trusted_and_successful(self)
⋮----
runs=[
result=validate_check_runs(runs,"o/r",commit_sha="abc",head_commit_timestamp=1767225600.0)
⋮----
def test_untrusted_check_run_does_not_satisfy_policy(self)
⋮----
result=validate_check_runs(runs,"o/r")
⋮----
def test_stale_check_run_is_rejected(self)
⋮----
def test_wrong_sha_check_run_is_rejected(self)
⋮----
def test_required_checks_from_multiple_workflow_runs_are_rejected(self)
⋮----
def test_workflow_text_requires_canonical_name_and_jobs(self)
⋮----
text="name: CI\npermissions:\n  contents: read\njobs:\n  validate:\n  python-tests:\n"
⋮----
def test_workflow_text_rejects_wrong_name(self)
⋮----
result=validate_workflow_text("name: Other\njobs:\n  validate:\n  python-tests:\n")
⋮----
def test_workflow_text_rejects_missing_required_job(self)
⋮----
result=validate_workflow_text("name: CI\npermissions:\n  contents: read\njobs:\n  python-tests:\n")
⋮----
def test_workflow_actions_must_be_allowlisted_and_sha_pinned(self)
⋮----
text=(
result=validate_action_pinning_text(text)
⋮----
def test_mutable_action_ref_is_rejected(self)
⋮----
def test_third_party_action_is_rejected(self)
⋮----
def test_unapproved_sha_for_trusted_action_is_rejected(self)
⋮----
def test_local_action_is_fail_closed(self)
⋮----
result=validate_action_pinning_text("jobs:\n  validate:\n    steps:\n      - uses: ./local-action\n")
⋮----
def test_workflow_permissions_are_exact_least_privilege(self)
⋮----
result=validate_workflow_permissions_text("permissions:\n  contents: read\njobs:\n")
⋮----
def test_workflow_write_permission_is_rejected(self)
⋮----
result=validate_workflow_permissions_text("permissions:\n  contents: write\njobs:\n")
⋮----
def test_extra_sensitive_permission_is_rejected(self)
⋮----
result=validate_workflow_permissions_text(
⋮----
def test_job_permission_override_is_rejected(self)
⋮----
def test_missing_explicit_permissions_is_rejected(self)
⋮----
result=validate_workflow_permissions_text("name: CI\njobs:\n  validate:\n")
⋮----
def test_runtime_policy_accepts_repository_ci(self)
⋮----
result=validate_workflow_runtime_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_pull_request_target_is_rejected(self)
⋮----
result=validate_workflow_runtime_text("on:\n  pull_request_target:\njobs:\n")
⋮----
def test_container_is_rejected(self)
⋮----
result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    container: python:3.12\n")
⋮----
def test_secret_expression_is_rejected(self)
⋮----
result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    env:\n      TOKEN: ${{ secrets.TOKEN }}\n")
⋮----
def test_required_runner_and_timeout_are_exact(self)
⋮----
result=validate_workflow_runtime_text("jobs:\n  validate:\n    runs-on: self-hosted\n    timeout-minutes: 30\n  python-tests:\n    runs-on: ubuntu-latest\n    timeout-minutes: 20\n")
⋮----
reasons={v["reason"] for v in result["violations"]}
⋮----
def test_expression_policy_rejects_untrusted_contexts(self)
⋮----
result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    env:\n      X: ${{ github.event.pull_request.title }}\n")
⋮----
def test_matrix_strategy_is_rejected(self)
⋮----
result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    strategy:\n      matrix:\n        python: [3.12]\n")
⋮----
def test_job_needs_and_if_are_rejected(self)
⋮----
result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    needs: build\n    if: success()\n")
⋮----
keys={v.get("key") for v in result["violations"]}
⋮----
def test_continue_on_error_is_rejected(self)
⋮----
result=validate_workflow_expression_policy_text("jobs:\n  validate:\n    continue-on-error: true\n")
⋮----
def test_static_safe_workflow_has_no_expression_violations(self)
⋮----
result=validate_workflow_expression_policy_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_run_policy_accepts_repository_ci(self)
⋮----
result=validate_workflow_run_commands_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_run_policy_rejects_network_download(self)
⋮----
result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: curl https://example.invalid/file\n")
⋮----
def test_run_policy_rejects_runtime_dependency_install(self)
⋮----
result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: pip install example\n")
⋮----
def test_run_policy_rejects_github_command_file(self)
⋮----
result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: echo X=1 >> $GITHUB_ENV\n")
⋮----
def test_run_policy_rejects_expression_in_command(self)
⋮----
result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - run: echo ${{ github.ref }}\n")
⋮----
def test_run_policy_rejects_untrusted_shell(self)
⋮----
result=validate_workflow_run_commands_text("jobs:\n  validate:\n    steps:\n      - shell: pwsh\n        run: echo ok\n")
⋮----
def test_yaml_surface_rejects_anchors_aliases_and_merge_keys(self)
⋮----
result=validate_yaml_surface_text(text)
⋮----
def test_yaml_surface_rejects_tags(self)
⋮----
result=validate_yaml_surface_text("value: !custom thing\n")
⋮----
def test_yaml_surface_rejects_duplicate_mapping_keys(self)
⋮----
result=validate_yaml_surface_text("permissions:\n  contents: read\n  contents: write\n")
⋮----
def test_yaml_surface_rejects_tab_indentation(self)
⋮----
result=validate_yaml_surface_text("jobs:\n\tvalidate:\n")
⋮----
def test_repository_ci_yaml_surface_is_unambiguous(self)
⋮----
result=validate_yaml_surface_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_schema_rejects_unknown_root_job_and_step_keys(self)
⋮----
samples=(
⋮----
result=validate_workflow_schema_text(text)
⋮----
def test_schema_accepts_repository_ci(self)
⋮----
result=validate_workflow_schema_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_schema_allowlists_are_reported(self)
⋮----
result=validate_workflow_schema_text("name: CI\n")
⋮----
def test_step_inputs_env_accepts_repository_ci(self)
⋮----
result=validate_step_inputs_env_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_setup_python_only_accepts_312(self)
⋮----
text="jobs:\n  validate:\n    steps:\n      - name: Setup\n        uses: actions/setup-python@sha\n        with:\n          python-version: \"3.13\"\n"
result=validate_step_inputs_env_text(text)
⋮----
def test_unknown_action_input_is_rejected(self)
⋮----
text="jobs:\n  validate:\n    steps:\n      - name: Setup\n        uses: actions/setup-python@sha\n        with:\n          cache: pip\n"
⋮----
def test_checkout_inputs_are_fail_closed(self)
⋮----
text="jobs:\n  validate:\n    steps:\n      - name: Checkout\n        uses: actions/checkout@sha\n        with:\n          persist-credentials: true\n"
⋮----
def test_run_env_only_allows_static_pythonpath(self)
⋮----
good="jobs:\n  validate:\n    steps:\n      - name: Test\n        env:\n          PYTHONPATH: studio\n        run: python -m unittest\n"
bad="jobs:\n  validate:\n    steps:\n      - name: Test\n        env:\n          TOKEN: value\n        run: python -m unittest\n"
⋮----
def test_trigger_concurrency_accepts_repository_ci(self)
⋮----
result=validate_trigger_concurrency_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_extra_trigger_is_rejected(self)
⋮----
text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\n  workflow_dispatch:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: true\n"
⋮----
def test_non_main_push_branch_is_rejected(self)
⋮----
text="on:\n  push:\n    branches: [\"dev\"]\n  pull_request:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: true\n"
⋮----
def test_concurrency_group_must_be_exact(self)
⋮----
text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\nconcurrency:\n  group: arbitrary\n  cancel-in-progress: true\n"
⋮----
def test_concurrency_cancellation_must_be_enabled(self)
⋮----
text="on:\n  push:\n    branches: [\"main\"]\n  pull_request:\nconcurrency:\n  group: ci-${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: false\n"
⋮----
def test_exact_job_steps_accept_repository_ci(self)
⋮----
result=validate_exact_job_steps_text((root/".github/workflows/ci.yml").read_text())
⋮----
def test_exact_job_steps_reject_extra_job(self)
⋮----
text=(root/".github/workflows/ci.yml").read_text()+"\n  surprise:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Surprise\n        run: echo nope\n"
⋮----
def test_exact_job_steps_reject_reordered_steps(self)
⋮----
text=(root/".github/workflows/ci.yml").read_text()
text=text.replace("      - name: Checkout\n        uses: actions/checkout@", "      - name: Checkout changed\n        uses: actions/checkout@",1)
⋮----
def test_exact_job_steps_reject_changed_command(self)
⋮----
text=(root/".github/workflows/ci.yml").read_text().replace("python -m compileall -q studio tests","python -m compileall studio tests")
⋮----
def test_semantic_digest_is_stable_for_repository_ci(self)
⋮----
first=workflow_semantic_manifest_text(text)
second=workflow_semantic_manifest_text(text)
⋮----
def test_validate_workflow_exposes_semantic_digest(self)
⋮----
def test_semantic_digest_refuses_untrusted_workflow(self)
⋮----
result=workflow_semantic_manifest_text("name: Other\njobs:\n")
```

## File: test_repo_maintenance.py
```python
class RepoMaintenanceTests(unittest.TestCase)
⋮----
def setUp(self)
⋮----
def test_archived_is_archived(self)
⋮----
result=classify({"archived":True,"pushed_at":"2026-09-01T00:00:00Z"},now=self.now)
⋮----
def test_recent_push_is_active(self)
⋮----
result=classify({"archived":False,"pushed_at":"2026-09-01T00:00:00Z"},now=self.now)
⋮----
def test_old_push_is_stale(self)
⋮----
result=classify({"archived":False,"pushed_at":"2025-01-01T00:00:00Z"},now=self.now)
⋮----
def test_missing_timestamp_is_unknown(self)
⋮----
result=classify({"archived":False},now=self.now)
```

## File: test_repo_version_probe.py
```python
class RepoVersionProbeTests(unittest.TestCase)
⋮----
def test_semver_major_is_extracted(self)
⋮----
def test_non_semver_is_unknown(self)
⋮----
def test_release_context_is_bounded(self)
⋮----
result=classify_release({"tag_name":"v5.1.0","prerelease":False,"draft":False})
```

## File: test_repository_research_provider.py
```python
class RepositoryResearchProviderTests(unittest.TestCase)
⋮----
SHA="a"*40
⋮----
def test_search_and_fetch_use_pinned_repository_provenance(self)
⋮----
root=Path(td)
⋮----
results=search("repeated failure implementation")
⋮----
def test_symlink_and_outside_url_fail_closed(self)
⋮----
root=Path(td); (root/"studio").mkdir()
outside=root/"outside.py"; outside.write_text("secret")
```

## File: test_request_budget.py
```python
BASE = {
⋮----
class RequestBudgetTests(unittest.TestCase)
⋮----
def test_accepts_project_budget_overrides(self)
⋮----
req = dict(BASE)
⋮----
result = request_check(req)
⋮----
def test_repair_budget_cannot_exceed_explicit_total_budget(self)
⋮----
def test_rejects_excessive_project_budget(self)
```

## File: test_request_contract.py
```python
BASE={
⋮----
class RequestContractTests(unittest.TestCase)
⋮----
def test_legacy_request_does_not_gain_play_publish_field(self)
⋮----
value=request_check(copy.deepcopy(BASE))
⋮----
def test_play_publish_opt_in_is_normalized(self)
⋮----
value=copy.deepcopy(BASE)
⋮----
checked=request_check(value)
⋮----
def test_commit_requires_enabled(self)
⋮----
def test_invalid_track_is_rejected(self)
```

## File: test_request_priority.py
```python
def _request(**overrides)
⋮----
value = {
⋮----
class RequestPriorityTests(unittest.TestCase)
⋮----
def test_priority_defaults_to_fifty(self)
⋮----
def test_priority_accepts_valid_range(self)
⋮----
def test_priority_rejects_invalid_values(self)
```

## File: test_resilience_soak.py
```python
class ResilienceSoakTests(unittest.TestCase)
⋮----
def test_repeated_state_checkpoint_lease_cycles_remain_bounded_and_clean(self)
⋮----
root = Path(td)
state_path = root / "runtime-state.json"
checkpoint_path = root / "workflow-checkpoints.json"
telemetry_path = root / "telemetry.jsonl"
lease_path = root / "task-leases.json"
env = {
⋮----
cycles = max(1, int(os.environ.get("STUDIO_SOAK_CYCLES", "40")))
⋮----
loaded = durable_state.load_recovering(state_path)
⋮----
key = workflow_checkpoint.operation_key(
⋮----
task = {
⋮----
final_state = durable_state.load(state_path)
⋮----
checkpoint_payload = json.loads(
⋮----
lease_payload = json.loads(lease_path.read_text(encoding="utf-8"))
⋮----
summary = telemetry.summarize(telemetry_path)
```

## File: test_routing_audit.py
```python
class RoutingAuditTests(unittest.TestCase)
⋮----
def test_audit_persists_explainable_decision_without_secrets(self)
⋮----
path = Path(td) / "routing-audit.json"
event = append(path, {
⋮----
raw = path.read_text()
⋮----
data = json.loads(raw)
⋮----
def test_audit_is_bounded(self)
⋮----
data = json.loads(path.read_text())
```

## File: test_routing_calibration.py
```python
class RoutingCalibrationTests(unittest.TestCase)
⋮----
def test_verified_high_quality_route_gets_positive_adjustment(self)
⋮----
audit = {"events": [{"winner": "p", "winner_model": "m"} for _ in range(12)]}
outcomes = [{"outcome": {"quality_score": 100, "successful": True}} for _ in range(12)]
report = build(audit, outcomes)
⋮----
def test_bad_verified_outcomes_reduce_route_score(self)
⋮----
outcomes = [{"outcome": {"quality_score": 0, "successful": False}} for _ in range(12)]
⋮----
def test_sparse_evidence_stays_near_neutral(self)
⋮----
report = build(
⋮----
def test_unknown_route_is_neutral(self)
```

## File: test_routing_history.py
```python
class RoutingHistoryTests(unittest.TestCase)
⋮----
def test_history_is_bounded_and_sanitized(self)
⋮----
path = Path(td) / "routing-history.json"
⋮----
def test_learning_adjusts_weights_conservatively(self)
⋮----
events = []
⋮----
weights = learned_weights(events, kind="provider", role="product")
⋮----
def test_weighted_total_applies_component_weights(self)
⋮----
total = weighted_total({"priority":100.0,"latency":10.0},{"priority":1.0,"latency":0.5})
```

## File: test_run_cost_controller.py
```python
class RunCostControllerTests(unittest.TestCase)
⋮----
def test_model_call_budget_forces_verification(self)
⋮----
c = RunCostController(total_budget_seconds=1000, max_model_calls=2)
⋮----
def test_excessive_agent_time_forces_verification(self)
⋮----
c = RunCostController(total_budget_seconds=1000, max_model_calls=20)
⋮----
def test_too_many_fallbacks_force_verification(self)
⋮----
c = RunCostController(total_budget_seconds=2000, max_model_calls=20)
⋮----
def test_near_total_budget_requests_stop(self)
⋮----
def test_snapshot_exposes_cumulative_costs(self)
⋮----
c = RunCostController(total_budget_seconds=1000, max_model_calls=10)
⋮----
snap = c.snapshot()
```

## File: test_runtime_health.py
```python
class RuntimeHealthTests(unittest.TestCase)
⋮----
def test_healthy_project_reports_runtime_signals(self)
⋮----
out = Path(td) / "project"
autonomy = out / ".autonomy"
⋮----
env = {
⋮----
key = workflow_checkpoint.operation_key("demo", {"x": 1})
⋮----
report = runtime_health.inspect(out)
⋮----
def test_corrupt_runtime_and_lease_state_is_degraded(self)
⋮----
def test_non_object_lease_state_is_degraded(self)
```

## File: test_runtime_journeys.py
```python
JOURNEYS = [{
⋮----
class RuntimeJourneyTests(unittest.TestCase)
⋮----
def test_render_uses_immutable_keys_and_ids(self)
⋮----
text = render_test('sample_app', JOURNEYS)
⋮----
def test_runner_restores_pubspec_and_lock(self)
⋮----
root = Path(td)
⋮----
calls = []
def runner(args, **kwargs)
result = run_on_device(root, JOURNEYS, 'emulator-5554', runner=runner)
⋮----
def test_failed_instrumentation_fails_closed(self)
⋮----
rc = 1 if args[:2] == ['flutter', 'test'] else 0
```

## File: test_runtime_soak.py
```python
class RuntimeSoakTests(unittest.TestCase)
⋮----
def test_persistent_stores_remain_bounded_under_repeated_cycles(self)
⋮----
root = Path(td)
env = {
⋮----
quick_entries = {
⋮----
key = wc.operation_key("soak", {"i": i})
⋮----
checkpoints = wc.load()
```

## File: test_safe_rewrite_learning.py
```python
class SafeRewriteLearningTests(unittest.TestCase)
⋮----
def test_attempt_and_finalize_round_trip(self)
⋮----
path = Path(td) / "learning.json"
⋮----
event = srl.finalize(
⋮----
summary = srl.summarize(path)
⋮----
def test_penalty_requires_minimum_samples(self)
⋮----
summary = {
⋮----
def test_repeated_poor_origin_gets_bounded_penalty(self)
⋮----
penalty = srl.routing_penalty(
⋮----
def test_non_implementation_roles_are_not_penalized(self)
⋮----
def test_origin_score_penalty_and_rewrite_bonus_are_asymmetric(self)
⋮----
penalty = srl.origin_violation_penalty(
bonus = srl.rewrite_recovery_bonus(
⋮----
def test_recovery_bonus_requires_evidence(self)
⋮----
def test_recent_events_have_more_weight_than_old_events(self)
⋮----
row = srl.summarize(path)["origin_rankings"][0]
⋮----
def test_recent_success_streak_marks_rehabilitation(self)
⋮----
outcomes = [False, False, False, False, False, True, True, True]
⋮----
def test_old_failures_decay_toward_exploration_floor(self)
⋮----
events = []
⋮----
penalty = srl.routing_penalty(summary, kind="provider", name="bad", role="implementation")
⋮----
def test_stale_actor_receives_bounded_exploration_bonus(self)
⋮----
bonus = srl.exploration_bonus(
⋮----
def test_recent_actor_has_no_exploration_bonus(self)
```

## File: test_security_agent.py
```python
class FakeModel
⋮----
def __init__(self, limit)
⋮----
def ask(self, role, context, screenshots=())
⋮----
class PassingSandbox
⋮----
def __init__(self, root)
⋮----
def gates(self, name, journeys)
⋮----
class FailingSandbox
⋮----
STATE = {
⋮----
class SecurityAgentTests(unittest.TestCase)
⋮----
def test_credentials_disable_external_agentic_repair(self)
⋮----
evidence = {
⋮----
def test_successful_patch_passes_trusted_gates(self)
⋮----
root = Path(td)
source = root / "lib/app.dart"
⋮----
result = attempt(
⋮----
def test_failed_trusted_gates_restore_original_source(self)
⋮----
original = "const endpoint = 'http://example.com';\n"
```

## File: test_security_remediation.py
```python
class SecurityRemediationTests(unittest.TestCase)
⋮----
def test_manifest_release_flags_are_hardened(self)
⋮----
root = Path(td)
manifest = root / "android/app/src/main/AndroidManifest.xml"
⋮----
evidence = {
⋮----
result = remediate(root, evidence)
text = manifest.read_text()
⋮----
def test_source_http_endpoint_is_not_blindly_rewritten(self)
⋮----
source = root / "lib/api.dart"
⋮----
evidence = {"blockers": ["cleartext_network_traffic_detected"]}
⋮----
def test_secrets_and_process_execution_are_not_auto_remediated(self)
```

## File: test_security_stage.py
```python
REQ = {
⋮----
def state_before_security()
⋮----
class FakeGitHub
⋮----
def __init__(self, *a, **k)
⋮----
def publish(self, *a, **k)
⋮----
class SecurityStageTests(unittest.TestCase)
⋮----
def test_human_review_classifier_only_selects_trust_decisions(self)
⋮----
blockers = [
⋮----
@patch("security_stage.GitHub", FakeGitHub)
@patch("security_stage.build_security_package")
    def test_security_trust_decision_becomes_human_action(self, build)
⋮----
root = Path(td)
out = root / "out"
⋮----
req = root / "request.json"
⋮----
result = advance(req, root / "work", out)
⋮----
@patch("security_stage.GitHub", FakeGitHub)
@patch("security_stage.build_security_package")
    def test_auto_fixable_security_failure_stays_machine_blocked(self, build)
⋮----
@patch("security_stage.GitHub", FakeGitHub)
@patch("security_stage.build_security_package")
    def test_resolved_human_action_clears_gate_and_finishes(self, build)
⋮----
state = state_before_security()
⋮----
@patch("security_stage.GitHub", FakeGitHub)
@patch("security_stage.remediate")
@patch("security_stage.build_security_package")
    def test_auto_remediation_rescans_until_converged(self, build, remediate_fn)
⋮----
evidence = result["release_evidence"]["security_scan"]
```

## File: test_security.py
```python
class SecurityAuditTests(unittest.TestCase)
⋮----
def make_app(self, root: Path, manifest: str = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application /></manifest>', dart: str = 'void main() {}', lock: str | None = None, pubspec: str = 'name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n')
⋮----
target = root / 'android/app/src/main'
⋮----
lib = root / 'lib'
⋮----
def test_clean_offline_app_passes(self)
⋮----
root = Path(tmp)
⋮----
audit = scan(root)
⋮----
def test_secret_material_fails_closed_without_exposing_value(self)
⋮----
def test_cleartext_endpoint_fails(self)
⋮----
def test_android_schema_url_is_not_mistaken_for_cleartext_endpoint(self)
⋮----
def test_dangerous_permission_fails(self)
⋮----
manifest = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-permission android:name="android.permission.READ_SMS"/><application /></manifest>'
⋮----
def test_lockfile_inventory_records_versions_and_sources(self)
⋮----
lock = '''packages:\n  characters:\n    dependency: transitive\n    description:\n      name: characters\n    source: hosted\n    version: "1.4.0"\n  flutter:\n    dependency: direct main\n    description: flutter\n    source: sdk\n    version: "0.0.0"\n'''
⋮----
inventory = dependency_inventory(root)
⋮----
def test_git_or_path_dependency_is_blocked(self)
⋮----
pubspec = '''name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  unsafe_pkg:\n    git: https://example.test/repo.git\n'''
⋮----
def test_hosted_dependency_requires_content_hash_and_trusted_registry(self)
⋮----
lock = '''packages:
⋮----
def test_cached_mit_license_and_hash_produce_resolved_dependency_evidence(self)
⋮----
digest = 'a' * 64
lock = f'''packages:
⋮----
cache = root / '.studio-cache/pub/hosted/pub.dev/demo_pkg-1.2.3'
⋮----
dep = audit['dependencies'][0]
⋮----
def test_unknown_dependency_license_blocks_release(self)
⋮----
digest = 'b' * 64
⋮----
cache = root / '.studio-cache/pub/hosted/pub.dev/mystery_pkg-9.9.9'
⋮----
def test_package_writes_hashed_audit_and_sbom(self)
⋮----
root = Path(tmp) / 'app'
out = Path(tmp) / 'out'
⋮----
evidence = build_security_package(root, out)
```

## File: test_stage_registry.py
```python
class StageRegistryTests(unittest.TestCase)
⋮----
def test_registry_contains_required_trusted_stages(self)
⋮----
required = {
⋮----
def test_generic_runner_advances_until_finished(self)
⋮----
out = Path(tmp) / 'out'
⋮----
project = {'file': 'control/mobile-requests/demo.json'}
sequence = ['real_device', 'capability_qa', 'store_metadata', 'artwork_qa', 'privacy_policy', 'security_scan']
state = {'completion': {'finished': False, 'next_stage': sequence[0]}}
⋮----
calls = []
def runner(args, timeout)
⋮----
current = json.loads((out / 'report.json').read_text())
name = current['completion']['next_stage']
index = sequence.index(name)
⋮----
def test_success_without_state_advance_fails_closed(self)
⋮----
state = {'completion': {'finished': False, 'next_stage': 'real_device'}}
⋮----
def test_deadline_returns_stage_specific_deferred_status(self)
⋮----
state = {'completion': {'finished': False, 'next_stage': 'privacy_policy'}}
```

## File: test_stagnation_controller.py
```python
class StagnationControllerTests(unittest.TestCase)
⋮----
def test_sparse_evidence_is_neutral(self)
⋮----
decision = decide([{"samples": 2, "failure_streak": 2, "ema_success": 0.0}])
⋮----
def test_three_failures_trigger_diversification(self)
⋮----
decision = decide([{"samples": 3, "failure_streak": 3, "ema_success": 0.2}])
⋮----
def test_five_failures_throttle_capacity(self)
⋮----
decision = decide([{"samples": 6, "failure_streak": 5, "ema_success": 0.1}])
⋮----
def test_eight_failures_pause_branch(self)
⋮----
decision = decide([{"samples": 8, "failure_streak": 8, "ema_success": 0.0}])
⋮----
def test_success_resets_stagnation(self)
⋮----
decision = decide([{"samples": 10, "failure_streak": 0, "ema_success": 0.4}])
⋮----
def test_summary_counts_actions(self)
⋮----
result = summarize({"rows": [
```

## File: test_star_recommendations.py
```python
CATALOG = {
⋮----
class StarScannerTests(unittest.TestCase)
⋮----
def test_structured_catalog_ranking_respects_constraints(self)
⋮----
path = Path(tmp) / "catalog.json"
⋮----
result = star_scanner.scan(
⋮----
def test_markdown_parser_accepts_scored_rows(self)
⋮----
text = "- owner/repo — 9.7/10 — CORE\n- other/repo\n"
⋮----
def test_project_recommendation_writes_evidence(self)
⋮----
out = Path(tmp)
fake = {
⋮----
result = recommend("browser", out, platform="web")
⋮----
written = json.loads((out / "star-recommendations.json").read_text())
⋮----
def test_run_loads_bounded_recommendation_evidence(self)
⋮----
root = Path(tmp)
payload = {
⋮----
result = _load_star_recommendations(root)
⋮----
def test_model_context_contains_recommendations_as_data(self)
⋮----
state = {"technical_recommendations": {"status": "ok", "matches": [{"repo": "owner/repo"}]}, "architecture_decision": {"status": "planned", "chosen": [{"repo": "owner/repo"}]}, "architecture_benchmark": {"status": "benchmarked", "migration_candidates": [{"best_alternative": "owner/alt"}]}, "architecture_replacement_work_orders": {"status": "planned", "work_orders": [{"id": "replace-1", "current_repo": "owner/repo", "replacement_repo": "owner/alt"}]}, "architecture_replacement_learning": {"outcomes_observed": 5, "rankings": [{"current_repo": "owner/repo", "replacement_repo": "owner/alt", "samples": 5, "success_rate": 1.0}]}, "architecture_drift_alerts": [{"type": "repository", "repo": "owner/repo", "score": 1.0}]}
payload = json.loads(build_context({"brief": "test"}, state, root))
⋮----
def test_load_architecture_benchmark_is_bounded(self)
⋮----
result = _load_architecture_benchmark(root)
⋮----
def test_load_replacement_work_orders_is_bounded(self)
⋮----
result = _load_architecture_replacement_work_orders(root)
⋮----
def test_recommendation_context_uses_project_brief(self)
⋮----
path = Path(tmp) / "request.json"
⋮----
result = _recommendation_context(path)
```

## File: test_store.py
```python
class StorePackageTests(unittest.TestCase)
⋮----
def make_png(self, path: Path, width=360, height=800, rgb=(20, 30, 40))
⋮----
pixel = bytes((*rgb, 255))
⋮----
def test_listing_is_bounded_and_derived_from_brief(self)
⋮----
req = {
state = {'product': {'acceptance_criteria': ['Start and stop a focus timer reliably.'], 'journeys': [{'id': 'focus', 'steps': []}]}}
listing = listing_from_state(req, state)
⋮----
def test_builds_valid_assets_and_permission_evidence(self)
⋮----
base = Path(td)
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
state = {'design': {'primary': '#102030', 'accent': '#5060F6'}}
listing = {
evidence = build_store_package(root, out, state, listing)
⋮----
store = out / 'play-store'
⋮----
shot = store / 'screenshots/phone/01.png'
⋮----
manifest_data = json.loads((store / 'manifest.json').read_text())
⋮----
def test_refuses_package_without_two_distinct_validated_screens(self)
```

## File: test_strategy_efficiency.py
```python
class StrategyEfficiencyTests(unittest.TestCase)
⋮----
def test_strategy_requires_four_samples(self)
⋮----
path=Path(td)/"strategy-efficiency.json"
⋮----
def test_best_strategy_prefers_verified_success_per_cost(self)
⋮----
best=best_strategy(load(path))
⋮----
def test_exploration_is_more_frequent_when_strategies_are_close(self)
⋮----
data={
⋮----
def test_exploration_decays_for_durable_dominant_strategy(self)
⋮----
def test_exploration_never_disappears(self)
⋮----
cadence=exploration_cadence(data,allowed={"model_only","dual"})
⋮----
selected=select_strategy(
⋮----
def test_bandit_exploits_best_strategy_outside_exploration_window(self)
⋮----
selected=select_strategy(data,allowed={"model_only","dual"},exploration_every=6)
⋮----
def test_bandit_explores_least_sampled_alternative_on_cadence(self)
⋮----
def test_bandit_requires_mature_strategy_before_exploration(self)
⋮----
def test_recent_failures_can_dethrone_historical_winner(self)
⋮----
def test_regime_shift_increases_exploration_frequency(self)
⋮----
def test_legacy_strategy_rows_migrate_recent_success_from_cumulative_rate(self)
⋮----
row=load(path)["model_only"]
⋮----
def test_uncertainty_decreases_with_more_evidence(self)
⋮----
low={
high={
⋮----
def test_risk_adjustment_can_prefer_mature_strategy(self)
⋮----
def test_metrics_expose_conservative_and_optimistic_efficiency(self)
⋮----
info=metrics(data,"model_only")
⋮----
def test_failure_rate_reduces_efficiency(self)
```

## File: test_strict_task_claim_store.py
```python
def _claim_in_process(path, result_path)
⋮----
class StrictTaskClaimStoreTests(unittest.TestCase)
⋮----
def test_corrupt_store_is_rejected_under_lock(self)
⋮----
path = Path(td) / "leases.json"
⋮----
def test_second_process_cannot_claim_live_task(self)
⋮----
result_path = Path(td) / "result.txt"
worker = multiprocessing.Process(
```

## File: test_studio.py
```python
REQUEST = {'id': 'demo-v1', 'target_repo': 'owner/mobile', 'app_name': 'demo_app',
JOURNEYS = [{'id': 'settings', 'steps': [{'action': 'tap', 'key': 'settings_button'}, {'action': 'expect_text', 'value': 'Settings'}]}]
PATCH = {'files': [{'path': 'lib/app.dart', 'content': 'source'}, {'path': 'test/app_test.dart', 'content': 'test'}]}
⋮----
class FakeGitHub
⋮----
def __init__(self)
def restore(self, branch, root)
⋮----
target = root / p
⋮----
def publish(self, branch, parent, root, state)
⋮----
class FakeModel
⋮----
vision = 'vision-model'
calls = 0
def __init__(self, limit)
def ask(self, role, context, screenshots=())
⋮----
class FakeSandbox
⋮----
def __init__(self, root)
def create(self, name)
def gates(self, name, journeys)
⋮----
p = self.root / 'build/app/outputs/flutter-apk/app-debug.apk'
⋮----
d = self.root / 'test/goldens'
⋮----
class StudioTests(unittest.TestCase)
⋮----
def test_request_defaults(self)
⋮----
req = {k: v for k, v in REQUEST.items() if not k.startswith('max_')}
⋮----
def test_request_rejects_injection_and_bad_types(self)
def test_paths(self)
def test_patch_atomic_validation(self)
⋮----
root = Path(d)
⋮----
def test_duplicate_and_secrets(self)
def test_symlink(self)
def test_verdict_fail_closed(self)
def test_http_endpoint(self)
def run_fixture(self, model=FakeModel, sandbox=FakeSandbox, gh=None)
⋮----
gh = gh or FakeGitHub()
temp = tempfile.TemporaryDirectory()
⋮----
root = Path(temp.name)
state = execute(copy.deepcopy(REQUEST), root / 'work', root / 'out', gh, model, sandbox)
⋮----
def test_full_pipeline_and_artifact(self)
def test_repair_loop(self)
⋮----
class RepairSandbox(FakeSandbox)
⋮----
def test_no_vision_is_not_completed(self)
⋮----
class NoVision(FakeModel)
⋮----
vision = ''
⋮----
def test_failed_build_does_not_export_stale_apk(self)
⋮----
class Failed(FakeSandbox)
⋮----
def test_visual_rejection_repairs(self)
⋮----
class Reject(FakeModel)
⋮----
r = super().ask(role, context, screenshots)
⋮----
def test_provider_error_checkpoints(self)
⋮----
class Broken(FakeModel)
⋮----
def test_completed_resume_skips_model_and_build(self)
⋮----
def forbidden(*args)
⋮----
def test_old_validation_contract_is_revalidated(self)
⋮----
previous_rounds = gh.state['rounds']
⋮----
def test_changed_brief_rejected(self)
def test_total_cycles_are_bounded(self)
def test_queue_duplicate_targets(self)
def test_empty_repository_initialized_through_contents(self)
⋮----
class Empty(GitHub)
⋮----
def get(self, path)
def call(self, method, path, data=None)
gh = Empty()
⋮----
def test_repository_access_error_never_initializes(self)
⋮----
class Denied(GitHub)
⋮----
def call(self, *args)
⋮----
def test_disabled_request_no_access(self)
def test_qa_supplies_missing_implementation_tests(self)
⋮----
class QA(FakeModel)
⋮----
def test_missing_tests_fails(self)
⋮----
class NoTests(FakeModel)
```

## File: test_task_claim_store.py
```python
def _try_claim(path, result_path)
⋮----
class TaskClaimStoreTests(unittest.TestCase)
⋮----
def test_second_process_cannot_claim_live_task(self)
⋮----
path = Path(td) / "leases.json"
⋮----
result_path = Path(td) / "result.txt"
worker = multiprocessing.Process(target=_try_claim, args=(path, result_path))
```

## File: test_task_context.py
```python
class TaskContextTests(unittest.TestCase)
⋮----
def test_explicit_bugfix_beats_backend_toolchain(self)
⋮----
def test_tests_context_is_detected(self)
⋮----
def test_mobile_context_is_detected(self)
⋮----
def test_frontend_context_is_detected(self)
⋮----
def test_backend_fallback_uses_toolchain(self)
⋮----
def test_hierarchy_falls_back_through_stack_and_general(self)
⋮----
def test_weighted_contexts_capture_multiple_task_signals(self)
⋮----
weighted = dict(weighted_contexts(
⋮----
def test_general_when_no_signal_exists(self)
```

## File: test_task_lease.py
```python
class TaskLeaseTests(unittest.TestCase)
⋮----
def test_second_worker_cannot_claim_active_lease(self)
⋮----
task = {"status": "running"}
⋮----
def test_owner_can_refresh_lease(self)
⋮----
token = task["lease_token"]
⋮----
def test_wrong_heartbeat_owner_is_rejected(self)
⋮----
def test_expired_running_task_is_recovered_for_retry(self)
⋮----
def test_release_clears_lease_metadata(self)
⋮----
def test_corrupted_persistent_lease_state_fails_closed(self)
⋮----
path = Path(td) / "leases.json"
⋮----
task = {"id": "task-1", "status": "pending"}
```

## File: test_task_scheduler.py
```python
def state_with_budget()
⋮----
class TaskSchedulerTests(unittest.TestCase)
⋮----
def test_selects_highest_scoring_runnable_task(self)
⋮----
state = state_with_budget()
⋮----
def test_human_task_is_not_auto_dispatched(self)
⋮----
def test_budget_infeasible_repair_is_not_dispatched(self)
⋮----
def test_unmet_dependency_blocks_task(self)
⋮----
def test_release_rebuild_prerequisite_dispatches_release_build(self)
⋮----
task = {
⋮----
def test_preview_task_dispatches_preview_stage(self)
⋮----
def test_expired_running_task_is_recovered_before_selection(self)
⋮----
selected = select(state)
```

## File: test_telemetry_maintenance.py
```python
class TelemetryMaintenanceTests(unittest.TestCase)
⋮----
def test_large_log_is_compacted_to_recent_tail(self)
⋮----
path = Path(td) / "telemetry.jsonl"
lines = [f'{{"kind":"event","n":{i}}}' for i in range(200)]
⋮----
result = tm.compact(path)
⋮----
text = path.read_text(encoding="utf-8")
⋮----
def test_small_log_is_left_unchanged(self)
⋮----
before = path.read_bytes()
```

## File: test_telemetry.py
```python
class TelemetryTests(unittest.TestCase)
⋮----
def test_emit_and_summarize(self)
⋮----
path = Path(td) / "telemetry.jsonl"
⋮----
summary = telemetry.summarize(path)
⋮----
def test_invalid_lines_do_not_break_summary(self)
```

## File: test_transport.py
```python
BASE = 'https://integrate.api.nvidia.com/v1'
RID = '12345678-1234-1234-1234-123456789abc'
⋮----
def response(status, body=None, rid=RID)
⋮----
obj = io.BytesIO(json.dumps(body or {}).encode())
⋮----
class TransportTests(unittest.TestCase)
⋮----
def call_with(self, replies, base=BASE)
⋮----
opener = Mock()
⋮----
result = API(base, 'test-token').call('POST', '/chat/completions', {})
⋮----
def test_pending_polls_same_origin_without_resubmitting(self)
⋮----
requests = [call.args[0] for call in opener.open.call_args_list]
⋮----
def test_rejects_untrusted_pending_ids_and_providers(self)
⋮----
def test_polling_has_a_hard_limit(self)
⋮----
def test_poll_error_never_resubmits_post(self)
⋮----
def test_non_json_response_is_clear(self)
⋮----
r = response(200)
⋮----
def test_transport_timeout_is_forwarded_to_http_open(self)
⋮----
result = API(BASE, 'test-token').call(
⋮----
def test_transport_timeout_is_clamped_to_safe_maximum(self)
⋮----
def test_retry_uses_one_total_timeout_budget(self)
⋮----
api = API(BASE, 'test-token')
transient = urllib.error.HTTPError(BASE, 503, 'busy', {}, None)
⋮----
result = api.call('POST', '/chat/completions', {}, timeout_seconds=10)
⋮----
first = response_call.call_args_list[0].kwargs['timeout_seconds']
second = response_call.call_args_list[1].kwargs['timeout_seconds']
⋮----
def test_completion_explicitly_disables_streaming(self)
⋮----
m = Model(1)
⋮----
class MalformedEnvelopeTests(unittest.TestCase)
⋮----
def test_bad_choices_trigger_bounded_repair_without_attribute_crash(self)
⋮----
invalid = [None, [], {}, {'choices': []}, {'choices': [None]},
⋮----
model = Model(2)
```

## File: test_unified_routing_score.py
```python
@dataclass
class Provider
⋮----
name: str = "p"
priority: int = 50
free_preferred: bool = False
unmetered: bool = False
monthly_token_quota: int = 0
⋮----
class UnifiedRoutingScoreTests(unittest.TestCase)
⋮----
def test_free_unmetered_provider_gets_bounded_resource_bonus(self)
⋮----
result = score(provider=Provider(free_preferred=True, unmetered=True), role="implementation", model="m")
⋮----
def test_runtime_and_latency_are_combined(self)
⋮----
runtime = {"routes": {"p::m": {"reliability_score": 0.9, "confidence": 1.0}}}
metrics = {"p:implementation": {"calls": 5, "ema_latency_seconds": 1.0}}
result = score(provider=Provider(), role="implementation", model="m", runtime=runtime, metrics=metrics)
⋮----
def test_context_and_exploration_are_strictly_bounded(self)
⋮----
result = score(
⋮----
def test_specialized_health_changes_score_by_role(self)
⋮----
health = {
implementation = score(
review = score(
⋮----
def test_missing_specialization_is_neutral_with_no_health(self)
⋮----
def test_sparse_specialization_has_limited_influence(self)
⋮----
sparse = score(
mature = score(
⋮----
def test_no_observations_have_zero_specialized_confidence(self)
⋮----
result = score(provider=Provider(), role="review", model="m", health={})
⋮----
def test_component_breakdown_sums_to_score(self)
⋮----
result = score(provider=Provider(priority=70, free_preferred=True), role="tests", model="m")
additive_keys = {
```

## File: test_v1_gate.py
```python
class V1GateTests(unittest.TestCase)
⋮----
def test_ready_host_without_project(self)
⋮----
readiness = {"ready": True, "checks": {"python": True}, "failed": []}
⋮----
report = v1_gate.evaluate(".")
⋮----
def test_operational_project_requires_healthy_runtime(self)
⋮----
runtime = {"status": "healthy", "errors": [], "runtime_status": "running"}
⋮----
report = v1_gate.evaluate(".", "out/project")
⋮----
def test_degraded_runtime_blocks_gate(self)
⋮----
runtime = {
⋮----
def test_host_readiness_failure_blocks_gate(self)
⋮----
readiness = {
```

## File: test_verification_cost.py
```python
class VerificationCostTests(unittest.TestCase)
⋮----
def test_stack_key_is_stable_for_multi_stack_repo(self)
⋮----
def test_ema_is_learned_per_toolchain(self)
⋮----
path=Path(td)/"verification-cost.json"
⋮----
data=load(path)
⋮----
def test_unknown_toolchain_uses_fallback_until_two_runs(self)
```

## File: test_worker_heartbeat.py
```python
class WorkerHeartbeatTests(unittest.TestCase)
⋮----
def test_marker_changes_with_checkpoint_progress(self)
⋮----
root = Path(td)
autonomy = root / ".autonomy"
⋮----
checkpoint = autonomy / "execution-checkpoint.json"
⋮----
first = progress_marker(root)
⋮----
second = progress_marker(root)
⋮----
def test_renew_passes_durable_marker_to_ledger(self)
⋮----
result = renew_if_progressed(
```

## File: test_worker_reaper.py
```python
class WorkerReaperTests(unittest.TestCase)
⋮----
def test_expired_claimed_worker_with_progress_is_stalled(self)
⋮----
root = Path(td)
ledger = root / "capacity-ledger.json"
⋮----
claim = claim_preemption_lease(ledger, "high", now=101, ttl_seconds=30)
⋮----
report = classify(root, now=141)
⋮----
def test_expired_unclaimed_preemption_lease_is_orphaned(self)
⋮----
report = classify(root, now=131)
⋮----
def test_expired_worker_without_heartbeat_is_crashed(self)
⋮----
report = classify(root, now=132)
⋮----
def test_terminal_project_is_classified_completed(self)
⋮----
project = root / "high"
```

## File: test_worker_reliability.py
```python
class WorkerReliabilityTests(unittest.TestCase)
⋮----
def test_failures_reduce_reliability_with_bounded_penalty(self)
⋮----
workers = [
report = summarize({"workers": workers})
row = report["projects"]["bad"]
⋮----
def test_completed_workers_improve_reliability(self)
⋮----
report = summarize({"workers": [
⋮----
def test_sparse_history_stays_close_to_neutral(self)
⋮----
def test_unknown_project_is_neutral(self)
```

## File: test_workflow_checkpoint.py
```python
class WorkflowCheckpointTests(unittest.TestCase)
⋮----
def test_completed_checkpoint_roundtrip(self)
⋮----
path = Path(td) / "checkpoint.json"
⋮----
key = wc.operation_key("release_fix", {"stage": "performance_qa", "x": 1})
value = {"patch": {"files": [{"path": "lib/app.dart", "content": "x"}]}}
⋮----
def test_operation_key_is_deterministic_and_context_sensitive(self)
⋮----
first = wc.operation_key("release_fix", {"a": 1, "b": 2})
second = wc.operation_key("release_fix", {"b": 2, "a": 1})
changed = wc.operation_key("release_fix", {"a": 1, "b": 3})
⋮----
def test_discard_removes_checkpoint(self)
⋮----
key = wc.operation_key("release_fix", {"x": 1})
⋮----
def test_stale_writer_merges_existing_checkpoints(self)
⋮----
first = wc.operation_key("one", {"x": 1})
second = wc.operation_key("two", {"x": 2})
⋮----
loaded = wc.load()
```

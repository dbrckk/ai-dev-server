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
````
agents/
  __init__.py
  adapters.py
  codex.py
  orchestrator.py
  performance.py
  registry.py
  router.py
  workspace.py
candidates/
  jumpy_profile_save.gd
capabilities/
  __init__.py
  asset_artwork.py
adaptation_research.py
adaptation.py
adaptive_phase_policy.py
adaptive_role_allocator.py
adaptive_scoring.py
android_signing.py
architecture_benchmark.py
architecture_change_guard.py
architecture_contract.py
architecture_evaluator.py
architecture_feedback.py
architecture_learning.py
architecture_obsolescence.py
architecture_outcome.py
architecture_planner.py
architecture_preflight.py
architecture_replacement_candidate.py
architecture_replacement_executor.py
architecture_replacement_learning.py
architecture_replacement_merge_gate.py
architecture_replacement_merge.py
architecture_replacement_outcome.py
architecture_replacement_persist.py
architecture_replacement_pipeline.py
architecture_replacement_planner.py
architecture_replacement_postmerge_pipeline.py
architecture_replacement_postmerge.py
architecture_replacement_pr_package.py
architecture_replacement_pr_validator.py
architecture_replacement_promotion.py
architecture_replacement_reputation.py
architecture_replacement_rollback_gate.py
architecture_replacement_rollback.py
architecture_replacement_synthesis.py
architecture_replacement_work_order.py
architecture_reputation_policy_approval.py
architecture_reputation_policy_github_attestation.py
architecture_reputation_policy_github_collect.py
architecture_reputation_policy_migration_cli.py
architecture_reputation_policy_migration_review.py
architecture_reputation_policy_migration.py
architecture_safe_rewrite.py
artifact_cas_audit.py
artifact_cas_namespace.py
artifact_cas_promotion.py
artifact_cas_stats.py
artifact_cas.py
artifact_handoff.py
artifact_share_policy.py
artwork_candidate_bridge.py
artwork_capability.py
artwork_stage.py
artwork_validation.py
atomic_file.py
autonomous_project.py
autonomous_research.py
billing_qa.py
billing_stage.py
candidate_portfolio_learning.py
capability_adaptation_state.py
capability_candidate_validator.py
capability_memory.py
capability_promotion.py
capability_qa.py
capability_registry_promotion_persist.py
capability_registry_review.py
capability_registry.py
capability_review.py
capability_runtime.py
capability_stage.py
capability_synthesis.py
capacity_budget.py
capacity_efficiency.py
capacity_ledger.py
capacity_runtime.py
capacity_scheduler.py
capacity_status.py
ci_provider.py
ci_runner.py
completion.py
contextual_routing_memory.py
contextual_strategy_efficiency.py
contextual_utility.py
continuous_improvement.py
core.py
cost_drift.py
device_qa.py
device_stage.py
diagnostics.py
diff_quick_gates.py
durable_state.py
engine_detect.py
engine_entry.py
engine_patch.py
evolution_automerge.py
evolution_benchmark.py
evolution_candidate.py
evolution_differential.py
evolution_evidence.py
evolution_executor.py
evolution_isolated_runner.py
evolution_pending.py
evolution_persist.py
evolution_promotion.py
evolution_research.py
evolution_rollback.py
evolution_stage_runner.py
evolution_synthesis.py
execution_budget.py
execution_checkpoint.py
existing_project.py
fault_injection_smoke.py
file_lock.py
fleet_capacity.py
fleet_daemon.py
fleet_dashboard.py
fleet_maintenance.py
fleet_metrics.py
fleet_regression.py
fleet_supervisor_apply.py
fleet_supervisor.py
flutter_workspace.py
free_capacity_recommendations.py
full_gate_cache.py
generic_capability_isolated_validation.py
generic_capability_persist.py
generic_capability_synthesis.py
generic_model.py
generic_policy.py
generic_project.py
generic_repository.py
generic_sandbox.py
generic_smoke.py
generic_toolchain.py
generic_verifier_adaptation.py
generic_verify.py
github_agent_performance_store.py
github_artifact_cas_audit_store.py
github_artifact_cas_stats_store.py
github_contextual_strategy_efficiency_store.py
github_execution_checkpoint_store.py
github_full_gate_cache_store.py
github_goal_store.py
github_memory_store.py
github_phase_cost_baseline_store.py
github_provider_health_store.py
github_provider_metrics_store.py
github_quick_gate_cache_store.py
github_routing_history_store.py
github_runner.py
github_strategy_efficiency_store.py
github_verification_cost_store.py
global_admission.py
goal_engine.py
goal_learning.py
goal_loop.py
godot_android_export.py
godot_android_stage.py
godot_baseline.py
godot_device_qa.py
godot_device_stage.py
godot_final_review_qa.py
godot_final_review_stage.py
godot_model.py
godot_play_stage.py
godot_preview.py
godot_privacy_security_qa.py
godot_privacy_security_stage.py
godot_release_artifact_stage.py
godot_release_artifact.py
godot_release_qa.py
godot_release_stage.py
godot_repository_probe.py
godot_runtime_journey_stage.py
godot_runtime_journeys.py
godot_runtime.py
godot_session.py
godot_store_metadata_qa.py
godot_store_metadata_stage.py
godot_visual_qa.py
godot_visual_stage.py
human_input_request.py
idempotent_model.py
immutable_artifact_cache.py
improvement_backlog.py
improvement_dispatch.py
improvement_executor.py
improvement_verifier.py
journeys.py
jumpy_baseline.gd
jumpy_save_checks.gd
learning_context.py
lease_guard.py
lease_keepalive.py
local_capacity_inventory.py
local_capacity.py
local_model_benchmark.py
local_model_leaderboard.py
local_model_reputation.py
local_model_specialization.py
memory_bridge.py
memory_lifecycle.py
meta_router.py
model_portfolio_audit.py
model_portfolio_learning.py
model_portfolio.py
multi_engine_orchestrator.py
multi_project_smoke.py
native_qa.py
native_stage.py
notification_qa.py
notification_stage.py
omniroute_capacity.py
orchestrator.py
performance_qa.py
performance_stage.py
persistent_quick_gate_cache.py
phase_budget.py
phase_cost_baseline.py
platform_view_qa.py
platform_view_stage.py
play_publisher.py
play_stage.py
portfolio_candidate_scheduler.py
portfolio_scan.py
post_preview.py
predictive_budget.py
preemption_apply.py
preemption_controller.py
privacy_audit.py
privacy_stage.py
production_os_worker.py
project_budget.py
project_context.py
project_engine.py
project_memory.py
project_recommendations.py
project_status.py
promoted_capabilities.py
provider_cost.py
provider_health.py
provider_metrics.py
provider_monthly_quota.py
provider_probe.py
provider_router.py
provider_runtime_reliability.py
queue.py
quick_gate_cache.py
readiness.py
recovery_controller.py
release_candidate_search.py
release_contract.py
release_readiness.py
release_repair.py
release_stage_engine.py
release.py
repair_planner.py
repair_queue.py
repair_search_policy.py
repair_strategy.py
replacement_ci_policy_check.py
replacement_ci_policy_v11.py
replacement_ci_policy.py
repo_maintenance.py
repo_version_probe.py
repository_research_provider.py
reputation_policy_check.py
routing_audit.py
routing_calibration.py
routing_history.py
run_cost_controller.py
run.py
runtime_health.py
runtime_journeys.py
safe_rewrite_learning.py
security_agent.py
security_audit.py
security_remediation.py
security_stage.py
smoke.py
stage_registry.py
stagnation_controller.py
star_scanner.py
store_package.py
store_stage.py
strategy_efficiency.py
strict_task_claim_store.py
task_claim_store.py
task_context.py
task_lease.py
task_scheduler.py
telemetry_maintenance.py
telemetry.py
unified_routing_score.py
v1_gate.py
verification_cost.py
worker_heartbeat.py
worker_reaper.py
worker_reliability.py
workflow_checkpoint.py
````

# Files

## File: agents/__init__.py
````python
"""Agent registry and routing primitives."""
⋮----
__all__ = [
````

## File: agents/adapters.py
````python
"""Execution adapters for registered coding agents.

Adapters deliberately use argv lists (never a shell) and return bounded evidence.
Agent-specific invocation templates can be added without changing the router.
"""
⋮----
@dataclass(frozen=True)
class AgentRun
⋮----
agent: str
returncode: int
duration_seconds: float
stdout_tail: str
stderr_tail: str
⋮----
class AgentAdapter
⋮----
def __init__(self, spec: AgentSpec)
⋮----
def probe(self) -> bool
⋮----
env = os.environ.copy()
# Coding agents do not need repository-write credentials: publishing is
# performed later by the trusted GitHub adapter after validation.
⋮----
# Never let an autonomous prompt override process-critical variables.
⋮----
started = time.monotonic()
⋮----
result = subprocess.run(
⋮----
duration = time.monotonic() - started
stdout=result.stdout[-24000:]
stderr=result.stderr[-24000:]
⋮----
terminal_event = None
⋮----
line = raw_line.strip()
⋮----
event = json.loads(line)
⋮----
terminal_event = line
⋮----
budget = max(0, 24000 - len(terminal_event) - 1)
stdout = terminal_event + "\n" + stdout[-budget:]
⋮----
stdout=stdout.replace(value,"[REDACTED]")
stderr=stderr.replace(value,"[REDACTED]")
````

## File: agents/codex.py
````python
"""Verified non-interactive Codex CLI contract and telemetry parsing."""
⋮----
_USAGE_FIELDS = (
⋮----
def codex_invocation(prompt: str) -> tuple[list[str], dict[str, str]]
⋮----
"""Build the upstream-supported headless Codex invocation.

    JSONL output gives the orchestrator structured terminal events while
    ``--ephemeral`` avoids leaving autonomous session state behind. The sandbox
    is fixed to workspace-write so an external user config cannot silently turn
    an implementation run into a read-only review.
    """
⋮----
"""Build an isolated Codex invocation routed through OmniRoute.

    The custom provider is supplied as CLI config and the caller must provide a
    dedicated CODEX_HOME. This prevents ChatGPT account authentication/config
    from silently taking precedence over the custom Responses endpoint.
    """
parsed = urlsplit(str(base_url or "").strip())
loopback_hosts = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
local_http = (
⋮----
home = str(codex_home or "").strip()
⋮----
base = str(base_url).strip().rstrip("/")
⋮----
provider = (
⋮----
def _token_count(value: Any) -> int
⋮----
def parse_codex_usage(stdout: str) -> dict[str, int] | None
⋮----
"""Return normalized usage from the last completed turn in JSONL output.

    Unknown and malformed lines are ignored so additive upstream event types do
    not break callers. Cached input is reported separately but is not added a
    second time to ``total_tokens`` because it is part of input usage.
    """
completed: dict[str, int] | None = None
⋮----
line = raw_line.strip()
⋮----
event = json.loads(line)
⋮----
usage = event.get("usage")
⋮----
normalized = {field: _token_count(usage.get(field, 0)) for field in _USAGE_FIELDS}
⋮----
completed = normalized
````

## File: agents/orchestrator.py
````python
"""Autonomous capability routing with ordered fallbacks and evidence."""
⋮----
def _safe_rewrite_summary()->dict
⋮----
raw=os.environ.get("STUDIO_SAFE_REWRITE_LEARNING_PATH","")
⋮----
def _contextual_routing_state()->tuple[dict,list[tuple[str,float]]]
⋮----
raw=os.environ.get("STUDIO_CONTEXTUAL_ROUTING_MEMORY_PATH","")
data=load_contextual_routing_memory(Path(raw)) if raw else {}
⋮----
value=json.loads(os.environ.get("STUDIO_ROUTING_CONTEXTS_JSON","[]"))
⋮----
value=[]
weighted=[]
⋮----
def _verification_seconds()->float
⋮----
def _agent_execution_seconds(perf:dict,role:str)->dict[str,float]
⋮----
result={}
⋮----
row=perf.get(spec.name+":"+role)
⋮----
def _opencode_runtime(prompt:str)->tuple[list[str],dict[str,str]]
⋮----
model=os.environ.get("STUDIO_CODE_MODEL") or os.environ.get("STUDIO_MODEL","")
base=os.environ.get("STUDIO_API_BASE","")
key=os.environ.get("STUDIO_API_KEY","")
env={"OPENCODE_DISABLE_MODELS_FETCH":"1"}
argv=["opencode","run","--auto","--format","json"]
⋮----
config={
⋮----
def omniroute_available_base()->str|None
⋮----
"""Return the authenticated OmniRoute Responses base when free capacity exists."""
raw=str(os.environ.get("OMNIROUTE_URL") or "").strip()
⋮----
service_root=raw.rstrip("/")
⋮----
service_root=service_root[:-3].rstrip("/")
⋮----
snapshot=fetch_omniroute_summary(
⋮----
def _runtime_invocation(name:str,prompt:str)
⋮----
"""Resolve runtime-specific capacity without changing static adapter support."""
⋮----
invocation=invocation_for(name,prompt)
⋮----
base=omniroute_available_base()
⋮----
codex_home=str(
⋮----
def invocation_for(name:str,prompt:str)->tuple[list[str],dict[str,str]]|None
⋮----
# Only invocation contracts verified against upstream CLIs are enabled.
⋮----
def _run_evidence(run,capacity_source:str|None=None)->dict
⋮----
evidence={"agent":run.agent,"returncode":run.returncode,
⋮----
usage=parse_codex_usage(run.stdout_tail)
⋮----
def _reserve_agent_budget(name:str,prompt:str)
⋮----
ledger_raw=str(os.environ.get("STUDIO_CAPACITY_LEDGER_PATH") or "").strip()
plan_raw=str(os.environ.get("STUDIO_CAPACITY_PLAN_PATH") or "").strip()
project_id=str(os.environ.get("STUDIO_PROJECT_ID") or "").strip()
⋮----
envelope=load_project_envelope(Path(plan_raw),project_id)
⋮----
estimated=max(1,(len(prompt)+3)//4+2048)
estimated=min(estimated,max(1,int(envelope)))
result=reserve_capacity(
⋮----
def _settle_agent_budget(capacity:dict|None,evidence:dict|None=None)->None
⋮----
reservation=capacity.get("reservation")
⋮----
actual=int(capacity.get("estimated_tokens",1) or 1)
mode="reserved_estimate"
⋮----
usage=evidence.get("usage")
⋮----
reported=usage.get("total_tokens")
⋮----
actual=reported
mode="reported"
⋮----
def execute(prompt:str,required:set[str],*,role:str,cwd:Path,memory_path:Path,timeout:int=1800)->dict
⋮----
perf=load(memory_path)
history_raw=os.environ.get("STUDIO_ROUTING_HISTORY_PATH","")
history=load_routing_history(Path(history_raw)) if history_raw else []
weights=learned_weights(history,kind="agent",role=role)
reliability={spec.name:bonus(perf,spec.name,role) for spec in DEFAULT_REGISTRY.all()}
⋮----
ranked=rank_agents(
attempts=[]
⋮----
runtime=_runtime_invocation(decision.agent.name,prompt)
⋮----
budget=_reserve_agent_budget(decision.agent.name,prompt)
⋮----
run=AgentAdapter(decision.agent).run(argv,cwd=cwd,timeout=timeout,extra_env=extra_env)
ok=run.returncode==0
evidence=_run_evidence(run,capacity_source)
⋮----
def ranked_agent_names(required:set[str],*,role:str,memory_path:Path,limit:int=2,preferred:str|None=None)->list[str]
⋮----
def usable(decision)->bool
⋮----
preferred_name=str(preferred or "").strip()
⋮----
preferred_name=""
⋮----
names=[]
⋮----
preferred_decision=next(
⋮----
def execute_named(name:str,prompt:str,*,cwd:Path,timeout:int=1800)->dict
⋮----
spec=DEFAULT_REGISTRY.get(name)
⋮----
runtime=_runtime_invocation(name,prompt)
⋮----
budget=_reserve_agent_budget(name,prompt)
⋮----
run=AgentAdapter(spec).run(argv,cwd=cwd,timeout=timeout,extra_env=extra_env)
⋮----
def routing_trace_for(name:str,required:set[str],*,role:str,memory_path:Path)->dict|None
⋮----
decision=next((item for item in ranked if item.agent.name==name),None)
````

## File: agents/performance.py
````python
"""Evidence-backed agent performance memory."""
⋮----
def load(path:Path)->dict
⋮----
x=json.loads(path.read_text())
⋮----
def record(path:Path,agent:str,role:str,*,success:bool,duration:float)->dict
⋮----
data=load(path); key=agent+":"+role
row=data.get(key,{"runs":0,"successes":0,"duration_total":0.0})
⋮----
def bonus(data:dict,agent:str,role:str)->float
⋮----
row=data.get(agent+":"+role)
⋮----
runs=max(1,int(row["runs"])); rate=float(row.get("successes",0))/runs
# bounded empirical adjustment: enough to learn, never enough to erase capability fit
⋮----
def eligible(data:dict,agent:str,role:str)->bool
⋮----
runs=int(row.get("runs",0)); successes=int(row.get("successes",0))
⋮----
# Cool down agents that have repeatedly produced changes that fail the
# trusted verifier. Fresh evidence can re-enable them once statistics improve.
````

## File: agents/registry.py
````python
"""Agent capability registry for AI Dev Server."""
⋮----
@dataclass(frozen=True)
class AgentSpec
⋮----
name: str
command: str
capabilities: frozenset[str]
priority: int = 50
free_preferred: bool = True
long_running: bool = False
browser: bool = False
mcp: bool = False
metadata: dict[str, str] = field(default_factory=dict)
⋮----
def available(self) -> bool
⋮----
_DEFAULTS = (
⋮----
class AgentRegistry
⋮----
def __init__(self, specs: Iterable[AgentSpec] = _DEFAULTS)
⋮----
def all(self) -> tuple[AgentSpec, ...]
⋮----
def get(self, name: str) -> AgentSpec | None
⋮----
def available(self) -> tuple[AgentSpec, ...]
⋮----
DEFAULT_REGISTRY = AgentRegistry()
````

## File: agents/router.py
````python
"""Capability-based agent routing."""
⋮----
@dataclass(frozen=True)
class RouteDecision
⋮----
agent: AgentSpec
score: float
matched: tuple[str, ...]
missing: tuple[str, ...]
trace: dict | None = None
⋮----
matched = sorted(required & set(spec.capabilities))
missing = sorted(required - set(spec.capabilities))
coverage = len(matched) / max(1, len(required))
capability_fit = coverage * 100.0 - (35.0 * len(missing))
free_adjustment = (30.0 if spec.free_preferred else -30.0) if prefer_free else 0.0
long_task_adjustment = (20.0 if spec.long_running else -10.0) if long_task else 0.0
trace = score_agent(
components = dict(trace.components)
⋮----
trace = ScoreTrace(
⋮----
bandit = contextual_bandit_score(
⋮----
architecture_hold = any(
utility = utility_score(
⋮----
score = trace.total
⋮----
trace_data = trace.as_dict()
⋮----
required_set = {x.strip() for x in required if x and x.strip()}
reliability = reliability or {}
decisions = [
⋮----
ranked = rank_agents(required, registry=registry, prefer_free=prefer_free, long_task=long_task)
available = [item for item in ranked if item.agent.available()]
````

## File: agents/workspace.py
````python
"""Validate autonomous agent edits before they are trusted or published."""
⋮----
MAX_SNAPSHOT_BYTES=8_000_000
⋮----
def snapshot(root:Path)->dict[str,str]
⋮----
root=root.resolve(); out={}; total=0
⋮----
rel=p.relative_to(root).as_posix()
⋮----
try: text=p.read_text(encoding="utf-8")
⋮----
def validate_delta(root:Path,before:dict[str,str])->dict
⋮----
after=snapshot(root)
deleted=sorted(set(before)-set(after))
⋮----
p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(before[rel],encoding="utf-8")
⋮----
changed=[]
⋮----
normalized=validate_patch({"files":changed})
⋮----
def restore(root:Path,before:dict[str,str])->None
⋮----
root=root.resolve()
current=snapshot(root)
⋮----
p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8")
````

## File: candidates/jumpy_profile_save.gd
````
extends Node

const SAVE_PATH: String = "user://jumpy_save.json"
const SAVE_VERSION: int = 1

const DEFAULT_DATA: Dictionary = {
	"version": SAVE_VERSION,
	"best_score": 0,
	"coins": 0,
	"runs": 0,
	"perfect_landings": 0,
	"total_score": 0,
	"selected_skin": 0,
	"unlocked_skins": [0],
	"daily_best": 0,
	"daily_key": "",
	"streak_days": 0,
	"last_play_date": "",
	"sound": true,
	"haptics": true,
	"reduced_motion": false,
	"high_contrast": false
}

var data: Dictionary = DEFAULT_DATA.duplicate(true)

func _save_integer(value: Variant, fallback: int = 0, maximum: int = 2147483647) -> int:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return fallback
	var number: float = float(value)
	if not is_finite(number) or number < 0.0 or number > maximum or number != floor(number):
		return fallback
	return int(number)

func _save_date(value: Variant) -> String:
	if not value is String or value.length() != 10:
		return ""
	var parts: PackedStringArray = value.split("-")
	if parts.size() != 3 or parts[0].length() != 4 or parts[1].length() != 2 or parts[2].length() != 2:
		return ""
	for part in parts:
		if not part.is_valid_int() or part.begins_with("+") or part.begins_with("-"):
			return ""
	var year: int = int(parts[0])
	var month: int = int(parts[1])
	var day: int = int(parts[2])
	if year < 1 or month < 1 or month > 12:
		return ""
	var days: Array[int] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
		days[1] = 29
	return value if day >= 1 and day <= days[month - 1] else ""

func _validated_save(parsed: Dictionary) -> Dictionary:
	var clean: Dictionary = DEFAULT_DATA.duplicate(true)
	for key in ["best_score", "coins", "runs", "perfect_landings", "total_score", "daily_best", "streak_days"]:
		clean[key] = _save_integer(parsed.get(key, 0))
	for key in ["sound", "haptics", "reduced_motion", "high_contrast"]:
		if typeof(parsed.get(key)) == TYPE_BOOL:
			clean[key] = parsed[key]
	for key in ["daily_key", "last_play_date"]:
		clean[key] = _save_date(parsed.get(key))
	var unlocks: Array = [0]
	var saved_unlocks: Variant = parsed.get("unlocked_skins")
	if saved_unlocks is Array:
		for item in saved_unlocks:
			var index: int = _save_integer(item, -1, 5)
			if index >= 0 and not index in unlocks:
				unlocks.append(index)
	clean.unlocked_skins = unlocks
	var selected: int = _save_integer(parsed.get("selected_skin", 0), 0, 5)
	clean.selected_skin = selected if selected in unlocks else 0
	return clean

func _ready() -> void:
	load_data()
	_refresh_daily()

func load_data() -> void:
	data = DEFAULT_DATA.duplicate(true)
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file: FileAccess = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		push_warning("Jumpy: unable to open save file; defaults preserved.")
		return
	if file.get_length() > 262144:
		push_warning("Jumpy: save file too large; defaults preserved.")
		return
	var parser: JSON = JSON.new()
	if parser.parse(file.get_as_text()) != OK or not parser.data is Dictionary:
		push_warning("Jumpy: save file is invalid; defaults preserved.")
		return
	data = _validated_save(parser.data)

func save() -> void:
	var file: FileAccess = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_warning("Jumpy: unable to open save file for writing. Error %s" % FileAccess.get_open_error())
		return
	file.store_string(JSON.stringify(data))
	file.flush()
	var error: Error = file.get_error()
	if error != OK:
		push_warning("Jumpy: save write failed with error %s" % error)

func set_preference(key: String, value: bool) -> void:
	if key not in ["sound", "haptics", "reduced_motion", "high_contrast"]:
		push_warning("Jumpy: unknown preference %s" % key)
		return
	data[key] = value
	save()

func record_run(score: int, run_coins: int, perfects: int, daily: bool) -> Dictionary:
	data.runs = int(data.runs) + 1
	data.coins = int(data.coins) + run_coins
	data.total_score = int(data.total_score) + score
	data.perfect_landings = int(data.perfect_landings) + perfects
	data.best_score = maxi(int(data.best_score), score)
	if daily:
		data.daily_best = maxi(int(data.daily_best), score)
	_update_streak()
	_unlock_earned_skins()
	save()
	return get_mission_progress()

func spend_coins(amount: int) -> bool:
	if amount <= 0 or int(data.coins) < amount:
		return false
	data.coins = int(data.coins) - amount
	save()
	return true

func select_skin(index: int) -> void:
	if index in data.unlocked_skins:
		data.selected_skin = index
		save()

func get_mission_progress() -> Dictionary:
	return {
		"runs": mini(int(data.runs), 10),
		"runs_goal": 10,
		"perfects": mini(int(data.perfect_landings), 50),
		"perfects_goal": 50,
		"score": mini(int(data.total_score), 5000),
		"score_goal": 5000
	}

func daily_seed() -> int:
	_refresh_daily()
	return absi(hash(str(data.daily_key)))

func _refresh_daily() -> void:
	var date: Dictionary = Time.get_date_dict_from_system()
	var key: String = "%04d-%02d-%02d" % [date.year, date.month, date.day]
	if str(data.daily_key) != key:
		data.daily_key = key
		data.daily_best = 0
		save()

func _update_streak() -> void:
	var date: Dictionary = Time.get_date_dict_from_system()
	var today: String = "%04d-%02d-%02d" % [date.year, date.month, date.day]
	if str(data.last_play_date) == today:
		return
	if str(data.last_play_date).is_empty():
		data.streak_days = 1
	else:
		var now_unix: int = int(Time.get_unix_time_from_system())
		var last_unix: int = int(Time.get_unix_time_from_datetime_string(str(data.last_play_date) + "T00:00:00"))
		var days: int = int((now_unix - last_unix) / 86400.0)
		data.streak_days = int(data.streak_days) + 1 if days <= 1 else 1
	data.last_play_date = today

func _unlock_earned_skins() -> void:
	var unlocks: Array = data.unlocked_skins
	var milestones: Array[int] = [0, 250, 900, 2200, 5000, 10000]
	for i: int in range(milestones.size()):
		if int(data.total_score) >= milestones[i] and not i in unlocks:
			unlocks.append(i)
	data.unlocked_skins = unlocks
````

## File: capabilities/__init__.py
````python
"""Trusted promoted capability provider namespace."""
````

## File: capabilities/asset_artwork.py
````python
"""Deterministic bounded artwork capability.

Returns SVG assets only. It performs no network, filesystem, subprocess, or registry actions.
"""
⋮----
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
MAX_TEXT = 120
MAX_ASSETS = 3
⋮----
class ArtworkCapabilityError(ValueError)
⋮----
def _color(value, fallback)
⋮----
def _label(value)
⋮----
clean = " ".join(value.split()).strip()
⋮----
def _palette(context)
⋮----
design = context.get("design")
⋮----
design = {}
primary = _color(design.get("primary"), "#182030")
accent = _color(design.get("accent"), "#5A64F6")
⋮----
def _icon_svg(label, primary, accent)
⋮----
mark = html.escape(label[:2].upper())
⋮----
def _feature_svg(label, primary, accent)
⋮----
safe = html.escape(label)
⋮----
def run(context)
⋮----
encoded = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
⋮----
label = _label(context.get("label") or context.get("objective") or "APP")
⋮----
requested = context.get("assets", ["icon", "feature_graphic"])
⋮----
assets = {}
⋮----
svg = _icon_svg(label, primary, accent)
⋮----
svg = _feature_svg(label, primary, accent)
````

## File: adaptation_research.py
````python
"""Fail-closed bridge from missing capabilities to researched adaptation evidence."""
⋮----
class AdaptationResearchError(ValueError)
⋮----
candidate_id = "capability:" + capability
objective = "Research implementation and security constraints for missing capability " + capability
````

## File: adaptation.py
````python
"""Fail-closed capability-gap detection for autonomous factory evolution.

This module never executes downloaded code. It turns unsupported completion work
into a machine-readable evolution request that can be researched, implemented on
an isolated branch, benchmarked, and either promoted or rejected.
"""
⋮----
VERSION = 1
⋮----
RESOURCE_PLAYBOOK = {
⋮----
DEFAULT_RESOURCES = [
⋮----
PROMOTION_GATES = [
⋮----
def _clean_strings(value: object) -> list[str]
⋮----
def build_adaptation_request(report: dict, registered_stages: set[str] | frozenset[str]) -> dict
⋮----
"""Describe unsupported work without guessing that it succeeded."""
completion = report.get('completion', {}) if isinstance(report, dict) else {}
release = report.get('release_evidence', {}) if isinstance(report, dict) else {}
capability = release.get('capability_qa', {}) if isinstance(release, dict) else {}
next_stage = completion.get('next_stage') if isinstance(completion, dict) else None
⋮----
gaps: list[dict] = []
seen: set[tuple[str, str]] = set()
⋮----
def add(kind: str, value: str, reason: str) -> None
⋮----
key = (kind, value)
⋮----
mapped_values = {
⋮----
blockers = _clean_strings(completion.get('blockers') if isinstance(completion, dict) else [])
⋮----
stage = blocker[:-8]
⋮----
resource_items: list[dict] = []
resource_seen: set[tuple[str, str]] = set()
⋮----
candidates = RESOURCE_PLAYBOOK.get(gap['value'], DEFAULT_RESOURCES)
⋮----
key = (item['kind'], item['query'])
⋮----
def write_adaptation_request(report: dict, out: Path, registered_stages: set[str] | frozenset[str]) -> dict
⋮----
request = build_adaptation_request(report, registered_stages)
⋮----
memory_path = out / '.memory' / 'memory.json'
project_id = os.environ.get('STUDIO_PROJECT_ID')
⋮----
memory = load_project_memory(memory_path)
request = attach_capability_hints(request, memory, project_id)
⋮----
path = out / 'evolution-request.json'
````

## File: adaptive_phase_policy.py
````python
"""Fail-closed phase gating for adaptive autonomous orchestration."""
⋮----
"""Decide whether a model planning call is worth its round budget.

    A skipped planning call still produces the stable plan schema consumed by
    downstream implementation. Invalid or missing objective text fails closed
    to model planning rather than inventing a plan without a usable objective.
    """
⋮----
objective = brief.strip()
⋮----
"""Decide whether a model review must run after trusted verification.

    Skipping the model reviewer is allowed only for rounds the adaptive role
    allocator marked low risk. Trusted verification remains authoritative: a
    failed or ambiguous verification can never be converted into completion.
    """
⋮----
remaining = max(0.0, float(review_remaining))
⋮----
remaining = 0.0
⋮----
verification_passed = (
reason = (
````

## File: adaptive_role_allocator.py
````python
"""Bounded adaptive allocation of model roles for one autonomous round."""
⋮----
@dataclass(frozen=True)
class RoleAllocation
⋮----
implementation_models: int
require_review: bool
require_planning: bool
difficulty: float
uncertainty: float
budget_pressure: float
reason: str
⋮----
def as_dict(self) -> dict
⋮----
verification = max(0.0, float(verification_seconds or 0.0))
remaining = None if remaining_seconds is None else max(0.0, float(remaining_seconds))
⋮----
reserve = max(120.0, verification * 2.0)
⋮----
"""Return whether this round is worth spending a model call on planning."""
normalized_difficulty = max(0.0, min(1.0, float(difficulty or 0.0)))
pressure = budget_pressure(
⋮----
difficulty = max(0.0, min(1.0, float(difficulty or 0.0)))
confidence = max(0.0, min(1.0, float(route_confidence or 0.0)))
uncertainty = 1.0 - confidence
capacity = max(0.0, min(1.0, float(free_capacity or 0.0)))
⋮----
implementation_models = 1
reason = "single implementation model"
⋮----
implementation_models = 2
reason = "difficult uncertain task benefits from independent implementation"
⋮----
implementation_models = 3
reason = "high difficulty and uncertainty justify a wide implementation portfolio"
⋮----
implementation_models = max(
require_planning = planning_required(
require_review = (
````

## File: adaptive_scoring.py
````python
"""Shared adaptive routing score and explainable decision traces."""
⋮----
@dataclass(frozen=True)
class ScoreTrace
⋮----
name: str
total: float
components: dict[str, float]
⋮----
def as_dict(self) -> dict
⋮----
def _weighted_total(components: dict[str, float], weights: dict[str, float] | None) -> float
⋮----
weights = weights or {}
⋮----
def score_provider(*, name: str, priority: float, free_preferred: bool, reliability: float, latency: float, weights: dict[str, float] | None = None) -> ScoreTrace
⋮----
components = {
⋮----
def score_agent(*, name: str, capability_fit: float, priority: float, free_adjustment: float, long_task_adjustment: float, reliability: float, weights: dict[str, float] | None = None) -> ScoreTrace
````

## File: android_signing.py
````python
"""Trusted Android AAB signing boundary.

Project/model-controlled code never receives signing credentials. Existing JAR
signature metadata is stripped from a copied AAB, then jarsigner signs only that
artifact using passwords passed through the signer process environment.
"""
⋮----
AAB_MAX_BYTES = 1_500_000_000
CERT_RE = re.compile(r"SHA256:\s*([0-9A-Fa-f:]{59,95})")
ALIAS_RE = re.compile(r"[A-Za-z0-9_.-]{1,80}")
SIGNATURE_SUFFIXES = (".SF", ".RSA", ".DSA", ".EC")
⋮----
def valid_aab(path: Path) -> bool
⋮----
names = set(zf.namelist())
⋮----
def _signature_entry(name: str) -> bool
⋮----
upper = name.upper()
⋮----
leaf = upper.rsplit("/", 1)[-1]
⋮----
def strip_existing_signatures(source: Path, destination: Path) -> dict
⋮----
source = source.resolve()
destination = destination.resolve()
⋮----
removed = []
⋮----
data = src.read(info.filename)
⋮----
def _sign_env(store_password: str, key_password: str) -> dict[str, str]
⋮----
env = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "JAVA_HOME"}}
⋮----
def signing_credentials(env: dict | None = None, *, project_root: Path | None = None) -> dict
⋮----
current = os.environ if env is None else env
path = current.get("STUDIO_ANDROID_UPLOAD_KEYSTORE_PATH")
alias = current.get("STUDIO_ANDROID_UPLOAD_KEY_ALIAS")
store_password = current.get("STUDIO_ANDROID_UPLOAD_STORE_PASSWORD")
key_password = current.get("STUDIO_ANDROID_UPLOAD_KEY_PASSWORD") or store_password
⋮----
keystore = Path(path).expanduser().resolve()
⋮----
root = Path(project_root).resolve()
⋮----
unsigned = unsigned.resolve()
signed = signed.resolve()
keystore = keystore.resolve()
⋮----
key_password = store_password if key_password is None else key_password
⋮----
env = _sign_env(store_password, key_password)
⋮----
clean = Path(td) / "unsigned-clean.aab"
stripped = strip_existing_signatures(unsigned, clean)
sign = [
result = runner(sign, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
⋮----
verify_env = {k: v for k, v in env.items() if not k.startswith("STUDIO_AAB_")}
verify = runner(
verify_text = verify.stdout.decode(errors="replace") if isinstance(verify.stdout, bytes) else str(verify.stdout or "")
⋮----
cert = runner(
cert_text = cert.stdout.decode(errors="replace") if isinstance(cert.stdout, bytes) else str(cert.stdout or "")
match = CERT_RE.search(cert_text)
⋮----
fingerprint = match.group(1).replace(":", "").lower()
````

## File: architecture_benchmark.py
````python
"""Compare selected architecture repositories with known alternatives using bounded evidence."""
⋮----
MIN_MIGRATION_DELTA = 8.0
⋮----
def _index(recommendations: dict) -> dict[str, dict]
⋮----
rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
⋮----
def _num(value, default=0.0) -> float
⋮----
def _candidate_score(row: dict, *, selected: bool, review: bool, blocker_count: int) -> float
⋮----
selection = _num(row.get("selection_score", row.get("score")), 0.0)
quality = _num(row.get("quality_score"), 0.0) * 3.0
tier = {"core": 8.0, "recommended": 5.0, "specialized": 2.0, "audit": -5.0}.get(row.get("tier"), 0.0)
score = selection * 0.65 + quality + tier
⋮----
def benchmark(decision: dict, evaluation: dict, recommendations: dict) -> dict
⋮----
rec_index = _index(recommendations)
review = isinstance(evaluation, dict) and evaluation.get("verdict") == "review"
blockers = evaluation.get("blockers", []) if isinstance(evaluation, dict) else []
blocker_count = len(blockers) if isinstance(blockers, list) else 0
⋮----
constraints = decision.get("constraints") if isinstance(decision, dict) and isinstance(decision.get("constraints"), dict) else {}
comparisons = []
⋮----
current = dict(chosen)
current_score = _candidate_score(current, selected=True, review=review, blocker_count=blocker_count)
alternatives = []
⋮----
alt = rec_index.get(alt_name)
⋮----
alt_score = _candidate_score(alt, selected=False, review=review, blocker_count=blocker_count)
⋮----
scored = [x for x in alternatives if isinstance(x.get("benchmark_score"), (int, float))]
best = max(scored, key=lambda x: x["benchmark_score"]) if scored else None
migration = bool(
⋮----
migration_candidates = [x for x in comparisons if x["migration_candidate"]]
⋮----
def write(decision: dict, evaluation: dict, recommendations: dict, out: Path) -> dict
⋮----
result = benchmark(decision, evaluation, recommendations)
````

## File: architecture_change_guard.py
````python
"""Fail-closed guard for architecture-sensitive model patches."""
⋮----
COMMON_ARCHITECTURE_NAMES = {
COMMON_ARCHITECTURE_PREFIXES = (
FLUTTER_ARCHITECTURE_NAMES = {
GODOT_ARCHITECTURE_NAMES = {
GODOT_ARCHITECTURE_PREFIXES = (
⋮----
class ArchitectureChangeBlocked(ValueError)
⋮----
SEMANTIC_IMPORT_PATTERNS = {
⋮----
SEMANTIC_MARKERS = (
⋮----
def _language(path: str) -> str | None
⋮----
suffix = PurePosixPath(path).suffix.lower()
⋮----
def _imports(text: str, language: str | None) -> set[str]
⋮----
pattern = SEMANTIC_IMPORT_PATTERNS.get(language)
⋮----
found = set()
⋮----
def _marker_hits(text: str) -> set[str]
⋮----
lowered = text.lower() if isinstance(text, str) else ""
⋮----
def semantic_impact(path: str, old_content: str, new_content: str) -> dict
⋮----
language = _language(path)
old_imports = _imports(old_content, language)
new_imports = _imports(new_content, language)
added_imports = sorted(new_imports - old_imports)
removed_imports = sorted(old_imports - new_imports)
old_markers = _marker_hits(old_content)
new_markers = _marker_hits(new_content)
added_markers = sorted(new_markers - old_markers)
⋮----
score = 0
⋮----
path_lower = path.lower()
⋮----
def inspect_semantic_patch(value: object, root: Path | str | None) -> dict
⋮----
files = value.get("files")
⋮----
root = Path(root)
details = []
⋮----
path = item.get("path")
content = item.get("content")
⋮----
target = root / path
⋮----
old_content = target.read_text(encoding="utf-8") if target.is_file() else ""
⋮----
old_content = ""
impact = semantic_impact(path, old_content, content)
⋮----
def is_architecture_sensitive(path: str, engine: str = "generic") -> bool
⋮----
normalized = PurePosixPath(path).as_posix()
name = PurePosixPath(normalized).name
⋮----
def inspect_patch(value: object, *, engine: str = "generic") -> dict
⋮----
files = value.get("files") if isinstance(value, dict) else None
⋮----
sensitive = []
⋮----
result = inspect_patch(value, engine=engine)
semantic = inspect_semantic_patch(value, root)
⋮----
blocked = sorted(set(result["sensitive_paths"] + result["semantic_paths"]))
````

## File: architecture_contract.py
````python
"""Enforce fail-closed safety invariants for architecture recommendation automation."""
⋮----
def validate() -> dict
⋮----
failures = []
⋮----
req = {
recs = {
learning = {
⋮----
adjusted = architecture_feedback.apply(
policy = adjusted.get("feedback_policy") or {}
⋮----
max_age = policy.get("max_evidence_age_seconds")
⋮----
decision = architecture_planner.plan(
dep_policy = decision.get("dependency_policy") or {}
constraints = decision.get("constraints") or {}
⋮----
evaluation = architecture_evaluator.evaluate(
eval_policy = evaluation.get("policy") or {}
⋮----
benchmark = architecture_benchmark.benchmark(decision, evaluation, recs)
bench_policy = benchmark.get("policy") or {}
⋮----
def main(argv=None) -> int
⋮----
report = validate()
````

## File: architecture_evaluator.py
````python
"""Evaluate architecture choices against observed project evidence without auto-changing dependencies."""
⋮----
_NEGATIVE_STATUSES={"failed","blocked","repair_needed","release_failed","human_action_required"}
_POSITIVE_STATUSES={"validated_preview","finished","complete","godot_preview_validated","godot_technical_store_ready","godot_play_validated","godot_published"}
⋮----
def _tokens(values)
⋮----
text=values
⋮----
text=" ".join(str(x) for x in values)
⋮----
text=""
⋮----
def _blockers(report)
⋮----
out=[]
⋮----
value=report.get(key)
⋮----
items=value.get("blockers",[])
⋮----
def evaluate(decision:dict, report:dict)->dict
⋮----
chosen=decision.get("chosen",[]) if isinstance(decision,dict) else []
blockers=_blockers(report)
btoks=_tokens(blockers)
status=str(report.get("status","unknown"))
⋮----
findings=[]
reconsider=[]
⋮----
caps=set(str(x).lower() for x in row.get("capabilities",[]) if isinstance(x,str))
overlap=sorted(btoks & caps)
⋮----
alts=row.get("alternatives",[])
⋮----
release=(report.get("release_evidence") or {}) if isinstance(report.get("release_evidence"),dict) else {}
failed_evidence=[]
⋮----
verdict="retain"
confidence="high"
⋮----
verdict="review"
confidence="medium"
⋮----
verdict="insufficient_evidence"
confidence="low"
⋮----
def write(decision:dict, report:dict, out:Path)->dict
⋮----
result=evaluate(decision,report)
````

## File: architecture_feedback.py
````python
"""Apply conservative historical outcome evidence to advisory architecture rankings."""
⋮----
MIN_SAMPLES = 5
MAX_SCORE_BONUS = 3.0
MAX_STACK_SCORE_BONUS = 2.0
MAX_EVIDENCE_AGE_SECONDS = 30 * 24 * 60 * 60
SUCCESS_WEIGHT = 0.6
QUALITY_WEIGHT = 0.4
UNCERTAINTY_BLEND = 0.5
MAX_DRIFT_PENALTY = 2.0
⋮----
"""Down-weight legacy/generic evidence; full bonus requires matching context."""
requested = (domain, framework, project_type, primary_domain)
fields = ("domain", "framework", "project_type", "primary_domain")
explicit = 0
⋮----
value = row.get(field)
⋮----
def _learning_map(learning: dict, *, now: float) -> dict[tuple[str, str | None, str | None, str | None, str | None], dict]
⋮----
rows = learning.get("rankings")
⋮----
out = {}
⋮----
repo = row.get("repo")
⋮----
samples = row.get("samples")
success_rate = row.get("success_rate")
⋮----
latest = row.get("latest_observed_at")
⋮----
domain = row.get("domain")
domain = domain if isinstance(domain, str) and domain else None
framework = row.get("framework")
framework = framework if isinstance(framework, str) and framework else None
project_type = row.get("project_type")
project_type = project_type if isinstance(project_type, str) and project_type else None
primary_domain = row.get("primary_domain")
primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
⋮----
rows = recommendations.get("matches")
rows = rows if isinstance(rows, list) else []
now_value = time.time() if now is None else float(now)
evidence = _learning_map(learning or {}, now=now_value)
⋮----
adjusted = []
applied_count = 0
⋮----
item = dict(row)
repo = item.get("repo")
domain = item.get("domain")
⋮----
history = None
normalized_framework = framework if isinstance(framework, str) and framework else None
normalized_project_type = project_type if isinstance(project_type, str) and project_type else None
normalized_primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
⋮----
# Context-aware runs only consume evidence from the same context.
# Legacy unscoped evidence remains usable only for legacy/unscoped callers.
⋮----
keys = [
⋮----
keys = [(repo, None, None, None, None)]
⋮----
history = evidence.get(key)
⋮----
base = item.get("score")
base_score = float(base) if isinstance(base, (int, float)) else 0.0
⋮----
bonus = 0.0
⋮----
success_rate = max(0.0, min(1.0, float(history["success_rate"])))
posterior = history.get("posterior_success_rate")
posterior_rate = max(0.0, min(1.0, float(posterior))) if isinstance(posterior, (int, float)) else success_rate
wilson = history.get("wilson_lower_95")
wilson_rate = max(0.0, min(1.0, float(wilson))) if isinstance(wilson, (int, float)) else posterior_rate
conservative_success = UNCERTAINTY_BLEND * posterior_rate + (1.0 - UNCERTAINTY_BLEND) * wilson_rate
mean_quality = history.get("quality_shrunk_mean", history.get("mean_quality_score"))
quality_rate = (
confidence = history.get("evidence_confidence")
confidence = max(0.0, min(1.0, float(confidence))) if isinstance(confidence, (int, float)) else 1.0
combined_rate = SUCCESS_WEIGHT * conservative_success + QUALITY_WEIGHT * quality_rate
centered = (combined_rate - 0.5) * 2.0
context_weight = _context_weight(
bonus = max(-MAX_SCORE_BONUS, min(MAX_SCORE_BONUS, centered * MAX_SCORE_BONUS * context_weight * confidence))
drift = history.get("drift") if isinstance(history.get("drift"), dict) else {}
drift_status = drift.get("status")
drift_score = drift.get("score")
drift_score = max(0.0, min(1.0, float(drift_score))) if isinstance(drift_score, (int, float)) else 0.0
drift_penalty = 0.0
⋮----
drift_penalty = MAX_DRIFT_PENALTY * drift_score * confidence * context_weight
bonus = min(0.0, bonus) - drift_penalty
bonus = max(-MAX_SCORE_BONUS, bonus)
⋮----
result = dict(recommendations)
⋮----
"""Return a bounded synergy adjustment from verified historical stack outcomes."""
⋮----
rows = learning.get("stack_rankings")
⋮----
chosen = {x for x in chosen_repos if isinstance(x, str) and x}
evidence = []
weighted = 0.0
total_weight = 0.0
⋮----
repos = row.get("repos")
⋮----
row_framework = row.get("framework")
row_framework = row_framework if isinstance(row_framework, str) and row_framework else None
⋮----
row_project_type = row.get("project_type")
row_project_type = row_project_type if isinstance(row_project_type, str) and row_project_type else None
row_primary_domain = row.get("primary_domain")
row_primary_domain = row_primary_domain if isinstance(row_primary_domain, str) and row_primary_domain else None
⋮----
requested_context = (
row_context = (
⋮----
repo_set = {x for x in repos if isinstance(x, str)}
overlap = len(chosen & repo_set)
⋮----
# Require at least candidate + one selected repo before claiming synergy.
⋮----
rate = max(0.0, min(1.0, float(success_rate)))
posterior = row.get("posterior_success_rate")
posterior_rate = max(0.0, min(1.0, float(posterior))) if isinstance(posterior, (int, float)) else rate
wilson = row.get("wilson_lower_95")
⋮----
mean_quality = row.get("quality_shrunk_mean", row.get("mean_quality_score"))
⋮----
confidence = row.get("evidence_confidence")
⋮----
drift = row.get("drift") if isinstance(row.get("drift"), dict) else {}
⋮----
drift_signal = -drift_score if drift_status == "degraded" else 0.0
⋮----
centered = min(0.0, centered) + drift_signal
⋮----
weight = min(1.0, samples / 10.0) * min(1.0, overlap / max(1, len(chosen))) * context_weight
⋮----
raw = (weighted / total_weight) * MAX_STACK_SCORE_BONUS
bonus = max(-MAX_STACK_SCORE_BONUS, min(MAX_STACK_SCORE_BONUS, raw))
````

## File: architecture_learning.py
````python
"""Aggregate architecture outcome evidence without turning correlation into authority."""
⋮----
MIN_SAMPLES = 5
CONFIDENCE_SAMPLE_TARGET = 20
QUALITY_PRIOR_MEAN = 50.0
QUALITY_PRIOR_STRENGTH = 5.0
DRIFT_RECENT_SAMPLES = 5
DRIFT_BASELINE_MIN_SAMPLES = 5
DRIFT_SUCCESS_DELTA = 0.20
DRIFT_QUALITY_DELTA = 15.0
⋮----
def _drift(observations: list[dict]) -> dict
⋮----
timed = [
⋮----
recent = timed[-DRIFT_RECENT_SAMPLES:]
baseline = timed[:-DRIFT_RECENT_SAMPLES]
recent_success = sum(1 for x in recent if x.get("successful") is True) / len(recent)
baseline_success = sum(1 for x in baseline if x.get("successful") is True) / len(baseline)
recent_quality = sum(float(x.get("quality", 0.0)) for x in recent) / len(recent)
baseline_quality = sum(float(x.get("quality", 0.0)) for x in baseline) / len(baseline)
success_delta = recent_success - baseline_success
quality_delta = recent_quality - baseline_quality
⋮----
success_component = min(1.0, abs(success_delta) / DRIFT_SUCCESS_DELTA) if DRIFT_SUCCESS_DELTA else 0.0
quality_component = min(1.0, abs(quality_delta) / DRIFT_QUALITY_DELTA) if DRIFT_QUALITY_DELTA else 0.0
magnitude = round(0.6 * success_component + 0.4 * quality_component, 4)
⋮----
degraded = success_delta <= -DRIFT_SUCCESS_DELTA or quality_delta <= -DRIFT_QUALITY_DELTA
improving = success_delta >= DRIFT_SUCCESS_DELTA or quality_delta >= DRIFT_QUALITY_DELTA
status = "degraded" if degraded else "improving" if improving else "stable"
⋮----
def _wilson_lower(successes: int, samples: int, z: float = 1.96) -> float
⋮----
p = successes / samples
z2 = z * z
denom = 1.0 + z2 / samples
centre = p + z2 / (2.0 * samples)
margin = z * ((p * (1.0 - p) / samples + z2 / (4.0 * samples * samples)) ** 0.5)
⋮----
def _confidence(samples: int) -> float
⋮----
def _quality_shrunk_mean(total: float, samples: int) -> float
⋮----
def root_for_output(out: Path | str) -> Path
⋮----
out = Path(out)
⋮----
def _rows(root: Path)
⋮----
candidates = []
direct = root / "architecture-outcome.json"
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
def summarize(root: Path | str = "studio-output") -> dict
⋮----
root = Path(root)
stats = {}
stack_stats = {}
projects = 0
⋮----
outcome = row.get("outcome")
⋮----
observed_at = row.get("observed_at")
observed_at = float(observed_at) if isinstance(observed_at, (int, float)) else None
successful = outcome.get("successful") is True
calls = max(0, int(outcome.get("model_calls_this_cycle", 0) or 0))
cycles = max(0, int(outcome.get("cycles", 0) or 0))
blockers = max(0, int(outcome.get("blocker_count", 0) or 0))
quality = outcome.get("quality_score")
quality = max(0.0, min(100.0, float(quality))) if isinstance(quality, (int, float)) else (100.0 if successful else 0.0)
⋮----
constraints = row.get("decision_constraints")
framework = (
project_type = (
primary_domain = (
⋮----
contexts = row.get("chosen_contexts")
⋮----
observed = [
⋮----
repos = row.get("chosen_repositories")
⋮----
stack_repos = tuple(sorted(item["repo"] for item in observed))
stack_key = (framework, project_type, primary_domain, stack_repos)
⋮----
stack = stack_stats.setdefault(stack_key, {
⋮----
prev = stack.get("latest_observed_at")
⋮----
repo = observed_item["repo"]
domain = observed_item.get("domain")
item_framework = observed_item.get("framework")
item_project_type = observed_item.get("project_type")
item_primary_domain = observed_item.get("primary_domain")
key = (repo, domain, item_framework, item_project_type, item_primary_domain)
item = stats.setdefault(key, {
⋮----
previous_ts = item.get("latest_observed_at")
⋮----
rankings = []
⋮----
samples = item["samples"]
success_rate = item["successes"] / samples if samples else 0.0
posterior_success = (item["successes"] + 1.0) / (samples + 2.0) if samples >= 0 else 0.5
wilson_lower = _wilson_lower(item["successes"], samples)
confidence = _confidence(samples)
quality_mean = item["quality_total"] / samples if samples else 0.0
quality_variance = max(0.0, item["quality_sq_total"] / samples - quality_mean * quality_mean) if samples else 0.0
quality_std = quality_variance ** 0.5
quality_shrunk = _quality_shrunk_mean(item["quality_total"], samples)
drift = _drift(item.get("observations", []))
⋮----
stack_rankings = []
⋮----
drift_alerts = []
⋮----
drift = row.get("drift")
⋮----
def write(root: Path | str = "studio-output", path: Path | str | None = None) -> dict
⋮----
path = Path(path) if path is not None else root / "architecture-learning.json"
⋮----
result = summarize(root)
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Aggregate architecture outcome evidence")
⋮----
args = parser.parse_args(argv)
result = write(args.root) if args.write else summarize(args.root)
````

## File: architecture_obsolescence.py
````python
"""Derive advisory obsolescence candidates from runtime drift and benchmark evidence."""
⋮----
MIN_DRIFT_SCORE = 0.6
⋮----
def _repo_drift(learning: dict) -> dict[str, dict]
⋮----
alerts = learning.get("drift_alerts", []) if isinstance(learning, dict) else []
out = {}
⋮----
repo = row.get("repo")
score = row.get("score")
⋮----
def _recommendation_index(recommendations: dict) -> dict[str, dict]
⋮----
rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
⋮----
def evaluate(learning: dict, benchmark: dict, recommendations: dict, maintenance: dict[str, dict] | None = None, versions: dict[str, dict] | None = None) -> dict
⋮----
drift = _repo_drift(learning)
recs = _recommendation_index(recommendations)
maintenance = maintenance if isinstance(maintenance, dict) else {}
versions = versions if isinstance(versions, dict) else {}
comparisons = benchmark.get("comparisons", []) if isinstance(benchmark, dict) else []
⋮----
candidates = []
⋮----
current = row["current_repo"]
drift_row = drift.get(current)
⋮----
drift_score = drift_row.get("score")
⋮----
best = row.get("best_alternative")
⋮----
current_meta = recs.get(current, {})
alt_meta = recs.get(best, {})
maintenance_row = maintenance.get(current, {})
maintenance_signal = maintenance_row.get("status") if isinstance(maintenance_row, dict) else None
⋮----
maintenance_signal = current_meta.get("maintenanceStatus")
⋮----
maintenance_signal = "unknown"
⋮----
def write(learning: dict, benchmark: dict, recommendations: dict, out: Path, maintenance: dict[str, dict] | None = None, versions: dict[str, dict] | None = None) -> dict
⋮----
result = evaluate(learning, benchmark, recommendations, maintenance=maintenance, versions=versions)
````

## File: architecture_outcome.py
````python
"""Record measurable outcomes for trusted architecture decisions."""
⋮----
SUCCESS_STATUSES = {
⋮----
def _count(value) -> int
⋮----
def _quality_score(*, successful: bool, blockers: int, cycles: int, rounds: int, calls: int) -> float
⋮----
"""Continuous 0..100 project-quality score derived only from observable execution evidence."""
completion = 50.0 if successful else 0.0
blocker_score = 20.0 * max(0.0, 1.0 - min(blockers, 5) / 5.0)
cycle_score = 10.0 * max(0.0, 1.0 - max(0, min(cycles, 10) - 1) / 9.0)
round_score = 10.0 * max(0.0, 1.0 - max(0, min(rounds, 10) - 1) / 9.0)
call_score = 10.0 * max(0.0, 1.0 - min(calls, 20) / 20.0)
⋮----
def _decision_id(decision: dict) -> str
⋮----
raw = json.dumps(decision, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
⋮----
def build(state: dict) -> dict
⋮----
decision = state.get("architecture_decision")
⋮----
decision = {"status": "unavailable", "chosen": []}
chosen = decision.get("chosen")
chosen = chosen if isinstance(chosen, list) else []
status = str(state.get("status", "unknown"))
blockers = state.get("blockers")
blockers = blockers if isinstance(blockers, list) else []
evaluation = state.get("architecture_evaluation")
⋮----
evaluation = {}
benchmark = state.get("architecture_benchmark")
⋮----
benchmark = {}
migration_candidates = benchmark.get("migration_candidates")
migration_candidates = migration_candidates if isinstance(migration_candidates, list) else []
successful = status in SUCCESS_STATUSES
cycles = _count(state.get("cycles", 0))
rounds = _count(state.get("rounds", 0))
calls = int(state.get("model_calls_this_cycle", 0) or 0)
quality_score = _quality_score(
⋮----
def write(state: dict, out: Path) -> dict
⋮----
result = build(state)
out = Path(out)
````

## File: architecture_planner.py
````python
"""Trusted architecture decision layer built from advisory star-list recommendations."""
⋮----
MAX_CHOSEN = 6
MAX_REJECTED = 12
HIGH_CONFIDENCE_MARGIN = 1.5
MEDIUM_CONFIDENCE_MARGIN = 0.5
⋮----
def _selection_confidence(margin: float | None) -> str
⋮----
def _autonomy_policy(chosen: list[dict], rejected: list[dict]) -> dict
⋮----
ranked = [
severity = {"high": 0, "medium": 1, "low": 2}
decision_confidence = max(
⋮----
mode = "independent_review"
retain = 3
⋮----
mode = "lightweight_review"
retain = 2
⋮----
mode = "standard"
retain = 1
fallback_repos = [
⋮----
def _clean_rows(value)
⋮----
rows=[]
⋮----
def _project_type(req: dict) -> str
⋮----
brief = req.get("brief") if isinstance(req.get("brief"), str) else ""
text = brief.lower()
rules = (
⋮----
def _primary_domain(rows: list[dict]) -> str | None
⋮----
counts = {}
⋮----
domain = row.get("domain") if isinstance(row, dict) else None
⋮----
def _reason(row)
⋮----
parts=[]
⋮----
caps=row.get("capabilities")
⋮----
best=row.get("best_for")
⋮----
resolved_framework = (
resolved_project_type = _project_type(req)
resolved_publication = (
resolved_platform = (
raw_rows = _clean_rows(recommendations)
resolved_primary_domain = _primary_domain(raw_rows)
recommendations = apply_feedback(
rows=_clean_rows(recommendations)
chosen=[]
rejected=[]
pending=[]
⋮----
repo=row["repo"]
avoid=row.get("avoid_when") if isinstance(row.get("avoid_when"),list) else []
⋮----
# Greedy selection: base recommendation/history score first, then a tightly bounded
# bonus for combinations that repeatedly succeeded together in prior projects.
⋮----
chosen_names=[x["repo"] for x in chosen]
scored=[]
⋮----
synergy=stack_adjustment(
base=row.get("feedback_score", row.get("score"))
base_score=float(base) if isinstance(base,(int,float)) else 0.0
effective=round(base_score + float(synergy.get("bonus",0.0)),4)
⋮----
runner_up_score = scored[1][0] if len(scored) > 1 else None
selection_margin = (
pending=[x for x in pending if x["repo"]!=row["repo"]]
⋮----
autonomy_policy = _autonomy_policy(chosen, rejected)
⋮----
decision=plan(
````

## File: architecture_preflight.py
````python
"""Independent deterministic preflight validation for architecture decisions."""
⋮----
MAX_REVIEW_ROWS = 24
MIN_OVERLAP_RATIO = 0.5
⋮----
def _clean_rows(recommendations: dict) -> list[dict]
⋮----
rows = recommendations.get("matches")
⋮----
out = []
⋮----
repo = row.get("repo")
⋮----
avoid = row.get("avoid_when")
⋮----
def _baseline_score(row: dict, primary_domain: str | None) -> float
⋮----
raw = row.get("score")
score = float(raw) if isinstance(raw, (int, float)) else 0.0
quality = row.get("quality_score")
⋮----
def _baseline_rank(recommendations: dict, primary_domain: str | None) -> list[dict]
⋮----
rows = _clean_rows(recommendations)
ranked = [
⋮----
def validate(decision: dict, recommendations: dict) -> dict
⋮----
decision = decision if isinstance(decision, dict) else {}
chosen = decision.get("chosen")
chosen = chosen if isinstance(chosen, list) else []
chosen_repos = [
constraints = decision.get("constraints")
constraints = constraints if isinstance(constraints, dict) else {}
primary_domain = constraints.get("primary_domain")
primary_domain = primary_domain if isinstance(primary_domain, str) and primary_domain else None
⋮----
baseline = _baseline_rank(recommendations, primary_domain)
baseline_repos = [item["repo"] for item in baseline[: max(1, len(chosen_repos))]]
top_matches = bool(chosen_repos and baseline_repos and chosen_repos[0] == baseline_repos[0])
⋮----
overlap = len(set(chosen_repos) & set(baseline_repos))
overlap_ratio = overlap / max(1, len(set(chosen_repos)))
⋮----
overlap = 0
overlap_ratio = 1.0
⋮----
policy = decision.get("autonomy_policy")
policy = policy if isinstance(policy, dict) else {}
requested_mode = policy.get("validation_mode", "standard")
validation_required = policy.get("validation_required") is True
⋮----
converged = top_matches and overlap_ratio >= MIN_OVERLAP_RATIO
⋮----
verdict = "pass"
reason = "planner confidence is high; independent baseline is informational"
⋮----
reason = "independent baseline sufficiently converges with planner selection"
⋮----
verdict = "hold"
reason = "independent baseline does not sufficiently converge with planner selection"
⋮----
def write(decision: dict, recommendations: dict, out: Path) -> dict
⋮----
out = Path(out)
⋮----
result = validate(decision, recommendations)
````

## File: architecture_replacement_candidate.py
````python
"""Validate model-generated replacement candidates before isolated execution."""
⋮----
class ReplacementCandidateRejected(ValueError)
⋮----
MAX_FILES=64
MAX_FILE_BYTES=256*1024
MAX_TOTAL_BYTES=2*1024*1024
ALLOWED_COMMANDS={"python3","python","flutter","dart"}
PROTECTED_PREFIXES=(".git/",".github/workflows/","studio/","tests/test_architecture_")
PROTECTED_FILES={".env",".env.local",".env.production"}
⋮----
def _safe_path(value)
⋮----
normalized=value.replace(chr(92),"/")
⋮----
def validate(order,candidate)
⋮----
files=candidate.get("files")
⋮----
normalized_files=[]
seen=set()
total=0
⋮----
path=_safe_path(item["path"])
content=item["content"]
⋮----
size=len(content.encode("utf-8"))
⋮----
commands=candidate.get("validation_commands")
⋮----
normalized_commands=[]
⋮----
notes=candidate.get("notes")
````

## File: architecture_replacement_executor.py
````python
"""Execute an explicitly supplied replacement candidate in an isolated worktree.

This executor does not synthesize migrations and never touches the default branch.
Candidate code is materialized only in a detached worktree. Validation commands run
inside the pinned container with networking disabled and no production credentials.
"""
⋮----
class ReplacementExecutionError(RuntimeError)
⋮----
SAFE_ENV={
⋮----
PROTECTED_PREFIXES=(
PROTECTED_FILES={
MAX_FILES=64
MAX_FILE_BYTES=256*1024
MAX_TOTAL_BYTES=2*1024*1024
⋮----
def _run(args, *, cwd=None, timeout=600, env=None, check=False)
⋮----
result=subprocess.run(
⋮----
def _sha(value, label)
⋮----
def _safe_path(value: str) -> str
⋮----
normalized=value.replace("\\","/")
⋮----
def _validate_candidate(order: dict, candidate: dict) -> list[dict]
⋮----
files=candidate.get("files")
⋮----
total=0
normalized=[]
seen=set()
⋮----
path=_safe_path(item["path"])
content=item["content"]
⋮----
size=len(content.encode("utf-8"))
⋮----
def _materialize(root: Path, files: list[dict]) -> None
⋮----
base=root.resolve()
⋮----
target=root/item["path"]
resolved=target.resolve()
⋮----
def _hash_files(root: Path, paths: list[str]) -> dict[str,str]
⋮----
out={}
⋮----
target=root/path
⋮----
def _commit_candidate(root: Path, baseline_sha: str, paths: list[str]) -> str
⋮----
env=dict(SAFE_ENV)
⋮----
sha=_run(["git","rev-parse","HEAD"],cwd=root,check=True).stdout.strip()
⋮----
def _docker_command(root: Path, command: list[str], timeout: int=1200)
⋮----
allowed={
⋮----
docker=[
⋮----
def _commands(candidate: dict) -> list[list[str]]
⋮----
commands=candidate.get("validation_commands")
⋮----
result=[]
⋮----
def _validate_tree(root: Path, commands: list[list[str]]) -> dict
⋮----
results=[]
⋮----
run=_docker_command(root,command)
⋮----
def execute(repo_root: Path, order: dict, candidate: dict, out: Path) -> dict
⋮----
files=_validate_candidate(order,candidate)
baseline_sha=_sha(candidate.get("baseline_sha"),"Baseline")
⋮----
temp=Path(tmp)
baseline=temp/"baseline"
replacement=temp/"replacement"
⋮----
paths=[x["path"] for x in files]
before_hashes=_hash_files(baseline,paths)
commands=_commands(candidate)
baseline_validation=_validate_tree(baseline,commands)
⋮----
candidate_sha=_commit_candidate(replacement,baseline_sha,paths)
candidate_validation=_validate_tree(replacement,commands)
after_hashes=_hash_files(replacement,paths)
⋮----
reversible=(
diff=_run(["git","diff","--stat",baseline_sha,candidate_sha],cwd=replacement)
changed=_run(["git","diff","--name-only",baseline_sha,candidate_sha],cwd=replacement)
⋮----
baseline_ok=baseline_validation["passed"]
candidate_ok=candidate_validation["passed"]
all_gates=baseline_ok and candidate_ok and reversible
verdict="GO_FOR_MANUAL_PROMOTION_REVIEW" if all_gates else "NO_GO"
⋮----
evidence={
⋮----
def main(argv=None) -> int
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
order=json.loads(Path(args.work_order).read_text(encoding="utf-8"))
candidate=json.loads(Path(args.candidate).read_text(encoding="utf-8"))
evidence=execute(Path(args.repo_root),order,candidate,out)
````

## File: architecture_replacement_learning.py
````python
"""Aggregate historical architecture replacement outcomes conservatively."""
⋮----
MIN_SAMPLES=5
CONFIDENCE_TARGET=20
REGIME_WINDOWS_DAYS=(30,90,180)
REGIME_MIN_SAMPLES=3
REGIME_DROP_THRESHOLD=0.20
SEQUENTIAL_MIN_SAMPLES=8
EWMA_ALPHA=0.35
EWMA_DROP_THRESHOLD=0.18
EWMA_RECOVERY_THRESHOLD=0.18
RECOVERY_BASELINE_MAX=0.65
RECOVERY_FINAL_MIN=0.70
CUSUM_ALLOWANCE=0.05
CUSUM_THRESHOLD=0.75
⋮----
def _wilson_lower(successes:int,samples:int,z:float=1.96)->float
⋮----
p=successes/samples
z2=z*z
denom=1.0+z2/samples
centre=p+z2/(2*samples)
margin=z*((p*(1-p)/samples+z2/(4*samples*samples))**0.5)
⋮----
def _sequential_drift(rows:list[dict])->dict
⋮----
timed=[
⋮----
n=len(timed)
⋮----
baseline_count=max(3,min(5,n//2))
baseline_rows=timed[:baseline_count]
baseline=sum(1.0 if row.get("successful") is True else 0.0 for row in baseline_rows)/baseline_count
ewma=baseline
min_ewma=ewma
max_ewma=ewma
negative_cusum=0.0
positive_cusum=0.0
max_negative_cusum=0.0
max_positive_cusum=0.0
⋮----
x=1.0 if row.get("successful") is True else 0.0
ewma=EWMA_ALPHA*x+(1.0-EWMA_ALPHA)*ewma
min_ewma=min(min_ewma,ewma)
max_ewma=max(max_ewma,ewma)
negative_cusum=max(0.0,negative_cusum+(baseline-x-CUSUM_ALLOWANCE))
positive_cusum=max(0.0,positive_cusum+(x-baseline-CUSUM_ALLOWANCE))
max_negative_cusum=max(max_negative_cusum,negative_cusum)
max_positive_cusum=max(max_positive_cusum,positive_cusum)
⋮----
ewma_drop=max(0.0,baseline-ewma)
ewma_rise=max(0.0,ewma-baseline)
detected=bool(
recovery=bool(
status="recovery" if recovery else "drift" if detected else "stable"
⋮----
def _rows(root:Path)
⋮----
candidates=[]
direct=root/"architecture-replacement-outcome.json"
⋮----
try: value=json.loads(path.read_text(encoding="utf-8"))
⋮----
def summarize(root:Path|str="studio-output", now:float|None=None)->dict
⋮----
root=Path(root)
now=float(now) if isinstance(now,(int,float)) else time.time()
stats={}
raw_by_key={}
outcomes=0
⋮----
current=row.get("current_repo"); replacement=row.get("replacement_repo")
⋮----
framework=row.get("framework") if isinstance(row.get("framework"),str) else None
project_type=row.get("project_type") if isinstance(row.get("project_type"),str) else None
primary_domain=row.get("primary_domain") if isinstance(row.get("primary_domain"),str) else None
platform=row.get("platform") if isinstance(row.get("platform"),str) else None
current_major=row.get("current_major_version")
replacement_major=row.get("replacement_major_version")
key=(current,replacement,framework,project_type,primary_domain,platform,current_major,replacement_major)
item=stats.setdefault(key,{
⋮----
q=row.get("quality_score")
⋮----
ts=row.get("observed_at")
⋮----
ts=float(ts)
first=item["first_observed_at"]
latest=item["latest_observed_at"]
⋮----
rankings=[]
⋮----
n=item["samples"]; successes=item["successes"]
success_rate=successes/n if n else 0.0
posterior=(successes+1)/(n+2) if n>=0 else 0.5
confidence=min(1.0,n/CONFIDENCE_TARGET) if n else 0.0
regress_rate=item["regressions"]/n if n else 0.0
rollback_preparation_rate=item["rollback_preparations"]/n if n else 0.0
rollback_rate=item["rollbacks"]/n if n else 0.0
mean_quality=item["quality_total"]/n if n else 0.0
windows={}
⋮----
cutoff=now-days*86400.0
recent=[
rn=len(recent)
rs=sum(int(row.get("successful") is True) for row in recent)
rr=sum(int(row.get("regressed") is True) for row in recent)
⋮----
comparable=[
recent_window=min(comparable,key=lambda pair:pair[0]) if comparable else None
recent_rate=recent_window[1]["success_rate"] if recent_window else None
regime_drop=(success_rate-float(recent_rate)) if isinstance(recent_rate,(int,float)) else 0.0
recent_regression=recent_window[1]["regression_rate"] if recent_window else None
regime_shift=bool(
sequential=_sequential_drift(raw_by_key.get((
````

## File: architecture_replacement_merge_gate.py
````python
"""Create a content-bound merge authorization template after PR validation.

This module is read-only. It does not call GitHub and does not merge. Its output can only
be consumed by the explicit merge executor after a separate authorization record is supplied.
"""
⋮----
class ReplacementMergeGateError(RuntimeError)
⋮----
def _sha(value,label)
⋮----
def build(validation: dict, review: dict, package: dict, persisted: dict) -> dict
⋮----
number=validation.get("pull_request")
branch=validation.get("branch")
head_sha=_sha(validation.get("head_sha"),"Head")
⋮----
work_order_id=review.get("work_order_id")
⋮----
payload={
authorization_id=hashlib.sha256(
⋮----
def write(validation: dict, review: dict, package: dict, persisted: dict, out: Path) -> dict
⋮----
result=build(validation,review,package,persisted)
````

## File: architecture_replacement_merge.py
````python
"""Explicit architecture replacement merge executor.

This is the only replacement component allowed to call GitHub's merge endpoint. It requires
an explicit authorization record bound to the exact PR head SHA and revalidates the PR,
trusted checks, file scope/content, and clean merge state immediately before merging.
"""
⋮----
class ReplacementMergeError(RuntimeError)
⋮----
def _verify_authorization(gate: dict, authorization: dict) -> None
⋮----
validation=validate_pr(review,package,persisted,token,repository,requester=requester)
⋮----
api="https://api.github.com/repos/"+repository
number=gate["pull_request"]
head_sha=gate["head_sha"]
⋮----
# Final TOCTOU re-read immediately before the write.
pr=requester(api+"/pulls/"+str(number),token)
⋮----
result=requester(
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
review=json.loads(Path(args.review).read_text(encoding="utf-8"))
package=json.loads(Path(args.package).read_text(encoding="utf-8"))
persisted=json.loads(Path(args.persisted).read_text(encoding="utf-8"))
gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
authorization=json.loads(Path(args.authorization).read_text(encoding="utf-8"))
result=merge(
````

## File: architecture_replacement_outcome.py
````python
"""Record post-merge replacement outcomes for empirical replacement learning."""
⋮----
def _identity(work_order: dict, merged: dict) -> str
⋮----
payload={
⋮----
def build(work_order: dict, merged: dict, postmerge: dict, rollback: dict | None = None) -> dict
⋮----
healthy=postmerge.get("status")=="post_merge_healthy" and postmerge.get("post_merge_healthy") is True
regressed=postmerge.get("status")=="post_merge_regression" or postmerge.get("rollback_required") is True
rollback_prepared=isinstance(rollback,dict) and rollback.get("status")=="replacement_rollback_pr_created"
rolled_back=isinstance(rollback,dict) and rollback.get("status")=="replacement_rollback_merged"
⋮----
quality=100.0
⋮----
failed=len(postmerge.get("failed_checks",[])) if isinstance(postmerge.get("failed_checks"),list) else 0
mismatches=len(postmerge.get("content_mismatches",[])) if isinstance(postmerge.get("content_mismatches"),list) else 0
quality=max(0.0,30.0-10.0*failed-15.0*mismatches)
⋮----
quality=50.0
⋮----
def write(work_order: dict, merged: dict, postmerge: dict, out: Path, rollback: dict | None = None) -> dict
⋮----
result=build(work_order,merged,postmerge,rollback=rollback)
````

## File: architecture_replacement_persist.py
````python
"""Persist an explicitly approved architecture replacement as a content-bound branch and PR.

This module performs GitHub writes only when invoked directly with an approved promotion
review + PR package. It never merges the pull request.
"""
⋮----
class ReplacementPersistenceError(RuntimeError)
⋮----
def _request(url, token, method="GET", payload=None, allow_404=False)
⋮----
data=None if payload is None else canonical(payload).encode("utf-8")
req=urllib.request.Request(
⋮----
def _valid_repository(value)
⋮----
def _sha(value,label)
⋮----
def _load_candidate(path: Path)
⋮----
value=json.loads(path.read_text(encoding="utf-8"))
⋮----
def _existing_pr(api, token, owner, branch, head_sha)
⋮----
query=urllib.parse.urlencode({
pulls=_request(api+"/pulls?"+query,token)
⋮----
matches=[
⋮----
def persist(repo_root: Path, review: dict, package: dict, candidate_path: Path, token: str, repository: str)
⋮----
baseline_sha=_sha(package.get("baseline_sha"),"Baseline")
candidate_sha=_sha(package.get("candidate_sha"),"Candidate")
branch=package.get("branch")
⋮----
root=repo_root.resolve()
candidate=_load_candidate(candidate_path)
⋮----
api="https://api.github.com/repos/"+repository
owner=repository.split("/",1)[0]
base_commit=_request(api+"/git/commits/"+baseline_sha,token)
base_tree=base_commit.get("tree",{}).get("sha") if isinstance(base_commit,dict) else None
⋮----
tree_entries=[]
⋮----
blob=_request(api+"/git/blobs",token,"POST",{
blob_sha=blob.get("sha") if isinstance(blob,dict) else None
⋮----
tree=_request(api+"/git/trees",token,"POST",{"base_tree":base_tree,"tree":tree_entries})
tree_sha=tree.get("sha") if isinstance(tree,dict) else None
⋮----
commit=_request(api+"/git/commits",token,"POST",{
commit_sha=commit.get("sha") if isinstance(commit,dict) else None
⋮----
# The isolated executor candidate SHA is local-only. The GitHub commit is content-bound
# by the candidate digest + branch identity, not required to equal the local commit SHA.
⋮----
existing=_existing_pr(api,token,owner,branch,commit_sha)
⋮----
body=package.get("body",{})
pr=_request(api+"/pulls",token,"POST",{
number=pr.get("number") if isinstance(pr,dict) else None
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
review=json.loads(Path(args.review).read_text(encoding="utf-8"))
package=json.loads(Path(args.package).read_text(encoding="utf-8"))
result=persist(
````

## File: architecture_replacement_pipeline.py
````python
"""Manual/explicit replacement pipeline: synthesize candidate, then benchmark it in isolation.

This module never promotes or merges. It is intentionally not called automatically by
orchestrator.py. It can be invoked only with an explicit work-order path.
"""
⋮----
def run(work_order_path: Path, repo_root: Path, out: Path) -> dict
⋮----
order=json.loads(work_order_path.read_text(encoding="utf-8"))
candidate=synthesize_candidate(work_order_path,repo_root,out)
execution=execute_candidate(repo_root,order,candidate,out)
promotion_review=None
pr_package=None
⋮----
promotion_review=write_promotion_review(order,candidate,execution,out)
pr_package=write_pr_package(promotion_review,candidate,out)
result={
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
result=run(Path(args.work_order),Path(args.repo_root),out)
````

## File: architecture_replacement_planner.py
````python
"""Create a bounded migration plan from evidence-backed architecture deprecation candidates."""
⋮----
MAX_PLANS = 8
LOW_RISK_DELTA = 15.0
MEDIUM_RISK_DELTA = 8.0
⋮----
CONTEXT_WEIGHTS = {
MIN_TRANSFERABILITY_FOR_RISK = 0.72
MIN_TRANSFERABILITY_FOR_POSITIVE_BIAS = 0.55
MAX_FUSED_HISTORIES = 8
MIN_FUSION_TRANSFERABILITY = 0.20
RECENCY_HALF_LIFE_DAYS = 180.0
RECENCY_FLOOR = 0.20
⋮----
def _major(value)
⋮----
def _version_similarity(expected, observed) -> float
⋮----
expected=_major(expected)
observed=_major(observed)
⋮----
gap=abs(expected-observed)
⋮----
def _numeric_similarity(expected, observed) -> float
⋮----
expected_valid=isinstance(expected,(int,float)) and not isinstance(expected,bool)
observed_valid=isinstance(observed,(int,float)) and not isinstance(observed,bool)
⋮----
gap=abs(float(expected)-float(observed))
⋮----
def _categorical_similarity(expected, observed) -> float
⋮----
def _compatibility_distance(history: dict | None, context: dict) -> dict
⋮----
components={}
⋮----
expected_current=_major(context.get("current_major_version"))
expected_replacement=_major(context.get("replacement_major_version"))
observed_current=_major(history.get("current_major_version"))
observed_replacement=_major(history.get("replacement_major_version"))
expected_jump=(expected_replacement-expected_current) if expected_current is not None and expected_replacement is not None else None
observed_jump=(observed_replacement-observed_current) if observed_current is not None and observed_replacement is not None else None
⋮----
transferability=sum(CONTEXT_WEIGHTS[key]*components[key] for key in CONTEXT_WEIGHTS)
⋮----
# Explicit categorical incompatibilities are stronger evidence than a merely
# nearby version number, so they cap cross-context transfer.
⋮----
transferability=min(transferability,0.20)
⋮----
transferability=min(transferability,0.60)
⋮----
transferability=min(transferability,0.65)
⋮----
transferability=max(0.0,min(1.0,transferability))
⋮----
def _index(recommendations: dict) -> dict[str, dict]
⋮----
rows = recommendations.get("matches", []) if isinstance(recommendations, dict) else []
⋮----
def _risk(current: dict, replacement: dict, benchmark_delta: float | None) -> str
⋮----
current_caps = set(current.get("capabilities", []) if isinstance(current.get("capabilities"), list) else [])
replacement_caps = set(replacement.get("capabilities", []) if isinstance(replacement.get("capabilities"), list) else [])
missing = current_caps - replacement_caps
delta = float(benchmark_delta) if isinstance(benchmark_delta, (int, float)) else 0.0
⋮----
def _replacement_histories(learning: dict | None, current_repo: str, replacement_repo: str, context: dict | None = None) -> list[dict]
⋮----
rows=learning.get("rankings")
⋮----
context=context if isinstance(context,dict) else {}
candidates=[]
⋮----
compatibility=_compatibility_distance(row,context)
transferability=float(compatibility.get("transferability",0.0) or 0.0)
⋮----
item=dict(row)
⋮----
def _replacement_history(learning: dict | None, current_repo: str, replacement_repo: str, context: dict | None = None) -> dict | None
⋮----
histories=_replacement_histories(learning,current_repo,replacement_repo,context=context)
⋮----
def _recency_factor(history: dict, now: float | None = None) -> float
⋮----
latest=history.get("latest_observed_at")
⋮----
now=float(now) if isinstance(now,(int,float)) else time.time()
age_seconds=max(0.0,now-float(latest))
age_days=age_seconds/86400.0
decay=math.pow(0.5,age_days/RECENCY_HALF_LIFE_DAYS)
⋮----
def _effective_sample_recency(history: dict, now: float | None = None) -> float
⋮----
# Legacy observations without timestamps remain usable for sample-mass
# confidence, while their actual fusion influence stays conservatively 0.5.
⋮----
def _fusion_weight(history: dict, now: float | None = None) -> float
⋮----
compatibility=history.get("compatibility") if isinstance(history.get("compatibility"),dict) else {}
⋮----
confidence=float(history.get("evidence_confidence",0.0) or 0.0)
samples=max(0,int(history.get("samples",0) or 0))
sample_factor=min(1.0,samples/20.0)
eligible_factor=1.0 if history.get("eligible_for_bias") is True else 0.35
recency=_recency_factor(history,now=now)
⋮----
def _fuse_histories(histories: list[dict], now: float | None = None) -> dict | None
⋮----
weighted=[]
⋮----
weight=_fusion_weight(history,now=now)
⋮----
total=sum(weight for weight,_ in weighted)
⋮----
def avg(field,default=0.0)
⋮----
effective_samples=sum(
max_transfer=max(
fused_transfer=sum(
positive_weight=sum(
negative_weight=sum(
conflict_ratio=min(positive_weight,negative_weight)/total if total>0 else 0.0
evidence_conflict=positive_weight/total>=0.20 and negative_weight/total>=0.20
contributors=[]
⋮----
compatibility=history.get("compatibility",{})
⋮----
recency_weighted=sum(
regime_shift_weight=sum(
regime_shift=regime_shift_weight>=0.50
sequential_drift_weight=sum(
sequential_drift=sequential_drift_weight>=0.50
recovery_weight=sum(
recovery_candidate=(
⋮----
def _history_context_weight(history: dict | None, context: dict) -> float
⋮----
compatibility=history.get("compatibility")
⋮----
def _impact(current: dict, replacement: dict) -> dict
⋮----
current_lang = set(current.get("languages", []) if isinstance(current.get("languages"), list) else [])
replacement_lang = set(replacement.get("languages", []) if isinstance(replacement.get("languages"), list) else [])
current_platform = set(current.get("platforms", []) if isinstance(current.get("platforms"), list) else [])
replacement_platform = set(replacement.get("platforms", []) if isinstance(replacement.get("platforms"), list) else [])
⋮----
def plan(obsolescence: dict, recommendations: dict, learning: dict | None = None, reputation_registry: dict | None = None) -> dict
⋮----
recs = _index(recommendations)
rows = obsolescence.get("deprecation_candidates", []) if isinstance(obsolescence, dict) else []
plans = []
⋮----
current_repo = row.get("repo")
replacement_repo = row.get("replacement_candidate")
⋮----
current = recs.get(current_repo, {})
replacement = recs.get(replacement_repo, {})
impact = _impact(current, replacement)
risk = _risk(current, replacement, row.get("benchmark_delta"))
context={
histories = _replacement_histories(learning,current_repo,replacement_repo,context=context)
history = histories[0] if histories else None
fused_history = _fuse_histories(histories)
empirical_status="unobserved"
empirical_priority_adjustment=0.0
history_context_weight=(
evidence=fused_history if isinstance(fused_history,dict) else history
desired_reputation=reputation_desired_state(evidence)
reputation={
persisted_reputation=lookup_reputation(reputation_registry,context)
⋮----
current_policy_digest=transition_policy_digest()
persisted_policy_version=persisted_reputation.get("transition_policy_version")
persisted_policy_digest=persisted_reputation.get("transition_policy_digest")
policy_revalidation_required=(
⋮----
regression=float(evidence.get("regression_rate",0.0) or 0.0)
wilson=float(evidence.get("wilson_lower_95",0.0) or 0.0)
confidence=float(evidence.get("evidence_confidence",0.0) or 0.0)
empirical_priority_adjustment=max(-10.0,min(5.0,(wilson-0.5)*10.0-regression*10.0))*confidence*history_context_weight
⋮----
empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)
risk="high"
empirical_status="sequential_drift_detected"
⋮----
empirical_status="regime_shift_detected"
⋮----
empirical_status="conflicting_history"
⋮----
empirical_priority_adjustment=min(0.0,empirical_priority_adjustment)*0.25
empirical_status="recovery_candidate"
⋮----
empirical_status="historically_risky"
⋮----
empirical_status="historically_supported"
⋮----
empirical_status="mixed_history"
⋮----
reputation_state=reputation.get("state")
reputation_is_persisted=reputation.get("source")=="persistent_registry"
⋮----
empirical_status="persisted_quarantine"
⋮----
empirical_status="persisted_degraded"
⋮----
empirical_status="persisted_recovering"
⋮----
gates = [
⋮----
transition_gates=reputation.get("required_transition_gates")
⋮----
def write(obsolescence: dict, recommendations: dict, out: Path, learning: dict | None = None, reputation_registry: dict | None = None) -> dict
⋮----
result = plan(obsolescence, recommendations, learning=learning, reputation_registry=reputation_registry)
````

## File: architecture_replacement_postmerge_pipeline.py
````python
"""Finalize post-merge replacement evidence and update empirical replacement learning.

Read-only with respect to GitHub. It verifies the exact merge, records a durable outcome,
updates the bounded historical learning file, and emits a rollback gate when regression
evidence requires one.
"""
⋮----
def _load(path: Path, label: str) -> dict
⋮----
value=json.loads(path.read_text(encoding="utf-8"))
⋮----
def run(work_order_path: Path, merged_path: Path, package_path: Path, out: Path, token: str, repository: str) -> dict
⋮----
work_order=_load(work_order_path,"work order")
merged=_load(merged_path,"merged evidence")
package=_load(package_path,"PR package")
⋮----
postmerge=verify_postmerge(merged,package,token,repository)
⋮----
rollback_gate=None
⋮----
rollback_gate=write_rollback_gate(postmerge,merged,package,out)
⋮----
terminal=postmerge.get("status") in {"post_merge_healthy","post_merge_regression"}
outcome=None
⋮----
outcome=write_replacement_outcome(work_order,merged,postmerge,out)
historical_root=root_for_output(out)
learning=summarize_replacement_learning(historical_root)
⋮----
reputation_entry=None
⋮----
context={
evidence=next((
reputation_entry=update_replacement_reputation(
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
result=run(
````

## File: architecture_replacement_postmerge.py
````python
"""Post-merge assurance for architecture replacements.

Read-only verifier for the exact merge commit. It checks that main contains the merge,
that trusted GitHub Actions checks on that exact merge SHA succeeded, and that approved
replacement file content survived the merge unchanged. It emits rollback-required evidence
on any regression but performs no rollback or GitHub write.
"""
⋮----
class ReplacementPostMergeError(RuntimeError)
⋮----
def _sha(value,label)
⋮----
def _expected_files(package)
⋮----
rows=package.get("files") if isinstance(package,dict) else None
⋮----
out={}
⋮----
path=row.get("path")
digest=row.get("sha256")
⋮----
def _content_bytes(value)
⋮----
def verify(merged,package,token,repository,requester=_request)
⋮----
merge_sha=_sha(merged.get("merge_sha"),"Merge")
api="https://api.github.com/repos/"+repository
⋮----
branch=requester(api+"/branches/main",token)
main_sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
⋮----
expected=_expected_files(package)
verified=[]
mismatches=[]
⋮----
value=requester(api+"/contents/"+quote(path,safe="/")+"?ref="+merge_sha,token)
actual=hashlib.sha256(_content_bytes(value)).hexdigest()
⋮----
checks=requester(api+"/commits/"+merge_sha+"/check-runs?per_page=100",token)
runs=checks.get("check_runs") if isinstance(checks,dict) else None
⋮----
check_result=validate_check_runs(runs,repository)
missing=check_result["missing_checks"]
incomplete=check_result["incomplete_checks"]
failed=check_result["failed_checks"]
⋮----
status="post_merge_regression"
rollback=True
healthy=False
⋮----
status="awaiting_post_merge_checks"
rollback=False
⋮----
status="post_merge_healthy"
⋮----
healthy=True
````

## File: architecture_replacement_pr_package.py
````python
"""Prepare a content-bound pull-request package for an approved replacement review.

This module does not call GitHub, does not push, and does not merge. It emits the exact
branch name, title, body, content digest, and rollback requirements that a separate
authorized persistence step may use.
"""
⋮----
class ReplacementPRPackageError(RuntimeError)
⋮----
def _sha(value,label)
⋮----
def build(review: dict, candidate: dict) -> dict
⋮----
baseline=_sha(review.get("baseline_sha"),"Baseline")
candidate_sha=_sha(review.get("candidate_sha"),"Candidate")
digest=review.get("candidate_digest")
⋮----
identity=hashlib.sha256(
branch=f"architecture/replacement-{identity}"
⋮----
files=[]
⋮----
def write(review: dict, candidate: dict, out: Path) -> dict
⋮----
result=build(review,candidate)
````

## File: architecture_replacement_pr_validator.py
````python
"""Validate persisted replacement pull requests against immutable local approval evidence.

Read-only GitHub validator: verifies PR identity, exact file scope/content hashes, trusted
GitHub Actions checks, branch/head binding, and clean merge state. It never writes or merges.
"""
⋮----
class ReplacementPRValidationError(RuntimeError)
⋮----
def _expected_files(package: dict) -> dict[str,str]
⋮----
rows=package.get("files") if isinstance(package,dict) else None
⋮----
out={}
⋮----
path=row.get("path")
digest=row.get("sha256")
⋮----
def _decode_content(value: dict) -> bytes
⋮----
content=value.get("content")
⋮----
def validate(review: dict, package: dict, persisted: dict, token: str, repository: str, requester=_request) -> dict
⋮----
number=persisted.get("pull_request")
head_sha=persisted.get("commit_sha")
branch=persisted.get("branch")
⋮----
api="https://api.github.com/repos/"+repository
pr=requester(api+"/pulls/"+str(number),token)
⋮----
expected=_expected_files(package)
files=requester(api+"/pulls/"+str(number)+"/files?per_page=100",token)
⋮----
names={row.get("filename") for row in files if isinstance(row,dict)}
⋮----
verified=[]
⋮----
content=requester(
actual=hashlib.sha256(_decode_content(content)).hexdigest()
⋮----
checks=requester(api+"/commits/"+head_sha+"/check-runs?per_page=100",token)
runs=checks.get("check_runs") if isinstance(checks,dict) else None
⋮----
check_result=validate_check_runs(runs,repository)
missing=check_result["missing_checks"]
⋮----
incomplete=check_result["incomplete_checks"]
⋮----
failed=check_result["failed_checks"]
⋮----
# Re-fetch immediately before readiness decision to bind the final state.
final_pr=requester(api+"/pulls/"+str(number),token)
⋮----
draft=final_pr.get("draft") is True
clean=final_pr.get("mergeable") is True and final_pr.get("mergeable_state")=="clean"
⋮----
status="validated_draft"
ready=False
⋮----
status="awaiting_clean_merge_state"
⋮----
status="ready_to_merge"
ready=True
````

## File: architecture_replacement_promotion.py
````python
"""Trusted review controller for isolated architecture replacement evidence.

This controller never modifies the repository, never pushes, and never merges.
It deterministically re-checks the replacement evidence and emits a promotion-review
package only when every required identity and safety condition still holds.
"""
⋮----
class ReplacementPromotionError(RuntimeError)
⋮----
def _sha(value, label)
⋮----
def _candidate_digest(candidate: dict) -> str
⋮----
files=candidate.get("files")
⋮----
payload={
⋮----
def review(work_order: dict, candidate: dict, execution: dict) -> dict
⋮----
order_id=work_order.get("id")
⋮----
current=work_order.get("current_repo")
replacement=work_order.get("replacement_repo")
⋮----
baseline=_sha(candidate.get("baseline_sha"),"Baseline")
⋮----
candidate_sha=_sha(execution.get("candidate_sha"),"Candidate")
⋮----
baseline_validation=execution.get("baseline_validation")
candidate_validation=execution.get("candidate_validation")
⋮----
required=work_order.get("required_gates")
required=[x for x in required if isinstance(x,str)] if isinstance(required,list) else []
⋮----
def write(work_order: dict, candidate: dict, execution: dict, out: Path) -> dict
⋮----
result=review(work_order,candidate,execution)
````

## File: architecture_replacement_reputation.py
````python
"""Persistent reputation registry with audited hysteretic state transitions."""
⋮----
REGISTRY_VERSION=5
MAX_AUDIT_EVENTS=500
RECOVERY_CONFIRMATIONS_REQUIRED=2
RECOVERY_MIN_DWELL_SECONDS=7*24*60*60
RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES=2.0
TRANSITION_POLICY_VERSION=2
TRANSITION_POLICY={
⋮----
REPUTATION_STATES={"UNOBSERVED","EXPERIMENTAL","TRUSTED","DEGRADED","QUARANTINED","RECOVERING"}
DANGEROUS_STATES={"DEGRADED","QUARANTINED","RECOVERING"}
DANGEROUS_STATE_GATES={
⋮----
def transition_policy_digest(policy: dict | None=None) -> str
⋮----
policy=TRANSITION_POLICY if policy is None else policy
payload={
⋮----
def validate_transition_policy(policy: dict | None=None) -> dict
⋮----
errors=[]
warnings=[]
⋮----
unknown_sources=sorted(set(policy)-REPUTATION_STATES)
⋮----
adjacency={state:set() for state in REPUTATION_STATES}
⋮----
gates=rule.get("required_gates",[])
⋮----
gates=[]
required=DANGEROUS_STATE_GATES.get(target)
⋮----
# Reachability catches dead states and accidental policy partitions.
reachable={"UNOBSERVED"}
frontier=["UNOBSERVED"]
⋮----
source=frontier.pop()
⋮----
unreachable=sorted(REPUTATION_STATES-reachable)
⋮----
# Every dangerous state must have a defined escape/recovery route.
⋮----
# There must be no path from a degraded/quarantined state to TRUSTED
# that bypasses RECOVERING.
⋮----
frontier=[(origin,frozenset({origin}))]
⋮----
frontier=[]
⋮----
def assert_transition_policy_valid(policy: dict | None=None) -> None
⋮----
validation=validate_transition_policy(policy)
⋮----
def transition_policy(previous: str | None, target: str) -> dict
⋮----
previous=previous if isinstance(previous,str) else "UNOBSERVED"
⋮----
row=TRANSITION_POLICY.get(previous,{})
rule=row.get(target) if isinstance(row,dict) else None
⋮----
def _identity(context: dict) -> str
⋮----
def desired_state(evidence: dict | None) -> dict
⋮----
samples=max(0,int(evidence.get("effective_samples",evidence.get("samples",0)) or 0))
confidence=float(evidence.get("evidence_confidence",0.0) or 0.0)
wilson=float(evidence.get("wilson_lower_95",0.0) or 0.0)
regression=float(evidence.get("regression_rate",0.0) or 0.0)
⋮----
sequential=evidence.get("sequential_drift")
sequential_detected=(
recovery_detected=(
⋮----
def _effective_samples(evidence: dict | None) -> float
⋮----
value=evidence.get("effective_samples",evidence.get("samples",0))
⋮----
previous=previous_entry.get("state") if isinstance(previous_entry.get("state"),str) else "UNOBSERVED"
confirmations=int(previous_entry.get("recovery_confirmations",0) or 0)
current_samples=_effective_samples(evidence)
state_since=float(previous_entry.get("state_since",previous_entry.get("updated_at",now)) or now)
recovery_started_at=previous_entry.get("recovery_started_at")
recovery_start_samples=previous_entry.get("recovery_start_effective_samples")
⋮----
meta={
⋮----
# Downward safety transitions are intentionally fast.
⋮----
reason="trusted_degraded" if desired=="DEGRADED" else "trusted_evidence_weakened"
⋮----
# A degraded or quarantined replacement can only climb through RECOVERING.
⋮----
started=now
⋮----
started=float(recovery_started_at) if isinstance(recovery_started_at,(int,float)) else state_since
start_samples=float(recovery_start_samples) if isinstance(recovery_start_samples,(int,float)) else current_samples
new_samples=max(0.0,current_samples-start_samples)
⋮----
dwell_ok=(now-started)>=RECOVERY_MIN_DWELL_SECONDS
samples_ok=new_samples>=RECOVERY_MIN_NEW_EFFECTIVE_SAMPLES
confirmations_ok=confirmations>=RECOVERY_CONFIRMATIONS_REQUIRED
⋮----
reason="recovery_minimum_dwell_pending"
⋮----
reason="recovery_new_evidence_pending"
⋮----
reason="recovery_confirmation_pending"
⋮----
reason="recovery_ongoing"
⋮----
# Bootstrap and non-recovery transitions use the current evidence directly.
⋮----
def apply(registry: dict | None, context: dict, evidence: dict | None, *, now: float | None=None) -> tuple[dict,dict]
⋮----
now=float(now) if isinstance(now,(int,float)) else time.time()
registry=registry if isinstance(registry,dict) else {}
entries=registry.get("entries") if isinstance(registry.get("entries"),dict) else {}
audit=registry.get("audit") if isinstance(registry.get("audit"),list) else []
key=_identity(context)
previous_entry=entries.get(key) if isinstance(entries.get(key),dict) else {}
previous_state=previous_entry.get("state") if isinstance(previous_entry.get("state"),str) else "UNOBSERVED"
desired=desired_state(evidence)
requested_rule=transition_policy(previous_state,desired["state"])
⋮----
applied_rule=transition_policy(previous_state,new_state)
⋮----
new_state=previous_state
new_confirmations=int(previous_entry.get("recovery_confirmations",0) or 0)
transition_reason="transition_blocked_by_policy"
⋮----
entry={
⋮----
event={
entries=dict(entries)
⋮----
audit=(audit+[event])[-MAX_AUDIT_EVENTS:]
updated={
⋮----
def load(path: Path) -> dict
⋮----
value=json.loads(path.read_text(encoding="utf-8"))
⋮----
def update(path: Path, context: dict, evidence: dict | None, *, now: float | None=None) -> dict
⋮----
def lookup(registry: dict | None, context: dict) -> dict | None
⋮----
entries=registry.get("entries")
⋮----
value=entries.get(_identity(context))
````

## File: architecture_replacement_rollback_gate.py
````python
"""Prepare a content-bound rollback gate for a regressed architecture replacement.

No network writes. The gate binds a future explicit rollback authorization to the exact
merge commit, original replacement head, PR, work order, and approved pre-replacement base.
"""
⋮----
class ReplacementRollbackGateError(RuntimeError)
⋮----
def _sha(value,label)
⋮----
def build(postmerge,merged,package)
⋮----
merge_sha=_sha(merged.get("merge_sha"),"Merge")
head_sha=_sha(merged.get("head_sha"),"Replacement head")
baseline_sha=_sha(package.get("baseline_sha"),"Baseline")
payload={
authorization_id=hashlib.sha256(
⋮----
def write(postmerge,merged,package,out:Path)
⋮----
result=build(postmerge,merged,package)
````

## File: architecture_replacement_rollback.py
````python
"""Explicit GitHub rollback executor for a regressed architecture replacement.

Creates a revert commit and a draft rollback PR. It never force-pushes main and never merges
the rollback automatically.
"""
⋮----
class ReplacementRollbackError(RuntimeError)
⋮----
def _verify(gate,authorization)
⋮----
def execute(gate,authorization,token,repository,requester=_request)
⋮----
merge_sha=gate.get("merge_sha")
⋮----
api="https://api.github.com/repos/"+repository
⋮----
branch=requester(api+"/branches/main",token)
main_sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
⋮----
merge_commit=requester(api+"/git/commits/"+merge_sha,token)
parents=merge_commit.get("parents") if isinstance(merge_commit,dict) else None
parent_shas=[x.get("sha") for x in parents] if isinstance(parents,list) else []
baseline=gate.get("baseline_sha")
⋮----
baseline_commit=requester(api+"/git/commits/"+baseline,token)
baseline_tree=baseline_commit.get("tree",{}).get("sha") if isinstance(baseline_commit,dict) else None
⋮----
revert=requester(api+"/git/commits",token,"POST",{
revert_sha=revert.get("sha") if isinstance(revert,dict) else None
⋮----
branch_name="architecture/rollback-"+gate["authorization_id"][:16]+"-"+revert_sha
⋮----
pr=requester(api+"/pulls",token,"POST",{
number=pr.get("number") if isinstance(pr,dict) else None
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
⋮----
gate=json.loads(Path(args.gate).read_text(encoding="utf-8"))
authorization=json.loads(Path(args.authorization).read_text(encoding="utf-8"))
result=execute(gate,authorization,os.environ.get("STUDIO_GITHUB_TOKEN",""),os.environ.get("GITHUB_REPOSITORY",""))
````

## File: architecture_replacement_synthesis.py
````python
"""Synthesize a bounded architecture replacement candidate from local project evidence."""
⋮----
MAX_CONTEXT_FILES=20
MAX_CONTEXT_BYTES=96*1024
TEXT_EXTENSIONS={".py",".dart",".yaml",".yml",".json",".toml",".gradle",".kts",".js",".ts",".tsx",".jsx",".md"}
MANIFESTS=("pubspec.yaml","pubspec.lock","package.json","package-lock.json","pnpm-lock.yaml","pyproject.toml","requirements.txt","build.gradle","build.gradle.kts")
⋮----
SYSTEM="""You are preparing ONE dependency/library replacement candidate for an isolated benchmark.
⋮----
def _baseline_sha(root)
⋮----
result=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=False)
sha=result.stdout.strip()
⋮----
def _collect_context(root,current_repo,replacement_repo)
⋮----
candidates=[]
⋮----
path=root/name
⋮----
needles={
⋮----
rel=path.relative_to(root).as_posix()
⋮----
content=path.read_text(encoding="utf-8")
⋮----
lower=content.lower()
⋮----
unique=[]
seen=set()
total=0
⋮----
encoded=content.encode("utf-8")
remaining=MAX_CONTEXT_BYTES-total
⋮----
content=encoded[:remaining].decode("utf-8",errors="ignore")
⋮----
def _prompt(order,root)
⋮----
current=order.get("current_repo")
replacement=order.get("replacement_repo")
⋮----
payload={
⋮----
def _response(messages,api=None,model=None)
⋮----
selected=model or os.environ.get("STUDIO_CODE_MODEL") or os.environ.get("STUDIO_MODEL")
⋮----
providers=load_providers(prefer_free=True)
⋮----
providers=candidates_for("implementation",providers=providers)
⋮----
last=None
⋮----
selected=model or provider.model_for("implementation")
routed=API(provider.base,provider.key)
⋮----
last=exc
⋮----
def synthesize(order,root,api=None,model=None)
⋮----
messages=[
response=_response(messages,api=api,model=model)
⋮----
choice=response["choices"][0]
⋮----
raw=choice["message"]["content"].strip()
⋮----
raw=raw.split("\n",1)[1].rsplit("```",1)[0]
candidate=json.loads(raw)
⋮----
def consume(order_path,root,out,api=None,model=None)
⋮----
order=json.loads(Path(order_path).read_text(encoding="utf-8"))
candidate=synthesize(order,Path(root),api=api,model=model)
out=Path(out)
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
out=Path(args.out)
⋮----
result=consume(args.work_order,args.repo_root,out)
````

## File: architecture_replacement_work_order.py
````python
"""Convert advisory replacement plans into bounded isolated migration work orders."""
⋮----
MAX_WORK_ORDERS = 4
⋮----
def _id(current_repo: str, replacement_repo: str) -> str
⋮----
payload=f"{current_repo}->{replacement_repo}".encode("utf-8")
⋮----
def build(replacement_plan: dict) -> dict
⋮----
rows = replacement_plan.get("replacement_plans", []) if isinstance(replacement_plan, dict) else []
work_orders = []
⋮----
current = row.get("current_repo")
replacement = row.get("replacement_repo")
⋮----
def write(replacement_plan: dict, out: Path) -> dict
⋮----
result=build(replacement_plan)
⋮----
order_dir=out/"replacement-work-orders"
````

## File: architecture_reputation_policy_approval.py
````python
"""Approval provenance and append-only anti-replay ledger for reputation policy migrations."""
⋮----
LEDGER_VERSION=1
GENESIS_HASH="0"*64
ROLE_REVIEWER="reviewer"
ROLE_RISK_OWNER="risk_owner"
⋮----
class ApprovalProvenanceError(RuntimeError)
⋮----
def _canonical(v)
⋮----
def approval_digest(approval: dict) -> str
⋮----
payload={k:v for k,v in approval.items() if k!="approval_digest"}
⋮----
def validate_approval(approval: dict, plan: dict, *, reinforced: bool) -> dict
⋮----
reviewer=approval.get("reviewer")
⋮----
roles=reviewer.get("roles")
⋮----
second=approval.get("second_reviewer")
⋮----
second_roles=second.get("roles")
⋮----
expected=approval_digest(approval)
⋮----
def new_ledger() -> dict
⋮----
def consume(ledger: dict | None, *, migration_id: str, review_digest: str, approval_digest_value: str, applied_at: float) -> dict
⋮----
ledger=dict(ledger) if isinstance(ledger,dict) else new_ledger()
events=list(ledger.get("events",[])) if isinstance(ledger.get("events"),list) else []
⋮----
previous=ledger.get("head") if isinstance(ledger.get("head"),str) else GENESIS_HASH
body={"sequence":len(events)+1,"previous_hash":previous,"migration_id":migration_id,"review_digest":review_digest,"approval_digest":approval_digest_value,"applied_at":applied_at}
event_hash=hashlib.sha256(_canonical(body).encode()).hexdigest()
event={**body,"event_hash":event_hash}
⋮----
def validate_ledger(ledger: dict | None) -> dict
⋮----
previous=GENESIS_HASH
events=ledger.get("events")
⋮----
seen=set()
⋮----
body={k:v for k,v in event.items() if k!="event_hash"}
digest=hashlib.sha256(_canonical(body).encode()).hexdigest()
⋮----
previous=digest
⋮----
def validate_github_attestation(attestation: dict, plan: dict, *, reinforced: bool) -> dict
⋮----
"""Validate already-fetched GitHub evidence. Network/API retrieval stays outside this pure validator."""
⋮----
required=("repository","commit_sha","pull_request","workflow_run_id")
⋮----
head_commit_timestamp=attestation.get("head_commit_timestamp")
⋮----
reviewer=attestation.get("reviewer")
⋮----
submitted=reviewer.get("submitted_at_epoch")
⋮----
second=attestation.get("second_reviewer")
⋮----
second_submitted=second.get("submitted_at_epoch")
⋮----
pr_identity=attestation.get("pr_identity")
⋮----
checks=attestation.get("required_checks")
⋮----
common_run_id=checks.get("common_workflow_run_id")
⋮----
required_checks=checks.get("required_checks")
passed_checks=checks.get("passed_checks")
evidence=checks.get("check_evidence")
⋮----
row=evidence.get(name)
⋮----
check_timestamp=row.get("timestamp")
⋮----
target=plan.get("github_review_target") if isinstance(plan,dict) else None
⋮----
expected={
actual={
⋮----
workflow_file=attestation.get("workflow_file")
⋮----
content_b64=workflow_file.get("content_b64")
⋮----
workflow_raw=base64.b64decode(content_b64,validate=False)
workflow_text=workflow_raw.decode("utf-8")
⋮----
workflow_policy_validation=validate_workflow_text(workflow_text)
⋮----
semantic_digest=workflow_policy_validation.get("semantic_digest")
⋮----
workflow_expected={
workflow_actual={
⋮----
workflow=attestation.get("workflow")
⋮----
workflow_timestamp=workflow.get("timestamp")
⋮----
payload={k:v for k,v in attestation.items() if k!="attestation_digest"}
digest=hashlib.sha256(_canonical(payload).encode()).hexdigest()
⋮----
def approval_from_github_attestation(attestation: dict, plan: dict, *, reinforced: bool) -> dict
⋮----
github=validate_github_attestation(attestation,plan,reinforced=reinforced)
approval={
````

## File: architecture_reputation_policy_github_attestation.py
````python
"""Build deterministic GitHub evidence for reputation-policy migration approval.

This module is intentionally connector-agnostic: callers fetch PR/review/permission/workflow
objects from GitHub, then this pure builder normalizes and binds them to the migration plan.
"""
⋮----
def _canonical(v)
⋮----
def _login(review)
⋮----
value=review.get(key)
⋮----
login=value.get("login") or value.get("name")
⋮----
def _state(review)
⋮----
value=review.get("state") if isinstance(review,dict) else None
⋮----
def _commit(review)
⋮----
def _timestamp(value) -> float | None
⋮----
text=value[:-1]+"+00:00" if value.endswith("Z") else value
dt=datetime.fromisoformat(text)
⋮----
dt=dt.replace(tzinfo=timezone.utc)
⋮----
def _submitted_at(review)
⋮----
def _review_order_key(review) -> tuple[float,int]
⋮----
ts=_timestamp(_submitted_at(review))
review_id=review.get("id") if isinstance(review,dict) else None
try: rid=int(review_id or 0)
except (TypeError,ValueError): rid=0
⋮----
def latest_approvals(reviews: list[dict], commit_sha: str, *, head_commit_timestamp: float | None=None) -> list[dict]
⋮----
latest={}
⋮----
login=_login(review)
⋮----
current=latest.get(login)
⋮----
rows=[]
⋮----
review_commit=_commit(review)
⋮----
submitted_raw=_submitted_at(review); submitted_ts=_timestamp(submitted_raw)
⋮----
def _workflow_path(run: dict) -> str | None
⋮----
raw=run.get("path")
⋮----
def successful_workflow(runs: list[dict], commit_sha: str, *, required_run_id: int | None=None, required_workflow_name: str=REQUIRED_WORKFLOW_NAME, required_workflow_path: str=REQUIRED_WORKFLOW_PATH, head_commit_timestamp: float | None=None) -> dict
⋮----
candidates=[]
⋮----
created=_timestamp(run.get("run_started_at") or run.get("created_at") or run.get("updated_at"))
⋮----
run=sorted(candidates,key=lambda x:int(x.get("id") or 0),reverse=True)[0]
⋮----
semantic_digest=workflow_file.get("semantic_digest")
⋮----
approvals=latest_approvals(reviews,commit_sha,head_commit_timestamp=float(head_commit_timestamp))
eligible=[a for a in approvals if permissions.get(a["login"]) in {"admin","maintain","write"}]
⋮----
first=eligible[0]; first["permission"]=permissions[first["login"]]
second=None
⋮----
second=eligible[1]; second["permission"]=permissions[second["login"]]
checks=validate_check_runs(check_runs,repository,commit_sha=commit_sha,head_commit_timestamp=float(head_commit_timestamp))
⋮----
required_workflow_run_id=checks.get("common_workflow_run_id")
⋮----
workflow=successful_workflow(workflow_runs,commit_sha,required_run_id=required_workflow_run_id,head_commit_timestamp=float(head_commit_timestamp))
attestation={
````

## File: architecture_reputation_policy_github_collect.py
````python
"""Collect GitHub evidence and build a migration approval attestation.

This module performs read-only GitHub API calls. It never approves, merges, or mutates a PR.
"""
⋮----
class GitHubAttestationCollectionError(RuntimeError)
⋮----
def _valid_repository(value: str) -> bool
⋮----
def _collect_workflow_file(api: str, token: str, commit_sha: str) -> dict
⋮----
encoded_path=urllib.parse.quote(REQUIRED_WORKFLOW_PATH,safe="/")
value=_request(api+f"/contents/{encoded_path}?ref={urllib.parse.quote(commit_sha,safe='')}",token)
⋮----
content=value.get("content")
⋮----
raw=base64.b64decode(content,validate=False)
⋮----
text=raw.decode("utf-8")
⋮----
validation=validate_workflow_text(text)
⋮----
def collect_review_target(*, token: str, repository: str, pull_request: int) -> dict
⋮----
api="https://api.github.com/repos/"+repository
⋮----
pr=_request(api+f"/pulls/{pull_request}",token)
⋮----
head=pr.get("head") if isinstance(pr.get("head"),dict) else {}
base=pr.get("base") if isinstance(pr.get("base"),dict) else {}
user=pr.get("user") if isinstance(pr.get("user"),dict) else {}
commit_sha=head.get("sha")
⋮----
workflow_file=_collect_workflow_file(api,token,commit_sha) if isinstance(commit_sha,str) and commit_sha else None
⋮----
target={
⋮----
def collect(plan: dict, *, token: str, repository: str, pull_request: int) -> dict
⋮----
commit_sha=pr.get("head",{}).get("sha") if isinstance(pr.get("head"),dict) else None
⋮----
commit=_request(api+f"/commits/{commit_sha}",token)
commit_data=commit.get("commit") if isinstance(commit,dict) and isinstance(commit.get("commit"),dict) else {}
committer=commit_data.get("committer") if isinstance(commit_data.get("committer"),dict) else {}
author_commit=commit_data.get("author") if isinstance(commit_data.get("author"),dict) else {}
head_commit_time_raw=committer.get("date") or author_commit.get("date")
⋮----
head_commit_timestamp=_timestamp(head_commit_time_raw)
⋮----
reviews=_request(api+f"/pulls/{pull_request}/reviews?per_page=100",token)
⋮----
approvals=latest_approvals(reviews,commit_sha,head_commit_timestamp=head_commit_timestamp)
permissions={}
⋮----
login=row.get("login")
⋮----
value=_request(api+f"/collaborators/{urllib.parse.quote(login,safe='')}/permission",token)
permission=value.get("permission") if isinstance(value,dict) else None
⋮----
checks_response=_request(api+f"/commits/{commit_sha}/check-runs?per_page=100",token)
check_runs=(
⋮----
query=urllib.parse.urlencode({
runs_response=_request(api+"/actions/runs?"+query,token)
workflow_runs=(
⋮----
workflow_file=_collect_workflow_file(api,token,commit_sha)
⋮----
risk=plan.get("risk") if isinstance(plan,dict) and isinstance(plan.get("risk"),dict) else {}
reinforced=risk.get("reinforced_review_required") is True
⋮----
pr_identity={
````

## File: architecture_reputation_policy_migration_cli.py
````python
"""CLI for dry-run and explicitly authorized reputation policy migrations."""
⋮----
def _load(path: Path, label: str) -> dict
⋮----
value=json.loads(path.read_text(encoding="utf-8"))
⋮----
def main(argv=None) -> int
⋮----
parser=argparse.ArgumentParser()
sub=parser.add_subparsers(dest="command",required=True)
⋮----
review=sub.add_parser("review")
⋮----
bind_target=sub.add_parser("bind-target")
⋮----
apply_cmd=sub.add_parser("apply")
⋮----
args=parser.parse_args(argv)
⋮----
registry=_load(Path(args.registry),"registry")
learning=_load(Path(args.learning),"learning") if args.learning else None
result=dry_run(registry,learning)
out=Path(args.out)
⋮----
target=out/"architecture-reputation-policy-migration-review.json"
⋮----
plan=_load(Path(args.plan),"migration plan")
target=collect_review_target(
bound=bind_github_review_target(plan,target)
⋮----
registry_path=Path(args.registry)
registry=_load(registry_path,"registry")
⋮----
authorization=_load(Path(args.authorization),"authorization")
approval=_load(Path(args.approval),"approval provenance") if args.approval else None
ledger=_load(Path(args.ledger),"approval ledger") if args.ledger else None
⋮----
github_attestation=_load(Path(args.github_attestation),"GitHub attestation")
⋮----
repository=args.repository or os.environ.get("GITHUB_REPOSITORY","")
pull_request=args.pull_request
⋮----
github_attestation=collect_github_attestation(
migrated=apply_migration(
target=Path(args.out) if args.out else registry_path
````

## File: architecture_reputation_policy_migration_review.py
````python
"""Render a deterministic Markdown review for a reputation policy migration plan."""
⋮----
def render(plan: dict) -> str
⋮----
explanation=plan.get("explanation") if isinstance(plan.get("explanation"),dict) else {}
risk=plan.get("risk") if isinstance(plan.get("risk"),dict) else {}
impact=explanation.get("state_impact") if isinstance(explanation.get("state_impact"),dict) else {}
lines=[
policy_changes=explanation.get("policy_changes") if isinstance(explanation.get("policy_changes"),list) else []
⋮----
transitions=impact.get("transitions") if isinstance(impact.get("transitions"),list) else []
⋮----
auth=plan.get("authorization_template") if isinstance(plan.get("authorization_template"),dict) else {}
⋮----
def main(argv=None) -> int
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args(argv)
⋮----
plan=json.loads(Path(args.plan).read_text(encoding="utf-8"))
⋮----
text=render(plan)
````

## File: architecture_reputation_policy_migration.py
````python
"""Dry-run and explicitly authorized migration of persisted replacement reputation policy.

Policy migrations never silently promote a replacement. A dry-run computes the exact
registry diff under the current canonical reputation engine/policy. Applying the migration
requires an authorization record bound to the source-registry digest and migration plan.
"""
⋮----
MIGRATION_VERSION=3
AUTHORIZATION_VERSION=2
AUTHORIZATION_TTL_SECONDS=24*60*60
RISK_LEVELS=("NO_IMPACT","SAFE_STRICTER","BEHAVIOR_CHANGE","TRUST_DOWNGRADE","PROMOTION_PATH_CHANGE","CRITICAL")
_REINFORCED_RISKS={"PROMOTION_PATH_CHANGE","CRITICAL"}
⋮----
class ReputationPolicyMigrationError(RuntimeError)
⋮----
_CONTEXT_FIELDS=(
⋮----
def _canonical(value) -> str
⋮----
def registry_digest(registry: dict) -> str
⋮----
def _entry_context(entry: dict) -> dict
⋮----
def _learning_index(learning: dict | None) -> dict[tuple,dict]
⋮----
rows=learning.get("rankings") if isinstance(learning,dict) else None
out={}
⋮----
key=tuple(row.get(field) for field in _CONTEXT_FIELDS)
current=out.get(key)
⋮----
def _evidence_for(entry: dict, learning_index: dict[tuple,dict]) -> dict | None
⋮----
key=tuple(entry.get(field) for field in _CONTEXT_FIELDS)
row=learning_index.get(key)
⋮----
metrics=entry.get("metrics")
⋮----
def _migrated_state(previous: str, desired: str) -> tuple[str,str,bool]
⋮----
# Policy migration itself is never a source of upward trust.
⋮----
# Any non-trusted state must re-enter normal recovery flow later.
⋮----
def _rule_snapshot(rule: dict | None) -> dict
⋮----
def _policy_edges(policy: dict | None) -> dict[tuple[str,str],dict]
⋮----
def _is_stricter_or_equal(old: dict, new: dict) -> bool
⋮----
severity_rank={"info":0,"warning":1,"critical":2}
⋮----
def classify_migration_risk(registry: dict, changes: list[dict]) -> dict
⋮----
source_policy=registry.get("policy") if isinstance(registry.get("policy"),dict) else {}
source_matrix=source_policy.get("transition_matrix") if isinstance(source_policy.get("transition_matrix"),dict) else {}
old_edges=_policy_edges(source_matrix)
new_edges=_policy_edges(TRANSITION_POLICY)
all_edges=sorted(set(old_edges)|set(new_edges))
⋮----
changed_edges=[]
promotion_path_changes=[]
only_stricter=True
⋮----
old=old_edges.get(edge,_rule_snapshot(None))
new=new_edges.get(edge,_rule_snapshot(None))
⋮----
stricter=_is_stricter_or_equal(old,new)
only_stricter=only_stricter and stricter
row={
⋮----
changed_rows=[row for row in changes if isinstance(row,dict) and row.get("changed") is True]
trusted_downgrades=[
⋮----
source_validation=source_policy.get("validation") if isinstance(source_policy.get("validation"),dict) else None
source_known_invalid=isinstance(source_validation,dict) and source_validation.get("valid") is False
⋮----
level="CRITICAL"
reason="source_policy_was_invalid"
⋮----
level="PROMOTION_PATH_CHANGE"
reason="transition_path_to_or_from_recovery_changed"
⋮----
level="TRUST_DOWNGRADE"
reason="one_or_more_trusted_entries_downgrade"
⋮----
level="SAFE_STRICTER"
reason="policy_only_became_stricter_without_state_changes"
⋮----
level="BEHAVIOR_CHANGE"
reason="policy_or_reputation_behavior_changes"
⋮----
level="NO_IMPACT"
reason="no_effective_policy_or_state_change"
⋮----
def _format_seconds(value: int | float) -> str
⋮----
seconds=max(0,int(value or 0))
⋮----
def explain_migration(risk: dict, changes: list[dict]) -> dict
⋮----
edge_explanations=[]
⋮----
old=row.get("old") if isinstance(row.get("old"),dict) else {}
new=row.get("new") if isinstance(row.get("new"),dict) else {}
diffs=[]
⋮----
before=old.get(field); after=new.get(field)
⋮----
before=_format_seconds(before); after=_format_seconds(after)
⋮----
old_gates=set(old.get("required_gates",[])); new_gates=set(new.get("required_gates",[]))
⋮----
state_counts={}
affected=[]
⋮----
key=f"{row.get('previous_state')} -> {row.get('target_state')}"
⋮----
review_action=(
⋮----
def review_digest(plan: dict) -> str
⋮----
payload={
⋮----
def authorization_template(plan: dict, *, now: float | None=None) -> dict
⋮----
now=float(now) if isinstance(now,(int,float)) else time.time()
risk=plan.get("risk") if isinstance(plan.get("risk"),dict) else {}
⋮----
def dry_run(registry: dict, learning: dict | None=None, *, now: float | None=None) -> dict
⋮----
validation=validate_transition_policy()
⋮----
entries=registry.get("entries")
⋮----
source_digest=registry_digest(registry)
target_policy_digest=transition_policy_digest()
index=_learning_index(learning)
⋮----
changes=[]
unchanged=0
downgrades=0
preserved_nontrusted=0
trusted_revalidated=0
⋮----
previous=entry.get("state") if isinstance(entry.get("state"),str) else "UNOBSERVED"
evidence=_evidence_for(entry,index)
desired=desired_state(evidence)
⋮----
changed=(
⋮----
risk=classify_migration_risk(registry,changes)
explanation=explain_migration(risk,changes)
core={
migration_id=hashlib.sha256(_canonical(core).encode("utf-8")).hexdigest()
result={**core,"migration_id":migration_id}
⋮----
def bind_github_review_target(plan: dict, target: dict, *, now: float | None=None) -> dict
⋮----
required=(
⋮----
semantic_digest=target.get("workflow_semantic_digest")
⋮----
bound={
⋮----
# Re-bind the plan identity to the exact GitHub review target.
migration_id=hashlib.sha256(_canonical(bound).encode("utf-8")).hexdigest()
⋮----
def apply_migration(registry: dict, plan: dict, authorization: dict, *, approval: dict | None=None, github_attestation: dict | None=None, approval_ledger: dict | None=None, now: float | None=None) -> dict
⋮----
expected_review_digest=review_digest(plan)
⋮----
reinforced=risk.get("reinforced_review_required") is True
github_provenance=validate_github_attestation(
⋮----
approval=approval_from_github_attestation(
provenance=validate_approval(
⋮----
issued_at=authorization.get("issued_at")
expires_at=authorization.get("expires_at")
⋮----
next_approval_ledger=consume_approval(
⋮----
current_digest=registry_digest(registry)
⋮----
audit=registry.get("audit") if isinstance(registry.get("audit"),list) else []
⋮----
change_index={row.get("identity"):row for row in plan.get("changes",[]) if isinstance(row,dict)}
migrated_entries={}
migration_events=[]
⋮----
row=change_index.get(identity)
⋮----
target=row.get("target_state")
⋮----
rule=transition_policy(previous,target)
required_gates=list(rule.get("required_gates",[]))
target_gate=DANGEROUS_STATE_GATES.get(target)
⋮----
updated=dict(entry)
⋮----
migrated={
⋮----
def write_dry_run(registry: dict, learning: dict | None, out: Path, *, now: float | None=None) -> dict
⋮----
result=dry_run(registry,learning,now=now)
⋮----
def write_applied(registry: dict, plan: dict, authorization: dict, path: Path, *, approval: dict | None=None, github_attestation: dict | None=None, approval_ledger: dict | None=None, now: float | None=None) -> dict
⋮----
migrated=apply_migration(registry,plan,authorization,approval=approval,github_attestation=github_attestation,approval_ledger=approval_ledger,now=now)
````

## File: architecture_safe_rewrite.py
````python
"""Build bounded retry context after an architecture-sensitive patch is rejected."""
⋮----
MAX_REJECTED_FILES = 12
MAX_CONTENT_PREVIEW = 800
⋮----
def _patch_summary(patch: object) -> list[dict]
⋮----
files = patch.get("files")
⋮----
result = []
⋮----
path = item.get("path")
content = item.get("content")
⋮----
payload = {
````

## File: artifact_cas_audit.py
````python
"""Append-only local audit log for explicit CAS promotions."""
⋮----
MAX_RECORDS = 512
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_ARTIFACT_CAS_AUDIT_PATH", "")
⋮----
def load() -> list[dict]
⋮----
path = _path()
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
def record(*, project_id: str, artifact_class: str, digest: str, size: int) -> dict
⋮----
rows = load()
row = {
⋮----
rows = rows[-MAX_RECORDS:]
````

## File: artifact_cas_namespace.py
````python
"""Project-scoped CAS namespaces for safe cross-project storage."""
⋮----
_SAFE = re.compile(r"^[a-z0-9._-]{1,120}$")
⋮----
def project_namespace(project_id: str) -> str
⋮----
normalized = project_id.strip().lower().replace("/", "--")
⋮----
def scoped_digest(project_id: str, content_digest: str) -> str
⋮----
namespace = project_namespace(project_id)
````

## File: artifact_cas_promotion.py
````python
"""Explicit promotion from project-private CAS to approved shared CAS."""
⋮----
ATTESTATION = "explicitly-public-generated-artifact-v1"
⋮----
data = cas_get(digest, size, shareable=False)
artifact_class = validate_shareable_payload(data, artifact_class)
shared = cas_put(
⋮----
project_id = os.environ.get("STUDIO_PROJECT_ID", "local-project")
audit = record_promotion(
````

## File: artifact_cas_stats.py
````python
"""Usage statistics and retention scoring for artifact CAS blobs."""
⋮----
SCHEMA = 1
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_ARTIFACT_CAS_STATS_PATH", "")
⋮----
def load() -> dict
⋮----
path = _path()
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
def save(data: dict) -> None
⋮----
data = load()
⋮----
blobs = data.setdefault("blobs", {})
row = blobs.setdefault(digest, {
⋮----
def retention_score(digest: str) -> float
⋮----
row = data.get("blobs", {}).get(digest)
⋮----
hits = max(0, int(row.get("hits", 0)))
cost = max(0.0, float(row.get("rebuild_cost_seconds", 0.0)))
size = max(1, int(row.get("size", 1)))
clock = max(1, int(data.get("clock", 1)))
last_used = max(0, int(row.get("last_used", 0)))
recency = max(0.0, 1.0 - ((clock - last_used) / max(1.0, float(clock))))
value = (hits * 12.0) + (cost * 2.0) + (recency * 8.0)
⋮----
def forget(digests: set[str]) -> None
⋮----
blobs = data.get("blobs", {})
⋮----
def summary() -> dict
⋮----
total_hits = 0
total_bytes = 0
protected_cost = 0.0
scores = []
````

## File: artifact_cas.py
````python
"""Local content-addressable store with strict project isolation."""
⋮----
MAX_CAS_BYTES = 64 * 1024 * 1024
⋮----
def _root() -> Path | None
⋮----
raw = os.environ.get("STUDIO_ARTIFACT_CAS_PATH", "")
⋮----
def _project_id() -> str
⋮----
raw = os.environ.get("STUDIO_PROJECT_ID", "")
⋮----
def _scope_root(*, shareable: bool = False, artifact_class: str | None = None) -> Path
⋮----
root = _root()
⋮----
shared_raw = os.environ.get("STUDIO_SHARED_ARTIFACT_CAS_PATH", "")
shared_root = Path(shared_raw) if shared_raw else root / "shared"
⋮----
def sha256(data: bytes) -> str
⋮----
def stats_digest(digest: str, *, shareable: bool = False, artifact_class: str | None = None) -> str
⋮----
artifact_class = validate_shareable_class(artifact_class)
⋮----
def blob_path(digest: str, *, shareable: bool = False, artifact_class: str | None = None) -> Path
⋮----
root = _scope_root(shareable=shareable, artifact_class=artifact_class)
⋮----
data = bytes(data)
⋮----
artifact_class = validate_shareable_payload(data, artifact_class)
digest = sha256(data)
path = blob_path(digest, shareable=shareable, artifact_class=artifact_class)
⋮----
existing = path.read_bytes()
⋮----
tmp = path.with_suffix(".tmp")
⋮----
def get(digest: str, expected_size: int, *, shareable: bool = False, artifact_class: str | None = None) -> bytes
⋮----
data = path.read_bytes()
⋮----
def usage(*, shareable: bool = False, artifact_class: str | None = None) -> int
⋮----
total = 0
⋮----
def gc(referenced: set[str], *, shareable: bool = False, artifact_class: str | None = None) -> dict
⋮----
removed = 0
bytes_removed = 0
removed_digests = set()
⋮----
rel = path.relative_to(root)
digest = rel.parts[0] + "".join(rel.parts[1:])
⋮----
size = path.stat().st_size
⋮----
after = usage(shareable=shareable, artifact_class=artifact_class)
````

## File: artifact_handoff.py
````python
"""Trusted selection of prior autonomous-run artifacts for release handoff."""
⋮----
PROJECT_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
⋮----
class ArtifactHandoffError(ValueError)
⋮----
def select_latest_project_artifact(payload: dict, project_id: str) -> dict | None
⋮----
prefix = "mobile-" + project_id + "-"
candidates = []
⋮----
name = item.get("name")
expired = item.get("expired")
workflow_run = item.get("workflow_run")
created_at = item.get("created_at")
artifact_id = item.get("id")
⋮----
suffix = name[len(prefix):]
⋮----
latest = candidates[0]
````

## File: artifact_share_policy.py
````python
"""Deny-by-default policy for cross-project CAS sharing."""
⋮----
_ALLOWED = {
_SAFE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
⋮----
def validate_shareable_class(artifact_class: str | None) -> str
⋮----
def approved_classes() -> tuple[str, ...]
⋮----
_MAX_SHAREABLE_BYTES = 2 * 1024 * 1024
_FORBIDDEN_MARKERS = (
⋮----
def validate_shareable_payload(data: bytes, artifact_class: str | None) -> str
⋮----
artifact_class = validate_shareable_class(artifact_class)
⋮----
data = bytes(data)
⋮----
text = data.decode("utf-8")
````

## File: artwork_candidate_bridge.py
````python
"""Bridge a trusted merged artwork provider into the generic candidate validator."""
⋮----
class ArtworkCandidateBridgeError(ValueError)
⋮----
def _canon(value)
⋮----
def build_artwork_candidate(provider_path: Path, tests_path: Path)
⋮----
provider_path = Path(provider_path)
tests_path = Path(tests_path)
⋮----
implementation = provider_path.read_text(encoding="utf-8")
tests = tests_path.read_text(encoding="utf-8")
⋮----
proof_bundle = validate_artwork_provider(provider_path)
⋮----
source_sha = hashlib.sha256(implementation.encode("utf-8")).hexdigest()
⋮----
payload = {
digest = hashlib.sha256(_canon(payload)).hexdigest()
envelope = {
⋮----
def bind(proof)
⋮----
value = dict(proof)
⋮----
validation = validate_candidate(
````

## File: artwork_capability.py
````python
"""Provider-neutral artwork capability contract with deterministic fallback."""
⋮----
ARTWORK_CAPABILITY="store.artwork.generate"
⋮----
REQUIREMENTS={
⋮----
class ArtworkError(ValueError)
⋮----
SHA40_RE=re.compile(r"[0-9a-f]{40}")
SHA256_RE=re.compile(r"[0-9a-f]{64}")
ALLOWED_LICENSE_STATUS={"generated_original","project_owned","permissive_verified"}
⋮----
def _provider_provenance(selection: dict) -> dict
⋮----
mode=selection.get("mode")
provider=selection.get("provider")
evidence=selection.get("evidence")
⋮----
explicit=evidence.get("provenance") if isinstance(evidence,dict) else None
⋮----
required={"origin","external_sources","license_status","provider_identity"}
⋮----
origin=explicit.get("origin")
external=explicit.get("external_sources")
license_status=explicit.get("license_status")
identity=explicit.get("provider_identity")
⋮----
def select_provider(registry)
⋮----
item=registry["capabilities"][ARTWORK_CAPABILITY]
⋮----
def validate_asset(path,kind)
⋮----
path=Path(path)
⋮----
req=REQUIREMENTS[kind]
⋮----
raw=path.read_bytes()
⋮----
def builtin_visual_qa(icon_path,feature_path)
⋮----
metrics={}
⋮----
sample_step=max(4,(len(pixels)//4//4096)*4)
colors=set()
luminance=[]
⋮----
rgb=(pixels[i],pixels[i+1],pixels[i+2])
⋮----
def validate_artwork_set(icon_path,feature_path,*,provider_selection,visual_qa)
⋮----
provenance=_provider_provenance(provider_selection)
icon=validate_asset(icon_path,"icon")
feature=validate_asset(feature_path,"feature_graphic")
````

## File: artwork_stage.py
````python
"""Validate generated Play Store artwork before privacy/security completion."""
⋮----
def _registry(out: Path)
⋮----
path=out/'.autonomy/capabilities.json'
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req=json.loads(request_path.read_text())
report_path=out/'report.json'
⋮----
state=json.loads(report_path.read_text())
⋮----
icon=out/'play-store/icon-512.png'
feature=out/'play-store/feature-graphic-1024x500.png'
⋮----
provider=select_provider(_registry(out))
visual=builtin_visual_qa(icon,feature)
evidence=validate_artwork_set(
⋮----
evidence={'passed':False,'blockers':[str(exc)]}
⋮----
parent=state.get('checkpoint_commit')
⋮----
github=GitHub(req['target_repo'])
sha=github.publish('studio/'+req['id'],parent,root,state)
⋮----
def main() -> int
⋮----
parser=argparse.ArgumentParser()
⋮----
args=parser.parse_args()
state=advance(Path(args.request),Path(args.work),Path(args.out))
evidence=state.get('release_evidence',{}).get('artwork_qa')
````

## File: artwork_validation.py
````python
"""Deterministic proof bundle for the asset_artwork capability."""
⋮----
class ArtworkValidationError(ValueError)
⋮----
def _canon(value)
⋮----
def _seal(value)
⋮----
def validate_artwork_provider(provider_path: Path)
⋮----
provider_path = Path(provider_path)
⋮----
source = provider_path.read_bytes()
⋮----
source_sha256 = hashlib.sha256(source).hexdigest()
⋮----
scenarios = [
⋮----
outputs=[]
⋮----
first=run(context)
second=run(context)
⋮----
assets=first.get("assets")
⋮----
content=asset.get("content")
digest=asset.get("sha256")
⋮----
targeted = {
⋮----
benchmark_score=sum(item["asset_count"] for item in outputs)
benchmark = {
⋮----
regression = {
````

## File: atomic_file.py
````python
"""Crash-safe atomic persistence for small local state files."""
⋮----
def write_bytes(path: Path, data: bytes) -> None
⋮----
"""Atomically replace *path* with *data* using a same-directory temp file."""
path = Path(path)
⋮----
tmp = Path(raw_tmp)
⋮----
# Persist the directory entry where supported. Some filesystems/platforms
# reject directory fsync; the file replacement itself has already
# completed safely in that case.
⋮----
dir_fd = os.open(path.parent, os.O_RDONLY)
⋮----
def write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None
````

## File: autonomous_project.py
````python
"""Persistent fail-closed wrapper around the multi-engine project orchestrator."""
⋮----
AUTONOMY_DIR = ".autonomy"
⋮----
def _state_paths(project_out: Path)
⋮----
root = Path(project_out) / AUTONOMY_DIR
⋮----
def _clear_human_input_request(project_out: Path) -> None
⋮----
def ensure_project_goal(project_out: Path, goal_id: str, objective: str, *, max_attempts: int = 20)
⋮----
current_registry = load_registry(registry_path)
promoted_registry = sync_into_registry(current_registry)
⋮----
def _sync_promoted_capabilities(registry_path: Path, repo_root: Path = Path("."))
⋮----
path = repo_root / "control" / "promoted_stages.json"
⋮----
value = json.loads(path.read_text())
⋮----
stages = value.get("stages") if isinstance(value, dict) else None
⋮----
registry = load_registry(registry_path)
changed = False
⋮----
script = item.get("script")
candidate_id = item.get("candidate_id")
candidate_sha = item.get("candidate_sha")
⋮----
registry = register(registry, name, script, {
changed = True
⋮----
def translate_orchestrator_result(result: dict) -> dict
⋮----
status = result.get("status")
report = result.get("report")
next_stage = result.get("next_stage")
⋮----
completion = report.get("completion") if isinstance(report, dict) else None
⋮----
action = next_stage if isinstance(next_stage, str) and next_stage else "external_human_action"
⋮----
detail = next_stage if isinstance(next_stage, str) and next_stage else "unknown_capability"
phase = result.get("pending_status") or result.get("promotion_status") or result.get("research_status") or "in_progress"
⋮----
details = [status]
⋮----
blockers = report.get("blockers")
⋮----
detail = ":".join(details)
⋮----
project_out = Path(project_out)
⋮----
autonomy_root = project_out / AUTONOMY_DIR
⋮----
runtime_state_path = autonomy_root / "runtime-state.json"
⋮----
runtime_paths = {
⋮----
goal_state = load_goal(goal_path)
⋮----
detail = str(goal_state.get("human_action") or "external_human_action_required")
⋮----
goal_state = resume_human_action(goal_state)
⋮----
context_path = project_out / AUTONOMY_DIR / "learned-context.json"
provider_health_path = project_out / AUTONOMY_DIR / "provider-health.json"
provider_metrics_path = project_out / AUTONOMY_DIR / "provider-metrics.json"
routing_history_path = project_out / AUTONOMY_DIR / "routing-history.json"
⋮----
def context_provider(_goal_state)
⋮----
memory = load_memory(memory_path)
items = context_for_goal(memory, goal_id)
portfolio_path=project_out/"portfolio-research.json"
⋮----
portfolio=json.loads(portfolio_path.read_text())
⋮----
portfolio={}
⋮----
profile=candidate.get("deep_profile") if isinstance(candidate.get("deep_profile"),dict) else {}
summary="Similar owned repository: "+candidate["repo"]
description=candidate.get("description")
⋮----
markers=profile.get("markers") if isinstance(profile.get("markers"),list) else []
⋮----
excerpt=profile.get("readme_excerpt")
⋮----
items=items[:20]
⋮----
def execute_cycle(_goal_state)
⋮----
previous = os.environ.get("STUDIO_LEARNED_CONTEXT_PATH")
previous_health = os.environ.get("STUDIO_PROVIDER_HEALTH_PATH")
previous_metrics = os.environ.get("STUDIO_PROVIDER_METRICS_PATH")
previous_history = os.environ.get("STUDIO_ROUTING_HISTORY_PATH")
⋮----
result = run_once(
⋮----
translated = translate_orchestrator_result(result)
report = result.get("report") if isinstance(result, dict) else None
⋮----
def cycle_observer(goal_state, result)
⋮----
learned = learn_from_cycle(memory, goal_id, goal_state, result, str(baseline_sha))
⋮----
def execute_registered_capability(registry, capability, goal_state)
⋮----
previous_runtime = {name: os.environ.get(name) for name in runtime_paths}
previous_project_id = os.environ.get("STUDIO_PROJECT_ID")
⋮----
result = run_goal(
````

## File: autonomous_research.py
````python
"""Bounded autonomous research with explicit source provenance."""
⋮----
MAX_QUERIES = 6
MAX_RESULTS_PER_QUERY = 8
MAX_CONTENT_BYTES = 200_000
SHA_RE = re.compile(r"[0-9a-f]{64}")
⋮----
class ResearchError(ValueError)
⋮----
def _clean_url(value)
⋮----
parsed = urlsplit(value.strip())
⋮----
def _queries(objective)
⋮----
base = " ".join(objective.split())
candidates = [
out = []
⋮----
def _content_bytes(value)
⋮----
raw = value.encode("utf-8")
⋮----
raw = value
⋮----
def run_research(candidate_id, objective, search_provider, fetch_provider, *, min_sources=2)
⋮----
selected = {}
⋮----
results = search_provider(query)
⋮----
results = results[:MAX_RESULTS_PER_QUERY]
⋮----
url = _clean_url(result.get("url"))
title = result.get("title")
kind = result.get("kind", "web")
⋮----
items = []
⋮----
meta = selected[url]
raw = _content_bytes(fetch_provider(url))
digest = hashlib.sha256(raw).hexdigest()
⋮----
text = raw.decode("utf-8")
notes = " ".join(text.split())
⋮----
def run_and_remember(memory, project_id, candidate_id, objective, search_provider, fetch_provider, *, min_sources=2)
⋮----
research = run_research(
````

## File: billing_qa.py
````python
"""Trusted Play Billing QA contract.

This stage never fabricates a successful purchase. It validates the generated app's
billing integration and accepts an external Play Billing sandbox result only when
that evidence matches the exact package and release APK hash.
"""
⋮----
BILLING_DEPENDENCIES = {'in_app_purchase', 'purchases_flutter'}
BILLING_MARKERS = ('InAppPurchase', 'PurchaseDetails', 'ProductDetails', 'Purchases.')
REQUIRED_OUTCOMES = ('product_query', 'purchase_success', 'purchase_cancel', 'purchase_restore')
⋮----
def _pubspec_dependencies(root: Path) -> set[str]
⋮----
path = root / 'pubspec.yaml'
⋮----
deps: set[str] = set()
in_deps = False
⋮----
line = raw.rstrip()
⋮----
in_deps = line.strip() == 'dependencies:'
⋮----
match = re.match(r'^\s{2}([A-Za-z0-9_]+):', line)
⋮----
def _source_markers(root: Path) -> list[str]
⋮----
found: set[str] = set()
lib = root / 'lib'
⋮----
text = path.read_text(errors='replace')
⋮----
def _apk_hash(root: Path) -> str | None
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
def validate_sandbox_evidence(value: object, package: str, apk_sha256: str) -> dict
⋮----
allowed = {'schema', 'provider', 'package', 'apk_sha256', 'tester_mode', 'outcomes'}
⋮----
outcomes = value.get('outcomes')
⋮----
entry = outcomes[name]
⋮----
def validate_billing(root: Path, out: Path) -> dict
⋮----
package = package_name(root)
apk_sha256 = _apk_hash(root)
dependencies = sorted(_pubspec_dependencies(root) & BILLING_DEPENDENCIES)
markers = _source_markers(root)
blockers: list[str] = []
⋮----
sandbox_path = out / 'billing-sandbox-evidence.json'
sandbox = None
⋮----
sandbox = validate_sandbox_evidence(json.loads(sandbox_path.read_text()), package, apk_sha256)
⋮----
evidence = {
````

## File: billing_stage.py
````python
"""Persist trusted Play Billing QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = evaluate_and_repair(root, out, state, req, 'billing_qa', validate_billing)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('billing_qa')
````

## File: candidate_portfolio_learning.py
````python
"""Learn verified efficiency of speculative candidate portfolio widths."""
⋮----
ALPHA = 0.25
MIN_SAMPLES = 4
MAX_WIDTH = 3
⋮----
def _key(width: int) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
key = _key(width)
row = data.get(key, {
samples = int(row.get("samples", 0) or 0)
observed = 1.0 if success else 0.0
cost = max(0.0, float(cost_seconds or 0.0))
previous_success = float(row.get("ema_success", 0.0) or 0.0)
previous_cost = float(row.get("ema_cost_seconds", 0.0) or 0.0)
row = {
⋮----
def recommendation(data: dict) -> dict
⋮----
rows = []
⋮----
row = data.get(_key(width)) if isinstance(data, dict) else None
⋮----
success = max(0.0, min(1.0, float(row.get("ema_success", 0.0) or 0.0)))
cost = max(1.0, float(row.get("ema_cost_seconds", 0.0) or 0.0))
# Reward verified success first; cost only breaks close outcomes.
utility = success * 100.0 - min(30.0, cost / 30.0)
````

## File: capability_adaptation_state.py
````python
"""Integrity-sealed persistent state for generic capability adaptation."""
⋮----
VERSION=1
STATUSES={"research_required","research_complete","synthesis_required","validation_required","promotion_required","awaiting_merge","awaiting_registry_merge","complete","blocked"}
CAP_RE=re.compile(r"[a-z][a-z0-9_.-]{2,120}")
⋮----
class CapabilityAdaptationStateError(ValueError)
⋮----
def _canon(value)
⋮----
def _seal(value)
⋮----
out=dict(value)
⋮----
def new_state(project_id,capability,source_candidate_id)
⋮----
def validate(value)
⋮----
required={
⋮----
digest=value.get("state_sha256")
unsigned=dict(value); unsigned.pop("state_sha256",None)
⋮----
def record_research(value, research_status)
⋮----
status="synthesis_required"
synthesis_status="required"
⋮----
status="research_required"
synthesis_status="not_started"
⋮----
def record_synthesis(value, candidate_sha256)
⋮----
def record_candidate_persistence(value, persistence_status)
⋮----
def record_registry_promotion_persistence(value, persistence_status)
⋮----
def record_validation(value, validation_status)
⋮----
status="promotion_required"
promotion_status="eligible"
⋮----
status="blocked"
promotion_status="not_ready"
````

## File: capability_candidate_validator.py
````python
"""Fail-closed validation for synthesized capability candidates."""
⋮----
SHA_RE = re.compile(r"[0-9a-f]{64}")
⋮----
class CapabilityValidationError(ValueError)
⋮----
def _canon(value)
⋮----
def _validate_candidate(envelope)
⋮----
required = {
⋮----
candidate = envelope.get("candidate")
⋮----
digest = envelope.get("candidate_sha256")
⋮----
def validate_candidate(candidate_envelope, targeted_test, benchmark, regression)
⋮----
benchmark_score = benchmark.get("score")
baseline_score = benchmark.get("baseline_score")
⋮----
evidence = {
````

## File: capability_memory.py
````python
"""Reuse validated cross-project experience as non-authoritative capability hints."""
⋮----
def capability_hints(memory, target_project_id, capability)
⋮----
items=reusable_for_project(memory,target_project_id,tags=["capability",capability])
hints=[]
⋮----
evidence=item.get("evidence")
provenance=item.get("provenance")
⋮----
commit=evidence.get("commit_sha")
⋮----
def attach_capability_hints(adaptation_request,memory,target_project_id)
⋮----
result=dict(adaptation_request)
gaps=result.get("gaps")
⋮----
attached={}
⋮----
capability=gap.get("value")
⋮----
hints=capability_hints(memory,target_project_id,capability)
````

## File: capability_promotion.py
````python
"""Controlled promotion of fully validated capability candidates."""
⋮----
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
DIGEST_RE = re.compile(r"[0-9a-f]{64}")
⋮----
class CapabilityPromotionError(ValueError)
⋮----
def _validate_registry_doc(value)
⋮----
def promote_candidate(registry_doc, candidate_envelope, validation, baseline_sha, candidate_commit_sha)
⋮----
candidate_id = candidate_envelope.get("candidate_id")
candidate_sha256 = candidate_envelope.get("candidate_sha256")
payload = candidate_envelope.get("candidate")
⋮----
capability = payload.get("capability")
provider = payload.get("provider")
⋮----
evidence = validation.get("evidence")
required_evidence = {"targeted_test_sha256", "benchmark_sha256", "regression_sha256"}
⋮----
existing = registry_doc["capabilities"].get(capability)
entry = {
⋮----
updated = copy.deepcopy(registry_doc)
````

## File: capability_qa.py
````python
"""Classify generated app capabilities and derive mandatory QA profiles."""
⋮----
PERMISSION_PROFILES = {
DEPENDENCY_PROFILES = {
SOURCE_PROFILES = {
PROFILE_STAGE = {
⋮----
def _manifest_permissions(root: Path) -> list[str]
⋮----
path = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
text = path.read_text(errors='replace')
⋮----
def _dependencies(root: Path) -> list[str]
⋮----
path = root / 'pubspec.yaml'
⋮----
names = []
in_deps = False
⋮----
in_deps = True
⋮----
match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', raw)
⋮----
def _source_text(root: Path) -> str
⋮----
chunks = []
lib = root / 'lib'
⋮----
def classify(root: Path) -> dict
⋮----
permissions = _manifest_permissions(root)
dependencies = _dependencies(root)
source = _source_text(root)
profiles = {'standard'}
reasons = []
⋮----
profile = PERMISSION_PROFILES.get(permission)
⋮----
profile = DEPENDENCY_PROFILES.get(dependency)
⋮----
ordered = ['standard'] + sorted(p for p in profiles if p != 'standard')
required_stages = [PROFILE_STAGE[p] for p in ordered if p in PROFILE_STAGE]
````

## File: capability_registry_promotion_persist.py
````python
"""Prepare a registry-only PR after a validated capability candidate was human-merged."""
⋮----
SHA40=re.compile(r"[0-9a-f]{40}")
SHA64=re.compile(r"[0-9a-f]{64}")
REGISTRY_PATH="control/promoted_capabilities.json"
⋮----
class CapabilityRegistryPromotionPersistError(RuntimeError)
⋮----
def _prefix(capability,candidate_id)
⋮----
ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
slug=re.sub(r"[^a-z0-9]+","-",capability).strip("-")
⋮----
def _repo_owner(github)
⋮----
parts=github.repo.strip("/").split("/")
⋮----
def _refs(github,prefix)
⋮----
refs=github.get("/git/matching-refs/heads/"+prefix)
⋮----
want="refs/heads/"+prefix
⋮----
def _existing_pr(github,branch,commit_sha)
⋮----
query=urllib.parse.urlencode({
pulls=github.get("/pulls?"+query)
⋮----
matches=[p for p in pulls if isinstance(p,dict)
⋮----
def _load_registry(github,main_sha)
⋮----
commit=github.get("/git/commits/"+main_sha)
tree_sha=commit.get("tree",{}).get("sha") if isinstance(commit,dict) else None
⋮----
tree=github.get("/git/trees/"+tree_sha+"?recursive=1")
items=tree.get("tree") if isinstance(tree,dict) else None
⋮----
entry=next((x for x in items if isinstance(x,dict) and x.get("path")==REGISTRY_PATH and x.get("type")=="blob"),None)
⋮----
blob=github.get("/git/blobs/"+entry.get("sha"))
⋮----
registry=json.loads(base64.b64decode(blob["content"]).decode("utf-8"))
⋮----
def _verify_materialized_provider(github,main_sha,candidate)
⋮----
payload=candidate.get("candidate",{})
capability=payload.get("capability")
provider=payload.get("provider")
module=provider.removeprefix("studio.capabilities.") if isinstance(provider,str) else ""
⋮----
path="studio/capabilities/"+module+".py"
⋮----
entry=next((x for x in items if isinstance(x,dict) and x.get("path")==path and x.get("type")=="blob"),None)
⋮----
blob=github.get("/git/blobs/"+str(entry.get("sha")))
⋮----
materialized=base64.b64decode(blob["content"]).decode("utf-8")
⋮----
def persist(github,candidate_envelope,validation_report,review,review_status,main_sha)
⋮----
candidate=validate_candidate_envelope(candidate_envelope)
report=validate_isolated_validation_result(validation_report)
⋮----
merge_sha=review_status.get("merge_commit_sha")
⋮----
candidate_commit=review.get("commit_sha")
⋮----
commit=github.get("/git/commits/"+candidate_commit)
parents=[x.get("sha") for x in commit.get("parents",[])] if isinstance(commit,dict) else []
⋮----
baseline_sha=parents[0]
⋮----
cid=candidate.get("candidate_id")
⋮----
digest=candidate.get("candidate_sha256")
⋮----
decision=report.get("validation",{})
⋮----
tree=github.call("POST",github.repo+"/git/trees",{
tree_sha=tree.get("sha") if isinstance(tree,dict) else None
⋮----
prefix=_prefix(capability,cid)
refs=_refs(github,prefix)
⋮----
branch=refs[0]["ref"][len("refs/heads/"):]
head=refs[0].get("object",{}).get("sha")
encoded=branch[len(prefix):]
⋮----
commit=github.get("/git/commits/"+head)
⋮----
number=_existing_pr(github,branch,head)
⋮----
commit=github.call("POST",github.repo+"/git/commits",{
commit_sha=commit.get("sha") if isinstance(commit,dict) else None
⋮----
branch=prefix+commit_sha
⋮----
pr=github.call("POST",github.repo+"/pulls",{
number=pr.get("number") if isinstance(pr,dict) else None
````

## File: capability_registry_review.py
````python
"""Verify the exact registry-only promotion PR while activation remains blocked."""
⋮----
SHA40 = re.compile(r"[0-9a-f]{40}")
⋮----
class CapabilityRegistryReviewError(RuntimeError)
⋮----
def inspect(github, review: dict) -> dict
⋮----
required = {
⋮----
branch = review.get("branch")
commit_sha = review.get("commit_sha")
number = review.get("pull_request")
⋮----
pr = github.get("/pulls/" + str(number))
⋮----
head = pr.get("head", {})
⋮----
merged = pr.get("merged") is True or pr.get("merged_at") is not None
state = pr.get("state")
⋮----
merge_sha = pr.get("merge_commit_sha")
````

## File: capability_registry.py
````python
"""Persistent capability registry for studio adapters."""
⋮----
VERSION=1
class CapabilityRegistryError(ValueError): pass
⋮----
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _seal(v)
⋮----
x=dict(v); x.pop("registry_sha256",None)
⋮----
def new_registry()
⋮----
def validate(registry)
⋮----
digest=registry.get("registry_sha256")
unsigned=dict(registry); unsigned.pop("registry_sha256",None)
⋮----
def register(registry,name,provider,evidence)
⋮----
x={"version":VERSION,"capabilities":dict(registry["capabilities"])}
⋮----
def has_capability(registry,name)
⋮----
def save(path,registry)
⋮----
validate(registry); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
⋮----
def load(path)
⋮----
try: value=json.loads(Path(path).read_text(encoding="utf-8"))
````

## File: capability_review.py
````python
"""Verify the exact persisted candidate PR while adaptation waits for review."""
⋮----
SHA40=re.compile(r"[0-9a-f]{40}")
⋮----
class CapabilityReviewError(RuntimeError): pass
⋮----
def inspect(github,review)
⋮----
required={"status","candidate_id","candidate_sha256","capability","branch","commit_sha","pull_request"}
⋮----
branch=review.get("branch"); commit_sha=review.get("commit_sha"); number=review.get("pull_request")
⋮----
pr=github.get("/pulls/"+str(number))
⋮----
head=pr.get("head",{})
⋮----
merged=pr.get("merged") is True or pr.get("merged_at") is not None
state=pr.get("state")
⋮----
merge_sha=pr.get("merge_commit_sha")
````

## File: capability_runtime.py
````python
"""Strict runtime for promoted studio capabilities."""
⋮----
PROVIDER_RE = re.compile(r"studio\.capabilities\.[a-z][a-z0-9_]{2,120}")
MAX_CONTEXT_BYTES = 128_000
MAX_RESULT_BYTES = 128_000
MAX_TIMEOUT_SECONDS = 30
⋮----
class CapabilityRuntimeError(RuntimeError)
⋮----
def _provider_path(provider: str, repo_root: Path) -> Path
⋮----
module = provider.removeprefix("studio.capabilities.")
path = (Path(repo_root) / "studio" / "capabilities" / (module + ".py"))
⋮----
resolved = path.resolve()
allowed_root = (Path(repo_root) / "studio" / "capabilities").resolve()
⋮----
def _bounded_json(value, limit, label)
⋮----
raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
⋮----
def _load_provider(provider: str, repo_root: Path)
⋮----
path = _provider_path(provider, repo_root)
spec = importlib.util.spec_from_file_location(provider, path)
⋮----
module = importlib.util.module_from_spec(spec)
⋮----
run = getattr(module, "run", None)
⋮----
def execute_capability(registry, capability, context, *, repo_root=Path("."), timeout_seconds=10)
⋮----
provider = registry["capabilities"][capability].get("provider")
run = _load_provider(provider, Path(repo_root))
⋮----
result_box = {}
⋮----
def invoke()
⋮----
thread = threading.Thread(target=invoke, daemon=True)
````

## File: capability_stage.py
````python
"""Persist capability classification and required QA stages."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = classify(root)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('capability_qa')
````

## File: capability_synthesis.py
````python
"""Synthesize isolated capability candidates from sealed research evidence."""
⋮----
NAME_RE = re.compile(r"[a-z][a-z0-9_.-]{2,80}")
PROVIDER_RE = re.compile(r"studio\.capabilities\.[a-z][a-z0-9_]{2,120}")
⋮----
class CapabilitySynthesisError(ValueError)
⋮----
def _canon(value)
⋮----
def _research_for(memory, project_id, capability)
⋮----
candidate_id = "capability:" + capability
items = query(memory, project_id=project_id, kind="research")
matched = []
⋮----
evidence = item.get("evidence")
⋮----
def synthesize_candidate(memory, project_id, capability, synthesizer)
⋮----
research = _research_for(memory, project_id, capability)
research_refs = [{
⋮----
proposal = synthesizer({
⋮----
allowed = {"provider", "implementation", "tests", "risk_notes"}
⋮----
provider = proposal.get("provider")
implementation = proposal.get("implementation")
tests = proposal.get("tests")
risk_notes = proposal.get("risk_notes")
⋮----
payload = {
digest = hashlib.sha256(_canon(payload)).hexdigest()
⋮----
def validate_candidate_envelope(envelope)
⋮----
required={
⋮----
candidate=envelope.get("candidate")
digest=envelope.get("candidate_sha256")
⋮----
capability=candidate.get("capability")
⋮----
expected_id="capability-candidate:"+capability+":"+digest[:16]
````

## File: capacity_budget.py
````python
"""Scale autonomous model-call budget from available free capacity."""
⋮----
ABSOLUTE_AUTO_CALL_CAP = 240
UNMETERED_MULTIPLIER = 4.0
POOLED_HIGH_MULTIPLIER = 3.0
POOLED_MEDIUM_MULTIPLIER = 2.0
⋮----
def multiplier(capacity_status: dict) -> float
⋮----
providers = capacity_status.get("providers")
⋮----
best_ratio = 0.0
⋮----
quota = row.get("monthly_quota")
⋮----
ratio = float(quota.get("remaining_ratio", 0.0) or 0.0)
⋮----
best_ratio = max(best_ratio, max(0.0, min(1.0, ratio)))
⋮----
base = max(1, int(base_limit))
⋮----
factor = multiplier(capacity_status)
effective = min(ABSOLUTE_AUTO_CALL_CAP, max(base, int(round(base * factor))))
⋮----
reason = "unmetered_capacity"
⋮----
reason = "pooled_free_capacity"
⋮----
reason = "standard_capacity"
````

## File: capacity_efficiency.py
````python
"""Verified progress-per-token memory for projects, providers, and models."""
⋮----
SCHEMA = 1
MAX_ROWS = 512
ALPHA = 0.25
⋮----
def _empty() -> dict
⋮----
def _load_unlocked(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
rows = value.get("rows")
⋮----
def load(path: Path) -> dict
⋮----
def _key(project_id: str, provider: str, model: str) -> str
⋮----
project = str(project_id).strip()
provider_name = str(provider).strip()
model_name = str(model).strip()
⋮----
consumed = max(1, int(tokens))
path = Path(path)
⋮----
data = _load_unlocked(path)
key = _key(project, provider_name, model_name)
row = data["rows"].get(key, {
samples = max(0, int(row.get("samples", 0) or 0))
prev_tokens = max(0.0, float(row.get("ema_tokens", 0.0) or 0.0))
prev_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0) or 0.0)))
observed_success = 1.0 if verified_success else 0.0
ema_tokens = float(consumed) if samples == 0 else ALPHA * consumed + (1.0 - ALPHA) * prev_tokens
ema_success = observed_success if samples == 0 else ALPHA * observed_success + (1.0 - ALPHA) * prev_success
previous_failure_streak = max(0, int(row.get("failure_streak", 0) or 0))
previous_success_streak = max(0, int(row.get("success_streak", 0) or 0))
row = {
⋮----
ordered = sorted(
⋮----
def _metrics(row: dict) -> dict
⋮----
successes = max(0, int(row.get("verified_successes", 0) or 0))
total_tokens = max(1, int(row.get("total_tokens", 0) or 0))
cumulative = min(1.0, successes / samples) if samples else 0.0
recent = max(0.0, min(1.0, float(row.get("ema_success", cumulative) or 0.0)))
success = 0.4 * cumulative + 0.6 * recent
tokens_per_success = total_tokens / max(1, successes)
verified_per_million = successes * 1_000_000.0 / total_tokens
conservative = success * min(1.0, samples / 8.0)
score = conservative * 1_000_000.0 / max(1.0, float(row.get("ema_tokens", total_tokens)))
⋮----
def summarize(path_or_data: Path | dict) -> dict
⋮----
data = load(path_or_data) if isinstance(path_or_data, Path) else path_or_data
rows = []
⋮----
item = dict(row)
⋮----
project_scores = {}
⋮----
project = row["project_id"]
bucket = project_scores.setdefault(project, {
tokens = max(1, int(row.get("total_tokens", 0) or 0))
⋮----
projects = {}
⋮----
def project_multiplier(summary: dict, project_id: str) -> float
⋮----
projects = summary.get("projects") if isinstance(summary, dict) else None
⋮----
row = projects.get(project_id)
⋮----
scores = [
⋮----
mean = sum(scores) / len(scores)
⋮----
ratio = max(0.5, min(1.5, float(row.get("risk_adjusted_score", 0.0) or 0.0) / mean))
⋮----
rows = summary.get("rows") if isinstance(summary, dict) else None
⋮----
mature = [
⋮----
target = next(
⋮----
scores = [max(0.0, float(row.get("risk_adjusted_score", 0.0) or 0.0)) for row in mature]
⋮----
ratio = float(target.get("risk_adjusted_score", 0.0) or 0.0) / mean
# Deliberately bounded: enough to influence close candidates, never enough
# to overpower health, capability, quarantine, or architecture safeguards.
⋮----
streak = max(0, int(target.get("failure_streak", 0) or 0))
````

## File: capacity_ledger.py
````python
"""Crash-safe token reservation ledger for concurrent autonomous projects."""
⋮----
SCHEMA = 1
DEFAULT_TTL_SECONDS = 900
MAX_RESERVATIONS = 4096
⋮----
def _empty() -> dict
⋮----
def _load_unlocked(path: Path) -> dict
⋮----
path = Path(path)
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
reservations = value.get("reservations")
consumed = value.get("consumed")
reap_events = value.get("reap_events")
⋮----
def load(path: Path) -> dict
⋮----
def _save_unlocked(path: Path, data: dict) -> None
⋮----
def _reap(data: dict, now: float) -> int
⋮----
reservations = data.setdefault("reservations", {})
expired = [
events = data.setdefault("reap_events", [])
⋮----
row = reservations.pop(key, None)
⋮----
def reserved_tokens(data: dict, *, provider: str | None = None, project_id: str | None = None) -> int
⋮----
total = 0
⋮----
def consumed_tokens(data: dict, *, project_id: str | None = None, provider: str | None = None) -> int
⋮----
project = str(project_id).strip()
provider_name = str(provider).strip()
⋮----
estimate = max(1, int(estimated_tokens))
ttl = max(30, int(ttl_seconds))
current = time.time() if now is None else float(now)
⋮----
data = _load_unlocked(path)
reaped = _reap(data, current)
provider_reserved = reserved_tokens(data, provider=provider_name)
project_reserved = reserved_tokens(data, project_id=project)
project_consumed = consumed_tokens(data, project_id=project)
⋮----
remaining = max(0, int(provider_remaining_tokens))
⋮----
envelope = max(0, int(project_envelope_tokens))
⋮----
token = uuid.uuid4().hex
⋮----
ordered = sorted(
⋮----
actual = max(0, int(actual_tokens))
⋮----
row = data["reservations"].pop(str(reservation_id), None)
⋮----
project = str(row["project_id"])
provider = str(row["provider"])
key = project + "::" + provider
⋮----
"""Renew a worker reservation only when its durable progress marker advances."""
marker_value = str(progress_marker).strip()
⋮----
row = data["reservations"].get(str(reservation_id))
⋮----
previous = row.get("progress_marker")
⋮----
def release(path: Path, reservation_id: str, *, now: float | None = None) -> dict
⋮----
"""Atomically release victim reservations and reserve a bounded contender lease."""
victim = str(victim_project_id).strip()
contender = str(contender_project_id).strip()
⋮----
amount = max(1, int(reserve_tokens))
⋮----
matches = [
released_tokens = 0
released_by_provider = {}
⋮----
row = data["reservations"].pop(key)
tokens = max(0, int(row.get("reserved_tokens", 0) or 0))
⋮----
provider_name = str(row.get("provider") or "")
⋮----
"""Convert one active preemption admission lease into a worker-owned reservation."""
⋮----
match = next(
⋮----
def release_project(path: Path, project_id: str, *, now: float | None = None) -> dict
⋮----
"""Atomically release every outstanding reservation owned by a project."""
⋮----
providers = {}
⋮----
amount = max(0, int(row.get("reserved_tokens", 0) or 0))
⋮----
provider = str(row.get("provider") or "")
⋮----
def preemption_leases(data: dict) -> dict[str, dict]
⋮----
result = {}
⋮----
def reservations_by_provider(data: dict) -> dict[str, int]
⋮----
provider = str(row.get("provider") or "").strip()
⋮----
def usage_by_project(data: dict) -> dict[str, dict]
⋮----
projects = {}
⋮----
project = str(row.get("project_id") or "").strip()
⋮----
item = projects.setdefault(project, {"reserved_tokens": 0, "consumed_tokens": 0})
⋮----
def detailed_snapshot(path: Path, *, now: float | None = None) -> dict
⋮----
def snapshot(path: Path, *, now: float | None = None) -> dict
````

## File: capacity_runtime.py
````python
"""Read per-project capacity envelopes produced by the fleet scheduler."""
⋮----
def project_envelope(path: Path | str | None, project_id: str | None) -> int | None
⋮----
target = Path(path)
⋮----
value = json.loads(target.read_text(encoding="utf-8"))
⋮----
rows = value.get("projects")
⋮----
raw = row.get("token_envelope")
⋮----
def project_state(path: Path | str | None, project_id: str | None) -> dict
````

## File: capacity_scheduler.py
````python
"""Global capacity scheduler for autonomous multi-project execution.

This module stays deterministic and side-effect free except for its CLI output.
It allocates token envelopes across active projects and assigns provider classes
in the preferred order: local/unmetered, pooled free quota, remote free, paid.
"""
⋮----
CRITICAL_PHASES = {"verification", "tests", "review", "security_fix", "release_fix"}
ACTIVE_STATES = {"running", "deferred", "failed", "queued", "pending"}
⋮----
@dataclass(frozen=True)
class ProviderCapacity
⋮----
name: str
available_tokens: int | None
unmetered: bool = False
free_preferred: bool = True
paid: bool = False
reliability: float = 0.5
latency_ms: float | None = None
cost_per_million_tokens: float = 0.0
circuit_open: bool = False
observations: int = 0
⋮----
@property
    def tier(self) -> int
⋮----
@property
    def adaptive_score(self) -> float
⋮----
"""Higher is better; preserve free-first policy while ranking peers by evidence."""
reliability = max(0.0, min(1.0, float(self.reliability)))
latency = 1000.0 if self.latency_ms is None else max(0.0, float(self.latency_ms))
latency_score = 1.0 / (1.0 + latency / 1000.0)
cost = max(0.0, float(self.cost_per_million_tokens))
cost_score = 1.0 / (1.0 + cost)
availability = 1.0 if self.unmetered else min(1.0, max(0.0, float(self.available_tokens or 0)) / 1_000_000.0)
⋮----
def _clean_project(row: dict) -> dict | None
⋮----
project_id = str(row.get("id") or "").strip()
⋮----
status = str(row.get("status") or row.get("runtime_status") or "running")
⋮----
phase = str(row.get("phase") or "implementation")
requested = max(1, int(row.get("requested_tokens", 1)))
priority = max(1, min(100, int(row.get("priority", 50))))
difficulty = str(row.get("difficulty_band") or "medium")
critical = bool(row.get("critical")) or phase in CRITICAL_PHASES
⋮----
pressure = float(row.get("capacity_pressure", 0.0) or 0.0)
⋮----
pressure = 0.0
pressure = max(0.0, min(1.5, pressure))
⋮----
efficiency = float(row.get("efficiency_multiplier", 1.0) or 1.0)
⋮----
efficiency = 1.0
efficiency = max(0.75, min(1.25, efficiency))
⋮----
stagnation = float(row.get("stagnation_multiplier", 1.0) or 0.0)
⋮----
stagnation = 1.0
stagnation = max(0.0, min(1.0, stagnation))
paused = bool(row.get("capacity_paused", False))
⋮----
def _weight(project: dict) -> float
⋮----
difficulty_bonus = {
critical_bonus = 1.45 if project["critical"] else 1.0
failure_bonus = 1.15 if project["status"] == "failed" else 1.0
pressure_bonus = 1.0 + min(0.60, project.get("capacity_pressure", 0.0) * 0.40)
efficiency_bonus = max(0.75, min(1.25, project.get("efficiency_multiplier", 1.0)))
stagnation_multiplier = max(0.0, min(1.0, project.get("stagnation_multiplier", 1.0)))
⋮----
def _finite_capacity(providers: list[ProviderCapacity]) -> int
⋮----
def _weighted_work_conserving(projects: list[dict], capacity: int) -> dict[str, int]
⋮----
"""Distribute finite capacity by weight without stranding capacity at capped peers."""
remaining = max(0, int(capacity))
allocations = {project["id"]: 0 for project in projects}
pending = [
⋮----
total_weight = sum(_weight(project) for project in pending) or 1.0
available_at_start = remaining
progressed = 0
⋮----
project_id = project["id"]
cap = max(0, int(project.get("_max_envelope", 0)))
room = max(0, cap - allocations[project_id])
⋮----
share = max(1, int(available_at_start * (_weight(project) / total_weight)))
grant = min(room, share, remaining)
⋮----
"""Allocate project envelopes and provider order for one scheduling cycle."""
cleaned = [item for row in projects if (item := _clean_project(row)) is not None]
⋮----
explore = max(0.0, min(0.25, float(exploration_strength)))
⋮----
explore = 0.08
⋮----
def routing_score(provider: ProviderCapacity) -> float
⋮----
# Deterministic uncertainty bonus: new/under-observed peers get bounded
# opportunities to prove themselves without random routing or tier bypass.
uncertainty = 1.0 / (1.0 + max(0, int(provider.observations))) ** 0.5
⋮----
ordered_providers = sorted(
has_unmetered = any(p.unmetered for p in ordered_providers)
⋮----
reserve_ratio = float(critical_reserve_ratio)
⋮----
reserve_ratio = 0.10
reserve_ratio = max(0.0, min(0.50, reserve_ratio))
⋮----
finite = _finite_capacity(ordered_providers)
reserve = int(finite * reserve_ratio)
ordinary_pool = max(0, finite - reserve)
⋮----
prepared = []
⋮----
requested = project["requested_tokens"]
stagnation_cap = max(
⋮----
reserve_allocations: dict[str, int] = {project["id"]: 0 for project in prepared}
shared_allocations: dict[str, int] = {project["id"]: 0 for project in prepared}
⋮----
critical_projects = [project for project in prepared if project["critical"]]
⋮----
shared_projects = []
⋮----
already_reserved = reserve_allocations.get(project["id"], 0)
⋮----
shared_allocations = _weighted_work_conserving(shared_projects, ordinary_pool)
⋮----
allocations = []
⋮----
weight = _weight(project)
⋮----
max_envelope = int(project["_max_envelope"])
⋮----
envelope = 0
constrained = True
⋮----
envelope = max_envelope
constrained = envelope < requested
⋮----
envelope = min(
⋮----
provider_order = []
⋮----
available = (
⋮----
current_time = time.time() if now is None else float(now)
result = []
⋮----
name = str(row.get("name") or "").strip()
⋮----
unmetered = bool(row.get("unmetered"))
raw_available = row.get("available_tokens")
⋮----
available = None
⋮----
available = max(0, int(raw_available))
empirical = (health_data or {}).get(name)
⋮----
reliability = float(row.get("reliability", 0.5))
⋮----
reliability = 0.5
⋮----
successes = max(0, int(empirical.get("successes", 0)))
failures = max(0, int(empirical.get("failures", 0)))
⋮----
successes = failures = 0
# Beta(1,1) smoothing prevents tiny samples from dominating routing.
reliability = (successes + 1) / (successes + failures + 2)
⋮----
reliability = max(0.0, min(1.0, reliability))
raw_latency = row.get("latency_ms")
⋮----
raw_latency = empirical.get("latency_ms_ema")
⋮----
latency = None if raw_latency is None else max(0.0, float(raw_latency))
⋮----
latency = None
⋮----
cost = max(0.0, float(row.get("cost_per_million_tokens", 0.0) or 0.0))
⋮----
cost = 0.0
circuit_open = False
⋮----
circuit_open = float(empirical.get("opened_until", 0.0) or 0.0) > current_time
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server global capacity scheduler")
⋮----
args = parser.parse_args(argv)
⋮----
projects_payload = json.loads(Path(args.projects).read_text(encoding="utf-8"))
providers_payload = json.loads(Path(args.providers).read_text(encoding="utf-8"))
projects = projects_payload.get("projects", []) if isinstance(projects_payload, dict) else projects_payload
provider_rows = list(
capacity_sources = {}
⋮----
snapshot = fetch_omniroute_summary(
live_row = snapshot.provider_row("omniroute")
⋮----
# A configured live source replaces any stale static OmniRoute row.
# On network/schema/auth ambiguity, fail closed for that provider
# while allowing unrelated local/free providers to continue.
live_row = {
⋮----
provider_rows = [
⋮----
health_data = provider_health.load(Path(args.provider_health)) if args.provider_health else {}
report = allocate(
⋮----
rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
````

## File: capacity_status.py
````python
"""Safe capacity snapshot for reports; never exposes provider keys."""
⋮----
def snapshot(quota_path: Path | None = None) -> dict
⋮----
providers = load_providers(prefer_free=True)
⋮----
providers = ()
quota_data = load_quota(quota_path) if quota_path is not None else {"schema": 1, "months": {}}
rows = []
⋮----
mode = "unmetered"
⋮----
mode = "pooled-free"
⋮----
mode = "metered"
row = {
````

## File: ci_provider.py
````python
"""Explicit, fail-closed ownership of privileged mobile generation."""
⋮----
def selected(path='control/ci.json')
⋮----
value = json.loads(Path(path).read_text())
⋮----
def enabled(provider, path='control/ci.json')
````

## File: ci_runner.py
````python
"""CircleCI queue adapter using the shared autonomous completion pipeline."""
⋮----
def bounded_run(args, timeout)
⋮----
run_id = uuid.uuid4().hex
env = dict(os.environ, STUDIO_RUN_ID=run_id)
process = subprocess.Popen(args, env=env, start_new_session=True)
⋮----
containers = subprocess.run(['docker', 'ps', '-aq', '--filter',
⋮----
def _admission_for_project(capacity_plan: dict, project_id: str) -> dict | None
⋮----
rows = capacity_plan.get("projects") if isinstance(capacity_plan, dict) else None
⋮----
admission = row.get("admission")
⋮----
def _heartbeat_loop(stop_event, ledger_path, reservation_id, project_out, *, interval=60.0)
⋮----
result = renew_if_progressed(ledger_path, reservation_id, project_out)
⋮----
def save_report(out, results)
⋮----
temporary = out / 'queue.json.tmp'
⋮----
def _run_registered_stages(project, project_out, work, report, deadline, runner, clock)
⋮----
"""Compatibility wrapper for callers/tests while stage logic lives in orchestrator.py."""
result = _shared_run_registered_stages(
status = None if result['status'] == 'complete' else result['status']
⋮----
def _run_project_for_queue(project, project_out, work, runner, deadline, clock, baseline_sha)
⋮----
state = run_persistent_project(
status = state.get('status')
⋮----
projects = matrix(directory)
⋮----
capacity_plan = persist_capacity_plan(out, directory)
results = [{'id': p['id'], 'status': 'pending'} for p in projects]
⋮----
deadline = clock() + 70 * 60
baseline_sha = os.environ.get('CIRCLE_SHA1')
⋮----
admission = _admission_for_project(capacity_plan, project["id"])
⋮----
admission_claim = None
⋮----
admission_claim = claim_preemption_lease(
⋮----
project_out = out / project['id']
heartbeat_stop = None
heartbeat_thread = None
⋮----
heartbeat_stop = threading.Event()
heartbeat_thread = threading.Thread(
⋮----
result = _run_project_for_queue(project, project_out, work, runner, deadline, clock, baseline_sha)
⋮----
deadline = 0
⋮----
released = release_capacity_reservation(
⋮----
def main()
⋮----
mode = sys.argv[1] if len(sys.argv) == 2 else 'queue'
````

## File: completion.py
````python
"""Definition-of-done contract for autonomous mobile generation.

A green preview is evidence, not a finished application. This module keeps the
orchestrator honest and gives CI a machine-readable list of work that remains.
"""
⋮----
PREVIEW_STATUS = "validated_preview"
FINISHED_STATUS = "finished"
HUMAN_ACTION_STATUS = "human_action_required"
⋮----
BASE_RELEASE_STAGES = (
POST_QA_STAGES = (
ALLOWED_DYNAMIC_QA = {
⋮----
def required_release_stages(state: dict) -> tuple[str, ...]
⋮----
"""Return trusted stages in order, including capability-derived QA gates."""
release = state.get("release_evidence", {})
capability = release.get("capability_qa")
dynamic: list[str] = []
⋮----
requested = capability.get("required_qa_stages", [])
⋮----
stages = BASE_RELEASE_STAGES + tuple(dynamic) + POST_QA_STAGES
publication = state.get("publication_request", {})
⋮----
def completion_report(state: dict) -> dict
⋮----
"""Return a deterministic completion assessment without inventing evidence."""
blockers: list[str] = []
⋮----
evidence = release.get(key)
⋮----
def next_stage(state: dict) -> str | None
⋮----
"""Select the globally scheduled repair stage, then fall back to pipeline order."""
report = completion_report(state)
⋮----
scheduled = select_repair_task(state)
scheduled_stage = pipeline_stage_for_task(scheduled)
⋮----
evidence = release.get(stage)
⋮----
def apply_completion(state: dict) -> dict
````

## File: contextual_routing_memory.py
````python
"""Context-scoped routing memory for providers and agents."""
⋮----
MAX_CONTEXTS = 32
MAX_ACTORS_PER_CONTEXT = 32
ALPHA = 0.25
MIN_SAMPLES = 4
MAX_CONTEXT_BONUS = 12.0
MAX_CONTEXT_PENALTY = 18.0
MAX_BANDIT_EXPLORATION = 8.0
BANDIT_C = 0.75
HIGH_RISK_EXPLORATION_MULTIPLIER = 0.35
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
context_rows = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
successes = min(samples, max(0, int(row.get("successes", 0))))
ema = max(0.0, min(1.0, float(row.get("ema_success_rate", (successes / samples) if samples else 0.0))))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
rows = data.setdefault(context, {})
key = kind + ":" + name
row = rows.get(key, {"samples": 0, "successes": 0, "ema_success_rate": 0.0})
samples = int(row["samples"])
observed = 1.0 if success else 0.0
previous = float(row.get("ema_success_rate", observed))
ema = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous
⋮----
"""Bounded contextual UCB-style exploration/exploitation signal."""
⋮----
weighted_success = 0.0
weighted_uncertainty = 0.0
evidence_mass = 0.0
risk_multiplier = 1.0
⋮----
relevance = max(0.0, float(relevance))
⋮----
risk_multiplier = min(risk_multiplier, HIGH_RISK_EXPLORATION_MULTIPLIER)
rows = data.get(context)
⋮----
row = rows.get(kind + ":" + name)
⋮----
samples = max(0, int(row.get("samples", 0) or 0))
rate = max(0.0, min(1.0, float(row.get("ema_success_rate", 0.5))))
confidence = min(1.0, samples / 12.0)
mass = relevance * max(0.1, confidence)
uncertainty = 1.0 / ((samples + 1) ** 0.5)
⋮----
expected = max(0.0, min(1.0, weighted_success / evidence_mass))
relevance_total = max(1e-9, sum(max(0.0, float(weight)) for _, weight in weighted_contexts))
uncertainty = max(0.0, min(1.0, weighted_uncertainty / relevance_total))
bonus = min(
⋮----
total_weight = 0.0
signal = 0.0
⋮----
samples = int(row.get("samples", 0) or 0)
⋮----
rate = max(0.0, min(1.0, float(row.get("ema_success_rate", 0.0))))
centered = (rate - 0.5) * 2.0
mass = relevance * confidence
⋮----
normalized = max(-1.0, min(1.0, signal / total_weight))
````

## File: contextual_strategy_efficiency.py
````python
"""Context-scoped verified strategy efficiency memory."""
⋮----
MAX_CONTEXTS = 16
⋮----
def load(path: Path) -> dict
⋮----
value=json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean={}
⋮----
valid={}
⋮----
samples=max(0,int(row.get("samples",0)))
successes=min(samples,max(0,int(row.get("successes",0))))
cost=max(0.0,float(row.get("ema_cost_seconds",0.0)))
fallback=(successes/samples) if samples else 0.0
recent=max(0.0,min(1.0,float(row.get("ema_success_rate",fallback))))
⋮----
def _save(path:Path,data:dict)->None
⋮----
path=Path(path)
⋮----
def record(path:Path,context:str,strategy:str,*,success:bool,cost_seconds:float)->dict
⋮----
data=load(path)
rows=data.setdefault(context,{})
row=rows.get(strategy,{
samples=int(row["samples"])
cost=max(0.0,float(cost_seconds))
previous=float(row["ema_cost_seconds"])
alpha=0.25
cost_ema=cost if samples==0 else alpha*cost+(1.0-alpha)*previous
observed=1.0 if success else 0.0
previous_success=float(row.get("ema_success_rate",(int(row["successes"])/samples) if samples else observed))
recent=observed if samples==0 else alpha*observed+(1.0-alpha)*previous_success
⋮----
def rows_for(data:dict,context:str)->dict
⋮----
rows=data.get(context,{})
⋮----
def blend_rows(data: dict, weighted: list[tuple[str, float]]) -> dict
⋮----
"""Blend contextual rows into synthetic strategy evidence.

    Samples are used as confidence mass while the caller-provided context
    weights determine relevance. The result preserves the global strategy row
    schema so existing risk/efficiency scoring can consume it unchanged.
    """
accum = {}
⋮----
weight = max(0.0, float(context_weight))
⋮----
rows = rows_for(data, context)
⋮----
samples = max(0, int(row.get("samples", 0)))
⋮----
mass = weight * samples
target = accum.setdefault(strategy, {
success_rate = max(0.0, min(1.0, int(row.get("successes", 0)) / samples))
recent = max(0.0, min(1.0, float(row.get("ema_success_rate", success_rate))))
cost = max(0.0, float(row.get("ema_cost_seconds", 0.0)))
⋮----
blended = {}
⋮----
mass = values["mass"]
⋮----
effective_samples = max(1, int(round(mass)))
cumulative_rate = max(0.0, min(1.0, values["successes"] / mass))
successes = max(0, min(effective_samples, int(round(cumulative_rate * effective_samples))))
````

## File: contextual_utility.py
````python
"""Bounded cost-aware utility for contextual routing."""
⋮----
MAX_UTILITY_BONUS = 12.0
MAX_UTILITY_PENALTY = 16.0
REFERENCE_LATENCY_SECONDS = 30.0
REFERENCE_VERIFICATION_SECONDS = 120.0
HIGH_RISK_MULTIPLIER = 1.35
REFERENCE_CALL_COST_USD = 0.05
REFERENCE_RETRY_RATE = 0.5
UNMETERED_BONUS = 4.0
⋮----
success = max(0.0, min(1.0, float(expected_success)))
execution = max(0.0, float(execution_seconds or 0.0))
verification = max(0.0, float(verification_seconds or 0.0))
⋮----
execution_cost = min(1.0, execution / REFERENCE_LATENCY_SECONDS)
verification_cost = min(1.0, verification / REFERENCE_VERIFICATION_SECONDS)
risk = HIGH_RISK_MULTIPLIER if architecture_hold else 1.0
money = max(0.0, float(monetary_cost_usd or 0.0))
monetary_cost = min(1.0, money / REFERENCE_CALL_COST_USD)
retry = max(0.0, min(1.0, float(retry_probability or 0.0)))
retry_cost = min(1.0, retry / REFERENCE_RETRY_RATE)
⋮----
quality_value = success * 1.2
time_cost = (0.40 * execution_cost + 0.30 * verification_cost) * risk
paid_cost = 0.0 if (free_preferred or unmetered) else 0.05
multi_cost = 0.0 if unmetered else (0.20 * monetary_cost)
⋮----
normalized = quality_value - time_cost - paid_cost - multi_cost
normalized = max(-1.0, min(1.0, normalized))
⋮----
score = normalized * MAX_UTILITY_BONUS
⋮----
score = normalized * MAX_UTILITY_PENALTY
````

## File: continuous_improvement.py
````python
"""Evidence-gated continuous-improvement planning for completed projects."""
⋮----
VERSION=1
⋮----
class ImprovementError(ValueError)
⋮----
def _digest(value)
⋮----
def _candidate(kind,key,priority,objective,source,required_evidence)
⋮----
identity={"kind":kind,"key":key,"source":source,"required_evidence":required_evidence}
⋮----
def assess(goal_state,project_state,*,max_candidates=20)
⋮----
candidates=[]
⋮----
failures=Counter(x for x in goal_state.get("failures",[]) if isinstance(x,str) and x.strip())
⋮----
source={"failure":failure,"occurrences":count}
⋮----
missing=Counter()
⋮----
capability=event.get("missing_capability")
⋮----
source={"capability":capability,"missing_occurrences":count}
⋮----
release=project_state.get("release_evidence")
⋮----
warnings=evidence.get("warnings")
⋮----
clean=sorted({w.strip() for w in warnings if isinstance(w,str) and w.strip()})
⋮----
source={"stage":stage,"warnings":clean}
⋮----
def next_candidate(assessment)
⋮----
candidates=assessment.get("candidates")
⋮----
def improvement_goal(candidate,*,max_attempts=8)
⋮----
required={"id","kind","priority","objective","source","required_evidence","evidence_fingerprint"}
⋮----
evidence=candidate["required_evidence"]
````

## File: core.py
````python
"""Bounded mobile studio. Standard library only; model output is data, never shell."""
⋮----
IMAGE = 'ghcr.io/cirruslabs/flutter:3.44.0@sha256:0a9de3b70b5b7b921a346eb2793e363dc22280849a4fd690d9dde99ce1c2b1b8'
ROLES = {
⋮----
class StudioError(Exception)
⋮----
def canonical(value)
⋮----
def request_check(data)
⋮----
required = {'id', 'target_repo', 'app_name', 'brief', 'enabled'}
⋮----
val = data.get(key, default)
⋮----
priority = data.get('priority', 50)
⋮----
project_calls = data.get('max_project_model_calls')
⋮----
repair_calls = data.get('max_project_repair_calls')
⋮----
api_budget = data.get('max_api_cost_usd')
⋮----
api_budget = float(api_budget)
⋮----
preference = data['agent_preference']
⋮----
production_os = data['production_os']
⋮----
workflow_id = production_os.get('workflow_id')
workflow_task_id = production_os.get('workflow_task_id')
⋮----
contracts = data['tool_contracts']
⋮----
normalized = {}
asset_forge = contracts.get('asset_forge')
⋮----
publish = data['play_publish']
⋮----
enabled = publish.get('enabled', False)
track = publish.get('track', 'internal')
commit = publish.get('commit', False)
⋮----
def allowed(path)
⋮----
parts = path.split('/')
⋮----
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|nvapi-[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}')
⋮----
def patch_check(value)
⋮----
def require_clean_patch_workspace(root)
⋮----
root = Path(root)
⋮----
def apply_patch(root, value)
⋮----
files = patch_check(value)
⋮----
p = root / f['path']
⋮----
staging = None
retain_recovery = False
⋮----
def ensure_directory(path)
⋮----
missing = []
⋮----
path = path.parent
⋮----
staging = Path(tempfile.mkdtemp(prefix='.__studio-patch-', dir=root))
⋮----
target = root / f['path']
staged = staging / str(index)
⋮----
retain_recovery = True
rollback_failed = False
⋮----
backup = staging / (str(index) + '.backup')
⋮----
rollback_failed = True
⋮----
def verdict(value)
⋮----
class APIError(StudioError)
⋮----
def __init__(self, status)
⋮----
class ProtocolError(StudioError)
⋮----
class NoRedirect(urllib.request.HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
⋮----
class API
⋮----
def __init__(self, base, key)
⋮----
u = urlsplit(base)
loopback_hosts = {'127.0.0.1', 'localhost', '::1', '0.0.0.0'}
local_http = u.scheme == 'http' and (u.hostname or '').lower() in loopback_hosts
secure_remote = u.scheme == 'https'
⋮----
def _response(self, req, timeout_seconds=300)
⋮----
# A pending inference is polled; never submit a second paid POST.
timeout_seconds = max(1.0, min(300.0, float(timeout_seconds)))
opener = urllib.request.build_opener(NoRedirect)
deadline = time.monotonic() + timeout_seconds
⋮----
remaining = deadline - time.monotonic()
⋮----
response = opener.open(req, timeout=min(180, remaining))
⋮----
raw = res.read(4000001)
⋮----
request_id = res.headers.get('NVCF-REQID', '')
⋮----
# Documented same-origin endpoint; never trust a remote Location URL.
req = urllib.request.Request(self.base + '/status/' + request_id,
⋮----
def call(self, method, path, data=None, timeout_seconds=300)
⋮----
headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
⋮----
req = urllib.request.Request(self.base + path, method=method,
⋮----
# Never print remote bodies: providers may echo secrets or prompts.
⋮----
delay = min(float(2 ** attempt), max(0.0, deadline - time.monotonic()))
⋮----
class Model
⋮----
def __init__(self, limit, avoid_providers=())
⋮----
primary = self.providers[0]
⋮----
def ask(self, role, context, screenshots=())
⋮----
context = augment(context)
# One schema/truncation repair, charged against the global model-call budget.
⋮----
value = self._ask(role, context, screenshots)
⋮----
error = str(e)
⋮----
def _ask(self, role, context, screenshots=())
⋮----
content = [{'type': 'text', 'text': context}]
⋮----
schema = ('Editable scope: lib/*.dart, test/*.dart (including subdirectories), assets/*.svg or *.json, docs/*.md, pubspec.yaml, analysis_options.yaml. Never use reserved __studio names. Provide at least one real *_test.dart file. Return ONLY JSON {"files":[{"path":"lib/app.dart","content":"full file"}]}.' if role in ('implementation', 'tests') else
⋮----
provider_candidates = tuple(
health_raw = os.environ.get('STUDIO_PROVIDER_HEALTH_PATH', '')
metrics_raw = os.environ.get('STUDIO_PROVIDER_METRICS_PATH', '')
health_path = Path(health_raw) if health_raw else None
metrics_path = Path(metrics_raw) if metrics_raw else None
history_raw = os.environ.get('STUDIO_ROUTING_HISTORY_PATH', '')
history_path = Path(history_raw) if history_raw else None
cost_raw = os.environ.get('STUDIO_PROVIDER_COST_PATH', '')
cost_path = Path(cost_raw) if cost_raw else None
quota_raw = os.environ.get('STUDIO_PROVIDER_MONTHLY_QUOTA_PATH', '')
quota_path = Path(quota_raw) if quota_raw else None
local_rep_raw = os.environ.get('STUDIO_LOCAL_MODEL_REPUTATION_PATH', '')
local_rep_path = Path(local_rep_raw) if local_rep_raw else None
local_benchmark_raw = os.environ.get('STUDIO_LOCAL_MODEL_BENCHMARK_PATH', '')
local_benchmark_path = Path(local_benchmark_raw) if local_benchmark_raw else None
local_specialization_raw = os.environ.get('STUDIO_LOCAL_MODEL_SPECIALIZATION_PATH', '')
local_specialization_path = Path(local_specialization_raw) if local_specialization_raw else None
portfolio_learning_raw = os.environ.get('STUDIO_MODEL_PORTFOLIO_LEARNING_PATH', '')
portfolio_learning_path = Path(portfolio_learning_raw) if portfolio_learning_raw else None
⋮----
local_weighted_contexts = json.loads(os.environ.get('STUDIO_ROUTING_CONTEXTS_JSON','[]'))
⋮----
local_weighted_contexts = []
⋮----
provider_costs = load_provider_cost(cost_path) if cost_path is not None else {}
quota_data = load_provider_monthly_quota(quota_path) if quota_path is not None else {'schema': 1, 'months': {}}
local_model_reputation = load_local_model_reputation(local_rep_path) if local_rep_path is not None else {}
local_model_benchmark = load_local_model_benchmark(local_benchmark_path) if local_benchmark_path is not None else {}
local_model_specialization = load_local_model_specialization(local_specialization_path) if local_specialization_path is not None else {}
portfolio_learning = load_model_portfolio_learning(portfolio_learning_path) if portfolio_learning_path is not None else {}
learned_diversity_bias = model_portfolio_diversity_bias(portfolio_learning)
⋮----
max_api_cost_usd = float(os.environ.get('STUDIO_MAX_API_COST_USD', '0') or 0.0)
⋮----
max_api_cost_usd = 0.0
spent_api_cost_usd = sum(
health = load_provider_health(health_path) if health_path is not None else {}
metrics = load_provider_metrics(metrics_path) if metrics_path is not None else {}
history = load_routing_history(history_path) if history_path is not None else []
weights = learned_weights(history, kind='provider', role=role)
⋮----
provider_candidates = budget_eligible(
⋮----
provider_scores = {}
⋮----
trace = score_provider(
components = dict(trace.components)
⋮----
gateway_name = provider.name.split(':', 1)[0]
model_name = provider.model_for(role, bool(screenshots))
reputation_component = local_model_reputation_score(
⋮----
parsed_local_contexts = [
specialization = local_model_specialization_score(
⋮----
quarantine = local_model_quarantine_status(
⋮----
implementation_provider = self.providers_used.get('implementation')
implementation_model = self.models_used.get('implementation')
candidate_model = provider.model_for(role, bool(screenshots))
⋮----
quota = provider_quota_status(
⋮----
provider_candidates = tuple(sorted(
⋮----
independent_candidates = tuple(
⋮----
provider_candidates = independent_candidates
⋮----
messages = [{'role': 'system', 'content': ROLES[role] + '\n' + (CONTRACT if role in ('product', 'implementation') else '') + schema}, {'role': 'user', 'content': content if screenshots else context}]
r = None
responded = False
last_error = None
selected_model = ''
selected_provider = None
selected_provider_spec = None
⋮----
selected_model = provider.model_for(role, bool(screenshots))
# Reuse the primary client created at construction time. Besides
# avoiding needless client churn, this keeps dependency injection
# deterministic for tests and callers. Fallback providers still
# receive isolated clients with their own credentials/base URL.
api = self.api if provider_index == 0 else API(provider.base, provider.key)
params = {'model': selected_model, 'stream': False,
⋮----
started = time.monotonic()
⋮----
r = api.call('POST', '/chat/completions', params)
elapsed = time.monotonic() - started
⋮----
responded = True
⋮----
last_error = exc
⋮----
selected_provider = provider.name
selected_provider_spec = provider
⋮----
usage = r.get('usage') if isinstance(r, dict) else None
⋮----
prompt_tokens = int(usage.get('prompt_tokens', 0) or 0)
completion_tokens = int(usage.get('completion_tokens', 0) or 0)
⋮----
prompt_tokens = completion_tokens = 0
⋮----
call_cost = (
⋮----
choice = r['choices'][0]
⋮----
raw = choice['message']['content']
⋮----
raw = raw.strip()
⋮----
raw = raw.split('\n', 1)[1].rsplit('```', 1)[0]
def unique_object(pairs)
⋮----
result = {}
⋮----
value = json.loads(raw, object_pairs_hook=unique_object)
⋮----
pending = [(value, 0)]
⋮----
serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
⋮----
class Sandbox
⋮----
def __init__(self, root)
def run(self, args, network=False, timeout=600)
⋮----
name = 'mobile-studio-' + uuid.uuid4().hex
⋮----
cmd = ['docker', 'run', '--name', name, '--rm', '--init', '--cap-drop=ALL', '--security-opt=no-new-privileges',
run_id = os.environ.get('STUDIO_RUN_ID', '')
⋮----
# No inherited credentials, host home, socket, .git or privileged mounts.
env = {k: os.environ[k] for k in ('PATH', 'HOME', 'DOCKER_HOST') if k in os.environ}
⋮----
r = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
⋮----
def create(self, name)
def quick_dependency_gate(self)
⋮----
args = ['flutter', 'pub', 'get']
⋮----
log = {'command': args, 'exit_code': rc, 'output': out}
⋮----
def quick_analyze_gate(self)
⋮----
args = ['flutter', 'analyze', '--no-pub']
⋮----
def quick_test_gate(self, targets=())
⋮----
targets = [target for target in targets if isinstance(target, str) and target.startswith('test/') and target.endswith('_test.dart')]
args = ['flutter', 'test', '--no-pub', '--exclude-tags=studio-visual'] + targets
⋮----
def quick_gates(self)
⋮----
"""Compatibility wrapper over progressive intermediate gates."""
logs = []
⋮----
def gates(self, name, journeys)
⋮----
# Trusted test is reinstated every round; model cannot edit its reserved name.
probe = Path(__file__).with_name('visual_test.dart').read_text().replace('APP_NAME', name).replace('JOURNEYS_BASE64', encoded_journeys(journeys))
⋮----
p = self.root / rel
⋮----
apk = self.root / 'build/app/outputs/flutter-apk/app-debug.apk'
pngs = list((self.root / 'test/goldens').glob('*.png'))
````

## File: cost_drift.py
````python
"""Phase cost drift detection for autonomous execution."""
⋮----
@dataclass
class CostDriftDetector
⋮----
elevated_ratio: float = 1.5
severe_ratio: float = 2.0
samples: list[dict] = field(default_factory=list)
⋮----
def record(self, *, phase: str, expected_seconds: float, observed_seconds: float, baseline: dict | None = None) -> dict
⋮----
expected = max(1.0, float(expected_seconds))
observed = max(0.0, float(observed_seconds))
ratio = observed / expected
source = "fixed_ratio"
normalized_deviation = None
⋮----
mean = max(1.0, float(baseline.get("ema_seconds", 0.0)))
deviation = max(1.0, float(baseline.get("ema_abs_deviation", 0.0)))
normalized_deviation = (observed - mean) / deviation
source = "historical"
⋮----
level = "severe"
⋮----
level = "elevated"
⋮----
level = "normal"
⋮----
sample = {
⋮----
def decision(self) -> dict
⋮----
severe = [x for x in self.samples if x["level"] == "severe"]
elevated = [x for x in self.samples if x["level"] == "elevated"]
⋮----
def exploration_multiplier(self) -> float
⋮----
action = self.decision()["action"]
⋮----
def snapshot(self) -> dict
````

## File: device_qa.py
````python
"""Trusted Android emulator QA for validated release artifacts and journeys."""
⋮----
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ')
SYSTEM_IMAGE = os.environ.get('STUDIO_ANDROID_SYSTEM_IMAGE', 'system-images;android-35;google_apis;x86_64')
AVD_NAME = 'studio-release-qa'
⋮----
def run_command(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess
⋮----
def wait_for_boot(adb: str = 'adb', timeout: int = 240) -> dict
⋮----
start = time.monotonic()
attempts = 0
⋮----
state = run_command([adb, 'get-state'], timeout=15)
⋮----
boot = run_command([adb, 'shell', 'getprop', 'sys.boot_completed'], timeout=15)
⋮----
def package_name(root: Path) -> str
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
text = manifest.read_text(errors='replace')
match = re.search(r'package="([A-Za-z0-9_.]+)"', text)
⋮----
gradle = root / rel
⋮----
match = re.search(r'applicationId\s*(?:=\s*)?["\']([A-Za-z0-9_.]+)["\']',
⋮----
def start_emulator() -> subprocess.Popen
⋮----
required = ('sdkmanager', 'avdmanager', 'emulator', 'adb')
missing = [name for name in required if shutil.which(name) is None]
⋮----
install = run_command(['sdkmanager', SYSTEM_IMAGE], timeout=900)
⋮----
avd_dir = Path.home() / '.android/avd' / (AVD_NAME + '.avd')
⋮----
created = subprocess.run(['avdmanager', 'create', 'avd', '-n', AVD_NAME, '-k', SYSTEM_IMAGE,
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
emulator = None
owned_emulator = False
serial = None
⋮----
emulator = start_emulator()
owned_emulator = True
boot = wait_for_boot(adb)
⋮----
serial = os.environ.get('ANDROID_SERIAL')
⋮----
devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
⋮----
serial = serials[0]
⋮----
pkg = package_name(root)
logs: list[dict] = []
⋮----
install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
⋮----
launch = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c',
⋮----
screenshot = out / 'device-release.png'
⋮----
shot = subprocess.run([adb, '-s', serial, 'exec-out', 'screencap', '-p'], stdout=handle,
⋮----
logcat = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
crash_lines = [line for line in logcat.stdout.splitlines()
⋮----
journey_evidence = None
⋮----
journey_evidence = run_on_device(root, journeys, serial)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
journeys = json.loads(Path(args.journeys_json).read_text()) if args.journeys_json else None
result = validate_release_on_device(Path(args.work), Path(args.out), journeys)
````

## File: device_stage.py
````python
"""Persist trusted Android emulator QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
journeys = validate_journeys(state.get('product', {}).get('journeys'))
⋮----
evidence = validate_release_on_device(root, out, journeys)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('real_device')
````

## File: diagnostics.py
````python
"""Normalize stage failures into machine, environment, and human-owned diagnostics."""
⋮----
ENVIRONMENT_BLOCKERS = {
⋮----
HUMAN_OR_EXTERNAL_BLOCKERS = {
⋮----
PREREQUISITE_BLOCKERS = {
⋮----
RETRYABLE_ENVIRONMENT_BLOCKERS = {
⋮----
CODE_PREFIXES = (
⋮----
CODE_BLOCKERS = {
⋮----
def _kind(blocker: str) -> str
⋮----
base = blocker.split(":", 1)[0]
⋮----
def classify(stage: str, evidence: dict) -> dict
⋮----
blockers = evidence.get("blockers", [])
⋮----
blockers = []
items = [
⋮----
def repairable(stage: str, evidence: dict) -> list[str]
⋮----
def retryable_environment(stage: str, evidence: dict) -> list[str]
⋮----
diagnostics = classify(stage, evidence)
````

## File: diff_quick_gates.py
````python
"""Plan minimal trusted Flutter quick gates from an editable-source delta."""
⋮----
DEPENDENCY_FILES = {"pubspec.yaml"}
ANALYZE_FILES = {"analysis_options.yaml", "pubspec.yaml"}
⋮----
def _package_name(root: Path) -> str | None
⋮----
pubspec = root / "pubspec.yaml"
⋮----
text = pubspec.read_text(encoding="utf-8")
⋮----
match = re.search(r"(?m)^name:\s*([a-zA-Z0-9_]+)\s*$", text)
⋮----
def _targeted_tests(root: Path, changed: list[str]) -> list[str]
⋮----
targets: set[str] = set()
changed_lib = [
⋮----
stem = rel[len("lib/"):-len(".dart")]
direct = "test/" + stem + "_test.dart"
leaf = "test/" + Path(stem).name + "_test.dart"
⋮----
package = _package_name(root)
⋮----
text = path.read_text(encoding="utf-8")
⋮----
rel_test = path.relative_to(root).as_posix()
⋮----
package_import = f"package:{package}/{lib_rel}" if package else None
⋮----
def plan(root: Path, changed: list[str]) -> dict
⋮----
changed = sorted({item for item in changed if isinstance(item, str) and item})
dependency_changed = any(item in DEPENDENCY_FILES for item in changed)
lib_changed = any(
test_changed = any(
code_changed = lib_changed or test_changed
# Test-only deltas are compiled by their targeted quick test. Full project
# analysis remains mandatory in the final trusted gate set.
analyze_needed = lib_changed or any(item in ANALYZE_FILES for item in changed)
tests_needed = code_changed
targeted = _targeted_tests(root, changed) if tests_needed else []
````

## File: durable_state.py
````python
"""Versioned, checksummed, crash-safe JSON state storage."""
⋮----
CURRENT_SCHEMA = 2
⋮----
def _checksum(schema: int, value: dict) -> str
⋮----
raw = canonical({"schema": schema, "value": value}).encode("utf-8")
⋮----
def _migrate(schema: int, value: dict) -> tuple[int, dict]
⋮----
current = dict(value)
version = int(schema)
⋮----
version = 1
⋮----
history = list(current["migration_history"])
⋮----
version = 2
⋮----
def load(path: Path, *, default: dict | None = None) -> dict
⋮----
path = Path(path)
⋮----
payload = json.loads(path.read_text(encoding="utf-8"))
⋮----
schema = payload.get("schema")
value = payload.get("value")
checksum = payload.get("sha256")
⋮----
def save(path: Path, value: dict) -> None
⋮----
envelope = {
⋮----
backup = path.with_name(path.name + ".bak")
⋮----
def load_recovering(path: Path, *, default: dict | None = None) -> dict
⋮----
value = load(backup)
⋮----
def repair_from_backup(path: Path, backup: Path) -> dict
````

## File: engine_detect.py
````python
"""Detect the target project engine as a bounded subprocess preflight."""
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
req = request_check(json.loads(Path(args.request).read_text()))
⋮----
result = {'status':'disabled','engine':None}
⋮----
github = GitHub(req['target_repo'])
result = {'status':'detected','engine':detect_engine(req, github)}
````

## File: engine_entry.py
````python
"""Trusted preview dispatcher preserving the mature Flutter runner unchanged."""
⋮----
def _exact_branch_ref(github: GitHub, branch: str)
⋮----
refs = github.get('/git/matching-refs/heads/' + branch)
⋮----
exact = [item for item in refs if isinstance(item, dict) and item.get('ref') == 'refs/heads/' + branch]
⋮----
def detect_engine(req: dict, github: GitHub) -> str
⋮----
"""Infer engine from the checkpoint branch when present, otherwise target default branch.

    Empty/bootstrap repositories stay Flutter for backwards compatibility. Existing repositories
    must expose exactly one trusted marker; ambiguous/unknown projects fail closed.
    """
metadata = github.get('')
⋮----
branch = 'studio/' + req['id']
exact = _exact_branch_ref(github, branch)
⋮----
source = exact.get('object', {}).get('sha')
⋮----
default = metadata.get('default_branch')
⋮----
info = github.get('/branches/' + default)
source = info.get('commit', {}).get('sha') if isinstance(info, dict) else None
⋮----
tree = github.get('/git/trees/' + source + '?recursive=1')
⋮----
paths = [item.get('path') for item in tree['tree'] if isinstance(item, dict) and item.get('type') == 'blob' and isinstance(item.get('path'), str)]
# Preserve legacy Flutter bootstrap repositories containing only documentation files.
⋮----
def execute(req: dict, root: Path, out: Path, github=None) -> dict
⋮----
req = request_check(req)
⋮----
github = github or GitHub(req['target_repo'])
engine = detect_engine(req, github)
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
out = Path(args.out)
⋮----
req = json.loads(Path(args.request).read_text())
state = execute(req, Path(args.work), out)
⋮----
detail = str(exc) if isinstance(exc, StudioError) else 'Invalid configuration or local IO failure'
````

## File: engine_patch.py
````python
"""Trusted engine-aware validation for model-generated source patches."""
⋮----
MAX_FILES = 60
MAX_TOTAL_BYTES = 600_000
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|nvapi-[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}')
⋮----
class PatchPolicyError(ValueError)
⋮----
def validate(value: dict, engine: str, role: str = 'implementation') -> list[dict]
⋮----
seen = set(); total = 0; normalized = []
⋮----
path = item.get('path'); content = item.get('content')
⋮----
size = len(content.encode())
````

## File: evolution_automerge.py
````python
"""Merge durable autonomous evolution from immutable content-bound GitHub proof."""
⋮----
REQUIRED_CHECKS = {'validate', 'mobile-smoke'}
TRUSTED_CHECK_APP = 'github-actions'
⋮----
class AutoMergeError(RuntimeError): pass
⋮----
def _allowed_paths(candidate_id, gap)
⋮----
expected=set(expected_paths(gap).values()); expected.add('control/promoted_stages.json'); expected.add('control/evolution_rollbacks/'+candidate_id+'.json'); return expected
⋮----
def _trusted_check(run, repository)
⋮----
app=run.get('app')
⋮----
details=run.get('details_url')
⋮----
parsed=urlparse(details); prefix='/'+repository+'/actions/runs/'
⋮----
def _proof(pending, persisted)
⋮----
proof={'pull_request':pending.get('pull_request'),'commit_sha':pending.get('commit_sha'),'branch':pending.get('branch')}
⋮----
def attempt(work_order:dict,persisted:dict|None,token:str,repository:str)->dict
⋮----
pending=check_pending(work_order,token,repository); status=pending.get('status')
⋮----
candidate_id=work_order.get('candidate_id'); gap=(work_order.get('primary_gap') or {}).get('value')
proof=_proof(pending,persisted or {}); number=proof['pull_request']; head_sha=proof['commit_sha']; branch=proof['branch']
api='https://api.github.com/repos/'+repository
pr=_request(api+'/pulls/'+str(number),token)
⋮----
files=_request(api+'/pulls/'+str(number)+'/files?per_page=100',token); allowed=_allowed_paths(candidate_id,gap)
⋮----
names={item.get('filename') for item in files if isinstance(item,dict)}
⋮----
checks=_request(api+'/commits/'+head_sha+'/check-runs?per_page=100',token); runs=checks.get('check_runs') if isinstance(checks,dict) else None
⋮----
trusted=[run for run in runs if _trusted_check(run,repository)]; by_name={run.get('name'):run for run in trusted if isinstance(run.get('name'),str)}
missing=REQUIRED_CHECKS-set(by_name)
⋮----
run=by_name[name]
⋮----
merged=_request(api+'/pulls/'+str(number)+'/merge',token,'PUT',{'sha':head_sha,'merge_method':'merge','commit_title':'Promote autonomous capability: '+gap})
⋮----
def wait_and_attempt(work_order,persisted,token,repository,wait_seconds,poll_seconds=20)
⋮----
deadline=time.monotonic()+max(0,wait_seconds)
⋮----
result=attempt(work_order,persisted,token,repository)
⋮----
remaining=deadline-time.monotonic()
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('persisted',nargs='?'); parser.add_argument('--out',default='studio-output'); parser.add_argument('--wait-seconds',type=int,default=0)
args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
⋮----
order=json.loads(Path(args.work_order).read_text()); persisted=json.loads(Path(args.persisted).read_text()) if args.persisted else {}
result=wait_and_attempt(order,persisted,os.environ.get('STUDIO_GITHUB_TOKEN',''),os.environ.get('GITHUB_REPOSITORY',''),args.wait_seconds)
````

## File: evolution_benchmark.py
````python
"""Deterministic promotion evaluator for factory-evolution candidates."""
⋮----
REQUIRED_RESULT_KEYS = {
⋮----
class BenchmarkRejected(ValueError)
⋮----
def _sha(value, label)
⋮----
def _hash_map(value)
⋮----
out = {}
⋮----
def _test_result(value)
⋮----
def _capability(value, expected_gap)
⋮----
def _differential(value, candidate_id, baseline_sha, candidate_sha)
⋮----
required = {'version','status','candidate_id','baseline_sha','candidate_sha','test_file','tests_collected','baseline_failed_all','candidate_passed','improvement_proved','blockers'}
⋮----
proved = (value.get('status') == 'differential_proved' and value.get('baseline_failed_all') is True
⋮----
def validate_execution_result(value, expected_gap)
⋮----
result = dict(value); result['commit_sha'] = _sha(value.get('commit_sha'), 'Benchmark')
⋮----
def evaluate(work_order, baseline, candidate, differential=None)
⋮----
primary = work_order.get('primary_gap'); gap = primary.get('value') if isinstance(primary, dict) else None
⋮----
baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
baseline = validate_execution_result(baseline, gap); candidate = validate_execution_result(candidate, gap)
⋮----
blockers = []; gates = {}
⋮----
non_regressing = (candidate['unit_tests']['passed'] and candidate['unit_tests']['count'] >= baseline['unit_tests']['count']
⋮----
protected_equal = candidate['protected_hashes'] == baseline['protected_hashes']
⋮----
capability_passed = candidate['capability_benchmark']['passed']
⋮----
required = work_order.get('promotion_gates')
⋮----
unknown = [item for item in required if item not in gates]
⋮----
marker = 'promotion_gate_failed:' + item
⋮----
accepted = capability_passed and not blockers
````

## File: evolution_candidate.py
````python
"""Fail-closed contract for synthesized factory-evolution candidates.

A candidate may add only the missing trusted QA implementation, its trusted stage
adapter, tests and a benchmark fixture. It cannot edit completion/security/privacy
contracts, CI workflows, existing tests, or other trusted factory code. Registry
changes are deliberately reserved for the later trusted promotion layer.
"""
⋮----
VERSION = 1
MAX_FILES = 6
MAX_FILE_BYTES = 80_000
MAX_TOTAL_BYTES = 220_000
⋮----
PROTECTED_PATHS = {
FORBIDDEN_CALLS = {'eval','exec','compile','__import__','os.system','os.popen','subprocess.call',
SECRET_PATTERNS = (re.compile(r'gh[pousr]_[A-Za-z0-9_]{20,}'),re.compile(r'AIza[0-9A-Za-z0-9_-]{20,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'))
⋮----
class CandidateRejected(ValueError): pass
⋮----
def _gap(value)
⋮----
def expected_paths(gap)
⋮----
gap=_gap(gap); base=gap[:-3]
⋮----
def _safe_path(path)
⋮----
p=PurePosixPath(path)
⋮----
normalized=p.as_posix()
⋮----
def _call_name(node)
⋮----
target=node.func
⋮----
parts=[]
while isinstance(target,ast.Attribute): parts.append(target.attr); target=target.value
⋮----
def _decorator_name(node)
⋮----
parts=[]; target=node
⋮----
def _python_tree(path,content)
def _validate_python(path,content)
⋮----
tree=_python_tree(path,content)
⋮----
name=_call_name(node)
⋮----
def _validate_benchmark(content,gap)
⋮----
try: value=json.loads(content)
⋮----
assertions=value.get('assertions')
⋮----
def _test_method_count(content)
⋮----
tree=_python_tree('candidate_test.py',content); names=[node.name for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_')]
⋮----
def _reject_top_level_candidate_import(test_content,gap)
⋮----
tree=_python_tree('candidate_test.py',test_content); targets={gap,'studio.'+gap}
⋮----
def validate_candidate(work_order,research,candidate)
⋮----
candidate_id=work_order.get('candidate_id')
⋮----
primary=work_order.get('primary_gap'); gap=_gap(primary.get('value') if isinstance(primary,dict) else None)
⋮----
files=candidate.get('files')
⋮----
expected=expected_paths(gap); allowed=set(expected.values()); normalized=[]; seen=set(); total=0; benchmark_value=None; test_content=None
⋮----
path=_safe_path(item.get('path'))
⋮----
seen.add(path); content=item.get('content')
⋮----
size=len(content.encode())
⋮----
if path==expected['tests']: test_content=content
else: benchmark_value=_validate_benchmark(content,gap)
⋮----
missing=[role for role,path in expected.items() if path not in seen]
⋮----
test_count=_test_method_count(test_content); assertion_count=len(benchmark_value['assertions'])
⋮----
digest_payload={'candidate_id':candidate_id,'gap':gap,'files':[{'path':item['path'],'sha256':hashlib.sha256(item['content'].encode()).hexdigest()} for item in sorted(normalized,key=lambda x:x['path'])]}
digest=hashlib.sha256(json.dumps(digest_payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
````

## File: evolution_differential.py
````python
"""Validate baseline-red/candidate-green proof for self-evolution."""
⋮----
class DifferentialRejected(ValueError): pass
def _sha(value,label)
def _result(value,label)
⋮----
required={'commit_sha','test_file','tests_collected','failures','errors','passed'}
⋮----
out=dict(value); out['commit_sha']=_sha(value.get('commit_sha'),label)
⋮----
def evaluate(work_order,validated_candidate,baseline,candidate)
⋮----
baseline_sha=_sha(work_order.get('baseline_sha'),'Baseline')
tests=[f.get('path') for f in validated_candidate.get('files',[]) if isinstance(f,dict) and isinstance(f.get('path'),str) and f['path'].startswith('tests/test_')]
⋮----
expected=tests[0]; baseline=_result(baseline,'Baseline'); candidate=_result(candidate,'Candidate')
⋮----
baseline_failed_all=(not baseline['passed'] and baseline['failures']+baseline['errors']==baseline['tests_collected'])
candidate_passed=candidate['passed']; improved=baseline_failed_all and candidate_passed; blockers=[]
````

## File: evolution_evidence.py
````python
"""Validate research evidence supplied to a factory-evolution work order.

The orchestrating ChatGPT/Work layer or trusted research adapters may gather
external metadata, but only compact allowlisted evidence enters the trusted
factory. Executable code is never accepted as research evidence.
"""
⋮----
OFFICIAL_HOSTS = {
PACKAGE_HOSTS = {'pub.dev'}
GITHUB_HOSTS = {'github.com'}
DEVICE_IDENTIFIERS = {
⋮----
def _https_host(source: str) -> str
⋮----
parsed = urlsplit(source)
⋮----
def validate_evidence(work_order: dict, evidence: dict) -> dict
⋮----
tasks = work_order.get('research_tasks') if isinstance(work_order, dict) else None
⋮----
expected = {task.get('id'): task for task in tasks if isinstance(task, dict) and isinstance(task.get('id'), str)}
⋮----
version = evidence.get('version')
⋮----
items = evidence.get('items')
⋮----
seen = set()
normalized = []
⋮----
required = {'task_id', 'kind', 'source', 'version_or_revision', 'license', 'maintenance_signal', 'risks', 'notes'}
⋮----
task_id = item.get('task_id')
task = expected.get(task_id)
⋮----
risks = item.get('risks')
⋮----
kind = item['kind']
source = item['source']
````

## File: evolution_executor.py
````python
"""Consume an evolution request into a safe, machine-readable candidate work order.

This module does not execute discovered code or weaken gates. It turns a trusted
adaptation request into the next bounded factory-evolution job.
"""
⋮----
SUPPORTED_RESOURCE_KINDS = {
⋮----
REQUIRED_PROMOTION_GATES = {
⋮----
def _slug(value: str) -> str
⋮----
cleaned = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
⋮----
def validate_request(request: dict) -> dict
⋮----
gaps = request.get('gaps')
resources = request.get('resource_research')
gates = request.get('promotion_gates')
policy = request.get('candidate_policy')
⋮----
def build_work_order(request: dict, baseline_sha: str) -> dict
⋮----
request = validate_request(request)
⋮----
primary = request['gaps'][0]
gap_value = primary['value']
slug = _slug(gap_value)
digest = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:12]
candidate_id = f'{slug}-{digest}'
⋮----
research = []
⋮----
def consume(request_path: Path, out: Path, baseline_sha: str) -> dict
⋮----
request = json.loads(request_path.read_text())
work_order = build_work_order(request, baseline_sha)
⋮----
path = out / 'evolution-work-order.json'
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
⋮----
order = consume(Path(args.request), Path(args.out), args.baseline_sha)
````

## File: evolution_isolated_runner.py
````python
"""Materialize, execute and score validated evolution candidates in isolation.

Candidate Python/tests run only in the pinned Flutter container with networking
removed, a read-only workspace, dropped Linux capabilities and no production
credentials. Trusted host-side code creates detached worktrees, runs the protected
factory smoke on baseline and candidate with a scrubbed environment, and feeds the
resulting machine evidence to the deterministic promotion evaluator. This module
never pushes or merges candidate code.
"""
⋮----
class IsolatedRunError(RuntimeError): pass
SAFE_ENV={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/tmp/home','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1'}
def _run(args,*,cwd=None,timeout=300,env=None,check=False)
⋮----
result=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
⋮----
def _sha(value,label)
def _test_path(validated_candidate)
⋮----
paths=[item.get('path') for item in validated_candidate.get('files',[]) if isinstance(item,dict) and isinstance(item.get('path'),str) and item['path'].startswith('tests/test_')]
⋮----
def _materialize_candidate(root,validated_candidate)
⋮----
target=root/item['path']
⋮----
def _protected_hashes(root)
⋮----
result={}
⋮----
file=root/path
⋮----
def _docker_python(root,python_args,timeout=300)
⋮----
command=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','1024m','--cpus','2','--tmpfs','/tmp:rw,noexec,nosuid,size=256m','-e','HOME=/tmp/home','-e','LANG=C.UTF-8','-e','LC_ALL=C.UTF-8','-e','PYTHONDONTWRITEBYTECODE=1','-e','PYTHONUNBUFFERED=1','-v',str(root.resolve())+':/workspace:ro','-w','/workspace',IMAGE,'python3',*python_args]
⋮----
def _trusted_flutter_smoke(root,smoke_root,timeout=900)
⋮----
env=dict(SAFE_ENV); env['STUDIO_SMOKE_ROOT']=str(smoke_root)
⋮----
def _parse_unittest(output,returncode)
⋮----
match=re.search(r'Ran\s+(\d+)\s+tests?',output); count=int(match.group(1)) if match else 0; failures=0; errors=0; failed=re.search(r'FAILED\s*\(([^)]*)\)',output)
⋮----
if key=='failures': failures=int(value)
elif key=='errors': errors=int(value)
passed=returncode==0 and count>0 and failures==0 and errors==0
⋮----
def _candidate_test_result(root,commit_sha,test_file)
⋮----
result=_docker_python(root,['-m','unittest','discover','-s','tests','-p',Path(test_file).name,'-v']); parsed=_parse_unittest((result.stdout or '')+'\n'+(result.stderr or ''),result.returncode)
⋮----
def _copy_test_into_baseline(candidate_root,baseline_root,test_file)
⋮----
source=candidate_root/test_file
⋮----
target=baseline_root/test_file; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(source.read_bytes())
def _commit_candidate(candidate_root,baseline_sha,paths)
⋮----
_run(['git','add','--',*paths],cwd=candidate_root,check=True); env=dict(SAFE_ENV); env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']='ai-dev-server evolution'; env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']='evolution@localhost'
_run(['git','commit','--no-gpg-sign','-m','Validated autonomous evolution candidate'],cwd=candidate_root,env=env,check=True); sha=_run(['git','rev-parse','HEAD'],cwd=candidate_root,check=True).stdout.strip()
⋮----
def _is_reversible(candidate_root,baseline_sha): return _run(['git','rev-parse','HEAD^'],cwd=candidate_root).stdout.strip()==baseline_sha
def _capability_result(gap,assertions,passed)
def execute(repo_root,work_order,validated_candidate,out)
⋮----
baseline_sha=_sha(work_order.get('baseline_sha'),'Baseline')
⋮----
gap=validated_candidate.get('gap')
⋮----
assertions=validated_candidate.get('benchmark_assertions')
⋮----
temp=Path(tmp); baseline_root=temp/'baseline'; candidate_root=temp/'candidate'; _run(['git','worktree','add','--detach',str(baseline_root),baseline_sha],cwd=repo_root,check=True)
⋮----
_materialize_candidate(candidate_root,validated_candidate); paths=[item['path'] for item in validated_candidate['files']]; candidate_sha=_commit_candidate(candidate_root,baseline_sha,paths); reversible=_is_reversible(candidate_root,baseline_sha); test_file=_test_path(validated_candidate); _copy_test_into_baseline(candidate_root,baseline_root,test_file)
baseline_diff=_candidate_test_result(baseline_root,baseline_sha,test_file); candidate_diff=_candidate_test_result(candidate_root,candidate_sha,test_file); differential=evaluate_differential(work_order,validated_candidate,baseline_diff,candidate_diff); capability_passed=bool(differential.get('improvement_proved'))
braw=_docker_python(baseline_root,['-m','unittest','discover','-s','tests','-v']); craw=_docker_python(candidate_root,['-m','unittest','discover','-s','tests','-v']); btests=_parse_unittest((braw.stdout or '')+'\n'+(braw.stderr or ''),braw.returncode); ctests=_parse_unittest((craw.stdout or '')+'\n'+(craw.stderr or ''),craw.returncode)
bcompile=_docker_python(baseline_root,['-m','compileall','-q','studio','tests']).returncode==0; ccompile=_docker_python(candidate_root,['-m','compileall','-q','studio','tests']).returncode==0; bsmoke=_trusted_flutter_smoke(baseline_root,temp/'baseline-smoke'); csmoke=_trusted_flutter_smoke(candidate_root,temp/'candidate-smoke')
baseline={'version':1,'commit_sha':baseline_sha,'compile_passed':bcompile,'unit_tests':btests,'flutter_smoke_passed':bsmoke,'protected_hashes':_protected_hashes(baseline_root),'capability_benchmark':_capability_result(gap,assertions,False),'reversible':True}
candidate={'version':1,'commit_sha':candidate_sha,'compile_passed':ccompile,'unit_tests':ctests,'flutter_smoke_passed':csmoke,'protected_hashes':_protected_hashes(candidate_root),'capability_benchmark':_capability_result(gap,assertions,capability_passed),'reversible':reversible}
promotion=evaluate_promotion(work_order,baseline,candidate,differential); evidence={'version':2,'status':'isolated_benchmark_complete','candidate_id':work_order.get('candidate_id'),'baseline_sha':baseline_sha,'candidate_sha':candidate_sha,'network':'disabled_for_candidate_code','candidate_workspace':'read_only','candidate_capabilities':'dropped','credentials_exposed_to_candidate':False,'baseline':baseline,'candidate':candidate,'differential':differential,'promotion':promotion}
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('candidate'); parser.add_argument('--repo-root',default='.'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv); out=Path(args.out)
⋮----
order=json.loads(Path(args.work_order).read_text()); candidate=json.loads(Path(args.candidate).read_text()); evidence=execute(Path(args.repo_root),order,candidate,out); print(canonical({'status':evidence['status'],'promotion':evidence['promotion']['status']})); return 0
````

## File: evolution_pending.py
````python
"""Recover a durable content-bound GitHub evolution across runner restarts."""
⋮----
class PendingError(RuntimeError)
⋮----
def _candidate_prs(api, token, prefix)
⋮----
query = urllib.parse.urlencode({'state':'all','base':'main','per_page':100})
pulls = _request(api + '/pulls?' + query, token)
⋮----
def check(work_order: dict, token: str, repository: str) -> dict
⋮----
candidate_id = work_order.get('candidate_id'); gap = (work_order.get('primary_gap') or {}).get('value')
⋮----
prefix = _branch_prefix(gap, candidate_id); api = 'https://api.github.com/repos/' + repository
matches = _candidate_prs(api, token, prefix)
⋮----
refs = _request(api + '/git/matching-refs/heads/' + urllib.parse.quote(prefix, safe='/'), token)
⋮----
pr = matches[0]; branch = pr['head']['ref']; encoded_sha = branch[len(prefix):]; pr_sha = pr.get('head', {}).get('sha')
⋮----
state = 'promotion_merged_restart_required'
⋮----
ref = _request(api + '/git/ref/heads/' + urllib.parse.quote(branch, safe='/'), token, allow_404=True)
current_sha = ref.get('object', {}).get('sha') if isinstance(ref, dict) else None
⋮----
state = 'promotion_pending_merge'
⋮----
state = 'promotion_closed_without_merge'
⋮----
def main(argv=None)
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('--out',default='studio-output')
args=parser.parse_args(argv); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
⋮----
order=json.loads(Path(args.work_order).read_text())
result=check(order,os.environ.get('STUDIO_GITHUB_TOKEN',''),os.environ.get('GITHUB_REPOSITORY',''))
````

## File: evolution_persist.py
````python
"""Persist an approved local promotion as a content-bound GitHub branch and PR."""
⋮----
class PersistenceError(RuntimeError)
⋮----
def _request(url, token, method='GET', payload=None, allow_404=False)
⋮----
data = None if payload is None else canonical(payload).encode()
req = urllib.request.Request(url, data=data, method=method, headers={
⋮----
def _branch_prefix(gap, candidate_id)
⋮----
slug = re.sub(r'[^a-z0-9-]+', '-', gap.replace('_', '-')).strip('-')
identity = hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
⋮----
def _branch_name(gap, candidate_id, commit_sha)
⋮----
def _matching_refs(api, token, prefix)
⋮----
url = api + '/git/matching-refs/heads/' + urllib.parse.quote(prefix, safe='/')
refs = _request(url, token)
⋮----
expected_prefix = 'refs/heads/' + prefix
⋮----
def _existing_pr(api, token, owner, branch, commit_sha)
⋮----
query = urllib.parse.urlencode({'state': 'all', 'head': owner + ':' + branch, 'base': 'main', 'per_page': 20})
pulls = _request(api + '/pulls?' + query, token)
⋮----
matches = [pr for pr in pulls if isinstance(pr, dict) and pr.get('head', {}).get('sha') == commit_sha
⋮----
def _verify_local_promotion(root, applied, baseline_sha)
⋮----
candidate_id = applied['candidate_id']; gap = applied['gap']; candidate_sha = applied.get('candidate_sha')
⋮----
rollback_path = root / 'control/evolution_rollbacks' / (candidate_id + '.json')
registry_path = root / 'control/promoted_stages.json'
⋮----
rollback = json.loads(rollback_path.read_text()); registry = json.loads(registry_path.read_text())
⋮----
hashes = rollback.get('created_sha256'); paths = rollback.get('created_paths')
⋮----
path = (root / rel).resolve()
⋮----
entry = registry.get('stages', {}).get(gap) if isinstance(registry, dict) else None
⋮----
def persist(repo_root: Path, applied: dict, token: str, repository: str, baseline_sha: str)
⋮----
candidate_id = applied.get('candidate_id'); gap = applied.get('gap')
⋮----
root = repo_root.resolve(); rollback, registry = _verify_local_promotion(root, applied, baseline_sha)
stage = root / f'studio/{gap[:-3]}_stage.py'; implementation = root / f'studio/{gap}.py'
tests = root / f'tests/test_{gap}.py'; benchmark = root / f'tests/benchmarks/{gap}.json'
files = [registry, rollback, stage, implementation, tests, benchmark]
⋮----
api = 'https://api.github.com/repos/' + repository; owner = repository.split('/', 1)[0]
base_commit = _request(api + '/git/commits/' + baseline_sha, token)
base_tree = base_commit.get('tree', {}).get('sha') if isinstance(base_commit, dict) else None
⋮----
tree_entries = []
⋮----
rel = path.relative_to(root).as_posix()
blob = _request(api + '/git/blobs', token, 'POST', {'content': base64.b64encode(path.read_bytes()).decode(), 'encoding': 'base64'})
sha = blob.get('sha') if isinstance(blob, dict) else None
⋮----
tree = _request(api + '/git/trees', token, 'POST', {'base_tree': base_tree, 'tree': tree_entries})
tree_sha = tree.get('sha') if isinstance(tree, dict) else None
⋮----
prefix = _branch_prefix(gap, candidate_id); refs = _matching_refs(api, token, prefix)
⋮----
branch = refs[0]['ref'][len('refs/heads/'):]
encoded_sha = branch[len(prefix):]
current_sha = refs[0].get('object', {}).get('sha')
⋮----
existing_commit = _request(api + '/git/commits/' + encoded_sha, token)
existing_tree = existing_commit.get('tree', {}).get('sha') if isinstance(existing_commit, dict) else None
parents = existing_commit.get('parents') if isinstance(existing_commit, dict) else None
parent_shas = [item.get('sha') for item in parents] if isinstance(parents, list) else []
⋮----
number = _existing_pr(api, token, owner, branch, encoded_sha)
⋮----
commit = _request(api + '/git/commits', token, 'POST', {'message': f'Promote autonomous capability {gap}', 'tree': tree_sha, 'parents': [baseline_sha]})
commit_sha = commit.get('sha') if isinstance(commit, dict) else None
⋮----
branch = _branch_name(gap, candidate_id, commit_sha)
⋮----
existing_number = _existing_pr(api, token, owner, branch, commit_sha)
⋮----
pr = _request(api + '/pulls', token, 'POST', {
number = pr.get('number') if isinstance(pr, dict) else None
⋮----
def main(argv=None)
⋮----
parser = argparse.ArgumentParser(); parser.add_argument('applied'); parser.add_argument('--repo-root', default='.'); parser.add_argument('--out', default='studio-output')
args = parser.parse_args(argv); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
⋮----
applied = json.loads(Path(args.applied).read_text())
result = persist(Path(args.repo_root), applied, os.environ.get('STUDIO_GITHUB_TOKEN', ''), os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_SHA', ''))
````

## File: evolution_promotion.py
````python
"""Trusted application of an already benchmark-approved evolution candidate."""
⋮----
REGISTRY = Path('control/promoted_stages.json')
ROLLBACK_DIR = Path('control/evolution_rollbacks')
⋮----
class PromotionError(RuntimeError)
⋮----
def _sha(value, label)
⋮----
def _candidate_digest(candidate)
⋮----
files = candidate.get('files')
⋮----
payload = {
⋮----
def _load_registry(root)
⋮----
path = root / REGISTRY
⋮----
value = json.loads(path.read_text())
⋮----
def _atomic_write(path, content)
⋮----
temp = Path(handle.name)
⋮----
def apply(repo_root, work_order, candidate, benchmark, supplied_promotion)
⋮----
root = repo_root.resolve()
⋮----
candidate_id = work_order.get('candidate_id')
gap = (work_order.get('primary_gap') or {}).get('value')
baseline_sha = _sha(work_order.get('baseline_sha'), 'Baseline')
⋮----
digest = _candidate_digest(candidate)
⋮----
recomputed = evaluate_promotion(work_order, benchmark.get('baseline'), benchmark.get('candidate'), benchmark.get('differential'))
⋮----
candidate_sha = _sha(supplied_promotion.get('candidate_sha'), 'Candidate')
⋮----
expected = expected_paths(gap)
⋮----
by_path = {item.get('path'): item.get('content') for item in files if isinstance(item, dict)}
⋮----
registry = _load_registry(root)
stages = dict(registry['stages'])
⋮----
existing = stages[gap]
⋮----
collisions = [path for path in expected.values() if (root / path).exists()]
⋮----
previous_registry = canonical(registry) + '\n'
file_hashes = {path: hashlib.sha256(content.encode()).hexdigest() for path, content in sorted(by_path.items())}
rollback = {
⋮----
written = []
⋮----
target = (root / path).resolve()
⋮----
new_registry = {'version': 1, 'stages': stages}
⋮----
def main(argv=None)
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
out = Path(args.out)
⋮----
order = json.loads(Path(args.work_order).read_text())
candidate = json.loads(Path(args.candidate).read_text())
benchmark = json.loads(Path(args.benchmark).read_text())
promotion = json.loads(Path(args.promotion).read_text())
result = apply(Path(args.repo_root), order, candidate, benchmark, promotion)
````

## File: evolution_research.py
````python
"""Trusted bounded research adapters for factory evolution candidates.

No downloaded source code is executed. Network access is limited to explicit HTTPS
hosts and bounded response sizes. Known capability research resolves to official
platform documentation; package/GitHub adapters retrieve metadata only.
"""
⋮----
MAX_RESPONSE_BYTES = 256 * 1024
TIMEOUT_SECONDS = 15
USER_AGENT = 'ai-dev-server-evolution-research/1'
⋮----
NETWORK_HOSTS = {
⋮----
KNOWN_DOCS = (
⋮----
PACKAGE_HINTS = {
⋮----
class ResearchBlocked(RuntimeError)
⋮----
@dataclass(frozen=True)
class FetchResult
⋮----
requested_url: str
final_url: str
status: int
headers: dict[str, str]
body: bytes
⋮----
@property
    def sha256(self) -> str
⋮----
class _SafeRedirect(HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
⋮----
def _validate_network_url(url: str) -> str
⋮----
parsed = urlsplit(url)
port = parsed.port
⋮----
host = parsed.hostname.lower()
⋮----
headers = {'User-Agent': USER_AGENT, 'Accept': 'text/html,application/json,text/plain;q=0.9,*/*;q=0.1'}
⋮----
request = Request(url, headers=headers, method='GET')
⋮----
final_url = response.geturl()
⋮----
content_type = (response.headers.get('Content-Type') or '').lower()
⋮----
body = response.read(max_bytes + 1)
⋮----
normalized_headers = {str(k).lower(): str(v)[:500] for k, v in response.headers.items()}
⋮----
def _title(body: bytes) -> str
⋮----
text = body.decode('utf-8', errors='replace')
match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
⋮----
value = re.sub(r'<[^>]+>', ' ', match.group(1))
⋮----
def _doc_source(task: dict) -> str
⋮----
query = task['query'].lower()
kind = task['kind']
⋮----
def _provenance(result: FetchResult) -> dict
⋮----
def _official_item(task: dict, fetcher) -> tuple[dict, list[dict]]
⋮----
url = _doc_source(task)
result = fetcher(url)
revision = result.headers.get('etag') or result.headers.get('last-modified') or result.sha256[:16]
title = _title(result.body)
⋮----
def _package_hint(query: str) -> str | None
⋮----
lower = query.lower()
⋮----
def _github_headers() -> dict[str, str]
⋮----
headers = {'Accept': 'application/vnd.github+json'}
token = os.environ.get('STUDIO_GITHUB_TOKEN')
⋮----
def _github_repo_from_url(value: object) -> tuple[str, str] | None
⋮----
parsed = urlsplit(value)
⋮----
parts = [part for part in parsed.path.split('/') if part]
⋮----
def _fetch_json(result: FetchResult) -> dict
⋮----
value = json.loads(result.body.decode('utf-8'))
⋮----
def _package_item(task: dict, fetcher) -> tuple[dict, list[dict]]
⋮----
package = _package_hint(task['query'])
provenance: list[dict] = []
⋮----
search = fetcher('https://pub.dev/api/search?q=' + quote_plus(task['query']))
⋮----
payload = _fetch_json(search)
packages = payload.get('packages')
⋮----
package = packages[0].get('package')
⋮----
detail = fetcher('https://pub.dev/api/packages/' + package)
⋮----
payload = _fetch_json(detail)
latest = payload.get('latest')
⋮----
version = latest.get('version')
pubspec = latest.get('pubspec')
⋮----
published = latest.get('published') if isinstance(latest.get('published'), str) else ''
repository = pubspec.get('repository') or pubspec.get('homepage')
license_value = 'license_requires_repository_review'
maintenance = published or 'latest_release_available'
risks = ['dependency_must_be_pinned_and_regression_tested']
notes = [f'Package: {package}.']
⋮----
repo = _github_repo_from_url(repository)
⋮----
meta = fetcher(f'https://api.github.com/repos/{owner}/{name}', extra_headers=_github_headers())
⋮----
repo_payload = _fetch_json(meta)
license_obj = repo_payload.get('license')
⋮----
license_value = license_obj['spdx_id'][:500]
pushed = repo_payload.get('pushed_at')
archived = bool(repo_payload.get('archived'))
⋮----
maintenance = f'pushed_at={pushed}; archived={str(archived).lower()}'
⋮----
html_url = repo_payload.get('html_url')
⋮----
combined_hash = hashlib.sha256(''.join(p['content_sha256'] for p in provenance).encode()).hexdigest()
⋮----
def _github_item(task: dict, fetcher) -> tuple[dict, list[dict]]
⋮----
url = 'https://api.github.com/search/repositories?q=' + quote_plus(task['query']) + '&sort=updated&order=desc&per_page=5'
result = fetcher(url, extra_headers=_github_headers())
payload = _fetch_json(result)
items = payload.get('items')
⋮----
candidates = [item for item in items if isinstance(item, dict) and not item.get('archived')]
⋮----
repo = candidates[0]
source = repo.get('html_url')
⋮----
license_obj = repo.get('license')
license_value = license_obj.get('spdx_id') if isinstance(license_obj, dict) else None
pushed = repo.get('pushed_at') if isinstance(repo.get('pushed_at'), str) else ''
stars = repo.get('stargazers_count') if isinstance(repo.get('stargazers_count'), int) else 0
default_branch = repo.get('default_branch') if isinstance(repo.get('default_branch'), str) else 'unknown'
⋮----
def _run_version(executable: str, args: list[str]) -> str
⋮----
path = shutil.which(executable)
⋮----
result = subprocess.run([path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
⋮----
def _device_item(task: dict) -> tuple[dict, list[dict]]
⋮----
adb = _run_version('adb', ['version'])
emulator = _run_version('emulator', ['-version'])
⋮----
fingerprint = json.dumps({'adb': adb, 'emulator': emulator}, sort_keys=True).encode()
digest = hashlib.sha256(fingerprint).hexdigest()
⋮----
def research_task(task: dict, fetcher=fetch_url) -> tuple[dict, list[dict]]
⋮----
def execute(work_order: dict, out: Path, fetcher=fetch_url) -> dict
⋮----
tasks = work_order.get('research_tasks') if isinstance(work_order, dict) else None
⋮----
candidate_id = work_order.get('candidate_id')
⋮----
items = []
provenance = []
⋮----
envelope = {'version': 2, 'candidate_id': candidate_id, 'items': items}
normalized = validate_evidence(work_order, envelope)
⋮----
provenance_payload = {
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
out = Path(args.out)
⋮----
work_order = json.loads(Path(args.work_order).read_text())
result = execute(work_order, out)
````

## File: evolution_rollback.py
````python
"""Trusted rollback for previously promoted evolution candidates."""
⋮----
class RollbackError(RuntimeError)
⋮----
def _atomic_write(path: Path, content: str) -> None
⋮----
temp = Path(handle.name)
⋮----
def _load_json(path: Path, label: str) -> dict
⋮----
value = json.loads(path.read_text())
⋮----
def rollback(repo_root: Path, candidate_id: str) -> dict
⋮----
root = repo_root.resolve()
⋮----
record_path = root / ROLLBACK_DIR / (candidate_id + '.json')
record = _load_json(record_path, 'Rollback record')
required = {'version','candidate_id','gap','baseline_sha','candidate_sha','created_paths','created_sha256','registry_before','registry_sha256_before'}
⋮----
gap = record.get('gap')
⋮----
paths = record.get('created_paths')
hashes = record.get('created_sha256')
⋮----
previous_registry = record.get('registry_before')
⋮----
previous_text = canonical(previous_registry) + '\n'
⋮----
registry_path = root / REGISTRY
current = _load_json(registry_path, 'Promoted-stage registry')
entry = (current.get('stages') or {}).get(gap) if isinstance(current.get('stages'), dict) else None
⋮----
targets = []
⋮----
target = (root / relative).resolve()
⋮----
applied = {
⋮----
def main(argv=None)
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
out = Path(args.out)
⋮----
result = rollback(Path(args.repo_root), args.candidate_id)
````

## File: evolution_stage_runner.py
````python
"""Execute a promoted QA stage with production credentials removed."""
⋮----
SECRET_ENV_PREFIXES = ('STUDIO_GITHUB_TOKEN', 'GITHUB_TOKEN', 'GH_TOKEN', 'STUDIO_API_KEY', 'NVIDIA_NIM_API_KEY')
⋮----
class PromotedStageError(RuntimeError)
⋮----
def scrubbed_env(source=None)
⋮----
env = dict(os.environ if source is None else source)
⋮----
upper = key.upper()
⋮----
def run(script: str, args: list[str], timeout: float | None = None)
⋮----
path = Path(script)
⋮----
def main(argv=None)
⋮----
argv = list(sys.argv[1:] if argv is None else argv)
⋮----
result = run(argv[0], argv[1:])
````

## File: evolution_synthesis.py
````python
"""Synthesize a missing factory QA capability inside the trusted candidate envelope."""
⋮----
SYSTEM='''You are generating ONE missing trusted QA capability for the mobile factory.
def _context(order,research)
⋮----
primary=order.get('primary_gap',{}); gap=primary.get('value') if isinstance(primary,dict) else None
⋮----
paths=expected_paths(gap); compact=[]
⋮----
def synthesize(order,research,api=None,model=None)
⋮----
messages=[{'role':'system','content':SYSTEM},{'role':'user','content':_context(order,research)}]
⋮----
selected=model or os.environ.get('STUDIO_CODE_MODEL') or os.environ.get('STUDIO_MODEL','nvidia/nemotron-3-super-120b-a12b')
⋮----
params={'model':selected,'stream':False,'max_tokens':16000,'messages':messages}
⋮----
response=api.call('POST','/chat/completions',params)
⋮----
try: providers=load_providers(prefer_free=True)
⋮----
providers=candidates_for('implementation',providers=providers)
⋮----
response=None; last_error=None
⋮----
selected=model or provider.model_for('implementation')
routed_api=API(provider.base,provider.key)
⋮----
response=routed_api.call('POST','/chat/completions',params)
⋮----
last_error=exc; continue
⋮----
choice=response['choices'][0]
⋮----
raw=choice['message']['content'].strip()
if raw.startswith('```'): raw=raw.split('\n',1)[1].rsplit('```',1)[0]
candidate=json.loads(raw)
⋮----
def consume(order_path:Path,research_path:Path,out:Path,api=None,model=None)
⋮----
order=json.loads(order_path.read_text()); research=json.loads(research_path.read_text()); validated=synthesize(order,research,api=api,model=model); out.mkdir(parents=True,exist_ok=True); (out/'evolution-candidate.json').write_text(canonical(validated)+'\n'); return validated
def main(argv=None)
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('work_order'); parser.add_argument('research'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv); out=Path(args.out)
try: result=consume(Path(args.work_order),Path(args.research),out)
````

## File: execution_budget.py
````python
"""Adaptive execution budgeting for bounded autonomous project loops."""
⋮----
@dataclass(frozen=True)
class ExecutionBudget
⋮----
max_work_passes: int
agent_limit: int
reserve_seconds: int
mode: str
⋮----
def as_dict(self) -> dict
⋮----
"""Choose conservative work depth from time and recent verification evidence."""
remaining = None if remaining_seconds is None else max(0.0, float(remaining_seconds))
previous_passed = bool(isinstance(previous_verification, dict) and previous_verification.get("passed") is True)
⋮----
predicted_work_passes = 2 if predicted_work_passes is None else max(1, min(2, int(predicted_work_passes)))
predicted_agent_limit = meta_agent_limit if predicted_agent_limit is None else max(0, min(meta_agent_limit, int(predicted_agent_limit)))
predicted_reserve_seconds = 90 if predicted_reserve_seconds is None else max(60, min(900, int(predicted_reserve_seconds)))
````

## File: execution_checkpoint.py
````python
"""Integrity-sealed execution checkpoints for resumable autonomous work."""
⋮----
VERSION = 1
ALLOWED_PHASES = {"restored", "planned", "implemented", "verified", "published", "complete"}
⋮----
class ExecutionCheckpointError(ValueError)
⋮----
def _canonical(value: dict) -> bytes
⋮----
def _seal(value: dict) -> dict
⋮----
item = dict(value)
⋮----
def new(project_id: str, engine: str, base_sha: str) -> dict
⋮----
def validate(value: dict) -> dict
⋮----
digest = value.get("sha256")
⋮----
unsigned = dict(value)
⋮----
last = value.get("last_verification")
⋮----
item = dict(checkpoint)
⋮----
def save(path: Path, checkpoint: dict) -> None
⋮----
path = Path(path)
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
````

## File: existing_project.py
````python
"""Plan and materialize a bounded existing mobile repository snapshot.

GitHub transport stays outside this module. The planner accepts only trusted tree
metadata and uses project_engine policy to decide what may enter the model workspace.
"""
⋮----
MAX_TREE_ENTRIES = 1200
MAX_TEXT_FILE_BYTES = 600_000
MAX_TOTAL_BYTES = 5_000_000
⋮----
class ExistingProjectError(ValueError)
⋮----
def plan(tree: dict, expected_engine: str | None = None) -> dict
⋮----
entries = tree.get('tree')
⋮----
blob_paths = [item.get('path') for item in entries
⋮----
engine = infer(blob_paths).name
⋮----
selected = []
total = 0
⋮----
path = item.get('path'); mode = item.get('mode'); sha = item.get('sha'); size = item.get('size', 0)
⋮----
def materialize(root: Path, import_plan: dict, fetch_blob) -> None
⋮----
root = root.resolve()
files = import_plan.get('files') if isinstance(import_plan, dict) else None
⋮----
prepared = []
⋮----
target = (root / item['path']).resolve()
⋮----
blob = fetch_blob(item['sha'])
⋮----
content = base64.b64decode(blob['content'], validate=False)
text = content.decode('utf-8')
````

## File: fault_injection_smoke.py
````python
"""Deterministic fail-closed resilience smoke test."""
⋮----
def main() -> int
⋮----
results = {}
⋮----
# Provider outage must fail closed after bounded retries.
api = API("https://provider.invalid/v1", "test-token")
transient = urllib.error.HTTPError("https://provider.invalid", 503, "busy", {}, None)
⋮----
root = Path(td)
⋮----
health = root / "provider-health.json"
⋮----
checkpoint_path = root / "checkpoint.json"
checkpoint = new_checkpoint("demo", "generic", "a" * 40)
⋮----
tampered = json.loads(checkpoint_path.read_text())
⋮----
durable_path = root / "durable-state.json"
⋮----
workflow_path = root / "workflow-checkpoints.json"
lease_path = root / "task-leases.json"
⋮----
key = operation_key("fault-injection", {"step": "model"})
⋮----
controller = RunCostController(total_budget_seconds=1000, max_model_calls=20)
⋮----
adaptation = new_capability_state("demo", "image_assets", "candidate:x")
⋮----
review = {
class FakeGitHub
⋮----
def get(self, path)
⋮----
passed = all(results.values())
out = Path("studio-output/fault-injection")
````

## File: file_lock.py
````python
"""Small inter-process advisory lock for local state files."""
⋮----
except ImportError:  # pragma: no cover - studio runners are Linux
fcntl = None
⋮----
@contextmanager
def exclusive(path: Path, *, timeout_seconds: float = 10.0, poll_seconds: float = 0.05)
⋮----
"""Serialize writers using a sibling .lock file."""
⋮----
path = Path(path)
⋮----
lock_path = path.with_name(path.name + ".lock")
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
deadline = time.monotonic() + max(0.0, float(timeout_seconds))
acquired = False
⋮----
acquired = True
````

## File: fleet_capacity.py
````python
"""Build a global capacity plan from the live fleet and configured providers."""
⋮----
DEFAULT_MAX_TOKENS_PER_MODEL_CALL = 16_000
⋮----
def _runtime_state(project_out: Path) -> dict
⋮----
path = project_out / ".autonomy" / "runtime-state.json"
⋮----
value = load_recovering(path)
⋮----
dashboard = collect(root)
health = {row["id"]: row for row in dashboard.get("projects", [])}
rows = []
⋮----
project_id = str(request.get("id") or "").strip()
⋮----
current = health.get(project_id, {})
runtime = _runtime_state(root / project_id)
⋮----
status = (
phase = (
max_calls = max(1, int(request.get("max_calls", 12)))
explicit_tokens = request.get("capacity_request_tokens")
⋮----
requested_tokens = max_calls * DEFAULT_MAX_TOKENS_PER_MODEL_CALL
⋮----
requested_tokens = max(1, int(explicit_tokens))
⋮----
usage = (ledger_usage or {}).get(project_id, {})
committed = max(0, int(usage.get("committed_tokens", 0) or 0))
previous_rows = (
previous_envelope = next(
pressure = (
verified_efficiency_multiplier = efficiency_multiplier(
worker_reliability_multiplier = reliability_multiplier(
reliability_project = (
efficiency_project = (
predicted_success_probability = max(
stagnation = (
stagnation_multiplier = max(
capacity_paused = bool(stagnation.get("pause", False))
recovery = {
⋮----
recovery_context = {
recovery = evaluate_recovery(
⋮----
capacity_paused = False
⋮----
def _preemption_evidence(root: Path, projects: list[dict]) -> dict
⋮----
evidence = {}
⋮----
project_id = row["id"]
checkpoint_path = root / project_id / ".autonomy" / "execution-checkpoint.json"
item = {"checkpoint_valid": False, "checkpoint_phase": None}
⋮----
checkpoint = load_execution_checkpoint(checkpoint_path)
⋮----
checkpoint = None
⋮----
item = {
⋮----
def _capacity_band(value: int | None, *, unmetered: bool = False) -> str
⋮----
amount = max(0, int(value))
⋮----
quota_raw = os.environ.get("STUDIO_PROVIDER_MONTHLY_QUOTA_PATH", "")
quota_path = Path(quota_raw) if quota_raw else None
quota_data = (
⋮----
capacities = []
⋮----
available = None
⋮----
available = quota_status(
reserved = max(
available = max(0, int(available or 0) - reserved)
⋮----
root = Path(root)
request_dir = Path(request_dir)
plan_path = root / "capacity-plan.json"
⋮----
previous_plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
⋮----
previous_plan = {}
ledger = ledger_detailed_snapshot(root / "capacity-ledger.json")
efficiency = summarize_capacity_efficiency(root / "capacity-efficiency.json")
stagnation = summarize_stagnation(efficiency)
⋮----
liveness = json.loads((root / "worker-liveness.json").read_text(encoding="utf-8"))
⋮----
liveness = {}
reliability = summarize_worker_reliability(liveness)
providers = _provider_rows(
provider_context = [
projects = _project_rows(
report = allocate(
admission = decide_global_admission(report["projects"])
active_leases = preemption_leases(load_capacity_ledger(root / "capacity-ledger.json"))
⋮----
decisions = admission.get("decisions", [])
⋮----
lease = active_leases.get(decision.get("id"))
⋮----
admission_by_id = {
⋮----
decision = admission_by_id.get(row["id"], {})
⋮----
preemption_evidence = _preemption_evidence(root, report["projects"])
⋮----
report = plan(
target = Path(output) if output is not None else root / "capacity-plan.json"
````

## File: fleet_daemon.py
````python
"""Long-running bounded operations loop for AI Dev Server fleets."""
⋮----
MIN_INTERVAL_SECONDS = 30.0
⋮----
root = Path(root)
history = Path(history) if history is not None else root / "fleet-metrics.json"
⋮----
dashboard = collect(root)
metric_row = snapshot(root)
metrics = append_metrics(history, metric_row)
regression = evaluate_regression(history)
maintenance = maintain(root)
worker_liveness = classify_worker_liveness(root)
capacity = persist_capacity_plan(root, request_dir)
preemption = apply_preemption(
⋮----
capacity_ledger = capacity_ledger_snapshot(root / "capacity-ledger.json")
⋮----
supervisor = apply_supervisor(
⋮----
interval = max(MIN_INTERVAL_SECONDS, float(interval_seconds))
rows = []
count = 0
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server fleet operations daemon")
⋮----
args = parser.parse_args(argv)
⋮----
report = tick(
````

## File: fleet_dashboard.py
````python
"""Aggregate health and activity for all autonomous project outputs."""
⋮----
def collect(root: Path | str = "studio-output") -> dict
⋮----
root = Path(root)
projects = []
⋮----
report = inspect(path)
⋮----
architecture = summarize_architecture_learning(root)
eligible = [
healthy = sum(1 for item in projects if item["status"] == "healthy")
degraded = len(projects) - healthy
running = sum(1 for item in projects if item.get("runtime_status") == "running")
complete = sum(1 for item in projects if item.get("runtime_status") == "complete")
blocked = sum(1 for item in projects if item.get("runtime_status") in {"blocked", "human_action_required"})
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server fleet dashboard")
⋮----
args = parser.parse_args(argv)
report = collect(args.root)
````

## File: fleet_maintenance.py
````python
"""Safe maintenance for long-running autonomous project outputs."""
⋮----
TMP_SUFFIXES = (".tmp", ".partial")
⋮----
def _cleanup_temps(root: Path) -> dict
⋮----
removed = 0
bytes_removed = 0
⋮----
size = path.stat().st_size
⋮----
def maintain_project(project_out: Path) -> dict
⋮----
autonomy = project_out / ".autonomy"
result = {
⋮----
def run(root: Path | str = "studio-output") -> dict
⋮----
root = Path(root)
projects = []
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server fleet maintenance")
⋮----
args = parser.parse_args(argv)
report = run(args.root)
````

## File: fleet_metrics.py
````python
"""Persist bounded fleet health snapshots for trend analysis."""
⋮----
MAX_SNAPSHOTS = 512
⋮----
def load(path: Path) -> list[dict]
⋮----
path = Path(path)
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
rows = data.get("snapshots")
⋮----
def snapshot(root: Path | str = "studio-output", *, ts: float | None = None) -> dict
⋮----
report = collect(root)
summary = dict(report["summary"])
⋮----
architecture = report.get("architecture_learning") or {}
⋮----
top = architecture.get("top_recommendations") or []
⋮----
value = top[0].get("success_rate")
⋮----
def append(path: Path, row: dict) -> dict
⋮----
rows = load(path)
⋮----
rows = rows[-MAX_SNAPSHOTS:]
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Record AI Dev Server fleet metrics")
⋮----
args = parser.parse_args(argv)
result = append(Path(args.history), snapshot(args.root))
````

## File: fleet_regression.py
````python
"""Detect fleet health regressions between the two latest snapshots."""
⋮----
def compare(previous: dict, current: dict) -> dict
⋮----
regressions = []
⋮----
def evaluate(path: Path | str) -> dict
⋮----
rows = load(Path(path))
⋮----
result = compare(rows[-2], rows[-1])
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Detect AI Dev Server fleet regressions")
⋮----
args = parser.parse_args(argv)
report = evaluate(args.history)
````

## File: fleet_supervisor_apply.py
````python
"""Apply bounded supervisor restart decisions to recoverable autonomous projects."""
⋮----
DEFAULT_MAX_RESTARTS = 2
⋮----
def _capacity_admission(root: Path, project_id: str) -> dict | None
⋮----
path = root / "capacity-plan.json"
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
rows = value.get("projects") if isinstance(value, dict) else None
⋮----
admission = item.get("admission")
⋮----
root = Path(root)
request_dir = Path(request_dir)
decisions = plan(root)
projects = {row["id"]: row for row in matrix(request_dir)}
results = []
restarted = 0
deadline = clock() + 70 * 60
baseline_sha = os.environ.get("GITHUB_SHA") or os.environ.get("CIRCLE_SHA1")
⋮----
project_id = decision["id"]
action = decision["action"]
row = {
⋮----
admission = _capacity_admission(root, project_id)
⋮----
project = projects.get(project_id)
⋮----
result = _run_project_for_queue(
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Apply AI Dev Server supervisor decisions")
⋮----
args = parser.parse_args(argv)
report = execute(
````

## File: fleet_supervisor.py
````python
"""Deterministic supervisor decisions for autonomous project runtimes."""
⋮----
RESTARTABLE_RUNTIME = {"running", "deferred", "failed"}
NON_RESTARTABLE_RUNTIME = {"complete", "human_action_required", "blocked"}
⋮----
def plan(root: Path | str = "studio-output") -> dict
⋮----
dashboard = collect(root)
actions = []
⋮----
runtime = project.get("runtime_status")
errors = list(project.get("errors") or [])
⋮----
action = "none"
reason = "healthy"
⋮----
action = "inspect"
reason = "terminal_or_human_state"
⋮----
action = "quarantine"
reason = "state_integrity_failure"
⋮----
action = "restart"
reason = "recoverable_degradation"
⋮----
reason = "unknown_state"
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server supervisor plan")
⋮----
args = parser.parse_args(argv)
report = plan(args.root)
````

## File: flutter_workspace.py
````python
"""Strict Flutter editable-workspace snapshots for isolated repair candidates."""
⋮----
MAX_BYTES = 2_000_000
TRANSIENT_PATHS = (
⋮----
def snapshot(root: Path) -> dict[str, str]
⋮----
root = root.resolve()
result: dict[str, str] = {}
total = 0
⋮----
rel = path.relative_to(root).as_posix()
⋮----
text = path.read_text(encoding="utf-8")
⋮----
def delta(root: Path, before: dict[str, str]) -> dict
⋮----
after = snapshot(root)
deleted = sorted(set(before) - set(after))
⋮----
changed = [
⋮----
normalized = patch_check({"files": changed})
⋮----
def restore(root: Path, before: dict[str, str]) -> None
⋮----
current = snapshot(root)
⋮----
path = root / rel
⋮----
def clean_transients(root: Path) -> None
````

## File: free_capacity_recommendations.py
````python
"""Discover self-hosted/open-source capacity sources from star-list."""
⋮----
_NEEDS = [
⋮----
_PREFERRED_REPOS = {
⋮----
def discover(out: Path) -> dict
⋮----
out = Path(out)
⋮----
result = scan(_NEEDS, self_hosted=True, top=24)
matches = result.get("matches") if isinstance(result, dict) else []
matches = matches if isinstance(matches, list) else []
ranked = []
⋮----
row = dict(item)
repo = row.get("repo")
⋮----
payload = {
````

## File: full_gate_cache.py
````python
"""Strict cache for successful full candidate validation only."""
⋮----
SCHEMA = 1
MAX_ENTRIES = 128
⋮----
FULL_GATE_CONTRACT = [
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_FULL_GATE_CACHE_PATH", "")
⋮----
def _hash_json(value) -> str
⋮----
def _native_fingerprint(root: Path) -> str
⋮----
rows = []
⋮----
base = root / folder
⋮----
rel = path.relative_to(root).as_posix()
⋮----
def validation_key(root: Path, *, app_name: str, journeys: list[dict]) -> str
⋮----
root = root.resolve()
template = Path(__file__).with_name("visual_test.dart")
template_hash = (
payload = {
⋮----
def load() -> dict
⋮----
path = _path()
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
entries = data.get("entries")
⋮----
def save(entries: dict) -> None
⋮----
merged = load()
⋮----
clean = [
clean_entries = dict(clean)
⋮----
def hit(entries: dict, key: str) -> bool
⋮----
row = entries.get(key)
⋮----
def record_success(entries: dict, key: str) -> None
````

## File: generic_capability_isolated_validation.py
````python
"""Isolated validation for synthesized generic capability candidates."""
⋮----
class IsolatedCapabilityValidationError(RuntimeError)
⋮----
FORBIDDEN_IMPORTS={"socket","ctypes","subprocess"}
FORBIDDEN_CALLS={"eval","exec","compile","__import__","open","os.system","os.popen"}
PROVIDER_RE=re.compile(r"studio\.capabilities\.([a-z][a-z0-9_]{2,120})")
⋮----
def _canon(value)
⋮----
def _seal(value)
⋮----
def _call_name(node)
⋮----
target=node.func
⋮----
parts=[]
⋮----
target=target.value
⋮----
def _static_check(source,label)
⋮----
tree=ast.parse(source,filename=label)
⋮----
name=_call_name(node)
⋮----
def _docker(root,args,timeout=180)
⋮----
cmd=[
result=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
⋮----
def _test_count(output)
⋮----
match=re.search(r"Ran\s+(\d+)\s+tests?",output)
⋮----
def _proof(kind,candidate_sha,passed,**extra)
⋮----
value={"kind":kind,"candidate_sha256":candidate_sha,"passed":bool(passed),**extra}
⋮----
def validate_in_isolation(envelope,repo_root=Path("."))
⋮----
candidate=envelope["candidate"]
provider=candidate.get("provider")
match=PROVIDER_RE.fullmatch(provider) if isinstance(provider,str) else None
⋮----
implementation=candidate.get("implementation")
tests=candidate.get("tests")
⋮----
candidate_sha=envelope["candidate_sha256"]
⋮----
root=Path(td)
module=match.group(1)
⋮----
baseline_count=_test_count(baseline_output)
⋮----
candidate_count=_test_count(candidate_output)
⋮----
targeted_passed=(compile_rc==0 and candidate_rc==0 and candidate_count>0)
differential_passed=(baseline_rc!=0 and candidate_rc==0 and candidate_count>0)
targeted=_proof(
benchmark=_proof(
⋮----
repo_root=Path(repo_root)
⋮----
regression=_proof(
validation=validate_candidate(envelope,targeted,benchmark,regression)
report={
⋮----
def validate_isolated_validation_result(value)
⋮----
required={
⋮----
report_digest=value.get("report_sha256")
unsigned_report=dict(value); unsigned_report.pop("report_sha256",None)
⋮----
candidate_id=value.get("candidate_id")
⋮----
sha=value.get("candidate_sha256")
⋮----
proofs={}
⋮----
proof=value.get(key)
⋮----
digest=proof.get("evidence_sha256")
unsigned=dict(proof); unsigned.pop("evidence_sha256",None)
⋮----
benchmark=proofs["benchmark"]
score=benchmark.get("score")
baseline_score=benchmark.get("baseline_score")
⋮----
validation=value.get("validation")
⋮----
decision=validation.get("status")
⋮----
expected_evidence={
all_passed=all(proof.get("passed") is True for proof in proofs.values())
⋮----
failed_gate=validation.get("failed_gate")
⋮----
expected_benchmark="passed" if proofs["benchmark"].get("passed") is True else "failed"
expected_regression="passed" if proofs["regression"].get("passed") is True else "failed"
````

## File: generic_capability_persist.py
````python
"""Persist a validated generic capability candidate to a dedicated GitHub PR."""
⋮----
SHA40=re.compile(r"[0-9a-f]{40}")
SHA64=re.compile(r"[0-9a-f]{64}")
NAME=re.compile(r"[a-z][a-z0-9_.-]{2,80}")
⋮----
class GenericCapabilityPersistError(RuntimeError): pass
⋮----
def _slug(name)
⋮----
def _prefix(capability,candidate_id)
⋮----
ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:12]
⋮----
def _paths(capability,candidate_id)
⋮----
slug=_slug(capability)
ident=hashlib.sha256(candidate_id.encode()).hexdigest()[:16]
⋮----
def _exact_refs(github,prefix)
⋮----
refs=github.get("/git/matching-refs/heads/"+prefix)
⋮----
expected="refs/heads/"+prefix
⋮----
def _existing_pr(github,branch,commit_sha)
⋮----
parts=github.repo.strip("/").split("/")
⋮----
query=urllib.parse.urlencode({"state":"all","head":parts[1]+":"+branch,"base":"main","per_page":20})
pulls=github.get("/pulls?"+query)
⋮----
matches=[p for p in pulls if isinstance(p,dict) and p.get("head",{}).get("ref")==branch and p.get("head",{}).get("sha")==commit_sha]
⋮----
def persist(github,candidate_envelope,validation_report,handoff,baseline_sha)
⋮----
candidate_envelope=validate_candidate_envelope(candidate_envelope)
validation_report=validate_isolated_validation_result(validation_report)
⋮----
cid=candidate_envelope["candidate_id"]; digest=candidate_envelope["candidate_sha256"]; payload=candidate_envelope["candidate"]
capability=payload.get("capability"); provider=payload.get("provider")
⋮----
implementation=payload.get("implementation"); tests=payload.get("tests")
⋮----
paths=_paths(capability,cid)
base=github.get("/git/commits/"+baseline_sha)
base_tree=base.get("tree",{}).get("sha") if isinstance(base,dict) else None
⋮----
baseline_tree=github.get("/git/trees/"+base_tree+"?recursive=1")
existing_paths={x.get("path") for x in baseline_tree.get("tree",[]) if isinstance(x,dict)} if isinstance(baseline_tree,dict) else set()
⋮----
evidence={
entries=[
tree=github.call("POST",github.repo+"/git/trees",{"base_tree":base_tree,"tree":entries})
tree_sha=tree.get("sha") if isinstance(tree,dict) else None
⋮----
prefix=_prefix(capability,cid)
refs=_exact_refs(github,prefix)
⋮----
branch=refs[0]["ref"][len("refs/heads/"):]
head=refs[0].get("object",{}).get("sha")
encoded=branch[len(prefix):]
⋮----
commit=github.get("/git/commits/"+head)
parents=[x.get("sha") for x in commit.get("parents",[])] if isinstance(commit,dict) else []
⋮----
number=_existing_pr(github,branch,head)
⋮----
commit=github.call("POST",github.repo+"/git/commits",{"message":"Persist validated capability candidate: "+capability,"tree":tree_sha,"parents":[baseline_sha]})
commit_sha=commit.get("sha") if isinstance(commit,dict) else None
⋮----
branch=prefix+commit_sha
⋮----
pr=github.call("POST",github.repo+"/pulls",{
number=pr.get("number") if isinstance(pr,dict) else None
````

## File: generic_capability_synthesis.py
````python
"""Model-backed synthesis for generic capability candidates.

The model output is data only. Synthesized code is never imported, executed,
promoted, registered, or written into the trusted provider namespace here.
"""
⋮----
SYSTEM = """Synthesize ONE missing internal capability candidate.
⋮----
def _proposal(request, *, api=None, model=None)
⋮----
api = api or API(
selected = model or os.environ.get("STUDIO_CODE_MODEL") or os.environ.get(
⋮----
params = {
⋮----
response = api.call("POST", "/chat/completions", params)
⋮----
choice = response["choices"][0]
⋮----
def synthesize_from_memory(memory, project_id, capability, *, api=None, model=None)
````

## File: generic_model.py
````python
"""Provider-routed structured model calls for generic projects."""
⋮----
def _decode(response: dict) -> dict
⋮----
choice = response["choices"][0]
⋮----
raw = choice["message"]["content"].strip()
⋮----
raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
value = json.loads(raw)
⋮----
providers = load_providers(prefer_free=True)
⋮----
role = role or ("implementation" if code else "product")
providers = candidates_for(role, providers=providers)
max_completion_tokens = 16000 if code else 8192
estimated_prompt_tokens = max(1, (len(system) + len(user) + 3) // 4)
estimated_call_tokens = estimated_prompt_tokens + max_completion_tokens
⋮----
quota_reserve_ratio = float(os.environ.get("STUDIO_PROVIDER_QUOTA_RESERVE_RATIO", "0.03") or 0.03)
⋮----
quota_reserve_ratio = 0.03
quota_reserve_ratio = max(0.0, min(0.50, quota_reserve_ratio))
quota_reserve_roles = {
allow_quota_reserve = role in quota_reserve_roles
health_raw = os.environ.get("STUDIO_PROVIDER_HEALTH_PATH", "")
metrics_raw = os.environ.get("STUDIO_PROVIDER_METRICS_PATH", "")
health_path = Path(health_raw) if health_raw else None
metrics_path = Path(metrics_raw) if metrics_raw else None
history_raw = os.environ.get("STUDIO_ROUTING_HISTORY_PATH", "")
history_path = Path(history_raw) if history_raw else None
safe_rewrite_raw = os.environ.get("STUDIO_SAFE_REWRITE_LEARNING_PATH", "")
safe_rewrite_path = Path(safe_rewrite_raw) if safe_rewrite_raw else None
contextual_routing_raw = os.environ.get("STUDIO_CONTEXTUAL_ROUTING_MEMORY_PATH", "")
contextual_routing_path = Path(contextual_routing_raw) if contextual_routing_raw else None
provider_cost_raw = os.environ.get("STUDIO_PROVIDER_COST_PATH", "")
provider_cost_path = Path(provider_cost_raw) if provider_cost_raw else None
quota_raw = os.environ.get("STUDIO_PROVIDER_MONTHLY_QUOTA_PATH", "")
quota_path = Path(quota_raw) if quota_raw else None
local_rep_raw = os.environ.get("STUDIO_LOCAL_MODEL_REPUTATION_PATH", "")
local_rep_path = Path(local_rep_raw) if local_rep_raw else None
local_benchmark_raw = os.environ.get("STUDIO_LOCAL_MODEL_BENCHMARK_PATH", "")
local_benchmark_path = Path(local_benchmark_raw) if local_benchmark_raw else None
local_specialization_raw = os.environ.get("STUDIO_LOCAL_MODEL_SPECIALIZATION_PATH", "")
local_specialization_path = Path(local_specialization_raw) if local_specialization_raw else None
portfolio_learning_raw = os.environ.get("STUDIO_MODEL_PORTFOLIO_LEARNING_PATH", "")
portfolio_learning_path = Path(portfolio_learning_raw) if portfolio_learning_raw else None
capacity_ledger_raw = os.environ.get("STUDIO_CAPACITY_LEDGER_PATH", "")
capacity_ledger_path = Path(capacity_ledger_raw) if capacity_ledger_raw else None
capacity_plan_raw = os.environ.get("STUDIO_CAPACITY_PLAN_PATH", "")
capacity_efficiency_raw = os.environ.get("STUDIO_CAPACITY_EFFICIENCY_PATH", "")
project_id = os.environ.get("STUDIO_PROJECT_ID", "").strip() or None
project_capacity_envelope = load_project_envelope(
capacity_efficiency = (
⋮----
weighted_contexts = json.loads(os.environ.get("STUDIO_ROUTING_CONTEXTS_JSON", "[]"))
⋮----
weighted_contexts = []
⋮----
health = load_provider_health(health_path) if health_path is not None else {}
metrics = load_provider_metrics(metrics_path) if metrics_path is not None else {}
history = load_routing_history(history_path) if history_path is not None else []
⋮----
verification_seconds = float(os.environ.get("STUDIO_EXPECTED_VERIFICATION_SECONDS", "0") or 0)
⋮----
verification_seconds = 0.0
architecture_hold = any(
safe_rewrite_summary = summarize_safe_rewrite_learning(safe_rewrite_path) if safe_rewrite_path is not None else {}
contextual_routing = load_contextual_routing_memory(contextual_routing_path) if contextual_routing_path is not None else {}
provider_costs = load_provider_cost(provider_cost_path) if provider_cost_path is not None else {}
provider_quota_data = load_provider_monthly_quota(quota_path) if quota_path is not None else {"schema": 1, "months": {}}
local_model_reputation = load_local_model_reputation(local_rep_path) if local_rep_path is not None else {}
local_model_benchmark = load_local_model_benchmark(local_benchmark_path) if local_benchmark_path is not None else {}
local_model_specialization = load_local_model_specialization(local_specialization_path) if local_specialization_path is not None else {}
portfolio_learning = load_model_portfolio_learning(portfolio_learning_path) if portfolio_learning_path is not None else {}
learned_diversity_bias = model_portfolio_diversity_bias(portfolio_learning)
⋮----
max_api_cost_usd = float(os.environ.get("STUDIO_MAX_API_COST_USD", "0") or 0.0)
⋮----
max_api_cost_usd = 0.0
spent_api_cost_usd = sum(
weights = learned_weights(history, kind="provider", role=role)
⋮----
providers = tuple(provider for provider in providers if provider_eligible(health_path, provider.name))
providers = budget_eligible(
providers = tuple(
⋮----
provider_scores = {}
⋮----
base = score_provider(
components = dict(base.components)
⋮----
gateway_name = provider.name.split(":", 1)[0]
reputation_component = local_model_reputation_score(
⋮----
parsed_local_contexts = [
specialization = local_model_specialization_score(
⋮----
quarantine = local_model_quarantine_status(
⋮----
candidate_model = provider.model_for(role)
⋮----
violation = origin_violation_penalty(
recovery = rewrite_recovery_bonus(
⋮----
parsed_contexts = [
⋮----
bandit = contextual_bandit_score(
⋮----
metric_row = metrics.get(provider.name + ":" + role, {}) if isinstance(metrics, dict) else {}
execution_seconds = (
retry_probability = max(0.0, min(1.0, 1.0 - bandit["expected_success"]))
pooled_free = provider.monthly_token_quota > 0
monetary_cost_usd = (
utility = utility_score(
⋮----
quota = provider_quota_status(
⋮----
remaining_ratio = max(
⋮----
providers = tuple(sorted(
⋮----
avoid_models = avoid_models or set()
avoid_providers = avoid_providers or set()
preferred = [
fallback = [provider for provider in providers if provider not in preferred]
ordered = [*preferred, *fallback]
last = None
total_timeout = max(1.0, min(300.0, float(timeout_seconds)))
deadline = time.monotonic() + total_timeout
⋮----
remaining = deadline - time.monotonic()
⋮----
model = provider.model_for(role)
api = API(provider.base, provider.key)
params = {
⋮----
reservation = None
reservation_open = False
⋮----
provider_remaining_tokens = None
⋮----
quota_now = provider_quota_status(
provider_remaining_tokens = quota_now["remaining_tokens"]
reservation = reserve_capacity(
⋮----
last = StudioError(
⋮----
reservation_open = True
⋮----
started = time.monotonic()
⋮----
response = api.call("POST", "/chat/completions", params, timeout_seconds=remaining)
elapsed = time.monotonic() - started
⋮----
usage = response.get("usage") if isinstance(response, dict) else None
actual_tokens = estimated_call_tokens
⋮----
actual_tokens = max(
⋮----
call_cost = 0.0
⋮----
call_cost = 0.0 if (provider.unmetered or provider.monthly_token_quota > 0) else estimate_call_cost(
⋮----
prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
completion_tokens = int(usage.get("completion_tokens", 0) or 0)
⋮----
prompt_tokens = completion_tokens = 0
⋮----
decoded = _decode(response)
⋮----
last = exc
````

## File: generic_policy.py
````python
"""Safe text-edit policy for generic autonomous projects."""
⋮----
MAX_FILE_BYTES = 400_000
MAX_PATCH_BYTES = 1_500_000
BLOCKED_PARTS = {
BLOCKED_NAMES = {
BLOCKED_SUFFIXES = {
SECRET_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|sk-[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{15,}")
⋮----
def editable(path: str) -> bool
⋮----
p = PurePosixPath(path)
⋮----
def validate_patch(value: object) -> list[dict]
⋮----
seen = set()
total = 0
normalized = []
⋮----
raw = content.encode("utf-8")
````

## File: generic_project.py
````python
"""Autonomous work/analyse/verify loop for generic software projects."""
⋮----
PLAN_SYSTEM = """You are the senior autonomous maintainer of an existing software repository.
⋮----
IMPLEMENT_SYSTEM = """You are the implementation worker for an autonomous software-maintenance system.
⋮----
PROGRESS_SYSTEM = """You are the autonomous engineering progress controller.
⋮----
CANDIDATE_REVIEW_SYSTEM = """You are an independent engineering reviewer comparing implementation candidates.
⋮----
REVIEW_SYSTEM = """You are the verification-driven senior reviewer.
⋮----
def _snapshot(root: Path, limit_bytes: int = 420_000) -> dict
⋮----
files = {}
used = 0
preferred = []
⋮----
rel = p.relative_to(root).as_posix()
priority = 0 if rel.lower() in {"readme.md","package.json","pyproject.toml","cargo.toml","go.mod","pom.xml"} else 1
⋮----
text = p.read_text(encoding="utf-8")
⋮----
size = len(text.encode("utf-8"))
⋮----
changed = []
⋮----
target = (root / item["path"]).resolve()
⋮----
def _prepare_architecture(req: dict, out: Path, state: dict) -> Path
⋮----
recommendations = recommend(
architecture_root = architecture_learning_root(out)
learning = summarize_architecture_learning(architecture_root)
⋮----
def _record_architecture(state: dict, out: Path, architecture_root: Path) -> None
⋮----
def run_project(req: dict, out: Path, work: Path, portfolio: dict | None = None, max_rounds: int = 6, deadline: float | None = None, clock=time.monotonic) -> dict
⋮----
github = GitHub(req["target_repo"])
repo = GenericRepository(github, req["target_repo"], req["id"])
⋮----
checkpoint_path = out / ".autonomy" / "generic-execution-checkpoint.json"
safe_rewrite_learning_path = out / ".autonomy" / "safe-rewrite-learning.json"
contextual_routing_path = out / ".autonomy" / "contextual-routing-memory.json"
provider_cost_path = out / ".autonomy" / "provider-cost.json"
provider_monthly_quota_path = out.parent / "provider-monthly-quota.json"
local_model_reputation_path = out / ".autonomy" / "local-model-reputation.json"
local_model_specialization_path = out / ".autonomy" / "local-model-specialization.json"
model_portfolio_learning_path = out / ".autonomy" / "model-portfolio-learning.json"
candidate_portfolio_learning_path = out / ".autonomy" / "candidate-portfolio-learning.json"
capacity_efficiency_path = out.parent / "capacity-efficiency.json"
⋮----
max_api_cost = req.get("max_api_cost_usd")
⋮----
checkpoint = load_checkpoint(checkpoint_path) if checkpoint_path.is_file() else new_checkpoint(req["id"], "generic", base_sha)
⋮----
checkpoint = new_checkpoint(req["id"], "generic", base_sha)
⋮----
resume_round = checkpoint.get("round", 0) if checkpoint.get("phase") in {"published", "complete"} else 0
resumed_verification = checkpoint.get("last_verification") if resume_round else None
⋮----
local_capacity_inventory = write_local_capacity_inventory(out)
state = {
⋮----
architecture_root = _prepare_architecture(req, out, state)
⋮----
bootstrap_evidence = []
⋮----
result = run_command(command, work, timeout=900, network=True)
⋮----
initial_remaining = None if deadline is None else max(0.0, deadline - clock())
initial_capacity_status = capacity_snapshot(provider_monthly_quota_path)
explicit_project_limit = req.get("max_project_model_calls")
base_model_calls = int(
capacity_plan = expanded_call_limit(
⋮----
capacity_multiplier = float(capacity_plan.get("multiplier", 1.0) or 1.0)
effective_rounds = (
⋮----
cost_controller = RunCostController(
drift_detector = CostDriftDetector()
phase_baseline_path = out/".autonomy/phase-cost-baselines.json"
last_verification = resumed_verification
adaptive_recipe = None
adaptive_path = out / "generic-verifier.json"
⋮----
saved = json.loads(adaptive_path.read_text())
⋮----
adaptive_recipe = validate_recipe(saved["recipe"], work)
⋮----
stagnation_state = summarize_stagnation(
capacity_runtime_state = load_capacity_project_state(
recovery_active = capacity_runtime_state.get("recovery_active") is True
admission = capacity_runtime_state.get("admission")
⋮----
stagnation_state = {
star_context=recommend('implementation',out)
snapshot = _snapshot(work)
previous_failures = sum(
⋮----
verification_fallback = (
verification_cost_path = out/".autonomy/verification-cost.json"
verification_seconds = estimate_verification_seconds(
⋮----
difficulty = estimate_difficulty(
learned_context = load_context()
round_weighted_contexts = weighted_task_contexts(req["brief"], state["toolchain"])
round_weighted_contexts = list(round_weighted_contexts)
⋮----
architecture_risk = (
⋮----
total_context_weight = sum(max(0.0, float(weight)) for _, weight in round_weighted_contexts)
⋮----
round_weighted_contexts = [
⋮----
contextual_routing = load_contextual_routing_memory(contextual_routing_path)
agent_perf = load_agent_performance(out/".autonomy/agent-performance.json")
safe_rewrite_summary = summarize_safe_rewrite_learning(safe_rewrite_learning_path)
agent_execution_seconds = {}
⋮----
row = agent_perf.get(agent_name + ":implementation")
⋮----
agent_candidates = []
⋮----
plan_payload = {
planning_started = clock()
preplan_remaining = None if deadline is None else max(0.0, deadline - clock())
preplan_quotas = allocate_phase_quotas(
normalized_difficulty = min(1.0, max(0.0, float(difficulty.score) / 10.0))
round_require_planning = planning_required(
planning_policy = planning_phase_decision(
planning_decision = {
⋮----
planning_timeout = bounded_timeout(
⋮----
plan = planning_policy["plan"]
plan_model = None
checkpoint = advance_checkpoint(checkpoint, round_index=round_index, phase="planned")
⋮----
implementation_models = []
safe_rewrite_event_ids = []
progress_trace = []
agent_trace = []
agent_used = None
round_candidate_portfolio = None
round_candidate_cost_seconds = 0.0
round_require_review = True
current_plan = plan
remaining_seconds = None if deadline is None else max(0.0, deadline - clock())
drift_multiplier = drift_detector.exploration_multiplier()
predicted_passes = max(1, int(round(difficulty.recommended_work_passes * drift_multiplier))) if drift_multiplier > 0 else 1
predicted_agents = max(0, int(round(difficulty.recommended_agent_limit * drift_multiplier)))
round_budget = choose_budget(
phase_quotas = allocate_phase_quotas(
planning_elapsed = max(0, int(clock() - planning_started))
planning_history = load_phase_cost_baselines(phase_baseline_path)
planning_baseline = phase_cost_baseline(planning_history, state["toolchain"], "planning")
⋮----
phase_quotas = reallocate_phase_quota(
⋮----
implementation_started = clock()
⋮----
global_cost_decision = cost_controller.decision()
⋮----
implementation_remaining = phase_remaining(
⋮----
current_remaining = None if deadline is None else max(0.0, deadline - clock())
⋮----
implementation_context = {
⋮----
used_external_agent = False
⋮----
before_agent = snapshot_agent_workspace(work)
⋮----
before_agent = None
agent_prompt = """Work autonomously on this repository. Implement the requested objective directly in the files.
⋮----
candidate_records = []
fallback_started = clock()
routing_events = load_routing_history(out/".autonomy/routing-history.json")
strategy_efficiency_path = out/".autonomy/strategy-efficiency.json"
contextual_strategy_path = out/".autonomy/contextual-strategy-efficiency.json"
task_context = classify_task_context(req["brief"], state["toolchain"])
context_hierarchy = task_context_hierarchy(req["brief"], state["toolchain"])
weighted_contexts = round_weighted_contexts
global_strategy_data = load_strategy_efficiency(strategy_efficiency_path)
contextual_strategy_data = load_contextual_strategy_efficiency(contextual_strategy_path)
blended_context_rows = blend_contextual_rows(contextual_strategy_data, weighted_contexts)
selected_context = None
strategy_data = global_strategy_data
⋮----
selected_context = "weighted"
strategy_data = blended_context_rows
⋮----
candidate_rows = contextual_rows_for(contextual_strategy_data, context_name)
⋮----
selected_context = context_name
strategy_data = candidate_rows
⋮----
preliminary_names = ranked_agent_names(
⋮----
direct_model_candidates = direct_candidates_for(
available_direct_models = len({
⋮----
available_direct_models = 1
meta_route = choose_execution_mode(
⋮----
current_drift_multiplier = drift_detector.exploration_multiplier()
route_budget = choose_budget(
⋮----
scheduler_confidence = (
candidate_width_learning = recommend_candidate_portfolio_width(
capacity_state = state.get("capacity_status", {})
free_capacity = 1.0 if capacity_state.get("unmetered_available") else (
role_allocation = choose_role_allocation(
round_require_review = role_allocation.require_review
⋮----
candidate_schedule = choose_candidate_schedule(
round_candidate_portfolio = {
⋮----
ranked_names = preliminary_names[:candidate_schedule.agent_limit]
⋮----
implementation_left = phase_remaining(
⋮----
model_timeout = bounded_timeout(
⋮----
model_files = validate_patch(model_patch)
model_changed = _apply(
⋮----
model_verify_timeout = bounded_timeout(
⋮----
model_verification = verify(
⋮----
model_success = model_verification.get("passed") is True
⋮----
candidate_provider = model_impl.get("provider")
⋮----
candidate_duration = model_impl.get("duration_seconds")
⋮----
candidate_latency_ms = (
⋮----
candidate_latency_ms = None
provider_health_env = str(
candidate_health_path = (
⋮----
routing_score = model_impl.get("routing_score") if isinstance(model_impl,dict) else None
⋮----
provider_name = str(model_impl.get("provider") or "direct-model")
⋮----
model_provider = str(
model_name = str(
candidate_id = "model:" + model_provider + ":" + model_name
⋮----
candidate = {
⋮----
selected_strategy = meta_route.strategy
model_first = selected_strategy in {"model_only","model_to_agent"}
model_candidate = (
model_verified = bool(
⋮----
allow_agents = selected_strategy not in {"model_only"}
need_agent_candidates = (
⋮----
agent_timeout = bounded_timeout(
⋮----
agent_result = execute_named_agent(
⋮----
delta = validate_agent_delta(work, before_agent)
⋮----
candidate_verify_timeout = bounded_timeout(
⋮----
candidate_verification = verify(
duration = 0.0
⋮----
try: duration=float(attempt.get("duration_seconds",0.0))
except (TypeError,ValueError): duration=0.0
⋮----
success = candidate_verification.get("passed") is True
route_trace = routing_trace_for(
⋮----
agent_verified = any(
allow_model_fallback = (
used_model_count = sum(
need_model_candidate = (
⋮----
used_model_candidates = [
avoided_model_names = {
avoided_provider_names = {
⋮----
candidate = evaluate_model_candidate(
⋮----
viable=[x for x in candidate_records if x.get("changed")]
⋮----
winner_id=viable[0]["id"]
candidate_review={"winner":winner_id,"reason":"single viable candidate","scores":{winner_id:100}}
candidate_review_model=None
⋮----
review_payload={
avoided_models={
avoided_providers={
candidate_review_timeout = bounded_timeout(
⋮----
verified=[item for item in viable if item["verification"].get("passed") is True]
winner_id=(verified[0] if verified else viable[0])["id"]
candidate_review={
⋮----
winner_id=candidate_review.get("winner")
⋮----
winner=next(item for item in viable if item["id"]==winner_id)
winner_patch={"files":winner["files"]}
⋮----
retry_context=build_architecture_safe_rewrite_context(
⋮----
event_id = f"{req['id']}:{round_index}:candidate:{len(safe_rewrite_event_ids)}"
⋮----
agent_used=winner["agent"]
⋮----
used_external_agent=True
⋮----
fallback_elapsed = max(0, int(clock() - fallback_started))
round_candidate_cost_seconds = max(
⋮----
strategy_success = False
⋮----
selected = next((item for item in viable if item["id"] == winner_id), None)
strategy_success = bool(selected and selected.get("verification",{}).get("passed") is True)
⋮----
fallback_history = load_phase_cost_baselines(phase_baseline_path)
fallback_baseline = phase_cost_baseline(fallback_history, state["toolchain"], "fallback")
⋮----
direct_model_timeout = bounded_timeout(
⋮----
direct_context=canonical(implementation_context)
⋮----
event_id = f"{req['id']}:{round_index}:direct:{len(safe_rewrite_event_ids)}"
⋮----
progress_timeout = bounded_timeout(
⋮----
progress = {"action":"verify","reason":"implementation phase quota exhausted","next_work":[]}
progress_model = None
⋮----
action = progress.get("action")
⋮----
action = "verify"
⋮----
next_work = progress.get("next_work")
⋮----
current_plan = {**current_plan, "controller_next_work": next_work}
⋮----
implementation_elapsed = max(0, int(clock() - implementation_started))
implementation_history = load_phase_cost_baselines(phase_baseline_path)
implementation_baseline = phase_cost_baseline(implementation_history, state["toolchain"], "implementation")
⋮----
verification_started = clock()
verification_timeout = bounded_timeout(
verification = verify(
⋮----
adaptive_verify_timeout = bounded_timeout(
⋮----
verification_elapsed = max(0, int(clock() - verification_started))
verification_history = load_phase_cost_baselines(phase_baseline_path)
verification_baseline = phase_cost_baseline(verification_history, state["toolchain"], "verification")
⋮----
last_verification = verification
checkpoint = advance_checkpoint(
⋮----
review_context = {
review_started = clock()
review_remaining = phase_remaining(
review_policy = review_phase_decision(
review_decision = {
⋮----
review_timeout = bounded_timeout(
implementation_providers = {
implementation_model_names = {
⋮----
review_duration = float(review_model.get("duration_seconds",0.0) or 0.0)
⋮----
review = review_policy["review"]
review_model = None
review_elapsed = max(0, int(clock() - review_started))
review_history = load_phase_cost_baselines(phase_baseline_path)
review_baseline = phase_cost_baseline(review_history, state["toolchain"], "review")
⋮----
complete = review.get("complete") is True and verification.get("passed") is True
⋮----
review_provider = review_model.get("provider")
⋮----
review_duration = review_model.get("duration_seconds")
⋮----
review_latency_ms = (
⋮----
review_latency_ms = None
verification_passed = verification.get("passed") is True
review_complete = review.get("complete") is True
review_agrees_with_evidence = (
review_health_env = str(
review_health_path = (
⋮----
verified_round_progress = verification.get("passed") is True
⋮----
planning_provider = plan_model.get("provider")
⋮----
planning_duration = plan_model.get("duration_seconds")
⋮----
planning_latency_ms = (
⋮----
planning_latency_ms = None
planning_health_env = str(
planning_health_path = (
⋮----
provider_health_env = str(__import__("os").environ.get("STUDIO_PROVIDER_HEALTH_PATH") or "").strip()
provider_health_path = Path(provider_health_env) if provider_health_env else out / ".autonomy/provider-health.json"
provider_samples = {}
⋮----
provider_name = model_meta.get("provider")
⋮----
duration = model_meta.get("duration_seconds")
⋮----
latency_ms = max(0.0, float(duration) * 1000.0) if duration is not None else None
⋮----
latency_ms = None
⋮----
feedback_attributable = verified_round_progress or len(provider_samples) == 1
⋮----
observed = [sample for sample in latency_samples if sample is not None]
latency_ms = (
⋮----
model_name = model_meta.get("model")
usage_tokens = model_meta.get("usage_tokens")
⋮----
verified_local_models = set()
⋮----
gateway_name = provider_name.split(":", 1)[0]
key = (gateway_name, model_name)
⋮----
provider_cost_state = load_provider_cost(provider_cost_path)
spent_api_cost_usd = sum(
budget_limit = state.get("budget_policy", {}).get("max_api_cost_usd")
⋮----
specialization_state = load_local_model_specialization(local_model_specialization_path)
⋮----
portfolio_rows = {}
⋮----
implementation_rows = [
⋮----
primary_impl = implementation_rows[0] if implementation_rows else {}
round_portfolio = choose_model_portfolio(
round_portfolio_audit = audit_model_portfolio(round_portfolio.get("roles", {}))
⋮----
actual_width = int(round_candidate_portfolio.get("candidate_count", 0) or 0)
⋮----
portfolio_learning = load_model_portfolio_learning(model_portfolio_learning_path)
⋮----
round_state = {
⋮----
drift_decision = drift_detector.decision()
⋮----
complete = False
⋮----
remaining_items = review.get("remaining")
⋮----
base_sha = repo.publish(base_sha, work, "Autonomous generic project round " + str(round_index))
````

## File: generic_repository.py
````python
"""Bounded GitHub snapshot/publish backend for generic projects."""
⋮----
MAX_FILES=500
MAX_TOTAL=6_000_000
⋮----
class GenericRepository
⋮----
def __init__(self,github,repo:str,project_id:str)
⋮----
def _tree(self,sha:str)->dict
⋮----
tree=self.github.get("/git/trees/"+sha+"?recursive=1")
⋮----
def restore(self,root:Path)->tuple[str,dict]
⋮----
metadata=self.github.get("")
⋮----
refs=self.github.get("/git/matching-refs/heads/"+self.branch)
exact=[r for r in refs if isinstance(r,dict) and r.get("ref")=="refs/heads/"+self.branch]
⋮----
source=exact[0].get("object",{}).get("sha")
⋮----
default=metadata.get("default_branch")
⋮----
init=self.github.call("PUT",self.github.repo+"/contents/README.md",{
source=init.get("commit",{}).get("sha") if isinstance(init,dict) else None
⋮----
source=self.github.get("/branches/"+default).get("commit",{}).get("sha")
⋮----
tree=self._tree(source)
⋮----
count=total=0
⋮----
path=item.get("path")
⋮----
size=item.get("size",0)
⋮----
blob=self.github.get("/git/blobs/"+item["sha"])
⋮----
text=base64.b64decode(blob["content"]).decode("utf-8")
⋮----
target=root/path
⋮----
def publish(self,base_sha:str,root:Path,message:str)->str
⋮----
base_tree=self.github.get("/git/commits/"+base_sha).get("tree",{}).get("sha")
⋮----
entries=[]
⋮----
rel=p.relative_to(root).as_posix()
⋮----
raw=p.read_bytes()
⋮----
text=raw.decode("utf-8")
⋮----
tree=self.github.call("POST",self.github.repo+"/git/trees",{"base_tree":base_tree,"tree":entries})
commit=self.github.call("POST",self.github.repo+"/git/commits",{"message":message,"tree":tree["sha"],"parents":[base_sha]})
⋮----
exists=any(r.get("ref")=="refs/heads/"+self.branch for r in refs if isinstance(r,dict))
````

## File: generic_sandbox.py
````python
"""Bounded generic command runner with explicit network and secret isolation."""
⋮----
_SECRET_PREFIXES=("STUDIO_","GITHUB_","GH_","OPENAI_","ANTHROPIC_","NVIDIA_","GEMINI_")
_ALLOWED_ENV={"PATH","HOME","LANG","LC_ALL","TMPDIR"}
⋮----
def safe_env() -> dict[str,str]
⋮----
env={k:v for k,v in os.environ.items() if k in _ALLOWED_ENV}
⋮----
def run(command:list[str],root:Path,*,timeout:int=900,network:bool=False)->dict
⋮----
started=time.monotonic()
env=safe_env()
argv=list(command)
network_isolated=False
⋮----
probe=subprocess.run(["unshare","--net","true"],env=env,stdin=subprocess.DEVNULL,
⋮----
argv=["unshare","--net","--",*command]
network_isolated=True
⋮----
# Commands never inherit provider/GitHub secrets. When the host permits an
# unprivileged network namespace, verification is also executed without
# network access; otherwise the evidence explicitly records that only
# credential isolation was enforced.
⋮----
p=subprocess.run(argv,cwd=root,env=env,stdin=subprocess.DEVNULL,
rc=p.returncode; log=p.stdout[-24000:]
⋮----
rc=124; log=(exc.stdout or "")[-24000:] if isinstance(exc.stdout,str) else "TimeoutExpired"
⋮----
rc=127; log=type(exc).__name__
````

## File: generic_smoke.py
````python
"""Deterministic generic-engine end-to-end smoke tests.

This exercises both the trusted toolchain/verifier path and the real
generic_project orchestration loop. Only the external GitHub and LLM boundaries
are replaced with deterministic local doubles.
"""
⋮----
def _fixture(root: Path) -> None
⋮----
class FakeRepository
⋮----
def __init__(self, github, target_repo, project_id)
⋮----
def restore(self, work: Path)
⋮----
def publish(self, base_sha: str, work: Path, message: str)
⋮----
def fake_ask(system: str, user: str, *, code=False, **kwargs)
⋮----
meta={
⋮----
payload=json.loads(user)
verification=payload.get("verification",{})
⋮----
def verifier_smoke() -> dict
⋮----
root=Path(td)
⋮----
# Correct locally so this lower-level smoke isolates toolchain + verifier.
⋮----
toolchain=detect(root)
commands=bootstrap_commands(root)
verification=verify(root,timeout_per_command=120)
⋮----
def orchestration_smoke(out: Path) -> dict
⋮----
work=out/"work"
project_out=out/"project"
req={
⋮----
result=generic_project.run_project(
report=result.get("report",{})
verification=(report.get("rounds") or [{}])[-1].get("verification",{})
⋮----
def main() -> int
⋮----
out=Path("studio-output/generic-smoke")
⋮----
verifier=verifier_smoke()
orchestration=orchestration_smoke(out)
evidence={
````

## File: generic_toolchain.py
````python
"""Trusted toolchain/dependency preparation for generic repositories.

Only deterministic project-native package-manager operations are emitted.
No model-generated bootstrap command is executed here.
"""
⋮----
def detect(root: Path) -> dict
⋮----
markers=[]
⋮----
def bootstrap_commands(root: Path) -> list[list[str]]
⋮----
commands=[]
````

## File: generic_verifier_adaptation.py
````python
"""Synthesize a bounded verifier recipe when a generic stack has no built-in verifier."""
⋮----
SYSTEM = """You design verification commands for an autonomous software repository.
⋮----
ALLOWED_EXECUTABLES = {
FORBIDDEN_ARGS = {
SAFE_ARG = re.compile(r"^[A-Za-z0-9_./:=+@%,-]{1,180}$")
⋮----
def available_tools() -> list[str]
⋮----
def _file_hints(root: Path) -> list[str]
⋮----
hints = []
⋮----
rel = p.relative_to(root).as_posix()
⋮----
def validate_recipe(value: object, root: Path) -> dict
⋮----
commands = value["commands"]
reason = value["reason"]
⋮----
normalized = []
⋮----
exe = command[0]
⋮----
lowered = {arg.lower() for arg in command[1:]}
⋮----
script = command[1]
⋮----
def synthesize(root: Path, brief: str, previous: dict | None = None) -> tuple[dict, dict]
⋮----
tools = available_tools()
⋮----
context = {
⋮----
def save_recipe(path: Path, recipe: dict, model: dict) -> None
⋮----
payload = {"status":"validated_recipe","recipe":recipe,"model":model}
````

## File: generic_verify.py
````python
"""Trusted verification command discovery for generic repositories."""
⋮----
def discover(root: Path) -> list[list[str]]
⋮----
commands: list[list[str]] = []
package = root / "package.json"
⋮----
data = json.loads(package.read_text())
⋮----
data = {}
scripts = data.get("scripts") if isinstance(data, dict) else {}
⋮----
venv_pytest=root/".studio-venv/bin/pytest"
venv_python=root/".studio-venv/bin/python"
⋮----
def run(root: Path, *, timeout_per_command: int = 900, commands: list[list[str]] | None = None) -> dict
⋮----
started = time.monotonic()
commands = discover(root) if commands is None else commands
⋮----
results = []
all_passed = True
⋮----
result = run_command(command, root, timeout=timeout_per_command, network=False)
passed = result["passed"]
all_passed = all_passed and passed
````

## File: github_agent_performance_store.py
````python
"""Persist learned agent routing statistics on the trusted memory branch."""
⋮----
STATE_BRANCH="studio-project-memory"
STATE_PATH=".studio-memory/agent-performance.json"
MAX_BYTES=256*1024
⋮----
class AgentPerformanceStoreError(RuntimeError): pass
⋮----
def _validate(data)
⋮----
runs=row["runs"]; successes=row["successes"]; duration=row["duration_total"]
⋮----
def _ref(github)
⋮----
refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
⋮----
def load(github)
⋮----
ref=_ref(github)
⋮----
head=ref.get("object",{}).get("sha")
tree=github.get("/git/trees/"+head+"?recursive=1")
⋮----
item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
⋮----
blob=github.get("/git/blobs/"+item["sha"])
⋮----
raw=base64.b64decode(blob["content"],validate=False)
⋮----
def save(github,data)
⋮----
data=_validate(data)
⋮----
meta=github.get(""); default=meta.get("default_branch")
parent=github.get("/branches/"+default).get("commit",{}).get("sha")
⋮----
parent=ref.get("object",{}).get("sha")
⋮----
base_tree=github.get("/git/commits/"+parent).get("tree",{}).get("sha")
tree=github.call("POST",github.repo+"/git/trees",{"base_tree":base_tree,"tree":[{
commit=github.call("POST",github.repo+"/git/commits",{"message":"Persist agent performance memory","tree":tree["sha"],"parents":[parent]})
sha=commit.get("sha")
⋮----
def restore_local(github,path:Path)
⋮----
data=load(github); path.parent.mkdir(parents=True,exist_ok=True)
⋮----
def persist_local(github,path:Path)
⋮----
try: data=json.loads(path.read_text())
except (OSError,json.JSONDecodeError): data={}
````

## File: github_artifact_cas_audit_store.py
````python
"""Persist CAS promotion audit records on trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/artifact-cas-audit.json"
MAX_BYTES = 512 * 1024
MAX_RECORDS = 512
⋮----
class ArtifactCasAuditStoreError(RuntimeError)
⋮----
def _validate(rows)
⋮----
clean = []
previous = 0
⋮----
previous = row["sequence"]
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next(
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
rows = json.loads(raw.decode("utf-8"))
⋮----
def save(github, rows)
⋮----
rows = _validate(rows)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call(
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call(
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
rows = load(github)
⋮----
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
rows = json.loads(path.read_text(encoding="utf-8"))
````

## File: github_artifact_cas_stats_store.py
````python
"""Persist artifact CAS retention statistics on trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/artifact-cas-stats.json"
MAX_BYTES = 512 * 1024
MAX_BLOBS = 4096
⋮----
class ArtifactCasStatsStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
blobs = data["blobs"]
⋮----
clean = {}
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next(
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
data = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call(
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call(
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
⋮----
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
````

## File: github_contextual_strategy_efficiency_store.py
````python
"""Persist context-scoped strategy efficiency memory."""
⋮----
STATE_BRANCH="studio-project-memory"
STATE_PATH=".studio-memory/contextual-strategy-efficiency.json"
MAX_BYTES=256*1024
MAX_CONTEXTS=16
⋮----
class ContextualStrategyEfficiencyStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean={}
⋮----
valid={}
⋮----
required={"samples","successes","ema_cost_seconds"}
allowed=required|{"ema_success_rate"}
⋮----
samples=row["samples"]; successes=row["successes"]; cost=row["ema_cost_seconds"]
⋮----
fallback=(successes/samples) if samples else 0.0
recent=row.get("ema_success_rate",fallback)
⋮----
def _ref(github)
⋮----
refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
⋮----
exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
⋮----
def load(github)
⋮----
ref=_ref(github)
⋮----
head=ref.get("object",{}).get("sha")
⋮----
tree=github.get("/git/trees/"+head+"?recursive=1")
⋮----
item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
⋮----
blob=github.get("/git/blobs/"+item.get("sha",""))
⋮----
raw=base64.b64decode(blob["content"],validate=False)
⋮----
value=json.loads(raw.decode("utf-8"))
⋮----
def save(github,data)
⋮----
data=_validate(data)
⋮----
meta=github.get("")
default=meta.get("default_branch") if isinstance(meta,dict) else None
⋮----
info=github.get("/branches/"+default)
parent=info.get("commit",{}).get("sha") if isinstance(info,dict) else None
⋮----
parent=ref.get("object",{}).get("sha")
⋮----
commit_info=github.get("/git/commits/"+parent)
base_tree=commit_info.get("tree",{}).get("sha") if isinstance(commit_info,dict) else None
⋮----
tree=github.call("POST",github.repo+"/git/trees",{
tree_sha=tree.get("sha") if isinstance(tree,dict) else None
⋮----
commit=github.call("POST",github.repo+"/git/commits",{
commit_sha=commit.get("sha") if isinstance(commit,dict) else None
⋮----
def restore_local(github,path:Path)
⋮----
data=load(github)
path=Path(path)
⋮----
def persist_local(github,path:Path)
⋮----
data=load_local(path) if path.is_file() else {}
````

## File: github_execution_checkpoint_store.py
````python
"""Persist execution checkpoint on the autonomous-state branch."""
⋮----
STATE_BRANCH = "studio-autonomy-state"
ROOT = ".studio-autonomy"
MAX_BYTES = 256 * 1024
⋮----
class ExecutionCheckpointStoreError(RuntimeError)
⋮----
def _safe_project_id(value: str) -> str
⋮----
def _path(project_id: str) -> str
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github, project_id: str)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
target = _path(project_id)
item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == target and x.get("type") == "blob"), None)
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, project_id: str, checkpoint: dict)
⋮----
checkpoint = validate(checkpoint)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
current = load(github, project_id)
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, project_id: str, path: Path) -> bool
⋮----
checkpoint = load(github, project_id)
⋮----
path = Path(path)
⋮----
def persist_local(github, project_id: str, path: Path)
````

## File: github_full_gate_cache_store.py
````python
"""Persist successful full candidate validation cache on trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/full-gate-cache.json"
MAX_BYTES = 128 * 1024
MAX_ENTRIES = 128
⋮----
class FullGateCacheStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
entries = data["entries"]
⋮----
clean = {}
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next(
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call(
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call(
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
⋮----
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
````

## File: github_goal_store.py
````python
"""GitHub-backed persistence for autonomous goal state outside main."""
⋮----
STATE_BRANCH = "studio-autonomy-state"
ROOT = ".studio-autonomy"
MAX_STATE_BYTES = 512 * 1024
⋮----
class RemoteStateError(RuntimeError)
⋮----
def _validate_candidate_review_link(adaptation, candidate, validation, review)
⋮----
required={"status","candidate_id","candidate_sha256","capability","branch","commit_sha","pull_request"}
⋮----
payload=candidate.get("candidate",{})
⋮----
def _validate_registry_review_link(adaptation, candidate, review, registry_review)
⋮----
required={"status","candidate_id","candidate_sha256","capability","candidate_merge_sha","branch","commit_sha","pull_request"}
⋮----
def _validate_candidate_validation_link(candidate, validation)
⋮----
def _safe_project_id(value)
⋮----
def _paths(project_id)
⋮----
project_id = _safe_project_id(project_id)
prefix = f"{ROOT}/{project_id}"
⋮----
def _exact_ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def _decode_blob(github, sha)
⋮----
blob = github.get("/git/blobs/" + sha)
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def load(github, project_id)
⋮----
ref = _exact_ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
matches = {item.get("path"): item for item in tree["tree"] if isinstance(item, dict) and item.get("type") == "blob"}
goal_item = matches.get(goal_path)
registry_item = matches.get(registry_path)
backlog_item = matches.get(backlog_path)
improvement_goal_item = matches.get(improvement_goal_path)
adaptation_item = matches.get(adaptation_path)
candidate_item = matches.get(candidate_path)
validation_item = matches.get(validation_path)
review_item = matches.get(review_path)
registry_review_item = matches.get(registry_review_path)
⋮----
goal = validate_goal(_decode_blob(github, goal_item.get("sha")))
registry = validate_registry(_decode_blob(github, registry_item.get("sha")))
backlog = new_backlog() if backlog_item is None else validate_backlog(_decode_blob(github, backlog_item.get("sha")))
improvement_goal = None if improvement_goal_item is None else validate_goal(_decode_blob(github, improvement_goal_item.get("sha")))
adaptation = None if adaptation_item is None else validate_adaptation_state(_decode_blob(github, adaptation_item.get("sha")))
candidate = None if candidate_item is None else validate_candidate_envelope(_decode_blob(github, candidate_item.get("sha")))
validation = None if validation_item is None else validate_isolated_validation_result(_decode_blob(github, validation_item.get("sha")))
review = None if review_item is None else _decode_blob(github, review_item.get("sha"))
registry_review = None if registry_review_item is None else _decode_blob(github, registry_review_item.get("sha"))
⋮----
def save(github, project_id, goal, registry, backlog=None, improvement_goal=None, capability_adaptation=None, capability_candidate=None, capability_validation=None, capability_review=None, capability_registry_review=None)
⋮----
backlog = new_backlog() if backlog is None else validate_backlog(backlog)
⋮----
improvement_goal = validate_goal(improvement_goal)
⋮----
capability_adaptation = validate_adaptation_state(capability_adaptation)
⋮----
capability_candidate = validate_candidate_envelope(capability_candidate)
⋮----
capability_validation = validate_isolated_validation_result(capability_validation)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
entries = [
⋮----
tree = github.call("POST", github.repo + "/git/trees", {"base_tree": base_tree, "tree": entries})
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, project_id, project_out)
⋮----
remote = load(github, project_id)
⋮----
root = Path(project_out) / ".autonomy"
⋮----
def persist_local(github, project_id, project_out)
⋮----
goal = json.loads((root / "goal.json").read_text())
registry = json.loads((root / "capabilities.json").read_text())
backlog_path = root / "improvement-backlog.json"
backlog = json.loads(backlog_path.read_text()) if backlog_path.is_file() else new_backlog()
improvement_goal_path = root / "improvement-goal.json"
improvement_goal = json.loads(improvement_goal_path.read_text()) if improvement_goal_path.is_file() else None
adaptation_path = root / "capability-adaptation.json"
capability_adaptation = json.loads(adaptation_path.read_text()) if adaptation_path.is_file() else None
candidate_path = root / "capability-candidate.json"
capability_candidate = json.loads(candidate_path.read_text()) if candidate_path.is_file() else None
validation_path = root / "capability-validation.json"
capability_validation = json.loads(validation_path.read_text()) if validation_path.is_file() else None
review_path = root / "capability-review.json"
capability_review = json.loads(review_path.read_text()) if review_path.is_file() else None
registry_review_path = root / "capability-registry-review.json"
capability_registry_review = json.loads(registry_review_path.read_text()) if registry_review_path.is_file() else None
````

## File: github_memory_store.py
````python
"""GitHub-backed persistence for trusted cross-project memory outside main."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/memory.json"
MAX_BYTES = 1024 * 1024
⋮----
class GitHubMemoryError(RuntimeError)
⋮----
def _exact_ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def _read_blob(github, sha)
⋮----
blob = github.get("/git/blobs/" + sha)
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def load(github)
⋮----
ref = _exact_ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
items = [x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"]
⋮----
def save(github, memory)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
current = load(github)
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path)
⋮----
memory = load(github)
⋮----
def persist_local(github, path)
⋮----
memory = load_memory_file(Path(path))
````

## File: github_phase_cost_baseline_store.py
````python
"""Persist historical phase-cost baselines."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/phase-cost-baselines.json"
MAX_BYTES = 256 * 1024
MAX_ROWS = 128
⋮----
class PhaseCostBaselineStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean = {}
⋮----
samples = row["samples"]
ema = row["ema_seconds"]
mad = row["ema_abs_deviation"]
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = load_local(path) if path.is_file() else {}
````

## File: github_provider_health_store.py
````python
"""Persist provider circuit-breaker state on the trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/provider-health.json"
MAX_BYTES = 128 * 1024
MAX_ROWS = 64
⋮----
class ProviderHealthStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean = {}
⋮----
successes = row["successes"]
failures = row["failures"]
consecutive = row["consecutive_failures"]
opened_until = row["opened_until"]
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next(
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = load_local(path) if path.is_file() else {}
````

## File: github_provider_metrics_store.py
````python
"""Persist role-scoped provider metrics on the trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/provider-metrics.json"
MAX_BYTES = 256 * 1024
MAX_ROWS = 128
⋮----
class ProviderMetricsStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean = {}
⋮----
calls = row["calls"]
ema = row["ema_latency_seconds"]
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = load_local(path) if path.is_file() else {}
````

## File: github_quick_gate_cache_store.py
````python
"""Persist toolchain-scoped quick-gate cache on trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/quick-gate-cache.json"
MAX_BYTES = 512 * 1024
MAX_ENTRIES = 512
⋮----
class QuickGateCacheStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
fingerprint = data["toolchain_fingerprint"]
⋮----
entries = data["entries"]
⋮----
clean = {}
⋮----
clean_logs = []
⋮----
command = log.get("command")
exit_code = log.get("exit_code")
output = log.get("output")
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next(
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
existing = load(github)
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call(
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call(
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
⋮----
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
````

## File: github_routing_history_store.py
````python
"""Persist bounded routing decision history on the trusted memory branch."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/routing-history.json"
MAX_BYTES = 1024 * 1024
MAX_EVENTS = 500
⋮----
class RoutingHistoryStoreError(RuntimeError)
⋮----
def _validate(events)
⋮----
clean = []
⋮----
score = event.get("score")
⋮----
components = {}
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, events)
⋮----
events = _validate(events)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
events = load(github)
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
events = load_local(path) if path.is_file() else []
````

## File: github_runner.py
````python
"""GitHub Actions adapter for the provider-neutral autonomous completion pipeline."""
⋮----
def _prepare_capability_promotion_handoff(out: Path, adaptation_state: dict, baseline_sha: str) -> dict
⋮----
candidate_path=out/'.autonomy/capability-candidate.json'
validation_path=out/'.autonomy/capability-validation.json'
⋮----
candidate=validate_candidate_envelope(json.loads(candidate_path.read_text()))
validation=validate_isolated_validation_result(json.loads(validation_path.read_text()))
candidate_id=candidate.get('candidate_id')
candidate_sha=candidate.get('candidate_sha256')
⋮----
payload=candidate.get('candidate',{})
⋮----
handoff={
⋮----
path=out/'.autonomy/capability-promotion-handoff.json'
⋮----
def _usage_count(value)
⋮----
def collect_agent_usage(report: dict) -> dict
⋮----
"""Aggregate normalized coding-agent token usage from persisted round traces."""
totals = {
⋮----
rounds = report.get("rounds")
⋮----
trace = round_state.get("agent_trace")
⋮----
attempts = event.get("attempts")
⋮----
usage = attempt.get("usage")
⋮----
agent = str(attempt.get("agent") or "unknown")
input_tokens = _usage_count(usage.get("input_tokens"))
cached_input_tokens = _usage_count(
output_tokens = _usage_count(usage.get("output_tokens"))
reasoning_tokens = _usage_count(
raw_total = usage.get("total_tokens")
total_tokens = (
⋮----
def write_production_os_result(out: Path, request: dict, summary: dict)
⋮----
correlation = request.get("production_os")
⋮----
usage = summary.get("usage")
⋮----
usage = {}
envelope = {
⋮----
def bounded_run(args, timeout)
⋮----
run_id=uuid.uuid4().hex; env=dict(os.environ,STUDIO_RUN_ID=run_id); process=subprocess.Popen(args,env=env,start_new_session=True)
⋮----
containers=subprocess.run(['docker','ps','-aq','--filter','label=mobile-studio-run='+run_id],capture_output=True,text=True,timeout=15,check=True).stdout.split()
⋮----
def _update_improvements(out: Path, goal_state: dict, project_state: dict) -> dict
⋮----
assessment=assess_improvements(goal_state,project_state)
⋮----
backlog_path=out/'.autonomy/improvement-backlog.json'
backlog=load_improvement_backlog(backlog_path) if backlog_path.is_file() else new_backlog()
backlog=merge_assessment(backlog,assessment)
backlog=activate_next(backlog)
⋮----
active=next((item for item in backlog['items'] if item['status']=='active'),None)
⋮----
def run(request_path:Path,out=Path('studio-output'),runner=bounded_run,clock=time.monotonic,budget_seconds=85*60,baseline_sha:str|None=None)->dict
⋮----
request=request_check(json.loads(request_path.read_text()))
⋮----
result={'status':'disabled','next_stage':None,'finished':False}; out.mkdir(parents=True,exist_ok=True); (out/'github-pipeline.json').write_text(canonical(result)); return result
⋮----
deadline=clock()+budget_seconds
# Every autonomous project starts by examining the owner's portfolio for
# related work that can accelerate architecture, implementation or testing.
⋮----
portfolio_api=RepoGitHub(request['target_repo'])
⋮----
remote_github=None
⋮----
control_repo=os.environ.get('GITHUB_REPOSITORY','')
⋮----
remote_github=RepoGitHub(control_repo)
⋮----
goal_path=out/'.autonomy/goal.json'
⋮----
goal_state=load_goal_state(goal_path)
⋮----
adaptation_path=out/'.autonomy/capability-adaptation.json'
memory_path=out/'.memory/memory.json'
registry_path=out/'.autonomy/capabilities.json'
⋮----
adaptation_state=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
⋮----
memory=load_project_memory(memory_path)
⋮----
registry=load_capability_registry(registry_path)
⋮----
normalized=research_state.get('research_status')
⋮----
normalized='research_incomplete'
adaptation_state=record_capability_research(adaptation_state,normalized)
⋮----
candidate=synthesize_from_memory(
⋮----
adaptation_state=record_capability_synthesis(
⋮----
candidate=json.loads(candidate_path.read_text())
validation_report=validate_in_isolation(candidate,Path('.'))
⋮----
decision=validation_report.get('validation',{}).get('status')
adaptation_state=record_capability_validation(adaptation_state,decision)
⋮----
handoff=_prepare_capability_promotion_handoff(out,adaptation_state,baseline_sha)
candidate_persistence=None
⋮----
candidate=json.loads((out/'.autonomy/capability-candidate.json').read_text())
validation=json.loads((out/'.autonomy/capability-validation.json').read_text())
candidate_persistence=persist_generic_capability_candidate(
adaptation_state=record_capability_candidate_persistence(
⋮----
review={
⋮----
summary={
⋮----
waiting=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
⋮----
review_status=None
⋮----
review_path=out/'.autonomy/capability-review.json'
⋮----
review_status=inspect_capability_review(
⋮----
review=json.loads((out/'.autonomy/capability-review.json').read_text())
registry_promotion=persist_capability_registry_promotion(
⋮----
waiting=record_capability_registry_promotion_persistence(
⋮----
registry_review={
⋮----
registry_waiting=validate_capability_adaptation(json.loads(adaptation_path.read_text()))
⋮----
registry_review_status=None
⋮----
registry_review_path=out/'.autonomy/capability-registry-review.json'
⋮----
registry_review_status=inspect_capability_registry_review(
⋮----
last_result={}
def run_once(*args)
⋮----
result=run_multi_engine_project(*args)
⋮----
state=run_persistent_project(
improvement=None
improvement_run=None
status=state.get('status')
⋮----
project_state=last_result.get('report') if isinstance(last_result.get('report'),dict) else {}
improvement=_update_improvements(out,state,project_state)
⋮----
improvement_goal_path=out/'.autonomy/improvement-goal.json'
⋮----
backlog=load_improvement_backlog(backlog_path)
⋮----
candidate=active['candidate']
def improvement_project_cycle(_goal_state)
improvement_run=run_active_improvement(
⋮----
# Memory ingestion must happen before autonomous-state persistence so
# every validated artifact produced during this run is durably
# checkpointed before the runner exits.
⋮----
memory=ingest_run(memory,request['id'],out)
⋮----
project_report=(
⋮----
missing=improvement_run['missing_capability']
⋮----
adaptation_state=new_capability_adaptation_state(
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--out',default='studio-output'); args=parser.parse_args(argv)
⋮----
baseline_sha=os.environ.get('GITHUB_SHA','')
⋮----
os.environ['STUDIO_CI_PROVIDER']='github'; os.environ['STUDIO_PERSIST_REMOTE']='1'; result=run(Path(args.request),Path(args.out),baseline_sha=baseline_sha); print(canonical(result)); return 0 if result['status'] in ('complete','disabled') else 1
⋮----
out=Path('studio-output'); out.mkdir(exist_ok=True)
detail=str(exc) if isinstance(exc,StudioError) else type(exc).__name__
⋮----
project_id=os.environ.get('STUDIO_PROJECT_ID','unknown-project')
target_repo=None
request_path=os.environ.get('STUDIO_REQUEST')
⋮----
request=json.loads(Path(request_path).read_text())
project_id=str(request.get('id') or project_id)
target_repo=request.get('target_repo')
````

## File: github_strategy_efficiency_store.py
````python
"""Persist verified strategy-efficiency memory."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/strategy-efficiency.json"
MAX_BYTES = 128 * 1024
⋮----
class StrategyEfficiencyStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean = {}
⋮----
allowed_fields={"samples","successes","ema_cost_seconds","ema_success_rate"}
⋮----
samples=row["samples"]; successes=row["successes"]; cost=row["ema_cost_seconds"]
⋮----
fallback_rate=(successes/samples) if samples else 0.0
recent=row.get("ema_success_rate",fallback_rate)
⋮----
def _ref(github)
⋮----
refs=github.get("/git/matching-refs/heads/"+STATE_BRANCH)
⋮----
exact=[x for x in refs if isinstance(x,dict) and x.get("ref")=="refs/heads/"+STATE_BRANCH]
⋮----
def load(github)
⋮----
ref=_ref(github)
⋮----
head=ref.get("object",{}).get("sha")
⋮----
tree=github.get("/git/trees/"+head+"?recursive=1")
⋮----
item=next((x for x in tree["tree"] if isinstance(x,dict) and x.get("path")==STATE_PATH and x.get("type")=="blob"),None)
⋮----
blob=github.get("/git/blobs/"+item.get("sha",""))
⋮----
raw=base64.b64decode(blob["content"],validate=False)
⋮----
value=json.loads(raw.decode("utf-8"))
⋮----
def save(github,data)
⋮----
data=_validate(data)
⋮----
meta=github.get("")
default=meta.get("default_branch") if isinstance(meta,dict) else None
⋮----
info=github.get("/branches/"+default)
parent=info.get("commit",{}).get("sha") if isinstance(info,dict) else None
⋮----
parent=ref.get("object",{}).get("sha")
⋮----
commit_info=github.get("/git/commits/"+parent)
base_tree=commit_info.get("tree",{}).get("sha") if isinstance(commit_info,dict) else None
⋮----
tree=github.call("POST",github.repo+"/git/trees",{
tree_sha=tree.get("sha") if isinstance(tree,dict) else None
⋮----
commit=github.call("POST",github.repo+"/git/commits",{
commit_sha=commit.get("sha") if isinstance(commit,dict) else None
⋮----
def restore_local(github,path:Path)
⋮----
data=load(github)
path=Path(path)
⋮----
def persist_local(github,path:Path)
⋮----
data=load_local(path) if path.is_file() else {}
````

## File: github_verification_cost_store.py
````python
"""Persist per-toolchain verification cost memory."""
⋮----
STATE_BRANCH = "studio-project-memory"
STATE_PATH = ".studio-memory/verification-cost.json"
MAX_BYTES = 128 * 1024
MAX_ROWS = 64
⋮----
class VerificationCostStoreError(RuntimeError)
⋮----
def _validate(data)
⋮----
clean = {}
⋮----
runs = row["runs"]
successes = row["successes"]
ema = row["ema_seconds"]
⋮----
def _ref(github)
⋮----
refs = github.get("/git/matching-refs/heads/" + STATE_BRANCH)
⋮----
exact = [x for x in refs if isinstance(x, dict) and x.get("ref") == "refs/heads/" + STATE_BRANCH]
⋮----
def load(github)
⋮----
ref = _ref(github)
⋮----
head = ref.get("object", {}).get("sha")
⋮----
tree = github.get("/git/trees/" + head + "?recursive=1")
⋮----
item = next((x for x in tree["tree"] if isinstance(x, dict) and x.get("path") == STATE_PATH and x.get("type") == "blob"), None)
⋮----
blob = github.get("/git/blobs/" + item.get("sha", ""))
⋮----
raw = base64.b64decode(blob["content"], validate=False)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def save(github, data)
⋮----
data = _validate(data)
⋮----
meta = github.get("")
default = meta.get("default_branch") if isinstance(meta, dict) else None
⋮----
info = github.get("/branches/" + default)
parent = info.get("commit", {}).get("sha") if isinstance(info, dict) else None
⋮----
parent = ref.get("object", {}).get("sha")
⋮----
commit_info = github.get("/git/commits/" + parent)
base_tree = commit_info.get("tree", {}).get("sha") if isinstance(commit_info, dict) else None
⋮----
tree = github.call("POST", github.repo + "/git/trees", {
tree_sha = tree.get("sha") if isinstance(tree, dict) else None
⋮----
commit = github.call("POST", github.repo + "/git/commits", {
commit_sha = commit.get("sha") if isinstance(commit, dict) else None
⋮----
def restore_local(github, path: Path)
⋮----
data = load(github)
path = Path(path)
⋮----
def persist_local(github, path: Path)
⋮----
data = load_local(path) if path.is_file() else {}
````

## File: global_admission.py
````python
"""Global admission decisions for autonomous project execution."""
⋮----
DEFAULT_MAX_STANDARD_ADMISSIONS = 3
MIN_USEFUL_ROUND_TOKENS = 16_000
⋮----
def _score(row: dict) -> float
⋮----
priority = max(1, min(100, int(row.get("priority", 50)))) / 100.0
success = max(
efficiency = max(
reliability = max(
requested = max(1, int(row.get("requested_tokens", 1) or 1))
envelope = max(0, int(row.get("token_envelope", 0) or 0))
coverage = min(1.0, envelope / requested)
continuity = 1.10 if row.get("status") in {"running", "deferred", "failed"} else 1.0
⋮----
def decide(projects: list[dict], *, max_standard_admissions: int = DEFAULT_MAX_STANDARD_ADMISSIONS) -> dict
⋮----
slots = max(1, int(max_standard_admissions))
decisions = []
ordinary = []
⋮----
row = dict(raw)
project_id = str(row.get("id") or "").strip()
⋮----
score = _score(row)
⋮----
base = {
⋮----
useful_floor = min(requested, MIN_USEFUL_ROUND_TOKENS)
⋮----
cutoff_score = ordinary[slots - 1]["score"] if len(ordinary) >= slots else None
⋮----
admitted = index < slots
⋮----
def decision_for(report: dict, project_id: str) -> dict | None
⋮----
rows = report.get("decisions") if isinstance(report, dict) else None
````

## File: goal_engine.py
````python
"""Persistent evidence-gated goal state for autonomous studio runs."""
⋮----
VERSION=1
TERMINAL={"complete","human_action_required","blocked"}
⋮----
class GoalStateError(ValueError): pass
⋮----
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _seal(v)
⋮----
x=dict(v); x.pop("state_sha256",None)
⋮----
def new_goal(goal_id,objective,criteria,max_attempts=20)
⋮----
names=set(); normalized=[]
⋮----
n=c["name"]; ev=c["required_evidence"]
⋮----
def validate(state)
⋮----
digest=state.get("state_sha256")
⋮----
unsigned=dict(state); unsigned.pop("state_sha256")
⋮----
def save(path,state)
⋮----
validate(state); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
⋮----
def load(path)
⋮----
try: value=json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
def missing_evidence(state)
⋮----
validate(state); found=state["evidence"]; out=[]
⋮----
def record_cycle(state,evidence=None,failure=None,missing_capability=None,human_action=None,blocked_reason=None,*,count_attempt=True)
⋮----
x={**state,"evidence":dict(state["evidence"]),"failures":list(state["failures"]),"missing_capabilities":list(state["missing_capabilities"]),"history":list(state["history"])}
⋮----
event={"attempt":x["attempt"],"evidence_keys":sorted((evidence or {}).keys())}
⋮----
m=str(missing_capability)
⋮----
def resolve_capability(state,name,evidence=None)
⋮----
x={**state,"evidence":dict(state["evidence"]),"missing_capabilities":list(state["missing_capabilities"]),"history":list(state["history"])}
⋮----
def decide(state)
⋮----
validate(state); missing=missing_evidence(state)
⋮----
def finalize(state)
⋮----
d=decide(state)
⋮----
x=dict(state); x["status"]=d["decision"]; return _seal(x)
⋮----
def resume_human_action(state)
⋮----
x={**state,"history":list(state["history"])}
````

## File: goal_learning.py
````python
"""Evidence-gated learning bridge for autonomous goal cycles."""
⋮----
def _digest(v)
⋮----
def context_for_goal(memory,project_id,tags=None,limit=20)
⋮----
local=query(memory,project_id=project_id,tags=tags)
reusable=reusable_for_project(memory,project_id,tags=tags)
items=(local+reusable)[-limit:]
⋮----
def learn_from_cycle(memory,project_id,goal_state,cycle_result,commit_sha)
⋮----
evidence=cycle_result.get("evidence")
⋮----
attempt=goal_state.get("attempt")
goal_id=goal_state.get("goal_id")
⋮----
summary=cycle_result.get("learning_summary")
⋮----
tags=cycle_result.get("learning_tags") or ["goal-cycle"]
reusable=cycle_result.get("reusable_learning") is True
proof={"tests_passed":True,"commit_sha":commit_sha,"evidence_sha256":_digest(evidence)}
````

## File: goal_loop.py
````python
"""Persistent bounded autonomous goal loop."""
⋮----
def run_goal(goal_path,registry_path,execute_cycle,adapt_capability=None,*,max_cycles=100,context_provider=None,cycle_observer=None,execute_registered_capability=None)
⋮----
goal_path=Path(goal_path); registry_path=Path(registry_path)
state=load_goal(goal_path); registry=load_registry(registry_path)
⋮----
decision=decide(state); action=decision["decision"]
⋮----
state=finalize(state); save_goal(goal_path,state); return state
⋮----
capability=decision["next_action"].removeprefix("adapt:")
⋮----
item=registry["capabilities"][capability]
⋮----
state=record_cycle(state,blocked_reason="registered capability has no runtime:"+capability)
⋮----
result=execute_registered_capability(registry,capability,dict(state))
⋮----
state=record_cycle(state,failure="registered capability execution unverified:"+capability)
⋮----
evidence={"registry_provider":item["provider"],"registry_evidence":item["evidence"],"runtime_evidence":result["evidence"]}
state=resolve_capability(state,capability,evidence)
⋮----
state=record_cycle(state,blocked_reason="no adapter for capability:"+capability)
⋮----
result=adapt_capability(capability,dict(state))
⋮----
state=record_cycle(state,failure="capability adaptation unverified:"+capability)
⋮----
registry=register(registry,capability,str(result["provider"]),result["evidence"])
⋮----
state=resolve_capability(state,capability,result["evidence"])
⋮----
cycle_state=dict(state)
⋮----
context=context_provider(dict(state))
⋮----
result=execute_cycle(cycle_state)
⋮----
# Transient worker/provider failures are retryable. Programming
# errors are deterministic internal defects: fail closed instead
# of burning the entire attempt budget on the same broken code.
kind=type(exc).__name__
⋮----
result={"blocked_reason":"internal_cycle_error:"+kind}
⋮----
result={"failure":"cycle_exception:"+kind}
⋮----
state=record_cycle(state,failure="cycle returned invalid result")
⋮----
state=record_cycle(state,evidence=result.get("evidence"),failure=result.get("failure"),
````

## File: godot_android_export.py
````python
"""Trusted Godot Android export gate.

Downloads the official Godot 4.7.2 export-template archive without credentials,
verifies its release SHA-256, extracts only the Android templates, and exports an
unsigned/debug APK from an ephemeral project copy. Source repositories are never
mounted into the container and no CI credentials are forwarded.
"""
⋮----
TEMPLATE_ASSET = 'Godot_v4.7.2-stable_export_templates.tpz'
TEMPLATE_URL = 'https://github.com/godotengine/godot/releases/download/4.7.2-stable/' + TEMPLATE_ASSET
TEMPLATE_SHA256 = 'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011'
MAX_TEMPLATE_ARCHIVE_BYTES = 1_350_000_000
MAX_TEMPLATE_MEMBER_BYTES = 180_000_000
ANDROID_TEMPLATE_MEMBERS = {
EXPORT_ERROR_MARKERS = ('ERROR:', 'SCRIPT ERROR', 'Parse Error', 'Failed loading resource', 'Export failed')
⋮----
def _archive_ok(path: Path) -> bool
⋮----
def _safe_member(info: zipfile.ZipInfo) -> bool
⋮----
path = PurePosixPath(info.filename)
⋮----
def install_android_templates(cache_dir: Path, opener=urllib.request.urlopen) -> Path
⋮----
cache_dir = cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
archive = cache_dir / TEMPLATE_ASSET
partial = cache_dir / (TEMPLATE_ASSET + '.part')
target = cache_dir / 'android-templates'
⋮----
request = urllib.request.Request(TEMPLATE_URL, headers={'User-Agent':'ai-dev-server-godot-android-export'})
⋮----
total = 0; digest = hashlib.sha256()
⋮----
chunk = response.read(1024 * 1024)
⋮----
staged = cache_dir / 'android-templates.new'
⋮----
found = set()
⋮----
infos = {i.filename:i for i in zf.infolist() if i.filename in ANDROID_TEMPLATE_MEMBERS}
⋮----
def _preset_name(export_presets: str) -> str
⋮----
names = re.findall(r'(?m)^name="([^"]+)"$', export_presets)
platforms = re.findall(r'(?m)^platform="([^"]+)"$', export_presets)
⋮----
android = [name for name, platform in zip(names, platforms) if platform == 'Android']
⋮----
def export_debug_apk(project_root: Path, binary: Path, templates: Path, runner=subprocess.run, timeout=900, artifact_path: Path | None=None) -> dict
⋮----
source = project_root.resolve(); binary = binary.resolve(); templates = templates.resolve()
binary_hash = _trusted_binary_hash(binary)
preset_path = source/'export_presets.cfg'
⋮----
preset = _preset_name(preset_path.read_text())
⋮----
p = templates/name
⋮----
root = Path(tmp); project = root/'project'; home = root/'home'; output = root/'out'
⋮----
version_dir = home/'.local/share/godot/export_templates'/GODOT_VERSION.replace('-stable','.stable')
⋮----
apk = output/'app-debug.apk'
command = ['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=256','--memory=4g','--cpus=2','--network=none',
try: result = runner(command, env=_host_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
⋮----
text = result.stdout.decode(errors='replace')[-32000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-32000:]
passed = result.returncode == 0 and apk.is_file() and apk.stat().st_size > 0 and not any(m in text for m in EXPORT_ERROR_MARKERS)
apk_hash = hashlib.sha256(apk.read_bytes()).hexdigest() if passed else None
preserved = None
⋮----
target = artifact_path.resolve(); target.parent.mkdir(parents=True, exist_ok=True)
⋮----
preserved = str(target)
````

## File: godot_android_stage.py
````python
"""Resumable trusted Android-export stage for Godot studio checkpoints."""
⋮----
req = request_check(req)
⋮----
branch = 'studio/' + req['id']
⋮----
completion = state.get('completion')
⋮----
artifact = out/'app-debug.apk'
⋮----
cache_root = Path(cache)
binary = runtime_installer(cache_root/'runtime')
templates = template_installer(cache_root/'templates')
evidence = exporter(root, binary, templates, artifact_path=artifact)
⋮----
coverage = dict(state.get('coverage') or {})
⋮----
parent = _publish(github, branch, parent, root, state)
⋮----
def main(argv=None) -> int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text()))
state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_baseline.py
````python
"""Read-only, pinned Jumpy baseline. No model calls or repository writes."""
⋮----
def config_check(c)
⋮----
fields = {'repository', 'baseline_commit', 'engine', 'engine_version', 'engine_sha256', 'mode'}
⋮----
def verify_archive(data, digest)
⋮----
def gate_ok(code, log, marker=None)
⋮----
def finance_fix(project)
⋮----
path = project / 'scripts/profile.gd'
original = path.read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
⋮----
before = original.decode()
needle = 'func spend_coins(amount: int) -> bool:\n\tif int(data.coins) < amount:'
⋮----
after = before.replace(needle, needle.replace('if int', 'if amount <= 0 or int'), 1)
⋮----
def main()
⋮----
parser = argparse.ArgumentParser()
⋮----
options = parser.parse_args()
out = Path('studio-output/jumpy-baseline').resolve()
⋮----
report = {'status': 'blocked', 'mode': 'baseline_only',
⋮----
c = config_check(json.loads(Path('control/existing-projects/jumpy.json').read_text()))
⋮----
root = Path(tmp)
home = root / 'home'
⋮----
# No inherited API keys, checkout SSH key, Git config, profile or user saves.
env = {'PATH': os.environ['PATH'], 'HOME': str(home), 'XDG_DATA_HOME': str(home / 'data'),
project = root / 'project'
def run(args, timeout=180)
⋮----
p = subprocess.run(args, env=env, cwd=root, timeout=timeout,
⋮----
version = c['engine_version']
name = f'Godot_v{version}-stable_linux.x86_64'
url = f'https://github.com/godotengine/godot/releases/download/{version}-stable/{name}.zip'
⋮----
data = response.read(200_000_001)
⋮----
archive = root / 'godot.zip'
⋮----
info = z.getinfo(name)
⋮----
binary = root / 'godot'
⋮----
command = [str(binary), '--headless', '--path', str(project),
evidence = out / 'gameplay.json'
⋮----
before = json.loads(evidence.read_text())
expected = ['Negative spending must preserve balance', 'Zero spending must be refused']
⋮----
patch = finance_fix(project)
⋮----
after = json.loads(evidence.read_text())
⋮----
profile = project / 'scripts/profile.gd'
original = profile.read_bytes()
⋮----
expected = [
⋮----
candidate = Path(__file__).with_name('candidates') / 'jumpy_profile_save.gd'
⋮----
gameplay = json.loads(evidence.read_text())
⋮----
patch = ''.join(difflib.unified_diff(original.decode().splitlines(True),
````

## File: godot_device_qa.py
````python
"""Trusted Android-emulator smoke QA for a hashed Godot debug APK.

The APK must match the Android-export evidence before installation. The untrusted app
runs only inside an emulator; CI credentials are not forwarded to Android tooling.
This gate proves install/launch/no-crash/screenshot only. It never claims scripted
journeys or visual acceptance review.
"""
⋮----
SYSTEM_IMAGE = 'system-images;android-35;google_apis;x86_64'
AVD_NAME = 'studio-godot-qa'
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ')
PACKAGE_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$')
⋮----
def _safe_env() -> dict[str, str]
⋮----
allowed = ('PATH','HOME','ANDROID_HOME','ANDROID_SDK_ROOT','JAVA_HOME','TMPDIR')
⋮----
def _run(args: list[str], timeout: int = 120, input_text: str | None = None) -> subprocess.CompletedProcess
⋮----
def package_name(root: Path) -> str
⋮----
preset = root / 'export_presets.cfg'
⋮----
text = preset.read_text(errors='replace')
values = re.findall(r'(?m)^package/unique_name="([^"]+)"$', text)
⋮----
def _start_emulator() -> subprocess.Popen
⋮----
required = ('sdkmanager','avdmanager','emulator','adb')
missing = [name for name in required if shutil.which(name) is None]
⋮----
installed = _run(['sdkmanager', SYSTEM_IMAGE], timeout=900)
⋮----
avd_dir = Path.home()/'.android/avd'/(AVD_NAME + '.avd')
⋮----
created = _run(['avdmanager','create','avd','-n',AVD_NAME,'-k',SYSTEM_IMAGE,'--force'],
⋮----
def _wait_for_boot(adb: str, timeout: int = 240) -> tuple[bool, str | None]
⋮----
start = time.monotonic()
⋮----
devices = _run([adb,'devices'],timeout=15)
serials = [line.split()[0] for line in devices.stdout.splitlines()[1:]
⋮----
serial = serials[0]
boot = _run([adb,'-s',serial,'shell','getprop','sys.boot_completed'],timeout=15)
⋮----
root = root.resolve(); apk = apk.resolve(); out = out.resolve()
⋮----
actual = hashlib.sha256(apk.read_bytes()).hexdigest()
⋮----
pkg = package_name(root)
emulator = None; serial = None
⋮----
existing = _run([adb,'devices'],timeout=20)
serials = [line.split()[0] for line in existing.stdout.splitlines()[1:]
⋮----
emulator = _start_emulator()
⋮----
logs = []
⋮----
# Keep the application offline during untrusted runtime smoke.
⋮----
airplane = _run([adb,'-s',serial,'shell','settings','get','global','airplane_mode_on'],timeout=30)
⋮----
install = _run([adb,'-s',serial,'install','-r','-t',str(apk)],timeout=180)
⋮----
launch = _run([adb,'-s',serial,'shell','monkey','-p',pkg,'-c','android.intent.category.LAUNCHER','1'],timeout=60)
⋮----
screenshot = out/'godot-device.png'
⋮----
shot = subprocess.run([adb,'-s',serial,'exec-out','screencap','-p'],stdout=handle,
⋮----
logcat = _run([adb,'-s',serial,'logcat','-d','-v','brief'],timeout=60)
crashes = [line for line in logcat.stdout.splitlines() if any(marker in line for marker in CRASH_PATTERNS)]
````

## File: godot_device_stage.py
````python
"""Resumable trusted Android device-smoke stage for Godot studio checkpoints."""
⋮----
def _valid_sha(value) -> bool
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']
⋮----
completion=state.get('completion'); export_state=state.get('android_export')
⋮----
apk=out/'app-debug.apk'; expected=export_state['apk_sha256']; reexported=False
local_ok=(apk.is_file() and not apk.is_symlink() and apk.stat().st_size>=1000 and
⋮----
reexported=True
⋮----
cache_root=Path(cache)
binary=runtime_installer(cache_root/'runtime')
templates=template_installer(cache_root/'templates')
evidence=exporter(root,binary,templates,artifact_path=apk)
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
expected=evidence['apk_sha256']
⋮----
export_state=dict(export_state); export_state.update(apk_sha256=expected,reexported_for_device_qa=True)
⋮----
result=device_validator(root,apk,expected,out)
⋮----
coverage=dict(state.get('coverage') or {}); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=False,visual_qa=False)
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text()))
state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_final_review_qa.py
````python
"""Deterministic final review for a Godot Google Play release candidate."""
⋮----
SHA_RE=re.compile(r'^[0-9a-f]{64}$')
REQUIRED_COVERAGE=(
⋮----
def _sha(v)->bool
⋮----
def _verify_file(path:Path,digest:str,label:str)->None
⋮----
def review(root:Path,out:Path,state:dict)->dict
⋮----
coverage=state.get('coverage')
⋮----
missing=[key for key in REQUIRED_COVERAGE if coverage.get(key) is not True]
⋮----
artifact=state.get('release_artifact'); store=state.get('store_metadata'); privacy=state.get('privacy_security')
preflight=state.get('release_preflight'); visual=state.get('visual_qa')
⋮----
aab_hash=artifact.get('aab_sha256'); manifest_hash=store.get('manifest_sha256')
⋮----
shots=visual.get('screenshot_sha256')
⋮----
data_safety=privacy.get('data_safety')
⋮----
bundle={
bundle_sha=hashlib.sha256(json.dumps(bundle,sort_keys=True,separators=(',',':')).encode()).hexdigest()
````

## File: godot_final_review_stage.py
````python
"""Resumable final Godot technical store-readiness review."""
⋮----
def execute(req:dict,root:Path,out:Path,github,reviewer=review)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion')
⋮----
evidence=reviewer(root,out,state); (out/'godot-final-review.json').write_text(canonical(evidence))
⋮----
actions=evidence.get('human_actions_required')
⋮----
coverage=dict(state.get('coverage') or {}); coverage['final_review']=True; state['coverage']=coverage
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
p=argparse.ArgumentParser(); p.add_argument('request'); p.add_argument('--work',required=True); p.add_argument('--out',required=True); a=p.parse_args(argv)
req=request_check(json.loads(Path(a.request).read_text())); state=execute(req,Path(a.work),Path(a.out),GitHub(req['target_repo']))
````

## File: godot_model.py
````python
"""Godot-specific model adapter that preserves the generic model budget and transport."""
⋮----
GODOT_ROLE = {
PATCH_SCHEMA = (
PRODUCT_SCHEMA = (
DESIGN_SCHEMA = 'Return ONLY a JSON object containing the complete Godot-oriented design specification.'
⋮----
class GodotModel(Model)
⋮----
def ask(self, role, context, screenshots=())
⋮----
context = augment(context)
⋮----
error = 'unknown structured-output error'
⋮----
value = self._ask_godot(role, context)
⋮----
error = str(exc)
⋮----
def _ask_godot(self, role: str, context: str) -> dict
⋮----
provider_candidates = tuple(
health_raw = os.environ.get('STUDIO_PROVIDER_HEALTH_PATH', '')
metrics_raw = os.environ.get('STUDIO_PROVIDER_METRICS_PATH', '')
cost_raw = os.environ.get('STUDIO_PROVIDER_COST_PATH', '')
quota_raw = os.environ.get('STUDIO_PROVIDER_MONTHLY_QUOTA_PATH', '')
health_path = Path(health_raw) if health_raw else None
metrics_path = Path(metrics_raw) if metrics_raw else None
cost_path = Path(cost_raw) if cost_raw else None
quota_path = Path(quota_raw) if quota_raw else None
⋮----
provider_costs = load_provider_cost(cost_path) if cost_path is not None else {}
spent_api_cost_usd = sum(
⋮----
max_api_cost_usd = float(os.environ.get('STUDIO_MAX_API_COST_USD', '0') or 0.0)
⋮----
max_api_cost_usd = 0.0
provider_candidates = budget_eligible(
quota_data = load_provider_monthly_quota(quota_path) if quota_path is not None else {'schema': 1, 'months': {}}
⋮----
schema = PATCH_SCHEMA if role in ('implementation', 'tests') else PRODUCT_SCHEMA if role == 'product' else DESIGN_SCHEMA
system_content = GODOT_ROLE[role] + '\n' + schema
response = None
selected_provider = None
selected_model = ''
elapsed = 0.0
last_error = None
primary_provider = self.providers[0] if self.providers else None
⋮----
selected_model = provider.model_for(role, False)
api = self.api if primary_provider is not None and provider == primary_provider else core.API(provider.base, provider.key)
params = {
⋮----
started = time.monotonic()
⋮----
response = api.call('POST', '/chat/completions', params)
⋮----
elapsed = time.monotonic() - started
⋮----
last_error = exc
⋮----
selected_provider = provider
⋮----
usage = response.get('usage') if isinstance(response, dict) else None
⋮----
prompt_tokens = int(usage.get('prompt_tokens', 0) or 0)
completion_tokens = int(usage.get('completion_tokens', 0) or 0)
⋮----
prompt_tokens = completion_tokens = 0
⋮----
call_cost = (
⋮----
choice = response['choices'][0]
⋮----
raw = choice['message'].get('content')
⋮----
raw = raw.strip()
⋮----
raw = raw.split('\n', 1)[1].rsplit('```', 1)[0]
value = json.loads(raw)
````

## File: godot_play_stage.py
````python
"""Trusted Google Play submission stage for a validated Godot release."""
⋮----
def _human_action(state: dict, action: str, detail: str) -> dict
⋮----
req = request_check(req)
⋮----
branch = "studio/" + req["id"]
⋮----
completion = state.get("completion")
⋮----
publication = req.get("play_publish")
⋮----
artifact_info = state.get("release_artifact") or {}
expected_hash = artifact_info.get("aab_sha256")
package_name = artifact_info.get("package")
artifact = out / "app-release.aab"
⋮----
current = os.environ if env is None else env
credentials = publication_credentials(current)
⋮----
commit = publication.get("commit") is True
track = publication.get("track", "internal")
⋮----
evidence = publisher(
⋮----
evidence = dict(evidence)
⋮----
coverage = dict(state.get("coverage") or {})
⋮----
parent = _publish(github, branch, parent, root, state)
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args(argv)
req = request_check(json.loads(Path(args.request).read_text()))
state = execute(req, Path(args.work), Path(args.out), GitHub(req["target_repo"]))
````

## File: godot_preview.py
````python
"""Resumable model-driven preview cycle for an existing Godot repository.

The runner checkpoints only to studio/<request-id>. It never updates the target default
branch and never claims Android export, device QA, visual QA or journey execution.
"""
⋮----
MAX_PUBLISH_FILE_BYTES = 1_000_000
⋮----
files = validate_patch(value, 'godot', role)
root = root.resolve(); targets = []
⋮----
target = (root / item['path']).resolve()
⋮----
def _context(req: dict, state: dict, root: Path) -> str
⋮----
files = {}
⋮----
rel = path.relative_to(root).as_posix()
⋮----
def _exact_branch_ref(github, branch: str)
⋮----
refs = github.get('/git/matching-refs/heads/' + branch)
⋮----
exact = [item for item in refs if isinstance(item, dict) and item.get('ref') == 'refs/heads/' + branch]
⋮----
def _restore(github, branch: str, root: Path) -> tuple[dict | None, str, bool]
⋮----
metadata = github.get('')
⋮----
branch_ref = _exact_branch_ref(github, branch)
⋮----
parent = branch_ref.get('object', {}).get('sha')
⋮----
source_ref = parent; existing_checkpoint = True
⋮----
default = metadata.get('default_branch')
⋮----
branch_info = github.get('/branches/' + default)
parent = branch_info.get('commit', {}).get('sha') if isinstance(branch_info, dict) else None
⋮----
source_ref = parent; existing_checkpoint = False
tree = github.get('/git/trees/' + source_ref + '?recursive=1')
⋮----
import_plan = plan(tree, expected_engine='godot')
⋮----
state = None
state_path = root / '.studio/state.json'
⋮----
state = json.loads(state_path.read_text())
⋮----
def _publish(github, branch: str, parent: str, root: Path, state: dict) -> str
⋮----
current = _exact_branch_ref(github, branch)
⋮----
current_sha = current.get('object', {}).get('sha')
⋮----
entries = []
⋮----
content = path.read_bytes()
⋮----
text = content.decode('utf-8')
⋮----
base_tree = github.get('/git/commits/' + parent).get('tree', {}).get('sha')
⋮----
tree = github.call('POST', github.repo + '/git/trees', {'base_tree':base_tree,'tree':entries})
tree_sha = tree.get('sha') if isinstance(tree, dict) else None
⋮----
commit = github.call('POST', github.repo + '/git/commits', {'message':'Godot studio: ' + state['status'],'tree':tree_sha,'parents':[parent]})
commit_sha = commit.get('sha') if isinstance(commit, dict) else None
⋮----
def execute(req: dict, root: Path, out: Path, github, model_factory=GodotModel, sandbox_factory=GodotSandbox) -> dict
⋮----
req = request_check(req)
⋮----
branch = 'studio/' + req['id']
⋮----
fingerprint = hashlib.sha256(canonical({k:v for k,v in req.items() if k != 'enabled'}).encode()).hexdigest()
⋮----
state = state or {'request_hash':fingerprint,'status':'pending','engine':'godot','cycles':0,'rounds':0,'blockers':[]}
⋮----
architecture_recommendations = recommend(
architecture_root = architecture_learning_root(out)
historical_learning = summarize_architecture_learning(architecture_root)
safe_rewrite_learning_path = out / '.autonomy' / 'safe-rewrite-learning.json'
⋮----
model = model_factory(req['max_calls']); sandbox = sandbox_factory(root); sandbox.create(req['app_name'])
⋮----
def checkpoint() -> None
⋮----
parent = _publish(github, branch, parent, root, state)
⋮----
result = model.ask(role, _context(req,state,root))
⋮----
implementation_context = _context(req,state,root)
patch = model.ask('implementation', implementation_context)
⋮----
event = {
⋮----
retry_patch = model.ask(
⋮----
event_id = f"{req['id']}:{state['rounds']}:godot"
model_name = str(getattr(model, 'models_used', {}).get('implementation') or 'unknown')
⋮----
qa = model.ask('tests', _context(req,state,root)); _safe_apply(
⋮----
try: journeys = validate_journeys(state['product'].get('journeys'))
⋮----
pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
⋮----
review = verdict(model.ask('review', _context(req,state,root))); state['code_review'] = review
````

## File: godot_privacy_security_qa.py
````python
"""Trusted privacy and security audit for Godot Play releases."""
⋮----
SECRET_PATTERNS=(
DANGEROUS_MARKERS=('OS.execute(','OS.shell_open(','JavaScriptBridge','GDExtension')
CLEARTEXT_RE=re.compile(r'http://(?!schemas\.android\.com)[A-Za-z0-9.-]+(?::\d+)?(?:/[^\s"\']*)?')
⋮----
def _sha(value)->bool
⋮----
def _source_files(root:Path)->list[Path]
⋮----
files=[]
⋮----
p=root/rel
⋮----
base=root/folder
⋮----
def audit(root:Path,out:Path,state:dict)->dict
⋮----
artifact=state.get('release_artifact') or {}; store=state.get('store_metadata') or {}
aab_hash=artifact.get('aab_sha256'); manifest_hash=store.get('manifest_sha256')
⋮----
aab=out/'app-release.aab'; manifest=out/'play-store-godot'/'manifest.json'
⋮----
chunks=[]; scanned=[]
⋮----
text=p.read_text(errors='replace'); chunks.append(text); scanned.append(p.relative_to(root).as_posix())
source='\n'.join(chunks)
secret_hits=sum(1 for pattern in SECRET_PATTERNS if pattern.search(source))
dangerous=sorted(marker for marker in DANGEROUS_MARKERS if marker in source)
cleartext=sorted(set(CLEARTEXT_RE.findall(source)))
privacy=privacy_classification(root)
blockers=[]
⋮----
policy_dir=out/'privacy-godot'; policy_dir.mkdir(parents=True,exist_ok=True)
data_safety={
⋮----
title=(store.get('listing') or {}).get('title') or 'Mobile App'
policy=(f'# Privacy Policy for {title}\n\n'
````

## File: godot_privacy_security_stage.py
````python
"""Resumable Godot privacy/security stage bound to release/store hashes."""
⋮----
def execute(req:dict,root:Path,out:Path,github,auditor=audit)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion'); coverage=state.get('coverage') or {}
⋮----
evidence=auditor(root,out,state); (out/'godot-privacy-security.json').write_text(canonical(evidence))
⋮----
artifact=state.get('release_artifact') or {}; store=state.get('store_metadata') or {}
⋮----
coverage=dict(coverage); coverage.update(privacy_qa=True,security_qa=True)
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
p=argparse.ArgumentParser(); p.add_argument('request'); p.add_argument('--work',required=True); p.add_argument('--out',required=True); a=p.parse_args(argv)
req=request_check(json.loads(Path(a.request).read_text())); state=execute(req,Path(a.work),Path(a.out),GitHub(req['target_repo']))
````

## File: godot_release_artifact_stage.py
````python
"""Resumable signed AAB artifact stage with isolated signing boundary."""
⋮----
def _sha(value)->bool
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion'); preflight=state.get('release_preflight')
⋮----
current=os.environ if env is None else env
credentials=signing_credentials(current)
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent; (out/'report.json').write_text(canonical(state)); return state
keystore=Path(current['GODOT_ANDROID_KEYSTORE_RELEASE_PATH']); alias=current['GODOT_ANDROID_KEYSTORE_RELEASE_USER']; password=current['GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD']
unsigned=out/'app-unsigned.aab'; signed=out/'app-release.aab'
⋮----
cache=Path(td); binary=runtime_installer(cache/'runtime'); source_template=source_installer(cache/'templates')
build=builder(root,binary,source_template,unsigned)
⋮----
signed_evidence=signer(unsigned,signed,keystore,alias,password)
⋮----
coverage=dict(state.get('coverage') or {}); coverage.update(release_artifact=True,release_signed=True)
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_release_artifact.py
````python
"""Build an unsigned Godot AAB without secrets, then sign only the artifact.

The untrusted project executes only inside a pinned container with networking disabled
and receives no production signing material. The upload keystore is exposed later only
to jarsigner/keytool operating on the already-built AAB, never to Godot or Gradle.
"""
⋮----
SOURCE_MEMBER='templates/android_source.zip'
MAX_SOURCE_TEMPLATE_BYTES=900_000_000
AAB_MAX_BYTES=1_500_000_000
CERT_RE=re.compile(r'SHA256:\s*([0-9A-Fa-f:]{59,95})')
⋮----
def _archive_ok(path:Path)->bool
⋮----
def _download_archive(cache_dir:Path,opener=urllib.request.urlopen)->Path
⋮----
cache=cache_dir.resolve(); cache.mkdir(parents=True,exist_ok=True)
archive=cache/TEMPLATE_ASSET; partial=cache/(TEMPLATE_ASSET+'.part'); partial.unlink(missing_ok=True)
⋮----
req=urllib.request.Request(TEMPLATE_URL,headers={'User-Agent':'ai-dev-server-godot-release-artifact'})
⋮----
total=0; digest=hashlib.sha256()
⋮----
chunk=response.read(1024*1024)
⋮----
def install_source_template(cache_dir:Path,opener=urllib.request.urlopen)->Path
⋮----
archive=_download_archive(cache_dir,opener)
target=cache_dir.resolve()/'android_source.zip'; staged=cache_dir.resolve()/'android_source.zip.part'; staged.unlink(missing_ok=True)
⋮----
matches=[i for i in zf.infolist() if i.filename==SOURCE_MEMBER]
⋮----
info=matches[0]; path=PurePosixPath(info.filename)
⋮----
def _unsigned_preset(project:Path)->str
⋮----
preset_path=project/'export_presets.cfg'
⋮----
text=preset_path.read_text(); preset=_preset_name(text)
required={
⋮----
pattern=re.compile(r'^'+re.escape(key)+r'=.*$',re.M)
⋮----
text=pattern.sub(key+'='+value,text,count=1)
⋮----
source=project_root.resolve(); binary=binary.resolve(); source_template=source_template.resolve()
binary_hash=_trusted_binary_hash(binary)
⋮----
root=Path(td); project=root/'project'; home=root/'home'; output=root/'out'; project.mkdir(); home.mkdir(); output.mkdir()
_copy_project(source,project); preset=_unsigned_preset(project)
version_dir=home/'.local/share/godot/export_templates'/GODOT_VERSION.replace('-stable','.stable'); version_dir.mkdir(parents=True)
⋮----
aab=output/'app-unsigned.aab'
command=['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=512','--memory=6g','--cpus=2','--network=none',
try: result=runner(command,env=_host_env(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
⋮----
output_text=result.stdout.decode(errors='replace')[-32000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-32000:]
passed=result.returncode==0 and aab.is_file() and 0<aab.stat().st_size<=AAB_MAX_BYTES and 'ERROR:' not in output_text and 'Export failed' not in output_text
digest=hashlib.sha256(aab.read_bytes()).hexdigest() if passed else None
⋮----
target=artifact_path.resolve(); target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(aab,target)
````

## File: godot_release_qa.py
````python
"""Trusted Google Play release preflight for Godot Android projects.

This layer only normalizes non-secret export settings and validates release identity.
It never invents or generates production signing credentials and does not claim that an
AAB was built. Actual signed bundle export is a separate evidence stage.
"""
⋮----
MIN_PLAY_TARGET_API = 36
PACKAGE_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+$')
⋮----
def _replace(text:str,key:str,value:str)->str
⋮----
pattern=re.compile(r'^'+re.escape(key)+r'=.*$',re.M)
replacement=key+'='+value
⋮----
def prepare_store_preset(root:Path)->dict
⋮----
path=root/'export_presets.cfg'
⋮----
original=path.read_text()
⋮----
text=original
text=_replace(text,'gradle_build/use_gradle_build','true')
text=_replace(text,'gradle_build/export_format','1')
text=_replace(text,'gradle_build/target_sdk','"36"')
text=_replace(text,'architectures/arm64-v8a','true')
text=_replace(text,'package/signed','true')
⋮----
def _value(text:str,key:str)->str
⋮----
match=re.search(r'^'+re.escape(key)+r'=(.*)$',text,re.M)
⋮----
def audit_store_preset(root:Path)->dict
⋮----
text=path.read_text()
blockers=[]
package=_value(text,'package/unique_name').strip('"')
version_name=_value(text,'version/name').strip('"')
try: version_code=int(_value(text,'version/code').strip('"'))
except ValueError: version_code=0
target=_value(text,'gradle_build/target_sdk').strip('"')
try: target_api=int(target)
except ValueError: target_api=0
⋮----
def signing_credentials(env:dict|None=None)->dict
⋮----
env=os.environ if env is None else env
names=('GODOT_ANDROID_KEYSTORE_RELEASE_PATH','GODOT_ANDROID_KEYSTORE_RELEASE_USER','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD')
present={name:bool(isinstance(env.get(name),str) and env.get(name)) for name in names}
⋮----
path=Path(env[names[0]])
⋮----
def preflight(root:Path,env:dict|None=None)->dict
⋮----
normalization=prepare_store_preset(root)
audit=audit_store_preset(root)
signing=signing_credentials(env)
passed=audit['passed'] and signing['available']
blockers=list(audit['blockers'])
````

## File: godot_release_stage.py
````python
"""Resumable Play release preflight for validated Godot visual checkpoints."""
⋮----
def execute(req:dict,root:Path,out:Path,github,validator=preflight)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion'); coverage=state.get('coverage') or {}
⋮----
evidence=validator(root)
⋮----
audit=evidence.get('audit') if isinstance(evidence,dict) else None
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_repository_probe.py
````python
"""Probe a pinned public Godot repository through the trusted import/runtime boundary."""
⋮----
MAX_RESPONSE_BYTES = 8_000_000
REPO_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9][A-Za-z0-9_.-]*')
SHA_RE = re.compile(r'[0-9a-f]{40}')
⋮----
def _get_json(url: str) -> dict
⋮----
req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'ai-dev-server-godot-probe'})
⋮----
raw = response.read(MAX_RESPONSE_BYTES + 1)
⋮----
value = json.loads(raw)
⋮----
def probe(repo: str, commit: str, fetch_json=_get_json) -> dict
⋮----
base = 'https://api.github.com/repos/' + repo
tree = fetch_json(base + '/git/trees/' + commit + '?recursive=1')
⋮----
import_plan = plan(tree, expected_engine='godot')
⋮----
root = Path(td) / 'project'
⋮----
def fetch_blob(sha: str) -> dict
⋮----
sandbox = GodotSandbox(root)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
result = probe(args.repository, args.commit)
text = canonical(result)
````

## File: godot_runtime_journey_stage.py
````python
"""Resumable trusted execution stage for immutable Godot acceptance journeys."""
⋮----
def execute(req:dict,root:Path,out:Path,github,runtime_installer=install,journey_runner=run_journeys)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion')
⋮----
product=state.get('product')
⋮----
try: journeys=validate_journeys(product.get('journeys'))
⋮----
binary=runtime_installer(Path(cache)); evidence=journey_runner(root,binary,journeys)
⋮----
expected=[item['id'] for item in journeys]
⋮----
coverage=dict(state.get('coverage') or {}); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=True,visual_qa=False)
⋮----
state['release_status']='not_store_ready'; parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_runtime_journeys.py
````python
"""Execute immutable Godot acceptance journeys inside an isolated runtime copy.

The harness is trusted factory code injected only into an ephemeral project copy.
Journey JSON is data, never generated GDScript. Project code runs with Docker networking
disabled and without CI credentials. Selectors are exact unique Godot Node.name values.
"""
⋮----
PASS_RE = re.compile(r'^STUDIO_JOURNEY_PASS:([a-z][a-z0-9_-]{0,39})$', re.M)
FAIL_RE = re.compile(r'^STUDIO_JOURNEY_FAIL:([a-z][a-z0-9_-]{0,39}):(.+)$', re.M)
COMPLETE_RE = re.compile(r'^STUDIO_JOURNEYS_COMPLETE:(\d+)$', re.M)
BLOCKING_MARKERS = ('SCRIPT ERROR','Parse Error','Cannot parse','Failed loading resource')
⋮----
HARNESS = r'''extends SceneTree
⋮----
def run_journeys(project_root: Path, binary: Path, journeys: list[dict], runner=subprocess.run, timeout=600) -> dict
⋮----
journeys = validate_journeys(journeys)
source = project_root.resolve(); binary = binary.resolve(); binary_hash = _trusted_binary_hash(binary)
⋮----
project = Path(tmp)/'project'; project.mkdir(); _copy_project(source,project)
⋮----
command=['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges',
⋮----
result=runner(command,env=_host_env(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
⋮----
output=result.stdout.decode(errors='replace')[-48000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-48000:]
passes=PASS_RE.findall(output); failures=[{'id':jid,'reason':reason[:300]} for jid,reason in FAIL_RE.findall(output)]
complete=COMPLETE_RE.findall(output)
expected=[item['id'] for item in journeys]
passed=(result.returncode==0 and not failures and passes==expected and complete==[str(len(expected))]
````

## File: godot_runtime.py
````python
"""Pinned, credential-free Godot validation runtime.

Godot executes project scripts during import, so untrusted project code never runs on
the privileged CI host. The trusted host downloads the official editor asset without
credentials, verifies its release SHA-256, then executes it inside the digest-pinned
studio container with networking disabled. The source project is never mounted into
the container: a bounded, symlink-free temporary copy is used instead.
"""
⋮----
GODOT_VERSION = '4.7.2-stable'
GODOT_ASSET = 'Godot_v4.7.2-stable_linux.x86_64.zip'
GODOT_BINARY = 'Godot_v4.7.2-stable_linux.x86_64'
GODOT_URL = 'https://github.com/godotengine/godot/releases/download/4.7.2-stable/' + GODOT_ASSET
GODOT_ARCHIVE_SHA256 = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'
MAX_ARCHIVE_BYTES = 90_000_000
MAX_BINARY_BYTES = 160_000_000
MAX_PROJECT_ENTRIES = 4000
MAX_PROJECT_BYTES = 160_000_000
BLOCKING_MARKERS = ('SCRIPT ERROR', 'Parse Error', 'Cannot parse', 'Failed loading resource')
⋮----
def _host_env()
⋮----
def _safe_member(info: zipfile.ZipInfo) -> bool
⋮----
path = PurePosixPath(info.filename)
⋮----
def _archive_ok(path: Path) -> bool
⋮----
def install(cache_dir: Path, opener=urllib.request.urlopen) -> Path
⋮----
cache_dir = cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
archive = cache_dir / GODOT_ASSET
binary = cache_dir / GODOT_BINARY
binary_digest = cache_dir / (GODOT_BINARY + '.sha256')
tmp = cache_dir / (GODOT_ASSET + '.part')
⋮----
request = urllib.request.Request(GODOT_URL, headers={'User-Agent': 'ai-dev-server-godot-runtime'})
⋮----
total = 0
⋮----
chunk = response.read(1024 * 1024)
⋮----
members = zf.infolist()
⋮----
extracted = cache_dir / (GODOT_BINARY + '.new')
⋮----
binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
⋮----
def _trusted_binary_hash(binary: Path) -> str
⋮----
digest_file = binary.with_name(binary.name + '.sha256')
⋮----
expected = digest_file.read_text().strip()
⋮----
actual = hashlib.sha256(binary.read_bytes()).hexdigest()
⋮----
def _copy_project(source: Path, destination: Path) -> None
⋮----
source = source.resolve(); destination = destination.resolve()
⋮----
entries = 0; total = 0
⋮----
rel = path.relative_to(source)
target = destination / rel
⋮----
size = path.stat().st_size; total += size
⋮----
def docker_command(sandbox_project: Path, binary: Path) -> list[str]
⋮----
sandbox_project = sandbox_project.resolve(); binary = binary.resolve()
⋮----
def validate(project_root: Path, binary: Path, runner=subprocess.run, timeout=600) -> dict
⋮----
source = project_root.resolve(); binary = binary.resolve()
binary_hash = _trusted_binary_hash(binary)
⋮----
sandbox_project = Path(tmp) / 'project'
⋮----
command = docker_command(sandbox_project, binary)
⋮----
result = runner(command, env=_host_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
⋮----
output = result.stdout.decode(errors='replace')[-24000:] if isinstance(result.stdout, bytes) else str(result.stdout or '')[-24000:]
blocked = result.returncode != 0 or any(marker in output for marker in BLOCKING_MARKERS)
````

## File: godot_session.py
````python
"""Trusted Godot session adapter for the generic studio.

This adapter deliberately exposes only validation. Android export, rendering and device QA
remain separate completion capabilities and are not implied by a successful headless gate.
"""
⋮----
class GodotSandbox
⋮----
def __init__(self, root: Path)
⋮----
def create(self, name: str) -> None
⋮----
def gates(self, name: str, journeys) -> tuple[bool, list[dict]]
⋮----
# journeys are retained in the generic contract but headless Godot validation does
# not claim to execute user journeys. Runtime/device journey QA is a later gate.
⋮----
binary = install(Path(cache))
result = validate(self.root, binary, timeout=600)
evidence = {
````

## File: godot_store_metadata_qa.py
````python
"""Build fail-closed Google Play metadata from validated Godot evidence."""
⋮----
NETWORK_MARKERS = (
SENSITIVE_PERMISSIONS = (
⋮----
def _sha(value)->bool
⋮----
def _project_text(root:Path)->str
⋮----
chunks=[]
⋮----
p=root/rel
⋮----
base=root/folder
⋮----
def privacy_classification(root:Path)->dict
⋮----
text=_project_text(root)
network=sorted(marker for marker in NETWORK_MARKERS if marker in text)
preset=root/'export_presets.cfg'
custom=[]
⋮----
raw=preset.read_text(errors='replace')
m=re.search(r'(?m)^permissions/custom_permissions=PackedStringArray\((.*)\)$',raw)
⋮----
custom=sorted(set(re.findall(r'"([^"]+)"',m.group(1))))
sensitive=sorted(p for p in custom if any(name in p for name in SENSITIVE_PERMISSIONS))
safe=not network and not sensitive
⋮----
def _validated_screens(out:Path,state:dict)->list[Path]
⋮----
visual=state.get('visual_qa') or {}
expected=visual.get('screenshot_sha256')
⋮----
found=[]
⋮----
digest=hashlib.sha256(p.read_bytes()).hexdigest()
⋮----
by_hash={d:p for d,p in found}
⋮----
found=[(h,by_hash[h]) for h in expected]
device=state.get('device_qa') or {}
device_hash=device.get('screenshot_sha256')
device_path=out/'godot-device.png'
⋮----
def build(req:dict,root:Path,out:Path,state:dict)->dict
⋮----
artifact=state.get('release_artifact') or {}
⋮----
listing=listing_from_state(req,state)
store=out/'play-store-godot'; shots=store/'screenshots'/'phone'; shots.mkdir(parents=True,exist_ok=True)
screen_evidence=[]
⋮----
icon=store/'icon-512.png'; feature=store/'feature-graphic-1024x500.png'
⋮----
privacy=privacy_classification(root)
listing_dir=store/'listing'/'en-US'; listing_dir.mkdir(parents=True,exist_ok=True)
⋮----
manifest={
path=store/'manifest.json'; path.write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
````

## File: godot_store_metadata_stage.py
````python
"""Resumable Godot Play metadata stage."""
⋮----
def execute(req:dict,root:Path,out:Path,github,builder=build)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion'); coverage=state.get('coverage') or {}
⋮----
evidence=builder(req,root,out,state)
⋮----
coverage=dict(coverage); coverage.update(store_metadata=True)
⋮----
parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text()))
state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: godot_visual_qa.py
````python
"""Trusted Android-rendered visual QA for Godot acceptance journeys.

A temporary project copy is instrumented with a trusted scene runner. The debug APK
executes immutable journey JSON on an offline emulator, captures each final frame into
user://, and the host retrieves those PNGs with run-as. Production source is never
modified and CI credentials are never forwarded to Android tooling.
"""
⋮----
PASS_RE = re.compile(r'^STUDIO_VISUAL_PASS:([a-z][a-z0-9_-]{0,39})$', re.M)
COMPLETE_RE = re.compile(r'^STUDIO_VISUAL_COMPLETE:(\d+)$', re.M)
PNG_SIG = b'\x89PNG\r\n\x1a\n'
⋮----
HARNESS = r'''extends Node
⋮----
SCENE = '''[gd_scene load_steps=2 format=3]\n\n[ext_resource path="res://.studio_visual_runner.gd" type="Script" id="1"]\n\n[node name="StudioVisualRunner" type="Node"]\nscript = ExtResource("1")\n'''
⋮----
def _safe_env() -> dict[str,str]
⋮----
def _run(args, timeout=120, **kwargs)
⋮----
def _instrument(source: Path, destination: Path, journeys: list[dict]) -> None
⋮----
project = destination/'project.godot'
⋮----
text = project.read_text()
match = re.search(r'^run/main_scene\s*=\s*"([^"]+)"\s*$', text, re.M)
⋮----
original = match.group(1)
⋮----
text = text[:match.start()] + 'run/main_scene="res://.studio_visual_runner.tscn"' + text[match.end():]
⋮----
def _pull_png(adb: str, serial: str, package: str, jid: str, target: Path) -> None
⋮----
proc = _run([adb,'-s',serial,'exec-out','run-as',package,'cat','files/studio-visual-'+jid+'.png'],timeout=60)
data = proc.stdout if isinstance(proc.stdout,bytes) else (proc.stdout or '').encode()
⋮----
journeys=validate_journeys(journeys)
⋮----
temp=Path(td); project=temp/'project'; project.mkdir(); _instrument(source,project,journeys)
runtime=runtime_installer(temp/'runtime'); templates=template_installer(temp/'templates'); apk=temp/'visual.apk'
export=exporter(project,runtime,templates,artifact_path=apk)
⋮----
package=package_name(project)
adb=shutil.which('adb') or 'adb'
devices=runner([adb,'devices'],timeout=30)
raw=devices.stdout.decode(errors='replace') if isinstance(devices.stdout,bytes) else str(devices.stdout or '')
serials=[line.split()[0] for line in raw.splitlines()[1:] if '\tdevice' in line]
⋮----
serial=serials[0]
⋮----
install_result=runner([adb,'-s',serial,'install','-r','-t',str(apk)],timeout=180)
⋮----
launch=runner([adb,'-s',serial,'shell','monkey','-p',package,'-c','android.intent.category.LAUNCHER','1'],timeout=60)
⋮----
logs=runner([adb,'-s',serial,'logcat','-d','-v','brief'],timeout=60)
log_text=logs.stdout.decode(errors='replace') if isinstance(logs.stdout,bytes) else str(logs.stdout or '')
expected=[j['id'] for j in journeys]; passed=PASS_RE.findall(log_text); complete=COMPLETE_RE.findall(log_text)
⋮----
shots=[]
⋮----
shot=out/('godot-visual-'+jid+'.png'); _pull_png(adb,serial,package,jid,shot); shots.append(shot)
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in shots]
⋮----
model=model_factory(4)
context='Review these actual Android-rendered Godot journey end-state screenshots against this design. Reject clipping, illegibility, poor contrast, inconsistent spacing, broken layout, or visibly unfinished UI. Design JSON: '+canonical(design)
verdict=model.ask('visual',context,shots)
````

## File: godot_visual_stage.py
````python
"""Resumable Android-rendered visual acceptance stage for Godot checkpoints."""
⋮----
def execute(req:dict,root:Path,out:Path,github,visual_validator=capture_and_review)->dict
⋮----
req=request_check(req); root.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
⋮----
branch='studio/'+req['id']; state,parent,checkpoint=_restore(github,branch,root)
⋮----
completion=state.get('completion'); coverage=state.get('coverage') or {}
⋮----
product=state.get('product'); design=state.get('design')
⋮----
try: journeys=validate_journeys(product.get('journeys'))
⋮----
evidence=visual_validator(root,journeys,design,out)
⋮----
expected=[item['id'] for item in journeys]
⋮----
hashes=evidence.get('screenshot_sha256')
⋮----
coverage=dict(coverage); coverage.update(engine='godot',android_export=True,device_qa=True,journeys_executed=True,visual_qa=True)
⋮----
state['release_status']='not_store_ready'; parent=_publish(github,branch,parent,root,state); state['checkpoint_commit']=parent
⋮----
def main(argv=None)->int
⋮----
parser=argparse.ArgumentParser(); parser.add_argument('request'); parser.add_argument('--work',required=True); parser.add_argument('--out',required=True); args=parser.parse_args(argv)
req=request_check(json.loads(Path(args.request).read_text())); state=execute(req,Path(args.work),Path(args.out),GitHub(req['target_repo']))
````

## File: human_input_request.py
````python
"""Render the only permitted human handoff for autonomous projects.

The factory should continue by itself whenever it can. This module is used only
when an external secret, identity, payment, legal approval, store action, or
other non-automatable prerequisite is genuinely required.
"""
⋮----
SECRET_HINTS = {
⋮----
_HUMAN_PATTERNS = (
_SECRET_SUFFIXES = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "CREDENTIALS")
_ENV_NAME_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
_SAFE_ACTION_RE = re.compile(r"^[a-z][a-z0-9_.:-]{0,127}$")
⋮----
def requires_human_input(detail: object) -> bool
⋮----
text = str(detail or "").lower()
⋮----
def requested_secret_names(detail: object) -> list[str]
⋮----
"""Return exact environment-variable names without inspecting their values."""
text = str(detail or "")
names: list[str] = []
⋮----
def _reason_category(detail: object) -> str
⋮----
def safe_handoff_detail(detail: object) -> str
⋮----
"""Keep safe action identifiers, but never persist secret-bearing/free-form detail."""
text = str(detail or "").strip()
names = requested_secret_names(text)
⋮----
def _requested_items(detail: str) -> list[str]
⋮----
names = requested_secret_names(detail)
⋮----
category = _reason_category(detail)
instructions = {
⋮----
def render(project_id: str, detail: str, *, target_repo: str | None = None) -> str
⋮----
items = _requested_items(detail)
⋮----
target = target_repo or "unknown"
lines = [
⋮----
def write_request(out: Path, project_id: str, detail: str, *, target_repo: str | None = None) -> Path
⋮----
out = Path(out)
⋮----
reason_category = _reason_category(detail)
text_path = out / "USER_INPUT_REQUIRED.txt"
⋮----
machine = {
⋮----
def prerequisite_satisfied(detail: str) -> bool
````

## File: idempotent_model.py
````python
"""Checkpointed model calls that can be safely replayed after a crash."""
⋮----
def _screenshots_fingerprint(screenshots) -> list[dict]
⋮----
result = []
⋮----
path = Path(item)
data = path.read_bytes()
⋮----
def ask(model, role: str, context: str, screenshots=(), *, namespace: str = "model") -> tuple[dict, bool, str]
⋮----
key = operation_key(namespace, {
cached = get(key)
⋮----
value = cached.get("response")
⋮----
value = model.ask(role, context, screenshots)
⋮----
def ask_value(model, role: str, context: str, screenshots=(), *, namespace: str = "model") -> dict
````

## File: immutable_artifact_cache.py
````python
"""Immutable artifact cache bound to a full validation key."""
⋮----
SCHEMA = 2
MAX_ENTRIES = 32
MAX_TOTAL_BYTES = 64 * 1024 * 1024
APK_REL = "build/app/outputs/flutter-apk/app-debug.apk"
GOLDEN_DIR = "test/goldens"
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_ARTIFACT_CACHE_PATH", "")
⋮----
def _read_artifacts(root: Path) -> dict[str, bytes]
⋮----
root = root.resolve()
files: dict[str, bytes] = {}
apk = root / APK_REL
⋮----
goldens = root / GOLDEN_DIR
⋮----
def capture(root: Path, validation_key: str, *, rebuild_cost_seconds: float = 0.0, entries: dict | None = None) -> dict
⋮----
files = _read_artifacts(root)
apk = files.get(APK_REL)
⋮----
goldens = [rel for rel in files if rel.startswith(GOLDEN_DIR + "/") and rel.endswith(".png")]
⋮----
total = sum(len(data) for data in files.values())
⋮----
def _projected_entry_value(files: dict[str, bytes], rebuild_cost_seconds: float) -> float
⋮----
value = 0.0
⋮----
size_mb = max(1.0, len(data) / (1024.0 * 1024.0))
⋮----
def missing_bytes_now()
⋮----
missing = 0
⋮----
digest = hashlib.sha256(data).hexdigest()
⋮----
exists = cas_blob_path(digest).is_file()
⋮----
exists = False
⋮----
quota = min(MAX_TOTAL_BYTES, MAX_CAS_BYTES)
⋮----
projected = _projected_entry_value(files, rebuild_cost_seconds)
⋮----
victims = [
⋮----
def verify_entry(entry: dict, validation_key: str) -> dict[str, bytes]
⋮----
rows = entry.get("files")
⋮----
decoded: dict[str, bytes] = {}
total = 0
⋮----
data = cas_get(meta["sha256"], meta["size"])
⋮----
def restore(root: Path, entry: dict, validation_key: str) -> dict
⋮----
files = verify_entry(entry, validation_key)
⋮----
restored = []
apk_sha256 = None
⋮----
path = root / rel
⋮----
meta = entry["files"][rel]
restored_bytes = path.read_bytes()
⋮----
apk_sha256 = meta["sha256"]
⋮----
def load() -> dict
⋮----
path = _path()
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
entries = data.get("entries")
⋮----
def _referenced_digests(entries: dict) -> set[str]
⋮----
result = set()
⋮----
files = entry.get("files")
⋮----
digest = meta.get("sha256")
⋮----
def touch(entries: dict, validation_key: str) -> None
⋮----
value = entries.pop(validation_key)
⋮----
def _entry_value(entry: dict) -> float
⋮----
files = entry.get("files", {}) if isinstance(entry, dict) else {}
scores = []
⋮----
def _trim_by_value(entries: dict) -> dict
⋮----
ranked = []
order = {key: index for index, key in enumerate(entries)}
⋮----
kept = {}
kept_digests = set()
used_bytes = 0
⋮----
files = entry.get("files", {})
new_bytes = 0
new_digests = set()
valid = True
⋮----
valid = False
⋮----
size = meta.get("size")
⋮----
def save(entries: dict) -> None
⋮----
merged = load()
⋮----
trimmed = _trim_by_value(merged)
⋮----
payload = {"schema": SCHEMA, "entries": trimmed}
raw = canonical(payload).encode("utf-8")
````

## File: improvement_backlog.py
````python
"""Persistent integrity-sealed backlog for evidence-derived improvements."""
⋮----
VERSION=1
STATUSES={"queued","active","proved","rejected"}
⋮----
class ImprovementBacklogError(ValueError)
⋮----
def _canon(value)
⋮----
def _seal(value)
⋮----
out=dict(value)
⋮----
def new_backlog()
⋮----
def validate(backlog)
⋮----
digest=backlog.get("backlog_sha256")
unsigned=dict(backlog); unsigned.pop("backlog_sha256",None)
⋮----
ids=set()
active=0
⋮----
required={"candidate","status","proof"}
⋮----
candidate=item["candidate"]
⋮----
def merge_assessment(backlog,assessment)
⋮----
existing={item["candidate"]["id"] for item in backlog["items"]}
items=[{"candidate":dict(item["candidate"]),"status":item["status"],"proof":dict(item["proof"])}
⋮----
def activate_next(backlog)
⋮----
items=[]
activated=False
⋮----
copy={"candidate":dict(item["candidate"]),"status":item["status"],"proof":dict(item["proof"])}
⋮----
copy["status"]="active"; activated=True
⋮----
def prove(backlog,candidate_id,proof)
⋮----
items=[]; found=False
⋮----
found=True
⋮----
required=copy["candidate"].get("required_evidence")
⋮----
def save(path,backlog)
⋮----
path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
⋮----
def load(path)
⋮----
value=json.loads(Path(path).read_text(encoding="utf-8"))
````

## File: improvement_dispatch.py
````python
"""Controlled dispatch policy for continuous-improvement execution."""
⋮----
BUILTIN_VERIFIERS={"persistent_warning"}
VERIFIER_CAPABILITIES={
APPLICATOR_CAPABILITIES={
⋮----
class ImprovementDispatchError(ValueError)
⋮----
def required_verifier_capability(candidate)
⋮----
kind=candidate["kind"]
⋮----
capability=VERIFIER_CAPABILITIES.get(kind)
⋮----
def dispatch(candidate,registry)
⋮----
applicator=APPLICATOR_CAPABILITIES.get(kind)
⋮----
applicator_provider=registry["capabilities"][applicator]["provider"]
verifier_capability=required_verifier_capability(candidate)
⋮----
verifier_provider=registry["capabilities"][verifier_capability]["provider"]
````

## File: improvement_executor.py
````python
"""Bounded execution of one active continuous-improvement goal at a time."""
⋮----
class ImprovementExecutionError(ValueError)
⋮----
def _active(backlog)
⋮----
active=[item for item in backlog["items"] if item["status"]=="active"]
⋮----
def verified_project_cycle(candidate, run_project_cycle)
⋮----
def execute(goal_state)
⋮----
result=run_project_cycle(goal_state)
evidence=verify_improvement_result(candidate,result)
out={}
⋮----
status=result.get("status")
⋮----
backlog_path=Path(backlog_path)
goal_path=Path(goal_path)
registry_path=Path(registry_path)
backlog=load_backlog(backlog_path)
item=_active(backlog)
⋮----
candidate=item["candidate"]
candidate_id=candidate["id"]
goal=None
⋮----
goal=load_goal(goal_path)
⋮----
registry=load_registry(registry_path)
route=dispatch(candidate,registry)
⋮----
goal=improvement_goal(candidate)
⋮----
state=run_goal(
status=state.get("status")
⋮----
required=candidate["required_evidence"]
evidence=state.get("evidence")
⋮----
proof={key:evidence[key] for key in required if key in evidence}
⋮----
backlog=prove(backlog,candidate_id,proof)
````

## File: improvement_verifier.py
````python
"""Fail-closed conversion of trusted project results into improvement evidence."""
⋮----
class ImprovementVerificationError(ValueError)
⋮----
def _full_regression(result)
⋮----
report=result.get("report")
completion=report.get("completion") if isinstance(report,dict) else None
⋮----
def verify_improvement_result(candidate,result)
⋮----
kind=candidate.get("kind")
source=candidate.get("source")
⋮----
evidence={}
⋮----
verification=result.get("improvement_verification") if isinstance(result,dict) else None
⋮----
failure=source.get("failure")
⋮----
capability=source.get("capability")
⋮----
stage=source.get("stage")
warnings=source.get("warnings")
report=result.get("report") if isinstance(result,dict) else None
release=report.get("release_evidence") if isinstance(report,dict) else None
stage_evidence=release.get(stage) if isinstance(release,dict) and isinstance(stage,str) else None
current=stage_evidence.get("warnings",[]) if isinstance(stage_evidence,dict) else None
````

## File: journeys.py
````python
"""Validate executable acceptance journeys; strings are data, never generated Dart code."""
⋮----
def validate_journeys(value)
⋮----
ids = set()
⋮----
name = journey['id']
⋮----
steps = journey['steps']
⋮----
assertions = interactions = 0
⋮----
action = step.get('action')
fields = {'tap': {'action', 'key'}, 'enter_text': {'action', 'key', 'value'},
⋮----
def encoded_journeys(value)
⋮----
CONTRACT = '''The product JSON MUST include journeys: 1..6 objects with exactly id and steps.
````

## File: jumpy_baseline.gd
````
extends SceneTree

var failures: Array[String] = []

func check(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
		push_error(label)

func _initialize() -> void:
	call_deferred("run_checks")

func run_checks() -> void:
	var scene = load("res://scenes/Main.tscn")
	if scene == null:
		quit(1)
		return
	var game = scene.instantiate()
	root.add_child(game)
	await process_frame
	game.set_physics_process(false)
	var profile = root.get_node("Profile")
	profile.data.sound = false
	profile.data.haptics = false

	check(game.state == "READY", "Initial state must be READY")
	game.reset_run(true)
	var first = game.platforms.duplicate(true)
	game.reset_run(true)
	check(first == game.platforms, "Daily platforms must reproduce within one day")
	game.start_run()
	check(game.state == "PLAYING" and game.player_vy < 0, "Start must initiate a jump")
	var tap = InputEventAction.new()
	tap.action = "tap"
	tap.pressed = true
	game._unhandled_input(tap)
	check(not game.pulse_available, "First airborne tap must consume the pulse")
	game.player_vy = 100.0
	game._unhandled_input(tap)
	check(game.player_vy == 100.0, "Second airborne tap must not apply another pulse")
	var runs_before = int(profile.data.runs)
	game.die()
	game.die()
	check(int(profile.data.runs) == runs_before + 1, "Death must record a run exactly once")
	check(game.state == "DEAD" and game.ui.retry.visible, "Death must offer retry")
	game.restart_pressed()
	check(game.state == "PLAYING" and game.score == 0, "Retry must reset score and start")

	var count: int = 8
	if "--finance" in OS.get_cmdline_user_args():
		count += 4
		profile.data.coins = 10
		check(not profile.spend_coins(-5) and int(profile.data.coins) == 10, "Negative spending must preserve balance")
		profile.data.coins = 10
		check(not profile.spend_coins(0) and int(profile.data.coins) == 10, "Zero spending must be refused")
		profile.data.coins = 10
		check(not profile.spend_coins(11) and int(profile.data.coins) == 10, "Insufficient funds must preserve balance")
		profile.data.coins = 10
		check(profile.spend_coins(4) and int(profile.data.coins) == 6, "Valid spending must debit exactly once")
	var report_path = OS.get_environment("STUDIO_BASELINE_REPORT")
	if report_path.is_empty():
		report_path = "user://baseline-result.json"
	var report = FileAccess.open(report_path, FileAccess.WRITE)
	if report == null:
		quit(1)
		return
	report.store_string(JSON.stringify({"passed": failures.is_empty(), "failures": failures, "checks": count}))
	report.close()
	print("JUMPY_BASELINE_PASS" if failures.is_empty() else "JUMPY_BASELINE_FAIL")
	quit(0 if failures.is_empty() else 1)
````

## File: jumpy_save_checks.gd
````
extends SceneTree

var failures: Array[String] = []
var profile
var original: Dictionary

func _initialize() -> void:
	call_deferred("run_checks")

func check(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
		push_error(label)

func load_text(text: String) -> void:
	profile.data = original.duplicate(true)
	var file = FileAccess.open("user://jumpy_save.json", FileAccess.WRITE)
	file.store_string(text)
	file.close()
	profile.load_data()

func run_checks() -> void:
	profile = root.get_node("Profile")
	original = profile.data.duplicate(true)
	original.coins = 0
	original.best_score = 0
	original.sound = true
	load_text(JSON.stringify({"coins": -10, "best_score": "bad", "sound": "false", "unlocked_skins": "bad", "selected_skin": 99, "daily_key": [1]}))
	check(profile.data.coins == 0 and profile.data.best_score == 0 and profile.data.sound == true and profile.data.unlocked_skins == [0] and profile.data.selected_skin == 0 and profile.data.daily_key == "", "Invalid save fields must fall back safely")

	load_text(JSON.stringify({"coins": 12, "sound": false, "unlocked_skins": [0, 2], "selected_skin": 2}))
	check(typeof(profile.data.coins) == TYPE_INT and profile.data.coins == 12 and profile.data.sound == false and profile.data.selected_skin == 2, "Valid JSON numbers must normalize without losing preferences")

	load_text(JSON.stringify({"unlocked_skins": [0, 0, 99, -1, 2.5, "x", 2], "selected_skin": 3}))
	check(profile.data.unlocked_skins == [0, 2] and profile.data.selected_skin == 0, "Skins must be unique valid indices and selected skin unlocked")

	load_text('{"coins":1e100,"runs":2.5,"best_score":true,"daily_key":"2025-02-29","last_play_date":"2024-02-29"}')
	check(profile.data.coins == 0 and profile.data.runs == 0 and profile.data.best_score == 0 and profile.data.daily_key == "" and profile.data.last_play_date == "2024-02-29", "Numeric bounds and calendar dates must be validated")

	load_text('{"coins":')
	check(profile.data.coins == 0, "Truncated JSON must preserve safe defaults")
	load_text('[]')
	check(profile.data.coins == 0, "Non-object JSON must preserve safe defaults")

	profile.data = original.duplicate(true)
	profile.data.coins = 9
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://jumpy_save.json"))
	profile.load_data()
	check(profile.data.coins == 0, "Missing save must restore defaults")

	profile.data = original.duplicate(true)
	profile.data.coins = 22
	profile.data.sound = false
	profile.save()
	profile.data.coins = 0
	profile.data.sound = true
	profile.load_data()
	check(profile.data.coins == 22 and profile.data.sound == false, "Valid save roundtrip must preserve progress")

	profile.data = original.duplicate(true)
	profile.save()
	var report = FileAccess.open(OS.get_environment("STUDIO_BASELINE_REPORT"), FileAccess.WRITE)
	if report == null:
		quit(1)
		return
	report.store_string(JSON.stringify({"passed": failures.is_empty(), "failures": failures, "checks": 8}))
	report.close()
	print("JUMPY_SAVE_PASS" if failures.is_empty() else "JUMPY_SAVE_FAIL")
	quit(0 if failures.is_empty() else 1)
````

## File: learning_context.py
````python
"""Bounded trusted learned-context injection for model prompts."""
⋮----
MAX_BYTES=64_000
MAX_ITEMS=20
⋮----
def load_context()
⋮----
path=os.environ.get("STUDIO_LEARNED_CONTEXT_PATH","")
⋮----
p=Path(path)
⋮----
try: value=json.loads(p.read_text(encoding="utf-8"))
⋮----
out=[]
⋮----
summary=item.get("summary")
⋮----
def augment(context)
⋮----
items=load_context()
⋮----
payload=json.dumps(items,ensure_ascii=False,sort_keys=True)
````

## File: lease_guard.py
````python
"""Background lease renewal for long-running task operations."""
⋮----
@contextmanager
def maintain(task: dict | None, *, lease_seconds: int = DEFAULT_LEASE_SECONDS, interval_seconds: float | None = None)
⋮----
owner = task.get("lease_owner")
token = task.get("lease_token")
⋮----
interval = float(interval_seconds if interval_seconds is not None else max(5.0, lease_seconds / 3.0))
stop = threading.Event()
errors: list[BaseException] = []
⋮----
def run()
⋮----
thread = threading.Thread(target=run, name="studio-task-lease-heartbeat", daemon=True)
````

## File: lease_keepalive.py
````python
"""Periodic renewal helper for long-running leased tasks."""
⋮----
@contextmanager
def keepalive(task: dict, *, interval_seconds: float = 120.0, lease_seconds: int = 3600)
⋮----
owner = task.get("lease_owner")
token = task.get("lease_token")
⋮----
stop = threading.Event()
errors = []
⋮----
def renew()
⋮----
worker = threading.Thread(target=renew, name="studio-lease-keepalive", daemon=True)
````

## File: local_capacity_inventory.py
````python
"""Persist a safe inventory of discovered local/free AI capacity."""
⋮----
def write(out: Path) -> dict
⋮----
out = Path(out)
⋮----
rows = []
benchmark_path = out / ".autonomy" / "local-model-benchmark.json"
⋮----
benchmark = {}
⋮----
benchmark = benchmark_gateway(
⋮----
payload = {
````

## File: local_capacity.py
````python
"""Fail-safe discovery of OpenAI-compatible local AI gateways."""
⋮----
DEFAULT_ENDPOINTS = (
⋮----
CODE_HINTS = (
VISION_HINTS = (
⋮----
def _bool(value: object, default: bool = True) -> bool
⋮----
def _model_ids(value: object) -> list[str]
⋮----
rows = value.get("data")
⋮----
ids = []
⋮----
model_id = row.get("id")
⋮----
def _pick(models: list[str], hints: tuple[str, ...]) -> str
⋮----
req = urllib.request.Request(
⋮----
raw = response.read(300_000)
value = json.loads(raw)
⋮----
models = _model_ids(value)
⋮----
def discover(*, timeout: float = 0.25) -> list[dict]
⋮----
custom = os.environ.get("STUDIO_LOCAL_CAPACITY_ENDPOINTS_JSON", "")
endpoints = DEFAULT_ENDPOINTS
⋮----
value = json.loads(custom)
⋮----
value = None
⋮----
parsed = []
⋮----
name = item.get("name")
base = item.get("base")
quota = item.get("monthly_token_quota", 0)
⋮----
endpoints = tuple(parsed)
⋮----
found = []
⋮----
row = probe_gateway(name, base, quota, timeout=timeout)
````

## File: local_model_benchmark.py
````python
"""Optional bounded micro-benchmark for local models."""
⋮----
MAX_BENCHMARK_MODELS = 6
MAX_SECONDS_PER_CALL = 20.0
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
def _decode_json(response: dict) -> dict
⋮----
raw = response["choices"][0]["message"]["content"].strip()
fence = chr(96) * 3
⋮----
raw = raw.split("\n", 1)[1].rsplit(fence, 1)[0]
value = json.loads(raw)
⋮----
def _call(api: API, model: str, system: str, user: str) -> tuple[dict | None, float]
⋮----
started = time.monotonic()
⋮----
response = api.call(
value = _decode_json(response)
⋮----
value = None
⋮----
def benchmark(base: str, model: str, *, key: str = "") -> dict
⋮----
api = API(base, key)
⋮----
json_pass = (
⋮----
code_text = code_value.get("code") if isinstance(code_value, dict) else None
code_pass = (
⋮----
score = 0.0
⋮----
avg_latency = (json_latency + code_latency) / 2.0
⋮----
existing = load(out_path)
results = dict(existing)
⋮----
item_key = provider + "|" + model
⋮----
def routing_bonus(data: dict, provider: str, model: str) -> float
⋮----
row = data.get(provider + "|" + model) if isinstance(data, dict) else None
⋮----
score = float(row.get("score", 0.0))
````

## File: local_model_leaderboard.py
````python
"""Summaries and leaderboards for local-model contextual specialization."""
⋮----
def leaderboards(data: dict, *, min_samples: int = 3, limit_per_context: int = 8) -> dict
⋮----
grouped: dict[str, list[dict]] = defaultdict(list)
⋮----
parts = key.split("|", 3)
⋮----
samples = int(row.get("samples", 0) or 0)
rate = float(row.get("ema_verified_success", 0.0) or 0.0)
⋮----
confidence = min(1.0, samples / 10.0)
specialist_score = (rate - 0.5) * 2.0 * confidence
⋮----
contexts = {}
````

## File: local_model_reputation.py
````python
"""Persistent per-model reputation learned from real routed executions."""
⋮----
ALPHA = 0.25
MIN_SAMPLES = 3
MAX_BONUS = 16.0
MAX_PENALTY = 18.0
MAX_ROWS = 256
QUARANTINE_MIN_VERIFIED = 5
QUARANTINE_VERIFIED_RATE = 0.20
QUARANTINE_PROTOCOL_RATE = 0.60
QUARANTINE_ROUTING_PENALTY = 1000.0
⋮----
def _key(provider: str, model: str, role: str) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
successes = min(samples, max(0, int(row.get("successes", 0))))
protocol_failures = max(0, int(row.get("protocol_failures", 0)))
ema_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
ema_latency = max(0.0, float(row.get("ema_latency_seconds", 0.0)))
verified_samples = max(0, int(row.get("verified_samples", 0)))
verified_successes = min(
ema_verified = max(
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
key = _key(provider, model, role)
row = data.get(key, {
samples = int(row["samples"])
observed = 1.0 if success else 0.0
previous_success = float(row["ema_success"])
previous_latency = float(row["ema_latency_seconds"])
latency = max(0.0, float(latency_seconds))
ema_success = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous_success
ema_latency = latency if samples == 0 else ALPHA * latency + (1.0 - ALPHA) * previous_latency
⋮----
verified_samples = int(row.get("verified_samples", 0))
observed = 1.0 if verified_success else 0.0
previous = float(row.get("ema_verified_success", 0.0))
ema_verified = (
⋮----
def score(data: dict, *, provider: str, model: str, role: str) -> float
⋮----
row = data.get(_key(provider, model, role)) if isinstance(data, dict) else None
⋮----
samples = int(row.get("samples", 0) or 0)
verified_samples = int(row.get("verified_samples", 0) or 0)
⋮----
protocol_success = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
protocol_rate = min(1.0, int(row.get("protocol_failures", 0) or 0) / max(1, samples))
verified_success = max(
⋮----
blended = 0.75 * verified_success + 0.25 * protocol_success
⋮----
blended = protocol_success
⋮----
centered = (blended - 0.5) * 2.0
base = centered * (MAX_BONUS if centered >= 0 else MAX_PENALTY)
penalty = protocol_rate * 8.0
⋮----
protocol_rate = min(
⋮----
def snapshot(data: dict) -> list[dict]
⋮----
rows = []
⋮----
parts = key.split("|", 2)
````

## File: local_model_specialization.py
````python
"""Context-specific verified reputation for local models."""
⋮----
ALPHA = 0.25
MIN_CONTEXT_SAMPLES = 3
MAX_CONTEXT_BONUS = 14.0
MAX_CONTEXT_PENALTY = 16.0
MAX_ROWS = 1024
⋮----
def _key(provider: str, model: str, role: str, context: str) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
successes = min(samples, max(0, int(row.get("successes", 0))))
ema = max(0.0, min(1.0, float(row.get("ema_verified_success", 0.0))))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
⋮----
relevance = float(weight)
⋮----
key = _key(provider, model, role, context)
row = data.get(key, {
samples = int(row["samples"])
observed = 1.0 if success else 0.0
previous = float(row.get("ema_verified_success", 0.0))
alpha = min(0.5, max(0.08, ALPHA * relevance * 2.0))
ema = observed if samples == 0 else alpha * observed + (1.0 - alpha) * previous
⋮----
total_mass = 0.0
weighted_signal = 0.0
evidence = []
⋮----
row = data.get(_key(provider, model, role, context)) if isinstance(data, dict) else None
⋮----
samples = int(row.get("samples", 0) or 0)
⋮----
rel = max(0.0, float(relevance))
⋮----
confidence = min(1.0, samples / 10.0)
mass = rel * confidence
rate = max(0.0, min(1.0, float(row.get("ema_verified_success", 0.0))))
centered = (rate - 0.5) * 2.0
⋮----
normalized = max(-1.0, min(1.0, weighted_signal / total_mass))
score = normalized * (MAX_CONTEXT_BONUS if normalized >= 0 else MAX_CONTEXT_PENALTY)
⋮----
def snapshot(data: dict) -> list[dict]
⋮----
rows = []
⋮----
parts = key.split("|", 3)
````

## File: memory_bridge.py
````python
"""Trusted ingestion helpers for project/research/experience memory."""
⋮----
def _digest(value)
⋮----
def remember_research(memory, project_id, research)
⋮----
candidate_id = research.get("candidate_id")
items = research.get("items")
⋮----
out = memory
⋮----
kind = item.get("kind")
source = item.get("source")
summary = item.get("notes")
⋮----
entry_id = "research:" + candidate_id + ":" + str(index)
out = add_entry(
⋮----
def remember_experience(memory, project_id, *, entry_id, summary, tags, proof, reusable=False, confidence=100)
⋮----
commit = proof.get("commit_sha")
````

## File: memory_lifecycle.py
````python
"""Ingest trusted run evidence into persistent project memory."""
⋮----
def _read(path)
⋮----
value=json.loads(Path(path).read_text())
⋮----
def ingest_run(memory, project_id, out)
⋮----
out=Path(out)
⋮----
# Generic-project learning: only retain experience backed by a real verifier
# and a persisted Git commit. This global memory is later reusable by other
# projects through the existing project-memory bridge.
verifier=_read(out/"generic-verifier.json")
generic=_read(out/"generic-report.json")
⋮----
rounds=generic.get("rounds")
commit=generic.get("checkpoint_commit")
⋮----
last=rounds[-1] if isinstance(rounds[-1],dict) else {}
verification=last.get("verification") if isinstance(last,dict) else {}
⋮----
entry_id="generic:"+project_id+":"+commit[:16]
existing={item.get("id") for item in memory.get("entries",[]) if isinstance(item,dict)}
⋮----
review=last.get("review") if isinstance(last.get("review"),dict) else {}
changed=last.get("changed_files") if isinstance(last.get("changed_files"),list) else []
summary="Verified generic-project cycle; changed "+str(len(changed))+" files."
reason=review.get("reason")
⋮----
summary=(summary+" "+reason.strip())[:4000]
tags=["generic-project","verified-cycle"]
⋮----
recipe=verifier.get("recipe") if isinstance(verifier.get("recipe"),dict) else {}
commands=recipe.get("commands") if isinstance(recipe.get("commands"),list) else []
⋮----
summary=(summary+" Adaptive verifier recipe: "+json.dumps(commands,ensure_ascii=False))[:4000]
⋮----
memory=remember_experience(
research=_read(out/"evolution-research.json")
⋮----
candidate_id=research.get("candidate_id")
items=research.get("items")
⋮----
expected={"research:"+candidate_id+":"+str(i) for i in range(len(items))}
⋮----
overlap=expected & existing
⋮----
memory=remember_research(memory,project_id,research)
⋮----
persisted=_read(out/"evolution-persisted.json")
promotion=_read(out/"evolution-promotion.json")
benchmark=_read(out/"evolution-isolated-benchmark.json")
⋮----
candidate=benchmark.get("candidate")
⋮----
unit=candidate.get("unit_tests")
⋮----
commit=persisted.get("commit_sha")
gap=persisted.get("gap")
candidate_id=persisted.get("candidate_id")
⋮----
proof={
entry_id="experience:"+candidate_id
````

## File: meta_router.py
````python
"""Meta-router CLI combining agent selection with star-list discovery."""
⋮----
MIN_EVENTS = 6
MIN_GAP = 0.20
⋮----
@dataclass(frozen=True)
class MetaRoute
⋮----
mode: str
agent_limit: int
confidence: float
reason: str
strategy: str = "dual"
⋮----
def as_dict(self) -> dict
⋮----
def _rate(events: list[dict], kind: str, role: str) -> tuple[int, float]
⋮----
rows = [event for event in events if event.get("kind") == kind and event.get("role") == role]
⋮----
success = sum(1 for event in rows if event.get("success") is True)
⋮----
architecture_bias = 0.0
⋮----
origins = safe_rewrite_summary.get("origin_rankings")
⋮----
agent_rows = [row for row in origins if row.get("kind") == "agent" and row.get("eligible_for_routing_bias") is True]
provider_rows = [row for row in origins if row.get("kind") == "provider" and row.get("eligible_for_routing_bias") is True]
⋮----
agent_rate = sum(float(row.get("verification_pass_rate", 0.0)) for row in agent_rows) / len(agent_rows)
provider_rate = sum(float(row.get("verification_pass_rate", 0.0)) for row in provider_rows) / len(provider_rows)
architecture_bias = max(-0.25, min(0.25, agent_rate - provider_rate))
⋮----
selected = select_strategy(
⋮----
confidence = min(
mapping = {
⋮----
gap = (agent_rate - provider_rate) + architecture_bias
confidence = min(1.0, min(agent_n, provider_n) / 20.0)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
⋮----
decisions = rank_agents(
payload = {
````

## File: model_portfolio_audit.py
````python
"""Audit diversity and independence of a multi-model portfolio."""
⋮----
def _identity(row: dict | None) -> tuple[str, str] | None
⋮----
provider = row.get("provider")
model = row.get("model")
⋮----
def audit(selections: dict) -> dict
⋮----
identities = {}
⋮----
identity = _identity(row)
⋮----
providers = {provider for provider, _ in identities.values()}
models = {model for _, model in identities.values()}
role_count = len(identities)
diversity_ratio = (
⋮----
impl = identities.get("implementation")
review = identities.get("review")
review_independent = None
⋮----
review_independent = (
````

## File: model_portfolio_learning.py
````python
"""Learn whether portfolio diversity and independent review improve verified outcomes."""
⋮----
ALPHA = 0.25
MIN_SAMPLES = 4
MAX_ROWS = 32
⋮----
def _bucket(audit: dict) -> str
⋮----
independent = audit.get("review_independent")
⋮----
diversity = float(audit.get("diversity_ratio", 0.0) or 0.0)
⋮----
diversity = 0.0
⋮----
diversity_bucket = "high"
⋮----
diversity_bucket = "medium"
⋮----
diversity_bucket = "low"
independent_bucket = (
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
successes = min(samples, max(0, int(row.get("successes", 0))))
ema = max(0.0, min(1.0, float(row.get("ema_success", 0.0))))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, *, audit: dict, success: bool) -> dict
⋮----
data = load(path)
key = _bucket(audit)
row = data.get(key, {"samples": 0, "successes": 0, "ema_success": 0.0})
samples = int(row["samples"])
observed = 1.0 if success else 0.0
previous = float(row.get("ema_success", 0.0))
ema = observed if samples == 0 else ALPHA * observed + (1.0 - ALPHA) * previous
⋮----
def diversity_bias(data: dict) -> float
⋮----
recommendation_data = recommendation(data)
preferred = recommendation_data.get("recommended_class")
⋮----
def recommendation(data: dict) -> dict
⋮----
eligible = []
⋮----
samples = int(row.get("samples", 0) or 0)
````

## File: model_portfolio.py
````python
"""Dynamic multi-model portfolio policy."""
⋮----
PORTFOLIO_ROLES = (
⋮----
INDEPENDENT_ROLES = {"review", "visual"}
⋮----
@dataclass(frozen=True)
class PortfolioChoice
⋮----
role: str
provider: str
model: str
score: float
independent_from: str | None = None
⋮----
def as_dict(self) -> dict
⋮----
choices = {}
⋮----
rows = ranked_by_role.get(role)
⋮----
selected = None
⋮----
selected = row
⋮----
selected = next((row for row in rows if isinstance(row, dict)), None)
````

## File: multi_engine_orchestrator.py
````python
"""Route preview orchestration without weakening the existing Flutter pipeline."""
⋮----
def _remaining(deadline, clock)
⋮----
value=deadline-clock()
⋮----
def _detect(request_path,project_out,runner,deadline,clock)
⋮----
try: remaining=_remaining(deadline,clock)
⋮----
result=runner([sys.executable,'studio/engine_detect.py',request_path,'--out',str(project_out)],timeout=remaining)
⋮----
path=project_out/'engine-detection.json'
⋮----
try: evidence=json.loads(path.read_text())
⋮----
def _run_stage(script,request_path,project_out,work,runner,deadline,clock)
⋮----
def run_project(request_path,project_out,work,runner,deadline,clock,baseline_sha=None)
⋮----
engine=_detect(request_path,project_out,runner,deadline,clock)
⋮----
req=json.loads(Path(request_path).read_text())
⋮----
portfolio={}
portfolio_path=project_out/'portfolio-research.json'
⋮----
try: portfolio=json.loads(portfolio_path.read_text())
except (OSError,json.JSONDecodeError): portfolio={}
⋮----
godot_request=request_check(json.loads(Path(request_path).read_text()))
⋮----
stages=[
report={}
⋮----
result=_run_stage(script,request_path,project_out,stage_work,runner,deadline,clock)
⋮----
report=load_report(project_out) if (project_out/'report.json').is_file() else {}
⋮----
completion=report.get('completion')
⋮----
coverage=report.get('coverage') or {}
⋮----
release_work=str(Path(work).with_name(Path(work).name+'-release'))
result=_run_stage('studio/godot_release_stage.py',request_path,project_out,release_work,runner,deadline,clock)
⋮----
artifact_work=str(Path(work).with_name(Path(work).name+'-release-artifact'))
result=_run_stage('studio/godot_release_artifact_stage.py',request_path,project_out,artifact_work,runner,deadline,clock)
⋮----
evidence=report.get('release_artifact')
⋮----
metadata_work=str(Path(work).with_name(Path(work).name+'-store-metadata'))
result=_run_stage('studio/godot_store_metadata_stage.py',request_path,project_out,metadata_work,runner,deadline,clock)
⋮----
completion=report.get('completion'); coverage=report.get('coverage') or {}
⋮----
privacy_work=str(Path(work).with_name(Path(work).name+'-privacy-security'))
result=_run_stage('studio/godot_privacy_security_stage.py',request_path,project_out,privacy_work,runner,deadline,clock)
⋮----
final_work=str(Path(work).with_name(Path(work).name+'-final-review'))
result=_run_stage('studio/godot_final_review_stage.py',request_path,project_out,final_work,runner,deadline,clock)
⋮----
publication=godot_request.get('play_publish')
⋮----
play_work=str(Path(work).with_name(Path(work).name+'-play-submit'))
result=_run_stage('studio/godot_play_stage.py',request_path,project_out,play_work,runner,deadline,clock)
````

## File: multi_project_smoke.py
````python
"""Sequential smoke runs proving project isolation across repeated executions."""
⋮----
_TRANSIENT_ANDROID_SDK_SIGNATURES = (
⋮----
def _is_transient_android_sdk_failure(output: object) -> bool
⋮----
text = str(output or "")
⋮----
def _clear_transient_android_download_cache(env: dict[str, str]) -> None
⋮----
android_home = env.get("ANDROID_HOME")
⋮----
root = Path(android_home)
⋮----
android_user_home = env.get("ANDROID_USER_HOME")
⋮----
def main() -> int
⋮----
base_env = dict(os.environ)
failures = []
⋮----
root = Path(td)
⋮----
project_root = root / f"project-{index + 1}"
env = dict(base_env)
⋮----
passed = False
⋮----
result = subprocess.run(
⋮----
passed = True
````

## File: native_qa.py
````python
"""Trusted Android QA for permission-driven/native-capability Flutter apps."""
⋮----
RUNTIME_PERMISSIONS = {
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
⋮----
def _serial(adb: str) -> str
⋮----
explicit = os.environ.get('ANDROID_SERIAL')
⋮----
devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
⋮----
def _declared_permissions(root: Path) -> list[str]
⋮----
"""Source-manifest permissions, retained as corroborating evidence/tests."""
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
text = manifest.read_text(errors='replace')
⋮----
def _parse_permission_output(text: str) -> list[str]
⋮----
"""Parse permission names from apkanalyzer/aapt output without trusting formatting."""
⋮----
def _release_permissions(apk: Path) -> dict
⋮----
"""Inspect permissions from the built APK so dependency/flavor manifests are included."""
attempts = []
commands = []
⋮----
result = run_command(command, timeout=60)
permissions = _parse_permission_output(result.stdout)
⋮----
def _launch(adb: str, serial: str, pkg: str) -> subprocess.CompletedProcess
⋮----
def _crashes(adb: str, serial: str) -> list[str]
⋮----
result = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
⋮----
def _exercise_permission(adb: str, serial: str, pkg: str, permission: str) -> dict
⋮----
steps = []
⋮----
result = run_command(command, timeout=30)
⋮----
launch = _launch(adb, serial, pkg)
⋮----
crash_lines = _crashes(adb, serial)
⋮----
def _exercise_location(adb: str, serial: str) -> dict
⋮----
geo = run_command([adb, '-s', serial, 'emu', 'geo', 'fix', '2.3522', '48.8566'], timeout=30)
⋮----
crashes = _crashes(adb, serial)
⋮----
def _exercise_biometric(adb: str, serial: str, pkg: str) -> dict
⋮----
"""Exercise emulator fingerprint input but do not invent app-level auth success.

    A generic harness cannot prove that the application consumed/authenticated the touch.
    Until the product supplies an explicit biometric acceptance journey, this remains a
    deliberate fail-closed blocker rather than false passing evidence.
    """
⋮----
finger = run_command([adb, '-s', serial, 'emu', 'finger', 'touch', '1'], timeout=30)
⋮----
stable = launch.returncode == 0 and finger.returncode == 0 and not crashes
⋮----
def validate_native(root: Path, out: Path, adb: str = 'adb') -> dict
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
emulator = None
owned_emulator = False
serial = None
⋮----
emulator = start_emulator()
owned_emulator = True
boot = wait_for_boot(adb)
⋮----
serial = _serial(adb)
pkg = package_name(root)
install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
⋮----
source_permissions = _declared_permissions(root)
release_inspection = _release_permissions(apk)
blockers = []
⋮----
release_permissions = []
⋮----
release_permissions = release_inspection['permissions']
⋮----
tested = [permission for permission in release_permissions if permission in RUNTIME_PERMISSIONS]
results = [_exercise_permission(adb, serial, pkg, permission) for permission in tested]
⋮----
dependencies = ((root / 'pubspec.yaml').read_text(errors='replace')
biometric = 'local_auth:' in dependencies
biometric_result = None
⋮----
biometric_result = _exercise_biometric(adb, serial, pkg)
⋮----
location_result = None
⋮----
location_result = _exercise_location(adb, serial)
⋮----
payload = {
````

## File: native_stage.py
````python
"""Persist native capability QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = evaluate_and_repair(root, out, state, req, 'native_qa', validate_native)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('native_qa')
````

## File: notification_qa.py
````python
"""Trusted Android QA for notification-capable Flutter apps."""
⋮----
POST_NOTIFICATIONS = 'android.permission.POST_NOTIFICATIONS'
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
NOTIFICATION_DEPENDENCIES = ('firebase_messaging', 'flutter_local_notifications')
BOUNDS = re.compile(r'^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$')
⋮----
def _serial(adb: str) -> str
⋮----
explicit = os.environ.get('ANDROID_SERIAL')
⋮----
devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
⋮----
def _dependencies(root: Path) -> list[str]
⋮----
pubspec = root / 'pubspec.yaml'
⋮----
found = []
in_dependencies = False
⋮----
in_dependencies = True
⋮----
match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', raw)
⋮----
def _manifest_permissions(root: Path) -> list[str]
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
def _launch(adb: str, serial: str, pkg: str) -> subprocess.CompletedProcess
⋮----
def _crashes(adb: str, serial: str) -> list[str]
⋮----
result = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
⋮----
def _notification_dump(adb: str, serial: str) -> str
⋮----
result = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'notification', '--noredact'], timeout=60)
⋮----
def _count_package_notifications(text: str, pkg: str) -> int
⋮----
def _apk_label(apk: Path) -> str | None
⋮----
aapt = shutil.which('aapt')
⋮----
result = run_command([aapt, 'dump', 'badging', str(apk)], timeout=60)
⋮----
match = re.search(r"application-label(?:-[^:]*)?:'([^']+)'", result.stdout)
⋮----
def _tap_notification(adb: str, serial: str, label: str, pkg: str) -> dict
⋮----
expand = run_command([adb, '-s', serial, 'shell', 'cmd', 'statusbar', 'expand-notifications'], timeout=30)
⋮----
dump = run_command([adb, '-s', serial, 'shell', 'uiautomator', 'dump', '/sdcard/studio-notification.xml'], timeout=30)
⋮----
xml = run_command([adb, '-s', serial, 'shell', 'cat', '/sdcard/studio-notification.xml'], timeout=30)
⋮----
root = ET.fromstring(xml.stdout[xml.stdout.find('<hierarchy'):])
⋮----
parents = {child: parent for parent in root.iter() for child in parent}
target = None
⋮----
text = (node.attrib.get('text', '') + ' ' + node.attrib.get('content-desc', '')).strip()
⋮----
current = node
⋮----
target = current
⋮----
current = parents.get(current)
⋮----
bounds = BOUNDS.match(target.attrib.get('bounds', ''))
⋮----
tap = run_command([adb, '-s', serial, 'shell', 'input', 'tap', str((x1 + x2) // 2), str((y1 + y2) // 2)], timeout=30)
⋮----
focus = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'window', 'windows'], timeout=60)
foreground = focus.returncode == 0 and any(
crashes = _crashes(adb, serial)
⋮----
def validate_notifications(root: Path, out: Path, adb: str = 'adb') -> dict
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
emulator = None
owned_emulator = False
serial = None
⋮----
emulator = start_emulator()
owned_emulator = True
boot = wait_for_boot(adb)
⋮----
serial = _serial(adb)
pkg = package_name(root)
install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
⋮----
deps = _dependencies(root)
declared = _manifest_permissions(root)
capability_sources = {
blockers: list[str] = []
states = []
⋮----
command = run_command([adb, '-s', serial, 'shell', 'pm', verb, pkg, POST_NOTIFICATIONS], timeout=30)
launch = _launch(adb, serial, pkg)
⋮----
resume = _launch(adb, serial, pkg)
⋮----
crash_lines = _crashes(adb, serial)
⋮----
before = _count_package_notifications(_notification_dump(adb, serial), pkg)
⋮----
after = _count_package_notifications(_notification_dump(adb, serial), pkg)
observed = after > before or after > 0
⋮----
tap_result = None
⋮----
label = _apk_label(apk)
⋮----
tap_result = _tap_notification(adb, serial, label, pkg)
⋮----
payload = {
````

## File: notification_stage.py
````python
"""Persist notification QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = evaluate_and_repair(root, out, state, req, 'notification_qa', validate_notifications)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('notification_qa')
````

## File: omniroute_capacity.py
````python
"""Read-only adapter for OmniRoute live free-tier capacity summary.

The scheduler treats OmniRoute as a single pooled free-capacity provider. Public
catalog totals are useful telemetry, but schedulable capacity is trusted only
when OmniRoute returns authenticated usage fields (usedThisMonth and remaining).
Anonymous summaries therefore fail closed to zero available tokens.
"""
⋮----
SUMMARY_PATH = "/api/free-tier/summary"
⋮----
class OmniRouteCapacityError(ValueError)
⋮----
"""Raised when OmniRoute capacity cannot be fetched or validated."""
⋮----
def _nonnegative_int(value, *, field: str, nullable: bool = False) -> int | None
⋮----
def _optional_text(value, *, field: str) -> str | None
⋮----
@dataclass(frozen=True)
class OmniRouteCapacitySnapshot
⋮----
steady_recurring_tokens: int
used_this_month: int | None
remaining_tokens: int | None
catalog_updated_at: str | None = None
catalog_source: str | None = None
⋮----
@property
    def authenticated_usage(self) -> bool
⋮----
def provider_row(self, name: str = "omniroute") -> dict
⋮----
"""Return a row accepted by capacity_scheduler.provider_capacities.

        Extra telemetry fields are deliberately retained for callers that persist
        the row before normalization. capacity_scheduler ignores unknown fields,
        so this stays backward compatible.
        """
provider_name = str(name or "").strip()
⋮----
def parse_summary(payload: dict) -> OmniRouteCapacitySnapshot
⋮----
"""Validate an OmniRoute /api/free-tier/summary response."""
⋮----
steady = _nonnegative_int(
used = _nonnegative_int(
remaining = _nonnegative_int(
⋮----
def _summary_url(base_url: str) -> str
⋮----
value = str(base_url or "").strip()
⋮----
value = value.rstrip("/")
⋮----
value = value[:-3].rstrip("/")
⋮----
"""Fetch and validate live OmniRoute free-tier capacity.

    api_key is sent only as a Bearer header and is never included in errors.
    The injectable opener keeps networking out of unit tests.
    """
⋮----
timeout_value = float(timeout)
⋮----
headers = {"Accept": "application/json"}
token = str(api_key or "").strip()
⋮----
request = Request(_summary_url(base_url), headers=headers, method="GET")
⋮----
raw = response.read()
⋮----
payload = json.loads(raw.decode("utf-8"))
````

## File: orchestrator.py
````python
"""Provider-neutral autonomous completion pipeline."""
⋮----
def _recommendation_context(request_path)
⋮----
value=json.loads(Path(request_path).read_text())
⋮----
brief=value.get('brief') if isinstance(value.get('brief'),str) else ''
text=brief.lower()
platform='android' if 'android' in text or 'play store' in text else ('ios' if 'ios' in text or 'iphone' in text else None)
language='dart' if 'flutter' in text else None
⋮----
def _load_recommendations(project_out)
⋮----
path=project_out/'star-recommendations.json'
⋮----
value=json.loads(path.read_text())
⋮----
def _evaluate_architecture(report,project_out)
⋮----
path=project_out/'architecture-decision.json'
⋮----
decision=json.loads(path.read_text())
⋮----
evaluation=write_architecture_evaluation(decision,report,project_out)
recommendations=_load_recommendations(project_out)
benchmark=write_architecture_benchmark(decision,evaluation,recommendations,project_out)
learning=summarize_architecture_learning(architecture_learning_root(project_out))
current_repos=[x.get('current_repo') for x in benchmark.get('comparisons',[]) if isinstance(x,dict) and isinstance(x.get('current_repo'),str)]
replacement_repos=[x.get('best_alternative') for x in benchmark.get('comparisons',[]) if isinstance(x,dict) and isinstance(x.get('best_alternative'),str)]
maintenance=probe_repo_maintenance(current_repos)
versions=probe_repo_versions(current_repos+replacement_repos)
obsolescence=write_architecture_obsolescence(learning,benchmark,recommendations,project_out,maintenance=maintenance,versions=versions)
historical_root=architecture_learning_root(project_out)
replacement_learning=summarize_replacement_learning(historical_root)
reputation_registry=load_replacement_reputation(historical_root/'architecture-replacement-reputation.json')
registry_policy=reputation_registry.get('policy') if isinstance(reputation_registry.get('policy'),dict) else {}
migration_review=None
⋮----
migration_review=write_reputation_policy_migration_review(
replacement_plan=write_architecture_replacement_plan(obsolescence,recommendations,project_out,learning=replacement_learning,reputation_registry=reputation_registry)
replacement_work_orders=write_architecture_replacement_work_orders(replacement_plan,project_out)
⋮----
def load_report(project_out)
⋮----
path=project_out/'report.json'
⋮----
try: value=json.loads(path.read_text())
⋮----
def _remaining(deadline,clock)
⋮----
value=deadline-clock()
⋮----
def _write_adaptation_handoff(report,project_out,baseline_sha)
⋮----
request=write_adaptation_request(report,project_out,frozenset(STAGES))
⋮----
def _run_adaptation_pending(project_out,deadline,runner,clock)
⋮----
order=project_out/'evolution-work-order.json'
⋮----
try: remaining=_remaining(deadline,clock)
⋮----
result=runner([sys.executable,'studio/evolution_pending.py',str(order),'--out',str(project_out)],timeout=remaining)
⋮----
path=project_out/'evolution-pending.json'
⋮----
status=value.get('status')
mapping={'no_pending_promotion':'none','promotion_pending_merge':'pending_merge','promotion_merged_restart_required':'restart_required','promotion_orphaned':'blocked','promotion_closed_without_merge':'blocked'}
⋮----
def _run_adaptation_research(project_out,deadline,runner,clock)
⋮----
result=runner([sys.executable,'studio/evolution_research.py',str(order),'--out',str(project_out)],timeout=remaining)
⋮----
evidence_path=project_out/'evolution-research.json'
⋮----
try: evidence=json.loads(evidence_path.read_text()); work_order=json.loads(order.read_text())
⋮----
def _run_adaptation_synthesis(project_out,deadline,runner,clock)
⋮----
order=project_out/'evolution-work-order.json'; research=project_out/'evolution-research.json'
⋮----
result=runner([sys.executable,'studio/evolution_synthesis.py',str(order),str(research),'--out',str(project_out)],timeout=remaining)
⋮----
candidate_path=project_out/'evolution-candidate.json'
⋮----
try: candidate=json.loads(candidate_path.read_text()); work_order=json.loads(order.read_text())
⋮----
def _run_adaptation_benchmark(project_out,deadline,runner,clock)
⋮----
order=project_out/'evolution-work-order.json'; candidate=project_out/'evolution-candidate.json'
⋮----
result=runner([sys.executable,'studio/evolution_isolated_runner.py',str(order),str(candidate),'--repo-root','.','--out',str(project_out)],timeout=remaining)
⋮----
promotion_path=project_out/'evolution-promotion.json'; benchmark_path=project_out/'evolution-isolated-benchmark.json'
⋮----
try: promotion=json.loads(promotion_path.read_text()); work_order=json.loads(order.read_text())
⋮----
def _run_adaptation_promotion(project_out,deadline,runner,clock)
⋮----
paths=[project_out/name for name in ('evolution-work-order.json','evolution-candidate.json','evolution-isolated-benchmark.json','evolution-promotion.json')]
⋮----
result=runner([sys.executable,'studio/evolution_promotion.py',str(paths[0]),str(paths[1]),str(paths[2]),str(paths[3]),'--repo-root','.','--out',str(project_out)],timeout=remaining)
⋮----
applied=project_out/'evolution-applied.json'
⋮----
try: value=json.loads(applied.read_text())
⋮----
def _run_adaptation_persistence(project_out,deadline,runner,clock)
⋮----
result=runner([sys.executable,'studio/evolution_persist.py',str(applied),'--repo-root','.','--out',str(project_out)],timeout=remaining)
⋮----
persisted=project_out/'evolution-persisted.json'
⋮----
try: value=json.loads(persisted.read_text())
⋮----
def _run_adaptation_automerge(project_out,deadline,runner,clock)
⋮----
order=project_out/'evolution-work-order.json'; persisted=project_out/'evolution-persisted.json'
⋮----
wait_seconds=max(0,min(int(remaining)-5,20*60))
⋮----
args=[sys.executable,'studio/evolution_automerge.py',str(order)]
⋮----
result=runner(args,timeout=remaining)
⋮----
path=project_out/'evolution-automerge.json'
⋮----
def _stage_command(name,stage,request_path,work,project_out)
⋮----
args=[request_path,'--work',work,'--out',str(project_out)]
⋮----
def run_registered_stages(request_path,project_out,work,report,deadline,runner,clock=time.monotonic,baseline_sha=None)
⋮----
visits={}
max_stage_visits=3
⋮----
completion=report.get('completion',{})
⋮----
name=completion.get('next_stage'); stage=get_stage(name) if isinstance(name,str) else None
⋮----
request=_write_adaptation_handoff(report,project_out,baseline_sha)
⋮----
pending_status=_run_adaptation_pending(project_out,deadline,runner,clock)
⋮----
automerge_status=_run_adaptation_automerge(project_out,deadline,runner,clock)
⋮----
research_status=_run_adaptation_research(project_out,deadline,runner,clock); synthesis_status='not_ready'; benchmark_status='not_ready'; promotion_status='not_ready'; persistence_status='not_ready'; automerge_status='not_ready'
if research_status=='complete': synthesis_status=_run_adaptation_synthesis(project_out,deadline,runner,clock)
if synthesis_status=='validated': benchmark_status=_run_adaptation_benchmark(project_out,deadline,runner,clock)
if benchmark_status=='approved': promotion_status=_run_adaptation_promotion(project_out,deadline,runner,clock)
if promotion_status=='promoted': persistence_status=_run_adaptation_persistence(project_out,deadline,runner,clock)
if persistence_status=='persisted': automerge_status=_run_adaptation_automerge(project_out,deadline,runner,clock)
⋮----
stage=get_stage(name)
⋮----
result=runner(_stage_command(name,stage,request_path,work,project_out),timeout=remaining)
⋮----
updated=load_report(project_out)
⋮----
updated=load_report(project_out); _evaluate_architecture(updated,project_out)
updated_completion=updated.get('completion',{}); next_name=updated_completion.get('next_stage') if isinstance(updated_completion,dict) else None
⋮----
report=updated
⋮----
def run_project(request_path,project_out,work,runner,deadline,clock=time.monotonic,baseline_sha=None)
⋮----
preview=runner([sys.executable,'studio/run.py',request_path,'--work',work,'--out',str(project_out)],timeout=remaining)
⋮----
report=load_report(project_out) if (project_out/'report.json').is_file() else {}
⋮----
report=load_report(project_out)
⋮----
release=runner([sys.executable,'studio/post_preview.py',request_path,'--work',work,'--out',str(project_out)],timeout=remaining)
⋮----
report=load_report(project_out); _evaluate_architecture(report,project_out)
````

## File: performance_qa.py
````python
"""Trusted Android performance QA for game/performance-sensitive Flutter apps."""
⋮----
FRAME_LIMIT_MS = float(os.environ.get('STUDIO_FRAME_LIMIT_MS', '16.7'))
JANK_RATIO_LIMIT = float(os.environ.get('STUDIO_JANK_RATIO_LIMIT', '0.15'))
MAX_FRAME_MS = float(os.environ.get('STUDIO_MAX_FRAME_MS', '80'))
SAMPLE_SECONDS = int(os.environ.get('STUDIO_PERF_SAMPLE_SECONDS', '20'))
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
⋮----
def _serial(adb: str) -> str
⋮----
explicit = os.environ.get('ANDROID_SERIAL')
⋮----
devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
⋮----
def _parse_gfxinfo(text: str) -> dict
⋮----
frames = []
in_profile = False
⋮----
stripped = line.strip()
⋮----
in_profile = True
⋮----
values = [float(value) for value in stripped.split(',')]
⋮----
ordered = sorted(frames)
p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
janky = sum(1 for value in frames if value > FRAME_LIMIT_MS)
⋮----
def _exercise(adb: str, serial: str, pkg: str) -> list[dict]
⋮----
actions = [
logs = []
⋮----
result = run_command(args, timeout=30)
⋮----
def validate_performance(root: Path, out: Path, adb: str = 'adb') -> dict
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
emulator = None
owned_emulator = False
serial = None
⋮----
emulator = start_emulator()
owned_emulator = True
boot = wait_for_boot(adb)
⋮----
serial = _serial(adb)
pkg = package_name(root)
⋮----
install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
⋮----
launch = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c',
⋮----
monkey = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg,
⋮----
gfx = run_command([adb, '-s', serial, 'shell', 'dumpsys', 'gfxinfo', pkg], timeout=60)
metrics = _parse_gfxinfo(gfx.stdout)
logcat = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
crashes = [line for line in logcat.stdout.splitlines()
⋮----
blockers = []
⋮----
payload = {
````

## File: performance_stage.py
````python
"""Persist game/performance QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = evaluate_and_repair(root, out, state, req, 'performance_qa', validate_performance)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('performance_qa')
````

## File: persistent_quick_gate_cache.py
````python
"""Persistent quick-gate cache scoped by project and toolchain fingerprint."""
⋮----
SCHEMA = 1
MAX_ENTRIES = 512
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_QUICK_GATE_CACHE_PATH", "")
⋮----
def toolchain_fingerprint() -> str
⋮----
payload = {
⋮----
def load() -> dict
⋮----
path = _path()
⋮----
data = json.loads(path.read_text())
⋮----
entries = data.get("entries")
⋮----
def save(entries: dict) -> None
⋮----
merged = load()
⋮----
trimmed = dict(list(merged.items())[-MAX_ENTRIES:])
````

## File: phase_budget.py
````python
"""Phase-level execution quota planning and bounded reallocation."""
⋮----
@dataclass(frozen=True)
class PhaseQuotas
⋮----
planning: int
implementation: int
verification: int
fallback: int
review: int
⋮----
def as_dict(self) -> dict
⋮----
@property
    def total(self) -> int
⋮----
total = max(900, verification_reserve_seconds + 480)
⋮----
total = max(180, int(available_seconds))
verify = max(60, min(total // 2, int(verification_reserve_seconds)))
remaining = max(0, total - verify)
⋮----
planning = max(30, int(remaining * planning_share))
implementation = max(60, int(remaining * implementation_share))
fallback = max(30, int(remaining * fallback_share))
review = max(30, remaining - planning - implementation - fallback)
⋮----
overflow = planning + implementation + fallback + review + verify - total
⋮----
reducible = max(0, implementation - 60)
take = min(reducible, overflow)
⋮----
reducible = max(0, fallback - 30)
⋮----
reducible = max(0, review - 30)
⋮----
planning = max(30, planning - overflow)
⋮----
def reallocate_unused(quotas: PhaseQuotas, *, phase: str, unused_seconds: int) -> PhaseQuotas
⋮----
unused = max(0, int(unused_seconds))
⋮----
values = quotas.as_dict()
⋮----
targets = {
first = unused * 2 // 3
second = unused - first
⋮----
def phase_remaining(quotas: PhaseQuotas, *, phase: str, elapsed_seconds: float) -> int
⋮----
def bounded_timeout(remaining_seconds: int, *, minimum: int = 30, maximum: int = 1800) -> int
````

## File: phase_cost_baseline.py
````python
"""Historical phase-cost baselines keyed by toolchain and phase."""
⋮----
ALPHA = 0.25
MAX_ROWS = 128
MIN_SAMPLES = 4
⋮----
def _key(toolchain: dict | None, phase: str) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
ema = max(0.0, float(row.get("ema_seconds", 0.0)))
mad = max(0.0, float(row.get("ema_abs_deviation", 0.0)))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, toolchain: dict | None, phase: str, observed_seconds: float) -> dict
⋮----
observed = max(0.0, float(observed_seconds))
data = load(path)
key = _key(toolchain, phase)
row = data.get(key, {"samples": 0, "ema_seconds": 0.0, "ema_abs_deviation": 0.0})
samples = int(row["samples"])
previous = float(row["ema_seconds"])
previous_dev = float(row["ema_abs_deviation"])
⋮----
ema = observed
deviation = 0.0
⋮----
delta = abs(observed - previous)
ema = ALPHA * observed + (1.0 - ALPHA) * previous
deviation = ALPHA * delta + (1.0 - ALPHA) * previous_dev
⋮----
def baseline(data: dict, toolchain: dict | None, phase: str) -> dict | None
⋮----
row = data.get(_key(toolchain, phase))
````

## File: platform_view_qa.py
````python
"""Trusted runtime QA for Flutter platform views on Android release builds."""
⋮----
DEPENDENCIES = {
CRASH_PATTERNS = ('FATAL EXCEPTION', 'AndroidRuntime: FATAL', 'ANR in ', 'Unhandled Exception')
⋮----
def _dependencies(root: Path) -> list[str]
⋮----
path = root / 'pubspec.yaml'
⋮----
found: set[str] = set()
⋮----
match = re.match(r'^\s{2}([A-Za-z0-9_]+):', raw)
⋮----
def _serial(adb: str) -> str | None
⋮----
devices = run_command([adb, 'devices'], timeout=30).stdout.splitlines()
serials = [line.split()[0] for line in devices[1:] if '\tdevice' in line]
⋮----
def _ui_classes(xml: str) -> set[str]
⋮----
def validate_platform_views(root: Path, out: Path, adb: str = 'adb') -> dict
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
deps = _dependencies(root)
blockers: list[str] = []
⋮----
evidence = {'passed': False, 'dependencies': deps, 'blockers': blockers}
⋮----
evidence = {'passed': False, 'dependencies': deps, 'blockers': ['adb_unavailable']}
⋮----
emulator = None
owned = False
serial = _serial(adb)
⋮----
emulator = start_emulator()
owned = True
boot = wait_for_boot(adb)
⋮----
pkg = package_name(root)
⋮----
install = run_command([adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
⋮----
launch = run_command([adb, '-s', serial, 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'], timeout=60)
⋮----
dump_cmd = [adb, '-s', serial, 'shell', 'uiautomator', 'dump', '/sdcard/window.xml']
dumped = run_command(dump_cmd, timeout=60)
xml = run_command([adb, '-s', serial, 'shell', 'cat', '/sdcard/window.xml'], timeout=30).stdout if dumped.returncode == 0 else ''
classes = _ui_classes(xml)
expected = sorted({c for dep in deps for c in DEPENDENCIES[dep]})
observed = sorted(set(expected) & classes)
⋮----
first = out / 'platform-view-foreground.png'
⋮----
shot = subprocess.run([adb, '-s', serial, 'exec-out', 'screencap', '-p'], stdout=handle, stderr=subprocess.PIPE, timeout=60)
⋮----
logcat = run_command([adb, '-s', serial, 'logcat', '-d', '-v', 'brief'], timeout=60)
crash_lines = [line for line in logcat.stdout.splitlines() if any(p in line for p in CRASH_PATTERNS)]
⋮----
evidence = {
⋮----
def _write(out: Path, deps: list[str], blockers: list[str], **extra) -> dict
⋮----
evidence = {'passed': False, 'dependencies': deps, 'blockers': blockers, **extra}
````

## File: platform_view_stage.py
````python
"""Persist platform-view QA evidence into the autonomous checkpoint."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = evaluate_and_repair(root, out, state, req, 'platform_view_qa', validate_platform_views)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('platform_view_qa')
````

## File: play_publisher.py
````python
"""Trusted Google Play publication boundary.

The client uses the Android Publisher v3 edit transaction. Publication is
validate-only by default; committing an edit requires an explicit trusted flag.
Generated/model-controlled code never receives the OAuth access token.
"""
⋮----
API_BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
UPLOAD_BASE = "https://androidpublisher.googleapis.com/upload/androidpublisher/v3"
PACKAGE_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+")
TRACKS = {"internal", "alpha", "beta", "production"}
RELEASE_STATUSES = {"draft", "completed"}
⋮----
def publication_credentials(env: dict | None = None) -> dict
⋮----
current = os.environ if env is None else env
token = current.get("STUDIO_PLAY_ACCESS_TOKEN")
⋮----
class PlayPublisher
⋮----
def __init__(self, access_token: str, opener=urllib.request.urlopen)
⋮----
def _request(self, method: str, url: str, body: bytes | None = None, *, content_type="application/json") -> dict
⋮----
headers = {
⋮----
req = urllib.request.Request(url, method=method, data=body, headers=headers)
⋮----
raw = response.read()
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def create_edit(self, package_name: str) -> str
⋮----
package = urllib.parse.quote(package_name, safe="")
value = self._request("POST", f"{API_BASE}/applications/{package}/edits", b"{}")
edit_id = value.get("id")
⋮----
def upload_bundle(self, package_name: str, edit_id: str, bundle: Path) -> int
⋮----
edit = urllib.parse.quote(edit_id, safe="")
url = f"{UPLOAD_BASE}/applications/{package}/edits/{edit}/bundles?uploadType=media"
value = self._request(
version_code = value.get("versionCode")
⋮----
version_code = int(version_code)
⋮----
def update_track(self, package_name: str, edit_id: str, track: str, version_code: int, *, status="completed") -> dict
⋮----
track_q = urllib.parse.quote(track, safe="")
payload = json.dumps({
⋮----
def validate_edit(self, package_name: str, edit_id: str) -> dict
⋮----
def commit_edit(self, package_name: str, edit_id: str) -> dict
⋮----
client = PlayPublisher(access_token, opener=opener)
edit_id = client.create_edit(package_name)
version_code = client.upload_bundle(package_name, edit_id, signed_aab)
⋮----
committed = False
⋮----
committed = True
````

## File: play_stage.py
````python
"""Trusted Google Play validation/publication stage."""
⋮----
PACKAGE_PATTERNS = (
PACKAGE_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+')
⋮----
def detect_package_name(root: Path) -> str
⋮----
candidates = [
⋮----
text = path.read_text(errors='replace')
⋮----
match = pattern.search(text)
⋮----
def _human_action(state: dict, action: str, detail: str) -> dict
⋮----
# Preserve validated-preview semantics while recomputing the missing stage;
# only then expose the external human-action status.
original_status = state.get('status')
⋮----
def _ensure_signed_aab(root: Path, out: Path, state: dict, env: dict | None = None) -> Path | None
⋮----
release = state.setdefault('release_evidence', {}).setdefault('release_build', {})
artifact = out / 'app-release.aab'
signing = release.get('production_signing')
⋮----
credentials = signing_credentials(env, project_root=root)
⋮----
unsigned = root / 'build/app/outputs/bundle/release/app-release.aab'
⋮----
rebuilt = build_release(root, Sandbox(root))
⋮----
signing = sign_aab(
⋮----
req = request_check(json.loads(request_path.read_text()))
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
publication = state.get('publication_request')
⋮----
evidence = state.get('release_evidence', {}).get(prerequisite)
⋮----
current = os.environ if env is None else env
artifact = _ensure_signed_aab(root, out, state, current)
⋮----
play_credentials = publication_credentials(current)
⋮----
commit = publication.get('commit') is True
track = publication.get('track', 'internal')
⋮----
package_name = detect_package_name(root)
result = publisher(
⋮----
result = dict(result)
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
⋮----
evidence = state.get('release_evidence', {}).get('play_publish')
````

## File: portfolio_candidate_scheduler.py
````python
"""Bounded scheduler for speculative implementation portfolios."""
⋮----
MAX_CANDIDATES = 3
⋮----
@dataclass(frozen=True)
class PortfolioSchedule
⋮----
candidate_limit: int
agent_limit: int
model_limit: int
include_model: bool
continue_after_verified: bool
uncertainty: float
free_capacity: float
verification_pressure: float
marginal_value: float
reason: str
⋮----
def as_dict(self) -> dict
⋮----
def _free_capacity(status: dict) -> float
⋮----
best = 0.0
rows = status.get("providers")
⋮----
quota = row.get("monthly_quota")
⋮----
best = max(best, float(quota.get("remaining_ratio", 0.0) or 0.0))
⋮----
confidence = max(0.0, min(1.0, float(route_confidence or 0.0)))
uncertainty = 1.0 - confidence
available_agents = max(0, int(available_agents))
available_models = max(0, int(available_models))
available_candidate_count = available_agents + available_models
capacity = _free_capacity(capacity_status)
verification = max(0.0, float(verification_seconds or 0.0))
verification_pressure = min(1.0, verification / 300.0)
quality = (
# Expected value of another candidate falls as confidence, verification cost,
# and the quality of an already verified candidate rise.
marginal_value = uncertainty * capacity * (1.0 - 0.65 * verification_pressure)
⋮----
candidate_limit = 1
reason = "single candidate is sufficient"
⋮----
enough_time_for_two = remaining_seconds is None or remaining_seconds >= max(180.0, verification * 2.0)
enough_time_for_three = remaining_seconds is None or remaining_seconds >= max(360.0, verification * 3.0)
⋮----
candidate_limit = 2
reason = "uncertain route with abundant low-cost capacity"
⋮----
candidate_limit = 3
reason = "high uncertainty, abundant free capacity, cheap verification"
⋮----
include_model = strategy != "agent_only" and available_models > 0
⋮----
learned_width = max(1, min(MAX_CANDIDATES, int(recommended_width)))
⋮----
learned_width = candidate_limit
# Historical learning may reduce speculative breadth, but cannot widen
# a run beyond current safety/capacity conditions.
candidate_limit = min(candidate_limit, learned_width)
⋮----
model_limit = 0
agent_limit = min(available_agents, candidate_limit)
⋮----
agent_limit = 0
model_limit = min(available_models, candidate_limit)
⋮----
# Prefer heterogeneous portfolios: model+agent at width 2, and
# two independent direct models plus one agent at width 3.
⋮----
model_limit = 2
agent_limit = 1
⋮----
model_limit = 1
agent_limit = 2
⋮----
agent_limit = min(available_agents, max(0, candidate_limit - model_limit))
⋮----
actual_capacity = model_limit + agent_limit
candidate_limit = max(1, min(MAX_CANDIDATES, candidate_limit, max(1, actual_capacity)))
model_limit = min(model_limit, candidate_limit)
agent_limit = min(agent_limit, max(0, candidate_limit - model_limit))
continue_after_verified = (
````

## File: portfolio_scan.py
````python
"""Portfolio-wide similarity scan used before every autonomous project.

Only repository metadata is inspected. Source code from other repositories is
never executed. The output is advisory context for planning/reuse.
"""
⋮----
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_+.-]{2,}")
⋮----
def _tokens(value: object) -> set[str]
⋮----
def _repo_tokens(repo: dict) -> set[str]
⋮----
values = [
out: set[str] = set()
⋮----
def _list_owned(api: API, owner: str) -> list[dict]
⋮----
repos: list[dict] = []
# User-token path includes private repositories. If unavailable, fall back to
# the public owner endpoint.
⋮----
batch = api.call("GET", f"/user/repos?affiliation=owner&per_page=100&page={page}&sort=updated")
⋮----
repos = []
⋮----
# affiliation=owner already scopes to repositories owned by the
# authenticated GitHub user. Do not re-filter by the target repo owner:
# the target may live in another namespace while the user's own
# portfolio still contains useful prior work.
⋮----
public = API("https://api.github.com", api.key)
⋮----
batch = public.call("GET", f"/users/{quote(owner)}/repos?per_page=100&page={page}&sort=updated")
⋮----
def _deep_profile(api: API, repo: dict) -> dict
⋮----
full=repo.get("full_name")
default=repo.get("default_branch")
⋮----
branch=api.call("GET","/repos/"+full+"/branches/"+quote(default))
sha=branch.get("commit",{}).get("sha") if isinstance(branch,dict) else None
⋮----
tree=api.call("GET","/repos/"+full+"/git/trees/"+sha+"?recursive=1")
⋮----
paths=[item.get("path") for item in tree["tree"] if isinstance(item,dict) and item.get("type")=="blob" and isinstance(item.get("path"),str)]
markers=[x for x in ("pubspec.yaml","project.godot","package.json","pyproject.toml","requirements.txt","Cargo.toml","go.mod","pom.xml","build.gradle","build.gradle.kts") if x in paths]
readme=next((item for item in tree["tree"] if isinstance(item,dict) and str(item.get("path","")).lower()=="readme.md" and item.get("type")=="blob"),None)
excerpt=""
⋮----
blob=api.call("GET","/repos/"+full+"/git/blobs/"+readme["sha"])
⋮----
try: excerpt=base64.b64decode(blob.get("content","")).decode("utf-8")[:3000]
except Exception: excerpt=""
⋮----
def scan(target_repo: str, brief: str, out: Path, api: API) -> dict
⋮----
owner = target_repo.split("/", 1)[0]
target_name = target_repo.split("/", 1)[1]
wanted = _tokens(target_name) | _tokens(brief)
repos = _list_owned(api, owner)
ranked = []
⋮----
full = repo.get("full_name")
⋮----
tokens = _repo_tokens(repo)
overlap = sorted(wanted & tokens)
⋮----
score = len(overlap) * 10
⋮----
by_name={repo.get("full_name"):repo for repo in repos if isinstance(repo,dict)}
selected=ranked[:12]
⋮----
source=by_name.get(item["repo"])
⋮----
result = {
````

## File: post_preview.py
````python
"""Autonomous trusted stages executed after a validated preview."""
⋮----
def ensure_workspace(req: dict, root: Path, github: GitHub, branch: str) -> tuple[dict, str]
⋮----
"""Restore a validated checkpoint into a fresh trusted Flutter workspace."""
⋮----
state = json.loads((Path(req['_out']) / 'report.json').read_text())
⋮----
sandbox = Sandbox(root)
⋮----
saved = Path(td)
⋮----
rel = p.relative_to(saved).as_posix()
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
⋮----
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
stage = next_stage(state)
⋮----
github = GitHub(req['target_repo'])
branch = 'studio/' + req['id']
⋮----
state = restored
⋮----
parent = state.get('checkpoint_commit')
⋮----
evidence = build_release(root, Sandbox(root))
⋮----
bundle = root / 'build/app/outputs/bundle/release/app-release.aab'
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
credentials = signing_credentials(project_root=root)
⋮----
signed_path = out / 'app-release.aab'
signing = sign_aab(
⋮----
sha = github.publish(branch, parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
⋮----
evidence = state.get('release_evidence', {}).get('release_build')
````

## File: predictive_budget.py
````python
"""Predictive difficulty and verification-reserve estimator.

The estimator is intentionally deterministic and bounded. It does not execute
code or inspect secrets; callers pass aggregate repository and verification
signals only.
"""
⋮----
@dataclass(frozen=True)
class DifficultyEstimate
⋮----
score: float
band: str
verification_reserve_seconds: int
recommended_work_passes: int
recommended_agent_limit: int
⋮----
def as_dict(self) -> dict
⋮----
verify = 0.0 if verification_seconds is None else max(0.0, float(verification_seconds))
score = 0.0
⋮----
score = max(0.0, min(100.0, score))
⋮----
band = "low"
reserve = max(90, int(verify * 1.5))
passes = 1
agents = 1
⋮----
band = "medium"
reserve = max(120, int(verify * 1.75))
passes = 2
⋮----
band = "high"
reserve = max(180, int(verify * 2.0))
⋮----
agents = 2
⋮----
band = "very_high"
reserve = max(240, int(verify * 2.5))
⋮----
def can_start_generation(*, remaining_seconds: float | None, reserve_seconds: int, minimum_generation_seconds: int = 90) -> bool
⋮----
remaining = max(0.0, float(remaining_seconds))
````

## File: preemption_apply.py
````python
"""Apply checkpoint-safe fleet preemption decisions."""
⋮----
STATE_FILE = "preemption-state.json"
COOLDOWN_FILE = "preemption-cooldown.json"
DEFAULT_COOLDOWN_SECONDS = 1800
⋮----
def _cooldown_active(root: Path, project_id: str, now: float, cooldown_seconds: int) -> bool
⋮----
path = root / project_id / ".autonomy" / COOLDOWN_FILE
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
root = Path(root)
current = time.time() if now is None else float(now)
cooldown = max(60, int(cooldown_seconds))
plan_path = root / "capacity-plan.json"
⋮----
capacity_plan = json.loads(plan_path.read_text(encoding="utf-8"))
⋮----
preemption = capacity_plan.get("preemption")
actions = preemption.get("actions") if isinstance(preemption, dict) else None
results = []
⋮----
victim = str(action.get("victim_id") or "")
contender = str(action.get("contender_id") or "")
row = {"victim_id": victim, "contender_id": contender, "executed": False}
⋮----
checkpoint_path = root / victim / ".autonomy" / "execution-checkpoint.json"
⋮----
checkpoint = load_checkpoint(checkpoint_path)
⋮----
contender_row = next(
lease_tokens = max(
transferred = transfer_project_reservations(
state = {
state_path = root / victim / ".autonomy" / STATE_FILE
⋮----
cooldown_state = {
⋮----
cooldown_path = root / project_id / ".autonomy" / COOLDOWN_FILE
````

## File: preemption_controller.py
````python
"""Deterministic, checkpoint-aware preemption planning for fleet admission."""
⋮----
MIN_SCORE_DELTA = 0.10
MIN_PRIORITY_DELTA = 20
PREEMPTIBLE_RUNTIME = {"running", "deferred", "failed"}
SAFE_CHECKPOINT_PHASES = {"published", "complete", "verified"}
⋮----
def _by_id(rows)
⋮----
def plan(capacity_plan: dict, runtime_evidence: dict | None = None) -> dict
⋮----
projects = capacity_plan.get("projects") if isinstance(capacity_plan, dict) else None
admission = capacity_plan.get("admission") if isinstance(capacity_plan, dict) else None
decisions = admission.get("decisions") if isinstance(admission, dict) else None
⋮----
project_by_id = _by_id(projects)
evidence_by_id = runtime_evidence if isinstance(runtime_evidence, dict) else {}
admitted = [row for row in decisions if isinstance(row, dict) and row.get("admitted") is True]
waiting = [
⋮----
victims = []
⋮----
project = project_by_id.get(row.get("id"), {})
runtime = str(project.get("status") or "")
evidence = evidence_by_id.get(row.get("id"), {})
phase = str(evidence.get("checkpoint_phase") or "")
checkpoint_ok = bool(evidence.get("checkpoint_valid")) and phase in SAFE_CHECKPOINT_PHASES
⋮----
actions = []
used_victims = set()
⋮----
contender_project = project_by_id.get(contender.get("id"), {})
contender_score = float(contender.get("score", 0.0) or 0.0)
contender_priority = int(contender_project.get("priority", 50) or 50)
victim = next(
````

## File: privacy_audit.py
````python
"""Derive privacy policy and Play Data Safety evidence from the generated app."""
⋮----
NETWORK_MARKERS = (
LOCAL_STORAGE_MARKERS = (
SENSITIVE_PERMISSION_DATA = {
ANDROID_SCHEMA_URLS = (
⋮----
DEPENDENCY_CAPABILITIES = {
EXTERNAL_DATA_CAPABILITIES = {
CAPABILITY_DATA_CLASSES = {
⋮----
def _files(root: Path) -> list[Path]
⋮----
allowed = []
⋮----
base = root / folder
⋮----
def _text(root: Path) -> str
⋮----
chunks = []
⋮----
pubspec = root / 'pubspec.yaml'
⋮----
def _network_text(root: Path) -> str
⋮----
"""Return source text with declarative Android XML namespaces removed.

    Android manifest namespace URIs are metadata, not reachable network endpoints.
    Actual INTERNET permission is checked independently below.
    """
source = _text(root)
⋮----
source = source.replace(schema, '')
⋮----
def permissions(root: Path) -> list[str]
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
def dependency_names(root: Path) -> list[str]
⋮----
names = []
in_dependencies = False
⋮----
line = raw.rstrip()
⋮----
in_dependencies = True
⋮----
match = re.match(r'^\s{2}([A-Za-z_][A-Za-z0-9_-]*):', line)
⋮----
def dependency_capabilities(dependencies: list[str]) -> list[dict]
⋮----
found = []
dep_set = set(dependencies)
⋮----
hits = sorted(dep_set & names)
⋮----
def analyze(root: Path) -> dict
⋮----
network_source = _network_text(root)
perms = permissions(root)
deps = dependency_names(root)
network_markers = sorted(marker for marker in NETWORK_MARKERS if marker in network_source)
local_markers = sorted(marker for marker in LOCAL_STORAGE_MARKERS if marker in source)
sensitive = sorted(set(SENSITIVE_PERMISSION_DATA[p] for p in perms if p in SENSITIVE_PERMISSION_DATA))
internet_permission = 'android.permission.INTERNET' in perms
capabilities = dependency_capabilities(deps)
capability_names = sorted(item['capability'] for item in capabilities)
external_capabilities = sorted(
network_capable = internet_permission or bool(network_markers) or bool(external_capabilities)
local_storage = bool(local_markers)
⋮----
potential_data_classes = sorted(set(
⋮----
blockers = []
⋮----
def build_data_safety(audit: dict) -> dict
⋮----
def policy_text(app_title: str, audit: dict, data_safety: dict) -> str
⋮----
sections = [
⋮----
def build_privacy_package(root: Path, out: Path, state: dict) -> dict
⋮----
audit = analyze(root)
safety = build_data_safety(audit)
title = state.get('release_evidence', {}).get('store_metadata', {}).get('listing', {}).get('title')
⋮----
title = 'Mobile App'
folder = out / 'privacy'
⋮----
policy = policy_text(title, audit, safety)
⋮----
manifest = {
manifest_path = folder / 'data-safety.json'
⋮----
passed = safety['status'] == 'derived'
````

## File: privacy_stage.py
````python
"""Create and checkpoint privacy policy and Play Data Safety evidence."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
evidence = build_privacy_package(root, out, state)
⋮----
audit=evidence.get('audit', {})
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('privacy_policy')
````

## File: production_os_worker.py
````python
"""Production-OS worker bridge helpers for AI Dev Server."""
⋮----
BASE_WORKER_CAPABILITIES = [
⋮----
def _asset_forge_operational_status(environ=None) -> dict | None
⋮----
executable = shutil.which("asset-forge")
⋮----
env = dict(os.environ)
⋮----
completed = subprocess.run(
⋮----
payload = json.loads(completed.stdout)
⋮----
def worker_capabilities(environ=None, *, home: Path | None = None) -> list[str]
⋮----
del home  # Kept for backwards-compatible callers/tests.
capabilities = list(BASE_WORKER_CAPABILITIES)
status = _asset_forge_operational_status(environ)
⋮----
visual = status.get("capabilities")
⋮----
class ProductionOSWorkerError(RuntimeError)
⋮----
class _NoRedirect(urllib.request.HTTPRedirectHandler)
⋮----
def redirect_request(self, req, fp, code, msg, headers, newurl)
⋮----
def _default_opener(request, timeout)
⋮----
class ProductionOSClient
⋮----
parsed = urlsplit(str(base_url or "").strip())
loopback = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
local_http = (
⋮----
secret = str(token or "").strip()
⋮----
timeout_value = float(timeout)
⋮----
request = urllib.request.Request(
⋮----
status = int(getattr(response, "status", 200))
⋮----
raw = response.read(1_000_001)
⋮----
value = json.loads(raw.decode("utf-8"))
⋮----
def claim(self, worker_id: str, capabilities: list[str]) -> dict | None
⋮----
payload = self._post(
⋮----
job = payload.get("job")
⋮----
def ack(self, key: str, worker_id: str) -> dict | None
⋮----
def complete(self, payload: dict) -> dict | None
⋮----
def fail(self, payload: dict) -> dict | None
⋮----
secret = str(operator_token or "").strip()
⋮----
payload = {
⋮----
"""Return a safe global token-capacity snapshot for Production-OS."""
env = os.environ if environ is None else environ
base_url = str(env.get("OMNIROUTE_URL") or "").strip()
⋮----
snapshot = fetch_summary(
⋮----
authenticated = bool(snapshot.authenticated_usage)
⋮----
def _project_id(job_key: str) -> str
⋮----
digest = hashlib.sha256(str(job_key).encode("utf-8")).hexdigest()[:24]
⋮----
def _app_name(repository: str) -> str
⋮----
name = str(repository).rsplit("/", 1)[-1].lower()
name = re.sub(r"[^a-z0-9_]+", "_", name).strip("_")
⋮----
name = "app_" + name
⋮----
name = (name + "_app")[:40]
⋮----
def _brief(task: str, final_goal: str) -> str
⋮----
task = str(task or "").strip()
final_goal = str(final_goal or "").strip()
value = task or final_goal
⋮----
expanded = (
⋮----
def _is_visual_handoff(handoff: dict[str, Any]) -> bool
⋮----
text = " ".join(
patterns = (
⋮----
def _asset_forge_guidance(handoff: dict[str, Any]) -> str
⋮----
candidates = handoff.get("reuse_candidates", [])
⋮----
candidates = []
visual_caps = {
asset_forge_candidate = any(
contracts = handoff.get("tool_contracts")
contract = (
contract_declared = (
⋮----
def build_studio_request(job: dict[str, Any]) -> dict[str, Any]
⋮----
"""Convert one claimed Production-OS job to the trusted Studio request."""
⋮----
payload = job.get("payload")
⋮----
handoff = payload.get("handoff")
⋮----
repository = str(
task = str(handoff.get("task") or job.get("task") or "").strip()
final_goal = str(handoff.get("final_goal") or task).strip()
workflow_id = str(payload.get("workflow_id") or "").strip()
workflow_task_id = str(payload.get("workflow_task_id") or "").strip()
job_key = str(job.get("key") or "").strip()
⋮----
request = {
tool_contracts = handoff.get("tool_contracts")
⋮----
preference = str(handoff.get("agent_preference") or "auto").strip()
⋮----
raw_budget = handoff.get("token_budget")
⋮----
requested = int(raw_budget)
⋮----
envelope = requested
capacity_source = "production-os"
constrained = False
⋮----
remaining = max(0, int(capacity["remaining_tokens"]))
envelope = min(envelope, remaining)
constrained = envelope < requested
capacity_source = str(capacity.get("source") or "omniroute")
⋮----
row = {
⋮----
path = Path(output_root) / "capacity-plan.json"
⋮----
payload = {"schema": 1, "projects": []}
⋮----
current = json.loads(path.read_text(encoding="utf-8"))
⋮----
current = None
⋮----
payload = dict(current)
projects = payload.get("projects")
⋮----
projects = []
projects = [
⋮----
def _result_payload(result: dict[str, Any]) -> dict[str, Any]
⋮----
usage = result.get("usage")
evidence = result.get("evidence")
⋮----
status = str(result.get("status") or "failed")
next_stage = result.get("evidence", {}).get("next_stage") if isinstance(
reason = status if not next_stage else f"{status}: {next_stage}"
⋮----
"""Claim and execute at most one Production-OS job."""
⋮----
clock = time.monotonic
⋮----
capabilities = list(capabilities or worker_capabilities())
job = client.claim(worker_id, capabilities)
⋮----
key = str(job.get("key") or "")
⋮----
request = build_studio_request(job)
root = Path(output_root)
handoff = dict((job.get("payload") or {}).get("handoff") or {})
⋮----
project_out = root / request["id"]
⋮----
request_path = project_out / "production-os-request.json"
⋮----
heartbeat_interval = float(heartbeat_interval_seconds)
⋮----
stop_heartbeat = threading.Event()
heartbeat_errors: list[str] = []
⋮----
def keep_job_alive()
⋮----
heartbeat_thread = threading.Thread(
⋮----
started = float(clock())
⋮----
summary = run_project(
⋮----
duration = max(0.0, float(clock()) - started)
envelope = {
⋮----
result_path = project_out / "production-os-result.json"
⋮----
envelope = json.loads(result_path.read_text(encoding="utf-8"))
⋮----
envelope = write_production_os_result(
⋮----
status = "completed"
⋮----
status = "failed"
⋮----
parser = argparse.ArgumentParser(
⋮----
args = parser.parse_args(argv)
⋮----
base_url = str(env.get("PRODUCTION_OS_URL") or "").strip()
worker_token = str(
operator_token = str(
⋮----
missing = []
⋮----
cycles = 1 if args.once else int(args.cycles)
⋮----
poll_interval = float(args.poll_interval)
⋮----
sleeper = time.sleep
⋮----
client = client_factory(base_url, worker_token)
capabilities = capabilities_provider(env)
⋮----
completed_cycles = 0
⋮----
capacity = capacity_provider(env)
result = run_once_fn(
````

## File: project_budget.py
````python
"""Persistent project-wide model budget and repair-efficiency accounting."""
⋮----
DEFAULT_REPAIR_RESERVE = 12
MIN_GAIN_PER_CALL = 0.15
STAGNANT_BRANCH_CALL_LIMIT = 4
⋮----
def configure(state: dict, req: dict) -> dict
⋮----
max_calls = int(req.get("max_calls", 12))
max_cycles = int(req.get("max_cycles", 5))
total_limit = int(req.get("max_project_model_calls", max_calls * max_cycles + DEFAULT_REPAIR_RESERVE))
repair_limit = int(req.get("max_project_repair_calls", min(DEFAULT_REPAIR_RESERVE, total_limit)))
current = state.get("project_budget")
⋮----
current = {}
⋮----
def remaining(state: dict, *, repair: bool = False) -> int
⋮----
budget = state.get("project_budget", {})
⋮----
def can_spend(state: dict, calls: int = 1, *, repair: bool = False) -> bool
⋮----
calls = max(0, int(calls))
⋮----
def record_calls(state: dict, calls: int, *, repair: bool = False) -> dict
⋮----
budget = state.setdefault("project_budget", {})
⋮----
budget = record_calls(state, calls, repair=True)
⋮----
gain = max(0, int(blockers_before) - int(blockers_after))
⋮----
def branch_efficiency(task: dict) -> float
⋮----
calls = max(0, int(task.get("model_calls_spent", 0)))
⋮----
improvements = max(0, int(task.get("improvement_count", 0)))
⋮----
def branch_should_stop(task: dict) -> bool
⋮----
def apply_capacity_limit(state: dict, capacity_plan: dict, *, explicit_limit: bool) -> dict
⋮----
effective = capacity_plan.get("effective_limit")
⋮----
current = int(budget.get("model_call_limit", effective))
⋮----
def budget_status(state: dict) -> dict
⋮----
total_limit = int(budget.get("model_call_limit", 0))
total_spent = int(budget.get("model_calls_spent", 0))
repair_limit = int(budget.get("repair_call_limit", 0))
repair_spent = int(budget.get("repair_calls_spent", 0))
gain = float(budget.get("diagnostic_gain", 0.0))
````

## File: project_context.py
````python
"""Trusted PROJECT_CONTEXT.md generator for every factory-managed app."""
⋮----
FILE = 'PROJECT_CONTEXT.md'
⋮----
def _clean_list(value)
⋮----
def _bullets(items, fallback)
⋮----
def render(req: dict, state: dict) -> str
⋮----
product = state.get('product') if isinstance(state.get('product'), dict) else {}
completion = state.get('completion') if isinstance(state.get('completion'), dict) else {}
evidence = state.get('release_evidence') if isinstance(state.get('release_evidence'), dict) else {}
capability = evidence.get('capability_qa') if isinstance(evidence.get('capability_qa'), dict) else {}
journeys = product.get('journeys') if isinstance(product.get('journeys'), list) else []
journey_ids = [j.get('id') for j in journeys if isinstance(j, dict) and isinstance(j.get('id'), str)]
acceptance = _clean_list(product.get('acceptance_criteria'))
assumptions = _clean_list(product.get('assumptions'))
blockers = _clean_list(completion.get('blockers')) or _clean_list(state.get('blockers'))
profiles = _clean_list(capability.get('profiles'))
required = _clean_list(completion.get('required_stages'))
next_stage = completion.get('next_stage')
status = state.get('status', 'unknown')
architecture = state.get('architecture_decision') if isinstance(state.get('architecture_decision'), dict) else {}
chosen_arch = architecture.get('chosen') if isinstance(architecture.get('chosen'), list) else []
chosen_repos = [x.get('repo') for x in chosen_arch if isinstance(x, dict) and isinstance(x.get('repo'), str)]
architecture_eval = state.get('architecture_evaluation') if isinstance(state.get('architecture_evaluation'), dict) else {}
architecture_verdict = architecture_eval.get('verdict') if isinstance(architecture_eval.get('verdict'), str) else 'not evaluated'
architecture_benchmark = state.get('architecture_benchmark') if isinstance(state.get('architecture_benchmark'), dict) else {}
migration_candidates = architecture_benchmark.get('migration_candidates') if isinstance(architecture_benchmark.get('migration_candidates'), list) else []
migration_repos = [x.get('best_alternative') for x in migration_candidates if isinstance(x, dict) and isinstance(x.get('best_alternative'), str)]
drift_alerts = state.get('architecture_drift_alerts') if isinstance(state.get('architecture_drift_alerts'), list) else []
obsolescence = state.get('architecture_obsolescence') if isinstance(state.get('architecture_obsolescence'), dict) else {}
deprecations = obsolescence.get('deprecation_candidates') if isinstance(obsolescence.get('deprecation_candidates'), list) else []
replacement_plan = state.get('architecture_replacement_plan') if isinstance(state.get('architecture_replacement_plan'), dict) else {}
replacement_rows = replacement_plan.get('replacement_plans') if isinstance(replacement_plan.get('replacement_plans'), list) else []
replacement_learning = state.get('architecture_replacement_learning') if isinstance(state.get('architecture_replacement_learning'), dict) else {}
learned_replacements = replacement_learning.get('rankings') if isinstance(replacement_learning.get('rankings'), list) else []
replacement_reputation = state.get('architecture_replacement_reputation') if isinstance(state.get('architecture_replacement_reputation'), dict) else {}
reputation_entries = replacement_reputation.get('entries') if isinstance(replacement_reputation.get('entries'), list) else []
reputation_lines = []
⋮----
current = item.get('current_repo')
replacement = item.get('replacement_repo')
state_name = item.get('state')
⋮----
learned_replacement_lines = []
⋮----
samples = item.get('samples')
success = item.get('success_rate')
⋮----
replacement_lines = []
⋮----
risk = item.get('risk')
suffix = f" -> {replacement}" if isinstance(replacement, str) and replacement else ""
risk_text = f" [{risk}]" if isinstance(risk, str) and risk else ""
⋮----
deprecation_lines = []
⋮----
replacement = item.get('replacement_candidate')
⋮----
drift_lines = []
⋮----
repos = ', '.join(str(x) for x in item.get('repos', [])[:6])
⋮----
immediate = (
⋮----
def write(root: Path, req: dict, state: dict) -> Path
⋮----
path = root / FILE
````

## File: project_engine.py
````python
"""Trusted mobile project-engine identification and path policy.

This module is intentionally independent from model output. Engine selection is
based on repository markers and each engine gets its own bounded editable scope.
"""
⋮----
class EngineError(ValueError)
⋮----
@dataclass(frozen=True)
class EngineProfile
⋮----
name: str
marker: str
test_suffix: str
⋮----
FLUTTER = EngineProfile('flutter', 'pubspec.yaml', '_test.dart')
GODOT = EngineProfile('godot', 'project.godot', '.gd')
GENERIC = EngineProfile('generic', '*', '')
PROFILES = {profile.name: profile for profile in (FLUTTER, GODOT, GENERIC)}
⋮----
_GODOT_ROOT_EDITABLE = {'project.godot', 'export_presets.cfg'}
_GODOT_TEXT_EXTENSIONS = {'.gd', '.tscn', '.tres', '.svg', '.json', '.md', '.txt'}
_GODOT_EDITABLE_ROOTS = {'scripts', 'scenes', 'assets', 'tests', 'docs'}
_GODOT_RESTORE_EXACT = {
⋮----
def _safe(path: str) -> PurePosixPath
⋮----
parsed = PurePosixPath(path)
⋮----
def infer(paths) -> EngineProfile
⋮----
values = set()
⋮----
parsed = _safe(value)
⋮----
specialized = [profile for profile in (FLUTTER, GODOT) if profile.marker in values]
⋮----
def editable(path: str, engine: str) -> bool
⋮----
parsed = _safe(path)
⋮----
parts = parsed.parts
⋮----
def restorable(path: str, engine: str) -> bool
⋮----
def profile(name: str) -> EngineProfile
````

## File: project_memory.py
````python
"""Persistent trusted memory for projects, research and reusable experience."""
⋮----
VERSION = 1
KINDS = {"project", "research", "experience"}
⋮----
class MemoryError(ValueError)
⋮----
def _canon(value)
⋮----
def _seal(value)
⋮----
out = dict(value)
⋮----
def new_memory()
⋮----
def validate(memory)
⋮----
digest = memory.get("memory_sha256")
unsigned = dict(memory)
⋮----
def _validate_entry(entry)
⋮----
required = {
⋮----
entry = {
⋮----
out = {"version": VERSION, "entries": [*memory["entries"], entry]}
⋮----
def query(memory, *, project_id=None, kind=None, tags=None, reusable_only=False)
⋮----
wanted_tags = set(tags or [])
result = []
⋮----
def reusable_for_project(memory, target_project_id, *, tags=None)
⋮----
items = query(memory, tags=tags, reusable_only=True)
⋮----
def save(path, memory)
⋮----
path = Path(path)
⋮----
def load(path)
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
````

## File: project_recommendations.py
````python
"""Create non-blocking structured star-list recommendations for the current project phase."""
⋮----
_PHASE_NEEDS = {
⋮----
_PHASE_CAPABILITIES = {
⋮----
needs = list(_PHASE_NEEDS.get(phase, ["agent", "code"]))
⋮----
result = scan(
⋮----
result = {
````

## File: project_status.py
````python
"""Read-only status for an autonomous project output directory."""
⋮----
AUTONOMY_DIR = ".autonomy"
⋮----
def _read_handoff(project_out: Path) -> dict | None
⋮----
path = project_out / "user-input-required.json"
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
def read_status(project_out: Path | str) -> dict
⋮----
"""Return persisted status without invoking models, verifiers or project code."""
project_out = Path(project_out)
autonomy_root = project_out / AUTONOMY_DIR
goal = load_goal(autonomy_root / "goal.json")
runtime_path = autonomy_root / "runtime-state.json"
runtime = load_runtime_state(runtime_path, default={}) if runtime_path.is_file() else {}
handoff = _read_handoff(project_out)
completion = (goal.get("evidence") or {}).get("project_completion")
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Read autonomous project status without executing work")
⋮----
args = parser.parse_args(argv)
⋮----
status = read_status(Path(args.project_out))
````

## File: promoted_capabilities.py
````python
"""Trusted source-controlled registry for promoted generic capabilities."""
⋮----
DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "control" / "promoted_capabilities.json"
NAME_RE = re.compile(r"[a-z][a-z0-9_.-]{2,80}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
⋮----
class PromotedCapabilityError(ValueError)
⋮----
def provider_for(name: str) -> str
⋮----
slug = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
⋮----
def load(path=DEFAULT_REGISTRY)
⋮----
path = Path(path)
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
capabilities = value.get("capabilities")
⋮----
def _provider_file(provider: str, repo_root: Path) -> Path
⋮----
module = provider.removeprefix("studio.capabilities.")
⋮----
def sync_into_registry(registry, path=DEFAULT_REGISTRY, *, repo_root=None)
⋮----
promoted = load(path)
root = Path(repo_root) if repo_root is not None else path.resolve().parents[1]
result = registry
⋮----
entry = promoted["capabilities"][name]
provider = entry["provider"]
provider_file = _provider_file(provider, root)
⋮----
current = result["capabilities"][name]
⋮----
result = register(
````

## File: provider_cost.py
````python
"""Persistent provider monetary-cost memory."""
⋮----
ALPHA = 0.25
MAX_ROWS = 128
⋮----
def _key(provider: str, role: str) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
calls = max(0, int(row.get("calls", 0)))
ema = max(0.0, float(row.get("ema_cost_usd", 0.0)))
total = max(0.0, float(row.get("total_cost_usd", 0.0)))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
prompt = max(0, int(prompt_tokens))
completion = max(0, int(completion_tokens))
input_rate = max(0.0, float(input_cost_per_million))
output_rate = max(0.0, float(output_cost_per_million))
⋮----
def record(path: Path, provider: str, role: str, cost_usd: float) -> dict
⋮----
cost = max(0.0, float(cost_usd))
data = load(path)
key = _key(provider, role)
row = data.get(key, {"calls": 0, "ema_cost_usd": 0.0, "total_cost_usd": 0.0})
calls = int(row["calls"])
previous = float(row["ema_cost_usd"])
ema = cost if calls == 0 else ALPHA * cost + (1.0 - ALPHA) * previous
⋮----
def ema_cost(data: dict, provider: str, role: str) -> float
⋮----
row = data.get(_key(provider, role))
````

## File: provider_health.py
````python
"""Persistent provider health and circuit-breaker state.

Only aggregate counters and cooldown timestamps are stored. Credentials,
prompts, provider response bodies, and exception messages are never persisted.
"""
⋮----
DEFAULT_THRESHOLD = 3
DEFAULT_COOLDOWN_SECONDS = 300
MAX_COOLDOWN_SECONDS = 3600
MAX_ROWS = 64
LATENCY_ALPHA = 0.25
REPUTATION_HALF_LIFE_SECONDS = 14 * 24 * 60 * 60
REGIME_WINDOW = 8
⋮----
def _row(value)
⋮----
successes = max(0, int(value.get("successes", 0)))
failures = max(0, int(value.get("failures", 0)))
consecutive = max(0, int(value.get("consecutive_failures", 0)))
opened_until = max(0.0, float(value.get("opened_until", 0.0)))
raw_latency = value.get("latency_ms_ema")
last_observed_at = max(0.0, float(value.get("last_observed_at", 0.0) or 0.0))
recent_raw = value.get("recent_outcomes", [])
recent_outcomes = [1 if bool(item) else 0 for item in recent_raw[-REGIME_WINDOW:]] if isinstance(recent_raw, list) else []
latency_ms_ema = None if raw_latency is None else max(0.0, float(raw_latency))
⋮----
def load(path: Path) -> dict
⋮----
path = Path(path)
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
def _save(path: Path, data: dict) -> None
⋮----
def eligible(path: Path, provider: str, *, now: float | None = None) -> bool
⋮----
row = load(path).get(provider)
⋮----
current = time.time() if now is None else float(now)
⋮----
def _record_latency(row: dict, latency_ms: float | None) -> None
⋮----
sample = max(0.0, float(latency_ms))
⋮----
previous = row.get("latency_ms_ema")
⋮----
def record_success(path: Path, provider: str, *, latency_ms: float | None = None) -> dict
⋮----
data = load(path)
row = _row(data.get(provider))
⋮----
exponent = row["consecutive_failures"] - threshold
cooldown = min(MAX_COOLDOWN_SECONDS, cooldown_seconds * (2 ** exponent))
⋮----
def reliability_bonus(data: dict, provider: str) -> float
⋮----
"""Return a bounded empirical routing bonus from observed success history."""
row = data.get(provider)
⋮----
successes = int(row.get("successes", 0))
failures = int(row.get("failures", 0))
runs = successes + failures
⋮----
rate = successes / runs
⋮----
"""Feed one verified execution outcome back into routing health.

    Only post-verification outcomes should call this function. This prevents
    provider self-reported success from contaminating adaptive routing evidence.
    """
⋮----
def health_snapshot(path: Path, *, now: float | None = None) -> dict
⋮----
"""Return scheduler-ready, credential-free provider evidence."""
⋮----
snapshot = {}
⋮----
successes = max(0, int(row.get("successes", 0)))
failures = max(0, int(row.get("failures", 0)))
observations = successes + failures
reliability = (successes + 1) / (observations + 2)
⋮----
def scoped_key(provider: str, *, model: str | None = None, role: str | None = None) -> str
⋮----
"""Build a stable non-secret health key for provider/model/role specialization."""
provider = str(provider or "").strip()
⋮----
parts = [provider]
⋮----
"""Record both global provider health and a specialized provider/model/role view."""
⋮----
key = scoped_key(provider, model=model, role=role)
⋮----
"""Return smoothed specialized reliability, falling back to provider evidence."""
keys = [
⋮----
row = data.get(key)
⋮----
def regime_signal(row: dict) -> dict
⋮----
"""Detect sharp recent deterioration relative to smoothed historical quality."""
recent = row.get("recent_outcomes", [])
⋮----
recent_rate = sum(1 if bool(item) else 0 for item in recent) / len(recent)
⋮----
historical_rate = (successes + 1) / (successes + failures + 2)
gap = max(0.0, historical_rate - recent_rate)
detected = recent_rate <= 0.5 and gap >= 0.25
penalty = min(0.75, gap) if detected else 0.0
⋮----
def recovery_signal(row: dict) -> dict
⋮----
"""Detect sustained recent recovery relative to historical provider quality."""
⋮----
gap = max(0.0, recent_rate - historical_rate)
detected = recent_rate >= 0.75 and gap >= 0.20
bonus = min(0.35, gap) if detected else 0.0
⋮----
"""Return reliability plus confidence from the best available specialization."""
⋮----
# Saturating evidence confidence: 10 observations ~= 50%, 50 ~= 83%.
confidence = observations / (observations + 10.0)
⋮----
last_observed = max(0.0, float(row.get("last_observed_at", 0.0) or 0.0))
⋮----
freshness = 1.0
⋮----
age = max(0.0, current - last_observed)
freshness = 0.5 ** (age / float(half_life_seconds))
⋮----
regime = regime_signal(row)
recovery = recovery_signal(row)
⋮----
# Recovery boosts confidence in fresh positive evidence, but never above 1.
confidence = min(1.0, confidence * (1.0 + float(recovery["bonus"])))
adjusted_reliability = reliability
⋮----
adjusted_reliability = min(
````

## File: provider_metrics.py
````python
"""Role-scoped provider performance metrics used by adaptive routing."""
⋮----
ALPHA = 0.25
MAX_ROWS = 128
⋮----
def _key(provider: str, role: str) -> str
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
calls = max(0, int(row.get("calls", 0)))
ema = max(0.0, float(row.get("ema_latency_seconds", 0.0)))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, provider: str, role: str, duration_seconds: float) -> dict
⋮----
duration = max(0.0, float(duration_seconds))
data = load(path)
key = _key(provider, role)
row = data.get(key, {"calls": 0, "ema_latency_seconds": 0.0})
calls = int(row["calls"])
previous = float(row["ema_latency_seconds"])
ema = duration if calls == 0 else (ALPHA * duration + (1.0 - ALPHA) * previous)
⋮----
def latency_bonus(data: dict, provider: str, role: str) -> float
⋮----
"""Bounded bonus: fast providers gain modestly, slow ones lose modestly."""
row = data.get(_key(provider, role))
⋮----
latency = float(row.get("ema_latency_seconds", 0.0))
````

## File: provider_monthly_quota.py
````python
"""Monthly token-quota accounting for pooled free/high-quota providers."""
⋮----
DEFAULT_OMNIROUTE_MONTHLY_TOKENS = 1_470_000_000
DEFAULT_RESERVE_RATIO = 0.03
⋮----
def month_key(now: datetime | None = None) -> str
⋮----
current = now or datetime.now(timezone.utc)
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
months = value.get("months")
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
key = month_key(now)
month = data["months"].setdefault(key, {})
row = month.get(provider, {
prompt = max(0, int(prompt_tokens))
completion = max(0, int(completion_tokens))
row = {
⋮----
# Retain only the newest 14 calendar buckets.
⋮----
def used_tokens(path_or_data: Path | dict, provider: str, *, now: datetime | None = None) -> int
⋮----
data = load(path_or_data) if isinstance(path_or_data, Path) else path_or_data
months = data.get("months", {}) if isinstance(data, dict) else {}
row = months.get(month_key(now), {}).get(provider, {}) if isinstance(months, dict) else {}
⋮----
quota = max(0, int(monthly_token_quota))
used = used_tokens(path_or_data, provider, now=now)
remaining = max(0, quota - used) if quota else None
ratio = (remaining / quota) if quota else None
⋮----
"""Decide whether a metered pooled provider may accept another call.

    Non-critical work cannot consume the configured reserve. Critical work may
    use it, while still refusing calls that would exceed the remaining quota.
    """
⋮----
estimate = max(1, int(estimated_tokens))
⋮----
ratio = float(reserve_ratio)
⋮----
ratio = DEFAULT_RESERVE_RATIO
ratio = max(0.0, min(0.50, ratio))
⋮----
status = quota_status(path_or_data, provider, quota, now=now)
⋮----
remaining = int(status["remaining_tokens"] or 0)
reserve = min(quota, max(0, int(quota * ratio)))
spendable = remaining if allow_reserve else max(0, remaining - reserve)
admitted = estimate <= spendable
⋮----
reason = "within_remaining_quota"
⋮----
reason = "insufficient_remaining_quota"
⋮----
reason = "reserved_for_critical_work"
````

## File: provider_probe.py
````python
"""One bounded real-provider preview. Saves artifacts, never modifies a target repository."""
⋮----
class ArtifactProject
⋮----
"""Local delivery backend for a preview, with no GitHub write credentials."""
def __init__(self, out)
def restore(self, branch, root)
def publish(self, branch, parent, root, state)
⋮----
data = canonical(state)
⋮----
files = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
⋮----
# Checkpoint digest, explicitly not a GitHub commit.
⋮----
def main()
⋮----
config = json.loads(Path('control/provider-probe.json').read_text())
⋮----
out = Path('studio-output')
req = {'id': 'focus-provider-preview', 'target_repo': 'preview/focus', 'app_name': 'focus_preview',
⋮----
state = execute(req, Path('/tmp/provider-preview-app'), out, github=ArtifactProject(out))
````

## File: provider_router.py
````python
"""Provider registry and ordered fallback policy for AI Dev Server."""
⋮----
@dataclass(frozen=True)
class ProviderSpec
⋮----
name: str
base: str
key: str
model: str
code_model: str = ""
vision_model: str = ""
priority: int = 50
free_preferred: bool = True
input_cost_per_million: float = 0.0
output_cost_per_million: float = 0.0
unmetered: bool = False
monthly_token_quota: int = 0
role_models: dict[str, str] = field(default_factory=dict)
⋮----
def model_for(self, role: str, screenshots: bool = False) -> str
⋮----
explicit = self.role_models.get(role)
⋮----
def _is_local_base(base: str) -> bool
⋮----
text = (base or "").strip().lower()
⋮----
def _bool(value, default=True)
⋮----
def _auto_omniroute() -> ProviderSpec | None
⋮----
base = os.environ.get("STUDIO_OMNIROUTE_BASE", "http://127.0.0.1:20128/v1").rstrip("/")
⋮----
req = urllib.request.Request(
⋮----
raw = response.read(200000)
value = json.loads(raw)
⋮----
def _primary() -> ProviderSpec | None
⋮----
base = os.environ.get("STUDIO_API_BASE", "https://integrate.api.nvidia.com/v1")
key = os.environ.get("STUDIO_API_KEY", "")
⋮----
model = os.environ.get("STUDIO_MODEL", "nvidia/nemotron-3-super-120b-a12b")
code_model = os.environ.get("STUDIO_CODE_MODEL", "") or model
vision = os.environ.get("STUDIO_VISION_MODEL", "")
⋮----
vision = "nvidia/nemotron-nano-12b-v2-vl"
⋮----
vision = ""
explicit_unmetered = os.environ.get("STUDIO_PROVIDER_UNMETERED")
role_models_raw = os.environ.get("STUDIO_ROLE_MODELS_JSON", "")
role_models = {}
⋮----
parsed_role_models = json.loads(role_models_raw)
⋮----
quota_raw = os.environ.get("STUDIO_MONTHLY_TOKEN_QUOTA", "")
⋮----
monthly_token_quota = max(0, int(quota_raw))
⋮----
monthly_token_quota = 1_470_000_000
⋮----
monthly_token_quota = 0
⋮----
def _json_specs(raw: str) -> list[ProviderSpec]
⋮----
data = json.loads(raw)
⋮----
specs = []
⋮----
allowed = {
⋮----
name = item.get("name") or f"fallback-{index + 1}"
base = item.get("base")
key_env = item.get("key_env")
model = item.get("model")
⋮----
local_base = _is_local_base(base)
⋮----
key = os.environ.get(key_env, "")
⋮----
key = ""
priority = item.get("priority", 50)
⋮----
role_models = item.get("role_models", {})
⋮----
clean_role_models = {}
⋮----
def _local_capacity_specs() -> list[ProviderSpec]
⋮----
name = str(row["name"])
base = str(row["base"])
quota = max(0, int(row.get("monthly_token_quota", 0) or 0))
⋮----
models = [
⋮----
models = [str(row["model"])]
vision_model = str(row.get("vision_model") or "")
⋮----
is_code = any(hint in model.lower() for hint in ("coder","code","qwen","deepseek","starcoder","codestral","devstral"))
is_vision = bool(vision_model and model == vision_model)
⋮----
def load_providers(*, prefer_free: bool = True) -> tuple[ProviderSpec, ...]
⋮----
primary = _primary()
explicit_json = os.environ.get("STUDIO_PROVIDERS_JSON", "")
⋮----
local_specs = _local_capacity_specs()
⋮----
auto_omniroute = _auto_omniroute()
⋮----
deduped = {}
⋮----
key = (
current = deduped.get(key)
⋮----
def sort_key(spec: ProviderSpec)
⋮----
unmetered_bonus = 2 if spec.unmetered else (1 if spec.monthly_token_quota > 0 else 0)
free_bonus = 1 if (prefer_free and spec.free_preferred) else 0
⋮----
specs = tuple(providers) if providers is not None else load_providers(prefer_free=prefer_free)
eligible = tuple(spec for spec in specs if spec.model_for(role, screenshots))
rejected = [
reliability_path = os.environ.get("STUDIO_WORKER_LIVENESS_PATH", "").strip()
⋮----
liveness = json.load(handle)
⋮----
reliability = summarize_runtime_reliability(liveness)
health_path = Path(os.environ.get("STUDIO_PROVIDER_HEALTH_PATH", "provider-health.json"))
metrics_path = Path(os.environ.get("STUDIO_PROVIDER_METRICS_PATH", "provider-metrics.json"))
health = load_provider_health(health_path)
metrics = load_provider_metrics(metrics_path)
calibration_path = os.environ.get("STUDIO_ROUTING_CALIBRATION_PATH", "").strip()
⋮----
calibration = json.loads(Path(calibration_path).read_text(encoding="utf-8"))
⋮----
calibration = {}
⋮----
current = tuple(
⋮----
scored = []
⋮----
model = spec.model_for(role, screenshots)
result = unified_provider_score(
⋮----
ordered = tuple(item[0] for item in scored)
audit_path = os.environ.get("STUDIO_ROUTING_AUDIT_PATH", "").strip()
⋮----
specs = tuple(providers)
limit = max(0.0, float(max_api_cost_usd))
spent = max(0.0, float(spent_api_cost_usd))
````

## File: provider_runtime_reliability.py
````python
"""Provider/model runtime reliability derived from worker liveness evidence."""
⋮----
def summarize(liveness: dict) -> dict
⋮----
workers = liveness.get("workers") if isinstance(liveness, dict) else []
buckets = {}
⋮----
provider = str(row.get("provider") or "").strip()
model = str(row.get("model") or "").strip()
⋮----
key = provider + "::" + (model or "*")
bucket = buckets.setdefault(key, {
classification = str(row.get("classification") or "")
⋮----
rows = {}
⋮----
positive = bucket["completed"]
negative = bucket["crashed"] + 0.75 * bucket["stalled"] + 0.5 * bucket["orphaned"]
score = (positive + 2.0) / (positive + negative + 4.0)
confidence = min(1.0, bucket["samples"] / 8.0)
⋮----
def routing_bonus(summary: dict, provider: str, model: str) -> float
⋮----
routes = summary.get("routes") if isinstance(summary, dict) else {}
row = routes.get(str(provider) + "::" + str(model)) if isinstance(routes, dict) else None
⋮----
row = routes.get(str(provider) + "::*")
⋮----
confidence = max(0.0, min(1.0, float(row.get("confidence", 0.0) or 0.0)))
score = max(0.05, min(0.95, float(row.get("reliability_score", 0.5) or 0.5)))
````

## File: queue.py
````python
"""Validate the entire trusted request queue before starting any privileged job."""
⋮----
def matrix(directory, terminal_ids=())
⋮----
terminal_ids = set(terminal_ids)
⋮----
req = request_check(json.loads(p.read_text()))
⋮----
target = req['target_repo'].lower()
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
⋮----
terminal_ids = json.loads(args.terminal_ids_json)
⋮----
projects = matrix('control/mobile-requests', terminal_ids)
````

## File: quick_gate_cache.py
````python
"""Run-local cache for deterministic quick validation results."""
⋮----
def delta_hash(files: list[dict]) -> str
⋮----
normalized = []
⋮----
path = item.get("path")
content = item.get("content")
⋮----
raw = json.dumps(
⋮----
def workspace_hash(snapshot: dict[str, str]) -> str
⋮----
def get(cache: dict, key: str) -> dict | None
⋮----
value = cache.get(key)
⋮----
def put(cache: dict, key: str, *, passed: bool, logs: list[dict]) -> None
````

## File: readiness.py
````python
"""Production-readiness gate for AI Dev Server runtime prerequisites."""
⋮----
REQUIRED_STATE_ENV = (
⋮----
def check(root: Path | str = ".", project_out: Path | str | None = None) -> dict
⋮----
root = Path(root).resolve()
project_out = Path(project_out).resolve() if project_out is not None else None
checks = {}
⋮----
ci_config = json.loads((root / "control/ci.json").read_text(encoding="utf-8"))
⋮----
providers = load_providers(prefer_free=True)
⋮----
providers = ()
⋮----
configured = bool(os.environ.get(name, "").strip())
⋮----
autonomy = project_out / ".autonomy"
defaults = {
configured = name in defaults
⋮----
required = list(checks)
passed = all(checks[name] for name in required)
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
report = check(project_out=args.project_out)
````

## File: recovery_controller.py
````python
"""Persistent recovery gate for projects paused by verified stagnation."""
⋮----
SCHEMA = 1
RECOVERY_MULTIPLIER = 0.15
⋮----
def _empty() -> dict
⋮----
def _load(path: Path) -> dict
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
def fingerprint(context: dict) -> str
⋮----
payload = json.dumps(context if isinstance(context, dict) else {}, sort_keys=True, separators=(",", ":"))
⋮----
project = str(project_id).strip()
⋮----
current = fingerprint(context)
path = Path(path)
⋮----
data = _load(path)
row = data["projects"].get(project, {})
last_pause = str(row.get("pause_fingerprint") or "")
last_attempt = str(row.get("last_recovery_fingerprint") or "")
⋮----
recover = False
reason = "pause_context_registered"
⋮----
recover = True
reason = "material_context_change"
⋮----
reason = "no_new_recovery_signal"
````

## File: release_candidate_search.py
````python
"""Isolated candidate search for release repair strategies."""
⋮----
MAX_CANDIDATES = 2
MAX_BRANCH_STEPS = 3
MAX_LOCAL_REFINEMENTS = 1
⋮----
def _candidate_score(candidate: dict) -> float
⋮----
changed_count = len(candidate.get("changed_files", []))
model_calls = max(0, int(candidate.get("model_calls", 0)))
elapsed = max(0.0, float(candidate.get("elapsed_seconds", 0.0)))
strategy_prior = float(candidate.get("strategy_prior_score", 0.0))
⋮----
def select_winner(candidates: list[dict]) -> dict | None
⋮----
passing = [item for item in candidates if item.get("passed") is True]
⋮----
ranked = sorted(
winner = dict(ranked[0])
⋮----
"""Legacy one-shot candidate path kept for focused unit tests."""
baseline = snapshot_workspace(root)
started = time.monotonic()
metadata = {}
⋮----
metadata = mutate()
delta = validate_delta(root, baseline)
changed = list(delta.get("changed", []))
⋮----
journeys = validate_journeys(state.get("product", {}).get("journeys"))
sandbox = sandbox_factory(root)
⋮----
elapsed = max(0.0, time.monotonic() - started)
candidate = {
⋮----
def apply_winner(root: Path, winner: dict) -> None
⋮----
files = winner.get("files", [])
⋮----
step_model_calls = [1] * len(steps)
⋮----
quick_gate_cache = {}
⋮----
full_gate_cache = {}
artifact_cache_enabled = artifact_cache is not None
⋮----
artifact_cache = {}
⋮----
metadata = {
⋮----
pending_failure = None
⋮----
before_step = snapshot_workspace(root)
step_started = time.monotonic()
result = step(pending_failure)
⋮----
result = {}
⋮----
step_trace = {
⋮----
step_delta = validate_delta(root, before_step)
quick_plan = plan_quick_gates(root, list(step_delta.get("changed", [])))
digest = delta_hash(list(step_delta.get("files", [])))
workspace_digest = workspace_hash(snapshot_workspace(root))
⋮----
quick_sandbox = sandbox_factory(root)
progressive = []
quick_passed = True
quick_failure = None
gate_specs = (
⋮----
gate_method = getattr(quick_sandbox, gate_method_name, None)
⋮----
fallback = getattr(quick_sandbox, "quick_gates")
⋮----
quick_passed = gate_ok is True
⋮----
quick_failure = canonical(gate_logs[-1:])[-4000:]
⋮----
targets = quick_plan["targeted_tests"] if gate_name == "test" else []
key = cache_key(
cached = cache_get(quick_gate_cache, key)
⋮----
gate_ok = cached["passed"]
gate_logs = cached["logs"]
from_cache = True
⋮----
from_cache = False
⋮----
quick_passed = False
⋮----
pending_failure = quick_failure
next_step_model_calls = step_model_calls[index]
⋮----
def validate_full_state()
⋮----
key = full_validation_key(root, app_name=app_name, journeys=journeys)
restored = None
restore_error = None
⋮----
restored = restore_artifacts(root, artifact_cache[key], key)
⋮----
restore_error = str(exc)
⋮----
gate_started = time.monotonic()
⋮----
gate_cost_seconds = max(0.0, time.monotonic() - gate_started)
⋮----
refinements = 0
⋮----
failure = canonical(logs[-1:])[-4000:]
refine_started = time.monotonic()
result = refine(failure)
````

## File: release_contract.py
````python
"""Validate VERSION, release manifest and required workflow contracts."""
⋮----
WORKFLOW_NAMES = {
⋮----
def validate(root: Path | str = ".") -> dict
⋮----
root = Path(root)
failures = []
⋮----
version_path = root / "VERSION"
manifest_path = root / "control/release.json"
⋮----
version = version_path.read_text(encoding="utf-8").strip()
⋮----
version = ""
⋮----
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
⋮----
manifest = {}
⋮----
gates = manifest.get("required_gates")
⋮----
gates = []
⋮----
missing_expected = sorted(set(WORKFLOW_NAMES) - set(gates))
⋮----
unknown = sorted(set(gates) - set(WORKFLOW_NAMES))
⋮----
workflow_files = {}
⋮----
path = root / rel
exists = path.is_file()
⋮----
commands = manifest.get("operational_commands")
⋮----
safety = manifest.get("safety")
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Validate AI Dev Server release contract")
⋮----
args = parser.parse_args(argv)
report = validate(args.root)
````

## File: release_readiness.py
````python
"""Machine-readable V1 release-candidate assessment for one project output."""
⋮----
def assess(project_out: Path) -> dict
⋮----
project_out = Path(project_out)
failures = []
evidence = {}
⋮----
report_path = project_out / "report.json"
⋮----
report = {}
⋮----
report = json.loads(report_path.read_text(encoding="utf-8"))
⋮----
completion = report.get("completion") if isinstance(report, dict) else None
⋮----
autonomy = project_out / ".autonomy"
runtime_path = autonomy / "runtime-state.json"
⋮----
runtime = load_recovering(runtime_path)
⋮----
runtime = {}
⋮----
telemetry_summary = summarize(autonomy / "telemetry.jsonl")
⋮----
checkpoint = autonomy / "workflow-checkpoints.json"
⋮----
artifact_cas = autonomy / "artifact-cas"
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
result = assess(Path(args.project_out))
````

## File: release_repair.py
````python
"""Generic bounded source repair for release-stage code diagnostics."""
⋮----
MAX_RELEASE_REPAIR_ROUNDS = 2
MAX_MODEL_CALLS_PER_BRANCH = 2
⋮----
def _persist_caches(quick_gate_cache: dict, full_gate_cache: dict, artifact_cache: dict | None) -> dict
⋮----
"""Persist optimization caches without invalidating a verified repair."""
errors = []
⋮----
def _context(root: Path, state: dict, stage: str, blockers: list[str], failure: str | None = None) -> str
⋮----
files = {}
⋮----
rel = path.relative_to(root).as_posix()
⋮----
text = path.read_text(errors="replace")
⋮----
def _agent_memory_path() -> Path
⋮----
raw = os.environ.get("STUDIO_AGENT_PERFORMANCE_PATH", "")
⋮----
def _agent_candidates() -> list[str]
⋮----
def _validate_agent_scope(root: Path, before: dict[str, str]) -> dict
⋮----
delta = validate_agent_delta(root, before)
⋮----
rel = item["path"]
⋮----
def _run_agent(root: Path, blockers: list[str], stage: str, failure: str | None = None) -> dict
⋮----
names = _agent_candidates()
⋮----
before = snapshot_agent_workspace(root)
prompt = (
result = execute_named_agent(names[0], prompt, cwd=root, timeout=900)
⋮----
delta = _validate_agent_scope(root, before)
⋮----
def _strategy_prior(selection: dict, strategy: str) -> float
⋮----
def _model_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory, failure: str | None = None)
⋮----
context = _context(root, state, stage, blockers, failure)
model = model_factory(4)
⋮----
last_provider = task.get("last_provider")
⋮----
files = patch_check(patch)
⋮----
effective_calls = max(0, int(model.calls) - int(getattr(model, "checkpoint_replays", 0)))
⋮----
def _agent_mutation(root: Path, blockers: list[str], stage: str, failure: str | None = None)
⋮----
evidence = _run_agent(root, blockers, stage, failure)
⋮----
def _hybrid_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory)
⋮----
metadata = _model_mutation(root, state, stage, blockers, task, model_factory)
⋮----
def _agent_to_model_mutation(root: Path, state: dict, stage: str, blockers: list[str], task: dict | None, model_factory)
⋮----
metadata = _agent_mutation(root, blockers, stage)
model_meta = _model_mutation(root, state, stage, blockers, task, model_factory)
⋮----
blockers = repairable(stage, evidence)
⋮----
# Fail before selecting either a model or an external agent. Both execution
# modes can inspect the workspace, so credential material must disable all
# autonomous source repair consistently.
⋮----
agents = _agent_candidates()
selection = choose_strategy(task, stage=stage, agent_available=bool(agents))
preferred = selection["strategy"]
⋮----
strategies = [preferred]
ranking = selection.get("candidate_ranking", [])
row_by_strategy = {
⋮----
candidates = []
quick_gate_cache = load_persistent_quick_cache()
full_gate_cache = load_full_gate_cache()
artifact_cache_enabled = (
artifact_cache = load_artifact_cache() if artifact_cache_enabled else None
⋮----
prior = _strategy_prior(selection, strategy_name)
⋮----
steps = [
step_model_calls = [1]
refine = lambda failure, s=state, st=stage, b=blockers, t=task: (
⋮----
step_model_calls = [0]
refine = lambda failure, st=stage, b=blockers: (
⋮----
step_model_calls = [0, 1]
⋮----
step_model_calls = [1, 0]
⋮----
already_spent = sum(
candidate = run_branch(
⋮----
current_winner = select_winner(candidates)
⋮----
name = row.get("strategy")
⋮----
winner = select_winner(candidates)
⋮----
cache_persistence = _persist_caches(
⋮----
def _restore(root: Path, snapshot: dict[str, bytes | None]) -> None
⋮----
path = root / rel
````

## File: release_stage_engine.py
````python
"""Shared bounded repair loop for release QA stages."""
⋮----
evidence = validator(root, out)
history = []
environment_retries = []
⋮----
initial_diagnostics = classify(stage, evidence)
initial_plan = plan(stage, initial_diagnostics)
initial_task = None
⋮----
initial_task = enqueue(
⋮----
retryable = retryable_environment(stage, evidence)
diagnostics = classify(stage, evidence)
⋮----
selected = scheduler_select(state)
⋮----
repair_plan = plan(stage, diagnostics)
task = initial_task
⋮----
task = enqueue(state, repair_plan, estimated_model_calls=MAX_MODEL_CALLS_PER_BRANCH)
⋮----
blockers_before = len(evidence.get('blockers', []))
⋮----
result = repair_attempt(
⋮----
evidence = {
⋮----
final_plan = evidence["repair_plan"]
⋮----
def apply_external_gate(state: dict, stage: str, evidence: dict) -> bool
⋮----
diagnostics = evidence.get("diagnostics") or classify(stage, evidence)
blockers = list(diagnostics.get("human_or_external", []))
⋮----
def invalidate_for_source_change(state: dict, evidence: dict) -> bool
````

## File: release.py
````python
"""Trusted post-preview release evidence collection.

This module performs only deterministic build/evidence work. Model output never
controls shell commands and signing credentials are never placed in model context.
"""
⋮----
def build_release(root: Path, sandbox: Sandbox | None = None) -> dict
⋮----
"""Build release AAB + APK and return verifiable evidence.

    The AAB is the store-oriented artifact. The APK is produced from the same
    source/release mode so trusted Android emulator QA can install exactly the
    release configuration instead of falling back to a debug build.
    """
sandbox = sandbox or Sandbox(root)
commands = [
logs = []
⋮----
bundle = root / 'build/app/outputs/bundle/release/app-release.aab'
apk = root / 'build/app/outputs/flutter-apk/app-release.apk'
⋮----
bundle_raw = bundle.read_bytes()
apk_raw = apk.read_bytes()
````

## File: repair_planner.py
````python
"""Deterministic repair planning from normalized diagnostics."""
⋮----
PRIORITY = (
⋮----
def plan(stage: str, diagnostics: dict) -> dict
⋮----
selected = "complete"
blockers: list[str] = []
⋮----
values = diagnostics.get(bucket, [])
⋮----
selected = action
blockers = list(values)
⋮----
def preview_plan(stage: str, blockers: list[str], *, kind: str = "code") -> dict
⋮----
diagnostics = {
⋮----
kind = "unknown"
````

## File: repair_queue.py
````python
"""Persistent deterministic repair-task queue stored inside studio state."""
⋮----
MAX_TASKS = 64
MAX_ATTEMPTS = 4
⋮----
ACTION_PRIORITY = {
⋮----
def _fingerprint(stage: str, action: str, blockers: list[str]) -> str
⋮----
raw = json.dumps(
⋮----
def _queue(state: dict) -> list[dict]
⋮----
value = state.setdefault("repair_queue", [])
⋮----
value = []
⋮----
action = repair_plan.get("action")
blockers = [
stage = repair_plan.get("stage")
⋮----
task_id = _fingerprint(stage, str(action), blockers)
queue = _queue(state)
⋮----
task = {
⋮----
terminal = [x for x in queue if x.get("status") in {"completed", "superseded"}]
⋮----
victim = terminal.pop(0)
⋮----
def score_task(task: dict) -> int
⋮----
base = int(ACTION_PRIORITY.get(task.get("action"), 20))
attempts = max(0, int(task.get("attempts", 0)))
stagnation = max(0, int(task.get("stagnation_count", 0)))
dependency_penalty = 20 if task.get("dependencies") else 0
cost_penalty = min(15, max(0, int(task.get("estimated_model_calls", 0))) * 3)
⋮----
def recover_expired_leases(state: dict, *, now: float | None = None) -> int
⋮----
recovered = 0
⋮----
def next_task(state: dict) -> dict | None
⋮----
completed = {x.get("id") for x in queue if x.get("status") == "completed"}
candidates = []
⋮----
deps = set(task.get("dependencies", []))
⋮----
history = list(task.get("strategy_history", []))
⋮----
providers = providers_used or {}
⋮----
used = [name for name in providers.values() if isinstance(name, str) and name]
⋮----
history = list(task.get("providers_history", []))
⋮----
def complete_stage_tasks(state: dict, stage: str) -> None
⋮----
def summarize(state: dict) -> dict
````

## File: repair_search_policy.py
````python
"""Adaptive depth policy for bounded repair search."""
⋮----
MIN_EXPANSION_VALUE = 8.0
MIN_REFINEMENT_VALUE = 10.0
⋮----
def branch_cost(row: dict) -> int
⋮----
def expected_value(row: dict) -> float
⋮----
success = max(0.0, min(1.0, float(row.get("conservative_success_rate", 0.5))))
risk = max(0.0, min(1.0, float(row.get("risk", 0.4))))
seconds = max(0.0, float(row.get("estimated_seconds", 30.0)))
calls = branch_cost(row)
⋮----
calls = branch_cost(candidate_row)
⋮----
value = expected_value(candidate_row)
⋮----
current = float(current_winner.get("candidate_score", -1_000_000.0))
# Once a verified winner exists, only spend more if learned evidence is
# materially strong; candidate_score has a 1000-point verified baseline.
⋮----
# Continuing a broken intermediate state is only justified for strategies
# with meaningful expected value. This lets a later agent/model repair an
# intermediate compile/test regression without blindly exploring.
````

## File: repair_strategy.py
````python
"""Repair-strategy selection and cross-project efficiency learning."""
⋮----
DEFAULT_STRATEGY = "model_only"
REPAIR_STRATEGIES = {"model_only", "agent_only", "model_to_agent", "agent_to_model"}
⋮----
RISK_PRIOR = {
CALL_COST_PRIOR = {
⋮----
def rank_candidates(data: dict, allowed: set[str]) -> list[dict]
⋮----
rows = []
⋮----
info = strategy_metrics(data, strategy)
success = float(info.get("conservative_success_rate", 0.5)) if info else 0.5
seconds = float(info.get("ema_cost_seconds", 30.0)) if info else 30.0
risk = float(RISK_PRIOR.get(strategy, 0.4))
calls = int(CALL_COST_PRIOR.get(strategy, 1))
score = success * 100.0 - min(25.0, seconds / 12.0) - risk * 30.0 - calls * 4.0
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_STRATEGY_EFFICIENCY_PATH", "")
⋮----
def load_data() -> dict
⋮----
path = _path()
⋮----
def _contextual_path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_CONTEXTUAL_STRATEGY_EFFICIENCY_PATH", "")
⋮----
def _context(stage: str) -> str
⋮----
def choose(task: dict | None, *, stage: str, agent_available: bool) -> dict
⋮----
allowed = {"model_only"}
⋮----
data = load_data()
source = "global"
contextual_path = _contextual_path()
contextual_rows = {}
⋮----
contextual_rows = rows_for(load_contextual(contextual_path), _context(stage))
selected = select_strategy(contextual_rows, allowed=allowed) if contextual_rows else None
⋮----
source = "stage_context"
⋮----
selected = select_strategy(data, allowed=allowed)
⋮----
name = DEFAULT_STRATEGY
mode = "bootstrap"
metrics = {}
⋮----
mode = metrics.get("selection_mode", "learned")
⋮----
previous = task.get("last_strategy")
alternatives = [
⋮----
name = alternatives[0]
mode = "stagnation_rotation"
⋮----
ranking_source = contextual_rows if source == "stage_context" else data
⋮----
def record_outcome(strategy: str, *, stage: str, success: bool, cost_seconds: float) -> None
````

## File: replacement_ci_policy_check.py
````python
"""CI entry point validating replacement-required GitHub check names."""
⋮----
def main(argv=None) -> int
⋮----
args=list(sys.argv[1:] if argv is None else argv)
path=Path(args[0]) if args else Path(".github/workflows/ci.yml")
⋮----
result=validate_workflow(path)
⋮----
result={"valid":False,"missing_checks":["workflow_unreadable"]}
````

## File: replacement_ci_policy_v11.py
````python
"""Single source of truth for replacement GitHub CI trust requirements."""
⋮----
REQUIRED_GITHUB_CHECKS=frozenset({"validate","python-tests"})
TRUSTED_CHECK_APP="github-actions"
REQUIRED_WORKFLOW_NAME="CI"
REQUIRED_WORKFLOW_PATH=".github/workflows/ci.yml"
CI_TRUST_POLICY_VERSION=11
REQUIRED_WORKFLOW_PERMISSIONS={"contents":"read"}
REQUIRED_JOB_RUNNER="ubuntu-latest"
REQUIRED_JOB_TIMEOUTS={"validate":5,"python-tests":20}
FORBIDDEN_WORKFLOW_TRIGGERS=frozenset({"pull_request_target","workflow_run"})
FORBIDDEN_JOB_KEYS=frozenset({"strategy","needs","if","continue-on-error","environment","container","services"})
FORBIDDEN_STEP_KEYS=frozenset({"if","continue-on-error","timeout-minutes"})
FORBIDDEN_EXPRESSION_CONTEXTS=frozenset({"secrets","github.event","github.token","github.actor","github.triggering_actor","vars","inputs","matrix","strategy","needs"})
FORBIDDEN_RUN_TOKENS=frozenset({"curl","wget","sudo","docker","podman","GITHUB_ENV","GITHUB_PATH","GITHUB_OUTPUT","GITHUB_STATE","GITHUB_STEP_SUMMARY"})
FORBIDDEN_RUN_PREFIXES=("pip install","pip3 install","npm install","npm ci","npx ","yarn ","pnpm ","apt install","apt-get install","git clone","git fetch","git pull","gh ")
REQUIRED_RUN_SHELL="bash"
FORBIDDEN_YAML_FEATURES=frozenset({"anchor","alias","tag","merge_key","tab_indentation","duplicate_key"})
ALLOWED_ROOT_KEYS=frozenset({"name","on","permissions","concurrency","jobs"})
ALLOWED_JOB_KEYS=frozenset({"name","runs-on","timeout-minutes","steps"})
ALLOWED_STEP_KEYS=frozenset({"name","uses","with","run","shell","env"})
ACTION_WITH_ALLOWLIST={
RUN_ENV_ALLOWLIST={"PYTHONPATH":"studio"}
REQUIRED_WORKFLOW_TRIGGERS={"push":{"branches":("main",)},"pull_request":{}}
REQUIRED_CONCURRENCY_GROUP="ci-${{ github.workflow }}-${{ github.ref }}"
REQUIRED_CONCURRENCY_CANCEL=True
REQUIRED_JOB_STEP_FINGERPRINTS={
⋮----
TRUSTED_ACTION_REVISIONS={
⋮----
def ci_trust_policy_digest() -> str
⋮----
payload={
⋮----
def _yaml_code(line: str) -> str
⋮----
"""Strip comments outside simple quoted scalars; sufficient for trusted CI subset."""
quote=None
escaped=False
out=[]
⋮----
out.append(ch); escaped=False; continue
⋮----
out.append(ch); escaped=True; continue
⋮----
if quote is None: quote=ch
elif quote==ch: quote=None
⋮----
def validate_yaml_surface_text(text: str) -> dict
⋮----
violations=[]
mapping_keys={}
stack=[]
sequence_ids={}
⋮----
leading=line[:len(line)-len(line.lstrip(" \t"))]
⋮----
code=_yaml_code(line)
⋮----
indent=len(code)-len(code.lstrip(" "))
stripped=code.lstrip()
⋮----
parent=tuple(item[1] for item in stack)
is_sequence_item=stripped.startswith("- ")
⋮----
seq_key=(parent,indent)
⋮----
sequence_id=sequence_ids.get((parent,indent),0)
match=re.match(r"^\s*(?:-\s*)?([A-Za-z0-9_-]+):",code)
⋮----
key=match.group(1)
scope=(parent,indent,sequence_id)
bucket=mapping_keys.setdefault(scope,set())
⋮----
segment=key+("#"+str(sequence_id) if sequence_id else "")
⋮----
def validate_workflow_schema_text(text: str) -> dict
⋮----
violations=[]; current_job=None; in_jobs=False; in_steps=False
⋮----
root=re.match(r"^([A-Za-z0-9_-]+):",code)
⋮----
key=root.group(1); in_jobs=(key=="jobs"); current_job=None; in_steps=False
⋮----
job=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",code)
⋮----
current_job=job.group(1); in_steps=False; continue
⋮----
job_key=re.match(r"^    ([A-Za-z0-9_-]+):",code)
⋮----
key=job_key.group(1); in_steps=(key=="steps")
⋮----
step_key=re.match(r"^      -\s+([A-Za-z0-9_-]+):",code)
⋮----
nested=re.match(r"^        ([A-Za-z0-9_-]+):",code)
⋮----
def validate_trigger_concurrency_text(text: str) -> dict
⋮----
violations=[]; triggers=set(); push_branches=[]; in_on=False; in_push=False; concurrency={}; in_concurrency=False
⋮----
if code=="on:": in_on=True; in_push=False; in_concurrency=False; continue
if code=="concurrency:": in_concurrency=True; in_on=False; in_push=False; continue
if code and not code.startswith(" "): in_on=False; in_push=False; in_concurrency=False
⋮----
m=re.match(r"^  ([A-Za-z0-9_-]+):\s*(.*)$",code)
⋮----
trigger=m.group(1); triggers.add(trigger); in_push=(trigger=="push"); continue
⋮----
b=re.match(r"^    branches:\s*\[\s*['\"]?([^'\"\], ]+)['\"]?\s*\]\s*$",code)
if b: push_branches=[b.group(1)]
⋮----
m=re.match(r"^  (group|cancel-in-progress):\s*(.+?)\s*$",code)
⋮----
def validate_step_inputs_env_text(text: str) -> dict
⋮----
violations=[]; current_action=None; current_run=False; mode=None; mode_indent=None
⋮----
if re.match(r"^      -\s+(?:name:\s*.*)?$",code): current_action=None; current_run=None; mode=None
uses=re.match(r"^        uses:\s*([^#\s]+)",code) or re.match(r"^      -\s+uses:\s*([^#\s]+)",code)
⋮----
value=uses.group(1).strip().strip("'\""); current_action=value.rsplit("@",1)[0] if "@" in value else value; current_run=False; mode=None; continue
if re.match(r"^        run:\s*",code) or re.match(r"^      -\s+run:\s*",code): current_run=True; current_action=None; mode=None
block=re.match(r"^        (with|env):\s*$",code)
⋮----
mode=block.group(1); mode_indent=8
⋮----
item=re.match(r"^          ([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*$",code)
⋮----
key=item.group(1); value=item.group(2).strip().strip("'\"")
⋮----
allowed=ACTION_WITH_ALLOWLIST.get(current_action,frozenset())
⋮----
expected=RUN_ENV_ALLOWLIST.get(key)
⋮----
if code.strip() and len(code)-len(code.lstrip(" "))<=mode_indent: mode=None
⋮----
def validate_exact_job_steps_text(text: str) -> dict
⋮----
violations=[]; jobs={}; current_job=None; current_step=None; in_jobs=False; lines=text.splitlines(); i=0
⋮----
line=lines[i]
if line=="jobs:": in_jobs=True; i+=1; continue
⋮----
jm=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",line)
if jm: current_job=jm.group(1); jobs[current_job]=[]; current_step=None; i+=1; continue
sm=re.match(r"^      - name:\s*(.+?)\s*$",line)
if sm and current_job: current_step={"name":sm.group(1).strip().strip("'\"")}; jobs[current_job].append(current_step); i+=1; continue
⋮----
um=re.match(r"^        uses:\s*([^#\s]+)",line)
⋮----
value=um.group(1).strip().strip("'\""); current_step["uses"]=value.rsplit("@",1)[0] if "@" in value else value
rm=re.match(r"^        run:\s*(.*)$",line)
⋮----
tail=rm.group(1).strip()
⋮----
body=[]; i+=1
⋮----
child=lines[i]
⋮----
actual=jobs.get(job)
⋮----
def _scalar_yaml_value(value: str)
⋮----
value=value.split("#",1)[0].strip().strip("'\"").lower()
⋮----
def validate_workflow_permissions_text(text: str) -> dict
⋮----
lines=text.splitlines(); top_permissions=None; job_permissions=[]; i=0
⋮----
line=lines[i]; match=re.match(r"^(\s*)permissions:\s*(.*?)\s*$",line)
⋮----
indent=len(match.group(1)); tail=match.group(2); block={}
if tail: block=_scalar_yaml_value(tail); i+=1
⋮----
child_indent=len(child)-len(child.lstrip(" "))
⋮----
item=re.match(r"^\s+([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*(?:#.*)?$",child)
⋮----
if indent==0: top_permissions=block
⋮----
def validate_workflow_runtime_text(text: str) -> dict
⋮----
forbidden_triggers=sorted(trigger for trigger in FORBIDDEN_WORKFLOW_TRIGGERS if re.search(r"(?m)^\s{0,2}"+re.escape(trigger)+r"\s*:",text))
⋮----
jobs={}; in_jobs=False; current=None
⋮----
if line=="jobs:": in_jobs=True; current=None; continue
⋮----
m=re.match(r"^  ([A-Za-z0-9_-]+):\s*$",line)
if m: current=m.group(1); jobs[current]={"runs_on":None,"timeout_minutes":None}; continue
⋮----
m=re.match(r"^    runs-on:\s*([^#\n]+?)\s*(?:#.*)?$",line)
⋮----
m=re.match(r"^    timeout-minutes:\s*(\d+)\s*(?:#.*)?$",line)
⋮----
row=jobs.get(job)
⋮----
expected=REQUIRED_JOB_TIMEOUTS[job]
⋮----
def validate_workflow_expression_policy_text(text: str) -> dict
⋮----
violations=[]; expressions=re.findall(r"\$\{\{(.*?)\}\}",text,flags=re.DOTALL)
⋮----
normalized=re.sub(r"\s+","",expression).lower()
⋮----
in_jobs=False; current_job=None; in_steps=False
⋮----
if line=="jobs:": in_jobs=True; current_job=None; in_steps=False; continue
⋮----
if m: current_job=m.group(1); in_steps=False; continue
⋮----
m=re.match(r"^    ([A-Za-z0-9_-]+):",line)
⋮----
if re.match(r"^    steps:\s*$",line): in_steps=True; continue
⋮----
m=re.match(r"^      (?:-\s+)?([A-Za-z0-9_-]+):",line)
⋮----
def validate_workflow_run_commands_text(text: str) -> dict
⋮----
violations=[]; run_commands=[]
⋮----
m=re.match(r"^\s*(?:-\s*)?run:\s*(.+?)\s*$",line)
⋮----
command=m.group(1).strip().strip("'\""); run_commands.append({"line":lineno,"command":command}); lowered=command.lower()
⋮----
m=re.match(r"^\s*(?:-\s*)?shell:\s*([^#\n]+?)\s*(?:#.*)?$",line)
⋮----
value=m.group(1).strip().strip("'\"")
⋮----
def workflow_action_uses_text(text: str) -> list[dict]
⋮----
rows=[]; pattern=re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*([^#\s]+)\s*(?:#.*)?$")
⋮----
value=match.group(1).strip().strip("'\"")
⋮----
def validate_action_pinning_text(text: str) -> dict
⋮----
uses=workflow_action_uses_text(text); violations=[]; trusted=[]
⋮----
action=row["action"]; revision=row["revision"]
⋮----
expected=TRUSTED_ACTION_REVISIONS.get(action)
⋮----
def workflow_job_ids_text(text: str) -> set[str]
⋮----
jobs=set(); in_jobs=False
⋮----
if line.strip()=="jobs:" and not line.startswith(" "): in_jobs=True; continue
⋮----
def workflow_job_ids(path: Path) -> set[str]: return workflow_job_ids_text(path.read_text(encoding="utf-8"))
⋮----
def workflow_semantic_manifest_text(text: str) -> dict
⋮----
validation=validate_workflow_text(text,include_semantic=False)
⋮----
manifest={"workflow_name":validation["workflow_name"],"jobs":validation["exact_job_steps"]["jobs"],"permissions":validation["permissions"]["workflow_permissions"],"runtime":validation["runtime"]["jobs"],"triggers":validation["trigger_concurrency"]["triggers"],"push_branches":validation["trigger_concurrency"]["push_branches"],"concurrency":validation["trigger_concurrency"]["concurrency"],"actions":validation["action_pinning"]["uses"],"step_inputs_env":{"action_with_allowlist":validation["step_inputs_env"]["action_with_allowlist"],"run_env_allowlist":validation["step_inputs_env"]["run_env_allowlist"]}}
encoded=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode("utf-8")
⋮----
def validate_workflow_text(text: str, *, include_semantic: bool=True) -> dict
⋮----
yaml_surface=validate_yaml_surface_text(text); schema=validate_workflow_schema_text(text); step_env=validate_step_inputs_env_text(text); trigger=validate_trigger_concurrency_text(text); exact=validate_exact_job_steps_text(text)
jobs=workflow_job_ids_text(text); missing=sorted(REQUIRED_GITHUB_CHECKS-jobs); m=re.search(r"(?m)^name:\s*([^#\n]+?)\s*$",text); workflow_name=m.group(1).strip().strip("'\"") if m else None
actions=validate_action_pinning_text(text); permissions=validate_workflow_permissions_text(text); runtime=validate_workflow_runtime_text(text); expressions=validate_workflow_expression_policy_text(text); commands=validate_workflow_run_commands_text(text)
result={"valid":yaml_surface["valid"] and schema["valid"] and step_env["valid"] and trigger["valid"] and exact["valid"] and not missing and workflow_name==REQUIRED_WORKFLOW_NAME and actions["valid"] and permissions["valid"] and runtime["valid"] and expressions["valid"] and commands["valid"],"required_checks":sorted(REQUIRED_GITHUB_CHECKS),"workflow_jobs":sorted(jobs),"missing_checks":missing,"workflow_name":workflow_name,"expected_workflow_name":REQUIRED_WORKFLOW_NAME,"yaml_surface":yaml_surface,"schema":schema,"step_inputs_env":step_env,"trigger_concurrency":trigger,"exact_job_steps":exact,"action_pinning":actions,"permissions":permissions,"runtime":runtime,"expressions":expressions,"run_commands":commands,"ci_trust_policy_version":CI_TRUST_POLICY_VERSION,"ci_trust_policy_digest":ci_trust_policy_digest()}
⋮----
semantic=workflow_semantic_manifest_text(text) if result["valid"] else {"valid":False,"manifest":None,"digest":None,"violations":["workflow_not_trusted"]}
⋮----
def validate_workflow(path: Path) -> dict: return validate_workflow_text(path.read_text(encoding="utf-8"))
⋮----
def _workflow_run_id_from_details(run: dict, repository: str) -> int | None
⋮----
details=run.get("details_url")
⋮----
parsed=urlparse(details)
⋮----
prefix="/"+repository+"/actions/runs/"
⋮----
token=parsed.path[len(prefix):].split("/",1)[0]
try: value=int(token)
⋮----
def _trusted_check_run(run: dict, repository: str) -> bool
⋮----
def _timestamp(value) -> float | None
⋮----
text=value[:-1]+"+00:00" if value.endswith("Z") else value; dt=datetime.fromisoformat(text)
if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
⋮----
def _check_timestamp(run: dict) -> float | None
⋮----
ts=_timestamp(run.get(key))
⋮----
def validate_check_runs(runs: list[dict], repository: str, *, commit_sha: str | None=None, head_commit_timestamp: float | None=None) -> dict
⋮----
trusted=[run for run in runs if _trusted_check_run(run,repository)]
if commit_sha is not None: trusted=[run for run in trusted if run.get("head_sha") in (None,commit_sha)]
by_name={}
⋮----
name=run.get("name")
⋮----
current=by_name.get(name); current_ts=_check_timestamp(current) if current else None; run_ts=_check_timestamp(run); current_id=int(current.get("id") or 0) if isinstance(current,dict) else -1; run_id=int(run.get("id") or 0)
⋮----
missing=sorted(REQUIRED_GITHUB_CHECKS-set(by_name)); incomplete=sorted(name for name in REQUIRED_GITHUB_CHECKS if name in by_name and by_name[name].get("status")!="completed"); failed=sorted(name for name in REQUIRED_GITHUB_CHECKS if name in by_name and by_name[name].get("status")=="completed" and by_name[name].get("conclusion")!="success")
stale=sorted(name for name in REQUIRED_GITHUB_CHECKS if name in by_name and head_commit_timestamp is not None and (_check_timestamp(by_name[name]) is None or _check_timestamp(by_name[name])<float(head_commit_timestamp)))
passed=sorted(name for name in REQUIRED_GITHUB_CHECKS if name in by_name and by_name[name].get("status")=="completed" and by_name[name].get("conclusion")=="success" and name not in stale)
evidence={name:{"id":by_name[name].get("id"),"head_sha":by_name[name].get("head_sha"),"timestamp":_check_timestamp(by_name[name]),"status":by_name[name].get("status"),"conclusion":by_name[name].get("conclusion"),"workflow_run_id":_workflow_run_id_from_details(by_name[name],repository)} for name in sorted(REQUIRED_GITHUB_CHECKS) if name in by_name}
run_ids=sorted({row.get("workflow_run_id") for row in evidence.values() if isinstance(row.get("workflow_run_id"),int)}); mixed=len(run_ids)>1 or (not missing and len(run_ids)!=1)
````

## File: replacement_ci_policy.py
````python
"""CI trust policy v12: v11 plus fail-closed checkout credential handling."""
⋮----
CI_TRUST_POLICY_VERSION=12
REQUIRED_ACTION_INPUT_VALUES={"actions/checkout":{"persist-credentials":"false"}}
ACTION_WITH_ALLOWLIST=dict(_base.ACTION_WITH_ALLOWLIST)
⋮----
def ci_trust_policy_digest() -> str
⋮----
payload={
⋮----
def _checkout_input_violations(text: str) -> list[dict]
⋮----
violations=[]
current_action=None
inputs={}
action_line=None
in_with=False
⋮----
def finish()
⋮----
value=inputs.get("persist-credentials")
⋮----
code=_base._yaml_code(line)
⋮----
current_action=None;inputs={};action_line=None;in_with=False
uses=re.match(r"^        uses:\s*([^#\s]+)",code) or re.match(r"^      -\s+uses:\s*([^#\s]+)",code)
⋮----
value=uses.group(1).strip().strip("'\"")
current_action=value.rsplit("@",1)[0] if "@" in value else value
action_line=lineno
⋮----
in_with=True
⋮----
item=re.match(r"^          ([A-Za-z0-9_-]+):\s*([^#\n]+?)\s*$",code)
⋮----
def validate_step_inputs_env_text(text: str) -> dict
⋮----
base=_base.validate_step_inputs_env_text(text)
violations=[
⋮----
def workflow_semantic_manifest_text(text: str) -> dict
⋮----
validation=validate_workflow_text(text,include_semantic=False)
⋮----
manifest={
encoded=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode("utf-8")
⋮----
def validate_workflow_text(text: str, *, include_semantic: bool=True) -> dict
⋮----
yaml_surface=validate_yaml_surface_text(text)
schema=validate_workflow_schema_text(text)
step_env=validate_step_inputs_env_text(text)
trigger=validate_trigger_concurrency_text(text)
exact=validate_exact_job_steps_text(text)
jobs=workflow_job_ids_text(text)
missing=sorted(REQUIRED_GITHUB_CHECKS-jobs)
match=re.search(r"(?m)^name:\s*([^#\n]+?)\s*$",text)
workflow_name=match.group(1).strip().strip("'\"") if match else None
actions=validate_action_pinning_text(text)
permissions=validate_workflow_permissions_text(text)
runtime=validate_workflow_runtime_text(text)
expressions=validate_workflow_expression_policy_text(text)
commands=validate_workflow_run_commands_text(text)
valid=(
result={
⋮----
semantic=workflow_semantic_manifest_text(text) if valid else {"manifest":None,"digest":None}
⋮----
def validate_workflow(path: Path) -> dict
````

## File: repo_maintenance.py
````python
"""Bounded GitHub repository maintenance probe for architecture evidence."""
⋮----
MAX_REPOS = 8
TIMEOUT_SECONDS = 4
ACTIVE_DAYS = 180
STALE_DAYS = 365
⋮----
def _epoch(value: str | None) -> float | None
⋮----
def classify(metadata: dict, *, now: float | None = None) -> dict
⋮----
now_value = time.time() if now is None else float(now)
⋮----
pushed_at = metadata.get("pushed_at")
pushed_epoch = _epoch(pushed_at)
⋮----
age_days = max(0.0, (now_value - pushed_epoch) / 86400.0)
⋮----
status = "stale"
⋮----
status = "aging"
⋮----
status = "active"
⋮----
def _fetch(repo: str, token: str | None) -> dict
⋮----
headers = {
⋮----
req = Request(f"https://api.github.com/repos/{repo}", headers=headers)
⋮----
value = json.loads(response.read().decode("utf-8"))
⋮----
result = classify(value)
⋮----
def probe(repositories: list[str], *, token: str | None = None) -> dict[str, dict]
⋮----
unique = []
seen = set()
⋮----
token = token if token is not None else os.environ.get("GITHUB_TOKEN")
results = {}
⋮----
futures = {pool.submit(_fetch, repo, token): repo for repo in unique}
⋮----
repo = futures[future]
⋮----
except Exception as exc:  # bounded evidence collection must not block pipeline
````

## File: repo_version_probe.py
````python
"""Bounded GitHub semantic-version probe for replacement context."""
⋮----
MAX_REPOS=8
TIMEOUT_SECONDS=4
SEMVER=re.compile(r"(?<!\d)v?(\d+)(?:\.\d+)?(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?")
⋮----
def _major(value)
⋮----
match=SEMVER.search(value.strip())
⋮----
def classify_release(value)
⋮----
tag=value.get("tag_name")
major=_major(tag)
⋮----
def _fetch(repo,token)
⋮----
headers={
⋮----
req=Request("https://api.github.com/repos/"+repo+"/releases/latest",headers=headers)
⋮----
value=json.loads(response.read().decode("utf-8"))
⋮----
result=classify_release(value)
⋮----
def probe(repositories,token=None)
⋮----
unique=[]
seen=set()
⋮----
token=token if token is not None else os.environ.get("GITHUB_TOKEN")
⋮----
out={}
⋮----
futures={pool.submit(_fetch,repo,token):repo for repo in unique}
⋮----
repo=futures[future]
````

## File: repository_research_provider.py
````python
"""Repository-native research providers with immutable Git provenance."""
⋮----
MAX_SOURCE_BYTES=160_000
MAX_RESULTS=8
TOKEN_RE=re.compile(r"[a-z0-9_]{3,}")
⋮----
class RepositoryResearchError(ValueError)
⋮----
def _tokens(value)
⋮----
def _trusted_files(root)
⋮----
root=Path(root).resolve()
files=[]
⋮----
base=root/dirname
⋮----
resolved=path.resolve()
⋮----
size=resolved.stat().st_size
⋮----
def build_repository_providers(repo_root, repo_full_name, commit_sha, capability)
⋮----
root=Path(repo_root).resolve()
⋮----
indexed=[]
capability_tokens=_tokens(capability)
⋮----
text=path.read_text(encoding="utf-8")
⋮----
rel=path.relative_to(root).as_posix()
haystack=(rel+"\n"+text).lower()
⋮----
prefix=f"https://github.com/{repo_full_name}/blob/{commit_sha}/"
⋮----
def search_provider(query)
⋮----
wanted=_tokens(query)|capability_tokens
scored=[]
⋮----
score=sum(haystack.count(token) for token in wanted)
⋮----
def fetch_provider(url)
⋮----
parsed=urlsplit(url)
⋮----
encoded_path=url[len(prefix):]
rel=unquote(encoded_path)
⋮----
target=(root/rel).resolve()
⋮----
raw=target.read_bytes()
````

## File: reputation_policy_check.py
````python
"""Standalone CI validator for replacement reputation policy invariants."""
⋮----
def main() -> int
⋮----
result=validate_transition_policy()
````

## File: routing_audit.py
````python
"""Bounded, credential-free audit log for provider routing decisions."""
⋮----
MAX_EVENTS = 512
⋮----
def append(path: Path, event: dict, *, now: float | None = None) -> dict
⋮----
path = Path(path)
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
value = {"schema": 1, "events": []}
⋮----
clean = {
````

## File: routing_calibration.py
````python
"""Calibrate provider/model routing from audited decisions and verified outcomes."""
⋮----
def _load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
def build(audit: dict, outcomes: list[dict]) -> dict
⋮----
successful = [o for o in outcomes if isinstance(o, dict) and isinstance(o.get("outcome"), dict)]
events = audit.get("events") if isinstance(audit, dict) else []
routes = {}
# Recent ordered attribution: each completed project outcome is matched to its
# most recent audited winner. This remains conservative when exact call IDs are absent.
winners = [
⋮----
key = event["winner"] + "::" + event["winner_model"]
row = routes.setdefault(key, {
observed = outcome["outcome"]
quality = max(0.0, min(100.0, float(observed.get("quality_score", 0.0) or 0.0)))
⋮----
n = row["samples"]
mean_quality = row.pop("quality_total") / max(1, n)
# Strong neutral prior prevents sparse outcomes from dominating routing.
posterior_quality = (mean_quality * n + 50.0 * 4.0) / (n + 4.0)
confidence = min(1.0, n / 12.0)
⋮----
def write(audit_path: Path, outcome_paths: list[Path], output_path: Path) -> dict
⋮----
audit = _load(audit_path)
outcomes = [_load(path) for path in outcome_paths]
result = build(audit, outcomes)
⋮----
def adjustment(summary: dict, provider: str, model: str) -> float
⋮----
row = (summary.get("routes") or {}).get(str(provider) + "::" + str(model)) if isinstance(summary, dict) else None
````

## File: routing_history.py
````python
"""Bounded routing-decision history and conservative weight learning."""
⋮----
MAX_EVENTS = 500
MIN_EVENTS_FOR_LEARNING = 8
MIN_WEIGHT = 0.75
MAX_WEIGHT = 1.25
DEFAULT_WEIGHTS = {
⋮----
def load(path: Path) -> list[dict]
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = []
⋮----
score = event.get("score")
⋮----
def _save(path: Path, events: list[dict]) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, *, kind: str, name: str, role: str, score: dict, success: bool, duration_seconds: float) -> list[dict]
⋮----
components = score.get("components") if isinstance(score, dict) else None
⋮----
safe_components = {}
⋮----
event = {
events = load(path)
⋮----
def learned_weights(events: list[dict], *, kind: str, role: str) -> dict[str, float]
⋮----
relevant = [e for e in events if e.get("kind") == kind and e.get("role") == role]
weights = dict(DEFAULT_WEIGHTS)
⋮----
component_names = set()
⋮----
success_values = [
failure_values = [
⋮----
success_mean = sum(success_values) / len(success_values)
failure_mean = sum(failure_values) / len(failure_values)
scale = max(1.0, max(abs(success_mean), abs(failure_mean)))
signal = max(-1.0, min(1.0, (success_mean - failure_mean) / scale))
⋮----
def weighted_total(components: dict[str, float], weights: dict[str, float]) -> float
````

## File: run_cost_controller.py
````python
"""Run-wide cost controller for bounded autonomous execution."""
⋮----
@dataclass
class RunCostController
⋮----
total_budget_seconds: float | None
max_model_calls: int
model_seconds: float = 0.0
agent_seconds: float = 0.0
verification_seconds: float = 0.0
review_seconds: float = 0.0
model_calls: int = 0
agent_calls: int = 0
verification_runs: int = 0
fallbacks: int = 0
events: list[dict] = field(default_factory=list)
⋮----
def _budget(self) -> float
⋮----
def record_model(self, duration: float, *, phase: str) -> None
⋮----
def record_agent(self, duration: float, *, fallback: bool = True) -> None
⋮----
def record_verification(self, duration: float) -> None
⋮----
def record_review(self, duration: float) -> None
⋮----
def decision(self) -> dict
⋮----
budget = self._budget()
⋮----
spent = self.model_seconds + self.agent_seconds + self.verification_seconds + self.review_seconds
⋮----
def snapshot(self) -> dict
````

## File: run.py
````python
"""GitHub brief -> bounded Flutter studio -> checkpoint branch and build artifacts."""
⋮----
class GitHub(API)
⋮----
def __init__(self, repo)
def get(self, path)
def restore(self, branch, root)
⋮----
metadata = self.get('')
⋮----
refs = self.get('/git/matching-refs/heads/' + branch)
⋮----
initial = self.call('PUT', self.repo + '/contents/README.md', {
⋮----
exact = [r for r in refs if r['ref'] == 'refs/heads/' + branch]
⋮----
default = metadata['default_branch']
branch_info = self.get('/branches/' + default)
parent = branch_info['commit']['sha']
tree = self.get('/git/trees/' + parent + '?recursive=1')
⋮----
paths = {x['path'] for x in tree['tree'] if x.get('type') == 'blob'}
bootstrap_only = paths <= {'README.md', 'LICENSE', '.gitignore'}
existing_flutter = 'pubspec.yaml' in paths and any(
⋮----
# Import only the trusted editable Flutter source surface. The default
# branch remains the base tree, so unrelated/native files are preserved
# on the studio branch rather than deleted.
⋮----
path = item.get('path')
⋮----
blob = self.get('/git/blobs/' + item['sha'])
content = base64.b64decode(blob['content']).decode()
⋮----
parent = exact[0]['object']['sha']
⋮----
state = None
⋮----
path = item['path']
⋮----
state = json.loads(content)
⋮----
def publish(self, branch, parent, root, state)
⋮----
state_json = json.dumps(state, sort_keys=True, ensure_ascii=False,
⋮----
entries = []
previous = {}
⋮----
previous = {x['path']: x.get('sha') for x in self.get('/git/trees/' + parent + '?recursive=1')['tree']}
candidates = {}
⋮----
rel = p.relative_to(root).as_posix()
⋮----
sha = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
⋮----
entry = {'path': rel, 'mode': '100755' if rel == 'android/gradlew' else '100644', 'type': 'blob'}
⋮----
blob = self.call('POST', self.repo + '/git/blobs', {'encoding': 'base64', 'content': base64.b64encode(content).decode()})
⋮----
data = {'tree': entries}
⋮----
tree = self.call('POST', self.repo + '/git/trees', data)
commit = self.call('POST', self.repo + '/git/commits', {'message': 'Mobile studio: ' + state['status'], 'tree': tree['sha'], 'parents': [parent] if parent else []})
⋮----
exists = any(r['ref'] == 'refs/heads/' + branch for r in refs)
⋮----
def _load_architecture_replacement_work_orders(out: Path) -> dict
⋮----
path = Path(out) / 'architecture-replacement-work-orders.json'
⋮----
value = json.loads(path.read_text(encoding='utf-8'))
⋮----
work_orders = []
⋮----
def _load_architecture_replacement_plan(out: Path) -> dict
⋮----
path = Path(out) / 'architecture-replacement-plan.json'
⋮----
plans = []
⋮----
def _load_architecture_obsolescence(out: Path) -> dict
⋮----
path = Path(out) / 'architecture-obsolescence.json'
⋮----
candidates = []
⋮----
def _load_architecture_benchmark(out: Path) -> dict
⋮----
path = Path(out) / 'architecture-benchmark.json'
⋮----
def _load_star_recommendations(out: Path) -> dict
⋮----
"""Load bounded recommendation evidence as advisory data only."""
path = Path(out) / 'star-recommendations.json'
⋮----
safe = []
⋮----
def context(req, state, root)
⋮----
files = {p.relative_to(root).as_posix(): p.read_text() for p in sorted(root.rglob('*'))
⋮----
def execute(req, root, out, github=None, model_factory=Model, sandbox_factory=Sandbox)
⋮----
def clear_preview_evidence(state)
⋮----
req = request_check(req)
⋮----
github = github or GitHub(req['target_repo'])
branch = 'studio/' + req['id']
⋮----
saved_root = Path(saved)
⋮----
fingerprint = hashlib.sha256(canonical({k: v for k, v in req.items() if k != 'enabled'}).encode()).hexdigest()
⋮----
state = state or {'request_hash': fingerprint, 'status': 'pending', 'cycles': 0, 'rounds': 0, 'blockers': []}
⋮----
autonomy_dir = out / '.autonomy'
⋮----
preliminary_capacity_plan = expanded_call_limit(
capacity_multiplier = float(preliminary_capacity_plan.get('multiplier', 1.0) or 1.0)
effective_max_cycles = (
⋮----
max_api_cost = req.get('max_api_cost_usd')
⋮----
capacity_plan = expanded_call_limit(
⋮----
cycle_budget = min(
⋮----
model = model_factory(cycle_budget)
sandbox = sandbox_factory(root)
⋮----
rel = p.relative_to(saved_root).as_posix()
⋮----
# Trusted derived handoff: regenerated at the next checkpoint,
# never reintroduced through the model-editable patch channel.
⋮----
safe_rewrite_learning_path = out / '.autonomy' / 'safe-rewrite-learning.json'
local_model_reputation_path = out / '.autonomy' / 'local-model-reputation.json'
local_model_specialization_path = out / '.autonomy' / 'local-model-specialization.json'
model_portfolio_learning_path = out / '.autonomy' / 'model-portfolio-learning.json'
⋮----
def current_flutter_contexts()
⋮----
contexts = list(weighted_task_contexts(
architecture_risk = (
⋮----
phase_context = (
⋮----
total = sum(max(0.0, float(weight)) for _, weight in contexts)
⋮----
def record_verified_implementation(success)
⋮----
provider_name = str(
model_name = str(
⋮----
gateway_name = provider_name.split(':', 1)[0]
⋮----
historical_root = architecture_learning_root(out)
historical_learning = summarize_architecture_learning(historical_root)
replacement_learning = summarize_replacement_learning(historical_root)
replacement_reputation = load_replacement_reputation(
⋮----
flutter_contexts = current_flutter_contexts()
⋮----
def checkpoint(parent_sha)
⋮----
result = checkpointed_ask(model, role, context(req, state, root), namespace='preview-' + role)
⋮----
parent = checkpoint(parent)
⋮----
implementation_context = context(req, state, root)
patch = checkpointed_ask(model, 'implementation', implementation_context, namespace='preview-implementation')
⋮----
origin_identity = str(
event = {
⋮----
rewrite_context = build_architecture_safe_rewrite_context(
retry_patch = checkpointed_ask(
⋮----
patch = retry_patch
⋮----
event_id = f"{req['id']}:{state['rounds']}:flutter"
origin_name = origin_identity
rewrite_name = str(
⋮----
qa_patch = checkpointed_ask(model, 'tests', context(req, state, root), namespace='preview-tests')
⋮----
journeys = validate_journeys(state['product'].get('journeys'))
⋮----
pending_safe_rewrite = state.pop('pending_safe_rewrite_event_id', None)
⋮----
review = verdict(checkpointed_ask(model, 'review', context(req, state, root), namespace='preview-review'))
⋮----
screenshots = sorted((root / 'test/goldens').glob('*.png'))
⋮----
visual = {'passed': True, 'blockers': []}
⋮----
batch = [p for p in screenshots if p.name.startswith(screen + '--')]
⋮----
result = verdict(checkpointed_ask(model, 'visual', canonical({'brief': req['brief'], 'design': state['design'],
⋮----
effective_model_calls = max(0, int(model.calls) - int(getattr(model, 'checkpoint_replays', 0)))
⋮----
selected_portfolio = {
⋮----
specialization_state = load_local_model_specialization(local_model_specialization_path)
⋮----
apk = root / 'build/app/outputs/flutter-apk/app-debug.apk'
⋮----
learning_root = architecture_learning_root(out)
⋮----
sha = checkpoint(parent)
⋮----
def main()
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
⋮----
provider = os.environ.get('STUDIO_CI_PROVIDER')
⋮----
state = execute(json.loads(Path(args.request).read_text()), Path(args.work), Path(args.out))
````

## File: runtime_health.py
````python
"""Machine-readable health report for one persistent autonomous project."""
⋮----
def _lease_summary(path: Path) -> dict
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
claims = data.get("claims")
⋮----
def inspect(project_out: Path | str) -> dict
⋮----
project_out = Path(project_out)
root = project_out / ".autonomy"
⋮----
paths = {
⋮----
errors = []
runtime = {}
⋮----
runtime = load_recovering(paths["runtime_state"])
⋮----
checkpoints = load_checkpoints(paths["checkpoints"])
⋮----
checkpoints = {}
⋮----
leases = _lease_summary(paths["leases"])
⋮----
telemetry = telemetry_summary(paths["telemetry"])
⋮----
status = "healthy" if not errors else "degraded"
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="Inspect one autonomous project runtime")
⋮----
args = parser.parse_args(argv)
report = inspect(args.project_out)
````

## File: runtime_journeys.py
````python
"""Generate and execute immutable product journeys on an Android target device."""
⋮----
TEST_PATH = Path('integration_test/__studio_runtime_journeys_test.dart')
⋮----
def package_name(root: Path) -> str
⋮----
pubspec = root / 'pubspec.yaml'
⋮----
match = re.search(r'^name:\s*([a-z][a-z0-9_]*)\s*$', pubspec.read_text(), re.MULTILINE)
⋮----
def render_test(package: str, journeys: list[dict]) -> str
⋮----
payload = base64.b64encode(json.dumps(journeys, ensure_ascii=False).encode()).decode()
⋮----
journeys = validate_journeys(journeys)
package = package_name(root)
⋮----
lock = root / 'pubspec.lock'
original_pubspec = pubspec.read_bytes()
original_lock = lock.read_bytes() if lock.is_file() else None
test_file = root / TEST_PATH
⋮----
logs: list[dict] = []
⋮----
commands = [
⋮----
result = runner(args, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
⋮----
encoded = json.dumps(journeys, sort_keys=True, separators=(',', ':')).encode()
````

## File: safe_rewrite_learning.py
````python
"""Persistent learning for architecture-safe rewrite recovery."""
⋮----
MAX_EVENTS = 500
MIN_SAMPLES = 5
MAX_PENALTY = 0.25
DECAY_HALF_LIFE_EVENTS = 20.0
MIN_EVENT_WEIGHT = 0.05
RECENT_WINDOW = 8
EXPLORATION_STALE_EVENTS = 20
MAX_EXPLORATION_BONUS = 5.0
⋮----
def _decay_weight(age: int) -> float
⋮----
age = max(0, int(age))
weight = 0.5 ** (age / DECAY_HALF_LIFE_EVENTS)
⋮----
def _weighted_rate(rows: list[tuple[dict, float]], field: str) -> float
⋮----
total = sum(weight for _, weight in rows)
⋮----
def _recent_success_streak(events: list[dict], field: str) -> int
⋮----
streak = 0
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
events = value.get("events")
⋮----
events = []
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
data = load(path)
event = {
⋮----
target = None
⋮----
target = dict(event)
⋮----
def summarize(path: Path) -> dict
⋮----
events = load(path)["events"]
completed = [e for e in events if e.get("completed") is True]
newest_index = max(0, len(completed) - 1)
⋮----
def rows(kind_key: str, name_key: str) -> list[dict]
⋮----
grouped = {}
⋮----
name = event.get(name_key)
kind = event.get(kind_key)
⋮----
key = (str(kind or "unknown"), name)
row = grouped.setdefault(key, {
⋮----
weight = _decay_weight(newest_index - index)
⋮----
result = []
⋮----
n = max(1, row["samples"])
⋮----
weighted = row.pop("_weighted_events")
raw_events = row.pop("_events")
last_index = row.pop("_last_index")
⋮----
def origin_violation_penalty(summary: dict, *, kind: str, name: str, role: str) -> float
⋮----
"""Bounded score-point penalty for repeatedly triggering architecture-safe recovery."""
fraction = routing_penalty(summary, kind=kind, name=name, role=role)
⋮----
def rewrite_recovery_bonus(summary: dict, *, kind: str, name: str, role: str) -> float
⋮----
"""Conservative bonus for models/providers that repeatedly recover rejected patches."""
⋮----
rows = summary.get("rewrite_rankings")
⋮----
samples = row.get("samples")
⋮----
verify_rate = float(row.get("decayed_verification_pass_rate", row.get("verification_pass_rate", 0.0)))
review_rate = float(row.get("decayed_review_pass_rate", row.get("review_pass_rate", 0.0)))
quality = min(verify_rate, review_rate if row.get("review_passes", 0) else verify_rate)
⋮----
# Smaller than the maximum violation penalty: recovery skill must not
# make architecture violations strategically desirable.
⋮----
def exploration_bonus(summary: dict, *, kind: str, name: str, role: str) -> float
⋮----
rows = summary.get("origin_rankings")
⋮----
stale = int(row.get("events_since_last_observation", 0) or 0)
⋮----
excess = stale - EXPLORATION_STALE_EVENTS
⋮----
def routing_penalty(summary: dict, *, kind: str, name: str, role: str) -> float
⋮----
verify_rate = min(1.0, verify_rate + 0.15)
# Penalize only repeatedly poor origins; never reward architecture violations.
⋮----
severity = min(1.0, (0.6 - verify_rate) / 0.6)
effective_weight = row.get("effective_sample_weight")
⋮----
freshness = max(0.1, min(1.0, float(effective_weight) / float(samples)))
⋮----
freshness = 1.0
````

## File: security_agent.py
````python
"""Bounded model-assisted remediation for technical security findings."""
⋮----
MAX_AGENTIC_ROUNDS = 2
AGENTIC_BLOCKERS = {
⋮----
def eligible_blockers(evidence: dict) -> list[str]
⋮----
blockers = set(evidence.get("blockers", []))
⋮----
def _context(root: Path, state: dict, blockers: list[str]) -> str
⋮----
files = {}
⋮----
rel = path.relative_to(root).as_posix()
⋮----
text = path.read_text(errors="replace")
⋮----
blockers = eligible_blockers(evidence)
⋮----
model = model_factory(4)
patch = model.ask("security_fix", _context(root, state, blockers))
files = patch_check(patch)
snapshot = {}
⋮----
path = root / item["path"]
⋮----
journeys = validate_journeys(state.get("product", {}).get("journeys"))
sandbox = sandbox_factory(root)
⋮----
path = root / rel
````

## File: security_audit.py
````python
"""Trusted static security, dependency and provenance audit for generated apps."""
⋮----
SECRET_PATTERNS = {
DANGEROUS_PERMISSIONS = {
SENSITIVE_PERMISSIONS = {
CLEAR_TEXT = re.compile(r'http://(?!schemas\.android\.com/)[^\s\"\'<>]+', re.I)
⋮----
TRUSTED_HOSTED_REGISTRIES = {'https://pub.dev'}
STRONG_COPYLEFT = {'GPL-2.0', 'GPL-3.0', 'AGPL-3.0'}
WEAK_COPYLEFT = {'LGPL-2.1', 'LGPL-3.0', 'MPL-2.0'}
PERMISSIVE_LICENSES = {'MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'Apache-2.0', 'ISC', 'Zlib'}
⋮----
HUMAN_REVIEW_BLOCKER_PREFIXES = (
HUMAN_REVIEW_BLOCKERS = {
⋮----
def human_review_reasons(blockers: list[str]) -> list[str]
⋮----
"""Return blockers that require an explicit trust/legal decision by a person."""
⋮----
def _candidate_files(root: Path) -> list[Path]
⋮----
files = []
⋮----
base = root / rel
⋮----
path = root / rel
⋮----
def _text_files(root: Path)
⋮----
def android_permissions(root: Path) -> list[str]
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
def dependency_inventory(root: Path) -> list[dict]
⋮----
lock = root / 'pubspec.lock'
⋮----
packages = []
current = None
in_description = False
⋮----
match = re.match(r'^  ([A-Za-z_][A-Za-z0-9_-]*):\s*$', raw)
⋮----
current = {
⋮----
dependency = re.match(r'^    dependency:\s*([^\s]+(?:\s+[^\s]+)?)\s*$', raw)
version = re.match(r'^    version:\s*["\']?([^"\']+)["\']?\s*$', raw)
source = re.match(r'^    source:\s*([^\s]+)\s*$', raw)
⋮----
in_description = True
⋮----
sha = re.match(r'^      sha256:\s*["\']?([0-9a-fA-F]{64})["\']?\s*$', raw)
url = re.match(r'^      url:\s*["\']?([^"\']+)["\']?\s*$', raw)
⋮----
def _license_text(root: Path, dep: dict) -> str | None
⋮----
name = dep.get('name')
version = dep.get('version')
⋮----
cache = root / '.studio-cache/pub/hosted/pub.dev' / f'{name}-{version}'
⋮----
path = cache / filename
⋮----
def _license_id(text: str | None) -> str
⋮----
lower = re.sub(r'\s+', ' ', text.lower())
⋮----
def dependency_license_inventory(root: Path, dependencies: list[dict]) -> list[dict]
⋮----
result = []
⋮----
license_id = 'SDK' if dep.get('source') == 'sdk' else _license_id(_license_text(root, dep))
status = (
⋮----
def dependency_risks(root: Path, dependencies: list[dict], licenses: list[dict] | None = None) -> list[str]
⋮----
pubspec = (root / 'pubspec.yaml').read_text(errors='replace') if (root / 'pubspec.yaml').is_file() else ''
blockers = []
⋮----
source = dep.get('source')
⋮----
registry = dep.get('registry')
⋮----
def scan(root: Path) -> dict
⋮----
secrets = []
cleartext_endpoints = []
debug_flags = []
executable_markers = []
⋮----
rel = path.relative_to(root).as_posix()
⋮----
permissions = android_permissions(root)
dangerous = sorted(p for p in permissions if p in DANGEROUS_PERMISSIONS)
sensitive = sorted(p for p in permissions if p in SENSITIVE_PERMISSIONS)
dependencies = dependency_inventory(root)
dependency_licenses = dependency_license_inventory(root, dependencies)
dep_risks = dependency_risks(root, dependencies, dependency_licenses)
⋮----
def sbom(root: Path, audit: dict) -> dict
⋮----
components = []
licenses = {item['name']: item for item in audit.get('dependency_licenses', [])}
⋮----
license_info = licenses.get(dep['name'], {})
⋮----
pubspec = root / 'pubspec.yaml'
app_hash = hashlib.sha256(pubspec.read_bytes()).hexdigest() if pubspec.is_file() else None
⋮----
def build_security_package(root: Path, out: Path) -> dict
⋮----
audit = scan(root)
bom = sbom(root, audit)
folder = out / 'security'
⋮----
audit_path = folder / 'audit.json'
sbom_path = folder / 'sbom.json'
⋮----
review_reasons = human_review_reasons(audit['blockers'])
````

## File: security_remediation.py
````python
"""Bounded deterministic remediation for security findings.

Only transformations that are semantics-preserving for a release build are
performed here. Findings that need product/security judgement remain blockers.
"""
⋮----
MAX_REMEDIATION_ROUNDS = 2
⋮----
def _android_manifest(root: Path) -> Path
⋮----
def remediate(root: Path, evidence: dict) -> dict
⋮----
blockers = set(evidence.get("blockers", []))
actions: list[dict] = []
changed = False
⋮----
manifest = _android_manifest(root)
⋮----
original = manifest.read_text(errors="strict")
updated = original
⋮----
changed = True
⋮----
def remediation_candidate(evidence: dict) -> bool
````

## File: security_stage.py
````python
"""Persist trusted security/SBOM evidence and close the completion contract."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
remediation_history = []
source_changed = False
evidence = build_security_package(root, out)
⋮----
blockers_before = len(evidence.get('blockers', []))
result = remediate(root, evidence)
⋮----
source_changed = True
⋮----
agentic_history = []
⋮----
result = agentic_attempt(root, state, evidence, req['app_name'])
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('security_scan')
````

## File: smoke.py
````python
"""Real Docker/Flutter smoke test with a deterministic app; no model or GitHub secrets."""
⋮----
root=Path(os.environ.get('STUDIO_SMOKE_ROOT','/tmp/studio-smoke')); root.mkdir(parents=True,exist_ok=False); sandbox=Sandbox(root); sandbox.create('smoke_app')
````

## File: stage_registry.py
````python
"""Trusted stage registry for bounded autonomous mobile completion."""
⋮----
@dataclass(frozen=True)
class Stage
⋮----
name: str
script: str
deferred_status: str
failed_status: str
⋮----
STAGES = {
⋮----
PROMOTED_REGISTRY = Path(__file__).resolve().parents[1] / 'control' / 'promoted_stages.json'
⋮----
def _promoted_stage(name: str) -> Stage | None
⋮----
value = json.loads(PROMOTED_REGISTRY.read_text())
⋮----
entry = value['stages'].get(name)
⋮----
expected_script = f"studio/{name[:-3]}_stage.py"
⋮----
def get_stage(name: str) -> Stage | None
````

## File: stagnation_controller.py
````python
"""Conservative stagnation control for token-burning autonomous projects."""
⋮----
@dataclass(frozen=True)
class StagnationDecision
⋮----
level: str
capacity_multiplier: float
force_diversify: bool
pause: bool
reason: str
⋮----
def as_dict(self) -> dict
⋮----
def decide(project_rows: list[dict]) -> StagnationDecision
⋮----
mature = [
⋮----
max_failure_streak = max(
total_samples = sum(max(0, int(row.get("samples", 0) or 0)) for row in mature)
recent_success = max(
⋮----
def summarize(efficiency_summary: dict) -> dict
⋮----
rows = efficiency_summary.get("rows") if isinstance(efficiency_summary, dict) else None
⋮----
rows = []
grouped = {}
⋮----
project = str(row.get("project_id") or "").strip()
⋮----
projects = {
````

## File: star_scanner.py
````python
"""Query the structured star-list catalog and rank repositories for a project need."""
⋮----
DEFAULT_SOURCE = "https://raw.githubusercontent.com/dbrckk/star-list/main/catalog.json"
FALLBACK_SOURCE = "https://raw.githubusercontent.com/dbrckk/star-list/main/text/star-list.md"
⋮----
_TIER_BONUS = {"core": 1.0, "recommended": 0.6, "specialized": 0.25, "audit": -0.4}
⋮----
def _read_source(source: str) -> str
⋮----
local = Path(source)
⋮----
req = Request(source, headers={"User-Agent": "ai-dev-server"})
⋮----
def _tokens(value: str) -> set[str]
⋮----
def parse_catalog(text: str) -> list[dict]
⋮----
value = json.loads(text)
rows = value.get("repositories")
⋮----
out = []
⋮----
def parse_repositories(text: str) -> list[str]
⋮----
repo = match.group(1)
⋮----
wanted = _tokens(" ".join(needs))
required = {x.lower() for x in (capabilities or [])}
ranked = []
⋮----
caps = set(row.get("capabilities", [])) | set(row.get("roles", []))
⋮----
text = " ".join([
rtoks = _tokens(text)
lexical = len(wanted & rtoks) / max(1, len(wanted))
quality = float(row.get("score", 0.0)) / 10.0
tier = _TIER_BONUS.get(row.get("tier"), 0.0)
best = _tokens(" ".join(row.get("bestFor", [])))
best_match = len(wanted & best) / max(1, len(wanted)) if best else 0.0
score = 55 * lexical + 15 * best_match + 20 * quality + 10 * max(0.0, tier)
⋮----
avoid = _tokens(" ".join(row.get("avoidWhen", [])))
⋮----
def rank_repositories(repositories: list[str], needs: list[str]) -> list[dict]
⋮----
rows = []
⋮----
rtoks = _tokens(repo)
matched = sorted(wanted & rtoks)
⋮----
def scan(needs: list[str], source: str = DEFAULT_SOURCE, **constraints) -> dict
⋮----
text = _read_source(source)
rows = parse_catalog(text)
matches = _catalog_rank(rows, needs, **constraints)
⋮----
fallback = FALLBACK_SOURCE if source == DEFAULT_SOURCE else source
text = _read_source(fallback)
repos = parse_repositories(text)
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
````

## File: store_package.py
````python
"""Build verifiable Google Play listing assets from validated app evidence."""
⋮----
CATEGORIES = {
SENSITIVE_PERMISSIONS = {
⋮----
def validate_store_listing(value: dict) -> dict
⋮----
required = {'title', 'short_description', 'full_description', 'category'}
⋮----
limits = [('title', 1, 30), ('short_description', 10, 80), ('full_description', 80, 4000)]
⋮----
text = value.get(key)
⋮----
def _sentence(text: str, limit: int) -> str
⋮----
clean = re.sub(r'\s+', ' ', text).strip()
⋮----
first = re.split(r'(?<=[.!?])\s+', clean)[0]
⋮----
cut = first[:limit - 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
⋮----
def _category(text: str) -> str
⋮----
tokens = set(re.findall(r'[a-z0-9]+', text.lower()))
rules = [
⋮----
def listing_from_state(req: dict, state: dict) -> dict
⋮----
title = re.sub(r'[_-]+', ' ', req['app_name']).strip().title()[:30] or 'Mobile App'
brief = re.sub(r'\s+', ' ', req.get('brief', '')).strip()
short = _sentence(brief, 80)
⋮----
short = f'{title} helps you complete the app’s core workflow simply and reliably.'[:80]
⋮----
product = state.get('product', {})
features: list[str] = []
⋮----
intro = _sentence(brief, 360)
body = [intro or f'{title} is designed around a focused, reliable mobile experience.']
⋮----
journeys = product.get('journeys', []) if isinstance(product, dict) else []
⋮----
full = '\n\n'.join(body)
⋮----
full = full[:4000].rstrip()
⋮----
def permissions(root: Path) -> list[str]
⋮----
manifest = root / 'android/app/src/main/AndroidManifest.xml'
⋮----
def _chunk(kind: bytes, payload: bytes) -> bytes
⋮----
def encode_rgba(width: int, height: int, pixels: bytes) -> bytes
⋮----
raw = b''.join(b'\x00' + pixels[y * width * 4:(y + 1) * width * 4] for y in range(height))
⋮----
def decode_png(path: Path) -> tuple[int, int, bytes]
⋮----
raw = path.read_bytes()
⋮----
size = struct.unpack('>I', raw[pos:pos + 4])[0]
kind = raw[pos + 4:pos + 8]
data = raw[pos + 8:pos + 8 + size]
⋮----
channels = 4 if ctype == 6 else 3
inflated = zlib.decompress(bytes(compressed))
stride = width * channels
⋮----
previous = bytearray(stride)
rgba = bytearray()
index = 0
⋮----
filter_type = inflated[index]
scan = bytearray(inflated[index + 1:index + 1 + stride])
⋮----
left = scan[x - channels] if x >= channels else 0
up = previous[x]
upper_left = previous[x - channels] if x >= channels else 0
⋮----
p = left + up - upper_left
⋮----
predictor = left if pa <= pb and pa <= pc else up if pb <= pc else upper_left
⋮----
previous = scan
⋮----
def store_screenshot(source: Path, destination: Path) -> dict
⋮----
target_w = math.ceil(height / 2)
⋮----
target_h = math.ceil(width / 2)
⋮----
bg = pixels[:4]
canvas = bytearray(bg * (target_w * target_h))
⋮----
src = y * width * 4
dst = ((y + oy) * target_w + ox) * 4
⋮----
pixels = bytes(canvas)
⋮----
def _colors(design: object) -> tuple[tuple[int, int, int], tuple[int, int, int]]
⋮----
text = json.dumps(design, ensure_ascii=False)
found = re.findall(r'#[0-9a-fA-F]{6}\b', text)
values = []
⋮----
rgb = tuple(int(item[i:i + 2], 16) for i in (1, 3, 5))
⋮----
def _brand_image(width: int, height: int, design: object, feature: bool) -> bytes
⋮----
pixels = bytearray(width * height * 4)
⋮----
radius = min(width, height) * (0.33 if feature else 0.28)
⋮----
t = y / max(1, height - 1)
base = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))
⋮----
dist = (dx * dx + dy * dy) ** 0.5
glow = max(0.0, 1.0 - dist / radius)
rgb = tuple(min(255, round(base[i] + glow * (255 - base[i]) * 0.72)) for i in range(3))
pos = (y * width + x) * 4
⋮----
def build_store_package(root: Path, out: Path, state: dict, listing: dict) -> dict
⋮----
listing = validate_store_listing(dict(listing))
store = out / 'play-store'
shots = store / 'screenshots' / 'phone'
⋮----
candidates = sorted(p for p in out.glob('*--compact-light.png') if p.is_file())
⋮----
digest = hashlib.sha256(source.read_bytes()).hexdigest()
⋮----
screenshot_evidence = []
⋮----
icon = store / 'icon-512.png'
feature = store / 'feature-graphic-1024x500.png'
⋮----
perms = permissions(root)
manifest = {
listing_dir = store / 'listing' / 'en-US'
⋮----
manifest_path = store / 'manifest.json'
````

## File: store_stage.py
````python
"""Create and checkpoint the autonomous Play Store metadata package."""
⋮----
def advance(request_path: Path, root: Path, out: Path) -> dict
⋮----
req = json.loads(request_path.read_text())
report_path = out / 'report.json'
⋮----
state = json.loads(report_path.read_text())
⋮----
listing = listing_from_state(req, state)
evidence = build_store_package(root, out, state, listing)
⋮----
evidence = {'passed': False, 'blockers': [str(e)]}
⋮----
parent = state.get('checkpoint_commit')
⋮----
github = GitHub(req['target_repo'])
sha = github.publish('studio/' + req['id'], parent, root, state)
⋮----
def main() -> int
⋮----
parser = argparse.ArgumentParser()
⋮----
args = parser.parse_args()
state = advance(Path(args.request), Path(args.work), Path(args.out))
evidence = state.get('release_evidence', {}).get('store_metadata')
````

## File: strategy_efficiency.py
````python
"""Verified-success efficiency memory for execution strategies."""
⋮----
ALPHA = 0.25
SUCCESS_ALPHA = 0.25
MAX_STRATEGIES = 8
MIN_SAMPLES = 4
VALID_STRATEGIES = {
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
samples = max(0, int(row.get("samples", 0)))
successes = max(0, int(row.get("successes", 0)))
successes = min(successes, samples)
ema_cost = max(0.0, float(row.get("ema_cost_seconds", 0.0)))
fallback_rate = (successes / samples) if samples else 0.0
ema_success = float(row.get("ema_success_rate", fallback_rate))
ema_success = max(0.0, min(1.0, ema_success))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, strategy: str, *, success: bool, cost_seconds: float) -> dict
⋮----
data = load(path)
row = data.get(strategy, {
samples = int(row["samples"])
cost = max(0.0, float(cost_seconds))
previous = float(row["ema_cost_seconds"])
ema = cost if samples == 0 else (ALPHA * cost + (1.0 - ALPHA) * previous)
observed_success = 1.0 if success else 0.0
previous_success = float(
ema_success = (
⋮----
def metrics(data: dict, strategy: str) -> dict | None
⋮----
row = data.get(strategy)
⋮----
successes = int(row["successes"])
cumulative_success_rate = successes / samples if samples else 0.0
recent_success_rate = max(
# Blend long-term evidence with recent behavior. Recent performance gets
# more weight so regime changes are detected without discarding history.
success_rate = 0.4 * cumulative_success_rate + 0.6 * recent_success_rate
cost = max(1.0, float(row.get("ema_cost_seconds", 0.0)))
⋮----
# Conservative uncertainty combines finite-sample risk with regime-shift
# disagreement. It is intentionally bounded so low-data strategies are
# penalized but never permanently excluded from exploration.
finite_sample = 0.5 / max(1.0, samples ** 0.5)
binomial = (
regime_gap = abs(recent_success_rate - cumulative_success_rate) * 0.5
uncertainty = min(0.5, finite_sample + binomial + regime_gap)
conservative_success = max(0.0, success_rate - 0.5 * uncertainty)
⋮----
# Scale to verified successes per 100 seconds for readable values.
efficiency = success_rate * 100.0 / cost
risk_adjusted_efficiency = conservative_success * 100.0 / cost
optimistic_efficiency = min(1.0, success_rate + uncertainty) * 100.0 / cost
⋮----
def best_strategy(data: dict, *, allowed: set[str] | None = None) -> tuple[str, dict] | None
⋮----
candidates = []
⋮----
info = metrics(data, strategy)
⋮----
EXPLORATION_EVERY = 6
MIN_EXPLORATION_EVERY = 4
MAX_EXPLORATION_EVERY = 12
⋮----
def exploration_cadence(data: dict, *, allowed: set[str] | None = None) -> int
⋮----
"""Return a deterministic exploration interval from evidence strength.

    Close strategies or shallow evidence explore more often. A durable,
    materially superior winner explores less often, but never less frequently
    than MAX_EXPLORATION_EVERY.
    """
allowed_set = set(VALID_STRATEGIES if allowed is None else allowed) & VALID_STRATEGIES
mature = []
⋮----
# A material recent-vs-cumulative gap indicates a regime change. Increase
# exploration immediately rather than waiting for long-term averages.
⋮----
winner = mature[0][1]
winner_samples = int(winner["samples"])
⋮----
runner_up = mature[1][1]
best_eff = float(winner["efficiency"])
second_eff = float(runner_up["efficiency"])
relative_gap = 0.0 if best_eff <= 0 else max(0.0, (best_eff - second_eff) / best_eff)
evidence = min(winner_samples, int(runner_up["samples"]))
⋮----
"""Deterministic bounded explore/exploit policy.

    Exploit the best mature strategy most of the time. Every Nth observed
    decision, explore the least-sampled allowed alternative so stale winners
    can be challenged without introducing randomness.
    """
⋮----
allowed_set = set(VALID_STRATEGIES if allowed is None else allowed)
⋮----
exploit = best_strategy(data, allowed=allowed_set)
⋮----
cadence = exploration_cadence(data, allowed=allowed_set) if exploration_every is None else exploration_every
total_samples = sum(
⋮----
exploit_name = exploit[0]
alternatives = [name for name in allowed_set if name != exploit_name]
⋮----
def exploration_key(name: str)
⋮----
row = data.get(name)
samples = max(0, int(row.get("samples", 0))) if isinstance(row, dict) else 0
info = metrics(data, name)
optimistic = float(info["optimistic_efficiency"]) if info is not None else 0.0
⋮----
selected = alternatives[0]
selected_metrics = metrics(data, selected)
info = dict(selected_metrics or {
⋮----
info = dict(exploit[1])
````

## File: strict_task_claim_store.py
````python
"""Fail-closed cross-process task claim registry."""
⋮----
SCHEMA = 1
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_TASK_LEASE_PATH", "").strip()
⋮----
def _read_locked(path: Path) -> dict
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
claims = data.get("claims")
⋮----
def claim(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None
⋮----
path = _path()
⋮----
now_value = time.time() if now is None else float(now)
⋮----
claims = _read_locked(path)
current = claims.get(task_id)
⋮----
current_owner = current.get("owner")
current_token = current.get("token")
current_expires = current.get("expires_at")
⋮----
def heartbeat(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None
⋮----
def release(task_id: str, owner: str | None = None, token: str | None = None) -> None
````

## File: task_claim_store.py
````python
"""Cross-process task claim registry backed by a locked JSON file."""
⋮----
SCHEMA = 1
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_TASK_LEASE_PATH", "").strip()
⋮----
def _read(path: Path) -> dict
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
claims = data.get("claims")
⋮----
def claim(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None
⋮----
path = _path()
⋮----
now_value = time.time() if now is None else float(now)
⋮----
claims = _read(path)
current = claims.get(task_id)
⋮----
current_owner = current.get("owner")
current_token = current.get("token")
current_expires = current.get("expires_at")
⋮----
def heartbeat(task_id: str, owner: str, token: str, expires_at: float, *, now: float | None = None) -> None
⋮----
def release(task_id: str, owner: str | None = None, token: str | None = None) -> None
````

## File: task_context.py
````python
"""Deterministic task-context classification for strategy routing."""
⋮----
VALID_CONTEXTS = {
⋮----
def classify(brief: str, toolchain: dict | None = None) -> str
⋮----
text = (brief or "").lower()
stacks = set(toolchain.get("stacks", [])) if isinstance(toolchain, dict) else set()
⋮----
rules = (
⋮----
def hierarchy(brief: str, toolchain: dict | None = None) -> list[str]
⋮----
primary = classify(brief, toolchain)
stacks = []
⋮----
stacks = sorted({str(x).strip().lower() for x in toolchain["stacks"] if str(x).strip()})
contexts = [primary]
⋮----
result = []
⋮----
def weighted_contexts(brief: str, toolchain: dict | None = None) -> list[tuple[str, float]]
⋮----
"""Return deterministic multi-label task contexts with normalized weights."""
⋮----
scores = {}
⋮----
hits = sum(1 for keyword in keywords if keyword in text)
⋮----
total = sum(scores.values())
⋮----
ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
````

## File: task_lease.py
````python
"""Worker lease primitives for resumable repair tasks."""
⋮----
DEFAULT_LEASE_SECONDS = 60 * 60
MIN_LEASE_SECONDS = 30
MAX_LEASE_SECONDS = 60 * 60
⋮----
def _validate_persisted_lease_state() -> None
⋮----
raw = os.environ.get("STUDIO_TASK_LEASE_PATH", "").strip()
⋮----
path = Path(raw)
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
def worker_id() -> str
⋮----
configured = os.environ.get("STUDIO_WORKER_ID", "").strip()
⋮----
run_id = os.environ.get("STUDIO_RUN_ID", "").strip()
⋮----
def _now(value: float | None = None) -> float
⋮----
def _duration(value: int | float | None) -> int
⋮----
def active(task: dict, *, now: float | None = None) -> bool
⋮----
owner = task.get("lease_owner")
expires = task.get("lease_expires_at")
⋮----
def expired(task: dict, *, now: float | None = None) -> bool
⋮----
now_value = _now(now)
owner = (owner or worker_id()).strip()
⋮----
current_owner = task.get("lease_owner")
⋮----
duration = _duration(lease_seconds)
token = uuid.uuid4().hex
⋮----
task_id = task.get("id")
⋮----
def release(task: dict, *, owner: str | None = None, token: str | None = None) -> dict
⋮----
current_token = task.get("lease_token")
⋮----
def recover(task: dict, *, now: float | None = None) -> bool
````

## File: task_scheduler.py
````python
"""Global repair scheduler over the persistent queue and pipeline state."""
⋮----
TERMINAL = {"completed", "superseded", "exhausted"}
RELEASE_STAGE_ORDER = (
PREVIEW_STAGES = {"preview_validation", "code_review", "visual_review", "preview"}
⋮----
def _completed_ids(state: dict) -> set[str]
⋮----
queue = state.get("repair_queue", [])
⋮----
def _dependencies_ready(task: dict, completed: set[str]) -> bool
⋮----
deps = task.get("dependencies", [])
⋮----
def _budget_feasible(state: dict, task: dict) -> bool
⋮----
action = task.get("action")
estimate = max(0, int(task.get("estimated_model_calls", 0)))
budget = budget_status(state)
⋮----
def _pipeline_ready(state: dict, task: dict) -> bool
⋮----
stage = task.get("stage")
⋮----
release = state.get("release_evidence", {})
index = RELEASE_STAGE_ORDER.index(stage)
⋮----
required = (
⋮----
evidence = release.get(prior)
⋮----
def _score(task: dict) -> float
⋮----
priority = float(task.get("priority", 0))
attempts = max(0, int(task.get("attempts", 0)))
stagnation = max(0, int(task.get("stagnation_count", 0)))
⋮----
efficiency = branch_efficiency(task)
⋮----
def candidates(state: dict) -> list[dict]
⋮----
completed = _completed_ids(state)
result = []
⋮----
def select(state: dict) -> dict | None
⋮----
ready = candidates(state)
⋮----
def dispatch(state: dict) -> dict
⋮----
task = select(state)
⋮----
def pipeline_stage_for_task(task: dict | None) -> str | None
⋮----
blockers = set(task.get("blockers", []))
````

## File: telemetry_maintenance.py
````python
"""Bound telemetry retention for long-running autonomous projects."""
⋮----
MAX_BYTES = 8 * 1024 * 1024
TARGET_BYTES = 4 * 1024 * 1024
⋮----
def compact(path: Path) -> dict
⋮----
path = Path(path)
⋮----
before = path.stat().st_size
⋮----
raw = path.read_text(encoding="utf-8")
⋮----
lines = raw.splitlines()
kept = []
used = 0
⋮----
encoded = (line + "\n").encode("utf-8")
⋮----
text = "\n".join(kept)
⋮----
after = path.stat().st_size if path.is_file() else 0
````

## File: telemetry.py
````python
"""Minimal durable operational telemetry for autonomous runs."""
⋮----
MAX_EVENT_BYTES = 64 * 1024
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_TELEMETRY_PATH", "").strip()
⋮----
def emit(kind: str, **fields) -> None
⋮----
path = _path()
⋮----
event = {
raw = canonical(event).encode("utf-8")
⋮----
def summarize(path: Path) -> dict
⋮----
path = Path(path)
⋮----
kinds = {}
count = 0
last_ts = None
⋮----
event = json.loads(line)
⋮----
kind = str(event.get("kind", "unknown"))
⋮----
ts = event.get("ts")
⋮----
last_ts = ts
````

## File: unified_routing_score.py
````python
"""Unified bounded provider routing score. Hard eligibility remains external/fail-closed."""
⋮----
base = max(0.0, min(100.0, float(getattr(provider, "priority", 50))))
free_bonus = 8.0 if bool(getattr(provider, "free_preferred", False)) else 0.0
unmetered_bonus = 10.0 if bool(getattr(provider, "unmetered", False)) else 0.0
quota_bonus = 5.0 if int(getattr(provider, "monthly_token_quota", 0) or 0) > 0 else 0.0
health_data = health or {}
health_signal = max(-20.0, min(20.0, reliability_bonus(health_data, provider.name)))
specialized = scoped_evidence(
specialized_rate = float(specialized["reliability"])
specialized_confidence = float(specialized["confidence"])
specialized_health_signal = max(
latency_signal = max(-12.0, min(12.0, latency_bonus(metrics or {}, provider.name, role)))
runtime_signal = max(-12.0, min(12.0, runtime_bonus(runtime or {}, provider.name, model)))
context_signal = max(-18.0, min(12.0, float(contextual_adjustment or 0.0)))
exploration_signal = max(0.0, min(8.0, float(exploration_bonus or 0.0)))
calibration_signal = calibration_adjustment(calibration or {}, provider.name, model)
total = (
````

## File: v1_gate.py
````python
"""Operational V1 gate combining host readiness and optional project runtime health."""
⋮----
def evaluate(root: Path | str = ".", project_out: Path | str | None = None) -> dict
⋮----
readiness = readiness_check(root=root, project_out=project_out)
runtime = runtime_health(project_out) if project_out is not None else None
⋮----
failures = []
⋮----
verdict = "blocked"
⋮----
verdict = "ready"
⋮----
verdict = "operational"
⋮----
def main(argv=None) -> int
⋮----
parser = argparse.ArgumentParser(description="AI Dev Server V1 operational gate")
⋮----
args = parser.parse_args(argv)
report = evaluate(args.root, args.project_out)
````

## File: verification_cost.py
````python
"""Persistent verification-cost memory keyed by detected toolchain."""
⋮----
ALPHA = 0.25
MAX_ROWS = 64
⋮----
def stack_key(toolchain: dict | None) -> str
⋮----
stacks = toolchain.get("stacks") if isinstance(toolchain, dict) else None
⋮----
clean = sorted({str(x).strip().lower() for x in stacks if str(x).strip()})
⋮----
def load(path: Path) -> dict
⋮----
value = json.loads(Path(path).read_text(encoding="utf-8"))
⋮----
clean = {}
⋮----
runs = max(0, int(row.get("runs", 0)))
successes = max(0, int(row.get("successes", 0)))
ema = max(0.0, float(row.get("ema_seconds", 0.0)))
⋮----
def _save(path: Path, data: dict) -> None
⋮----
path = Path(path)
⋮----
def record(path: Path, toolchain: dict | None, *, elapsed_seconds: float, success: bool) -> dict
⋮----
key = stack_key(toolchain)
data = load(path)
row = data.get(key, {"runs": 0, "successes": 0, "ema_seconds": 0.0})
runs = int(row["runs"])
previous = float(row["ema_seconds"])
elapsed = max(0.0, float(elapsed_seconds))
ema = elapsed if runs == 0 else (ALPHA * elapsed + (1.0 - ALPHA) * previous)
⋮----
def estimate_seconds(data: dict, toolchain: dict | None, *, fallback: float | None = None) -> float | None
⋮----
row = data.get(stack_key(toolchain))
````

## File: worker_heartbeat.py
````python
"""Progress-gated heartbeat helper for claimed worker capacity."""
⋮----
def progress_marker(project_out: Path | str) -> str
⋮----
root = Path(project_out)
candidates = [
digest = hashlib.sha256()
seen = 0
⋮----
payload = path.read_bytes()
````

## File: worker_reaper.py
````python
"""Classify expired worker reservations and surface recoverable capacity."""
⋮----
REPORT_FILE = "worker-liveness.json"
⋮----
def _project_status(root: Path, project_id: str) -> str
⋮----
path = root / project_id / name
⋮----
value = json.loads(path.read_text(encoding="utf-8"))
⋮----
def classify(root: Path | str = "studio-output", *, now: float | None = None) -> dict
⋮----
root = Path(root)
ledger_path = root / "capacity-ledger.json"
snap = detailed_snapshot(ledger_path, now=now)
data = load(ledger_path)
rows = []
⋮----
project_id = str(event.get("project_id") or "")
kind = str(event.get("kind") or "")
status = _project_status(root, project_id)
⋮----
classification = "completed"
⋮----
classification = "orphaned"
⋮----
classification = "stalled"
⋮----
classification = "crashed"
⋮----
report = {
````

## File: worker_reliability.py
````python
"""Reliability scoring from durable worker liveness evidence."""
⋮----
WEIGHTS = {"completed": 1.0, "crashed": -1.0, "stalled": -0.75, "orphaned": -0.5}
⋮----
def summarize(liveness: dict) -> dict
⋮----
workers = liveness.get("workers") if isinstance(liveness, dict) else None
buckets = {}
⋮----
project = str(row.get("project_id") or "").strip()
⋮----
classification = str(row.get("classification") or "")
bucket = buckets.setdefault(project, {
⋮----
projects = {}
⋮----
samples = bucket["samples"]
positive = bucket["completed"]
negative_weight = (
# Beta prior keeps sparse histories near neutral instead of overreacting.
reliability = (positive + 2.0) / (positive + negative_weight + 4.0)
confidence = min(1.0, samples / 8.0)
multiplier = 1.0 + (reliability - 0.5) * confidence
⋮----
def project_multiplier(summary: dict, project_id: str) -> float
⋮----
row = (summary.get("projects") or {}).get(project_id) if isinstance(summary, dict) else None
````

## File: workflow_checkpoint.py
````python
"""Crash-resumable idempotency checkpoints for expensive workflow operations."""
⋮----
SCHEMA = 1
MAX_ENTRIES = 256
MAX_BYTES = 4 * 1024 * 1024
⋮----
def _path() -> Path | None
⋮----
raw = os.environ.get("STUDIO_CHECKPOINT_PATH", "").strip()
⋮----
def operation_key(kind: str, payload: dict) -> str
⋮----
raw = canonical({
⋮----
def _load_path(path: Path) -> dict
⋮----
data = json.loads(path.read_text(encoding="utf-8"))
⋮----
entries = data.get("entries")
⋮----
def load_path(path: Path) -> dict
⋮----
def load() -> dict
⋮----
path = _path()
⋮----
def get(key: str) -> dict | None
⋮----
row = load().get(key)
⋮----
value = row.get("value")
⋮----
def put(key: str, value: dict, *, kind: str) -> None
⋮----
entries = _load_path(path)
⋮----
entries = dict(list(entries.items())[-MAX_ENTRIES:])
payload = {"schema": SCHEMA, "entries": entries}
raw = canonical(payload)
⋮----
def discard(key: str) -> None
````

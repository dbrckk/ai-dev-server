"""Deterministic fail-closed resilience smoke test."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import urllib.error

from capability_adaptation_state import new_state as new_capability_state, validate as validate_capability_state, CapabilityAdaptationStateError
from capability_registry_review import inspect as inspect_registry_review, CapabilityRegistryReviewError
from core import API, APIError
from execution_checkpoint import new as new_checkpoint, save as save_checkpoint, load as load_checkpoint, ExecutionCheckpointError
from provider_health import record_failure, eligible
from run_cost_controller import RunCostController


def main() -> int:
    results = {}

    # Provider outage must fail closed after bounded retries.
    api = API("https://provider.invalid/v1", "test-token")
    transient = urllib.error.HTTPError("https://provider.invalid", 503, "busy", {}, None)
    try:
        with patch.object(api, "_response", side_effect=[transient, transient, transient]), patch("core.time.sleep"):
            api.call("POST", "/chat/completions", {}, timeout_seconds=30)
    except APIError as exc:
        results["provider_outage"] = exc.status == 503
    else:
        results["provider_outage"] = False

    with tempfile.TemporaryDirectory(prefix="studio-fault-injection-") as td:
        root = Path(td)

        health = root / "provider-health.json"
        for _ in range(3):
            record_failure(health, "p1", threshold=3, cooldown_seconds=60, now=100.0)
        results["circuit_breaker"] = eligible(health, "p1", now=120.0) is False

        checkpoint_path = root / "checkpoint.json"
        checkpoint = new_checkpoint("demo", "generic", "a" * 40)
        save_checkpoint(checkpoint_path, checkpoint)
        tampered = json.loads(checkpoint_path.read_text())
        tampered["round"] = 9
        checkpoint_path.write_text(json.dumps(tampered))
        try:
            load_checkpoint(checkpoint_path)
        except ExecutionCheckpointError:
            results["checkpoint_integrity"] = True
        else:
            results["checkpoint_integrity"] = False

    controller = RunCostController(total_budget_seconds=1000, max_model_calls=20)
    controller.model_seconds = 300
    controller.agent_seconds = 250
    controller.verification_seconds = 250
    controller.review_seconds = 120
    results["run_cost_stop"] = controller.decision()["action"] == "stop"

    adaptation = new_capability_state("demo", "image_assets", "candidate:x")
    adaptation["status"] = "complete"
    try:
        validate_capability_state(adaptation)
    except CapabilityAdaptationStateError:
        results["adaptation_integrity"] = True
    else:
        results["adaptation_integrity"] = False

    review = {
        "status": "registry_promotion_persisted",
        "candidate_id": "candidate:a",
        "candidate_sha256": "a" * 64,
        "capability": "image_assets",
        "candidate_merge_sha": "d" * 40,
        "branch": "capability/promote-image-assets-x-" + "b" * 40,
        "commit_sha": "b" * 40,
        "pull_request": 24,
    }
    class FakeGitHub:
        def get(self, path):
            if path != "/pulls/24":
                raise AssertionError(path)
            return {
                "state": "open",
                "merged": False,
                "merged_at": None,
                "merge_commit_sha": None,
                "base": {"ref": "main"},
                "head": {"ref": review["branch"], "sha": "e" * 40},
            }
    try:
        inspect_registry_review(FakeGitHub(), review)
    except CapabilityRegistryReviewError:
        results["promotion_identity"] = True
    else:
        results["promotion_identity"] = False

    passed = all(results.values())
    out = Path("studio-output/fault-injection")
    out.mkdir(parents=True, exist_ok=True)
    (out / "fault-injection.json").write_text(json.dumps({
        "passed": passed,
        "scenarios": results,
    }, sort_keys=True, indent=2) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

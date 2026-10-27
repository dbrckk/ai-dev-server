"""Deterministic generic-engine end-to-end smoke tests.

This exercises both the trusted toolchain/verifier path and the real
generic_project orchestration loop. Only the external GitHub and LLM boundaries
are replaced with deterministic local doubles.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import generic_project
from generic_toolchain import detect, bootstrap_commands
from generic_verify import run as verify
from core import StudioError


def _fixture(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root/"pyproject.toml").write_text(
        "[project]\nname='studio-generic-smoke'\nversion='0.1.0'\nrequires-python='>=3.11'\n"
    )
    (root/"calculator.py").write_text(
        "def add(a,b):\n    return a-b\n"
    )
    (root/"test_calculator.py").write_text(
        "import unittest\nfrom calculator import add\n\n"
        "class CalculatorTests(unittest.TestCase):\n"
        "    def test_add(self): self.assertEqual(add(2,3),5)\n\n"
        "if __name__=='__main__': unittest.main()\n"
    )


class FakeRepository:
    def __init__(self, github, target_repo, project_id):
        self.github=github
        self.repo=target_repo
        self.project_id=project_id
        self.branch="studio/"+project_id
        self.default_branch="main"

    def restore(self, work: Path):
        _fixture(work)
        return "a"*40, {"mode":"deterministic_smoke"}

    def publish(self, base_sha: str, work: Path, message: str):
        if not (work/"calculator.py").is_file():
            raise RuntimeError("smoke publish missing implementation")
        return "b"*40


def fake_ask(system: str, user: str, *, code=False, **kwargs):
    meta={
        "provider":"deterministic-smoke",
        "model":"local-fixture",
        "duration_seconds":0.01,
    }
    if system == generic_project.PLAN_SYSTEM:
        return {
            "objective":"Fix addition and preserve a verified regression test.",
            "work_items":["Correct calculator.add"],
            "done_when":["unit tests pass"],
        }, meta
    if system == generic_project.IMPLEMENT_SYSTEM:
        return {
            "files":[{
                "path":"calculator.py",
                "content":"def add(a,b):\n    return a+b\n",
            }]
        }, meta
    if system == generic_project.PROGRESS_SYSTEM:
        return {
            "action":"verify",
            "reason":"The targeted implementation is ready for trusted unit verification.",
            "next_work":[],
        }, meta
    if system == generic_project.REVIEW_SYSTEM:
        payload=json.loads(user)
        verification=payload.get("verification",{})
        return {
            "complete":verification.get("passed") is True,
            "remaining":[] if verification.get("passed") is True else ["repair failing tests"],
            "reason":"Trusted verification determines completion in this fixed fixture.",
        }, meta
    raise AssertionError("unexpected deterministic model role")


def verifier_smoke() -> dict:
    with tempfile.TemporaryDirectory(prefix="studio-generic-verifier-") as td:
        root=Path(td)
        _fixture(root)
        # Correct locally so this lower-level smoke isolates toolchain + verifier.
        (root/"calculator.py").write_text("def add(a,b):\n    return a+b\n")
        toolchain=detect(root)
        commands=bootstrap_commands(root)
        verification=verify(root,timeout_per_command=120)
        return {
            "passed":toolchain.get("stacks")==["python"] and not commands and verification.get("passed") is True,
            "toolchain":toolchain,
            "bootstrap_commands":commands,
            "verification":verification,
        }


def orchestration_smoke(out: Path) -> dict:
    work=out/"work"
    project_out=out/"project"
    req={
        "id":"generic-smoke",
        "target_repo":"fixture/generic-smoke",
        "brief":"Fix the calculator addition bug and leave the repository verified.",
        "max_calls":8,
    }
    with patch.object(generic_project,"GitHub",side_effect=lambda repo:object()), \
         patch.object(generic_project,"GenericRepository",FakeRepository), \
         patch.object(generic_project,"ask",side_effect=fake_ask), \
         patch.object(generic_project,"rank_agents",return_value=[]), \
         patch.object(generic_project,"recommend",return_value={"matches":[]}):
        result=generic_project.run_project(
            req,
            project_out,
            work,
            portfolio={},
            max_rounds=1,
        )
    report=result.get("report",{})
    verification=(report.get("rounds") or [{}])[-1].get("verification",{})
    return {
        "passed":(
            result.get("status")=="complete"
            and report.get("completion",{}).get("finished") is True
            and verification.get("passed") is True
            and (work/"calculator.py").read_text()=="def add(a,b):\n    return a+b\n"
            and report.get("execution_checkpoint",{}).get("phase")=="complete"
        ),
        "status":result.get("status"),
        "verification":verification,
        "execution_checkpoint":report.get("execution_checkpoint"),
        "round_count":len(report.get("rounds",[])),
    }


def main() -> int:
    out=Path("studio-output/generic-smoke")
    out.mkdir(parents=True,exist_ok=True)
    verifier=verifier_smoke()
    orchestration=orchestration_smoke(out)
    # Exercise the real managed generation -> verification -> publication loop.
    # External model/GitHub boundaries remain explicitly deterministic fixtures.
    managed_out = Path(tempfile.mkdtemp(prefix="managed-", dir=out))
    request = {"id": "managed-smoke", "target_repo": "fixture/generic-smoke",
               "brief": "Fix calculator addition", "max_calls": 8,
               "production_os": {"workflow_id": "1" * 32, "workflow_task_id": "implementation"}}
    publication = {"sha": "a" * 40, "count": 0, "available": False,
                   "ci": "absent", "dispatches": 0}
    delivery_clock = [1000.0]
    class ManagedGitHub:
        repo = "/repos/fixture/generic-smoke"
        def dispatch(self, repo, wid):
            assert wid == 7 and repo.branch == "studio/managed-smoke"
            publication["dispatches"] += 1
            return {"status": "accepted"}
        def get(self, path):
            workflow = {"id": 7, "name": "CI", "state": "active", "path": ".github/workflows/ci.yml"}
            run = {"id": 12, "run_attempt": 1, "head_sha": publication["sha"],
                   "head_branch": "studio/managed-smoke", "workflow_id": 7,
                   "path": workflow["path"], "event": "workflow_dispatch",
                   "status": "completed" if publication["ci"] in {"success", "failure"} else "in_progress",
                   "conclusion": publication["ci"]}
            if path == "/actions/workflows?per_page=100":
                return {"total_count": 1, "workflows": [workflow]}
            if path.startswith("/contents/"):
                return {"type": "file", "sha": "d" * 40}
            if path.startswith("/actions/workflows/7/runs?"):
                return {"workflow_runs": [] if publication["ci"] == "absent" else [run]}
            if path == "/actions/runs/12":
                return run
            if path == "/actions/runs/12/attempts/1/jobs?per_page=100":
                return {"total_count": 1, "jobs": [{"run_id": 12, "run_attempt": 1,
                        "head_sha": publication["sha"], "name": "independent-test",
                        "status": "completed", "conclusion": publication["ci"],
                        "steps": [{"status": "completed", "conclusion": publication["ci"]}]}]}
            raise AssertionError(path)
    class ManagedRepository(FakeRepository):
        def delivery_head(self):
            return publication["sha"]
        def restore(self, work):
            _fixture(work)
            if publication["count"]:
                (work / "calculator.py").write_text(publication["content"])
            return publication["sha"], {"mode": "deterministic_smoke"}
        def publish(self, base_sha, work, message):
            publication["count"] += 1
            publication["sha"] = super().publish(base_sha, work, message)
            if publication["count"] > 1:
                publication["sha"] = "c" * 40
            publication["content"] = (work / "calculator.py").read_text()
            return publication["sha"]
        def ensure_pull_request(self, **kwargs):
            assert kwargs["expected_sha"] == publication["sha"]
            if not publication["available"]:
                raise StudioError("API HTTP 403")
            return {"number": 1, "state": "open", "url": "https://github.com/fixture/generic-smoke/pull/1"}
        def request_trusted_review_handoff(self, sha):
            return {"status": "unavailable"}
        def _find_open_pull_request(self, **kwargs):
            return self.ensure_pull_request(**kwargs)
    with patch.object(generic_project, "GitHub", side_effect=lambda repo: ManagedGitHub()), \
         patch("generic_delivery.time.time", side_effect=lambda: delivery_clock[0]), \
         patch("generic_delivery.dispatch_ci", side_effect=ManagedGitHub().dispatch), \
         patch.object(generic_project, "GenericRepository", ManagedRepository), \
         patch.object(generic_project, "ask", side_effect=fake_ask) as model, \
         patch.object(generic_project, "rank_agents", return_value=[]), \
         patch.object(generic_project, "recommend", return_value={"matches": []}):
        pending = generic_project.run_project(request, managed_out, out / "managed-work", max_rounds=1)
        calls = model.call_count
        assert calls > 0
        model.side_effect = AssertionError("delivery recovery must not regenerate implementation")
        publication["available"] = True
        awaiting_ci = generic_project.run_project(request, managed_out, out / "managed-ci-wait", max_rounds=1)
        assert awaiting_ci["status"] == "deferred" and publication["dispatches"] == 0
        delivery_clock[0] += 59
        grace_wait = generic_project.run_project(request, managed_out, out / "managed-ci-grace", max_rounds=1)
        assert grace_wait["status"] == "deferred" and publication["dispatches"] == 0
        delivery_clock[0] += 1
        dispatched = generic_project.run_project(request, managed_out, out / "managed-ci-dispatched", max_rounds=1)
        assert dispatched["status"] == "deferred" and publication["dispatches"] == 1
        waiting_again = generic_project.run_project(request, managed_out, out / "managed-ci-wait-again", max_rounds=1)
        assert waiting_again["status"] == "deferred" and publication["dispatches"] == 1
        publication["ci"] = "success"
        resumed = generic_project.run_project(request, managed_out, out / "managed-resume", max_rounds=1)
        managed = {
            "passed": pending["status"] == "deferred" and resumed["status"] == "complete"
                      and publication["count"] == 1 and model.call_count == calls
                      and resumed["report"]["checkpoint_commit"] == "b" * 40,
            "initial_status": pending["status"], "resumed_status": resumed["status"],
            "publication_count": publication["count"], "new_model_calls_on_resume": model.call_count - calls,
            "ci_dispatches": publication["dispatches"], "independent_ci": resumed["report"]["ci"]["status"],
        }
        # Inject an independent CI failure, then exercise another real local
        # implementation/verifier cycle using explicit deterministic responses.
        publication["ci"] = "failure"
        rejected = generic_project.run_project(request, managed_out, out / "managed-rejected", max_rounds=1)
        assert rejected["next_stage"] == "generic_ci_repair" and model.call_count == calls
        seen_failure = []
        def repair_ask(system, user, **kwargs):
            answer, meta = fake_ask(system, user, **kwargs)
            if system == generic_project.IMPLEMENT_SYSTEM:
                seen_failure.append("independent_CI_failed" in user)
                answer["files"][0]["content"] += "# Independently rechecked fixture repair.\n"
            return answer, meta
        model.side_effect = repair_ask
        publication["ci"] = "absent"
        repaired = generic_project.run_project(request, managed_out, out / "managed-repair", max_rounds=1)
        assert repaired["status"] == "deferred" and seen_failure == [True]
        assert publication["count"] == 2 and publication["dispatches"] == 1
        repair_calls = model.call_count
        model.side_effect = AssertionError("repaired CI dispatch must not invoke model")
        delivery_clock[0] += 60
        repair_dispatch = generic_project.run_project(request, managed_out, out / "managed-repair-ci-dispatch", max_rounds=1)
        assert repair_dispatch["status"] == "deferred"
        assert publication["count"] == 2 and publication["dispatches"] == 2
        model.side_effect = AssertionError("CI confirmation must not invoke model")
        publication["ci"] = "success"
        accepted = generic_project.run_project(request, managed_out, out / "managed-repaired-ci", max_rounds=1)
        managed["repair"] = {"passed": accepted["status"] == "complete" and model.call_count == repair_calls,
                             "checkpoint_commit": accepted["report"]["checkpoint_commit"],
                             "failure_reached_model": all(seen_failure), "publication_count": publication["count"]}
        managed["passed"] = managed["passed"] and managed["repair"]["passed"]
    evidence={
        "passed":verifier.get("passed") is True and orchestration.get("passed") is True and managed["passed"],
        "verifier":verifier,
        "orchestration":orchestration,
        "managed_delivery": managed,
    }
    (out/"generic-smoke.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    return 0 if evidence["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())

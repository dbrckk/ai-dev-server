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
        self.project_id=project_id

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
    evidence={
        "passed":verifier.get("passed") is True and orchestration.get("passed") is True,
        "verifier":verifier,
        "orchestration":orchestration,
    }
    (out/"generic-smoke.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    return 0 if evidence["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())

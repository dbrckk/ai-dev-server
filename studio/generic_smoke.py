"""Deterministic generic-engine smoke test using the trusted verifier."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from generic_toolchain import detect, bootstrap_commands
from generic_verify import run as verify


def main() -> int:
    out=Path("studio-output/generic-smoke")
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="studio-generic-smoke-") as td:
        root=Path(td)
        (root/"pyproject.toml").write_text(
            "[project]\nname='studio-generic-smoke'\nversion='0.1.0'\nrequires-python='>=3.11'\n"
        )
        (root/"calculator.py").write_text(
            "def add(a,b):\n    return a+b\n"
        )
        (root/"test_calculator.py").write_text(
            "import unittest\nfrom calculator import add\n\n"
            "class CalculatorTests(unittest.TestCase):\n"
            "    def test_add(self): self.assertEqual(add(2,3),5)\n\n"
            "if __name__=='__main__': unittest.main()\n"
        )
        toolchain=detect(root)
        if toolchain.get("stacks") != ["python"]:
            evidence={"passed":False,"reason":"python toolchain not detected","toolchain":toolchain}
        else:
            commands=bootstrap_commands(root)
            if commands:
                evidence={"passed":False,"reason":"unexpected dependency bootstrap for dependency-free fixture","commands":commands}
            else:
                verification=verify(root,timeout_per_command=120)
                evidence={
                    "passed":verification.get("passed") is True,
                    "toolchain":toolchain,
                    "bootstrap_commands":commands,
                    "verification":verification,
                }
        (out/"generic-smoke.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
        return 0 if evidence.get("passed") is True else 1


if __name__=="__main__":
    raise SystemExit(main())

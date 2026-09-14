"""CI entry point validating replacement-required GitHub check names."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from replacement_ci_policy import validate_workflow

def main(argv=None) -> int:
    args=list(sys.argv[1:] if argv is None else argv)
    path=Path(args[0]) if args else Path(".github/workflows/ci.yml")
    try:
        result=validate_workflow(path)
    except OSError:
        result={"valid":False,"missing_checks":["workflow_unreadable"]}
    print(json.dumps(result,sort_keys=True))
    return 0 if result.get("valid") is True else 1

if __name__=="__main__":
    sys.exit(main())

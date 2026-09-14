"""Standalone CI validator for replacement reputation policy invariants."""
from __future__ import annotations

import json
import sys

from architecture_replacement_reputation import validate_transition_policy

def main() -> int:
    result=validate_transition_policy()
    print(json.dumps(result,sort_keys=True))
    return 0 if result.get("valid") is True else 1

if __name__=="__main__":
    sys.exit(main())

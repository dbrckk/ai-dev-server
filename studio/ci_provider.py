"""Explicit, fail-closed ownership of privileged mobile generation."""
import json
from pathlib import Path
from core import StudioError

def selected(path='control/ci.json'):
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict) or set(value) != {'provider'} or value['provider'] not in ('github', 'circleci', 'disabled'):
        raise StudioError('Invalid CI provider configuration')
    return value['provider']

def enabled(provider, path='control/ci.json'):
    if provider not in ('github', 'circleci'):
        raise StudioError('Unknown CI provider')
    return selected(path) == provider

if __name__ == '__main__':
    import sys
    sys.exit(0 if enabled(sys.argv[1]) else 1)

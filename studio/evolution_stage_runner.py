"""Execute a promoted QA stage with production credentials removed."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

SECRET_ENV_PREFIXES = ('STUDIO_GITHUB_TOKEN', 'GITHUB_TOKEN', 'GH_TOKEN', 'STUDIO_API_KEY', 'NVIDIA_NIM_API_KEY')


class PromotedStageError(RuntimeError):
    pass


def scrubbed_env(source=None):
    env = dict(os.environ if source is None else source)
    for key in list(env):
        upper = key.upper()
        if key in SECRET_ENV_PREFIXES or upper.endswith('_TOKEN') or upper.endswith('_API_KEY') or upper.endswith('_SECRET'):
            env.pop(key, None)
    env['STUDIO_PROMOTED_STAGE'] = '1'
    return env


def run(script: str, args: list[str], timeout: float | None = None):
    path = Path(script)
    if path.is_absolute() or '..' in path.parts or len(path.parts) != 2 or path.parts[0] != 'studio' or not path.name.endswith('_stage.py'):
        raise PromotedStageError('Promoted stage path rejected')
    return subprocess.run([sys.executable, script, *args], env=scrubbed_env(), timeout=timeout)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 1:
        raise PromotedStageError('Promoted stage script missing')
    result = run(argv[0], argv[1:])
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())

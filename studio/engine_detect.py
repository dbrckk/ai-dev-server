"""Detect the target project engine as a bounded subprocess preflight."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import StudioError, canonical, request_check
from engine_entry import detect_engine
from run import GitHub


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    req = request_check(json.loads(Path(args.request).read_text()))
    if not req['enabled']:
        result = {'status':'disabled','engine':None}
    else:
        github = GitHub(req['target_repo'])
        result = {'status':'detected','engine':detect_engine(req, github)}
    (out/'engine-detection.json').write_text(canonical(result))
    print(canonical(result))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (StudioError, ValueError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))

"""Validate the entire trusted request queue before starting any privileged job."""
import json
from pathlib import Path
from core import request_check, StudioError


def matrix(directory, terminal_ids=()):
    requests, targets, ids = [], set(), set()
    terminal_ids = set(terminal_ids)
    if any(not isinstance(x, str) or not x for x in terminal_ids):
        raise StudioError('Invalid terminal project id')
    for p in sorted(Path(directory).glob('*.json')):
        if not p.name.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise StudioError('Unsafe request filename')
        req = request_check(json.loads(p.read_text()))
        if not req['enabled'] or req['id'] in terminal_ids:
            continue
        target = req['target_repo'].lower()
        if target in targets or req['id'] in ids:
            raise StudioError('Only one active brief per target, with a unique id')
        targets.add(target)
        ids.add(req['id'])
        requests.append({'file': str(p), 'id': req['id'], 'target': target})
    if len(requests) > 5:
        raise StudioError('At most five active projects')
    return requests

if __name__ == '__main__':
    import argparse
    from ci_provider import enabled
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=['github', 'circleci'])
    parser.add_argument('--terminal-ids-json', default='[]')
    args = parser.parse_args()
    try:
        terminal_ids = json.loads(args.terminal_ids_json)
    except json.JSONDecodeError:
        raise StudioError('Invalid terminal project id JSON') from None
    if not isinstance(terminal_ids, list):
        raise StudioError('Invalid terminal project id JSON')
    projects = matrix('control/mobile-requests', terminal_ids)
    print(json.dumps(projects if not args.provider or enabled(args.provider) else []))

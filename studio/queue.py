"""Validate the entire trusted request queue before starting any privileged job."""
import json
from pathlib import Path
from core import request_check, StudioError


def matrix(directory):
    requests, targets, ids = [], set(), set()
    for p in sorted(Path(directory).glob('*.json')):
        if not p.name.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise StudioError('Unsafe request filename')
        req = request_check(json.loads(p.read_text()))
        if not req['enabled']:
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
    print(json.dumps(matrix('control/mobile-requests')))

"""Validate generated Play Store artwork before privacy/security completion."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from artwork_capability import builtin_visual_qa, select_provider, validate_artwork_set, ArtworkError
from capability_registry import load as load_registry, new_registry
from completion import apply_completion, next_stage
from core import StudioError, canonical
from run import GitHub


def _registry(out: Path):
    path=out/'.autonomy/capabilities.json'
    return load_registry(path) if path.is_file() else new_registry()


def advance(request_path: Path, root: Path, out: Path) -> dict:
    req=json.loads(request_path.read_text())
    report_path=out/'report.json'
    if not report_path.is_file():
        raise StudioError('Missing store metadata report')
    state=json.loads(report_path.read_text())
    if next_stage(state)!='artwork_qa':
        apply_completion(state)
        report_path.write_text(canonical(state))
        return state

    icon=out/'play-store/icon-512.png'
    feature=out/'play-store/feature-graphic-1024x500.png'
    try:
        provider=select_provider(_registry(out))
        visual=builtin_visual_qa(icon,feature)
        evidence=validate_artwork_set(
            icon,feature,
            provider_selection=provider,
            visual_qa=visual,
        )
    except (ArtworkError,ValueError) as exc:
        evidence={'passed':False,'blockers':[str(exc)]}

    state.setdefault('release_evidence',{})['artwork_qa']=evidence
    apply_completion(state)

    parent=state.get('checkpoint_commit')
    if not parent:
        raise StudioError('Store metadata report has no checkpoint commit')
    github=GitHub(req['target_repo'])
    sha=github.publish('studio/'+req['id'],parent,root,state)
    state['checkpoint_commit']=sha
    report_path.write_text(canonical(state))
    return state


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('request')
    parser.add_argument('--work',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    state=advance(Path(args.request),Path(args.work),Path(args.out))
    evidence=state.get('release_evidence',{}).get('artwork_qa')
    print(canonical({
        'status':state.get('status'),
        'next_stage':state.get('completion',{}).get('next_stage'),
        'artwork_qa_passed':evidence.get('passed') if isinstance(evidence,dict) else None,
    }))
    return 0 if isinstance(evidence,dict) and evidence.get('passed') else 1


if __name__=='__main__':
    raise SystemExit(main())

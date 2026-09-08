"""One bounded real-provider preview. Saves artifacts, never modifies a target repository."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from core import StudioError, allowed, canonical
from run import execute

class ArtifactProject:
    """Local delivery backend for a preview, with no GitHub write credentials."""
    def __init__(self, out):
        self.out = out
        self.native_files = {}
    def restore(self, branch, root):
        return None, None
    def publish(self, branch, parent, root, state):
        self.out.mkdir(parents=True, exist_ok=True)
        data = canonical(state)
        (self.out / 'checkpoint.json').write_text(data)
        files = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
                 if p.is_file() and not p.is_symlink() and
                 (allowed(p.relative_to(root).as_posix()) or p.relative_to(root).as_posix() == 'pubspec.lock')}
        files.update(self.native_files)
        with zipfile.ZipFile(self.out / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        # Checkpoint digest, explicitly not a GitHub commit.
        return hashlib.sha256(data.encode()).hexdigest()


def main():
    config = json.loads(Path('control/provider-probe.json').read_text())
    if config != {'enabled': True, 'revision': 1}:
        print('Provider preview disabled or unexpected control payload')
        return 0
    out = Path('studio-output')
    req = {'id': 'focus-provider-preview', 'target_repo': 'preview/focus', 'app_name': 'focus_preview',
           'enabled': True, 'max_rounds': 2, 'max_calls': 12, 'max_cycles': 1,
           'brief': 'Create a polished French Android focus timer. Use Flutter SDK only. Main screen: functional countdown starting at 25 minutes, start/pause/reset, and settings navigation. Settings: select 5 or 25 minute session duration, return to the main screen. Include light and dark themes, large touch targets, readable large text, clear hierarchy, professional spacing, and no decorative clutter. No backend, ads, account or persistence is required: settings and statistics are session-only. Define exactly two acceptance journeys. Acceptance journeys must verify the settings screen and start/pause/reset states using stable keys and deterministic text. Include real widget tests. The app must run without external assets, dependencies or services.'}
    try:
        state = execute(req, Path('/tmp/provider-preview-app'), out, github=ArtifactProject(out))
        state['delivery_mode'] = 'workflow_artifact_only'
        state['checkpoint_digest'] = state.pop('checkpoint_commit', None)
        (out / 'report.json').write_text(canonical(state))
        print(canonical({'status': state['status'], 'model_calls': state.get('model_calls_this_cycle'), 'blockers': state.get('blockers', [])}))
        return 0 if state['status'] in ('validated_preview', 'awaiting_visual_review') else 1
    except (StudioError, ValueError, OSError) as e:
        out.mkdir(exist_ok=True)
        (out / 'error.json').write_text(canonical({'status': 'blocked', 'error': str(e) if isinstance(e, StudioError) else type(e).__name__, 'delivery_mode': 'workflow_artifact_only'}))
        print('Provider preview blocked; see artifact report.')
        return 1

if __name__ == '__main__':
    sys.exit(main())

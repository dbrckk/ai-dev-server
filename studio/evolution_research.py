"""Trusted bounded research adapters for factory evolution candidates.

No downloaded source code is executed. Network access is limited to explicit HTTPS
hosts and bounded response sizes. Known capability research resolves to official
platform documentation; package/GitHub adapters retrieve metadata only.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from evolution_evidence import validate_evidence

MAX_RESPONSE_BYTES = 256 * 1024
TIMEOUT_SECONDS = 15
USER_AGENT = 'ai-dev-server-evolution-research/1'

NETWORK_HOSTS = {
    'developer.android.com',
    'docs.flutter.dev',
    'developers.google.com',
    'firebase.google.com',
    'support.google.com',
    'developer.apple.com',
    'pub.dev',
    'api.github.com',
}

KNOWN_DOCS = (
    (('billing',), 'official_docs', 'https://developer.android.com/google/play/billing/integrate'),
    (('billing',), 'sdk_tool', 'https://developer.android.com/google/play/billing/test'),
    (('notification',), 'official_docs', 'https://developer.android.com/develop/ui/views/notifications/notification-permission'),
    (('platform view',), 'official_docs', 'https://docs.flutter.dev/platform-integration/android/platform-views'),
    (('runtime permission',), 'official_docs', 'https://developer.android.com/training/permissions/requesting'),
    (('native capability',), 'official_docs', 'https://developer.android.com/training/permissions/requesting'),
    (('performance',), 'official_docs', 'https://docs.flutter.dev/perf/ui-performance'),
    (('frame timing',), 'official_docs', 'https://docs.flutter.dev/perf/ui-performance'),
)

PACKAGE_HINTS = {
    'in_app_purchase': 'in_app_purchase',
    'billing': 'in_app_purchase',
    'webview_flutter': 'webview_flutter',
    'webview': 'webview_flutter',
    'google_maps_flutter': 'google_maps_flutter',
    'maps': 'google_maps_flutter',
    'video_player': 'video_player',
    'notification': 'flutter_local_notifications',
}


class ResearchBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class FetchResult:
    requested_url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_network_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _validate_network_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        raise ResearchBlocked('Invalid research URL') from None
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.fragment or port not in (None, 443)):
        raise ResearchBlocked('Research URL must be safe HTTPS')
    host = parsed.hostname.lower()
    if host not in NETWORK_HOSTS:
        raise ResearchBlocked('Research host is not allowlisted')
    return host


def fetch_url(url: str, *, extra_headers: dict[str, str] | None = None,
              timeout: int = TIMEOUT_SECONDS, max_bytes: int = MAX_RESPONSE_BYTES) -> FetchResult:
    _validate_network_url(url)
    headers = {'User-Agent': USER_AGENT, 'Accept': 'text/html,application/json,text/plain;q=0.9,*/*;q=0.1'}
    if extra_headers:
        headers.update(extra_headers)
    request = Request(url, headers=headers, method='GET')
    try:
        with build_opener(_SafeRedirect()).open(request, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_network_url(final_url)
            content_type = (response.headers.get('Content-Type') or '').lower()
            if content_type and not any(t in content_type for t in ('text/', 'json', 'html', 'xml')):
                raise ResearchBlocked('Research response is not textual metadata')
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ResearchBlocked('Research response exceeds size limit')
            normalized_headers = {str(k).lower(): str(v)[:500] for k, v in response.headers.items()}
            return FetchResult(url, final_url, int(getattr(response, 'status', 200)), normalized_headers, body)
    except ResearchBlocked:
        raise
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ResearchBlocked('Research source fetch failed') from None


def _title(body: bytes) -> str:
    text = body.decode('utf-8', errors='replace')
    match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ''
    value = re.sub(r'<[^>]+>', ' ', match.group(1))
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()[:300]


def _doc_source(task: dict) -> str:
    query = task['query'].lower()
    kind = task['kind']
    for needles, expected_kind, url in KNOWN_DOCS:
        if kind == expected_kind and all(needle in query for needle in needles):
            return url
    raise ResearchBlocked('No trusted official source mapping for research task')


def _provenance(result: FetchResult) -> dict:
    return {
        'requested_url': result.requested_url,
        'final_url': result.final_url,
        'status': result.status,
        'content_sha256': result.sha256,
        'content_bytes': len(result.body),
        'etag': result.headers.get('etag', ''),
        'last_modified': result.headers.get('last-modified', ''),
    }


def _official_item(task: dict, fetcher) -> tuple[dict, list[dict]]:
    url = _doc_source(task)
    result = fetcher(url)
    revision = result.headers.get('etag') or result.headers.get('last-modified') or result.sha256[:16]
    title = _title(result.body)
    return {
        'task_id': task['id'],
        'kind': task['kind'],
        'source': result.final_url,
        'version_or_revision': revision[:500],
        'license': 'official_documentation_terms',
        'maintenance_signal': (result.headers.get('last-modified') or result.headers.get('date') or 'source_retrieved')[:500],
        'risks': ['documentation_may_require_platform_version_cross_check'],
        'notes': ('Official source retrieved without executing external code.' + (f' Title: {title}' if title else ''))[:4000],
        'content_sha256': result.sha256,
    }, [_provenance(result)]


def _package_hint(query: str) -> str | None:
    lower = query.lower()
    for marker, package in PACKAGE_HINTS.items():
        if marker in lower:
            return package
    return None


def _github_headers() -> dict[str, str]:
    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('STUDIO_GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    return headers


def _github_repo_from_url(value: object) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme != 'https' or parsed.hostname not in ('github.com', 'www.github.com'):
        return None
    parts = [part for part in parsed.path.split('/') if part]
    if len(parts) < 2 or not all(re.fullmatch(r'[A-Za-z0-9_.-]+', p) for p in parts[:2]):
        return None
    return parts[0], parts[1].removesuffix('.git')


def _fetch_json(result: FetchResult) -> dict:
    try:
        value = json.loads(result.body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ResearchBlocked('Research metadata response is invalid JSON') from None
    if not isinstance(value, dict):
        raise ResearchBlocked('Research metadata JSON must be an object')
    return value


def _package_item(task: dict, fetcher) -> tuple[dict, list[dict]]:
    package = _package_hint(task['query'])
    provenance: list[dict] = []
    if package is None:
        search = fetcher('https://pub.dev/api/search?q=' + quote_plus(task['query']))
        provenance.append(_provenance(search))
        payload = _fetch_json(search)
        packages = payload.get('packages')
        if not isinstance(packages, list) or not packages or not isinstance(packages[0], dict):
            raise ResearchBlocked('Package registry returned no candidate')
        package = packages[0].get('package')
        if not isinstance(package, str) or not re.fullmatch(r'[a-z0-9_]+', package):
            raise ResearchBlocked('Package registry candidate name invalid')

    detail = fetcher('https://pub.dev/api/packages/' + package)
    provenance.append(_provenance(detail))
    payload = _fetch_json(detail)
    latest = payload.get('latest')
    if not isinstance(latest, dict):
        raise ResearchBlocked('Package registry metadata missing latest release')
    version = latest.get('version')
    pubspec = latest.get('pubspec')
    if not isinstance(version, str) or not isinstance(pubspec, dict):
        raise ResearchBlocked('Package registry latest release malformed')
    published = latest.get('published') if isinstance(latest.get('published'), str) else ''
    repository = pubspec.get('repository') or pubspec.get('homepage')
    license_value = 'license_requires_repository_review'
    maintenance = published or 'latest_release_available'
    risks = ['dependency_must_be_pinned_and_regression_tested']
    notes = [f'Package: {package}.']

    repo = _github_repo_from_url(repository)
    if repo:
        owner, name = repo
        meta = fetcher(f'https://api.github.com/repos/{owner}/{name}', extra_headers=_github_headers())
        provenance.append(_provenance(meta))
        repo_payload = _fetch_json(meta)
        license_obj = repo_payload.get('license')
        if isinstance(license_obj, dict) and isinstance(license_obj.get('spdx_id'), str):
            license_value = license_obj['spdx_id'][:500]
        pushed = repo_payload.get('pushed_at')
        archived = bool(repo_payload.get('archived'))
        if isinstance(pushed, str):
            maintenance = f'pushed_at={pushed}; archived={str(archived).lower()}'
        if archived:
            risks.append('upstream_repository_archived')
        html_url = repo_payload.get('html_url')
        if isinstance(html_url, str):
            notes.append('Repository: ' + html_url[:500])

    combined_hash = hashlib.sha256(''.join(p['content_sha256'] for p in provenance).encode()).hexdigest()
    return {
        'task_id': task['id'],
        'kind': task['kind'],
        'source': f'https://pub.dev/packages/{package}',
        'version_or_revision': version[:500],
        'license': license_value,
        'maintenance_signal': maintenance[:500],
        'risks': risks,
        'notes': ' '.join(notes)[:4000],
        'content_sha256': combined_hash,
    }, provenance


def _github_item(task: dict, fetcher) -> tuple[dict, list[dict]]:
    url = 'https://api.github.com/search/repositories?q=' + quote_plus(task['query']) + '&sort=updated&order=desc&per_page=5'
    result = fetcher(url, extra_headers=_github_headers())
    payload = _fetch_json(result)
    items = payload.get('items')
    if not isinstance(items, list):
        raise ResearchBlocked('GitHub research response missing items')
    candidates = [item for item in items if isinstance(item, dict) and not item.get('archived')]
    if not candidates:
        raise ResearchBlocked('GitHub research found no maintained candidate')
    repo = candidates[0]
    source = repo.get('html_url')
    if not isinstance(source, str) or _github_repo_from_url(source) is None:
        raise ResearchBlocked('GitHub candidate URL invalid')
    license_obj = repo.get('license')
    license_value = license_obj.get('spdx_id') if isinstance(license_obj, dict) else None
    pushed = repo.get('pushed_at') if isinstance(repo.get('pushed_at'), str) else ''
    stars = repo.get('stargazers_count') if isinstance(repo.get('stargazers_count'), int) else 0
    default_branch = repo.get('default_branch') if isinstance(repo.get('default_branch'), str) else 'unknown'
    return {
        'task_id': task['id'],
        'kind': task['kind'],
        'source': source,
        'version_or_revision': f'{default_branch}; pushed_at={pushed}'[:500],
        'license': str(license_value or 'license_unresolved')[:500],
        'maintenance_signal': f'pushed_at={pushed}; stars={stars}'[:500],
        'risks': ['reference_implementation_is_untrusted_until_reviewed_and_pinned'],
        'notes': 'Repository metadata only; no discovered code was executed.',
        'content_sha256': result.sha256,
    }, [_provenance(result)]


def _run_version(executable: str, args: list[str]) -> str:
    path = shutil.which(executable)
    if not path:
        return ''
    try:
        result = subprocess.run([path, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ''
    return re.sub(r'\s+', ' ', result.stdout).strip()[:500]


def _device_item(task: dict) -> tuple[dict, list[dict]]:
    adb = _run_version('adb', ['version'])
    emulator = _run_version('emulator', ['-version'])
    if not adb or not emulator:
        raise ResearchBlocked('Android emulator runtime is unavailable')
    fingerprint = json.dumps({'adb': adb, 'emulator': emulator}, sort_keys=True).encode()
    digest = hashlib.sha256(fingerprint).hexdigest()
    return {
        'task_id': task['id'],
        'kind': task['kind'],
        'source': 'android-emulator',
        'version_or_revision': emulator[:500],
        'license': 'installed_android_sdk_runtime',
        'maintenance_signal': adb[:500],
        'risks': ['emulator_results_do_not_replace_required_physical_device_evidence'],
        'notes': 'Trusted local runtime fingerprint; no external code executed.',
        'content_sha256': digest,
    }, [{'runtime': 'android-emulator', 'content_sha256': digest}]


def research_task(task: dict, fetcher=fetch_url) -> tuple[dict, list[dict]]:
    if not isinstance(task, dict) or not all(isinstance(task.get(k), str) for k in ('id', 'kind', 'query')):
        raise ResearchBlocked('Malformed research task')
    kind = task['kind']
    if kind in ('official_docs', 'sdk_tool'):
        return _official_item(task, fetcher)
    if kind == 'package_registry':
        return _package_item(task, fetcher)
    if kind == 'github_source':
        return _github_item(task, fetcher)
    if kind == 'device_runtime':
        return _device_item(task)
    raise ResearchBlocked('Unsupported research task kind')


def execute(work_order: dict, out: Path, fetcher=fetch_url) -> dict:
    tasks = work_order.get('research_tasks') if isinstance(work_order, dict) else None
    if not isinstance(tasks, list) or not tasks:
        raise ResearchBlocked('Evolution work order has no research tasks')
    candidate_id = work_order.get('candidate_id')
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ResearchBlocked('Evolution work order candidate id missing')

    items = []
    provenance = []
    for task in tasks:
        item, task_provenance = research_task(task, fetcher)
        items.append(item)
        provenance.append({'task_id': task['id'], 'sources': task_provenance})

    envelope = {'version': 2, 'candidate_id': candidate_id, 'items': items}
    normalized = validate_evidence(work_order, envelope)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'evolution-research.json').write_text(json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    provenance_payload = {
        'version': 1,
        'candidate_id': candidate_id,
        'status': 'research_provenance_recorded',
        'tasks': provenance,
    }
    (out / 'evolution-research-provenance.json').write_text(
        json.dumps(provenance_payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    return normalized


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('work_order')
    parser.add_argument('--out', default='studio-output')
    args = parser.parse_args(argv)
    out = Path(args.out)
    try:
        work_order = json.loads(Path(args.work_order).read_text())
        result = execute(work_order, out)
    except (OSError, json.JSONDecodeError, ValueError, ResearchBlocked):
        out.mkdir(parents=True, exist_ok=True)
        (out / 'evolution-research-error.json').write_text(json.dumps({
            'status': 'research_blocked',
            'error': 'trusted_research_failed',
        }, sort_keys=True) + '\n')
        return 1
    print(json.dumps({'status': result['status'], 'candidate_id': result['candidate_id']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())

This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
test_production_os_server_integration.py
```

# Files

## File: test_production_os_server_integration.py
```python
"""Exercise the worker against Production-OS's real authenticated HTTP API.

The dedicated CI job installs the pinned server and requires these tests.
The runner executes a deterministic Python artifact; no live LLM is involved.
"""
⋮----
ControlPlane = None
⋮----
@unittest.skipIf(ControlPlane is None, 'Production-OS installed by dedicated integration CI')
class RealServerWorkerTests(unittest.TestCase)
⋮----
def test_worker_only_session_executes_and_reports_real_workflow(self)
⋮----
def test_unreadable_result_is_reported_to_real_server(self)
⋮----
def _exercise(self, expected)
⋮----
root = Path(td)
auth = TokenAuthorizer([{
control = ControlPlane(str(root / 'state.sqlite'), authorizer=auth)
workflow = control.workflows.create(
jobs = control.workflows.dispatch_ready(workflow['id'])
⋮----
server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(control))
thread = threading.Thread(target=server.serve_forever, daemon=True)
⋮----
client = ProductionOSClient(f'http://127.0.0.1:{server.server_port}',
# No operator token: validates real /v1/workers/session permissions.
⋮----
executed = []
def runner(request_path, project_out, **kwargs)
⋮----
artifact = project_out / 'verify.py'
⋮----
proc = subprocess.run([sys.executable, str(artifact)], check=True,
⋮----
result = run_once(client, worker_id='github-actions-worker',
⋮----
current = control.workflows.get(workflow['id'])
```

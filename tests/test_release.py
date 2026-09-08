import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "studio"))
from release import build_release


class FakeSandbox:
    def __init__(self, root, fail_at=None):
        self.root = root
        self.fail_at = fail_at
        self.calls = []

    def run(self, args, network=False, timeout=0):
        self.calls.append((args, network, timeout))
        if self.fail_at == len(self.calls):
            return 1, "failed"
        if args[:3] == ["flutter", "build", "appbundle"]:
            p = self.root / "build/app/outputs/bundle/release/app-release.aab"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"a" * 2000)
        return 0, "ok"


def test_release_build_collects_hash_and_size(tmp_path):
    result = build_release(tmp_path, FakeSandbox(tmp_path))
    assert result["passed"] is True
    assert result["artifact"] == "app-release.aab"
    assert result["bytes"] == 2000
    assert len(result["sha256"]) == 64


def test_release_build_stops_on_first_failure(tmp_path):
    sandbox = FakeSandbox(tmp_path, fail_at=2)
    result = build_release(tmp_path, sandbox)
    assert result["passed"] is False
    assert len(sandbox.calls) == 2
    assert len(result["logs"]) == 2

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from quick_gate_cache import cache_key, delta_hash, workspace_hash


class QuickGateCacheTests(unittest.TestCase):
    def test_same_delta_and_workspace_produce_same_key(self):
        files = [{"path": "lib/app.dart", "content": "a"}]
        snapshot = {"lib/app.dart": "a", "pubspec.yaml": "name: demo\n"}
        d1 = delta_hash(files)
        d2 = delta_hash(list(reversed(files)))
        w1 = workspace_hash(snapshot)
        w2 = workspace_hash(dict(reversed(list(snapshot.items()))))
        self.assertEqual(d1, d2)
        self.assertEqual(w1, w2)
        self.assertEqual(
            cache_key(d1, "analyze", [], workspace_digest=w1),
            cache_key(d2, "analyze", [], workspace_digest=w2),
        )

    def test_same_delta_on_different_workspace_does_not_collide(self):
        files = [{"path": "lib/app.dart", "content": "a"}]
        digest = delta_hash(files)
        w1 = workspace_hash({
            "lib/app.dart": "a",
            "lib/other.dart": "const x = 1;\n",
        })
        w2 = workspace_hash({
            "lib/app.dart": "a",
            "lib/other.dart": "const x = 2;\n",
        })
        self.assertNotEqual(
            cache_key(digest, "analyze", [], workspace_digest=w1),
            cache_key(digest, "analyze", [], workspace_digest=w2),
        )

    def test_test_targets_are_part_of_cache_key(self):
        digest = delta_hash([{"path": "lib/app.dart", "content": "a"}])
        workspace = workspace_hash({"lib/app.dart": "a"})
        self.assertNotEqual(
            cache_key(digest, "test", ["test/a_test.dart"], workspace_digest=workspace),
            cache_key(digest, "test", ["test/b_test.dart"], workspace_digest=workspace),
        )


if __name__ == "__main__":
    unittest.main()

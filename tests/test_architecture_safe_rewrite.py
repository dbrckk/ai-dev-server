import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_safe_rewrite as safe


class ArchitectureSafeRewriteTests(unittest.TestCase):
    def test_context_contains_bounded_rewrite_contract(self):
        patch = {"files": [
            {"path": "pubspec.yaml", "content": "dependencies:\n  go_router: ^1.0.0\n"},
            {"path": "lib/router.dart", "content": "import 'package:go_router/go_router.dart';\n" + "x" * 2000},
        ]}
        context = safe.build_context(
            "BASE",
            patch,
            "blocked",
            engine="flutter",
        )
        self.assertIn("ARCHITECTURE_SAFE_REWRITE", context)
        self.assertIn("Preserve the existing architecture", context)
        self.assertIn("pubspec.yaml", context)
        self.assertLess(len(context), 5000)

    def test_patch_summary_is_file_count_bounded(self):
        patch = {
            "files": [
                {"path": f"src/{i}.py", "content": "x" * 2000}
                for i in range(30)
            ]
        }
        context = safe.build_context("BASE", patch, "blocked", engine="generic")
        payload = json.loads(context.split("ARCHITECTURE_SAFE_REWRITE:\n", 1)[1])
        rows = payload["architecture_safe_rewrite"]["rejected_patch_summary"]
        self.assertEqual(len(rows), safe.MAX_REJECTED_FILES)
        self.assertTrue(all(len(row["content_preview"]) <= safe.MAX_CONTENT_PREVIEW for row in rows))


if __name__ == "__main__":
    unittest.main()

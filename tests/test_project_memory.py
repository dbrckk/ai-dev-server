import json
from pathlib import Path
import tempfile
import unittest

from studio.project_memory import MemoryError, add_entry, load, new_memory, query, reusable_for_project, save


class ProjectMemoryTests(unittest.TestCase):
    def make_entry(self, memory, **overrides):
        data = {
            "entry_id": "e1",
            "kind": "experience",
            "project_id": "app-a",
            "summary": "Godot Android export requires target API evidence before release.",
            "tags": ["godot", "android", "release"],
            "evidence": {"tests": "passed", "commit": "a" * 40},
            "provenance": {"source": "validated_ci"},
            "reusable": True,
            "confidence": 95,
        }
        data.update(overrides)
        return add_entry(memory, **data)

    def test_reusable_memory_requires_evidence_provenance_and_high_confidence(self):
        with self.assertRaisesRegex(MemoryError, "high confidence"):
            self.make_entry(new_memory(), confidence=79)
        with self.assertRaisesRegex(MemoryError, "evidence"):
            self.make_entry(new_memory(), evidence={})
        with self.assertRaisesRegex(MemoryError, "provenance"):
            self.make_entry(new_memory(), provenance={})

    def test_query_scopes_project_kind_and_tags(self):
        memory = self.make_entry(new_memory())
        memory = add_entry(
            memory,
            entry_id="e2",
            kind="research",
            project_id="app-a",
            summary="Official billing docs reviewed.",
            tags=["billing", "android"],
            evidence={"content_sha256": "b" * 64},
            provenance={"source": "developer.android.com"},
            reusable=False,
            confidence=100,
        )
        self.assertEqual([x["id"] for x in query(memory, project_id="app-a", kind="research")], ["e2"])
        self.assertEqual([x["id"] for x in query(memory, tags=["godot", "release"])], ["e1"])

    def test_cross_project_reuse_excludes_same_project(self):
        memory = self.make_entry(new_memory())
        memory = self.make_entry(memory, entry_id="e2", project_id="app-b", summary="Reusable second lesson.")
        items = reusable_for_project(memory, "app-b", tags=["godot"])
        self.assertEqual([x["id"] for x in items], ["e1"])

    def test_non_reusable_research_never_crosses_projects(self):
        memory = add_entry(
            new_memory(),
            entry_id="r1",
            kind="research",
            project_id="app-a",
            summary="Candidate package needs more validation.",
            tags=["billing"],
            evidence={"hash": "c" * 64},
            provenance={"source": "pub.dev"},
            reusable=False,
            confidence=100,
        )
        self.assertEqual(reusable_for_project(memory, "app-b"), [])

    def test_duplicate_id_rejected(self):
        memory = self.make_entry(new_memory())
        with self.assertRaisesRegex(MemoryError, "already exists"):
            self.make_entry(memory)

    def test_persistence_detects_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "memory.json"
            memory = self.make_entry(new_memory())
            save(path, memory)
            self.assertEqual(load(path), memory)
            value = json.loads(path.read_text())
            value["entries"][0]["summary"] = "tampered"
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(MemoryError, "integrity"):
                load(path)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import json,os,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from learning_context import augment,load_context

class LearningContextTests(unittest.TestCase):
    def test_bounded_valid_context_is_injected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ctx.json"
            path.write_text(json.dumps([{"summary":"Use deterministic node names","tags":["godot"],"same_project":False,"provenance":{"source":"validated_project_execution"}}]))
            old=os.environ.get("STUDIO_LEARNED_CONTEXT_PATH"); os.environ["STUDIO_LEARNED_CONTEXT_PATH"]=str(path)
            try:
                items=load_context(); self.assertEqual(len(items),1)
                text=augment("task")
                self.assertIn("Use deterministic node names",text)
                self.assertIn("fallible prior evidence",text)
                # Constrain only the optional memory, never the task text;
                # favour observations from the same Godot project.
                path.write_text(json.dumps([
                    {"summary": "Generic observation " + "x" * 800,
                     "tags": ["generic"], "same_project": False,
                     "provenance": {"source": "old", "metadata": "Y" * 2000}},
                    {"summary": "Jumpy-specific input regression " + "z" * 800,
                     "tags": ["godot", "jumpy", "input", "ui"],
                     "same_project": True,
                     "provenance": {"source": "validated_project_execution"}},
                ]))
                bounded = augment("authoritative full source", max_items=1, max_chars=600)
                self.assertTrue(bounded.startswith("authoritative full source\n\n"))
                self.assertIn("Jumpy-specific input regression", bounded)
                self.assertNotIn("Generic observation", bounded)
                compact = json.loads(bounded.split("overrides it:\n", 1)[1])
                self.assertLessEqual(len(json.dumps(compact, ensure_ascii=False, sort_keys=True)), 600)
                self.assertEqual(len(compact), 1)
                self.assertEqual(compact[0]["tags"], ["godot", "jumpy", "input"])
                self.assertEqual(compact[0]["provenance"]["source"], "validated_project_execution")
                self.assertEqual(
                    augment("authoritative full source", max_items=1, max_chars=10),
                    "authoritative full source",
                )
            finally:
                if old is None: os.environ.pop("STUDIO_LEARNED_CONTEXT_PATH",None)
                else: os.environ["STUDIO_LEARNED_CONTEXT_PATH"]=old

    def test_invalid_or_oversized_context_is_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ctx.json"; path.write_text("x"*70000)
            old=os.environ.get("STUDIO_LEARNED_CONTEXT_PATH"); os.environ["STUDIO_LEARNED_CONTEXT_PATH"]=str(path)
            try: self.assertEqual(load_context(),[]); self.assertEqual(augment("task"),"task")
            finally:
                if old is None: os.environ.pop("STUDIO_LEARNED_CONTEXT_PATH",None)
                else: os.environ["STUDIO_LEARNED_CONTEXT_PATH"]=old

if __name__=="__main__": unittest.main()

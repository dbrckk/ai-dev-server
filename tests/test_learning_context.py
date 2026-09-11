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

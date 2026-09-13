from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from dependency_ledger import DependencyLedgerError, advance, load, new, resume, save, suggestions


class DependencyLedgerTests(unittest.TestCase):
    def test_persists_verified_batch_and_downstream_suggestion(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ledger.json"
            ledger=new("demo","a"*40)
            ledger=advance(ledger,base_sha="b"*40,files=["core.py"])
            save(path,ledger)
            restored=load(path)
            graph={"reverse":{"core.py":["api.py","worker.py"]}}
            info=suggestions(restored,graph)
            self.assertEqual(info["published_batches"],1)
            self.assertEqual(info["last_batch"],["core.py"])
            self.assertEqual(info["next_dependents"],["api.py","worker.py"])

    def test_base_mismatch_resets_ledger(self):
        ledger=advance(new("demo","a"*40),base_sha="b"*40,files=["core.py"])
        restored=resume(ledger,project_id="demo",base_sha="c"*40)
        self.assertEqual(restored["batches"],[])
        self.assertEqual(restored["verified_files"],[])

    def test_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"ledger.json"
            save(path,new("demo","a"*40))
            value=json.loads(path.read_text())
            value["verified_files"]=["evil.py"]
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(DependencyLedgerError,"integrity"):
                load(path)

    def test_batches_are_bounded(self):
        ledger=new("demo","a"*40)
        for i in range(105):
            ledger=advance(ledger,base_sha=f"{i:040x}"[-40:],files=[f"f{i}.py"])
        self.assertEqual(len(ledger["batches"]),100)


if __name__=="__main__":
    unittest.main()

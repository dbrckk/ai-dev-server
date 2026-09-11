import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import API, Model, StudioError, apply_patch
from run import GitHub


class PatchSafetyRebuildTests(unittest.TestCase):
    def test_write_failure_restores_original(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"lib").mkdir()
            target=root/"lib/app.dart"
            target.write_text("original")
            real_replace=os.replace
            calls={"n":0}
            def fail(src,dst):
                calls["n"]+=1
                if calls["n"]==2:
                    raise OSError("disk failure")
                return real_replace(src,dst)
            with patch("core.os.replace",side_effect=fail), self.assertRaises(StudioError):
                apply_patch(root,{"files":[
                    {"path":"lib/app.dart","content":"changed"},
                    {"path":"lib/new.dart","content":"new"},
                ]})
            self.assertEqual(target.read_text(),"original")
            self.assertFalse((root/"lib/new.dart").exists())
            self.assertFalse(list(root.glob(".__studio-patch-*")))

    def test_duplicate_model_keys_are_rejected_with_bounded_repair(self):
        with patch.dict(os.environ,{"STUDIO_API_KEY":"test"},clear=True):
            model=Model(2)
            envelope=lambda text:{"choices":[{"finish_reason":"stop","message":{"content":text}}]}
            model.api.call=Mock(side_effect=[
                envelope('{"passed":false,"passed":true,"blockers":[]}'),
                envelope('{"passed":false,"blockers":["defect"]}'),
            ])
            self.assertEqual(model.ask("review","brief"),{"passed":False,"blockers":["defect"]})
            self.assertEqual(model.calls,2)

    def test_nonfinite_model_number_is_repaired(self):
        with patch.dict(os.environ,{"STUDIO_API_KEY":"test"},clear=True):
            model=Model(2)
            envelope=lambda text:{"choices":[{"finish_reason":"stop","message":{"content":text}}]}
            model.api.call=Mock(side_effect=[
                envelope('{"value":NaN}'),
                envelope('{"value":1.5}'),
            ])
            self.assertEqual(model.ask("design","brief"),{"value":1.5})
            self.assertEqual(model.calls,2)

    def test_checkpoint_metadata_rejects_secret_before_remote_access(self):
        with tempfile.TemporaryDirectory() as td:
            gh=GitHub.__new__(GitHub)
            gh.repo="/repos/example/demo"
            gh.get=Mock(side_effect=AssertionError("remote read"))
            gh.call=Mock(side_effect=AssertionError("remote write"))
            with self.assertRaisesRegex(StudioError,"credential"):
                gh.publish("studio/demo",None,Path(td),{"status":"blocked","detail":"ghp_abcdef123456"})
            gh.get.assert_not_called()
            gh.call.assert_not_called()

    def test_unresolved_recovery_blocks_publication(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/".__studio-patch-leftover").mkdir()
            gh=GitHub.__new__(GitHub)
            gh.repo="/repos/example/demo"
            gh.get=Mock(side_effect=AssertionError("remote read"))
            gh.call=Mock(side_effect=AssertionError("remote write"))
            with self.assertRaises(RuntimeError):
                gh.publish("studio/demo",None,root,{"status":"blocked"})
            gh.get.assert_not_called()
            gh.call.assert_not_called()


if __name__=="__main__":
    unittest.main()

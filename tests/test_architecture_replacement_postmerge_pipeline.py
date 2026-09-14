import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
import architecture_replacement_postmerge_pipeline as pipeline

class ReplacementPostMergePipelineTests(unittest.TestCase):
    def test_healthy_result_records_learning_without_rollback_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            work=root/"work.json"; merged=root/"merged.json"; package=root/"package.json"
            work.write_text(json.dumps({"id":"r1","current_repo":"a/current","replacement_repo":"a/better","risk":"low","scope":"narrow"}))
            merged.write_text(json.dumps({"status":"replacement_merged","work_order_id":"r1","merge_sha":"3"*40}))
            package.write_text(json.dumps({"status":"pr_package_ready","work_order_id":"r1"}))
            post={"status":"post_merge_healthy","work_order_id":"r1","post_merge_healthy":True,"rollback_required":False}
            with patch.object(pipeline,"verify_postmerge",return_value=post):
                result=pipeline.run(work,merged,package,root/"studio-output"/"p1","token","owner/repo")
            self.assertEqual(result["postmerge_status"],"post_merge_healthy")
            self.assertEqual(result["rollback_gate_status"],"not_required")
            self.assertTrue((root/"studio-output"/"p1"/"architecture-replacement-outcome.json").is_file())
            self.assertTrue((root/"studio-output"/"architecture-replacement-learning.json").is_file())

    def test_regression_emits_rollback_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            work=root/"work.json"; merged=root/"merged.json"; package=root/"package.json"
            work.write_text(json.dumps({"id":"r1","current_repo":"a/current","replacement_repo":"a/better"}))
            merged.write_text(json.dumps({"status":"replacement_merged","work_order_id":"r1","merge_sha":"3"*40,"head_sha":"1"*40}))
            package.write_text(json.dumps({"status":"pr_package_ready","work_order_id":"r1","baseline_sha":"0"*40}))
            post={"status":"post_merge_regression","work_order_id":"r1","post_merge_healthy":False,"rollback_required":True,"failed_checks":["validate"],"content_mismatches":[]}
            gate={"status":"rollback_authorization_required"}
            with patch.object(pipeline,"verify_postmerge",return_value=post), patch.object(
                pipeline,"write_rollback_gate",return_value=gate
            ):
                result=pipeline.run(work,merged,package,root/"studio-output"/"p1","token","owner/repo")
            self.assertEqual(result["rollback_gate_status"],"rollback_authorization_required")

    def test_nonterminal_postmerge_does_not_pollute_learning(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            work=root/"work.json"; merged=root/"merged.json"; package=root/"package.json"
            work.write_text(json.dumps({"id":"r1","current_repo":"a/current","replacement_repo":"a/better"}))
            merged.write_text(json.dumps({"status":"replacement_merged","work_order_id":"r1","merge_sha":"3"*40}))
            package.write_text(json.dumps({"status":"pr_package_ready","work_order_id":"r1"}))
            post={"status":"awaiting_post_merge_checks","work_order_id":"r1","post_merge_healthy":False,"rollback_required":False}
            out=root/"studio-output"/"p1"
            with patch.object(pipeline,"verify_postmerge",return_value=post):
                result=pipeline.run(work,merged,package,out,"token","owner/repo")
            self.assertIsNone(result["replacement_outcome"])
            self.assertFalse((out/"architecture-replacement-outcome.json").exists())
            learning=json.loads((root/"studio-output"/"architecture-replacement-learning.json").read_text())
            self.assertEqual(learning["outcomes_observed"],0)

if __name__=="__main__":
    unittest.main()

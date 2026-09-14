import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))

import architecture_replacement_pipeline as arp

class ReplacementPipelineTests(unittest.TestCase):
    def test_pipeline_never_auto_promotes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            order=root/"order.json"
            order.write_text(json.dumps({
                "id":"replace-1",
                "current_repo":"a/current",
                "replacement_repo":"a/better",
            }))
            fake_candidate={
                "status":"replacement_candidate_validated",
                "work_order_id":"replace-1",
            }
            fake_execution={
                "status":"replacement_isolated_benchmark_complete",
                "go_no_go":"GO_FOR_MANUAL_PROMOTION_REVIEW",
            }
            with patch.object(arp,"synthesize_candidate",return_value=fake_candidate), patch.object(
                arp,"execute_candidate",return_value=fake_execution
            ):
                result=arp.run(order,root,root/"out")
            self.assertFalse(result["auto_promoted"])
            self.assertFalse(result["default_branch_modified"])
            self.assertEqual(result["go_no_go"],"GO_FOR_MANUAL_PROMOTION_REVIEW")

if __name__=="__main__":
    unittest.main()

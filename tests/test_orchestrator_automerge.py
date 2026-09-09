import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from orchestrator import _run_adaptation_automerge


class OrchestratorAutoMergeTests(unittest.TestCase):
    def test_github_automerge_uses_local_persistence_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            (out/'evolution-work-order.json').write_text('{}')
            (out/'evolution-persisted.json').write_text('{}')
            calls=[]
            def runner(args,timeout):
                calls.append((args,timeout))
                (out/'evolution-automerge.json').write_text(json.dumps({'status':'promotion_merged'}))
                return subprocess.CompletedProcess(args,0)
            with patch.dict(os.environ,{'STUDIO_CI_PROVIDER':'github'},clear=False):
                status=_run_adaptation_automerge(out,1000,runner,lambda:0)
            self.assertEqual(status,'merged')
            args=calls[0][0]
            self.assertIn('studio/evolution_automerge.py',args)
            self.assertIn(str(out/'evolution-persisted.json'),args)
            self.assertIn('--wait-seconds',args)

    def test_non_github_provider_never_attempts_automerge(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            with patch.dict(os.environ,{'STUDIO_CI_PROVIDER':'circleci'},clear=False):
                status=_run_adaptation_automerge(Path(tmp),100,lambda args,timeout:calls.append(args),lambda:0)
            self.assertEqual(status,'not_applicable')
            self.assertEqual(calls,[])


if __name__=='__main__': unittest.main()

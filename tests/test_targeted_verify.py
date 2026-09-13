from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from targeted_verify import targeted_command, run


class TargetedVerifyTests(unittest.TestCase):
    @patch("targeted_verify.discover")
    def test_builds_pytest_command(self, discover):
        discover.return_value=[["pytest","-q"]]
        cmd=targeted_command(Path("."),["tests/test_api.py"])
        self.assertEqual(cmd,["pytest","-q","tests/test_api.py"])

    @patch("targeted_verify.discover")
    def test_builds_uv_pytest_command(self, discover):
        discover.return_value=[["uv","run","pytest","-q"]]
        cmd=targeted_command(Path("."),["tests/test_api.py"])
        self.assertEqual(cmd,["uv","run","pytest","-q","tests/test_api.py"])

    @patch("targeted_verify.discover")
    def test_unsupported_runner_returns_none(self, discover):
        discover.return_value=[["npm","test"]]
        self.assertIsNone(targeted_command(Path("."),["tests/a.test.ts"]))

    @patch("targeted_verify.run_command")
    @patch("targeted_verify.discover")
    def test_run_is_bounded_and_network_off(self, discover, run_command):
        discover.return_value=[["pytest","-q"]]
        run_command.return_value={"passed":True}
        result=run(Path("."),["tests/test_api.py"],timeout=999)
        self.assertTrue(result["passed"])
        args,kwargs=run_command.call_args
        self.assertEqual(kwargs["timeout"],300)
        self.assertFalse(kwargs["network"])


if __name__=="__main__":
    unittest.main()

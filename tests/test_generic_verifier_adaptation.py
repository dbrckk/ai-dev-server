from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path:
    sys.path.insert(0,str(STUDIO))

from generic_verifier_adaptation import validate_recipe


class GenericVerifierAdaptationTests(unittest.TestCase):
    def test_accepts_safe_available_tool(self):
        with tempfile.TemporaryDirectory() as td, patch("shutil.which", return_value="/usr/bin/python"):
            recipe=validate_recipe({"commands":[["python","-m","unittest","discover"]],"reason":"run unit tests"},Path(td))
        self.assertEqual(recipe["commands"][0][0],"python")

    def test_rejects_shell_command_string(self):
        with tempfile.TemporaryDirectory() as td, patch("shutil.which", return_value="/bin/bash"):
            with self.assertRaises(ValueError):
                validate_recipe({"commands":[["bash","-c","echo hacked"]],"reason":"bad"},Path(td))

    def test_rejects_install_operation(self):
        with tempfile.TemporaryDirectory() as td, patch("shutil.which", return_value="/usr/bin/npm"):
            with self.assertRaises(ValueError):
                validate_recipe({"commands":[["npm","install"]],"reason":"bad"},Path(td))


if __name__=="__main__":
    unittest.main()

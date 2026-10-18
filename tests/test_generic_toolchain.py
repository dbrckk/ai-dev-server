from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]; STUDIO=ROOT/"studio"
if str(STUDIO) not in sys.path: sys.path.insert(0,str(STUDIO))
from generic_toolchain import bootstrap_commands,detect
from generic_verify import discover as discover_verifiers
from generic_sandbox import safe_env

class GenericToolchainTests(unittest.TestCase):
    def test_detects_node_and_python(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"package.json").write_text("{}"); (root/"pyproject.toml").write_text("[project]\nname='x'\n")
            self.assertEqual(detect(root)["stacks"],["node","python"])

        # A real pytest-configured repository must not fall back to
        # unittest discovery (which may return zero tests).
        with tempfile.TemporaryDirectory() as td, patch(
            "generic_verify.shutil.which",
            side_effect=lambda name: "/usr/bin/python" if name == "python" else None,
        ):
            root = Path(td)
            (root/"pyproject.toml").write_text(
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
                encoding="utf-8",
            )
            self.assertEqual(discover_verifiers(root), [["python", "-m", "pytest", "-q"]])
            venv = root/".studio-venv/bin/python"
            venv.parent.mkdir(parents=True)
            venv.write_text("", encoding="utf-8")
            self.assertEqual(discover_verifiers(root), [[str(venv), "-m", "pytest", "-q"]])
            venv.unlink()
            (root/"pyproject.toml").write_text(
                '[project]\nname = "unittest-project"\n', encoding="utf-8",
            )
            self.assertEqual(discover_verifiers(root), [["python", "-m", "unittest", "discover"]])

    def test_npm_bootstrap_is_lockfile_bound_and_ignores_scripts(self):
        with tempfile.TemporaryDirectory() as td, patch("shutil.which", return_value="/usr/bin/npm"):
            root=Path(td); (root/"package.json").write_text("{}"); (root/"package-lock.json").write_text("{}")
            cmd=bootstrap_commands(root)[0]
            self.assertEqual(cmd[:2],["npm","ci"]); self.assertIn("--ignore-scripts",cmd)
    def test_safe_env_drops_studio_and_github_secrets(self):
        with patch.dict("os.environ",{"PATH":"/bin","STUDIO_API_KEY":"x","GITHUB_TOKEN":"y","HOME":"/tmp"},clear=True):
            env=safe_env()
        self.assertNotIn("STUDIO_API_KEY",env); self.assertNotIn("GITHUB_TOKEN",env)

if __name__=="__main__": unittest.main()

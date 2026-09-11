import tempfile
import time
import unittest
from pathlib import Path

from studio.capability_registry import new_registry, register
from studio.capability_runtime import CapabilityRuntimeError, execute_capability


class CapabilityRuntimeTests(unittest.TestCase):
    def make_provider(self, root, name, source):
        path=Path(root)/"studio/capabilities"/(name+".py")
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(source)
        return path

    def registry(self, provider):
        return register(
            new_registry(),
            "demo.capability",
            provider,
            {"source":"promoted_factory_capability","candidate_sha":"a"*40},
        )

    def test_executes_registered_provider(self):
        with tempfile.TemporaryDirectory() as td:
            self.make_provider(td,"demo_capability",
                "def run(context):\n    return {'status':'ok','echo':context['value']}\n")
            result=execute_capability(
                self.registry("studio.capabilities.demo_capability"),
                "demo.capability",
                {"value":7},
                repo_root=td,
            )
            self.assertEqual(result,{"status":"ok","echo":7})

    def test_missing_or_symlink_provider_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(CapabilityRuntimeError,"unavailable"):
                execute_capability(
                    self.registry("studio.capabilities.demo_capability"),
                    "demo.capability",{},repo_root=td,
                )

    def test_provider_must_expose_run(self):
        with tempfile.TemporaryDirectory() as td:
            self.make_provider(td,"demo_capability","VALUE=1\n")
            with self.assertRaisesRegex(CapabilityRuntimeError,"callable run"):
                execute_capability(
                    self.registry("studio.capabilities.demo_capability"),
                    "demo.capability",{},repo_root=td,
                )

    def test_timeout_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            self.make_provider(td,"demo_capability",
                "import time\ndef run(context):\n    time.sleep(2)\n    return {'status':'late'}\n")
            with self.assertRaisesRegex(CapabilityRuntimeError,"timed out"):
                execute_capability(
                    self.registry("studio.capabilities.demo_capability"),
                    "demo.capability",{},repo_root=td,timeout_seconds=1,
                )

    def test_non_json_result_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            self.make_provider(td,"demo_capability",
                "def run(context):\n    return {'bad': float('nan')}\n")
            with self.assertRaisesRegex(CapabilityRuntimeError,"valid JSON"):
                execute_capability(
                    self.registry("studio.capabilities.demo_capability"),
                    "demo.capability",{},repo_root=td,
                )

    def test_unregistered_capability_cannot_execute(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(CapabilityRuntimeError,"not registered"):
                execute_capability(new_registry(),"missing",{},repo_root=td)


if __name__=="__main__":
    unittest.main()

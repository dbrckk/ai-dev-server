import json
from pathlib import Path
import tempfile
import unittest

from studio.capability_registry import new_registry, register
from studio.promoted_capabilities import PromotedCapabilityError, load, provider_for, sync_into_registry


class PromotedCapabilitiesTests(unittest.TestCase):
    def write(self, root, capabilities):
        path = root / "promoted_capabilities.json"
        path.write_text(json.dumps({"version": 1, "capabilities": capabilities}))
        return path

    def entry(self, name):
        return {
            "provider": provider_for(name),
            "candidate_id": "candidate-1",
            "baseline_sha": "a" * 40,
            "candidate_sha": "b" * 40,
        }

    def test_missing_registry_is_empty(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(load(Path(td) / "missing.json"), {"version": 1, "capabilities": {}})

    def test_provider_path_is_deterministic(self):
        self.assertEqual(provider_for("improvement.apply.repeated_failure"),
                         "studio.capabilities.improvement_apply_repeated_failure")

    def test_promoted_capability_bootstraps_project_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); name="improvement.apply.repeated_failure"
            provider_file=root/"studio/capabilities/improvement_apply_repeated_failure.py"
            provider_file.parent.mkdir(parents=True)
            provider_file.write_text("def provide():\n    return True\n")
            registry=sync_into_registry(
                new_registry(), self.write(root,{name:self.entry(name)}), repo_root=root
            )
            self.assertEqual(registry["capabilities"][name]["provider"],provider_for(name))
            self.assertEqual(registry["capabilities"][name]["evidence"]["source"],"promoted_factory_capability")

    def test_provider_redirect_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); name="improvement.apply.repeated_failure"; entry=self.entry(name)
            entry["provider"]="studio.orchestrator"
            with self.assertRaisesRegex(PromotedCapabilityError,"provider mismatch"):
                load(self.write(root,{name:entry}))

    def test_project_provider_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); name="improvement.verify.repeated_failure"
            provider_file=root/"studio/capabilities/improvement_verify_repeated_failure.py"
            provider_file.parent.mkdir(parents=True)
            provider_file.write_text("def provide():\n    return True\n")
            registry=register(new_registry(),name,"studio.other_provider",{"tests":"passed"})
            with self.assertRaisesRegex(PromotedCapabilityError,"conflicts"):
                sync_into_registry(
                    registry,self.write(root,{name:self.entry(name)}),repo_root=root
                )

    def test_missing_provider_implementation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); name="improvement.apply.repeated_failure"
            with self.assertRaisesRegex(PromotedCapabilityError,"implementation missing"):
                sync_into_registry(
                    new_registry(),self.write(root,{name:self.entry(name)}),repo_root=root
                )

    def test_symlink_provider_implementation_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); name="improvement.apply.repeated_failure"
            outside=root/"outside.py"; outside.write_text("def provide(): return True\n")
            provider_file=root/"studio/capabilities/improvement_apply_repeated_failure.py"
            provider_file.parent.mkdir(parents=True)
            provider_file.symlink_to(outside)
            with self.assertRaisesRegex(PromotedCapabilityError,"implementation missing"):
                sync_into_registry(
                    new_registry(),self.write(root,{name:self.entry(name)}),repo_root=root
                )


if __name__=="__main__":
    unittest.main()

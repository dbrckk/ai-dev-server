import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import architecture_contract


class ArchitectureContractTests(unittest.TestCase):
    def test_contract_is_valid(self):
        report = architecture_contract.validate()
        self.assertTrue(report["valid"], report["failures"])
        self.assertEqual(report["failures"], [])
        self.assertFalse(report["policy"]["automatic_dependency_addition"])
        self.assertFalse(report["policy"]["automatic_migration"])
        self.assertLessEqual(
            report["policy"]["max_feedback_age_seconds"],
            90 * 24 * 60 * 60,
        )
        self.assertEqual(
            report["policy"]["context_dimensions"],
            ["framework", "project_type", "primary_domain"],
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from studio.capability_registry import new_registry, register
from studio.improvement_dispatch import dispatch, required_verifier_capability


class ImprovementDispatchTests(unittest.TestCase):
    def test_warning_uses_builtin_verifier(self):
        candidate={"kind":"persistent_warning"}
        result=dispatch(candidate,new_registry())
        self.assertEqual(result["decision"],"execute")
        self.assertEqual(result["verifier"],"builtin")

    def test_repeated_failure_requires_adaptable_verifier_capability(self):
        candidate={"kind":"repeated_failure"}
        result=dispatch(candidate,new_registry())
        self.assertEqual(result["decision"],"adapt")
        self.assertEqual(result["missing_capability"],"improvement.verify.repeated_failure")

    def test_registered_verifier_allows_execution(self):
        registry=register(
            new_registry(),
            "improvement.verify.repeated_failure",
            "studio.repeated_failure_verifier",
            {"tests":"passed","regression":"passed"},
        )
        result=dispatch({"kind":"repeated_failure"},registry)
        self.assertEqual(result["decision"],"execute")
        self.assertEqual(result["verifier"],"studio.repeated_failure_verifier")

    def test_capability_churn_has_distinct_verifier(self):
        self.assertEqual(
            required_verifier_capability({"kind":"capability_churn"}),
            "improvement.verify.capability_churn",
        )


if __name__=="__main__":
    unittest.main()

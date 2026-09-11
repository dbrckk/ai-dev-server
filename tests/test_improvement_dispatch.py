import unittest

from studio.capability_registry import new_registry, register
from studio.improvement_dispatch import dispatch, required_verifier_capability


def add(registry,name,provider):
    return register(registry,name,provider,{"tests":"passed","regression":"passed"})


class ImprovementDispatchTests(unittest.TestCase):
    def test_warning_requires_applicator_even_with_builtin_verifier(self):
        candidate={"kind":"persistent_warning"}
        result=dispatch(candidate,new_registry())
        self.assertEqual(result["decision"],"adapt")
        self.assertEqual(result["missing_capability"],"improvement.apply.persistent_warning")

    def test_warning_executes_with_registered_applicator_and_builtin_verifier(self):
        registry=add(new_registry(),"improvement.apply.persistent_warning","studio.warning_improver")
        result=dispatch({"kind":"persistent_warning"},registry)
        self.assertEqual(result["decision"],"execute")
        self.assertEqual(result["applicator"],"studio.warning_improver")
        self.assertEqual(result["verifier"],"builtin")

    def test_repeated_failure_requires_applicator_before_verifier(self):
        candidate={"kind":"repeated_failure"}
        result=dispatch(candidate,new_registry())
        self.assertEqual(result["decision"],"adapt")
        self.assertEqual(result["missing_capability"],"improvement.apply.repeated_failure")

    def test_repeated_failure_then_requires_verifier(self):
        registry=add(new_registry(),"improvement.apply.repeated_failure","studio.failure_improver")
        result=dispatch({"kind":"repeated_failure"},registry)
        self.assertEqual(result["decision"],"adapt")
        self.assertEqual(result["applicator"],"studio.failure_improver")
        self.assertEqual(result["missing_capability"],"improvement.verify.repeated_failure")

    def test_registered_applicator_and_verifier_allow_execution(self):
        registry=add(new_registry(),"improvement.apply.repeated_failure","studio.failure_improver")
        registry=add(registry,"improvement.verify.repeated_failure","studio.repeated_failure_verifier")
        result=dispatch({"kind":"repeated_failure"},registry)
        self.assertEqual(result["decision"],"execute")
        self.assertEqual(result["applicator"],"studio.failure_improver")
        self.assertEqual(result["verifier"],"studio.repeated_failure_verifier")

    def test_capability_churn_has_distinct_verifier(self):
        self.assertEqual(
            required_verifier_capability({"kind":"capability_churn"}),
            "improvement.verify.capability_churn",
        )


if __name__=="__main__":
    unittest.main()

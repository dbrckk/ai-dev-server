import unittest

from studio.capability_synthesis import CapabilitySynthesisError, synthesize_candidate
from studio.memory_bridge import remember_research
from studio.project_memory import new_memory


def memory_with_research():
    research={
        "status":"research_complete",
        "candidate_id":"capability:image_assets",
        "items":[
            {
                "kind":"docs","source":"https://docs.example.com/a","notes":"official constraints",
                "content_sha256":"a"*64,
            },
            {
                "kind":"security","source":"https://security.example.org/b","notes":"security constraints",
                "content_sha256":"b"*64,
            },
        ],
    }
    return remember_research(new_memory(),"project-a",research)


class CapabilitySynthesisTests(unittest.TestCase):
    def synth(self, context):
        return {
            "provider":"studio.capabilities.image_assets",
            "implementation":"def provide():\n    return {'ok': True}\n",
            "tests":"def test_provider():\n    assert True\n",
            "risk_notes":["Requires sandbox validation"],
        }

    def test_candidate_is_synthesized_but_never_promoted(self):
        result=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
        self.assertEqual(result["status"],"candidate_synthesized")
        self.assertEqual(result["benchmark_status"],"required")
        self.assertEqual(result["regression_status"],"required")
        self.assertEqual(result["promotion_status"],"not_ready")
        self.assertFalse(result["capability_registered"])
        self.assertEqual(len(result["candidate"]["research"]),2)
        self.assertEqual(len(result["candidate_sha256"]),64)

    def test_same_inputs_are_deterministically_sealed(self):
        one=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
        two=synthesize_candidate(memory_with_research(),"project-a","image_assets",self.synth)
        self.assertEqual(one["candidate_sha256"],two["candidate_sha256"])
        self.assertEqual(one["candidate_id"],two["candidate_id"])

    def test_missing_research_fails_closed(self):
        with self.assertRaisesRegex(CapabilitySynthesisError,"insufficient"):
            synthesize_candidate(new_memory(),"project-a","image_assets",self.synth)

    def test_arbitrary_provider_redirect_is_rejected(self):
        def bad(context):
            value=self.synth(context)
            value["provider"]="studio.orchestrator"
            return value
        with self.assertRaisesRegex(CapabilitySynthesisError,"provider"):
            synthesize_candidate(memory_with_research(),"project-a","image_assets",bad)

    def test_candidate_cannot_smuggle_extra_control_fields(self):
        def bad(context):
            value=self.synth(context)
            value["promotion_status"]="ready"
            return value
        with self.assertRaisesRegex(CapabilitySynthesisError,"fields"):
            synthesize_candidate(memory_with_research(),"project-a","image_assets",bad)


if __name__=="__main__":
    unittest.main()

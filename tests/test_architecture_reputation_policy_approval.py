import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"studio"))
from architecture_reputation_policy_approval import *

class ApprovalProvenanceTests(unittest.TestCase):
    def approval(self,reinforced=False):
        a={"migration_id":"m1","review_digest":"r1","reviewer":{"id":"alice","roles":["reviewer"]}}
        if reinforced:a["second_reviewer"]={"id":"bob","roles":["risk_owner"]}
        a["approval_digest"]=approval_digest(a)
        return a
    def test_standard_approval(self):
        self.assertEqual(validate_approval(self.approval(),{"migration_id":"m1","review_digest":"r1"},reinforced=False)["reviewer_id"],"alice")
    def test_reinforced_requires_separation(self):
        a=self.approval(True);a["second_reviewer"]["id"]="alice";a["approval_digest"]=approval_digest(a)
        with self.assertRaises(ApprovalProvenanceError):validate_approval(a,{"migration_id":"m1","review_digest":"r1"},reinforced=True)
    def test_reinforced_accepts_distinct_risk_owner(self):
        self.assertEqual(validate_approval(self.approval(True),{"migration_id":"m1","review_digest":"r1"},reinforced=True)["second_reviewer_id"],"bob")
    def test_ledger_is_append_only_and_replay_safe(self):
        a=self.approval();ledger=consume(None,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=1)
        self.assertTrue(validate_ledger(ledger)["valid"])
        with self.assertRaises(ApprovalProvenanceError):consume(ledger,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=2)
    def test_tampered_ledger_fails(self):
        a=self.approval();ledger=consume(None,migration_id="m1",review_digest="r1",approval_digest_value=a["approval_digest"],applied_at=1)
        ledger=copy.deepcopy(ledger);ledger["events"][0]["applied_at"]=99
        self.assertFalse(validate_ledger(ledger)["valid"])

if __name__=="__main__":unittest.main()

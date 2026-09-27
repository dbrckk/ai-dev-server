import unittest
from studio.capability_review import CapabilityReviewError, inspect

REVIEW={
    "status":"candidate_persisted",
    "candidate_id":"candidate:a",
    "candidate_sha256":"a"*64,
    "capability":"image_assets",
    "branch":"capability/candidate-image_assets-deadbeef-"+"b"*40,
    "commit_sha":"b"*40,
    "pull_request":17,
}

class GitHub:
    def __init__(self,pr,runs=None,statuses=None):
        self.pr=pr
        self.runs=[] if runs is None else runs
        self.statuses=[] if statuses is None else statuses
    def get(self,path):
        if path=="/pulls/17": return self.pr
        if path.startswith("/actions/runs?head_sha="):
            return {"workflow_runs":self.runs}
        if path=="/commits/"+REVIEW["commit_sha"]+"/status":
            return {"statuses":self.statuses}
        raise AssertionError(path)

def pr(state="open",merged=False):
    return {
        "state":state,
        "merged":merged,
        "merged_at":"2026-09-12T00:00:00Z" if merged else None,
        "merge_commit_sha":"c"*40 if merged else None,
        "base":{"ref":"main"},
        "head":{"ref":REVIEW["branch"],"sha":REVIEW["commit_sha"]},
    }

class CapabilityReviewTests(unittest.TestCase):
    def test_open_exact_pr_remains_pending(self):
        self.assertEqual(inspect(GitHub(pr()),REVIEW)["status"],"candidate_review_pending")

    def test_open_exact_pr_reports_ready_when_all_checks_pass(self):
        result=inspect(
            GitHub(
                pr(),
                runs=[{"name":"CI","status":"completed","conclusion":"success"}],
                statuses=[{"context":"circleci/smoke","state":"success"}],
            ),
            REVIEW,
        )
        self.assertEqual(result["status"],"candidate_review_ready")
        self.assertEqual(result["checks"]["state"],"ready")

    def test_open_exact_pr_reports_failed_when_check_fails(self):
        result=inspect(
            GitHub(
                pr(),
                runs=[{"name":"CI","status":"completed","conclusion":"failure"}],
            ),
            REVIEW,
        )
        self.assertEqual(result["status"],"candidate_review_failed")
        self.assertEqual(result["checks"]["state"],"failed")


    def test_merged_exact_pr_reports_merge_commit_without_promoting(self):
        result=inspect(GitHub(pr(state="closed",merged=True)),REVIEW)
        self.assertEqual(result["status"],"candidate_merged")
        self.assertEqual(result["merge_commit_sha"],"c"*40)

    def test_closed_unmerged_pr_is_rejected(self):
        self.assertEqual(inspect(GitHub(pr(state="closed")),REVIEW)["status"],"candidate_review_rejected")

    def test_changed_head_fails_closed(self):
        value=pr(); value["head"]["sha"]="d"*40
        with self.assertRaisesRegex(CapabilityReviewError,"identity changed"):
            inspect(GitHub(value),REVIEW)

    def test_changed_base_fails_closed(self):
        value=pr(); value["base"]["ref"]="release"
        with self.assertRaisesRegex(CapabilityReviewError,"base changed"):
            inspect(GitHub(value),REVIEW)


if __name__=="__main__":
    unittest.main()

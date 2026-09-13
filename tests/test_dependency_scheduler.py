from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from dependency_scheduler import hotspot_plan, patch_batch_guard, schedule


class DependencySchedulerTests(unittest.TestCase):
    def test_dependency_is_scheduled_before_consumer(self):
        graph={"edges":{"api.py":["core.py"],"core.py":[]},"reverse":{}}
        result=schedule(graph,["api.py","core.py"],max_batch_files=2)
        self.assertEqual(result["batches"],[["core.py"],["api.py"]])

    def test_independent_files_share_batch(self):
        graph={"edges":{"a.py":[],"b.py":[]},"reverse":{}}
        result=schedule(graph,["a.py","b.py"],max_batch_files=2)
        self.assertEqual(result["batches"],[["a.py","b.py"]])

    def test_cycle_is_split_into_singletons(self):
        graph={"edges":{"a.py":["b.py"],"b.py":["a.py"]},"reverse":{}}
        result=schedule(graph,["a.py","b.py"],max_batch_files=2)
        self.assertEqual(result["cyclic"],["a.py","b.py"])
        self.assertEqual(result["batches"],[["a.py"],["b.py"]])

    def test_guard_rejects_patch_spanning_batches(self):
        graph={"edges":{"api.py":["core.py"],"core.py":[]},"reverse":{}}
        result=patch_batch_guard(graph,["api.py","core.py"],max_batch_files=2)
        self.assertTrue(result["reject"])
        self.assertEqual(result["batch_count"],2)

    def test_hotspot_plan_orders_by_coupling(self):
        graph={
            "edges":{"core.py":[],"leaf.py":[]},
            "reverse":{"core.py":["a.py","b.py","c.py"],"leaf.py":[]},
        }
        result=hotspot_plan(graph,max_batch_files=3)
        self.assertEqual(result["hotspots"][0]["path"],"core.py")
        self.assertEqual(result["recommended_batch_files"],3)


if __name__=="__main__":
    unittest.main()

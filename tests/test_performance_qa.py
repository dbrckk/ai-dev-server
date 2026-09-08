from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
from performance_qa import _parse_gfxinfo
from stage_registry import get_stage


class PerformanceQATests(unittest.TestCase):
    def test_parse_gfxinfo_computes_frame_metrics(self):
        sample = '''Profile data in ms:\n\nDraw,Prepare,Process,Execute\n1,1,1,1\n2,2,2,2\n10,10,10,10\n20,20,20,20\n'''
        metrics = _parse_gfxinfo(sample)
        self.assertEqual(metrics['frame_count'], 4)
        self.assertEqual(metrics['janky_frames'], 2)
        self.assertEqual(metrics['jank_ratio'], 0.5)
        self.assertEqual(metrics['max_ms'], 80.0)

    def test_empty_gfxinfo_fails_closed_upstream(self):
        metrics = _parse_gfxinfo('no profile data')
        self.assertEqual(metrics['frame_count'], 0)
        self.assertIsNone(metrics['jank_ratio'])

    def test_performance_stage_is_registered(self):
        stage = get_stage('performance_qa')
        self.assertIsNotNone(stage)
        self.assertEqual(stage.script, 'studio/performance_stage.py')
        self.assertEqual(stage.failed_status, 'performance_failed')


if __name__ == '__main__':
    unittest.main()

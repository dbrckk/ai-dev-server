from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))

from godot_runtime_journeys import HARNESS,run_journeys

JOURNEYS=[{'id':'open_settings','steps':[{'action':'tap','key':'settings_button'},{'action':'expect_text','value':'Settings'}]}]

class GodotRuntimeJourneyTests(unittest.TestCase):
    def setup(self,root):
        project=root/'project'; project.mkdir(); (project/'project.godot').write_text('[application]\nrun/main_scene="res://Main.tscn"\n'); (project/'Main.tscn').write_text('x')
        binary=root/'godot'; binary.write_bytes(b'godot'); digest=hashlib.sha256(binary.read_bytes()).hexdigest(); (root/'godot.sha256').write_text(digest); binary.chmod(0o755)
        return project,binary

    def test_harness_uses_json_data_and_unique_node_names(self):
        self.assertIn('JSON.parse_string',HARNESS)
        self.assertIn('String(node.name) == key',HARNESS)
        self.assertNotIn('eval(',HARNESS)
        self.assertNotIn('load(String(step',HARNESS)

    def test_success_requires_every_exact_journey_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project,binary=self.setup(root); seen={}
            def runner(command,**kwargs):
                seen['command']=command
                return subprocess.CompletedProcess(command,0,b'STUDIO_JOURNEY_PASS:open_settings\nSTUDIO_JOURNEYS_COMPLETE:1\n')
            result=run_journeys(project,binary,JOURNEYS,runner=runner)
        self.assertTrue(result['passed']); self.assertTrue(result['journeys_executed'])
        self.assertIn('--network=none',seen['command'])
        self.assertFalse(any(str(project.resolve())==part.split(':',1)[0] for part in seen['command'] if ':/' in part))

    def test_missing_or_failed_marker_fails_closed(self):
        outputs=[b'STUDIO_JOURNEYS_COMPLETE:1\n',b'STUDIO_JOURNEY_FAIL:open_settings:expected_text_missing\n']
        for output in outputs:
            with self.subTest(output=output):
                with tempfile.TemporaryDirectory() as td:
                    root=Path(td); project,binary=self.setup(root)
                    def runner(command,**kwargs): return subprocess.CompletedProcess(command,1 if b'FAIL' in output else 0,output)
                    result=run_journeys(project,binary,JOURNEYS,runner=runner)
                self.assertFalse(result['passed']); self.assertFalse(result['journeys_executed'])

    def test_host_credentials_are_not_forwarded(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project,binary=self.setup(root); captured={}
            def runner(command,**kwargs):
                captured['env']=kwargs['env']; return subprocess.CompletedProcess(command,0,b'STUDIO_JOURNEY_PASS:open_settings\nSTUDIO_JOURNEYS_COMPLETE:1\n')
            with patch.dict('os.environ',{'PATH':'/bin','HOME':'/tmp','GITHUB_TOKEN':'secret','STUDIO_GITHUB_TOKEN':'secret'},clear=True):
                run_journeys(project,binary,JOURNEYS,runner=runner)
        self.assertEqual(captured['env'],{'PATH':'/bin','HOME':'/tmp'})

if __name__=='__main__': unittest.main()

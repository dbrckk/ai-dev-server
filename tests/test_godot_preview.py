import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

import godot_preview
from core import StudioError


def blob(text):
    raw=text.encode(); return {'encoding':'base64','content':base64.b64encode(raw).decode()}, len(raw)


class FakeGitHub:
    def __init__(self):
        self.repo='/repos/dbrckk/Jumpy'; self.parent='a'*40; self.branch_head=None; self.states=[]
        self.project_blob,self.project_size=blob('[application]\n')
        self.script_blob,self.script_size=blob('extends Node\n')
    def get(self,path):
        if path=='': return {'default_branch':'main','archived':False}
        if path.startswith('/git/matching-refs/heads/'):
            return [] if self.branch_head is None else [{'ref':'refs/heads/studio/jumpy','object':{'sha':self.branch_head}}]
        if path=='/branches/main': return {'commit':{'sha':self.parent}}
        if path.startswith('/git/trees/'):
            return {'truncated':False,'tree':[
                {'path':'project.godot','type':'blob','mode':'100644','sha':'1'*40,'size':self.project_size},
                {'path':'scripts/main.gd','type':'blob','mode':'100644','sha':'2'*40,'size':self.script_size},
            ]}
        if path.endswith('/'+'1'*40): return self.project_blob
        if path.endswith('/'+'2'*40): return self.script_blob
        if path.startswith('/git/commits/'): return {'tree':{'sha':'b'*40}}
        raise AssertionError(path)
    def call(self,method,path,data=None):
        if path.endswith('/git/trees'):
            state_entries=[e for e in data['tree'] if e['path']=='.studio/state.json']
            self.states.append(json.loads(state_entries[0]['content']))
            return {'sha':'c'*40}
        if path.endswith('/git/commits'): return {'sha':hex(1000+len(self.states))[2:].rjust(40,'d')[-40:]}
        if path.endswith('/git/refs'):
            self.branch_head=data['sha']; return {}
        if '/git/refs/heads/' in path:
            self.branch_head=data['sha']; return {}
        raise AssertionError((method,path,data))


class FakeModel:
    def __init__(self,limit): self.calls=0; self.models_used={}
    def ask(self,role,context,screenshots=()):
        self.calls+=1; self.models_used[role]='fake'
        if role=='product': return {'journeys':[{'id':'play','steps':[{'action':'tap','key':'play_button'},{'action':'expect_text','value':'Score'}]}]}
        if role=='design': return {'direction':'minimal'}
        if role=='implementation': return {'files':[{'path':'scripts/main.gd','content':'extends Node\n# improved\n'}]}
        if role=='tests': return {'files':[{'path':'tests/main_test.gd','content':'extends Node\n'}]}
        if role=='review': return {'passed':True,'blockers':[]}
        raise AssertionError(role)


class FakeSandbox:
    def __init__(self,root): self.root=root
    def create(self,name):
        if not (self.root/'project.godot').is_file(): raise AssertionError('missing project')
    def gates(self,name,journeys):
        return True,[{'exit_code':0,'journeys_executed':False,'source_project_immutable':True}]


class GodotPreviewTests(unittest.TestCase):
    def request(self):
        return {'id':'jumpy','target_repo':'dbrckk/Jumpy','app_name':'jumpy','brief':'Improve Jumpy safely without external services.','enabled':True,'max_rounds':1,'max_calls':8,'max_cycles':2}

    def test_existing_godot_project_checkpoints_without_claiming_completion(self):
        github=FakeGitHub()
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); state=godot_preview.execute(self.request(),base/'work',base/'out',github,FakeModel,FakeSandbox)
        self.assertEqual(state['status'],'godot_preview_validated')
        self.assertFalse(state['completion']['finished'])
        self.assertEqual(state['completion']['next_stage'],'godot_android_export_qa')
        self.assertFalse(state['coverage']['journeys_executed'])
        self.assertFalse(state['coverage']['android_export'])
        self.assertIsNotNone(github.branch_head)
        self.assertGreaterEqual(len(github.states),3)
        self.assertEqual(state['architecture_decision']['constraints']['framework'],'godot')
        self.assertEqual(
            state['architecture_autonomy_policy']['decision_confidence'],
            state['architecture_decision'].get('autonomy_policy', {}).get('decision_confidence'),
        )
        self.assertIn('architecture_changes_allowed', state['architecture_autonomy_policy'])
        self.assertEqual(state['architecture_preflight']['status'],'validated')
        self.assertIn(state['architecture_preflight']['verdict'], {'pass','hold'})
        self.assertEqual(state['architecture_evaluation']['status'],'evaluated')
        self.assertEqual(state['architecture_benchmark']['status'],'benchmarked')
        self.assertIn('architecture_learning',state)
        self.assertIn('architecture_decision',github.states[-1])
        self.assertIn('architecture_evaluation',github.states[-1])
        self.assertIn('architecture_benchmark',github.states[-1])

        # Existing Godot projects can have large editable scripts. Product
        # and design only need bounded, labelled source excerpts; implementation
        # must retain the exact full file for safe source rewrites.
        with tempfile.TemporaryDirectory() as td:
            source_root = Path(td)
            (source_root / 'scripts').mkdir()
            (source_root / 'scenes').mkdir()
            main_source = 'extends Node\n' + '# existing gameplay\n' * 30_000
            (source_root / 'project.godot').write_text('[application]\nrun/main_scene="res://scenes/main.tscn"\n')
            (source_root / 'scripts/main.gd').write_text(main_source)
            (source_root / 'scenes/main.tscn').write_text('[gd_scene format=3]\n')
            for phase in ('product', 'design'):
                planning = json.loads(godot_preview._context(
                    self.request(), {}, source_root, phase=phase,
                ))
                self.assertEqual(planning['editable_file_count'], 3)
                self.assertEqual(
                    planning['files_mode'], 'bounded_planning_excerpts_not_complete_source',
                )
                self.assertIn('project.godot', planning['files'])
                self.assertIn('scripts/main.gd', planning['files'])
                self.assertIn('[TRUNCATED: planning excerpt only]', planning['files']['scripts/main.gd'])
                self.assertLess(
                    sum(len(content) for content in planning['files'].values()),
                    godot_preview.PLANNING_SOURCE_CHAR_BUDGET + 300,
                )
                self.assertEqual(planning['manifest_omitted_count'], 0)
                self.assertTrue(any(
                    row['path'] == 'scripts/main.gd' and row['size_bytes'] > 300_000
                    for row in planning['editable_file_manifest']
                ))
            implementation = json.loads(godot_preview._context(
                self.request(), {}, source_root,
            ))
            self.assertEqual(implementation['files']['scripts/main.gd'], main_source)
            self.assertNotIn('files_mode', implementation)

            # A small change must not require the model to echo the complete
            # 570k-character existing script. The runner expands each edit
            # only after verifying a unique match in the authoritative file.
            guard = source_root / 'scripts/guard.gd'
            before = 'extends Node\\nfunc handle():\\n    if settings_open:\\n        start_game()\\n'
            guard.write_text(before)
            replacement = 'if not settings_open:\\n        start_game()'
            payload = {'edits': [{'path': 'scripts/guard.gd',
                                  'find': 'if settings_open:\\n        start_game()',
                                  'replace': replacement}]}
            godot_preview._safe_apply(source_root, payload, 'implementation',
                                      architecture_changes_allowed=False)
            after = guard.read_text()
            self.assertIn(replacement, after)
            self.assertNotIn('    if settings_open:', after)
            for invalid in (
                {'edits': [{'path': 'scripts/guard.gd', 'find': 'missing text',
                            'replace': 'safe'}]},
                {'edits': [{'path': 'scripts/guard.gd', 'find': 'Node',
                            'replace': 'OtherNode'},
                           {'path': 'scripts/main.gd', 'find': 'absent',
                            'replace': 'safe'}]},
            ):
                with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    StudioError, 'exactly one source match',
                ):
                    godot_preview._safe_apply(source_root, invalid, 'implementation')
                self.assertEqual(guard.read_text(), after)
            with self.assertRaisesRegex(StudioError, 'existing workspace file'):
                godot_preview._safe_apply(source_root, {'edits': [{
                    'path': 'scripts/new.gd', 'find': 'x', 'replace': 'y',
                }]}, 'implementation')
            with self.assertRaisesRegex(godot_preview.ArchitectureChangeBlocked, 'HOLD'):
                godot_preview._safe_apply(source_root, {'edits': [{
                    'path': 'project.godot', 'find': '[application]',
                    'replace': '[application]\\n# changed',
                }]}, 'implementation', architecture_changes_allowed=False)
            link = source_root / 'scripts/linked.gd'
            link.symlink_to('guard.gd')
            with self.assertRaisesRegex(StudioError, 'symlink'):
                godot_preview._safe_apply(source_root, {'edits': [{
                    'path': 'scripts/linked.gd', 'find': 'extends Node',
                    'replace': 'extends Control',
                }]}, 'implementation')
            self.assertEqual(guard.read_text(), after)

        req = godot_preview.request_check(self.request())
        fingerprint = godot_preview.hashlib.sha256(godot_preview.canonical(
            {k: v for k, v in req.items() if k != 'enabled'}
        ).encode()).hexdigest()
        for status in ('repair_needed', 'godot_preview_validated'):
            restored = {'request_hash': fingerprint, 'engine': 'godot',
                        'status': status, 'cycles': req['max_cycles'], 'rounds': 14,
                        'blockers': ['real parse error']}
            model_factory = Mock()
            sandbox_factory = Mock()
            with self.subTest(status=status), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                with patch.object(godot_preview, '_restore', return_value=(restored, 'f'*40, True)):
                    resumed = godot_preview.execute(req, root/'work', root/'out', github,
                                                     model_factory, sandbox_factory)
                self.assertEqual(resumed['checkpoint_commit'], 'f'*40)
                self.assertEqual(json.loads((root/'out/report.json').read_text()), resumed)
                model_factory.assert_not_called()
                sandbox_factory.assert_not_called()
                if status == 'repair_needed':
                    self.assertEqual(resumed['status'], 'blocked')
                    self.assertTrue(resumed['preview_cycle_budget_exhausted'])
                    self.assertFalse(resumed['completion']['finished'])
                    self.assertEqual(resumed['blockers'], ['real parse error'])
                else:
                    self.assertEqual(resumed['status'], 'godot_preview_validated')
                    self.assertNotIn('preview_cycle_budget_exhausted', resumed)

    def test_publication_refuses_branch_movement(self):
        github=FakeGitHub(); github.branch_head='e'*40
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'project.godot').write_text('[application]\n')
            with self.assertRaisesRegex(StudioError,'moved during generation'):
                godot_preview._publish(github,'studio/jumpy','f'*40,root,{'status':'x'})


if __name__=='__main__': unittest.main()

import base64
import json
from pathlib import Path
import tempfile
import unittest
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

    def test_publication_refuses_branch_movement(self):
        github=FakeGitHub(); github.branch_head='e'*40
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'project.godot').write_text('[application]\n')
            with self.assertRaisesRegex(StudioError,'moved during generation'):
                godot_preview._publish(github,'studio/jumpy','f'*40,root,{'status':'x'})


if __name__=='__main__': unittest.main()

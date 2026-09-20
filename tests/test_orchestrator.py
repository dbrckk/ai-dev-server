import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))

from core import StudioError
from github_runner import main as github_main, run as github_run
from orchestrator import run_project, run_registered_stages

BASELINE = 'a' * 40
MISSING_STAGE = 'future_capability_qa'


class OrchestratorTests(unittest.TestCase):
    def payload_for(self, args):
        if 'studio/post_preview.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'real_device'}}
        if 'studio/device_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'capability_qa'}}
        if 'studio/capability_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'store_metadata'}}
        if 'studio/store_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'privacy_policy'}}
        if 'studio/privacy_stage.py' in args:
            return {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'security_scan'}}
        if 'studio/security_stage.py' in args:
            return {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}}
        return {'status': 'validated_preview'}

    def missing_report(self):
        return {
            'status': 'validated_preview',
            'completion': {'finished': False, 'next_stage': MISSING_STAGE, 'blockers': [MISSING_STAGE + '_missing']},
            'release_evidence': {'capability_qa': {'passed': True, 'required_qa_stages': [MISSING_STAGE],
                'permissions': [], 'reasons': [{'profile': MISSING_STAGE, 'source': 'source_marker', 'value': 'future_capability'}]}},
        }

    def test_premium_visual_request_prefetches_asset_forge_before_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'
            request.write_text(json.dumps({
                'id':'deadline-zero',
                'brief':'Create premium AAA zombie sprites for a Godot game.',
                'engine':'godot4',
            }))
            calls=[]
            def runner(args, timeout):
                calls.append(args)
                out.mkdir(parents=True, exist_ok=True)
                if args and args[0]=='production-os':
                    return subprocess.CompletedProcess(args,0)
                if 'studio/run.py' in args:
                    (out/'report.json').write_text(json.dumps({
                        'status':'validated_preview',
                        'completion':{'finished':False,'next_stage':'release_build'},
                    }))
                    return subprocess.CompletedProcess(args,0)
                if 'studio/post_preview.py' in args:
                    (out/'report.json').write_text(json.dumps({
                        'status':'finished',
                        'completion':{'finished':True,'next_stage':None},
                    }))
                    return subprocess.CompletedProcess(args,0)
                self.fail('unexpected stage '+str(args))
            result=run_project(str(request),out,str(root/'work'),runner,1000,lambda:0,BASELINE)
            self.assertEqual(result['status'],'complete')
            self.assertEqual(calls[0][0],'production-os')
            self.assertIn('asset-forge-dispatch',calls[0])
            route=json.loads((out/'asset-forge-prefetch.json').read_text())
            self.assertEqual(route['status'],'dispatched')
            self.assertEqual(route['routes'][0]['project'],'deadline-zero')
            self.assertEqual(route['routes'][0]['command'][route['routes'][0]['command'].index('--asset-type')+1],'sprite-sheet')
            self.assertEqual(route['routes'][0]['command'][route['routes'][0]['command'].index('--format')+1],'png')

    def test_multi_asset_request_uses_transactional_asset_forge_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'
            request.write_text(json.dumps({
                'id':'deadline-zero',
                'target_repo':'dbrckk/deadline-zero',
                'asset_requests':[
                    {'id':'hud-a','objective':'Create premium professional UI icon','engine':'libgdx'},
                    {'id':'hud-b','objective':'Create premium professional UI icon','engine':'libgdx'},
                ],
            }))
            calls=[]
            def runner(args, timeout):
                calls.append(args)
                out.mkdir(parents=True, exist_ok=True)
                if args and args[0]=='production-os':
                    self.assertIn('asset-forge-batch',args)
                    spec = Path(args[args.index('--spec')+1])
                    payload=json.loads(spec.read_text())
                    self.assertEqual(len(payload['items']),2)
                    return subprocess.CompletedProcess(args,0)
                if 'studio/run.py' in args:
                    (out/'report.json').write_text(json.dumps({
                        'status':'validated_preview',
                        'completion':{'finished':False,'next_stage':'release_build'},
                    }))
                    return subprocess.CompletedProcess(args,0)
                if 'studio/post_preview.py' in args:
                    (out/'report.json').write_text(json.dumps({
                        'status':'finished',
                        'completion':{'finished':True,'next_stage':None},
                    }))
                    return subprocess.CompletedProcess(args,0)
                self.fail('unexpected stage '+str(args))
            result=run_project(str(request),out,str(root/'work'),runner,1000,lambda:0,BASELINE)
            self.assertEqual(result['status'],'complete')
            production_calls=[call for call in calls if call and call[0]=='production-os']
            self.assertEqual(len(production_calls),1)
            self.assertIn('asset-forge-batch',production_calls[0])
            prefetch=json.loads((out/'asset-forge-prefetch.json').read_text())
            self.assertTrue(prefetch['batch'])
            self.assertEqual(len(prefetch['routes']),2)

    def test_full_pipeline_reaches_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}')
            calls = []
            def runner(args, timeout):
                calls.append(args); out.mkdir(parents=True, exist_ok=True)
                (out / 'report.json').write_text(json.dumps(self.payload_for(args)))
                return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)
            self.assertEqual(result['status'], 'complete')
            expected = ['studio/run.py', 'studio/post_preview.py', 'studio/device_stage.py', 'studio/capability_stage.py',
                        'studio/store_stage.py', 'studio/privacy_stage.py', 'studio/security_stage.py']
            self.assertEqual(len(calls), len(expected))
            for call, script in zip(calls, expected): self.assertIn(script, call)

    def test_unregistered_stage_research_then_synthesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}'); calls = []
            def runner(args, timeout):
                calls.append(args); out.mkdir(parents=True, exist_ok=True)
                if 'studio/evolution_research.py' in args:
                    order = json.loads((out / 'evolution-work-order.json').read_text())
                    (out / 'evolution-research.json').write_text(json.dumps({'version': 2, 'candidate_id': order['candidate_id'],
                        'status': 'research_complete', 'items': []}))
                    return subprocess.CompletedProcess(args, 0)
                if 'studio/evolution_synthesis.py' in args:
                    order = json.loads((out / 'evolution-work-order.json').read_text())
                    (out / 'evolution-candidate.json').write_text(json.dumps({
                        'status': 'candidate_validated', 'candidate_id': order['candidate_id']}))
                    return subprocess.CompletedProcess(args, 0)
                if 'studio/evolution_isolated_runner.py' in args:
                    order = json.loads((out / 'evolution-work-order.json').read_text())
                    (out / 'evolution-isolated-benchmark.json').write_text(json.dumps({
                        'version': 1, 'candidate_id': order['candidate_id'], 'status': 'benchmark_complete'}))
                    (out / 'evolution-promotion.json').write_text(json.dumps({
                        'version': 1, 'candidate_id': order['candidate_id'], 'status': 'promotion_rejected',
                        'promotion_decision': 'reject', 'reasons': ['fixture_rejection']}))
                    return subprocess.CompletedProcess(args, 0)
                report = {'status': 'validated_preview'} if 'studio/run.py' in args else self.missing_report()
                (out / 'report.json').write_text(json.dumps(report)); return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)
            self.assertEqual(result['status'], 'adaptation_required')
            self.assertEqual(result['research_status'], 'complete')
            self.assertEqual(result['synthesis_status'], 'validated')
            self.assertEqual(result['benchmark_status'], 'rejected')
            order = json.loads((out / 'evolution-work-order.json').read_text())
            self.assertEqual(order['baseline_sha'], BASELINE)
            self.assertTrue(order['candidate_branch'].startswith('evolution/future-capability-qa-'))
            self.assertTrue(any('studio/evolution_research.py' in call for call in calls))
            self.assertTrue(any('studio/evolution_synthesis.py' in call for call in calls))
            self.assertTrue(any('studio/evolution_isolated_runner.py' in call for call in calls))

    def test_research_failure_prevents_synthesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}'); calls=[]
            def runner(args, timeout):
                calls.append(args); out.mkdir(parents=True, exist_ok=True)
                if 'studio/evolution_research.py' in args:
                    (out / 'evolution-research-error.json').write_text(json.dumps({'status': 'research_blocked'}))
                    return subprocess.CompletedProcess(args, 1)
                report = {'status': 'validated_preview'} if 'studio/run.py' in args else self.missing_report()
                (out / 'report.json').write_text(json.dumps(report)); return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)
            self.assertEqual(result['status'], 'adaptation_required')
            self.assertEqual(result['research_status'], 'blocked')
            self.assertEqual(result['synthesis_status'], 'not_ready')
            self.assertFalse(any('studio/evolution_synthesis.py' in call for call in calls))

    def test_adaptation_without_baseline_has_no_promotable_work_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}')
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                report = {'status': 'validated_preview'} if 'studio/run.py' in args else self.missing_report()
                (out / 'report.json').write_text(json.dumps(report)); return subprocess.CompletedProcess(args, 0)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, None)
            self.assertEqual(result['research_status'], 'not_planned_without_baseline')
            self.assertEqual(result['synthesis_status'], 'not_ready')
            self.assertTrue((out / 'evolution-request.json').is_file()); self.assertFalse((out / 'evolution-work-order.json').exists())

    def test_stage_return_code_two_is_human_action_not_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}')
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                if 'studio/run.py' in args:
                    report = {'status': 'validated_preview'}
                    rc = 0
                elif 'studio/post_preview.py' in args:
                    report = {'status': 'validated_preview', 'completion': {'finished': False, 'next_stage': 'play_publish'}}
                    rc = 0
                elif 'studio/play_stage.py' in args:
                    report = {
                        'status': 'human_action_required',
                        'human_action': {'action': 'play_access_token_required'},
                        'completion': {'finished': False, 'next_stage': 'play_publish'},
                    }
                    rc = 2
                else:
                    self.fail('unexpected stage ' + str(args))
                (out / 'report.json').write_text(json.dumps(report))
                return subprocess.CompletedProcess(args, rc)
            result = run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)
            self.assertEqual(result['status'], 'human_action_required')
            self.assertEqual(result['human_action']['action'], 'play_access_token_required')
            self.assertEqual(result['next_stage'], 'play_publish')

    def test_scheduler_rewind_can_revisit_release_build_boundedly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'out'
            request = root / 'request.json'
            request.write_text('{}')
            calls = []
            release_build_calls = 0

            def runner(args, timeout):
                nonlocal release_build_calls
                calls.append(args)
                out.mkdir(parents=True, exist_ok=True)
                if 'studio/post_preview.py' in args:
                    release_build_calls += 1
                    if release_build_calls == 1:
                        report = {
                            'status': 'validated_preview',
                            'completion': {'finished': False, 'next_stage': 'performance_qa'},
                        }
                    else:
                        report = {
                            'status': 'validated_preview',
                            'completion': {'finished': False, 'next_stage': 'security_scan'},
                        }
                elif 'studio/performance_stage.py' in args:
                    report = {
                        'status': 'validated_preview',
                        'completion': {'finished': False, 'next_stage': 'release_build'},
                    }
                elif 'studio/security_stage.py' in args:
                    report = {
                        'status': 'finished',
                        'completion': {'finished': True, 'next_stage': None},
                    }
                else:
                    self.fail('unexpected stage ' + str(args))
                (out / 'report.json').write_text(json.dumps(report))
                return subprocess.CompletedProcess(args, 0)

            initial = {
                'status': 'validated_preview',
                'completion': {'finished': False, 'next_stage': 'release_build'},
            }
            result = run_registered_stages(
                str(request), out, str(root / 'work'), initial,
                1000, runner, lambda: 0, BASELINE,
            )
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(release_build_calls, 2)
            self.assertEqual(
                [next(arg for arg in call if arg.startswith('studio/')) for call in calls],
                [
                    'studio/post_preview.py',
                    'studio/performance_stage.py',
                    'studio/post_preview.py',
                    'studio/security_stage.py',
                ],
            )


    def test_successful_stage_must_advance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'out'; request = root / 'request.json'; request.write_text('{}')
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                report = {'status': 'validated_preview'} if 'studio/run.py' in args else {'status': 'validated_preview',
                    'completion': {'finished': False, 'next_stage': 'real_device'}}
                (out / 'report.json').write_text(json.dumps(report)); return subprocess.CompletedProcess(args, 0)
            with self.assertRaisesRegex(StudioError, 'did not advance'):
                run_project(str(request), out, str(root / 'work'), runner, 1000, lambda: 0, BASELINE)


class GitHubRunnerTests(unittest.TestCase):
    def request(self, root):
        path = root / 'request.json'
        path.write_text(json.dumps({'id': 'app-one', 'target_repo': 'owner/app-one', 'app_name': 'app_one',
            'brief': 'Build a polished offline focus timer mobile application.', 'enabled': True}))
        return path

    def test_non_main_is_rejected_before_generation(self):
        with patch.dict('os.environ', {'GITHUB_REF': 'refs/heads/feature'}, clear=True):
            with self.assertRaisesRegex(StudioError, 'requires main'): github_main(['request.json'])

    def test_adapter_reports_complete_only_after_machine_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); request = self.request(root); out = root / 'out'
            def runner(args, timeout):
                out.mkdir(parents=True, exist_ok=True)
                report = {'status': 'finished', 'completion': {'finished': True, 'next_stage': None}} if 'studio/post_preview.py' in args else {'status': 'validated_preview'}
                (out / 'report.json').write_text(json.dumps(report)); return subprocess.CompletedProcess(args, 0)
            result = github_run(request, out, runner=runner, clock=lambda: 0, budget_seconds=1000, baseline_sha=BASELINE)
            self.assertEqual(result['status'], 'complete'); self.assertTrue(result['finished'])


if __name__ == '__main__': unittest.main()

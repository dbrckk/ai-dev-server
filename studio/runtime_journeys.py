"""Generate and execute immutable product journeys on an Android target device."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

from core import StudioError
from journeys import validate_journeys

TEST_PATH = Path('integration_test/__studio_runtime_journeys_test.dart')


def package_name(root: Path) -> str:
    pubspec = root / 'pubspec.yaml'
    if not pubspec.is_file():
        raise StudioError('pubspec.yaml missing')
    match = re.search(r'^name:\s*([a-z][a-z0-9_]*)\s*$', pubspec.read_text(), re.MULTILINE)
    if not match:
        raise StudioError('Unable to determine Flutter package name')
    return match.group(1)


def render_test(package: str, journeys: list[dict]) -> str:
    validate_journeys(journeys)
    payload = base64.b64encode(json.dumps(journeys, ensure_ascii=False).encode()).decode()
    return f'''import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:{package}/app.dart';

Future<void> settle(WidgetTester tester) async {{
  await tester.pumpAndSettle(const Duration(milliseconds: 100),
      EnginePhase.sendSemanticsUpdate, const Duration(seconds: 10));
  expect(tester.takeException(), isNull);
}}

void main() {{
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  final journeys = jsonDecode(utf8.decode(base64Decode('{payload}'))) as List<dynamic>;
  for (final journey in journeys) {{
    testWidgets('studio-runtime:${{journey['id']}}', (tester) async {{
      await tester.pumpWidget(const StudioApp());
      await settle(tester);
      for (final step in journey['steps'] as List<dynamic>) {{
        final action = step['action'] as String;
        final key = step['key'] as String?;
        final target = find.byKey(ValueKey<String>(key ?? '__unused'));
        if (key != null) expect(target, findsOneWidget);
        switch (action) {{
          case 'tap':
            await tester.ensureVisible(target);
            await tester.tap(target);
          case 'enter_text':
            await tester.ensureVisible(target);
            await tester.enterText(target, step['value'] as String);
          case 'scroll':
            await tester.drag(target, Offset(0, (step['dy'] as num).toDouble()));
          case 'expect_text':
            expect(find.text(step['value'] as String), findsWidgets);
          case 'expect_absent':
            expect(find.text(step['value'] as String), findsNothing);
          case 'expect_key':
            expect(target, findsOneWidget);
          default:
            fail('Unsupported action');
        }}
        await settle(tester);
      }}
    }});
  }}
}}
'''


def run_on_device(root: Path, journeys: list[dict], device: str,
                  runner=subprocess.run, timeout: int = 1200) -> dict:
    journeys = validate_journeys(journeys)
    package = package_name(root)
    pubspec = root / 'pubspec.yaml'
    lock = root / 'pubspec.lock'
    original_pubspec = pubspec.read_bytes()
    original_lock = lock.read_bytes() if lock.is_file() else None
    test_file = root / TEST_PATH
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(render_test(package, journeys))
    logs: list[dict] = []
    try:
        commands = [
            ['flutter', 'pub', 'add', 'dev:integration_test:{sdk: flutter}'],
            ['flutter', 'test', TEST_PATH.as_posix(), '-d', device, '--no-pub'],
        ]
        for args in commands:
            result = runner(args, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, timeout=timeout)
            logs.append({'command': args, 'exit_code': result.returncode,
                         'output': result.stdout[-12000:]})
            if result.returncode:
                return {'passed': False, 'blockers': ['runtime_journey_failed'], 'logs': logs}
        encoded = json.dumps(journeys, sort_keys=True, separators=(',', ':')).encode()
        return {
            'passed': True,
            'journey_ids': [j['id'] for j in journeys],
            'journey_count': len(journeys),
            'journeys_sha256': hashlib.sha256(encoded).hexdigest(),
            'logs': logs,
        }
    finally:
        pubspec.write_bytes(original_pubspec)
        if original_lock is None:
            if lock.exists():
                lock.unlink()
        else:
            lock.write_bytes(original_lock)
        try:
            test_file.unlink()
            test_file.parent.rmdir()
        except OSError:
            pass

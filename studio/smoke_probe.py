"""Run one deterministic smoke gate for CI diagnosis without secrets."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from core import Sandbox, StudioError, apply_patch
from journeys import encoded_journeys

JOURNEYS = [{'id': 'settings', 'steps': [
    {'action': 'tap', 'key': 'settings_button'},
    {'action': 'expect_text', 'value': 'Session duration'},
]}]


def prepare(root: Path) -> Sandbox:
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    sandbox = Sandbox(root)
    sandbox.create('smoke_app')
    apply_patch(root, {'files': [
        {'path': 'lib/main.dart', 'content': "import 'package:flutter/material.dart';\nimport 'app.dart';\nvoid main() => runApp(const StudioApp());\n"},
        {'path': 'lib/app.dart', 'content': """import 'package:flutter/material.dart';
class StudioApp extends StatelessWidget {
  const StudioApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue)),
    darkTheme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark)),
    home: const HomeScreen(),
  );
}
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Focus')),
    body: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
      const Text('Ready'),
      FilledButton(key: const ValueKey('settings_button'), onPressed: () {
        Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => Scaffold(
          appBar: AppBar(title: const Text('Settings')),
          body: const Center(child: Text('Session duration')),
        )));
      }, child: const Text('Open settings')),
    ])),
  );
}
"""},
        {'path': 'test/app_test.dart', 'content': """import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:smoke_app/app.dart';
void main() {
  testWidgets('shows the focus screen', (tester) async {
    await tester.pumpWidget(const StudioApp());
    expect(find.text('Focus'), findsOneWidget);
    expect(find.text('Ready'), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
  });
}
"""},
    ]})
    return sandbox


def run(stage: str) -> int:
    root = Path('/tmp/studio-smoke-probe')
    sandbox = prepare(root)
    if stage == 'create':
        return 0
    commands = [
        ('pubget', ['flutter', 'pub', 'get'], True),
        ('analyze', ['flutter', 'analyze', '--no-pub'], False),
        ('test', ['flutter', 'test', '--no-pub'], False),
    ]
    for name, command, network in commands:
        rc, output = sandbox.run(command, network=network, timeout=900)
        print(output)
        if rc:
            return rc
        if stage == name:
            return 0
    if stage in ('visual', 'build'):
        probe = Path(__file__).with_name('visual_test.dart').read_text().replace('APP_NAME', 'smoke_app').replace('JOURNEYS_BASE64', encoded_journeys(JOURNEYS))
        (root / 'test/__studio_visual_test.dart').write_text(probe)
        (root / 'dart_test.yaml').write_text('tags:\n  studio-visual:\n')
        rc, output = sandbox.run(['flutter', 'test', '--no-pub', '--update-goldens', 'test/__studio_visual_test.dart'], network=False, timeout=900)
        print(output)
        if rc:
            return rc
        if stage == 'visual':
            return 0
    if stage == 'build':
        rc, output = sandbox.run(['flutter', 'build', 'apk', '--debug', '--no-pub'], network=True, timeout=900)
        print(output)
        return rc
    raise StudioError('Unknown smoke probe stage')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['create', 'pubget', 'analyze', 'test', 'visual', 'build'])
    return run(parser.parse_args().stage)


if __name__ == '__main__':
    raise SystemExit(main())

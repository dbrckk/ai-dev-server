"""Real Docker/Flutter smoke test with a deterministic app; no model or GitHub secrets."""
import json
from pathlib import Path
import sys
from core import Sandbox, apply_patch

root = Path('/tmp/studio-smoke')
root.mkdir()
sandbox = Sandbox(root)
sandbox.create('smoke_app')
apply_patch(root, {'files': [
    {'path': 'lib/main.dart', 'content': "import 'package:flutter/material.dart';\nimport 'app.dart';\nvoid main() => runApp(const StudioApp());\n"},
    {'path': 'lib/app.dart', 'content': """import 'package:flutter/material.dart';
class StudioApp extends StatelessWidget {
  const StudioApp({super.key});

  ThemeData _theme(Brightness brightness) {
    final dark = brightness == Brightness.dark;
    return ThemeData(
      brightness: brightness,
      scaffoldBackgroundColor: dark ? Colors.black : Colors.white,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: brightness,
      ),
    );
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    theme: _theme(Brightness.light),
    darkTheme: _theme(Brightness.dark),
    home: const HomeScreen(),
  );
}
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Focus')),
    body: Center(child: FilledButton(
      key: const ValueKey('settings_button'),
      onPressed: () {
        Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => Scaffold(
          appBar: AppBar(title: const Text('Settings')),
          body: const Center(child: Text('Session duration')),
        )));
      },
      child: const Text('Open settings'),
    )),
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
    expect(find.text('Open settings'), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
  });
}
"""}
]})
passed, logs = sandbox.gates('smoke_app', [{'id': 'settings', 'steps': [
    {'action': 'tap', 'key': 'settings_button'}, {'action': 'expect_text', 'value': 'Session duration'}]}])
Path('studio-output').mkdir(exist_ok=True)
import shutil
for screenshot in (root / 'test/goldens').glob('*.png'):
    shutil.copyfile(screenshot, Path('studio-output') / screenshot.name)
Path('studio-output/smoke.json').write_text(json.dumps({'passed': passed, 'logs': logs}, indent=2))
for log in logs:
    print(' '.join(log['command']), log['exit_code'])
    if log['exit_code']:
        print(log['output'])
sys.exit(0 if passed else 1)

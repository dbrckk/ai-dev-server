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
  @override
  Widget build(BuildContext context) => MaterialApp(
    theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue)),
    darkTheme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark)),
    home: Scaffold(appBar: AppBar(title: const Text('Focus')), body: const Center(child: Text('Ready'))),
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
"""}
]})
passed, logs = sandbox.gates('smoke_app')
Path('studio-output').mkdir(exist_ok=True)
Path('studio-output/smoke.json').write_text(json.dumps({'passed': passed, 'logs': logs}, indent=2))
for log in logs:
    print(' '.join(log['command']), log['exit_code'])
    if log['exit_code']:
        print(log['output'])
sys.exit(0 if passed else 1)

@Tags(['studio-visual'])
library;

import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:APP_NAME/app.dart';

Future<void> settle(WidgetTester tester) async {
  await tester.pumpAndSettle(const Duration(milliseconds: 100),
      EnginePhase.sendSemanticsUpdate, const Duration(seconds: 10));
  expect(tester.takeException(), isNull,
      reason: 'No render/layout/runtime exception');
}

Future<void> checkScreen(WidgetTester tester, String filename) async {
  expect(find.byType(MaterialApp), findsOneWidget);
  await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
  await expectLater(tester, meetsGuideline(textContrastGuideline));
  await expectLater(find.byType(StudioApp), matchesGoldenFile('goldens/$filename.png'));
}

Future<void> loadSdkFonts() async {
  final sdk = Platform.environment['FLUTTER_ROOT'];
  if (sdk == null) throw StateError('Flutter SDK root missing');
  final directory = Directory('$sdk/bin/cache/artifacts/material_fonts');
  final fonts = directory.listSync().whereType<File>().toList();
  final roboto = fonts.where((file) =>
      file.uri.pathSegments.last.startsWith('Roboto') && file.path.endsWith('.ttf')).toList();
  if (roboto.isEmpty) throw StateError('Real Roboto fonts missing; refusing block-glyph screenshots');
  final textLoader = FontLoader('Roboto');
  for (final font in roboto) {
    textLoader.addFont(Future.value(ByteData.sublistView(font.readAsBytesSync())));
  }
  await textLoader.load();
  final icons = File('${directory.path}/MaterialIcons-Regular.otf');
  final iconLoader = FontLoader('MaterialIcons');
  iconLoader.addFont(Future.value(ByteData.sublistView(icons.readAsBytesSync())));
  await iconLoader.load();
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUpAll(loadSdkFonts);
  final journeys = jsonDecode(utf8.decode(base64Decode('JOURNEYS_BASE64'))) as List<dynamic>;
  for (final variant in [
    ('compact-light', const Size(360, 800), Brightness.light, 1.0),
    ('compact-dark', const Size(360, 800), Brightness.dark, 1.0),
    ('large-text', const Size(360, 800), Brightness.light, 1.6),
    ('wide-light', const Size(430, 932), Brightness.light, 1.0),
  ]) {
    for (final journey in <dynamic>[{'id': 'initial', 'steps': <dynamic>[]}, ...journeys]) {
      testWidgets('${journey['id']}--${variant.$1}', (tester) async {
        tester.view.devicePixelRatio = 1;
        tester.view.physicalSize = variant.$2;
        tester.platformDispatcher.platformBrightnessTestValue = variant.$3;
        tester.platformDispatcher.textScaleFactorTestValue = variant.$4;
        addTearDown(() {
          tester.view.resetDevicePixelRatio();
          tester.view.resetPhysicalSize();
          tester.platformDispatcher.clearAllTestValues();
        });
        final handle = tester.ensureSemantics();
        try {
          await tester.pumpWidget(const StudioApp());
          await settle(tester);
          for (final step in journey['steps'] as List<dynamic>) {
            final action = step['action'] as String;
            final key = step['key'] as String?;
            final target = find.byKey(ValueKey<String>(key ?? '__unused'));
            if (key != null) expect(target, findsOneWidget);
            switch (action) {
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
            }
            await settle(tester);
          }
          await checkScreen(tester, '${journey['id']}--${variant.$1}');
        } finally {
          handle.dispose();
        }
      });
    }
  }
}

@Tags(['studio-visual'])
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:APP_NAME/app.dart';

void main() {
  for (final variant in [
    ('compact-light', const Size(360, 800), Brightness.light, 1.0),
    ('compact-dark', const Size(360, 800), Brightness.dark, 1.0),
    ('large-text', const Size(360, 800), Brightness.light, 1.6),
    ('wide-light', const Size(430, 932), Brightness.light, 1.0),
  ]) {
    testWidgets(variant.$1, (tester) async {
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
      addTearDown(handle.dispose);
      await tester.pumpWidget(const StudioApp());
      await tester.pumpAndSettle(const Duration(milliseconds: 100), EnginePhase.sendSemanticsUpdate, const Duration(seconds: 10));
      expect(tester.takeException(), isNull, reason: 'No render/layout/runtime exception');
      expect(find.byType(MaterialApp), findsOneWidget);
      await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
      await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
      await expectLater(tester, meetsGuideline(textContrastGuideline));
      await expectLater(find.byType(StudioApp), matchesGoldenFile('goldens/${variant.$1}.png'));
    });
  }
}

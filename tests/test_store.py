import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'studio'))
from store_package import build_store_package, decode_png, encode_rgba, listing_from_state


class StorePackageTests(unittest.TestCase):
    def make_png(self, path: Path, width=360, height=800, rgb=(20, 30, 40)):
        pixel = bytes((*rgb, 255))
        path.write_bytes(encode_rgba(width, height, pixel * (width * height)))

    def test_listing_is_bounded_and_derived_from_brief(self):
        req = {
            'app_name': 'focus_timer',
            'brief': 'A focused productivity timer that helps people complete tasks without distraction.'
        }
        state = {'product': {'acceptance_criteria': ['Start and stop a focus timer reliably.'], 'journeys': [{'id': 'focus', 'steps': []}]}}
        listing = listing_from_state(req, state)
        self.assertEqual(listing['title'], 'Focus Timer')
        self.assertEqual(listing['category'], 'PRODUCTIVITY')
        self.assertLessEqual(len(listing['short_description']), 80)
        self.assertTrue(80 <= len(listing['full_description']) <= 4000)

    def test_builds_valid_assets_and_permission_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, out = base / 'app', base / 'out'
            manifest = root / 'android/app/src/main/AndroidManifest.xml'
            manifest.parent.mkdir(parents=True)
            manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
                                '<uses-permission android:name="android.permission.CAMERA"/>\n'
                                '</manifest>')
            out.mkdir()
            self.make_png(out / 'device-release.png', rgb=(10, 20, 30))
            self.make_png(out / 'initial--compact-light.png', rgb=(30, 40, 50))
            self.make_png(out / 'focus--compact-light.png', rgb=(50, 60, 70))
            state = {'design': {'primary': '#102030', 'accent': '#5060F6'}}
            listing = {
                'title': 'Focus Timer',
                'short_description': 'Stay focused with a clear, reliable timer for important tasks.',
                'full_description': 'Focus Timer provides a simple mobile workflow for starting, tracking and completing focused work sessions. It is designed for clarity, reliable interaction and straightforward everyday use.',
                'category': 'PRODUCTIVITY',
            }
            evidence = build_store_package(root, out, state, listing)
            self.assertTrue(evidence['passed'])
            self.assertGreaterEqual(evidence['screenshot_count'], 2)
            self.assertIn('android.permission.CAMERA', evidence['sensitive_permissions'])
            store = out / 'play-store'
            self.assertTrue((store / 'manifest.json').is_file())
            self.assertEqual(decode_png(store / 'icon-512.png')[:2], (512, 512))
            self.assertEqual(decode_png(store / 'feature-graphic-1024x500.png')[:2], (1024, 500))
            shot = store / 'screenshots/phone/01.png'
            width, height, _ = decode_png(shot)
            self.assertLessEqual(max(width, height), 2 * min(width, height))
            manifest_data = json.loads((store / 'manifest.json').read_text())
            self.assertEqual(manifest_data['account_fields_required_at_submission'], ['developer_contact_email'])

    def test_refuses_package_without_two_distinct_validated_screens(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, out = base / 'app', base / 'out'
            out.mkdir()
            self.make_png(out / 'device-release.png')
            listing = {
                'title': 'Timer',
                'short_description': 'A reliable timer for focused work sessions.',
                'full_description': 'A reliable timer designed for focused work sessions, clear interaction and a straightforward mobile experience without unnecessary complexity.',
                'category': 'PRODUCTIVITY',
            }
            with self.assertRaisesRegex(ValueError, 'two distinct'):
                build_store_package(root, out, {}, listing)


if __name__ == '__main__':
    unittest.main()

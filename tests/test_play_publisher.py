import io
import json
import tempfile
import unittest
from pathlib import Path
import zipfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

from core import StudioError
from play_publisher import publish_bundle, publication_credentials


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False


def make_aab(path: Path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("BundleConfig.pb", b"cfg")
        z.writestr("base/manifest/AndroidManifest.xml", b"manifest")


class PlayPublisherTests(unittest.TestCase):
    def test_validate_only_flow_does_not_commit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = root / "app.aab"
            make_aab(bundle)
            calls = []

            def opener(req, timeout=0):
                calls.append((req.full_url, req.method, dict(req.headers), req.data))
                if req.full_url.endswith("/edits"):
                    return Response(json.dumps({"id":"edit-1"}).encode())
                if "upload/androidpublisher" in req.full_url:
                    return Response(json.dumps({"versionCode":123}).encode())
                if "/tracks/internal" in req.full_url:
                    return Response(json.dumps({"track":"internal"}).encode())
                if req.full_url.endswith(":validate"):
                    return Response(b"{}")
                if req.full_url.endswith(":commit"):
                    return Response(b"{}")
                raise AssertionError(req.full_url)

            result = publish_bundle(
                package_name="com.example.demo",
                signed_aab=bundle,
                track="internal",
                access_token="x"*40,
                commit=False,
                opener=opener,
            )

        self.assertTrue(result["passed"])
        self.assertTrue(result["edit_validated"])
        self.assertFalse(result["committed"])
        self.assertFalse(any(url.endswith(":commit") for url, *_ in calls))
        self.assertTrue(any(url.endswith(":validate") for url, *_ in calls))

    def test_commit_requires_explicit_true(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td)/"app.aab"
            make_aab(bundle)
            calls=[]
            def opener(req, timeout=0):
                calls.append(req.full_url)
                if req.full_url.endswith("/edits"): return Response(b'{"id":"e"}')
                if "upload/androidpublisher" in req.full_url: return Response(b'{"versionCode":"7"}')
                if "/tracks/beta" in req.full_url: return Response(b'{"track":"beta"}')
                return Response(b"{}")
            result=publish_bundle(
                package_name="com.example.demo",
                signed_aab=bundle,
                track="beta",
                access_token="y"*40,
                commit=True,
                opener=opener,
            )
        self.assertTrue(result["committed"])
        self.assertTrue(any(url.endswith(":commit") for url in calls))

    def test_token_is_only_in_authorization_header(self):
        token="SECRET_ACCESS_TOKEN_1234567890"
        with tempfile.TemporaryDirectory() as td:
            bundle=Path(td)/"app.aab"; make_aab(bundle); calls=[]
            def opener(req, timeout=0):
                calls.append(req)
                if req.full_url.endswith("/edits"): return Response(b'{"id":"edit"}')
                if "upload/androidpublisher" in req.full_url: return Response(b'{"versionCode":1}')
                if "/tracks/internal" in req.full_url: return Response(b'{"track":"internal"}')
                return Response(b"{}")
            publish_bundle(
                package_name="com.example.demo", signed_aab=bundle,
                track="internal", access_token=token, opener=opener,
            )
        self.assertTrue(calls)
        for req in calls:
            self.assertEqual(req.headers["Authorization"], "Bearer " + token)
            self.assertNotIn(token, req.full_url)
            if req.data:
                self.assertNotIn(token.encode(), req.data)

    def test_missing_publication_credentials_are_explicit(self):
        self.assertEqual(
            publication_credentials({}),
            {"available":False,"blocker":"play_access_token_required"},
        )

    def test_invalid_track_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as td:
            bundle=Path(td)/"app.aab"; make_aab(bundle)
            with self.assertRaisesRegex(StudioError,"track not allowed"):
                publish_bundle(
                    package_name="com.example.demo",
                    signed_aab=bundle,
                    track="production-now",
                    access_token="z"*40,
                    opener=lambda *a,**k: (_ for _ in ()).throw(AssertionError("network")),
                )


if __name__ == "__main__":
    unittest.main()

"""Trusted Android AAB signing boundary.

Project/model-controlled code never receives signing credentials. Existing JAR
signature metadata is stripped from a copied AAB, then jarsigner signs only that
artifact using passwords passed through the signer process environment.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

from core import StudioError

AAB_MAX_BYTES = 1_500_000_000
CERT_RE = re.compile(r"SHA256:\s*([0-9A-Fa-f:]{59,95})")
ALIAS_RE = re.compile(r"[A-Za-z0-9_.-]{1,80}")
SIGNATURE_SUFFIXES = (".SF", ".RSA", ".DSA", ".EC")


def valid_aab(path: Path) -> bool:
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size <= AAB_MAX_BYTES:
        return False
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            return "BundleConfig.pb" in names and "base/manifest/AndroidManifest.xml" in names
    except zipfile.BadZipFile:
        return False


def _signature_entry(name: str) -> bool:
    upper = name.upper()
    if not upper.startswith("META-INF/"):
        return False
    leaf = upper.rsplit("/", 1)[-1]
    return leaf == "MANIFEST.MF" or leaf.endswith(SIGNATURE_SUFFIXES)


def strip_existing_signatures(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    if not valid_aab(source):
        raise StudioError("Unsigned AAB structure invalid")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    removed = []
    with zipfile.ZipFile(source, "r") as src, zipfile.ZipFile(destination, "w") as dst:
        for info in src.infolist():
            if _signature_entry(info.filename):
                removed.append(info.filename)
                continue
            data = src.read(info.filename)
            dst.writestr(info, data)
    if not valid_aab(destination):
        destination.unlink(missing_ok=True)
        raise StudioError("AAB signature stripping produced invalid artifact")
    return {
        "removed_signature_entries": sorted(removed),
        "unsigned_aab_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }


def _sign_env(store_password: str, key_password: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "JAVA_HOME"}}
    env["STUDIO_AAB_STOREPASS"] = store_password
    env["STUDIO_AAB_KEYPASS"] = key_password
    return env


def signing_credentials(env: dict | None = None, *, project_root: Path | None = None) -> dict:
    current = os.environ if env is None else env
    path = current.get("STUDIO_ANDROID_UPLOAD_KEYSTORE_PATH")
    alias = current.get("STUDIO_ANDROID_UPLOAD_KEY_ALIAS")
    store_password = current.get("STUDIO_ANDROID_UPLOAD_STORE_PASSWORD")
    key_password = current.get("STUDIO_ANDROID_UPLOAD_KEY_PASSWORD") or store_password
    if not any((path, alias, store_password, current.get("STUDIO_ANDROID_UPLOAD_KEY_PASSWORD"))):
        return {"available": False, "blocker": "android_upload_keystore_required"}
    if not all((path, alias, store_password, key_password)):
        return {"available": False, "blocker": "android_upload_keystore_configuration_incomplete"}
    keystore = Path(path).expanduser().resolve()
    if not keystore.is_file() or keystore.is_symlink():
        return {"available": False, "blocker": "android_upload_keystore_unavailable"}
    if project_root is not None:
        root = Path(project_root).resolve()
        if keystore == root or root in keystore.parents:
            raise StudioError("Signing keystore must remain outside project workspace")
    if not ALIAS_RE.fullmatch(alias):
        raise StudioError("Release keystore alias invalid")
    return {
        "available": True,
        "keystore": keystore,
        "alias": alias,
        "store_password": store_password,
        "key_password": key_password,
    }


def sign_aab(
    unsigned: Path,
    signed: Path,
    keystore: Path,
    alias: str,
    store_password: str,
    key_password: str | None = None,
    *,
    runner=subprocess.run,
) -> dict:
    unsigned = unsigned.resolve()
    signed = signed.resolve()
    keystore = keystore.resolve()
    if not valid_aab(unsigned):
        raise StudioError("Unsigned AAB structure invalid")
    if not keystore.is_file() or keystore.is_symlink():
        raise StudioError("Release keystore unavailable")
    if not isinstance(alias, str) or not ALIAS_RE.fullmatch(alias):
        raise StudioError("Release keystore alias invalid")
    if not isinstance(store_password, str) or not store_password:
        raise StudioError("Release keystore password missing")
    key_password = store_password if key_password is None else key_password
    if not isinstance(key_password, str) or not key_password:
        raise StudioError("Release key password missing")

    signed.parent.mkdir(parents=True, exist_ok=True)
    signed.unlink(missing_ok=True)
    env = _sign_env(store_password, key_password)
    with tempfile.TemporaryDirectory(prefix="studio-aab-sign-") as td:
        clean = Path(td) / "unsigned-clean.aab"
        stripped = strip_existing_signatures(unsigned, clean)
        sign = [
            "jarsigner",
            "-keystore", str(keystore),
            "-storepass:env", "STUDIO_AAB_STOREPASS",
            "-keypass:env", "STUDIO_AAB_KEYPASS",
            "-signedjar", str(signed),
            str(clean),
            alias,
        ]
        result = runner(sign, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    if result.returncode or not valid_aab(signed):
        signed.unlink(missing_ok=True)
        raise StudioError("AAB signing failed")

    verify_env = {k: v for k, v in env.items() if not k.startswith("STUDIO_AAB_")}
    verify = runner(
        ["jarsigner", "-verify", "-verbose", "-certs", str(signed)],
        env=verify_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    verify_text = verify.stdout.decode(errors="replace") if isinstance(verify.stdout, bytes) else str(verify.stdout or "")
    if verify.returncode or "jar verified." not in verify_text.lower():
        signed.unlink(missing_ok=True)
        raise StudioError("Signed AAB verification failed")

    cert = runner(
        ["keytool", "-list", "-v", "-keystore", str(keystore),
         "-storepass:env", "STUDIO_AAB_STOREPASS", "-alias", alias],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120,
    )
    cert_text = cert.stdout.decode(errors="replace") if isinstance(cert.stdout, bytes) else str(cert.stdout or "")
    match = CERT_RE.search(cert_text)
    if cert.returncode or not match:
        signed.unlink(missing_ok=True)
        raise StudioError("Upload certificate fingerprint unavailable")
    fingerprint = match.group(1).replace(":", "").lower()
    if len(fingerprint) != 64:
        signed.unlink(missing_ok=True)
        raise StudioError("Upload certificate fingerprint invalid")
    return {
        "passed": True,
        "signed_aab_sha256": hashlib.sha256(signed.read_bytes()).hexdigest(),
        "certificate_sha256": fingerprint,
        "signing_scope": "artifact_only",
        "project_code_had_signing_material": False,
        "verified_with": "jarsigner",
        "removed_previous_signature_entries": stripped["removed_signature_entries"],
    }

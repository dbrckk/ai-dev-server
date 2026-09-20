from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_imagen_installer_is_version_pinned_and_checksum_verified():
    script = (ROOT / "scripts" / "install-imagen-codex.sh").read_text(
        encoding="utf-8"
    )

    assert 'version="v0.1.2"' in script
    assert "releases/latest" not in script
    assert "sha256sum --check --status" in script
    assert "2ae06f466ba49898ff0c8a2afdd77b74481002d3036c247316138c727ceb7cb0" in script
    assert "caf5f2987db8e4e5e255a7c464ea3355dba778f45e952254726c22a9c82ff4e3" in script


def test_bootstrap_installs_imagen_without_making_it_mandatory():
    script = (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")

    assert "bash scripts/install-imagen-codex.sh ||" in script
    assert "continuing without it" in script

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_asset_forge_installer_expands_environment_configuration():
    script = (ROOT / "scripts" / "install-asset-forge.sh").read_text(
        encoding="utf-8"
    )

    assert "\\${ASSET_FORGE_HOME" not in script
    assert "\\${ASSET_FORGE_REPOSITORY" not in script
    assert "\\${ASSET_FORGE_REF" not in script
    assert "${ASSET_FORGE_HOME:-$HOME/.local/share/asset-forge}" in script
    assert "${ASSET_FORGE_REPOSITORY:-https://github.com/dbrckk/asset-forge.git}" in script
    assert "${ASSET_FORGE_REF:-7cd615b9b42956b9b3d0d44992ac3e45e1764b6b}" in script


def test_asset_forge_installer_uses_pyproject_editable_install():
    script = (ROOT / "scripts" / "install-asset-forge.sh").read_text(
        encoding="utf-8"
    )

    assert 'python -m pip install --user --no-deps --editable "$install_root"' in script
    assert 'cat >"$bin_dir/asset-forge"' not in script
    assert '"$bin_dir/asset-forge" --help' in script


def test_asset_forge_default_ref_is_immutable_commit():
    script = (ROOT / "scripts" / "install-asset-forge.sh").read_text(
        encoding="utf-8"
    )

    assert "7cd615b9b42956b9b3d0d44992ac3e45e1764b6b" in script
    assert 'ref="${ASSET_FORGE_REF:-main}"' not in script

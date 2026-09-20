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
    assert "${ASSET_FORGE_REF:-c96b87faa5c1a52d2b785cd7c6c3de2da4d16efa}" in script


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

    assert "c96b87faa5c1a52d2b785cd7c6c3de2da4d16efa" in script
    assert 'ref="${ASSET_FORGE_REF:-main}"' not in script

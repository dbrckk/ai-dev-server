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
    assert "${ASSET_FORGE_REF:-main}" in script

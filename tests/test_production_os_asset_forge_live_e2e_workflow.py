from pathlib import Path


WORKFLOW = Path(
    ".github/workflows/production-os-asset-forge-live-e2e.yml"
).read_text(encoding="utf-8")


def test_live_e2e_supports_current_free_asset_forge_backends():
    assert "CLOUDFLARE_API_TOKEN" in WORKFLOW
    assert "CLOUDFLARE_ACCOUNT_ID" in WORKFLOW
    assert "KAGGLE_API_TOKEN" in WORKFLOW
    assert "KAGGLE_USERNAME" in WORKFLOW
    assert 'echo "backend=cloudflare"' in WORKFLOW
    assert 'echo "backend=kaggle-qwen"' in WORKFLOW
    assert 'echo "backend=pollinations"' in WORKFLOW
    assert 'echo "backend=imagen-codex"' in WORKFLOW


def test_live_e2e_never_reports_green_without_real_generation_backend():
    assert "if: steps.credential.outputs.configured != 'true'" in WORKFLOW
    assert "github.event_name == 'workflow_dispatch'" not in WORKFLOW
    assert "No real Asset Forge image-generation backend is configured." in WORKFLOW
    assert "Live E2E requires Cloudflare, Kaggle, Pollinations, or imagen-codex credentials." in WORKFLOW


def test_live_e2e_uses_current_asset_forge_and_generation_dependencies():
    assert "Checkout current Asset Forge" in WORKFLOW
    assert "repository: dbrckk/asset-forge" in WORKFLOW
    assert "ref: 7cd615b9b42956b9b3d0d44992ac3e45e1764b6b" not in WORKFLOW
    assert 'python -m pip install "./asset-forge[generation]"' in WORKFLOW
    assert "python -m pip install -U kaggle" in WORKFLOW
    assert "npm install --global @pollinations/cli@0.1.15" in WORKFLOW


def test_live_e2e_checks_backend_specific_readiness():
    assert 'backend == "cloudflare"' in WORKFLOW
    assert 'data["generation"]["cloudflare"]["rasterReady"] is True' in WORKFLOW
    assert 'backend == "kaggle-qwen"' in WORKFLOW
    assert 'data["generation"]["kaggleQwen"]["rasterReady"] is True' in WORKFLOW
    assert 'backend == "pollinations"' in WORKFLOW
    assert 'backend == "imagen-codex"' in WORKFLOW

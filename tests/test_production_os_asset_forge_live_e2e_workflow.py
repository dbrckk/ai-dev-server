from pathlib import Path


WORKFLOW = Path(
    ".github/workflows/production-os-asset-forge-live-e2e.yml"
).read_text(encoding="utf-8")


def test_live_e2e_delegates_generation_to_asset_forge_repository():
    assert "GH_TOKEN: ${{ secrets.STUDIO_GITHUB_TOKEN || secrets.CODESPACES_PAT }}" in WORKFLOW
    assert "ASSET_FORGE_REPO: dbrckk/asset-forge" in WORKFLOW
    assert "gh workflow run production-os-batch.yml" in WORKFLOW
    assert '--repo "$ASSET_FORGE_REPO"' in WORKFLOW
    assert "-f backend=auto" in WORKFLOW
    assert "gh run watch" in WORKFLOW
    assert "gh run download" in WORKFLOW


def test_live_e2e_does_not_duplicate_asset_forge_provider_secrets():
    assert "secrets.CLOUDFLARE_API_TOKEN" not in WORKFLOW
    assert "secrets.CLOUDFLARE_ACCOUNT_ID" not in WORKFLOW
    assert "secrets.KAGGLE_API_TOKEN" not in WORKFLOW
    assert "secrets.KAGGLE_USERNAME" not in WORKFLOW
    assert "secrets.POLLINATIONS_API_KEY" not in WORKFLOW
    assert "secrets.CODEX_ACCESS_TOKEN" not in WORKFLOW
    assert "secrets.CHATGPT_ACCESS_TOKEN" not in WORKFLOW


def test_live_e2e_requires_exact_asset_forge_sha():
    assert "Checkout current Asset Forge" in WORKFLOW
    assert "repository: dbrckk/asset-forge" in WORKFLOW
    assert 'local_sha="$(git -C asset-forge rev-parse HEAD)"' in WORKFLOW
    assert 'remote_sha="$(gh run view "$run_id"' in WORKFLOW
    assert 'if [ "$local_sha" != "$remote_sha" ]; then' in WORKFLOW
    assert "Asset Forge main advanced during dispatch" in WORKFLOW


def test_live_e2e_validates_remote_bundle_before_integration():
    assert "asset-forge/remote-batch-result/v1" in WORKFLOW
    assert 'assert result["success"] is True' in WORKFLOW
    assert 'assert result["count"] == 1' in WORKFLOW
    assert 'assert digest == item["sha256"]' in WORKFLOW
    assert "live-production-pipeline-icon.png" in WORKFLOW
    assert "deadline-zero/assets/art/live-production-pipeline-icon.png" in WORKFLOW


def test_live_e2e_preserves_production_os_correlation_and_remote_evidence():
    assert "Materialize Production OS live visual handoff" in WORKFLOW
    assert '"report_schema": "asset-forge/production-report/v1"' in WORKFLOW
    assert '"command": "asset-forge fulfill"' in WORKFLOW
    assert '"productionOsCorrelation": studio["production_os"]' in WORKFLOW
    assert '"assetForgeRemoteRunId": int(os.environ["ASSET_FORGE_RUN_ID"])' in WORKFLOW
    assert '"assetForgeSha": os.environ["ASSET_FORGE_SHA"]' in WORKFLOW
    assert '"assetForgeRouting": batch.get("routing_summary")' in WORKFLOW
    assert '"deadlineZeroCompileAndTests": True' in WORKFLOW


def test_live_e2e_is_bounded_and_cross_repo_token_is_mandatory():
    assert "timeout-minutes: 50" in WORKFLOW
    assert "STUDIO_GITHUB_TOKEN or CODESPACES_PAT is required" in WORKFLOW
    assert "Unable to locate dispatched Asset Forge workflow run." in WORKFLOW
    assert "for attempt in $(seq 1 30)" in WORKFLOW

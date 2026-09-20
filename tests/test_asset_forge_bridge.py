from studio.asset_forge_bridge import build_production_os_asset_dispatch, should_route_to_asset_forge


def test_routes_premium_visual_task():
    task = {"objective": "Create premium AAA zombie sprites for the game"}
    assert should_route_to_asset_forge(task) is True


def test_ignores_plain_code_task():
    task = {"objective": "Fix API pagination bug"}
    assert should_route_to_asset_forge(task) is False


def test_builds_production_os_dispatch_contract():
    route = build_production_os_asset_dispatch(
        {
            "id": "hero",
            "objective": "Create premium player icon",
            "asset_type": "icon",
            "format": "svg",
            "engine": "godot4",
        },
        project="deadline-zero",
    )
    assert route["executor"] == "production-os"
    assert route["capability"] == "asset-forge"
    assert "asset-forge-dispatch" in route["command"]
    assert "--backend" in route["command"]


def test_premium_route_defaults_to_primary_importance():
    route = build_production_os_asset_dispatch(
        {"id": "hero-sprite", "objective": "Create premium AAA player sprite"},
        project="deadline-zero",
    )
    assert route["importance"] == "primary"
    idx = route["command"].index("--importance")
    assert route["command"][idx + 1] == "primary"


def test_explicit_secondary_importance_is_preserved():
    route = build_production_os_asset_dispatch(
        {
            "id": "minor-icon",
            "objective": "Create polished UI icon",
            "importance": "secondary",
        },
        project="deadline-zero",
    )
    assert route["importance"] == "secondary"


def test_route_includes_repository_delivery_target():
    route = build_production_os_asset_dispatch(
        {
            "id": "hud-icon",
            "objective": "Create premium professional UI icon",
            "engine": "libgdx",
        },
        project="deadline-zero",
        target_repository="dbrckk/deadline-zero",
    )
    assert route["target_repository"] == "dbrckk/deadline-zero"
    assert route["target_path"] == "assets/art/hud-icon.svg"
    assert "--target-repository" in route["command"]
    assert "--target-path" in route["command"]


def test_batch_preserves_explicit_asset_dependencies():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [
            {
                "id": "character",
                "objective": "Create premium professional character sprite",
                "engine": "libgdx",
            },
            {
                "id": "animation",
                "objective": "Create premium professional animation sprite",
                "engine": "libgdx",
                "depends_on": ["character"],
            },
        ],
        project="deadline-zero",
        target_repository="dbrckk/deadline-zero",
    )
    by_id = {item["id"]: item for item in batch["items"]}
    assert by_id["character"]["depends_on"] == []
    assert by_id["animation"]["depends_on"] == ["character"]


def test_batch_infers_parent_asset_dependency():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [
            {
                "id": "character",
                "objective": "Create premium professional character sprite",
                "engine": "libgdx",
            },
            {
                "id": "atlas",
                "objective": "Create premium professional UI atlas",
                "engine": "libgdx",
                "parent_asset": "character",
            },
        ],
        project="deadline-zero",
    )
    by_id = {item["id"]: item for item in batch["items"]}
    assert by_id["atlas"]["depends_on"] == ["character"]


def test_batch_infers_animation_of_dependency():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [
            {
                "id": "character",
                "objective": "Create premium professional character sprite",
                "engine": "libgdx",
            },
            {
                "id": "run-animation",
                "objective": "Create premium professional run animation sprite",
                "engine": "libgdx",
                "animation_of": "character",
            },
        ],
        project="deadline-zero",
    )
    by_id = {item["id"]: item for item in batch["items"]}
    assert by_id["run-animation"]["depends_on"] == ["character"]


def test_primary_raster_batch_uses_stricter_visual_similarity_policy():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [
            {
                "id": "character",
                "objective": "Create premium AAA character sprite",
                "engine": "libgdx",
            },
            {
                "id": "run",
                "objective": "Create premium AAA run animation sprite",
                "engine": "libgdx",
                "animation_of": "character",
            },
        ],
        project="deadline-zero",
    )
    run = {item["id"]: item for item in batch["items"]}["run"]
    constraints = run["request"]["manifest"]["constraints"]
    assert constraints["visualSimilarityMin"] == 0.55
    assert constraints["visualSimilarityRetries"] == 2
    assert constraints["technicalQualityMin"] == 0.62
    assert constraints["technicalQualityMin"] == 0.58
    assert constraints["maxBorderAlphaRatio"] == 0.04


def test_secondary_raster_batch_uses_lighter_visual_similarity_policy():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [
            {
                "id": "badge",
                "objective": "Create polished UI sprite badge",
                "engine": "libgdx",
                "importance": "secondary",
            },
            {
                "id": "badge-variant",
                "objective": "Create polished UI sprite badge variant",
                "engine": "libgdx",
                "importance": "secondary",
                "variant_of": "badge",
            },
        ],
        project="deadline-zero",
    )
    variant = {item["id"]: item for item in batch["items"]}["badge-variant"]
    constraints = variant["request"]["manifest"]["constraints"]
    assert constraints["visualSimilarityMin"] == 0.42
    assert constraints["visualSimilarityRetries"] == 1
    assert constraints["technicalQualityMin"] == 0.50
    assert constraints["technicalQualityMin"] == 0.42
    assert constraints["maxBorderAlphaRatio"] == 0.08


def test_brief_inference_builds_character_dependency_chain():
    from asset_forge_bridge import infer_asset_tasks_from_brief
    tasks = infer_asset_tasks_from_brief(
        "Create premium AAA zombie character animations and polished visual assets.",
        engine="libgdx",
    )
    by_id = {item["id"]: item for item in tasks}
    assert "character-foundation" in by_id
    assert "character-animation" in by_id
    assert by_id["character-animation"]["animation_of"] == "character-foundation"
    assert by_id["character-foundation"]["format"] == "png"


def test_brief_inference_detects_3d_environment():
    from asset_forge_bridge import infer_asset_tasks_from_brief
    tasks = infer_asset_tasks_from_brief(
        "Create a premium AAA 3D environment model with professional visuals.",
        engine="godot4",
    )
    environment = {item["id"]: item for item in tasks}["environment-foundation"]
    assert environment["asset_type"] == "environment"
    assert environment["format"] == "glb"


def test_raster_quality_policy_can_be_overridden_per_task():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [{
            "id": "hero",
            "objective": "Create premium AAA character sprite",
            "engine": "libgdx",
            "technical_quality_min": 0.72,
            "max_border_alpha_ratio": 0.02,
        }],
        project="deadline-zero",
    )
    constraints = batch["items"][0]["request"]["manifest"]["constraints"]
    assert constraints["technicalQualityMin"] == 0.72
    assert constraints["maxBorderAlphaRatio"] == 0.02


def test_target_repository_defaults_visual_delivery_to_assets_art_without_engine():
    from asset_forge_bridge import build_production_os_asset_dispatch
    route = build_production_os_asset_dispatch(
        {
            "id": "hero",
            "objective": "Create premium professional character sprite",
        },
        project="demo",
        target_repository="owner/game",
    )
    assert route["target_path"] == "assets/art/hero.png"


def test_engine_is_inferred_from_visual_instruction():
    from asset_forge_bridge import build_production_os_asset_batch
    batch = build_production_os_asset_batch(
        [{
            "id": "hero",
            "objective": "Create premium professional sprite art for this libGDX game",
        }],
        project="demo",
        target_repository="owner/game",
    )
    manifest = batch["items"][0]["request"]["manifest"]
    assert manifest["target"]["engine"] == "libgdx"
    assert batch["routes"][0]["target_path"] == "assets/art/hero.png"

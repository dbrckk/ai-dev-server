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

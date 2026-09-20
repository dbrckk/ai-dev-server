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

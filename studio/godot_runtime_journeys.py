"""Execute immutable Godot acceptance journeys inside an isolated runtime copy.

The harness is trusted factory code injected only into an ephemeral project copy.
Journey JSON is data, never generated GDScript. Project code runs with Docker networking
disabled and without CI credentials. Selectors are exact unique Godot Node.name values.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import tempfile

from core import IMAGE, StudioError, canonical
from godot_runtime import _copy_project, _host_env, _trusted_binary_hash
from journeys import validate_journeys

PASS_RE = re.compile(r'^STUDIO_JOURNEY_PASS:([a-z][a-z0-9_-]{0,39})$', re.M)
FAIL_RE = re.compile(r'^STUDIO_JOURNEY_FAIL:([a-z][a-z0-9_-]{0,39}):(.+)$', re.M)
COMPLETE_RE = re.compile(r'^STUDIO_JOURNEYS_COMPLETE:(\d+)$', re.M)
BLOCKING_MARKERS = ('SCRIPT ERROR','Parse Error','Cannot parse','Failed loading resource')

HARNESS = r'''extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _visible(node: Node) -> bool:
    if node is CanvasItem:
        return node.is_visible_in_tree()
    return true

func _collect_named(node: Node, key: String, found: Array[Node]) -> void:
    if String(node.name) == key and _visible(node):
        found.append(node)
    for child in node.get_children():
        _collect_named(child, key, found)

func _find_unique(root_node: Node, key: String) -> Node:
    var found: Array[Node] = []
    _collect_named(root_node, key, found)
    if found.size() != 1:
        return null
    return found[0]

func _collect_text(node: Node, values: Array[String]) -> void:
    if _visible(node):
        if node is Label or node is Button or node is LineEdit or node is TextEdit:
            values.append(String(node.text))
    for child in node.get_children():
        _collect_text(child, values)

func _all_text(root_node: Node) -> String:
    var values: Array[String] = []
    _collect_text(root_node, values)
    return "\n".join(values)

func _tap(root_node: Node, key: String) -> String:
    var node := _find_unique(root_node, key)
    if node == null:
        return "selector_not_unique_or_visible:" + key
    if node is BaseButton:
        node.emit_signal("pressed")
        return ""
    var event := InputEventAction.new()
    event.action = "tap"
    event.pressed = true
    Input.parse_input_event(event)
    event = InputEventAction.new()
    event.action = "tap"
    event.pressed = false
    Input.parse_input_event(event)
    return ""

func _enter_text(root_node: Node, key: String, value: String) -> String:
    var node := _find_unique(root_node, key)
    if node == null:
        return "selector_not_unique_or_visible:" + key
    if node is LineEdit:
        node.text = value
        node.emit_signal("text_changed", value)
        return ""
    if node is TextEdit:
        node.text = value
        node.emit_signal("text_changed")
        return ""
    return "selector_not_text_control:" + key

func _scroll(root_node: Node, key: String, dy: float) -> String:
    var node := _find_unique(root_node, key)
    if node == null:
        return "selector_not_unique_or_visible:" + key
    if not node is ScrollContainer:
        return "selector_not_scroll_container:" + key
    node.scroll_vertical = int(node.scroll_vertical + dy)
    return ""

func _execute_step(root_node: Node, step: Dictionary) -> String:
    var action := String(step.get("action", ""))
    if action == "tap":
        return _tap(root_node, String(step.key))
    if action == "enter_text":
        return _enter_text(root_node, String(step.key), String(step.value))
    if action == "scroll":
        return _scroll(root_node, String(step.key), float(step.dy))
    if action == "expect_key":
        return "" if _find_unique(root_node, String(step.key)) != null else "expected_key_missing:" + String(step.key)
    var text := _all_text(root_node)
    if action == "expect_text":
        return "" if text.contains(String(step.value)) else "expected_text_missing"
    if action == "expect_absent":
        return "" if not text.contains(String(step.value)) else "unexpected_text_present"
    return "unsupported_action"

func _run() -> void:
    var raw := FileAccess.get_file_as_string("res://.studio_journeys.json")
    var parsed = JSON.parse_string(raw)
    if not parsed is Array:
        print("STUDIO_HARNESS_FAIL:invalid_json")
        quit(2)
        return
    var scene_path := String(ProjectSettings.get_setting("application/run/main_scene", ""))
    if scene_path.is_empty():
        print("STUDIO_HARNESS_FAIL:missing_main_scene")
        quit(2)
        return
    for journey in parsed:
        var packed = load(scene_path)
        if packed == null or not packed is PackedScene:
            print("STUDIO_HARNESS_FAIL:main_scene_load")
            quit(2)
            return
        var app: Node = packed.instantiate()
        root.add_child(app)
        await process_frame
        await process_frame
        var reason := ""
        for step in journey.steps:
            reason = _execute_step(app, step)
            await process_frame
            await process_frame
            if not reason.is_empty():
                break
        var jid := String(journey.id)
        if reason.is_empty():
            print("STUDIO_JOURNEY_PASS:" + jid)
        else:
            failures.append(jid)
            print("STUDIO_JOURNEY_FAIL:" + jid + ":" + reason)
        app.queue_free()
        await process_frame
    if failures.is_empty():
        print("STUDIO_JOURNEYS_COMPLETE:" + str(parsed.size()))
        quit(0)
    else:
        quit(1)
'''


def run_journeys(project_root: Path, binary: Path, journeys: list[dict], runner=subprocess.run, timeout=600) -> dict:
    journeys = validate_journeys(journeys)
    source = project_root.resolve(); binary = binary.resolve(); binary_hash = _trusted_binary_hash(binary)
    with tempfile.TemporaryDirectory(prefix='studio-godot-journeys-') as tmp:
        project = Path(tmp)/'project'; project.mkdir(); _copy_project(source,project)
        (project/'.studio_journeys.json').write_text(canonical(journeys))
        (project/'.studio_journey_runner.gd').write_text(HARNESS)
        command=['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges',
                 '--pids-limit=256','--memory=3g','--cpus=2','--network=none',
                 '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=256m','-v',str(project)+':/project:rw',
                 '-v',str(binary)+':/opt/godot:ro','-w','/project',IMAGE,
                 '/opt/godot','--headless','--path','/project','--script','res://.studio_journey_runner.gd']
        try:
            result=runner(command,env=_host_env(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        except subprocess.TimeoutExpired:
            raise StudioError('Godot runtime journeys timed out') from None
        output=result.stdout.decode(errors='replace')[-48000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-48000:]
    passes=PASS_RE.findall(output); failures=[{'id':jid,'reason':reason[:300]} for jid,reason in FAIL_RE.findall(output)]
    complete=COMPLETE_RE.findall(output)
    expected=[item['id'] for item in journeys]
    passed=(result.returncode==0 and not failures and passes==expected and complete==[str(len(expected))]
            and not any(marker in output for marker in BLOCKING_MARKERS))
    return {'passed':passed,'journeys_executed':passed,'journey_count':len(expected),'passed_ids':passes,
            'failures':failures,'exit_code':result.returncode,'output':output,'engine_version':'4.7.2-stable',
            'binary_sha256':binary_hash,'network':'none','source_project':'not_mounted','harness':'trusted_ephemeral_v1'}

"""Trusted Android-rendered visual QA for Godot acceptance journeys.

A temporary project copy is instrumented with a trusted scene runner. The debug APK
executes immutable journey JSON on an offline emulator, captures each final frame into
user://, and the host retrieves those PNGs with run-as. Production source is never
modified and CI credentials are never forwarded to Android tooling.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from core import Model, StudioError, canonical
from godot_android_export import export_debug_apk, install_android_templates
from godot_device_qa import package_name
from godot_runtime import _copy_project, install
from journeys import validate_journeys

PASS_RE = re.compile(r'^STUDIO_VISUAL_PASS:([a-z][a-z0-9_-]{0,39})$', re.M)
COMPLETE_RE = re.compile(r'^STUDIO_VISUAL_COMPLETE:(\d+)$', re.M)
PNG_SIG = b'\x89PNG\r\n\x1a\n'

HARNESS = r'''extends Node

var journeys: Array = []
var failures: Array[String] = []
var original_scene: String = ""

func _ready() -> void:
    call_deferred("_run")

func _visible(node: Node) -> bool:
    return not (node is CanvasItem) or node.is_visible_in_tree()

func _collect_named(node: Node, key: String, found: Array[Node]) -> void:
    if String(node.name) == key and _visible(node): found.append(node)
    for child in node.get_children(): _collect_named(child, key, found)

func _find_unique(root_node: Node, key: String) -> Node:
    var found: Array[Node] = []
    _collect_named(root_node, key, found)
    return found[0] if found.size() == 1 else null

func _collect_text(node: Node, values: Array[String]) -> void:
    if _visible(node) and (node is Label or node is Button or node is LineEdit or node is TextEdit):
        values.append(String(node.text))
    for child in node.get_children(): _collect_text(child, values)

func _step(root_node: Node, step: Dictionary) -> String:
    var action := String(step.get("action", ""))
    if action == "tap":
        var node := _find_unique(root_node, String(step.key))
        if node == null: return "selector"
        if node is BaseButton: node.emit_signal("pressed")
        else:
            var ev := InputEventAction.new(); ev.action = "tap"; ev.pressed = true; Input.parse_input_event(ev)
            ev = InputEventAction.new(); ev.action = "tap"; ev.pressed = false; Input.parse_input_event(ev)
        return ""
    if action == "enter_text":
        var text_node := _find_unique(root_node, String(step.key))
        if text_node is LineEdit: text_node.text = String(step.value); text_node.emit_signal("text_changed", String(step.value)); return ""
        if text_node is TextEdit: text_node.text = String(step.value); text_node.emit_signal("text_changed"); return ""
        return "text_selector"
    if action == "scroll":
        var scroll := _find_unique(root_node, String(step.key))
        if not scroll is ScrollContainer: return "scroll_selector"
        scroll.scroll_vertical = int(scroll.scroll_vertical + float(step.dy)); return ""
    if action == "expect_key": return "" if _find_unique(root_node, String(step.key)) != null else "expected_key"
    var values: Array[String] = []; _collect_text(root_node, values); var all_text := "\n".join(values)
    if action == "expect_text": return "" if all_text.contains(String(step.value)) else "expected_text"
    if action == "expect_absent": return "" if not all_text.contains(String(step.value)) else "unexpected_text"
    return "unsupported"

func _run() -> void:
    var raw := FileAccess.get_file_as_string("res://.studio_visual_journeys.json")
    var parsed = JSON.parse_string(raw)
    if not parsed is Array: get_tree().quit(2); return
    original_scene = String(ProjectSettings.get_setting("studio/original_main_scene", ""))
    if original_scene.is_empty(): get_tree().quit(2); return
    journeys = parsed
    for journey in journeys:
        var packed = load(original_scene)
        if packed == null or not packed is PackedScene: failures.append(String(journey.id)); continue
        var app: Node = packed.instantiate(); add_child(app)
        await get_tree().process_frame; await get_tree().process_frame; await get_tree().process_frame
        var reason := ""
        for step in journey.steps:
            reason = _step(app, step)
            await get_tree().process_frame; await get_tree().process_frame
            if not reason.is_empty(): break
        var jid := String(journey.id)
        if reason.is_empty():
            await get_tree().process_frame
            var image := get_viewport().get_texture().get_image()
            var err := image.save_png("user://studio-visual-" + jid + ".png")
            if err == OK: print("STUDIO_VISUAL_PASS:" + jid)
            else: failures.append(jid)
        else: failures.append(jid)
        app.queue_free(); await get_tree().process_frame
    if failures.is_empty(): print("STUDIO_VISUAL_COMPLETE:" + str(journeys.size())); get_tree().quit(0)
    else: get_tree().quit(1)
'''

SCENE = '''[gd_scene load_steps=2 format=3]\n\n[ext_resource path="res://.studio_visual_runner.gd" type="Script" id="1"]\n\n[node name="StudioVisualRunner" type="Node"]\nscript = ExtResource("1")\n'''


def _safe_env() -> dict[str,str]:
    return {k:v for k,v in os.environ.items() if k in {'PATH','HOME','ANDROID_HOME','ANDROID_SDK_ROOT','JAVA_HOME'} }


def _run(args, timeout=120, **kwargs):
    kwargs.setdefault('env', _safe_env())
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.STDOUT)
    return subprocess.run(args, timeout=timeout, **kwargs)


def _instrument(source: Path, destination: Path, journeys: list[dict]) -> None:
    _copy_project(source.resolve(), destination)
    project = destination/'project.godot'
    if not project.is_file(): raise StudioError('Godot project missing')
    text = project.read_text()
    match = re.search(r'^run/main_scene\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match: raise StudioError('Godot main scene missing')
    original = match.group(1)
    if not original.startswith('res://'): raise StudioError('Godot main scene invalid')
    text = text[:match.start()] + 'run/main_scene="res://.studio_visual_runner.tscn"' + text[match.end():]
    if '[studio]' not in text: text += '\n[studio]\n'
    text += 'original_main_scene="' + original.replace('"','') + '"\n'
    project.write_text(text)
    (destination/'.studio_visual_runner.gd').write_text(HARNESS)
    (destination/'.studio_visual_runner.tscn').write_text(SCENE)
    (destination/'.studio_visual_journeys.json').write_text(canonical(journeys))


def _pull_png(adb: str, serial: str, package: str, jid: str, target: Path) -> None:
    target.parent.mkdir(parents=True,exist_ok=True)
    proc = _run([adb,'-s',serial,'exec-out','run-as',package,'cat','files/studio-visual-'+jid+'.png'],timeout=60)
    data = proc.stdout if isinstance(proc.stdout,bytes) else (proc.stdout or '').encode()
    if proc.returncode or len(data)<1000 or not data.startswith(PNG_SIG):
        raise StudioError('Godot visual screenshot retrieval failed')
    target.write_bytes(data)


def capture_and_review(source: Path, journeys: list[dict], design: dict, out: Path,
                       model_factory=Model, runtime_installer=install,
                       template_installer=install_android_templates,
                       exporter=export_debug_apk, runner=_run, sleeper=time.sleep) -> dict:
    journeys=validate_journeys(journeys)
    if not isinstance(design,dict) or not design: raise StudioError('Godot design evidence missing')
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='studio-godot-visual-') as td:
        temp=Path(td); project=temp/'project'; project.mkdir(); _instrument(source,project,journeys)
        runtime=runtime_installer(temp/'runtime'); templates=template_installer(temp/'templates'); apk=temp/'visual.apk'
        export=exporter(project,runtime,templates,artifact_path=apk)
        if not export.get('passed') or not apk.is_file(): raise StudioError('Godot visual QA APK export failed')
        package=package_name(project)
        adb=shutil.which('adb') or 'adb'
        devices=runner([adb,'devices'],timeout=30)
        raw=devices.stdout.decode(errors='replace') if isinstance(devices.stdout,bytes) else str(devices.stdout or '')
        serials=[line.split()[0] for line in raw.splitlines()[1:] if '\tdevice' in line]
        if len(serials)!=1: raise StudioError('Godot visual QA requires exactly one Android device')
        serial=serials[0]
        runner([adb,'-s',serial,'shell','settings','put','global','airplane_mode_on','1'],timeout=30)
        runner([adb,'-s',serial,'shell','am','broadcast','-a','android.intent.action.AIRPLANE_MODE','--ez','state','true'],timeout=30)
        install_result=runner([adb,'-s',serial,'install','-r','-t',str(apk)],timeout=180)
        if install_result.returncode: raise StudioError('Godot visual QA APK install failed')
        runner([adb,'-s',serial,'logcat','-c'],timeout=30)
        launch=runner([adb,'-s',serial,'shell','monkey','-p',package,'-c','android.intent.category.LAUNCHER','1'],timeout=60)
        if launch.returncode: raise StudioError('Godot visual QA launch failed')
        sleeper(8)
        logs=runner([adb,'-s',serial,'logcat','-d','-v','brief'],timeout=60)
        log_text=logs.stdout.decode(errors='replace') if isinstance(logs.stdout,bytes) else str(logs.stdout or '')
        expected=[j['id'] for j in journeys]; passed=PASS_RE.findall(log_text); complete=COMPLETE_RE.findall(log_text)
        if passed!=expected or complete!=[str(len(expected))]: raise StudioError('Godot visual harness did not complete every journey')
        shots=[]
        for jid in expected:
            shot=out/('godot-visual-'+jid+'.png'); _pull_png(adb,serial,package,jid,shot); shots.append(shot)
    hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in shots]
    if len(set(hashes))<min(2,len(hashes)):
        raise StudioError('Godot visual QA requires distinct rendered evidence')
    model=model_factory(4)
    context='Review these actual Android-rendered Godot journey end-state screenshots against this design. Reject clipping, illegibility, poor contrast, inconsistent spacing, broken layout, or visibly unfinished UI. Design JSON: '+canonical(design)
    verdict=model.ask('visual',context,shots)
    if not verdict.get('passed'):
        return {'passed':False,'visual_reviewed':True,'blockers':verdict.get('blockers') or ['visual review failed'],
                'journey_ids':expected,'screenshot_sha256':hashes,'environment':'android_emulator','network':'airplane_mode'}
    return {'passed':True,'visual_reviewed':True,'blockers':[],'journey_ids':expected,
            'screenshot_sha256':hashes,'environment':'android_emulator','network':'airplane_mode',
            'review_model':model.models_used.get('visual','')}

"""Trusted Google Play release preflight for Godot Android projects.

This layer only normalizes non-secret export settings and validates release identity.
It never invents or generates production signing credentials and does not claim that an
AAB was built. Actual signed bundle export is a separate evidence stage.
"""
from __future__ import annotations

import os
from pathlib import Path
import re

from core import StudioError

MIN_PLAY_TARGET_API = 36
PACKAGE_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+$')


def _replace(text:str,key:str,value:str)->str:
    pattern=re.compile(r'^'+re.escape(key)+r'=.*$',re.M)
    replacement=key+'='+value
    if not pattern.search(text):
        raise StudioError('Godot Android preset missing release option: '+key)
    return pattern.sub(replacement,text,count=1)


def prepare_store_preset(root:Path)->dict:
    path=root/'export_presets.cfg'
    if not path.is_file() or path.is_symlink(): raise StudioError('Godot Android export preset missing')
    original=path.read_text()
    if len(re.findall(r'^platform="Android"$',original,re.M))!=1:
        raise StudioError('Godot release QA requires exactly one Android preset')
    text=original
    text=_replace(text,'gradle_build/use_gradle_build','true')
    text=_replace(text,'gradle_build/export_format','1')
    text=_replace(text,'gradle_build/target_sdk','"36"')
    text=_replace(text,'architectures/arm64-v8a','true')
    text=_replace(text,'package/signed','true')
    if text!=original: path.write_text(text)
    return {'changed':text!=original,'target_api':MIN_PLAY_TARGET_API,'format':'aab','gradle':True,'arm64':True}


def _value(text:str,key:str)->str:
    match=re.search(r'^'+re.escape(key)+r'=(.*)$',text,re.M)
    if not match: raise StudioError('Godot Android preset missing release option: '+key)
    return match.group(1).strip()


def audit_store_preset(root:Path)->dict:
    path=root/'export_presets.cfg'
    if not path.is_file() or path.is_symlink(): raise StudioError('Godot Android export preset missing')
    text=path.read_text()
    blockers=[]
    package=_value(text,'package/unique_name').strip('"')
    version_name=_value(text,'version/name').strip('"')
    try: version_code=int(_value(text,'version/code').strip('"'))
    except ValueError: version_code=0
    target=_value(text,'gradle_build/target_sdk').strip('"')
    try: target_api=int(target)
    except ValueError: target_api=0
    if not PACKAGE_RE.fullmatch(package): blockers.append('invalid_package_id')
    if version_code<1: blockers.append('invalid_version_code')
    if not version_name or len(version_name)>64: blockers.append('invalid_version_name')
    if _value(text,'gradle_build/use_gradle_build')!='true': blockers.append('gradle_build_required')
    if _value(text,'gradle_build/export_format')!='1': blockers.append('aab_export_required')
    if target_api<MIN_PLAY_TARGET_API: blockers.append('target_api_36_required')
    if _value(text,'architectures/arm64-v8a')!='true': blockers.append('arm64_required')
    if _value(text,'package/signed')!='true': blockers.append('signed_release_required')
    return {'passed':not blockers,'blockers':blockers,'package':package,'version_code':version_code,
            'version_name':version_name,'target_api':target_api,'format':'aab' if _value(text,'gradle_build/export_format')=='1' else 'apk',
            'gradle':_value(text,'gradle_build/use_gradle_build')=='true','arm64':_value(text,'architectures/arm64-v8a')=='true'}


def signing_credentials(env:dict|None=None)->dict:
    env=os.environ if env is None else env
    names=('GODOT_ANDROID_KEYSTORE_RELEASE_PATH','GODOT_ANDROID_KEYSTORE_RELEASE_USER','GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD')
    present={name:bool(isinstance(env.get(name),str) and env.get(name)) for name in names}
    if not all(present.values()):
        return {'available':False,'human_action_required':True,'blocker':'release_keystore_required'}
    path=Path(env[names[0]])
    if not path.is_file() or path.is_symlink():
        return {'available':False,'human_action_required':True,'blocker':'release_keystore_file_unavailable'}
    return {'available':True,'human_action_required':False,'blocker':None}


def preflight(root:Path,env:dict|None=None)->dict:
    normalization=prepare_store_preset(root)
    audit=audit_store_preset(root)
    signing=signing_credentials(env)
    passed=audit['passed'] and signing['available']
    blockers=list(audit['blockers'])
    if signing['blocker']: blockers.append(signing['blocker'])
    return {'passed':passed,'preset_normalized':normalization['changed'],'audit':audit,'signing':signing,
            'blockers':blockers,'aab_built':False,'play_target_api_floor':MIN_PLAY_TARGET_API}

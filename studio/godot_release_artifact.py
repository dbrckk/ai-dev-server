"""Build an unsigned Godot AAB without secrets, then sign only the artifact.

The untrusted project executes only inside a pinned container with networking disabled
and receives no production signing material. The upload keystore is exposed later only
to jarsigner/keytool operating on the already-built AAB, never to Godot or Gradle.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

from core import IMAGE, StudioError
from godot_android_export import (MAX_TEMPLATE_ARCHIVE_BYTES, TEMPLATE_ASSET,
                                  TEMPLATE_SHA256, TEMPLATE_URL, _archive_ok,
                                  _preset_name)
from godot_runtime import GODOT_VERSION, _copy_project, _host_env, _trusted_binary_hash

SOURCE_MEMBER='templates/android_source.zip'
MAX_SOURCE_TEMPLATE_BYTES=900_000_000
AAB_MAX_BYTES=1_500_000_000
CERT_RE=re.compile(r'SHA256:\s*([0-9A-Fa-f:]{59,95})')


def _download_archive(cache_dir:Path,opener=urllib.request.urlopen)->Path:
    cache=cache_dir.resolve(); cache.mkdir(parents=True,exist_ok=True)
    archive=cache/TEMPLATE_ASSET; partial=cache/(TEMPLATE_ASSET+'.part'); partial.unlink(missing_ok=True)
    try:
        if not _archive_ok(archive):
            archive.unlink(missing_ok=True)
            req=urllib.request.Request(TEMPLATE_URL,headers={'User-Agent':'ai-dev-server-godot-release-artifact'})
            with opener(req,timeout=90) as response, partial.open('wb') as out:
                total=0; digest=hashlib.sha256()
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk: break
                    total+=len(chunk)
                    if total>MAX_TEMPLATE_ARCHIVE_BYTES: raise StudioError('Godot template archive exceeded trusted size limit')
                    digest.update(chunk); out.write(chunk)
            if digest.hexdigest()!=TEMPLATE_SHA256: raise StudioError('Godot template archive SHA-256 mismatch')
            partial.replace(archive)
        if not _archive_ok(archive): raise StudioError('Godot cached template archive is not trusted')
        return archive
    finally:
        partial.unlink(missing_ok=True)


def install_source_template(cache_dir:Path,opener=urllib.request.urlopen)->Path:
    archive=_download_archive(cache_dir,opener)
    target=cache_dir.resolve()/'android_source.zip'; staged=cache_dir.resolve()/'android_source.zip.part'; staged.unlink(missing_ok=True)
    with zipfile.ZipFile(archive) as zf:
        matches=[i for i in zf.infolist() if i.filename==SOURCE_MEMBER]
        if len(matches)!=1: raise StudioError('Godot Android source template missing')
        info=matches[0]; path=PurePosixPath(info.filename)
        if path.is_absolute() or '..' in path.parts or info.is_dir() or info.file_size<=0 or info.file_size>MAX_SOURCE_TEMPLATE_BYTES:
            raise StudioError('Godot Android source template rejected')
        with zf.open(info) as src, staged.open('wb') as dst: shutil.copyfileobj(src,dst)
    if staged.stat().st_size!=info.file_size or not _archive_ok(archive):
        staged.unlink(missing_ok=True); raise StudioError('Godot Android source template integrity check failed')
    staged.replace(target); return target


def _unsigned_preset(project:Path)->str:
    preset_path=project/'export_presets.cfg'
    if not preset_path.is_file() or preset_path.is_symlink(): raise StudioError('Godot Android export preset missing')
    text=preset_path.read_text(); preset=_preset_name(text)
    required={
        'gradle_build/use_gradle_build':'true',
        'gradle_build/export_format':'1',
        'package/signed':'false',
    }
    for key,value in required.items():
        pattern=re.compile(r'^'+re.escape(key)+r'=.*$',re.M)
        if not pattern.search(text): raise StudioError('Godot release preset missing option: '+key)
        text=pattern.sub(key+'='+value,text,count=1)
    preset_path.write_text(text); return preset


def build_unsigned_aab(project_root:Path,binary:Path,source_template:Path,artifact_path:Path,
                       runner=subprocess.run,timeout=1200)->dict:
    source=project_root.resolve(); binary=binary.resolve(); source_template=source_template.resolve()
    binary_hash=_trusted_binary_hash(binary)
    if not source_template.is_file() or source_template.is_symlink() or source_template.stat().st_size>MAX_SOURCE_TEMPLATE_BYTES:
        raise StudioError('Godot Android source template invalid')
    with tempfile.TemporaryDirectory(prefix='studio-godot-release-build-') as td:
        root=Path(td); project=root/'project'; home=root/'home'; output=root/'out'; project.mkdir(); home.mkdir(); output.mkdir()
        _copy_project(source,project); preset=_unsigned_preset(project)
        version_dir=home/'.local/share/godot/export_templates'/GODOT_VERSION.replace('-stable','.stable'); version_dir.mkdir(parents=True)
        shutil.copyfile(source_template,version_dir/'android_source.zip')
        aab=output/'app-unsigned.aab'
        command=['docker','run','--rm','--init','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=512','--memory=6g','--cpus=2','--network=none',
                 '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=1g','-v',str(project)+':/project:rw','-v',str(home)+':/home/studio:rw',
                 '-v',str(output)+':/out:rw','-v',str(binary)+':/opt/godot:ro','-e','HOME=/home/studio','-w','/project',IMAGE,
                 '/opt/godot','--headless','--path','/project','--install-android-build-template','--export-release',preset,'/out/app-unsigned.aab']
        try: result=runner(command,env=_host_env(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        except subprocess.TimeoutExpired: raise StudioError('Godot AAB export timed out') from None
        output_text=result.stdout.decode(errors='replace')[-32000:] if isinstance(result.stdout,bytes) else str(result.stdout or '')[-32000:]
        passed=result.returncode==0 and aab.is_file() and 0<aab.stat().st_size<=AAB_MAX_BYTES and 'ERROR:' not in output_text and 'Export failed' not in output_text
        digest=hashlib.sha256(aab.read_bytes()).hexdigest() if passed else None
        if passed:
            target=artifact_path.resolve(); target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(aab,target)
            if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
                target.unlink(missing_ok=True); raise StudioError('Preserved unsigned AAB hash mismatch')
        return {'passed':passed,'exit_code':result.returncode,'unsigned_aab_sha256':digest,'preset':preset,'engine_version':GODOT_VERSION,
                'binary_sha256':binary_hash,'network':'none','source_project':'not_mounted','signing_material_exposed':False}


def _valid_aab(path:Path)->bool:
    if not path.is_file() or path.is_symlink() or not 0<path.stat().st_size<=AAB_MAX_BYTES: return False
    try:
        with zipfile.ZipFile(path) as zf:
            names=set(zf.namelist())
            return 'BundleConfig.pb' in names and 'base/manifest/AndroidManifest.xml' in names
    except zipfile.BadZipFile:
        return False


def _sign_env(password:str)->dict[str,str]:
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','JAVA_HOME'}}
    env['STUDIO_AAB_STOREPASS']=password; env['STUDIO_AAB_KEYPASS']=password
    return env


def sign_aab(unsigned:Path,signed:Path,keystore:Path,alias:str,password:str,runner=subprocess.run)->dict:
    unsigned=unsigned.resolve(); signed=signed.resolve(); keystore=keystore.resolve()
    if not _valid_aab(unsigned): raise StudioError('Unsigned AAB structure invalid')
    if not keystore.is_file() or keystore.is_symlink(): raise StudioError('Release keystore unavailable')
    if not isinstance(alias,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',alias): raise StudioError('Release keystore alias invalid')
    if not isinstance(password,str) or not password: raise StudioError('Release keystore password missing')
    signed.parent.mkdir(parents=True,exist_ok=True); signed.unlink(missing_ok=True)
    env=_sign_env(password)
    sign=['jarsigner','-keystore',str(keystore),'-storepass:env','STUDIO_AAB_STOREPASS','-keypass:env','STUDIO_AAB_KEYPASS',
          '-signedjar',str(signed),str(unsigned),alias]
    result=runner(sign,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    if result.returncode or not _valid_aab(signed): signed.unlink(missing_ok=True); raise StudioError('AAB signing failed')
    verify=runner(['jarsigner','-verify','-verbose','-certs',str(signed)],env={k:v for k,v in env.items() if not k.startswith('STUDIO_AAB_')},
                  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    verify_text=verify.stdout.decode(errors='replace') if isinstance(verify.stdout,bytes) else str(verify.stdout or '')
    if verify.returncode or 'jar verified.' not in verify_text.lower(): signed.unlink(missing_ok=True); raise StudioError('Signed AAB verification failed')
    cert=runner(['keytool','-list','-v','-keystore',str(keystore),'-storepass:env','STUDIO_AAB_STOREPASS','-alias',alias],
                env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    cert_text=cert.stdout.decode(errors='replace') if isinstance(cert.stdout,bytes) else str(cert.stdout or '')
    match=CERT_RE.search(cert_text)
    if cert.returncode or not match: signed.unlink(missing_ok=True); raise StudioError('Upload certificate fingerprint unavailable')
    fingerprint=match.group(1).replace(':','').lower()
    if len(fingerprint)!=64: signed.unlink(missing_ok=True); raise StudioError('Upload certificate fingerprint invalid')
    return {'passed':True,'signed_aab_sha256':hashlib.sha256(signed.read_bytes()).hexdigest(),'certificate_sha256':fingerprint,
            'signing_scope':'artifact_only','project_code_had_signing_material':False,'verified_with':'jarsigner'}

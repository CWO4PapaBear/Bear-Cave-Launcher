"""PTR updater: pinned manifests, verified ZIPs and recoverable file replacement."""
from pathlib import Path
from contextlib import contextmanager
import csv, hashlib, io, json, os, re, shutil, stat, subprocess, sys, uuid, zipfile
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from package import managed_path, safe_file, sha
from . import rune_fix, baseline, fullclient

REPOSITORY = 'CWO4PapaBear/Bear-Cave-Launcher'
CHANNEL_URL = f'https://raw.githubusercontent.com/{REPOSITORY}/main/channels/ptr.json'
REPOSITORIES = {'ptr': REPOSITORY, 'area52': 'CWO4PapaBear/Area52-FreePick-Client'}

def repository(channel):
    if channel not in REPOSITORIES:raise ValueError('Unknown update channel')
    return REPOSITORIES[channel]

MAX_ASSET = 2 * 1024**3

def save_json(path, data):
    temp = path.with_name(path.name+'.new')
    if temp.is_symlink():
        raise ValueError('Linked state file is not allowed')
    with temp.open('w', encoding='utf-8') as out:
        json.dump(data, out, indent=2); out.flush(); os.fsync(out.fileno())
    os.replace(temp, path)

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def fetch(url, target=None, limit=8*1024**2, report=lambda message: None, progress=lambda done,total:None):
    if not url.startswith('https://'):
        raise ValueError('HTTPS required')
    request = Request(url, headers={'User-Agent':'BearCaveLauncher/0.2', 'Cache-Control':'no-cache'})
    with urlopen(request, timeout=45) as response:
        if not response.url.startswith('https://'):
            raise ValueError('Insecure download redirect')
        if int(response.headers.get('Content-Length', '0')) > limit:
            raise ValueError('Download exceeds expected size')
        size=0; memory=io.BytesIO(); stream=target.open('wb') if target else memory
        try:
            while True:
                block=response.read(1024*1024)
                if not block: break
                size+=len(block)
                if size>limit: raise ValueError('Download exceeds expected size')
                stream.write(block)
                progress(size,limit)
                if target: report(f'Downloading {target.name}: {size//1024**2} MB')
        finally:
            if target: stream.close()
        return None if target else memory.getvalue()

def valid_digest(value):
    return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value)

def validate_manifest(m,channel='ptr'):
    repo=repository(channel)
    if m.get('schema')==4:
        if channel!='area52':raise ValueError('Full client repair is Area 52 only')
        return fullclient.validate(m,repo)
    if m.get('schema') not in (1,2,3) or m.get('channel')!=channel:
        raise ValueError('Manifest belongs to another channel')
    if channel=='area52' and m.get('schema') not in (1,3):raise ValueError('Area 52 does not use PTR executable repairs')
    if m.get('schema')==3:
        if channel!='area52' or m.get('minimum_launcher_build') not in (305,306) or m.get('client_fixes'):raise ValueError('Invalid Area 52 baseline requirements')
        baseline.validate(m.get('baseline'))
    if m.get('schema') == 2:
        if m.get('client_fixes') != [rune_fix.FIX_ID] or m.get('minimum_launcher_build') != 301:
            raise ValueError('Unsupported client compatibility requirements')
    elif m.get('schema')!=3 and (m.get('client_fixes') or m.get('minimum_launcher_build')):
        raise ValueError('Client compatibility fixes require manifest schema 2')
    version=m.get('version','')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,70}',version) or m.get('tag')!=channel+'-'+version:
        raise ValueError('Invalid release identity')
    prefix=f'https://github.com/{repo}/releases/download/{m["tag"]}/'
    ids=set(); paths=set(); total=0
    components=m.get('components')
    if not isinstance(components,list) or not (0 if channel=='area52' else 1)<=len(components)<=100:
        raise ValueError('Invalid component list')
    for c in components:
        cid=c.get('id','')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,50}',cid) or cid in ids:
            raise ValueError('Duplicate/invalid component')
        ids.add(cid)
        if c.get('asset')!=cid+'.zip' or c.get('url')!=prefix+c['asset'] or not valid_digest(c.get('sha256')):
            raise ValueError('Unexpected release asset')
        if type(c.get('bytes')) is not int or not 0<c['bytes']<MAX_ASSET:
            raise ValueError('Invalid component size')
        if not isinstance(c.get('files'),list) or not 1<=len(c['files'])<=20000:
            raise ValueError('Invalid file list')
        for f in c['files']:
            managed_path(f['path'],channel)
            if f['path'].lower() in ('ascension.ok','data/patch-m.mpq','data/patch-s.mpq') and (m.get('schema')!=3 or m.get('minimum_launcher_build')!=306):
                raise ValueError('Base-client repairs require launcher 0.3.6')
            if f['path'].lower() in paths: raise ValueError('Duplicate managed file')
            paths.add(f['path'].lower())
            if type(f.get('bytes')) is not int or not 0<=f['bytes']<=4*1024**3 or not valid_digest(f.get('sha256')):
                raise ValueError('Invalid file size/hash')
            total+=f['bytes']
    if total>16*1024**3: raise ValueError('Release too large for this updater')
    if m.get('notes_url')!=prefix+'PATCH-NOTES.md': raise ValueError('Unexpected notes URL')
    return m

class ChannelUnavailable(ValueError):
    pass


def latest(channel='ptr'):
    repo=repository(channel)
    url=CHANNEL_URL if channel=='ptr' else f'https://raw.githubusercontent.com/{repo}/main/channels/{channel}.json'
    pointer=json.loads(fetch(url))
    if pointer.get('schema')!=1 or pointer.get('channel')!=channel: raise ValueError('Invalid PTR channel')
    if not pointer.get('enabled'): raise ChannelUnavailable(pointer.get('message','Updates are not published yet.'))
    url=pointer.get('manifest_url','')
    expected=f'https://github.com/{repo}/releases/download/'
    if not url.startswith(expected) or not re.fullmatch(re.escape(channel)+r'-[A-Za-z0-9._-]+/manifest.json',url[len(expected):]):
        raise ValueError('Unexpected manifest URL')
    raw=fetch(url)
    if not valid_digest(pointer.get('manifest_sha256')) or hashlib.sha256(raw).hexdigest()!=pointer['manifest_sha256']:
        raise ValueError('Manifest checksum mismatch')
    m=validate_manifest(json.loads(raw),channel)
    if url!=expected+m['tag']+'/manifest.json': raise ValueError('Manifest release mismatch')
    return m

def ensure_closed():
    if os.name=='nt':
        p=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,check=True,timeout=20,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        rows=csv.reader(io.StringIO(p.stdout))
        if any(row and row[0].lower() in ('wow.exe','wow-64.exe','ascension.exe') for row in rows):
            raise RuntimeError('Close WoW completely before updating or recovering files.')
    elif Path('/proc').is_dir():
        for directory in Path('/proc').iterdir():
            if not directory.name.isdigit(): continue
            try:
                args=(directory/'cmdline').read_bytes().decode(errors='replace').lower().split('\0')
                comm=(directory/'comm').read_text().strip().lower()
                if comm in ('wow.exe','wow-64.exe','ascension.exe') or any(a.replace('\\','/').rsplit('/',1)[-1] in ('wow.exe','wow-64.exe','ascension.exe') for a in args):
                    raise RuntimeError('Close WoW/Wine before updating or recovering files.')
            except (FileNotFoundError,ProcessLookupError): pass
            except PermissionError:
                raise RuntimeError('Cannot verify running processes; refusing client changes.')
    else: raise RuntimeError('Process checks support Windows and Linux only.')

def client_root(value,channel='ptr'):
    repository(channel)
    executable='Ascension.exe' if channel=='area52' else 'Wow.exe'
    root=Path(value).expanduser().resolve(strict=True)
    if not root.is_dir() or not ((root/executable).is_file() or (channel=='area52' and (root/'Data').is_dir())):
        raise ValueError('Select the dedicated client folder containing '+executable)
    return root

def state_dir(root,channel='ptr'):
    repository(channel)
    path=root/'.bear-cave-launcher'
    if path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):
        raise ValueError('Linked launcher state is not allowed')
    path.mkdir(exist_ok=True)
    # Never follow a substituted local state file/directory during recovery.
    for item in path.rglob('*'):
        if item.is_symlink() or (hasattr(item,'is_junction') and item.is_junction()):
            raise ValueError('Linked launcher state is not allowed')
    marker=path/'channel.json'
    if marker.exists() and read_json(marker).get('channel')!=channel:
        raise ValueError('This folder belongs to another channel')
    return path

@contextmanager
def locked(root,channel='ptr'):
    state=state_dir(root,channel)
    with (state/'update.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error: raise RuntimeError('Another launcher is using this client') from error
        try: yield state
        finally:
            if os.name=='nt':
                lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            else: fcntl.flock(lock,fcntl.LOCK_UN)

def changed(root,m,channel='ptr',report=lambda message:None):
    validate_manifest(m,channel); result=[]
    for c in m['components']:
        for f in c['files']:
            report('Checking '+f['path'])
            target=safe_file(root,f['path'])
            if not target.is_file() or target.stat().st_size!=f['bytes'] or sha(target)!=f['sha256']:
                result.append(c);break
    return result

def stored_file(base,relative):
    if relative != 'Wow.exe': managed_path(relative,full=True)
    # Flat internal names avoid duplicating long addon paths under backups/stage.
    return base/hashlib.sha256(relative.encode('utf-8')).hexdigest()[:32]

def transaction_file(root, relative):
    return rune_fix.target(root) if relative == 'Wow.exe' else safe_file(root, relative)

def pending_changes(root, manifest, channel='ptr'):
    parts = changed(root, manifest,channel)
    result = [dict(id=c['id'],bytes=c['bytes']) for c in parts]
    if manifest.get('schema')==4 and baseline.signature(root,manifest['baseline'])['extra_archives']:
        result.append(dict(id='quarantine-extra-archives',bytes=0))
    if channel=='ptr' and rune_fix.needed(root, manifest):
        result.append(dict(id='rune-recovery-client-fix',bytes=0))
    return result

def unpack(asset,component,stage):
    if asset.stat().st_size!=component['bytes'] or sha(asset)!=component['sha256']:
        raise ValueError('Archive checksum mismatch')
    expected={f['path']:f for f in component['files']}
    with zipfile.ZipFile(asset) as archive:
        members=archive.infolist()
        if len(members)!=len(expected) or {m.filename for m in members}!=set(expected):
            raise ValueError('Archive contents differ from manifest')
        for member in members:
            record=expected[member.filename]
            if member.is_dir() or stat.S_ISLNK(member.external_attr>>16) or member.file_size!=record['bytes']:
                raise ValueError('Invalid archive member')
            target=stored_file(stage,member.filename);target.parent.mkdir(parents=True,exist_ok=True)
            with archive.open(member) as source,target.open('wb') as out:
                count=0
                while block:=source.read(1024*1024):
                    count+=len(block)
                    if count>record['bytes']: raise ValueError('Expanded file exceeds manifest size')
                    out.write(block)
            if sha(target)!=record['sha256']: raise ValueError('File checksum mismatch')

def recover(root,guard=ensure_closed,report=lambda message:None,channel='ptr'):
    with locked(root,channel) as state:
        guard(); pending=state/'pending.json'
        if not pending.exists(): return 'No interrupted update to recover.'
        journal=read_json(pending);tx=journal['transaction']
        if not re.fullmatch(r'[0-9a-f]{32}',tx): raise ValueError('Invalid recovery journal')
        base=state/'transactions'/tx
        for f in reversed(journal['files']):
            guard(); target=transaction_file(root,f['path']); current=sha(target) if target.is_file() else None
            if current==f['before']: continue
            if current!=f['after']: raise RuntimeError('File changed outside launcher; recovery paused: '+f['path'])
            if f['before'] is None:
                target.unlink()
            else:
                backup=stored_file(base/'backup',f['path'])
                if sha(backup)!=f['before']: raise ValueError('Backup checksum mismatch')
                temp=base/'restore.tmp';shutil.copy2(backup,temp);os.replace(temp,target)
            report('Restored '+f['path'])
        if journal.get('previous_install') is not None:
            save_json(state/'installed.json',journal['previous_install'])
        elif (state/'installed.json').exists():
            (state/'installed.json').unlink()
        pending.unlink()
        return 'Previous client files restored.'

def install(root,m,download=fetch,guard=ensure_closed,report=lambda message:None,channel='ptr',progress=lambda phase,done,total:None):
    validate_manifest(m,channel);guard()
    try:
        with locked(root,channel) as state:
            if (state/'pending.json').exists(): raise RuntimeError('Recover the interrupted update first.')
            executable = rune_fix.target(root) if rune_fix.FIX_ID in m.get('client_fixes',[]) else None
            original = executable.read_bytes() if executable else None
            repaired = rune_fix.patched(original) if original is not None else None
            parts=changed(root,m,channel,report)
            extras=baseline.signature(root,m['baseline'])['extra_archives'] if m.get('schema')==4 else []
            if not parts and repaired is None and not extras: return channel+' client is up to date.'
            needed=sum(c['bytes']+sum(f['bytes']+(safe_file(root,f['path']).stat().st_size if safe_file(root,f['path']).is_file() else 0) for f in c['files']) for c in parts)+(len(repaired)*2 if repaired else 0)
            needed+=sum(safe_file(root,name).stat().st_size for name in extras)
            if m.get('schema')==4:needed-=fullclient.prepare_retry(state,parts)
            free=shutil.disk_usage(root).free
            if free<needed+128*1024**2: raise RuntimeError(f'Not enough free space for downloads and backups: {(needed+128*1024**2)/1024**3:.1f} GiB required, {free/1024**3:.1f} GiB available')
            tx=uuid.uuid4().hex;base=state/'transactions'/tx;base.mkdir(parents=True)
            stage=base/'stage';stage.mkdir();files=[]
            downloaded=0;download_total=sum(c['bytes'] for c in parts)
            def tracked_download(url,target,limit,report):
                if download is fetch:
                    def advance(done,total):
                        progress('Downloading',downloaded+done,download_total)
                        report(f'Downloading client files: {(downloaded+done)/1024**2:.0f} / {download_total/1024**2:.0f} MB')
                    return download(url,target=target,limit=limit,report=lambda message:None,progress=advance)
                return download(url,target=target,limit=limit,report=report)
            def chunk_done(size):
                nonlocal downloaded
                downloaded+=size;progress('Downloading',downloaded,download_total)
            if repaired is not None:
                backup=stored_file(base/'backup','Wow.exe');backup.parent.mkdir(parents=True,exist_ok=True)
                backup.write_bytes(original)
                stored_file(stage,'Wow.exe').write_bytes(repaired)
                original_hash=hashlib.sha256(original).hexdigest()
                repaired_hash=hashlib.sha256(repaired).hexdigest()
                if sha(backup)!=original_hash or sha(stored_file(stage,'Wow.exe'))!=repaired_hash:
                    raise ValueError('Rune repair staging verification failed')
                files.append(dict(path='Wow.exe',before=original_hash,after=repaired_hash))
            for c in parts:
                if m.get('schema')==4:
                    fullclient.stage(c,stored_file(stage,c['files'][0]['path']),state/'downloads',tracked_download,report,chunk_done)
                else:
                    asset=base/c['asset'];tracked_download(c['url'],target=asset,limit=c['bytes'],report=report)
                    unpack(asset,c,stage)
                    chunk_done(c['bytes'])
                for record in c['files']:
                    target=safe_file(root,record['path'])
                    before=sha(target) if target.is_file() else None
                    if before==record['sha256']: continue
                    if target.exists() and not target.is_file(): raise ValueError('File destination is a directory')
                    if before:
                        backup=stored_file(base/'backup',record['path']);backup.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copy2(target,backup)
                        if sha(backup)!=before: raise ValueError('Source changed during backup')
                    files.append(dict(path=record['path'],before=before,after=record['sha256']))
            for name in extras:
                target=safe_file(root,name);before=sha(target)
                backup=stored_file(base/'backup',name);backup.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(target,backup)
                if sha(backup)!=before:raise ValueError('Extra archive changed during backup')
                files.append(dict(path=name,before=before,after=None))
            guard()
            previous=read_json(state/'installed.json') if (state/'installed.json').exists() else None
            save_json(base/'files.json',files)
            save_json(state/'pending.json',dict(transaction=tx,files=files,previous_install=previous))
            for index,f in enumerate(files,1):
                guard();target=transaction_file(root,f['path'])
                if (sha(target) if target.is_file() else None)!=f['before']:
                    raise RuntimeError('Client changed during update: '+f['path'])
                target.parent.mkdir(parents=True,exist_ok=True)
                if f['after'] is None:
                    report('Quarantining extra archive '+f['path']);target.unlink()
                else:
                    report('Installing '+f['path']);os.replace(stored_file(stage,f['path']),target)
                if (sha(target) if target.is_file() else None)!=f['after']: raise RuntimeError('Installed file verification failed')
                progress('Installing',index,len(files))
            # The pending journal is retained until the full install commits.
            save_json(state/'channel.json',dict(channel=channel))
            save_json(state/'installed.json',dict(version=m['version'],transaction=tx))
            (state/'pending.json').unlink()
            if m.get('schema')==4:
                try:fullclient.clear_downloads(state)
                except (OSError,ValueError):report('Update installed; temporary downloads could not be removed.')
            report('Backup retained in '+str(base/'backup'))
            return channel+' updated to '+m['version']+'. Ready to play.'
    except Exception:
        # Leave pending journal for explicit recovery if WoW started meanwhile.
        pending=root/'.bear-cave-launcher/pending.json'
        if pending.exists():
            try: recover(root,guard,report,channel)
            except Exception as recovery: report('Recovery required: '+str(recovery))
        raise

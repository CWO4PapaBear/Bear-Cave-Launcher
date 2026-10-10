"""Verified Windows launcher updates, independent of game patch channels."""
from pathlib import Path, PurePosixPath
import hashlib,json,os,re,shutil,stat,subprocess,sys,time,uuid,zipfile
from urllib.request import Request,urlopen
from .updater import fetch,REPOSITORY
VERSION='0.3.9'
BUILD=309
URL=f'https://raw.githubusercontent.com/{REPOSITORY}/main/channels/launcher-win32.json'
MAX_ZIP=200*1024**2
MAX_UNPACKED=800*1024**2

def validate(data):
    if data.get('schema')!=1 or data.get('platform')!='win32':raise ValueError('Invalid launcher channel')
    if type(data.get('build')) is not int or data['build']<1:raise ValueError('Invalid build')
    v=data.get('version','')
    if not re.fullmatch(r'\d+\.\d+\.\d+',v):raise ValueError('Invalid version')
    expected=f'https://github.com/{REPOSITORY}/releases/download/launcher-{v}/BearCaveLauncher-update-win32.zip'
    if data.get('url')!=expected or not re.fullmatch(r'[0-9a-f]{64}',data.get('sha256','')):raise ValueError('Invalid launcher asset')
    if type(data.get('bytes')) is not int or not 0<data['bytes']<=MAX_ZIP:raise ValueError('Invalid download size')
    return data

def extract(archive,destination,info):
    if archive.stat().st_size!=info['bytes'] or hashlib.sha256(archive.read_bytes()).hexdigest()!=info['sha256']:raise ValueError('Launcher download checksum mismatch')
    if destination.exists():raise ValueError('Staging destination exists')
    with zipfile.ZipFile(archive) as z:
        entries=z.infolist();seen=set();total=0
        if not 1<=len(entries)<=10000:raise ValueError('Invalid archive entries')
        for item in entries:
            name=item.filename;parts=name.split('/')
            if (item.is_dir() or '\\' in name or any(not p or p in ('.','..') or p.endswith((' ','.')) or re.search(r'[<>:"|?*\x00-\x1f]',p) or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',p,re.I) for p in parts)
                or name.lower() in seen or stat.S_ISLNK(item.external_attr>>16)):raise ValueError('Unsafe launcher archive path')
            if not (parts[0]=='_internal' or len(parts)==1):raise ValueError('Unexpected launcher layout')
            if name.lower().endswith(('connection.json','connection-area52.json','access.json')):raise ValueError('Public launcher asset contains private connection settings')
            seen.add(name.lower());total+=item.file_size
        if total>MAX_UNPACKED or not {'bearcavelauncher.exe','launcher-version.json'}<=seen:raise ValueError('Incomplete/oversized launcher')
        metadata=json.loads(z.read('launcher-version.json'))
        if metadata!={'version':info['version'],'build':info['build']}:raise ValueError('Launcher identity mismatch')
        destination.mkdir()
        for item in entries:
            target=destination.joinpath(*PurePosixPath(item.filename).parts);target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(item) as source,target.open('xb') as out:shutil.copyfileobj(source,out)

def preserve_connection(root,payload):
    for name in ('connection.json','connection-area52.json'):
        for relative in ('_internal/'+name,name,'local/'+name):
            path=root/relative
            if path.exists():
                if path.is_symlink() or any(p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) for p in path.parents if p!=root.parent):raise ValueError('Linked connection configuration')
                target=payload/'_internal'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
                break


def log(message):
    try:
        folder=Path(os.getenv('LOCALAPPDATA') or Path.home()/'.config')/'BearCaveLauncher';folder.mkdir(parents=True,exist_ok=True)
        with (folder/'launcher-update.log').open('a',encoding='utf8')as out:out.write(time.strftime('%Y-%m-%d %H:%M:%S ')+str(message)+'\n')
    except OSError:pass # Logging must never block startup or trigger a second restart.


def startup(report=lambda message:None, progress=lambda phase,done,total:None, *, force=False):
    if not getattr(sys,'frozen',False) or sys.platform!='win32' or ('--skip-launcher-update' in sys.argv and not force):return False
    root=Path(sys.executable).resolve().parent;work=None;lock=root.parent/(root.name+'.update-lock')
    try:
        request=Request(URL,headers={'Cache-Control':'no-cache','User-Agent':'BearCaveLauncher/'+VERSION})
        with urlopen(request,timeout=5)as response:
            raw=response.read(65537)
            if len(raw)>65536:raise ValueError('Launcher channel too large')
        data=json.loads(raw)
        if data.get('enabled') is not True:return False
        info=validate(data)
        if info['build']<=BUILD:return False
        # Exclusive handoff lock prevents concurrent updater workers.
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
        work=root.parent/('bcu-'+uuid.uuid4().hex[:12]);work.mkdir()
        report('Updating launcher to '+info['version']+'. Please keep this window open.')
        progress('Downloading launcher',0,info['bytes'])
        archive=work/'download.zip';fetch(info['url'],archive,limit=info['bytes'],progress=lambda done,total:progress('Downloading launcher',done,total))
        report('Verifying and unpacking the launcher update...');progress('Verifying launcher',1,1)
        payload=work/'payload';extract(archive,payload,info);preserve_connection(root,payload)
        report('Checking the new launcher...');progress('Checking launcher',1,1)
        subprocess.run([str(payload/'BearCaveLauncher.exe'),'--self-test'],check=True,timeout=60)
        runner=work/'runner';shutil.copytree(payload,runner)
        job={'root':str(root),'parent_pid':os.getpid(),'compatibility':'--compatibility' in sys.argv}
        (work/'job.json').write_text(json.dumps(job))
        subprocess.Popen([str(runner/'BearCaveLauncher.exe'),'--apply-launcher-update',str(work/'job.json')],cwd=work,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        deadline=time.monotonic()+15
        while not (work/'worker-ready').exists():
            if time.monotonic()>deadline:raise RuntimeError('Update worker did not start')
            time.sleep(.1)
        report('Launcher update verified. Restarting into the new version...');progress('Restarting launcher',1,1)
        log('Verified '+info['version']+'; handing off installation')
        return True
    except FileExistsError:
        if force:raise RuntimeError('Launcher update already pending. Reopen the launcher when it finishes.')
        log('Launcher update already pending; using current installation')
    except Exception as error:
        report('Launcher update could not complete; current launcher remains available. '+str(error))
        log('Continuing current launcher: '+str(error))
        if work is not None and lock.exists():lock.unlink()
        if force:raise RuntimeError('Launcher version could not be verified or updated. Please try Play again. '+str(error)) from error
    return False

def validate_job(path):
    path=Path(path).resolve();work=path.parent;job=json.loads(path.read_text());root=Path(job['root'])
    if not root.is_absolute() or root.resolve()!=root or work.parent!=root.parent or not re.fullmatch(r'bcu-[0-9a-f]{12}',work.name):raise ValueError('Invalid update workspace')
    for p in [root,work,work/'payload',root.parent/(root.name+'.update-lock')]:
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):raise ValueError('Linked update path')
    if type(job['parent_pid']) is not int or job['parent_pid']<=0:raise ValueError('Invalid parent process')
    return work,root,job

def swap(work,root,check,restart):
    backup=work/'previous';payload=work/'payload'
    if backup.exists() or not (payload/'BearCaveLauncher.exe').is_file():raise ValueError('Invalid update state')
    root.rename(backup)
    try:
        payload.rename(root);check(root);restart(root)
    except BaseException:
        if root.exists():root.rename(work/'failed')
        backup.rename(root)
        raise

def apply(path):
    import ctypes
    work,root,job=validate_job(path);lock=root.parent/(root.name+'.update-lock')
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x00100000,False,job['parent_pid'])
    (work/'worker-ready').write_text('ready')
    try:
        if handle:
            try:
                if kernel.WaitForSingleObject(handle,60000)!=0:raise RuntimeError('Previous launcher did not exit')
            finally:kernel.CloseHandle(handle)
        def check(target):subprocess.run([str(target/'BearCaveLauncher.exe'),'--self-test'],check=True,timeout=60)
        def restart(target):
            command=[str(target/'BearCaveLauncher.exe'),'--skip-launcher-update']
            if job['compatibility']:command.append('--compatibility')
            subprocess.Popen(command,cwd=target)
        swap(work,root,check,restart)
        log('Launcher updated; previous installation retained at '+str(work/'previous'))
    except Exception as error:
        log('Launcher update failed; previous version retained: '+str(error))
        if (root/'BearCaveLauncher.exe').exists():
            command=[str(root/'BearCaveLauncher.exe'),'--skip-launcher-update']
            if job['compatibility']:command.append('--compatibility')
            subprocess.Popen(command,cwd=root)
    finally:
        if lock.exists():lock.unlink()

"""PTR realm setup; deployment address is supplied outside source control."""
from pathlib import Path
import json, os, re, shutil, uuid

def address(value):
    if not isinstance(value,str):raise ValueError('Invalid connection address')
    host,separator,port=value.partition(':')
    if separator and (not port.isdigit() or not 1<=int(port)<=65535):raise ValueError('Invalid auth port')
    if len(host)>253 or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?',host):
        raise ValueError('Invalid connection address')
    if any(not label or len(label)>63 or label.startswith('-') or label.endswith('-') for label in host.split('.')):
        raise ValueError('Invalid connection address')
    return value


def load(root,channel='ptr'):
    if channel not in ('ptr','area52'):raise ValueError('Unknown connection channel')
    name='connection.json' if channel=='ptr' else 'connection-area52.json'
    path=root/name
    if not path.exists():path=root/'local'/name
    if not path.is_file():
        raise ValueError('This launcher package has no PTR connection settings. Obtain the configured launcher from the server owner.')
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('channel')!=channel or data.get('schema')!=1:raise ValueError('Invalid PTR connection settings')
    return address(data.get('address'))

def safe(root,relative):
    target=root
    for part in Path(relative).parts:
        target=target/part
        if target.is_symlink() or (hasattr(target,'is_junction') and target.is_junction()):
            raise ValueError('Linked realm configuration paths are not allowed')
    if not target.resolve().is_relative_to(root.resolve()):raise ValueError('Realm configuration escapes client')
    return target

def native_windows():
    if os.name!='nt' or os.environ.get('WINEPREFIX') or os.environ.get('WINELOADERNOEXEC'):return False
    import ctypes
    try:
        getattr(ctypes.WinDLL('ntdll'),'wine_get_version')
        return False
    except AttributeError:return True
    except OSError:return False


def configure(root,state,host,guard,force_direct3d=True):
    """Caller holds updater.locked. Preserve originals and all unrelated settings."""
    host=address(host);guard()
    targets=[]
    data=safe(root,'Data')
    if data.is_dir():
        for directory in sorted(data.iterdir()):
            if re.fullmatch(r'[a-z]{2}[A-Z]{2}',directory.name) and directory.is_dir():
                targets.append(safe(root,'Data/'+directory.name+'/realmlist.wtf'))
    root_list=safe(root,'realmlist.wtf')
    if root_list.exists() or not targets:targets.append(root_list)
    config=safe(root,'WTF/Config.wtf')
    direct3d=force_direct3d and native_windows()
    if config.is_file() or direct3d:targets.append(config)
    changes=[]
    for target in targets:
        original=target.read_bytes() if target.exists() else None
        content=original or b''
        # Preserve arbitrary locale encodings and unrelated settings byte-for-byte.
        line=b'SET realmList "'+host.encode('ascii')+b'"'
        pattern=rb'(?im)^[ \t]*set[ \t]+realmlist[ \t]+[^\r\n]*'
        if re.search(pattern,content):updated=re.sub(pattern,lambda _:line,content)
        else:updated=content+(b'\r\n' if content and not content.endswith(b'\n') else b'')+line+b'\r\n'
        if target==config and direct3d:
            renderer=b'SET gxApi "D3D9"'
            api=rb'(?im)^[ \t]*set[ \t]+gxapi[ \t]+[^\r\n]*'
            if re.search(api,updated):updated=re.sub(api,lambda _:renderer,updated)
            else:updated+= (b'\r\n' if updated and not updated.endswith(b'\n') else b'')+renderer+b'\r\n'
        if updated!=original:changes.append((target,original,updated))
    if not changes:return
    backup=state/'realm-backups'/uuid.uuid4().hex;backup.mkdir(parents=True)
    for target,original,_ in changes:
        if original is not None:
            dest=backup/target.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original)
    written=[]
    try:
        for target,original,updated in changes:
            guard()
            if (target.read_bytes() if target.exists() else None)!=original:raise RuntimeError('Realm settings changed during setup')
            target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                with temp.open('xb') as stream:stream.write(updated);stream.flush();os.fsync(stream.fileno())
                os.replace(temp,target);written.append((target,original))
            finally:
                if temp.exists():temp.unlink()
    except Exception:
        for target,original in reversed(written):
            if original is None:target.unlink()
            else:target.write_bytes(original)
        raise

"""Read-only comparison with a reviewed Area 52 client baseline."""
import hashlib,re
from pathlib import PurePosixPath
RUNTIME={'ascension.exe','ascension.ok','extensions.dll','discord_game_sdk.dll','divxdecoder.dll','divxtac.dll','mmgr64.exe','wowerror.exe'}
def path_allowed(value):
    if not isinstance(value,str) or '\\' in value:return False
    parts=value.split('/')
    if any(not p or p in ('.','..') or p.endswith((' ','.')) or re.search(r'[<>:"|?*\x00-\x1f]',p) or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',p,re.I) for p in parts):return False
    low=value.lower()
    if (len(parts)==1 and low in RUNTIME) or (parts[0].lower()=='data' and len(parts) in (2,3) and (low.endswith('.mpq') or low=='data/area-52/listarchive')):return True
    from package import managed_path
    try:managed_path(value,'area52',full=True)
    except ValueError:return False
    return (low.startswith(('data/content/','data/enus/interface/cinematics/','interface/glues/'))
            or (low.startswith('interface/addons/blizzard_') and len(parts)==4 and low.endswith('.pub'))
            or (len(parts)==4 and parts[2].lower() in ('area52bundlestore','area52mysticrules') and low.endswith(('.lua','.toc'))))
def validate(records):
    if not isinstance(records,list) or not 1<=len(records)<=4000:raise ValueError('Invalid baseline file count')
    seen=set()
    for row in records:
        name=row.get('path')
        if not path_allowed(name) or name.lower() in seen:raise ValueError('Invalid/duplicate baseline path')
        seen.add(name.lower())
        if type(row.get('bytes')) is not int or not 0<=row['bytes']<=8*1024**3 or not re.fullmatch('[0-9a-f]{64}',row.get('sha256','')):raise ValueError('Invalid baseline hash or size')
    if 'ascension.exe' not in seen or 'extensions.dll' not in seen:raise ValueError('Baseline must identify the runtime pair')
def target(root,relative):
    if not path_allowed(relative):raise ValueError('Unsafe baseline path')
    path=root
    for part in PurePosixPath(relative).parts:
        path=path/part
        if path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):raise ValueError('Linked baseline file')
    return path
def signature(root,records):
    result={}
    for row in records:
        path=target(root,row['path'])
        st=path.stat() if path.is_file() else None
        result[row['path']]=(st.st_size,st.st_mtime_ns,st.st_ctime_ns) if st else None
    expected={row['path'].lower() for row in records}
    extras=[]
    data=root/'Data'
    if data.is_symlink() or (hasattr(data,'is_junction') and data.is_junction()):raise ValueError('Linked data directory')
    if data.is_dir():
        for folder in [data]+[p for p in data.iterdir() if p.is_dir() and not p.is_symlink() and not (hasattr(p,'is_junction') and p.is_junction())]:
            for p in folder.iterdir():
                if p.suffix.lower()=='.mpq' and p.relative_to(root).as_posix().lower() not in expected:
                    extras.append(p.relative_to(root).as_posix())
    result['extra_archives']=tuple(sorted(extras))
    return result
def compare(root,records,report=lambda message:None,progress=lambda done,total:None):
    validate(records);before=signature(root,records);mismatches=[dict(path=p,reason='unexpected archive') for p in before['extra_archives']]
    for index,row in enumerate(records,1):
        progress(index-1,len(records))
        report(f'Checking client baseline {index}/{len(records)}: {row["path"]}')
        path=target(root,row['path'])
        if not path.is_file():mismatches.append(dict(path=row['path'],reason='missing'));continue
        if path.stat().st_size!=row['bytes']:mismatches.append(dict(path=row['path'],reason='size differs'));continue
        with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=row['sha256']:mismatches.append(dict(path=row['path'],reason='hash differs'))
    if signature(root,records)!=before:raise ValueError('Client changed during verification; close the game and retry')
    progress(len(records),len(records))
    return mismatches,before

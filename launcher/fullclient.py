"""Area 52 full baseline repair using independently verified resumable chunks."""
import hashlib,re
from package import sha
from . import baseline

CHUNK_LIMIT=256*1024**2
TOTAL_LIMIT=100*1024**3

def validate(m,repo):
    if m.get('channel')!='area52' or m.get('minimum_launcher_build')!=307 or m.get('client_fixes'):
        raise ValueError('Full client repair requires launcher 0.3.7')
    version=m.get('version','')
    if not isinstance(version,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,70}',version) or m.get('tag')!='area52-'+version:
        raise ValueError('Invalid full client release identity')
    prefix=f'https://github.com/{repo}/releases/download/{m["tag"]}/'
    if m.get('notes_url')!=prefix+'PATCH-NOTES.md':raise ValueError('Invalid notes URL')
    baseline.validate(m.get('baseline'))
    records={f['path']:f for f in m['baseline']}
    components=m.get('components')
    if not isinstance(components,list) or len(components)!=len(records):raise ValueError('Incomplete baseline repair coverage')
    seen=set();ids=set();total=0
    for component in components:
        cid=component.get('id','')
        if not isinstance(cid,str) or not re.fullmatch(r'[a-z0-9-]{1,50}',cid) or cid in ids:raise ValueError('Invalid component identity')
        ids.add(cid)
        files=component.get('files')
        if not isinstance(files,list) or len(files)!=1:raise ValueError('Expected one file per full repair component')
        record=files[0];name=record.get('path')
        if name not in records or name in seen or record!=records[name]:raise ValueError('Repair does not match baseline')
        seen.add(name)
        if type(component.get('bytes')) is not int or component['bytes']!=record['bytes']:raise ValueError('Invalid component size')
        chunks=component.get('chunks')
        if not isinstance(chunks,list) or len(chunks)>64:raise ValueError('Invalid chunk count')
        count=0
        for index,chunk in enumerate(chunks):
            asset=f'{cid}-{index:03d}.bin'
            if chunk.get('asset')!=asset or chunk.get('url')!=prefix+asset:raise ValueError('Invalid chunk URL')
            if type(chunk.get('bytes')) is not int or not 0<chunk['bytes']<=CHUNK_LIMIT:raise ValueError('Invalid chunk size')
            if not isinstance(chunk.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',chunk['sha256']):raise ValueError('Invalid chunk checksum')
            count+=chunk['bytes']
        if count!=record['bytes']:raise ValueError('Chunks do not cover file')
        total+=count
    if total>TOTAL_LIMIT:raise ValueError('Full client release exceeds size limit')
    return m

def stage(component,target,cache,download,report,completed=lambda size:None):
    cache.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256();count=0
    with target.open('wb') as output:
        for chunk in component['chunks']:
            path=cache/chunk['sha256']
            if path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):raise ValueError('Linked download cache')
            valid=path.is_file() and path.stat().st_size==chunk['bytes'] and sha(path)==chunk['sha256']
            if not valid:
                pending=cache/(chunk['sha256']+'.partial')
                if pending.is_symlink():raise ValueError('Linked partial download')
                download(chunk['url'],target=pending,limit=chunk['bytes'],report=report)
                if pending.stat().st_size!=chunk['bytes'] or sha(pending)!=chunk['sha256']:raise ValueError('Chunk checksum mismatch')
                pending.replace(path)
            else:report('Reusing verified download '+chunk['asset'])
            with path.open('rb') as source:
                while block:=source.read(1024**2):
                    output.write(block);digest.update(block);count+=len(block)
            completed(chunk['bytes'])
    record=component['files'][0]
    if count!=record['bytes'] or digest.hexdigest()!=record['sha256']:raise ValueError('Assembled client file checksum mismatch')

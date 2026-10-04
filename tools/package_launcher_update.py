"""Build a public code-only launcher update from the configured local bundle."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from launcher.selfupdate import VERSION,BUILD,REPOSITORY,validate,extract

def prepare():
    source=ROOT/'dist/launcher/BearCaveLauncher';out=ROOT/'dist'/('launcher-'+VERSION)
    out.mkdir(exist_ok=False)
    metadata=json.loads((source/'launcher-version.json').read_text());assert metadata==dict(version=VERSION,build=BUILD)
    archive=out/'BearCaveLauncher-update-win32.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted(source.rglob('*')):
            if p.is_symlink() or (hasattr(p,'is_junction')and p.is_junction()):raise ValueError('Linked build file')
            if not p.is_file():continue
            rel=p.relative_to(source).as_posix()
            if rel.lower().endswith(('connection.json','connection-area52.json','access.json')):continue
            z.write(p,rel)
    info=dict(schema=1,enabled=True,platform='win32',version=VERSION,build=BUILD,
              url=f'https://github.com/{REPOSITORY}/releases/download/launcher-{VERSION}/{archive.name}',
              bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    validate(info);extract(archive,out/'verified-payload',info)
    assert not (out/'verified-payload/_internal/connection.json').exists()
    (out/'channel.json').write_text(json.dumps(info,indent=2)+'\n')
    print('PUBLIC CODE-ONLY BUNDLE VERIFIED:',out)
if __name__=='__main__':prepare()

"""Read-only local update planning. Does not download or install client files."""
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from launcher import rune_fix, updater
from package import safe_file, sha

def plan(client, manifest, channel):
    if manifest.get('schema') not in (1,2) or manifest['channel'] != channel:
        raise ValueError('Wrong schema or realm channel')
    if manifest.get('schema') == 2: updater.validate_manifest(manifest)
    changes=[]; seen=set()
    for component in manifest['components']:
        missing=[]
        for record in component['files']:
            key=record['path'].lower()
            if key in seen:
                raise ValueError('Duplicate managed path')
            seen.add(key)
            path=safe_file(client.resolve(),record['path'])
            if not path.is_file() or path.stat().st_size!=record['bytes'] or sha(path)!=record['sha256']:
                missing.append(record['path'])
        if missing:
            changes.append(dict(component=component['id'],download_bytes=component['bytes'],files=missing))
    if rune_fix.needed(client.resolve(),manifest):
        changes.append(dict(component='rune-recovery-client-fix',download_bytes=0,files=['Wow.exe']))
    return changes

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--client',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--channel',choices=['main','ptr'],required=True)
    a=p.parse_args();print(json.dumps(plan(a.client,json.loads(a.manifest.read_text(encoding='utf-8')),a.channel),indent=2))

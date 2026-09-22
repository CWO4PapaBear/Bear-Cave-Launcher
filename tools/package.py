"""Build allowlisted client components. Never reads credentials or uploads files."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re, shutil, uuid, zipfile

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def managed_path(value):
    if not isinstance(value, str) or '\\' in value:
        raise ValueError('Use relative forward-slash paths')
    path = PurePosixPath(value)
    parts = value.split('/')
    if any(p in ('', '.', '..') or p.endswith(('.', ' ')) or re.search(r'[<>:"|?*\x00-\x1f]', p)
           or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', p, re.I) for p in parts):
        raise ValueError('Unsafe path: ' + value)
    low = value.lower()
    addon = low.startswith('interface/addons/') and len(parts) >= 3
    patch = low in ('data/patch-z.mpq', 'data/enus/patch-enus-z.mpq')
    if not (addon or patch):
        raise ValueError('Outside managed addon/patch paths: ' + value)
    if any(p.lower() in ('savedvariables', '.git', 'backups') for p in parts):
        raise ValueError('Private/generated directory: ' + value)
    return path

def safe_file(root, relative):
    managed_path(relative)
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('Links/junctions are not distributable: ' + relative)
    if not current.resolve().is_relative_to(root):
        raise ValueError('File escapes client root')
    return current

def build(root, config, output, notes):
    root = root.resolve(); output = output.resolve()
    channel, version, repo = config['channel'], config['version'], config['repository']
    if channel not in ('main', 'ptr') or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,70}', version):
        raise ValueError('Invalid channel/version')
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid repository')
    if not config.get('server_build') or config['server_build'].startswith('REPLACE_'):
        raise ValueError('Record the approved server build first')
    if not notes.strip():
        raise ValueError('Release notes required')
    if output.exists() or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('Choose a new output folder outside the client')
    tag = channel + '-' + version
    base = f'https://github.com/{repo}/releases/download/{tag}/'
    manifest = dict(schema=1, channel=channel, version=version, tag=tag,
                    server_build=config['server_build'], realm_address=config.get('realm_address'),
                    components=[], notes_url=base+'PATCH-NOTES.md')
    used, ids = set(), set()
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.parent / ('.bear-package-' + uuid.uuid4().hex)
    temp.mkdir()
    try:
        for component in config['components']:
            cid = component['id']
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,50}', cid) or cid in ids:
                raise ValueError('Invalid/duplicate component ID')
            ids.add(cid); files = []
            asset = temp / (cid + '.zip')
            with zipfile.ZipFile(asset, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for relative in component['paths']:
                    path = safe_file(root, relative)
                    if not path.exists():
                        raise ValueError('Missing selected path: ' + relative)
                    paths = sorted(path.rglob('*')) if path.is_dir() else [path]
                    for item in paths:
                        rel = item.relative_to(root).as_posix(); safe_file(root, rel)
                        if item.is_dir():
                            continue
                        if not item.is_file():
                            raise ValueError('Not a regular file: ' + rel)
                        if rel.lower() in used:
                            raise ValueError('Duplicate or case-colliding path: ' + rel)
                        used.add(rel.lower())
                        if rel.lower().startswith('interface/') and item.suffix.lower() not in (
                                '.lua', '.toc', '.xml', '.blp', '.tga', '.png', '.jpg', '.ttf', '.otf', '.wav', '.ogg', '.mp3'):
                            raise ValueError('Unreviewed addon file type: ' + rel)
                        archive.write(item, rel)
                        files.append(dict(path=rel, bytes=item.stat().st_size, sha256=sha(item)))
            if not files:
                raise ValueError('Empty component: ' + cid)
            # Re-read ZIP payload to reject source changes during packaging.
            with zipfile.ZipFile(asset) as archive:
                for record in files:
                    h = hashlib.sha256(); count = 0
                    with archive.open(record['path']) as stream:
                        for block in iter(lambda: stream.read(1024*1024), b''):
                            h.update(block); count += len(block)
                    if count != record['bytes'] or h.hexdigest() != record['sha256']:
                        raise ValueError('Client changed during packaging; close WoW and retry')
            if asset.stat().st_size >= 2 * 1024**3:
                raise ValueError('Component exceeds GitHub asset limit; split it')
            manifest['components'].append(dict(id=cid, asset=asset.name, url=base+asset.name,
                                              bytes=asset.stat().st_size, sha256=sha(asset), files=files))
        if not manifest['components']:
            raise ValueError('No components')
        (temp/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
        (temp/'PATCH-NOTES.md').write_text(notes, encoding='utf-8')
        (temp/'SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(temp.iterdir())), encoding='utf-8')
        temp.rename(output)
    except BaseException:
        if temp.resolve().parent != output.parent or not temp.name.startswith('.bear-package-'):
            raise RuntimeError('Unexpected staging path; refusing cleanup')
        shutil.rmtree(temp)
        raise
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--notes', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.client, json.loads(args.config.read_text(encoding='utf-8-sig')),
                   args.output, args.notes.read_text(encoding='utf-8-sig'))
    print('PACKAGED', result['tag'], '— no client changes or uploads.')

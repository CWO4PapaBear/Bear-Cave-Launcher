"""Publish reviewed local packages using the owner's GitHub CLI login.

Draft creation and publication/channel promotion are separate explicit commands.
No GitHub token is ever placed in distributed client files.
"""
from pathlib import Path
import argparse, json, re, shutil, subprocess
from package import sha, managed_path

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, encoding='utf-8').stdout

def validate(folder, repo):
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    channel = manifest['channel']; version = manifest['version']
    if channel not in ('main', 'ptr') or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,70}', version):
        raise ValueError('Invalid release identity')
    tag = channel+'-'+version
    if manifest['tag'] != tag:
        raise ValueError('Tag mismatch')
    base = f'https://github.com/{repo}/releases/download/{tag}/'
    if manifest['notes_url'] != base+'PATCH-NOTES.md':
        raise ValueError('Package was built for a different repository')
    expected = {'manifest.json', 'PATCH-NOTES.md'}
    sums = {}
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        if not re.fullmatch(r'[a-zA-Z0-9._-]+', name) or not re.fullmatch(r'[0-9a-f]{64}', digest) or name in sums:
            raise ValueError('Invalid checksum record')
        sums[name] = digest
    seen = set()
    for component in manifest['components']:
        asset = component['asset']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,50}\.zip', asset) or asset in expected:
            raise ValueError('Invalid or duplicate asset')
        expected.add(asset)
        if component['url'] != base+asset or sha(folder/asset) != component['sha256'] or (folder/asset).stat().st_size != component['bytes']:
            raise ValueError('Asset checksum, size or URL mismatch')
        for record in component['files']:
            managed_path(record['path'])
            if record['path'].lower() in seen:
                raise ValueError('Duplicate managed file')
            seen.add(record['path'].lower())
    if not seen or set(sums) != expected:
        raise ValueError('Incomplete package/checksums')
    for name, digest in sums.items():
        if sha(folder/name) != digest:
            raise ValueError('Package changed: '+name)
    return manifest, sorted(expected | {'SHA256SUMS'})

def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['draft', 'publish'])
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--repo', default='CWO4PapaBear/Bear-Cave-Launcher')
    args = p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', args.repo):
        p.error('Invalid GitHub repository')
    gh = shutil.which('gh')
    if not gh:
        p.error('Install GitHub CLI and run gh auth login on your publishing computer.')
    manifest, assets = validate(args.package, args.repo)
    tag, channel = manifest['tag'], manifest['channel']
    run(gh, 'auth', 'status')
    if args.action == 'draft':
        # The release tag points at an explicitly pushed source commit.
        commit = run('git', '-C', str(ROOT), 'rev-parse', 'HEAD').strip()
        options = ['--prerelease'] if channel == 'ptr' else []
        run(gh, 'release', 'create', tag, *[str(args.package/name) for name in assets],
            '--repo', args.repo, '--target', commit, '--draft', '--latest=false',
            '--title', 'The Bear Cave '+tag, '--notes-file', str(args.package/'PATCH-NOTES.md'), *options)
        print('DRAFT uploaded. Review files and test the exact package before publishing.')
    else:
        # Draft tags may not resolve through the by-tag REST endpoint.
        pages = json.loads(run(gh, 'api', '--paginate', '--slurp', f'repos/{args.repo}/releases'))
        matches = [release for page in pages for release in page if release['tag_name'] == tag]
        if len(matches) != 1:
            raise ValueError('Expected exactly one release for '+tag)
        remote = matches[0]
        remote_assets = {a['name']: a for a in remote['assets']}
        # Keep verified downloads in the ignored local workspace. Some Windows
        # runtimes create inaccessible ACLs for TemporaryDirectory(mode=0700).
        import uuid
        from contextlib import nullcontext
        with nullcontext(ROOT/'local'/('release-review-'+uuid.uuid4().hex)) as td:
            td.mkdir(parents=True)
            for name in assets:
                item = remote_assets.get(name)
                if not item or item['state'] != 'uploaded':
                    raise ValueError('Remote asset missing/incomplete: '+name)
                # Do not rely on API digest availability. Verify downloaded bytes.
                run(gh, 'release', 'download', tag, '--repo', args.repo, '--pattern', name, '--dir', str(td))
                if sha(Path(td)/name) != sha(args.package/name):
                    raise ValueError('Remote asset differs: '+name)
        run(gh, 'release', 'edit', tag, '--repo', args.repo, '--draft=false', '--latest=false',
            '--prerelease='+('true' if channel == 'ptr' else 'false'))
        pointer = dict(schema=1, channel=channel, name='The Bear Cave'+(' — PTR' if channel=='ptr' else ''),
                       enabled=True, manifest_url=f'https://github.com/{args.repo}/releases/download/{tag}/manifest.json',
                       manifest_sha256=sha(args.package/'manifest.json'), message='Update available: '+manifest['version'])
        (ROOT/'channels'/f'{channel}.json').write_text(json.dumps(pointer, indent=2)+'\n', encoding='utf-8')
        print('Release published; local channel pointer prepared. Commit and push channels/'+channel+'.json to enable discovery.')

if __name__ == '__main__':
    main()

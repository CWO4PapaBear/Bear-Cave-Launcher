import base64
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

from publication_common import GitHub, save, sha, payload

GH = '/mnt/c/Program Files/GitHub CLI/gh.exe'
PYTHON = '/mnt/c/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'


def verify_commit(api, repo, branch, files, new, previous, journal=None, intent=None):
    """Retry reads only. A failed/uncertain ref write is never repeated here."""
    intent = dict(intent or {})
    last = {}
    for attempt, delay in enumerate((0, 1, 2, 4, 8), 1):
        if delay:
            time.sleep(delay)
        last = {'attempt': attempt, 'phase': 'branch-read', 'expected_commit': new}
        try:
            ref = api.api(f'repos/{repo}/git/ref/heads/{branch}', missing=True)
            actual = ref['object']['sha'] if ref else None
            last['observed_head'] = actual
            reachable = actual == new
            if actual and actual not in (new, previous):
                last['phase'] = 'ancestry-read'
                comparison = api.api(f'repos/{repo}/compare/{new}...{actual}')
                reachable = comparison.get('status') in ('ahead', 'identical')
            if reachable:
                last['phase'] = 'immutable-file-read'
                mismatches = {}
                # Check both the authored commit and any newer descendant. Never
                # accept a concurrent change that overwrote an allowlisted file.
                for revision in dict.fromkeys((new, actual)):
                    for path, expected in files.items():
                        content, _ = api.file(repo, path, revision)
                        if content != expected:
                            mismatches[revision + ':' + path] = {
                                'expected_sha256': sha(expected),
                                'actual_sha256': sha(content) if content is not None else None}
                last['mismatches'] = mismatches
                if not mismatches:
                    if journal:
                        save(journal, dict(intent, status='verified', verified_commit=actual, readback=last))
                    return actual
        except Exception as error:
            # Never include response bodies, credentials or arbitrary exception text.
            last['error_type'] = type(error).__name__
        if journal:
            save(journal, dict(intent, status='ref_update_attempted', readback=last))
    raise RuntimeError('Publication readback incomplete for ' + repo + ' branch ' + branch +
                       '; expected commit ' + new + '; observed head ' + str(last.get('observed_head')) +
                       '; phase ' + last['phase'] + '; mismatched paths ' +
                       ', '.join(last.get('mismatches', {})) +
                       '. No write was retried; reconcile using publication-only recovery.')


def commit_files(api, repo, branch, files, message, base=None, journal=None):
    scope = {'repo': repo, 'branch': branch, 'files': {path: sha(data) for path, data in files.items()}}
    if journal and Path(journal).exists():
        intent = json.loads(Path(journal).read_text())
        if any(intent.get(key) != value for key, value in scope.items()):
            raise RuntimeError('Publication commit journal differs from reviewed scope')
        return verify_commit(api, repo, branch, files, intent['new_commit'], intent.get('previous_head'), journal, intent)
    ref = api.api(f'repos/{repo}/git/ref/heads/{branch}', missing=True)
    if ref:
        head = ref['object']['sha']
        if all(api.file(repo, name, head)[0] == content for name, content in files.items()):
            if journal:
                save(journal, dict(scope, status='verified', new_commit=head, verified_commit=head, previous_head=head))
            return head
        if base and head != base:
            raise RuntimeError('Existing source branch differs from the prepared payload')
    else:
        if not base:
            raise RuntimeError('Missing publication branch')
        head = base
    commit = api.api(f'repos/{repo}/git/commits/{head}')
    tree = []
    for path, content in files.items():
        blob = api.api(f'repos/{repo}/git/blobs', {'content': base64.b64encode(content).decode(), 'encoding': 'base64'})
        tree.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    created = api.api(f'repos/{repo}/git/trees', {'base_tree': commit['tree']['sha'], 'tree': tree})
    new = api.api(f'repos/{repo}/git/commits', {'message': message, 'tree': created['sha'], 'parents': [head]})['sha']
    intent = dict(scope, status='ref_update_attempted', new_commit=new, previous_head=head)
    if journal:
        save(journal, intent)  # Durable before the uncertain remote mutation.
    try:
        if ref:
            api.api(f'repos/{repo}/git/refs/heads/{branch}', {'sha': new, 'force': False}, method='PATCH')
        else:
            api.api(f'repos/{repo}/git/refs', {'ref': 'refs/heads/' + branch, 'sha': new})
    except Exception as error:
        # A timeout can follow a successful write. Reconcile, never send it twice.
        intent['write_error_type'] = type(error).__name__
    return verify_commit(api, repo, branch, files, new, head, journal, intent)


def resume_journal(api, repo, branch, journal):
    """Recover exact generated notes from their immutable authored commit."""
    intent = json.loads(Path(journal).read_text())
    if intent.get('repo') != repo or intent.get('branch') != branch:
        raise RuntimeError('Publication journal repository or branch differs')
    files = {}
    for path, expected in intent['files'].items():
        content, _ = api.file(repo, path, intent['new_commit'])
        if content is None or sha(content) != expected:
            raise RuntimeError('Immutable publication journal payload differs: ' + path)
        files[path] = content
    return commit_files(api, repo, branch, files, '', journal=journal)


def preflight(api, root, config):
    for name in ('render_progress.py', 'CertificationIcon.tga'):
        if not (root / name).is_file():
            raise RuntimeError('Missing packaged progress renderer asset: ' + name)
    for repo in (config['source_repo'], config['notes_repo']):
        info = api.api(f'repos/{repo}')
        if not info.get('permissions', {}).get('push'):
            raise RuntimeError('No publication permission for ' + repo)
    secrets = api.api(f"repos/{config['notes_repo']}/actions/secrets")
    if 'DISCORD_PATCH_NOTES_WEBHOOK' not in {v['name'] for v in secrets['secrets']}:
        raise RuntimeError('Missing configured Discord secret')
    subprocess.run([PYTHON, '-c', 'from PIL import Image, ImageDraw, ImageFont'], check=True, capture_output=True)
    for record in config['source_files']:
        if sha((root / record['artifact']).read_bytes()) != record['sha256']:
            raise RuntimeError('Publication source artifact changed')
    validate_source_branch(api, root, config)
    payload(config, (root / 'notes.md').read_text(encoding='utf-8-sig'), False)
    print('Publication preflight passed: repositories, auth, webhook-secret presence, source hashes and renderer; no publication.')


def validate_source_branch(api, root, config):
    ref = api.api(f"repos/{config['source_repo']}/git/ref/heads/{config['source_branch']}", missing=True)
    if ref and ref['object']['sha'] != config['source_base']:
        head = ref['object']['sha']
        if not all(api.file(config['source_repo'], record['path'], head)[0]
                   == (root / record['artifact']).read_bytes() for record in config['source_files']):
            raise RuntimeError('Existing source branch differs from the prepared payload')


def main():
    root = Path(os.environ['AREA52_PACKAGE_DIR']) / 'publication'
    transaction = Path(os.environ['AREA52_TRANSACTION_DIR'])
    config = json.loads((root / 'config.json').read_text())
    api = GitHub(GH)
    if sys.argv[1] == 'preflight':
        preflight(api, root, config)
        return
    state = json.loads((transaction / 'state.json').read_text())
    if state['status'] not in ('server_ready', 'publish_failed'):
        raise RuntimeError('Publication requires successfully deployed server')
    current = subprocess.check_output(['docker', 'exec', 'ascension-freepick-worldserver', 'sha256sum', '/proc/1/exe'], text=True).split()[0]
    if current != config['server_sha256']:
        raise RuntimeError('Running server is not the qualified package')
    receipts = transaction / 'publication'
    receipts.mkdir(exist_ok=True)
    source_files = {x['path']: (root / x['artifact']).read_bytes() for x in config['source_files']}
    source_commit = commit_files(api, config['source_repo'], config['source_branch'], source_files,
                                 'Publish deployed ' + config['title'], config['source_base'], receipts / 'source-commit-intent.json')
    save(receipts / 'source.json', {'commit': source_commit, 'repo': config['source_repo'], 'branch': config['source_branch']})
    prefix = f"docs/publication/{config['id']}"
    notes_journal = receipts / 'notes-commit-intent.json'
    notes_revision = 'main'
    if notes_journal.exists():
        notes_revision = resume_journal(api, config['notes_repo'], 'main', notes_journal)
        save(receipts / 'notes.json', {'commit': notes_revision, 'url': config['notes_url']})
    remote_config, _ = api.file(config['notes_repo'], prefix + '/config.json', notes_revision)
    remote_receipt, _ = api.file(config['notes_repo'], prefix + '/discord-receipt.json')
    if remote_receipt and json.loads(remote_receipt)['status'] == 'complete':
        save(receipts / 'discord.json', json.loads(remote_receipt))
        print('GitHub publication and Discord delivery already verified.')
        return
    if not remote_config:
        subprocess.run(['python3', str(root / 'snapshot.py'), 'aggregate', str(receipts)], check=True)
        snapshot_script = subprocess.check_output(['wslpath', '-w', str(root / 'render_progress.py')], text=True).strip()
        snapshot_folder = subprocess.check_output(['wslpath', '-w', str(receipts)], text=True).strip()
        subprocess.run([PYTHON, snapshot_script, snapshot_folder], check=True)
        progress = json.loads((receipts / 'progress.json').read_text())
        safe_progress = {k: v for k, v in progress.items() if k != 'sources'}
        safe_progress['source_hashes'] = {k: v.get('sha256', v.get('result_sha256')) for k, v in progress['sources'].items()}
        files = {prefix + '/config.json': json.dumps(config).encode(),
                 prefix + '/notes.md': (root / 'notes.md').read_bytes(),
                 prefix + '/progress.json': json.dumps(safe_progress, indent=2).encode(),
                 prefix + '/progress.png': (receipts / 'progress.png').read_bytes(),
                 'tools/area52_publication/announce_package.py': (root / 'announce_package.py').read_bytes(),
                 'tools/area52_publication/publication_common.py': (root / 'publication_common.py').read_bytes(),
                 '.github/workflows/area52-package-notes.yml': (root / 'area52-package-notes.yml').read_bytes()}
        for day, first_package in config.get('known_daily_first', {}).items():
            daily = f'docs/publication/daily/{day}.json'
            if api.file(config['notes_repo'], daily)[0] is None:
                files[daily] = json.dumps({'date': day, 'first_package': first_package,
                                          'status': 'historical_delivery_confirmed'}).encode()
        notes_commit = commit_files(api, config['notes_repo'], 'main', files, 'Publish deployed patch notes: ' + config['title'],
                                    journal=receipts / 'notes-commit-intent.json')
        save(receipts / 'notes.json', {'commit': notes_commit, 'url': config['notes_url']})
    elif json.loads(remote_config) != config:
        raise RuntimeError('Published package configuration differs; refuse overwrite')
    intent = receipts / 'dispatch.json'
    workflow = f"repos/{config['notes_repo']}/actions/workflows/area52-package-notes.yml"
    def runs():
        return [r for r in api.api(workflow + '/runs?event=workflow_dispatch&per_page=100')['workflow_runs']
                if r['display_title'] == 'Area52 publication ' + config['id']]
    existing = runs()
    if (existing and existing[0]['status'] == 'completed' and remote_receipt
            and json.loads(remote_receipt).get('message_id')):
        api.api(f"repos/{config['notes_repo']}/actions/runs/{existing[0]['id']}/rerun-failed-jobs", {})
        time.sleep(10)
    if not existing and not intent.exists():
        save(intent, {'status': 'intent', 'package_id': config['id']})
        api.api(workflow + '/dispatches', {'ref': 'main', 'inputs': {'package_id': config['id']}})
    elif not existing:
        raise RuntimeError('Workflow dispatch outcome uncertain; inspect GitHub before dispatching again')
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        existing = runs()
        if existing:
            run = existing[0]
            save(intent, {'run_id': run['id'], 'url': run['html_url'], 'status': run['status']})
            if run['status'] == 'completed':
                receipt, _ = api.file(config['notes_repo'], prefix + '/discord-receipt.json')
                if receipt and json.loads(receipt)['status'] == 'complete':
                    save(receipts / 'discord.json', json.loads(receipt))
                    print('Source, notes and Discord publication verified.')
                    return
                raise RuntimeError('Discord workflow needs reconciliation: ' + run['html_url'] + '; do not repost')
        time.sleep(10)
    raise RuntimeError('Workflow still pending; use publication-only resume later')


if __name__ == '__main__':
    main()

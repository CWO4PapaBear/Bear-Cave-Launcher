import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


class GitHub:
    def __init__(self, executable='gh'):
        self.executable = executable

    def api(self, endpoint, data=None, method=None, missing=False):
        args = [self.executable, 'api', endpoint, '--method', method or ('POST' if data is not None else 'GET')]
        if data is not None:
            args += ['--input', '-']
        result = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                                text=True, capture_output=True, timeout=120)
        if result.returncode:
            if missing and 'HTTP 404' in result.stderr:
                return None
            raise RuntimeError('GitHub operation failed: ' + endpoint.split('?')[0] + ' (credentials withheld)')
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def file(self, repo, path, ref='main'):
        value = self.api(f'repos/{repo}/contents/{path}?ref={ref}', missing=True)
        if not value:
            return None, None
        revision = value['sha']
        size = value['size'] if 'size' in value else None
        if value.get('encoding') == 'none':
            value = self.api(f'repos/{repo}/git/blobs/{revision}')
        if value.get('encoding', 'base64') != 'base64':
            raise RuntimeError('Unsupported GitHub file encoding')
        content = base64.b64decode(''.join(value['content'].split()), validate=True)
        digest = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if digest != revision or (size is not None and len(content) != size):
            raise RuntimeError('GitHub file integrity verification failed')
        return content, revision

    def put(self, repo, path, content, message, branch='main'):
        old, revision = self.file(repo, path, branch)
        if old == content:
            return None
        body = {'message': message, 'content': base64.b64encode(content).decode(), 'branch': branch}
        if revision:
            body['sha'] = revision
        return self.api(f'repos/{repo}/contents/{path}', body, method='PUT')


def payload(config, notes, first):
    if '| Category |' in notes or '| VERIFIED |' in notes:
        raise RuntimeError('Discord progress tables are prohibited')
    if len(notes) > 3800:
        raise RuntimeError('Discord notes too long')
    value = {'username': 'The Bear Cave - Updates',
             'avatar_url': 'https://raw.githubusercontent.com/CWO4PapaBear/Bear-Cave-Launcher/main/ui/assets/bear-cave-app-icon.png',
             'content': '<@&1551989024833667072> **Area 52 patch notes — ' + config['title'] + '**',
             'allowed_mentions': {'parse': [], 'roles': ['1551989024833667072']},
             'embeds': [{'title': config['title'], 'description': notes, 'color': 0xD5A546,
                         'url': config['notes_url']}]}
    if first:
        value['attachments'] = [{'id': 0, 'filename': 'making-progress.png',
                                 'description': 'Making Progress: current Area 52 engineering verification and tester certification totals.'}]
        value['embeds'][0]['image'] = {'url': 'attachment://making-progress.png'}
    return value

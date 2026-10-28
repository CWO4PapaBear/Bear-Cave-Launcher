import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import uuid
from zoneinfo import ZoneInfo

from publication_common import GitHub, payload, save, sha


def verify_image(message, expected):
    urls = [a['url'] for a in message.get('attachments', [])]
    urls += [e['image']['url'] for e in message.get('embeds', []) if e.get('image')]
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in ('cdn.discordapp.com', 'media.discordapp.net'):
            continue
        with urlopen(Request(url, headers={'User-Agent': 'BearCavePublisher/1.0'}), timeout=30) as response:
            if sha(response.read()) == expected:
                return
    raise RuntimeError('Uploaded progress image hash not confirmed')


def deliver(config, root, api, webhook, now=None):
    repo, package = config['notes_repo'], config['id']
    date = (now or datetime.now(ZoneInfo('America/Los_Angeles'))).strftime('%Y-%m-%d')
    receipt_path = f'docs/publication/{package}/discord-receipt.json'
    old, _ = api.file(repo, receipt_path)
    receipt = json.loads(old) if old else None
    if receipt and receipt['status'] == 'complete':
        save('discord-receipt.json', receipt)
        return receipt
    if receipt and receipt['status'] == 'intent' and not receipt.get('message_id'):
        raise RuntimeError('Previous send outcome uncertain. Recover existing message ID; never repost blindly.')
    with urlopen(Request(webhook, headers={'User-Agent': 'BearCavePublisher/1.0'}), timeout=30) as response:
        destination = json.loads(response.read())
    if destination.get('channel_id') != config['discord_channel']:
        raise RuntimeError('Unexpected Discord destination')
    daily_path = f'docs/publication/daily/{date}.json'
    daily_raw, _ = api.file(repo, daily_path)
    first = daily_raw is None
    if receipt:
        first = receipt['includes_progress']
        date = receipt['reporting_date']
    if first:
        progress = json.loads((root / 'progress.json').read_text())
        if progress['reporting_date'] != date:
            raise RuntimeError('Progress snapshot is not from this Pacific reporting day')
    notes = (root / 'notes.md').read_text(encoding='utf-8-sig')
    data = payload(config, notes, first)
    image = (root / 'progress.png').read_bytes() if first else b''
    if not receipt:
        receipt = {'status': 'intent', 'package_id': package, 'reporting_date': date,
                   'includes_progress': first, 'channel_id': destination['channel_id'],
                   'guild_id': destination.get('guild_id'), 'content_sha256': sha(json.dumps(data).encode()),
                   'image_sha256': sha(image) if first else None}
        api.put(repo, receipt_path, json.dumps(receipt).encode(), 'Reserve Discord publication ' + package)
        if first:
            api.put(repo, daily_path, json.dumps({'first_package': package, 'status': 'reserved',
                                                'date': date}).encode(), 'Reserve daily progress ' + date)
        boundary = 'BearCave' + uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n'.encode()
                + json.dumps(data).encode())
        if first:
            body += (f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="making-progress.png"\r\nContent-Type: image/png\r\n\r\n'.encode() + image)
        body += f'\r\n--{boundary}--\r\n'.encode()
        request = Request(webhook + '?wait=true', data=body,
                          headers={'Content-Type': 'multipart/form-data; boundary=' + boundary,
                                   'User-Agent': 'BearCavePublisher/1.0'}, method='POST')
        try:
            with urlopen(request, timeout=30) as response:
                message = json.loads(response.read())
        except Exception:
            raise RuntimeError('Discord send outcome uncertain; inspect reserved receipt before recovery') from None
        receipt['message_id'] = message['id']
        receipt['status'] = 'sent'
        save('discord-receipt.json', receipt)
        api.put(repo, receipt_path, json.dumps(receipt).encode(), 'Record sent Discord message ' + package)
    request = Request(webhook + '/messages/' + receipt['message_id'], headers={'User-Agent': 'BearCavePublisher/1.0'})
    with urlopen(request, timeout=30) as response:
        message = json.loads(response.read())
    actual_notes = message.get('embeds', [{}])[0].get('description', '')
    if message.get('content') != data['content'] or actual_notes.strip() != notes.strip():
        raise RuntimeError('Discord message text readback differs: ' + repr({
            'expected_content': data['content'], 'actual_content': message.get('content'),
            'expected_description': notes, 'actual_description': actual_notes}))
    if first:
        verify_image(message, receipt['image_sha256'])
    receipt['status'] = 'complete'
    if receipt.get('guild_id'):
        receipt['url'] = f"https://discord.com/channels/{receipt['guild_id']}/{receipt['channel_id']}/{receipt['message_id']}"
    save('discord-receipt.json', receipt)
    api.put(repo, receipt_path, json.dumps(receipt).encode(), 'Verify Discord publication ' + package)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    args = parser.parse_args()
    if not all(c.islower() or c.isdigit() or c == '-' for c in args.package):
        raise RuntimeError('Invalid package ID')
    root = Path('docs/publication') / args.package
    config = json.loads((root / 'config.json').read_text())
    if config['id'] != args.package:
        raise RuntimeError('Package ID differs')
    deliver(config, root, GitHub(), os.environ['DISCORD_PATCH_NOTES_WEBHOOK'])


if __name__ == '__main__':
    main()

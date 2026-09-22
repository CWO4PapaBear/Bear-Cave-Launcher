"""Announce the promoted public PTR release; never print webhook credentials."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from launcher import updater


def payload(manifest, notes):
    release = f"https://github.com/{updater.REPOSITORY}/releases/tag/{manifest['tag']}"
    # Leave room for the title and update instructions within Discord embed limits.
    description = notes.strip()
    if len(description) > 3400:
        description = description[:3300].rsplit('\n', 1)[0] + '\n\nRead the full patch notes at the release link.'
    return {
        'username': 'The Bear Cave - PTR Updates',
        'avatar_url': 'https://raw.githubusercontent.com/CWO4PapaBear/Bear-Cave-Launcher/main/ui/assets/bear-cave-app-icon.png',
        'allowed_mentions': {'parse': []},
        'content': '\U0001f43e **PTR update available**',
        'embeds': [{
            'title': 'The Bear Cave PTR - ' + manifest['version'],
            'url': release,
            'description': description,
            'color': 0xD5A546,
            'fields': [{'name': '\U0001f6e0 How to update',
                        'value': 'Close WoW → Open launcher → Check / Repair → Update PTR → Play.'}],
            'footer': {'text': 'PTR only • Main Server unchanged'},
        }],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    local = updater.read_json(ROOT/'channels/ptr.json')
    if not local.get('enabled'):
        print('PTR disabled; no announcement.'); return
    # Verify public discovery and pinned manifest before announcing availability.
    public = json.loads(updater.fetch(updater.CHANNEL_URL))
    if public != local:
        raise ValueError('This checkout is not the current published PTR pointer; no announcement.')
    manifest = updater.latest()
    release_url = f"https://api.github.com/repos/{updater.REPOSITORY}/releases/tags/{manifest['tag']}"
    release = json.loads(updater.fetch(release_url))
    if release.get('draft', True) or not release.get('published_at'):
        raise ValueError('Release is not published; no announcement.')
    notes = updater.fetch(manifest['notes_url'], limit=256*1024).decode('utf-8-sig')
    data = payload(manifest, notes)
    if args.dry_run:
        print(json.dumps(data, ensure_ascii=True, indent=2)); return
    webhook = os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK', '').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+', webhook):
        raise ValueError('Set the DISCORD_PATCH_NOTES_WEBHOOK repository secret to a Discord webhook URL.')
    request = Request(webhook+'?wait=true', data=json.dumps(data).encode(),
                      headers={'Content-Type': 'application/json', 'User-Agent': 'BearCavePTRPublisher/1.0'}, method='POST')
    try:
        with urlopen(request, timeout=30) as response:
            message = json.loads(response.read())
        if not message.get('id'):
            raise ValueError('Discord did not confirm a message ID.')
    except HTTPError as error:
        raise RuntimeError(f'Discord returned HTTP {error.code}. No automatic retry; review the channel before rerunning.') from None
    except Exception:
        raise RuntimeError('Discord delivery was not confirmed. Review the channel before rerunning to avoid duplicate posts.') from None
    print('Discord confirmed the PTR patch notes message.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Only our own validation errors are safe; URL/network exceptions may contain secrets.
        if isinstance(error, (ValueError, RuntimeError)):
            print(str(error), file=sys.stderr)
        else:
            print('Announcement validation or network request failed. No credentials logged.', file=sys.stderr)
        sys.exit(1)

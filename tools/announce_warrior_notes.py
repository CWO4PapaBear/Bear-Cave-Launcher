"""Explicitly dispatched status notes; does not announce or promote client availability."""
import argparse,json,os,re,sys
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
def payload(notes):
    if not notes.strip() or len(notes)>3900:raise ValueError('Invalid note length')
    return dict(username='The Bear Cave - PTR Updates',
        avatar_url='https://raw.githubusercontent.com/CWO4PapaBear/Bear-Cave-Launcher/main/ui/assets/bear-cave-app-icon.png',
        allowed_mentions={'parse':[]},content='🐾 **PTR Warrior patch notes**',
        embeds=[dict(title='Charge and Thunder Clap — PTR server update',
            url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/PTR-WARRIOR-STANCE-NOTES.md',
            description=notes.strip(),color=0xD5A546,
            footer={'text':'Server active • Matching launcher client release pending • Main unchanged'})])
def main():
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    data=payload((ROOT/'docs/PTR-WARRIOR-STANCE-NOTES.md').read_text(encoding='utf-8'))
    if a.dry_run:print(json.dumps(data,ensure_ascii=True,indent=2));return
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise ValueError('Patch notes webhook secret unavailable')
    request=Request(webhook+'?wait=true',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePTRPublisher/1.0'},method='POST')
    try:
        with urlopen(request,timeout=30) as response:message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError('Missing confirmation')
    except Exception:raise RuntimeError('Discord delivery was not confirmed. Inspect the channel before retrying; no automatic retry.') from None
    print('Discord confirmed the Warrior patch notes message.')
if __name__=='__main__':
    try:main()
    except Exception as e:
        print(str(e) if isinstance(e,(ValueError,RuntimeError)) else 'Announcement failed; credentials withheld.',file=sys.stderr);sys.exit(1)

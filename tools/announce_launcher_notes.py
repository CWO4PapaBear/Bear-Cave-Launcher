from pathlib import Path
import argparse,json,os,re
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    channel=json.loads((ROOT/'channels/launcher-win32.json').read_text())
    if channel.get('version')!='0.3.4' or not channel.get('enabled'):raise RuntimeError('Launcher 0.3.4 is not promoted')
    notes=(ROOT/'docs/LAUNCHER-0.3.4.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',allowed_mentions={'parse':[]},embeds=[dict(title='Launcher 0.3.4 - Area 52 Alpha',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/releases/tag/launcher-0.3.4')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCaveLauncherPublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response: message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed launcher patch notes; message ID: '+str(message['id']))
if __name__=='__main__':main()

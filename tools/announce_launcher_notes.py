from pathlib import Path
import argparse,hashlib,json,os,re,sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from launcher import updater,fullclient

def verify_live():
    launcher=json.loads(updater.fetch('https://raw.githubusercontent.com/CWO4PapaBear/Bear-Cave-Launcher/main/channels/launcher-win32.json'))
    if launcher.get('version')!='0.3.8' or not launcher.get('enabled'):
        raise RuntimeError('Launcher 0.3.8 is not publicly promoted')
    repo='CWO4PapaBear/Area52-FreePick-Client'
    tag='area52-0.1.0-alpha.4'
    pointer=json.loads(updater.fetch(f'https://raw.githubusercontent.com/{repo}/main/channels/area52.json'))
    expected=f'https://github.com/{repo}/releases/download/{tag}/manifest.json'
    if not pointer.get('enabled') or pointer.get('manifest_url')!=expected:
        raise RuntimeError('Full Area 52 client is not publicly promoted; no announcement')
    raw=updater.fetch(expected)
    if hashlib.sha256(raw).hexdigest()!=pointer.get('manifest_sha256'):
        raise RuntimeError('Public client manifest hash differs; no announcement')
    manifest=json.loads(raw);fullclient.validate(manifest,repo)
    if manifest.get('tag')!=tag or len(manifest['baseline'])!=504:
        raise RuntimeError('Unexpected client package; no announcement')
    for repository,release_tag in ((repo,tag),('CWO4PapaBear/Bear-Cave-Launcher','launcher-0.3.8')):
        release=json.loads(updater.fetch(f'https://api.github.com/repos/{repository}/releases/tags/{release_tag}'))
        if release.get('draft',True) or not release.get('published_at'):
            raise RuntimeError('Release is not published; no announcement')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    channel=json.loads((ROOT/'channels/launcher-win32.json').read_text())
    if channel.get('version')!='0.3.8' or not channel.get('enabled'):raise RuntimeError('Launcher 0.3.8 is not promoted')
    notes=(ROOT/'docs/AREA52-2026-10-07.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Please fully close and reopen your Bear Cave Launcher to install update 0.3.8.**',allowed_mentions={'parse':[], 'roles':['1551989024833667072']},embeds=[dict(title='Bear Cave Launcher 0.3.8 - Restart Required',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Area52-FreePick-Client/releases/tag/area52-0.1.0-alpha.4')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    verify_live()
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCaveLauncherPublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response: message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed launcher patch notes; message ID: '+str(message['id']))
if __name__=='__main__':main()

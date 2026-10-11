from pathlib import Path
import argparse,json,os,re,sys
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from launcher import updater

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    notes=(ROOT/'docs/AREA52-2026-10-11-HOTSPOTS-WARRIOR.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Area 52 update is available. Close the game, reopen your launcher, and press Play before testing.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},embeds=[dict(title='Area 52 - Hotspot Maps and Warrior Proc Repairs',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-11-HOTSPOTS-WARRIOR.md')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    manifest=updater.latest('area52')
    expected={'Data/patch-B.MPQ': '1c43ab90e771318e2f1e2efeb1a73fc9775ce2fab48886782a09bc9b78c9314d', 'Data/area-52/patch-D.MPQ': '86598748c5f2ed16ac4034afc29d82c64edd6e3407fc743619dc9ba3d238d1d4'}
    records={r['path']:r['sha256'] for r in manifest['baseline']}
    if any(not records.get(path,'').startswith(digest) for path,digest in expected.items()):
        raise RuntimeError('Expected combined client package is not publicly promoted; no announcement')
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response:message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed Area 52 patch notes; message ID: '+str(message['id']))

if __name__=='__main__':main()

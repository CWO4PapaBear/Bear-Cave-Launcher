from pathlib import Path
import argparse,json,os,re,sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from launcher import updater

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    notes=(ROOT/'docs/AREA52-2026-10-09-REPAIRS.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Area 52 client update is available. Close the game and reopen your launcher before pressing Play.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},embeds=[dict(title='Area 52 - Block, Trainers and Legendary Repairs',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-09-REPAIRS.md')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    manifest=updater.latest('area52')
    if manifest.get('server_build')!='783bc1c5c1081a04916da1667f17f93738d310e6f874e08b7646ce707d2a766f':
        raise RuntimeError('Expected Area 52 package is not publicly promoted; no announcement')
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response:message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed Area 52 patch notes; message ID: '+str(message['id']))
if __name__=='__main__':main()

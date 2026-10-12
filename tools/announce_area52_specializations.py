from pathlib import Path
import argparse,json,os,re,sys
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    notes=(ROOT/'docs/AREA52-2026-10-11-SPECIALIZATIONS-DUMMIES.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Area 52 server update is live. Log back in to test; no client download is required.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},embeds=[dict(title='Area 52 - Specializations and Training Dummies',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-11-SPECIALIZATIONS-DUMMIES.md')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response:message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed Area 52 patch notes; message ID: '+str(message['id']))

if __name__=='__main__':main()

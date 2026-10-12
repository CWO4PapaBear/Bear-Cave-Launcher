from pathlib import Path
import argparse,json,os,re,sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from launcher import updater

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
 notes=(ROOT/'docs/AREA52-2026-10-12-HOTSPOT-PAINT.md').read_text(encoding='utf-8').strip()
 assert len(notes)<3900
 payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Area 52 is back online. Close the game, reopen your launcher, and press Play to update.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},embeds=[dict(title='Area 52 â€” XP Hotspot Drawing Tools',description=notes,color=0xD5A546)])
 if args.dry_run:print(json.dumps(payload));return
 expected=json.loads((ROOT/'docs/AREA52-2026-10-12-PAINT-CLIENT-HASHES.json').read_text())
 records={r['path']:r['sha256'] for r in updater.latest('area52')['baseline']}
 assert all(records.get(k)==v for k,v in expected.items()),'Matching release is not live; no announcement'
 webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
 assert re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook),'Webhook unavailable'
 try:
  request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePublisher/1.0'},method='POST')
  with urlopen(request,timeout=30) as response:message=json.loads(response.read())
  assert message.get('id') and message.get('embeds')
 except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
 print('Discord confirmed patch notes; message ID: '+str(message['id']))

if __name__=='__main__':main()

from pathlib import Path
import argparse,json,os,re,sys,uuid
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from launcher import updater

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
 notes=(ROOT/'docs/AREA52-2026-10-12-BULWARK-HOTSPOTS.md').read_text(encoding='utf-8-sig').split('\n![Making Progress]')[0].strip()
 image=ROOT/'docs/images/AREA52-2026-10-12-PROGRESS.png'
 assert len(notes)<3900 and image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
 payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072> **Area 52 is back online. Close the game, reopen your launcher, and press Play to update before testing.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},attachments=[{'id':0,'filename':image.name,'description':'Area 52 verification and certification progress by category, including totals and percentages.'}],embeds=[dict(title='Area 52 — Bulwark, Hotspots & Character Repairs',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-12-BULWARK-HOTSPOTS.md',image={'url':'attachment://'+image.name})])
 if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
 manifest=updater.latest('area52')
 expected=json.loads((ROOT/'docs/AREA52-2026-10-12-CLIENT-HASHES.json').read_text())
 records={r['path']:r['sha256'] for r in manifest['baseline']}
 if any(records.get(path)!=digest for path,digest in expected.items()):raise RuntimeError('Matching client package is not publicly promoted; no announcement')
 webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
 if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
 boundary='BearCave'+uuid.uuid4().hex
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n'.encode()+json.dumps(payload).encode()+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="{image.name}"\r\nContent-Type: image/png\r\n\r\n'.encode()+image.read_bytes()+f'\r\n--{boundary}--\r\n'.encode())
 try:
  request=Request(webhook+'?wait=true',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary,'User-Agent':'BearCavePublisher/1.0'},method='POST')
  with urlopen(request,timeout=30) as response:message=json.loads(response.read())
  if not message.get('id') or not any(a.get('filename')==image.name for a in message.get('attachments',[])):raise RuntimeError()
 except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
 print('Discord confirmed Area 52 patch notes with progress image; message ID: '+str(message['id']))

if __name__=='__main__':main()

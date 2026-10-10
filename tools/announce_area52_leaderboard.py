from pathlib import Path
import argparse,json,os,re,sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from launcher import updater

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    notes=(ROOT/'docs/AREA52-2026-10-09-LEADERBOARD.md').read_text(encoding='utf-8').strip()
    assert len(notes)<3900
    payload=dict(username='The Bear Cave - Updates',avatar_url='https://raw.githubusercontent.com/CWO4PapaBear/Bear-Cave-Launcher/main/ui/assets/bear-cave-app-icon.png',content='<@&1551989024833667072> **Area 52 client update is available. Close the game and reopen your launcher before pressing Play.**',allowed_mentions={'parse':[],'roles':['1551989024833667072']},embeds=[dict(title='Area 52 - Leaderboard and Stormwind Dummies',description=notes,color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/blob/main/docs/AREA52-2026-10-09-LEADERBOARD.md')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    manifest=updater.latest('area52')
    if next(r['sha256'] for r in manifest['baseline'] if r['path']=='Interface/AddOns/Area52MysticRules/TesterCertification.lua')!='d036deba33fa720c78e09156423fabde8c7ea32231801c61584518517f442326':
        raise RuntimeError('Expected Area 52 package is not publicly promoted; no announcement')
    if next(r['sha256'] for r in manifest['baseline'] if r['path']=='Interface/Glues/BearCave/CertificationIcon.tga')!='ed41faf1f10a14728c170f697f2d0d86bc15544655fea3b11cee1f4d05dcbf61':
        raise RuntimeError('Leaderboard icon is not promoted; no announcement')
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    edit_id=os.environ.get('DISCORD_EDIT_MESSAGE_ID','').strip()
    if edit_id and not re.fullmatch(r'[0-9]+',edit_id):raise RuntimeError('Invalid message ID')
    try:
        url=webhook+'/messages/'+edit_id if edit_id else webhook+'?wait=true'
        request=Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCavePublisher/1.0'},method='PATCH' if edit_id else 'POST')
        with urlopen(request,timeout=30) as response:message=json.loads(response.read())
        if not message.get('id'):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed Area 52 patch notes; message ID: '+str(message['id']))
if __name__=='__main__':main()


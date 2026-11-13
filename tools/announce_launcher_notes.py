from pathlib import Path
import argparse,hashlib,json,os,re,sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from launcher import updater,fullclient

def verify_live():
    from launcher import selfupdate
    channel=selfupdate.validate(json.loads(updater.fetch(selfupdate.URL)))
    if channel.get('enabled') is not True or channel['version']!='0.3.18' or channel['sha256']!='c3772d6814b8fbb8ff5c6da98a0ee82cdc01753c173f2077604abf40c0a50262':
        raise RuntimeError('Launcher feed has not promoted the verified release')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    payload=dict(username='The Bear Cave - Updates',content='<@&1551989024833667072>',allowed_mentions={'parse':[], 'roles':['1551989024833667072']},embeds=[dict(title='Bear Cave Launcher 0.3.18',description='Fully close and reopen Bear Cave Launcher to update.\n\nIf Check / Repair, Recover, and Play were greyed out because your Area 52 connection files were missing, the launcher now supplies the realm connection automatically. Your saved client folder and custom connection settings are preserved.',color=0xD5A546,url='https://github.com/CWO4PapaBear/Bear-Cave-Launcher/releases/tag/launcher-0.3.18')])
    if args.dry_run:print(json.dumps(payload,ensure_ascii=True));return
    verify_live()
    webhook=os.environ.get('DISCORD_PATCH_NOTES_WEBHOOK','').strip()
    if not re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook):raise RuntimeError('Patch notes webhook unavailable')
    try:
        request=Request(webhook+'?wait=true',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'BearCaveLauncherPublisher/1.0'},method='POST')
        with urlopen(request,timeout=30) as response: message=json.loads(response.read())
        if not (message.get('id') and message.get('channel_id')):raise RuntimeError()
    except Exception:raise RuntimeError('Discord delivery unconfirmed; inspect channel before retrying.') from None
    print('Discord confirmed launcher patch notes; message ID: '+str(message['id'])+' channel: '+str(message['channel_id']))
if __name__=='__main__':main()

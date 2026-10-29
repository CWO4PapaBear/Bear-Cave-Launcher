import hashlib,json,os,re
from pathlib import Path
from urllib.request import Request,urlopen

MESSAGE='1565394708291788932'
CHANNEL='1551651626719248514'
PACKAGE='area52-playerbots-startup-recovery-20261029'
DESCRIPTION='''**Reusable dungeon bots and Arena 1v1**

- Added 20 Hero bots: 10 Alliance and 10 Horde. Each faction has 2 Mystic Knight tanks, 2 Naturalist healers and 6 Hoplite damage dealers.
- Dungeon Finder can use available bots to fill missing roles. Bots match the group leader’s level from 15–80, with level-appropriate builds and equipment. Their initial open-world level is 70.
- Dungeon Finder content is enabled through Wrath of the Lich King, subject to normal eligibility. Bots already busy with another group or activity are not reassigned.
- Added skirmish and rated 1v1 Arena support for Heroes. Rated 1v1 uses the personal 5v5 team slot and will not replace an existing multi-member team.
- Bots do not automatically queue for arenas or battlegrounds.
- No addon or client download is needed.'''

def run():
    webhook=os.environ['DISCORD_PATCH_NOTES_WEBHOOK'].strip()
    assert re.fullmatch(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+',webhook)
    url=webhook+'/messages/'+MESSAGE
    def request(method='GET',payload=None):
        req=Request(url,data=None if payload is None else json.dumps(payload).encode(),headers={'User-Agent':'BearCavePublisher/1.0','Content-Type':'application/json'},method=method)
        with urlopen(req,timeout=30) as response:return json.load(response)
    old=request()
    assert old['id']==MESSAGE and old['channel_id']==CHANNEL
    assert old['content'].startswith('<@&1551989024833667072>')
    matches=[i for i,e in enumerate(old['embeds']) if PACKAGE in e.get('url','')]
    assert len(matches)==1,'Unexpected message embeds; no edit'
    index=matches[0]
    embeds=[]
    for e in old['embeds']:
        clean={k:v for k,v in e.items() if k in ('title','description','url','timestamp','color','footer','image','thumbnail','author','fields')}
        for key in ('image','thumbnail'):
            if key in clean:clean[key]={'url':clean[key]['url']}
        for key in ('footer','author'):
            if key in clean:clean[key]={k:v for k,v in clean[key].items() if not k.startswith('proxy_')}
        embeds.append(clean)
    previous=embeds[index].get('description','')
    assert previous==DESCRIPTION or 'Engineering validation' in previous,'Unexpected prior text; no edit'
    Path('discord-before.json').write_text(json.dumps(old,indent=2))
    embeds[index]['description']=DESCRIPTION
    if previous!=DESCRIPTION:
        request('PATCH',{'embeds':embeds,'allowed_mentions':{'parse':[],'roles':['1551989024833667072']}})
    new=request()
    assert new['content']==old['content'] and new['embeds'][index]['description']==DESCRIPTION
    assert [(a['id'],a.get('size')) for a in new.get('attachments',[])]==[(a['id'],a.get('size')) for a in old.get('attachments',[])]
    assert [e.get('image',{}).get('url') for e in new['embeds']]==[e.get('image',{}).get('url') for e in old['embeds']]
    Path('discord-after.json').write_text(json.dumps(new,indent=2))
    Path('edit-receipt.json').write_text(json.dumps({'status':'verified','message_id':MESSAGE,'channel_id':CHANNEL,'description_sha256':hashlib.sha256(DESCRIPTION.encode()).hexdigest(),'url':f'https://discord.com/channels/1312920749866090628/{CHANNEL}/{MESSAGE}','attachment_identity_preserved':True},indent=2))
    print('Existing Discord message edited and read back; attachment retained; no new message sent')

if __name__=='__main__':
    try:run()
    except Exception as error:
        print('Discord edit failed; reconcile existing message before retry. Error type: '+type(error).__name__)
        raise SystemExit(1)

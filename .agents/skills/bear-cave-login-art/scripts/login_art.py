"""Inspect, build, install or roll back a local WotLK login-art overlay."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,struct
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inspect','build','install','rollback'])
 for key in ['client','art','work','mpq-tools']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();sys.path.insert(0,str(a.mpq_tools));from lib.mpq import MPQArchive,write_archive
 a.work.mkdir(parents=True,exist_ok=True)
 target=a.client/'Data/enUS/patch-enUS-Z.MPQ';candidate=a.work/'patch-enUS-Z.MPQ';record=a.work/'build.json';backup=a.work/'patch-enUS-Z.before.MPQ'
 if a.action=='inspect':
  from PIL import Image
  info={'artIsDirectory':a.art.is_dir(),'art':[],'loginSources':[]}
  for f in sorted(a.art.glob('*.blp')):
   im=Image.open(f);info['art'].append(dict(name=f.name,size=im.size,sha256=sha(f)))
   if f.name.startswith(('background_full','logo_SEPARATE')):im.save(a.work/(f.name+'.png'))
  for f in sorted((a.client/'Data').glob('*.MPQ'))+sorted((a.client/'Data/enUS').glob('*.MPQ')):
   if not f.is_file():continue
   with MPQArchive(f)as ar:
    name='Interface/GlueXML/AccountLogin.lua'
    if ar.has_file(name):
     data=ar.read_file(name);out=a.work/'extracted'/f.name/'AccountLogin.lua';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
     info['loginSources'].append(dict(archive=str(f),sha256=hashlib.sha256(data).hexdigest()))
  (a.work/'inspection.json').write_text(json.dumps(info,indent=2));print('INSPECTED. Review PNGs and archive precedence.');return
 if a.action=='build':
  base=a.client/'Data/enUS/patch-enUS-3.MPQ'
  with MPQArchive(base)as ar:original=ar.read_file('Interface/GlueXML/AccountLogin.lua')
  with MPQArchive(target)as ar:
   names=ar.read_file('(listfile)').decode('utf-8-sig').splitlines()
   names=[n for n in names if n and n not in ('(listfile)','(attributes)','(signature)')]
   assert len(set(n.lower()for n in names))==len(names)
   occupied=[row for row in struct.iter_unpack('<IIHHI',ar._load_hash_table())if row[4] not in (0xffffffff,0xfffffffe)]
   known=names+[n for n in ['(listfile)','(attributes)','(signature)']if ar.has_file(n)]
   assert len(occupied)==len(known) and all(row[2]==0 for row in occupied),'Unlisted entries or locale variants: use a preserving MPQ editor'
   assert not ar.has_file('Interface/GlueXML/AccountLogin.lua'),'Reconcile existing login override first'
   files={n:ar.read_file(n)for n in names}
  before={n:hashlib.sha256(v).hexdigest()for n,v in files.items()}
  lines=original.decode('utf-8-sig').splitlines(True);removed=[x for x in lines if 'AccountLogin:SetModel('in x]
  assert len(removed)==2 and all('UI_MainMenu'in x for x in removed)
  source=''.join(x for x in lines if x not in removed)+'\n'+Path(__file__).with_name('login-art.lua').read_text()
  files['Interface\\GlueXML\\AccountLogin.lua']=source.encode()
  for name,filename in [('Background','background_full_2048x1024.blp'),('Logo','logo_SEPARATE_1024x512.blp')]:files['Interface\\Glues\\BearCave\\'+name+'.blp']=(a.art/filename).read_bytes()
  write_archive(candidate,files)
  with MPQArchive(candidate)as ar:
   for n,v in files.items():assert ar.read_file(n)==v,n
  (a.work/'AccountLogin.lua').write_text(source)
  record.write_text(json.dumps(dict(before=sha(target),after=sha(candidate),base=sha(base),preserved=before),indent=2))
  print('BUILT. Existing entries preserved; three login-only additions. Not installed.');return
 m=json.loads(record.read_text())
 assert subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process Wow -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Close WoW first'
 if a.action=='install':
  raise RuntimeError('Installation blocked: this GlueXML candidate was rejected by the tested client. Use the asset-only redesign; rollback remains available.')
  assert sha(target)==m['before'] and sha(candidate)==m['after'],'Archive drift'
  assert not backup.exists(),'Backup exists; review previous install'
  shutil.copy2(target,backup);source=candidate
 else:
  assert sha(target)==m['after'] and sha(backup)==m['before'],'Rollback drift'
  source=backup
 try:shutil.copyfile(source,target);assert sha(target)==sha(source)
 except BaseException:shutil.copyfile(backup,target);raise
 (a.work/'installation.json').write_text(json.dumps(dict(action=a.action,sha256=sha(target),backup=str(backup.resolve())),indent=2))
 print(a.action.upper()+' COMPLETE. No server changes; original artwork untouched.')
if __name__=='__main__':main()

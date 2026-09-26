"""Asset-only successor. Never adds or changes GlueXML or executable code."""
from pathlib import Path
import argparse,hashlib,json,shutil,struct,subprocess,sys
from build_scene import scene,validate
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','install','rollback'])
 for key in ['client','art','work','mpq-tools']:p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--previous-build',type=Path)
 p.add_argument('--original-snow',action='store_true')
 a=p.parse_args();sys.path.insert(0,str(a.mpq_tools));from lib.mpq import MPQArchive,write_archive
 if a.original_snow:raise RuntimeError('Original-snow prototype caused client error 132; disabled pending model validation.')
 a.work.mkdir(parents=True,exist_ok=True);target=a.client/'Data/enUS/patch-enUS-Z.MPQ';candidate=a.work/target.name;backup=a.work/'original.MPQ';record=a.work/'manifest.json'
 if a.action=='build':
  assert not backup.exists(),'Use a fresh work folder for another revision'
  with MPQArchive(target)as ar:
   names=ar.read_file('(listfile)').decode('utf-8-sig').splitlines();names=[n for n in names if n and n not in ['(listfile)','(attributes)','(signature)']]
   occupied=[r for r in struct.iter_unpack('<IIHHI',ar._load_hash_table())if r[4]not in (0xffffffff,0xfffffffe)]
   assert len(occupied)==len(names)+sum(ar.has_file(n)for n in ['(listfile)','(attributes)','(signature)']) and all(r[2]==0 for r in occupied)
   files={n:ar.read_file(n)for n in names}
   assert not any(n.lower().startswith('interface\\gluexml\\')for n in files),'Unexpected signed UI override; reconcile'
  original=files.copy();m,s=scene();validate(m,s)
  if a.original_snow:
   from snow_scene import snow_scene
   base='Interface/Glues/Models/UI_MainMenu_Northrend/UI_MainMenu_Northrend'
   with MPQArchive(a.client/'Data/enUS/patch-enUS-2.MPQ')as ar:m,s=snow_scene(ar.read_file(base+'.m2'),ar.read_file(base+'00.skin'))
  assets={'Interface\\Glues\\BearCave\\Background.blp':(a.art/'background_full_2048x1024.blp').read_bytes(),'Interface\\Glues\\Common\\Glues-WoW-WotLKLogo.blp':(a.art/'logo_SEPARATE_1024x512.blp').read_bytes()}
  for name in ['UI_MainMenu_Northrend','UI_MainMenu']:
   base='Interface\\Glues\\Models\\'+name+'\\'+name;assets[base+'.m2']=m;assets[base+'00.skin']=s
  overlap={n.lower()for n in assets}&{n.lower()for n in files}
  if overlap:
   assert a.previous_build,'Existing art override requires --previous-build manifest'
   previous=json.loads(a.previous_build.read_text());assert sha(target)==previous['after'],'Previous archive drift'
   assert overlap=={n.lower()for n in assets}=={n.lower()for n in previous['assets']}
   for n,digest in previous['assets'].items():assert hashlib.sha256(files[n]).hexdigest()==digest,n
  for name,data in assets.items():
   out=a.work/'payload'/Path(name.replace('\\','/'));out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  files.update(assets);write_archive(candidate,files)
  with MPQArchive(candidate)as ar:
   for n,v in files.items():assert ar.read_file(n)==v,n
   assert not ar.has_file('Interface/GlueXML/AccountLogin.lua')
  record.write_text(json.dumps(dict(before=sha(target),after=sha(candidate),preserved=len(original),assets={n:hashlib.sha256(v).hexdigest()for n,v in assets.items()}),indent=2))
  print('BUILT AND READ-BACK VERIFIED: asset-only, no GlueXML; Ladik-ready payload exported.');return
 info=json.loads(record.read_text())
 assert subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process Wow -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Close WoW first'
 if a.action=='install':
  with MPQArchive(candidate)as ar:
   model=ar.read_file('Interface/Glues/Models/UI_MainMenu_Northrend/UI_MainMenu_Northrend.m2')
   assert struct.unpack_from('<I',model,60)[0]==4,'Donor-snow prototype is blocked after client error 132'
  assert sha(target)==info['before'] and sha(candidate)==info['after'] and not backup.exists(),'Archive/backup drift'
  shutil.copy2(target,backup);source=candidate
 else:
  assert sha(target)==info['after'] and sha(backup)==info['before'],'Rollback drift';source=backup
 try:shutil.copyfile(source,target);assert sha(target)==sha(source)
 except BaseException:shutil.copyfile(backup,target);raise
 (a.work/'installation.json').write_text(json.dumps(dict(action=a.action,hash=sha(target)),indent=2))
 print(a.action.upper()+' COMPLETE. No server, GlueXML or executable changes.')
if __name__=='__main__':main()

from pathlib import Path
import sys,struct,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[1]/'outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools'))
from lib.mpq import MPQArchive
base=Path('D:/DML WOTLK Client Side/WoW-3.3.5a - HeroFreePick - Classic Test/Data')
archives=[]
def priority(p):
 stem=p.stem.lower()
 if not stem.startswith('patch'):return (0,{'common':0,'common-2':1,'expansion':2,'lichking':3}.get(stem,4),str(p))
 parts=stem.split('-')[1:]
 if parts and parts[0] in ('enus','engb'):parts=parts[1:]
 suffix=parts[-1] if parts else ''
 if not suffix:return (1,0,str(p))
 if suffix.isdigit():return (1,int(suffix),str(p))
 return (2,ord(suffix[0]),str(p))
for p in sorted(base.rglob('*.MPQ'),key=priority):
 try:archives.append((p,MPQArchive(p)))
 except:pass
for p in sorted((R/'candidate').rglob('*.MPQ'),key=priority):
 archives.append((p,MPQArchive(p)))

def read(n):
 for p,a in reversed(archives):
  try:return a.read_file(n),str(p)
  except (KeyError,FileNotFoundError):pass
 raise KeyError(n)
def dbc(b):
 _,n,f,size,ss=struct.unpack_from('<4s4I',b);strings=b[20+n*size:]
 return [struct.unpack_from('<'+'I'*f,b,20+i*size) for i in range(n)],lambda off:strings[off:].split(b'\0',1)[0].decode(errors='replace')
models,ms=dbc(read('DBFilesClient\\CreatureModelData.dbc')[0]);models={r[0]:ms(r[2]).replace('.mdx','.m2').replace('.MDX','.m2') for r in models}
displayBytes=read('DBFilesClient/CreatureDisplayInfo.dbc')[0]
displays,ds=dbc(displayBytes);cache={};issues=[];inspected=0
for row in displays:
 path=models.get(row[1]); skins=[ds(row[i]) for i in (6,7,8)]
 if not path:continue
 if path not in cache:
  try:
   b,source=read(path)
   if b[:4]!=b'MD20':raise ValueError('Not M2')
   n,o=struct.unpack_from('<2I',b,80);ts=[]
   for i in range(n):
    typ,flags,length,offset=struct.unpack_from('<4I',b,o+i*16)
    ts.append((typ,b[offset:offset+length].split(b'\0',1)[0].decode(errors='replace')))
   cache[path]=(source,ts)
  except Exception as e:cache[path]=None
 if not cache[path]:continue
 source,ts=cache[path]
 if row[0]==19483: print('SWIFT WHITE HAWKSTRIDER',path,skins,source,ts)
 if Path(source).stem.lower() in ('common','common-2','expansion','lichking','patch','patch-2','patch-3'):continue
 inspected+=1;missing=[]
 for typ,name in ts:
  if typ in (11,12,13):
   skin=skins[typ-11]
   if not skin:missing.append({'slot':typ-10,'issue':'empty display skin'});continue
   name=path.replace('/','\\').rsplit('\\',1)[0]+'\\'+skin+'.blp'
  elif typ!=0:continue
  if name:
   try:read(name)
   except KeyError:missing.append({'texture':name,'issue':'file not found'})
 if missing:issues.append(dict(display=row[0],model=row[1],path=path,skins=skins,archive=source,missing=missing))
for _,a in archives:a.close()
(R/'sweep.json').write_text(json.dumps(dict(inspectedDisplays=inspected,uniqueModels=len(cache),issues=issues),indent=2))
print('Inspected replacement displays:',inspected,'Candidates:',len(issues))
print('Hawkstrider candidates:',json.dumps([i for i in issues if 'hawkstrider' in i['path'].lower() or 'cockatrice' in i['path'].lower()],indent=2)[:8000])

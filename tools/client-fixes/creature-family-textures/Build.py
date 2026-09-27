from pathlib import Path
import sys,struct,json,hashlib,io
from PIL import Image
sys.path.insert(0,'outputs/Adaptive_Auto_Attack/mod-adaptive-autoattack/tools')
from lib.mpq import MPQArchive,write_archive
H=Path(__file__).resolve().parent
REFERENCE=Path('D:/DML WOTLK Client Side/Ascension A52 Free Pick/ascension-live/ascension-live/Data')
def source_path(name):
 p=Path(name)
 return p if p.is_absolute() else REFERENCE/p
s=Path('outputs/Replacement_Model_Audit/Scan.py').read_text();exec(s[s.index('base=Path'):s.index('models,ms=dbc')])
rows,ds=dbc(read('DBFilesClient/CreatureDisplayInfo.dbc')[0]);plan=[];deferred=[]
for r in rows:
 skins=[ds(r[i]) for i in (6,7,8)];edits={};reason=''
 if r[1]==188 and skins[0].lower() in ['ancientofwarskin','ancientofwarskindiseased','ancientofwarskinsnow'] and not any(skins[1:]):
  edits={7:skins[0]+'2',8:skins[0]+'3'};reason='Replacement ancient requires foliage and secondary body layers'
 elif r[1]==33:
  color=skins[0].removeprefix('OgreSkin')
  if color in ['Beige','Black','Blue','Gray','Red','Yellow']:
   edits={7:'Mage'+color};reason='Replacement ogre mage requires matching Mage armor atlas'
  else:deferred.append({'display':r[0],'reason':'Noncanonical ogre body skin; needs separate render review','skins':skins})
 elif r[1]==27 and skins[0].lower()=='kotobeastwoolyskin':
  edits={1:4005,6:'KotoBeastwoolySkin1',7:'KotoBeastwoolySkin2'};reason='Dedicated wooly replacement mesh and body/fur atlases'
 if edits:plan.append({'display':r[0],'beforeModel':r[1],'beforeSkins':skins,'fields':edits,'reason':reason})
# Exact-path dependencies, never substitute by filename alone.
assets={};provenance=[]
ref=json.loads((H/'reflection-sources.json').read_text())
for target in ['Creature\\OgreHighmaulKing\\smoothreflect.blp','Creature\\OgreHighmaulKing\\ArmorReflect4.blp']:
 p,n=next((p,n) for p,n in ref if n.lower()==target.lower())
 with MPQArchive(source_path(p)) as a:b=a.read_file(n)
 Image.open(io.BytesIO(b)).load();assets[target]=b;provenance.append({'path':target,'source':p,'sha256':hashlib.sha256(b).hexdigest()})
# Reuse the modern Kodo-family reflection map for renamed model directories.
# This is a shared lighting lookup, not a body UV atlas. Record the alias explicitly.
p,n=next((p,n) for p,n in ref if n.lower()=='creature\\kodobeast2mount\\orbreflectbright.blp')
with MPQArchive(source_path(p)) as a:b=a.read_file(n)
assert hashlib.sha256(b).hexdigest()=='ff8db5fbdd2e07e1f4b4aca767aa29822921bed65384707b79f28c9edd1b4276'
Image.open(io.BytesIO(b)).load()
for target in ['Creature\\KodoBeast2\\OrbReflectBright.blp','Creature\\KodoBeast2Wooly\\OrbReflectBright.blp']:
 assets[target]=b;provenance.append({'path':target,'source':p,'sourcePath':n,'sha256':hashlib.sha256(b).hexdigest(),'reason':'Shared modern Kodo reflection-map alias; visual test required'})
# Broader exact-path restorations: unique source bytes only, image decode required.
for item in json.loads((H/'broad-dependencies.json').read_text())['exactUnique']:
 with MPQArchive(source_path(item['source'])) as a:b=a.read_file(item['sourcePath'])
 assert hashlib.sha256(b).hexdigest()==item['sha256']
 Image.open(io.BytesIO(b)).load()
 assert item['path'].lower() not in {n.lower() for n in assets}
 assets[item['path']]=b;provenance.append(item)
models,ms=dbc(read('DBFilesClient/CreatureModelData.dbc')[0]);models={r[0]:ms(r[2]).lower().replace('.mdx','.m2') for r in models}
for p in plan:
 model=models[p['fields'].get(1,p['beforeModel'])];read(model);read(model[:-3]+'00.skin')
 for i in [6,7,8]:
  skin=p['fields'].get(i,p['beforeSkins'][i-6])
  if skin:
   b,_=read(model.rsplit('\\',1)[0]+'\\'+skin+'.blp');Image.open(io.BytesIO(b)).load()
for _,a in archives:a.close()
changes={p['display']:p['fields'] for p in plan};reports=[]
for rel in ['Data/patch-Z.MPQ','Data/enUS/patch-enUS-Z.MPQ']:
 src=base.parent/rel
 with MPQArchive(src) as a:
  names=[n for n in a.read_file('(listfile)').decode('utf-8-sig').splitlines() if n and n not in ('(listfile)','(attributes)','(signature)')]
  occupied=[v for v in struct.iter_unpack('<IIHHI',a._load_hash_table()) if v[4] not in (0xffffffff,0xfffffffe)]
  assert len(occupied)==len(names)+sum(a.has_file(n) for n in ('(listfile)','(attributes)','(signature)')) and all(v[2]==0 for v in occupied)
  files={n:a.read_file(n) for n in names}
 key=next(n for n in files if n.replace('/','\\').lower()=='dbfilesclient\\creaturedisplayinfo.dbc');old=files[key]
 magic,n,f,size,ss=struct.unpack_from('<4s4I',old);assert magic==b'WDBC' and size==f*4
 records=bytearray(old[20:20+n*size]);strings=bytearray(old[20+n*size:]);seen=set()
 for i in range(n):
  row=struct.unpack_from('<'+'I'*f,records,i*size);edits=changes.get(row[0],{})
  for field,value in edits.items():
   assert field in (1,6,7,8)
   if isinstance(value,str):off=len(strings);strings.extend(value.encode()+b'\0');value=off
   struct.pack_into('<I',records,i*size+field*4,value)
  new=struct.unpack_from('<'+'I'*f,records,i*size);assert all(row[j]==new[j] for j in range(f) if j not in edits)
  if edits:seen.add(row[0])
 assert seen==set(changes)
 files[key]=struct.pack('<4s4I',magic,n,f,size,len(strings))+records+strings
 for name,b in assets.items():assert not any(k.lower()==name.lower() for k in files);files[name]=b
 out=H/'candidate'/rel;out.parent.mkdir(parents=True,exist_ok=True);write_archive(out,files)
 with MPQArchive(out) as a:
  for name,b in files.items():assert a.read_file(name)==b,name
 reports.append({'path':rel,'before':hashlib.sha256(src.read_bytes()).hexdigest(),'after':hashlib.sha256(out.read_bytes()).hexdigest()})
(H/'plan.json').write_text(json.dumps(plan,indent=2));(H/'deferred.json').write_text(json.dumps(deferred,indent=2));(H/'report.json').write_text(json.dumps({'status':'staged-not-installed','displayCorrections':len(plan),'archives':reports,'assets':provenance},indent=2))
print('PASS',len(plan),'display corrections; complete archive readback; unrelated files preserved. Deferred:',len(deferred))
